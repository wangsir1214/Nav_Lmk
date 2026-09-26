"""Build a reviewable local-place retrieval development set; no model calls."""
from __future__ import annotations
import argparse, csv, hashlib, io, json, math, os, platform, random, struct, sys, time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

def digest(data): return hashlib.sha256(data).hexdigest()
def read_csv(p):
    with Path(p).open(encoding="utf-8-sig", newline="") as f: return list(csv.DictReader(f))
def write_csv(p, rows, fields=None):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    if fields is None: fields=list(rows[0]) if rows else []
    with p.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
def write_json(p, obj):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
def log(out,msg):
    text=f"{datetime.now(timezone.utc).isoformat()} {msg}"
    print(text,flush=True)
    with (out/"run.log").open("a",encoding="utf-8") as f: f.write(text+"\n")
def dbf(raw,encoding="utf-8"):
    count=struct.unpack("<I",raw[4:8])[0]; head,size=struct.unpack("<HH",raw[8:12])
    fields=[]; off=32
    while off<head-1 and raw[off]!=13:
        x=raw[off:off+32]; fields.append((x[:11].split(b"\0")[0].decode(),chr(x[11]),x[16])); off+=32
    rows=[]
    for i in range(count):
        x=raw[head+i*size:head+(i+1)*size]; assert len(x)==size
        if x[:1]==b"*": raise ValueError("Deleted DBF record: cannot preserve row-index join")
        row={}; off=1
        for name,kind,length in fields:
            s=x[off:off+length].decode(encoding).strip().strip("\0"); off+=length
            if not s: val=None
            elif kind in ("N","F"): val=float(s) if "." in s else int(s)
            elif kind=="L": val=s.upper() in ("Y","T")
            else: val=s
            row[name]=val
        rows.append(row)
    return rows
def polylines(raw):
    off=100; result=[]
    while off<len(raw):
        _,words=struct.unpack(">II",raw[off:off+8]); x=raw[off+8:off+8+2*words]; off+=8+2*words
        typ=struct.unpack("<I",x[:4])[0]
        if typ not in (3,13,23): raise ValueError(f"Unexpected road shape type {typ}")
        nparts,npoints=struct.unpack("<II",x[36:44])
        starts=list(struct.unpack(f"<{nparts}I",x[44:44+4*nparts])); start=44+4*nparts
        coords=[struct.unpack("<dd",x[start+16*i:start+16*i+16]) for i in range(npoints)]
        result.append([coords[a:b] for a,b in zip(starts,starts[1:]+[npoints])])
    return result
def graph_tables(path):
    d=json.loads(Path(path).read_text(encoding="utf-8-sig")); out={}
    for ds in d["datasets"]:
        tab=ds["data"]; fields=[f["name"] for f in tab["fields"]]
        rows=[dict(zip(fields,r)) for r in tab["allData"]]
        out["nodes" if "panoid" in fields else "edges"]=rows
    return out
def angle(a,b): return abs((float(a)-float(b)+180)%360-180)
def distance(a,b): return math.hypot(a["x_m"]-b["x_m"],a["y_m"]-b["y_m"])
def project_on_parts(x,y,parts):
    best=None; chain=0.
    for part in parts:
        for (ax,ay),(bx,by) in zip(part,part[1:]):
            dx=bx-ax;dy=by-ay;length=math.hypot(dx,dy)
            if not length: continue
            t=max(0.,min(1.,((x-ax)*dx+(y-ay)*dy)/length**2))
            px=ax+t*dx;py=ay+t*dy;dist=math.hypot(x-px,y-py)
            item=(dist,chain+t*length,px,py)
            if best is None or item[0]<best[0]: best=item
            chain+=length
    if best is None: raise ValueError("Empty geometry")
    return best,chain
def inventory(args):
    out=args.output_dir; out.mkdir(parents=True,exist_ok=True)
    log(out,"START index; exact metadata and two non-recursive image listings")
    sources={}
    for key,path in [("heading",args.metadata),("point_road",args.point_road_dbf),("road_dbf",args.road_dbf),("road_shp",args.road_shp),("road_prj",args.road_shp.with_suffix(".prj")),("graph",args.graph)]:
        raw=path.read_bytes(); sources[key]={"path":str(path),"sha256":digest(raw),"bytes":len(raw)}
        if key!="graph": (out/"sources").mkdir(exist_ok=True); (out/"sources"/(key+path.suffix)).write_bytes(raw)
    heading=read_csv(args.metadata); assert len({r["panoid"] for r in heading})==len(heading)
    points=dbf(args.point_road_dbf.read_bytes()); point_map={r["panoid"]:r for r in points}; assert len(point_map)==len(points)
    roads=dbf(args.road_dbf.read_bytes()); shapes=polylines(args.road_shp.read_bytes()); assert len(roads)==len(shapes)
    from pyproj import Transformer
    tr=Transformer.from_crs(4326,2154,always_xy=True)
    projected=[[[tr.transform(*xy) for xy in part] for part in parts] for parts in shapes]
    graph=graph_tables(args.graph); nodes={n["panoid"]:n for n in graph["nodes"]}
    graph_edges={tuple(sorted((r["from"],r["to"]))) for r in graph["edges"]}
    listings={}
    for key,root in [("fixed",args.image_dir),("erp",args.erp_dir)]:
        with os.scandir(root) as it: listings[key]={f.name for f in it if f.is_file()}
    panos=[]; views=[]; roadcounts=Counter()
    for h in sorted(heading,key=lambda r:r["panoid"]):
        pid=h["panoid"]; lon=float(h["lng_from_api"]);lat=float(h["lat_from_api"]); x,y=tr.transform(lon,lat)
        n=nodes.get(pid,{}); p=point_map.get(pid); sid=int(p["nearest_st"]) if p else None
        road=roads[sid] if sid is not None else {}
        if sid is not None:
            assert str(road["osmid"])==str(p["nearest__1"]),f"road join mismatch {pid}"
            proj,length=project_on_parts(x,y,projected[sid])
        else: proj=(None,None,None,None);length=None
        row={"pano_id":pid,"capture_lon":lon,"capture_lat":lat,"x_m":x,"y_m":y,
             "original_lon":float(h["lon"]),"original_lat":float(h["lat"]),
             "snapped_lon":n.get("lon"),"snapped_lat":n.get("lat"),
             "capture_date":h["date_from_api"],"heading_from_api":float(h["heading_from_api"])%360,
             "street_segment_id":sid,"osm_way_id":road.get("osmid"),"road_name":road.get("name"),
             "road_highway":road.get("highway"),"road_u":road.get("u"),"road_v":road.get("v"),
             "road_oneway":road.get("oneway"),"road_offset_m":proj[0],"chainage_m":proj[1],
             "road_length_m":length,"graph_member":pid in nodes,
             "fixed_complete":all(f"{pid}_panorama_{i}.jpg" in listings["fixed"] for i in range(4)),
             "erp_exists":f"{pid}_panorama.jpg" in listings["erp"],
             "metadata_source_sha256":sources["heading"]["sha256"]}
        panos.append(row);roadcounts[sid]+=1
        for i in range(4):
            views.append({**row,"view_id":f"{pid}__v{i}","view_index":i,
                "absolute_heading":(row["heading_from_api"]+90*i)%360,
                "fixed_root_key":"paris_fixed","image_relative_path":f"{pid}_panorama_{i}.jpg",
                "erp_root_key":"paris_erp","erp_relative_path":f"{pid}_panorama.jpg",
                "file_exists":f"{pid}_panorama_{i}.jpg" in listings["fixed"],
                "width":640,"height":640,"dimensions_status":"historical_audit_not_individually_read",
                "image_448_relative_path":"","image_448_status":"not_generated",
                "area_id":"paris_arc","spatial_group_id":f"road_{sid:03d}" if sid is not None else "unmapped",
                "experiment_split":"unassigned","retrieval_role":"unused",
                "capture_coordinate_source":"heading_csv:lng_from_api,lat_from_api",
                "original_coordinate_source":"heading_csv:lon,lat",
                "snapped_coordinate_source":"graph:lon,lat" if n else "",
                "distance_crs":"EPSG:2154"})
    road_out=[]
    for sid,road in enumerate(roads):
        items=[p for p in panos if p["street_segment_id"]==sid]
        viable=[p for p in items if p["road_offset_m"]<=12 and p["fixed_complete"]]
        # Count spatially separated positions without forcing capture month consistency.
        ordered=sorted(viable,key=lambda p:(p["chainage_m"],p["pano_id"]))
        selected=[]
        for p in ordered:
            if all(distance(p,q)>=8 for q in selected): selected.append(p)
        road_out.append({"street_segment_id":sid,**road,"pano_count":len(items),"spaced8m_count":len(selected),
                         "chainage_range_m":max((p["chainage_m"] for p in viable),default=0)-min((p["chainage_m"] for p in viable),default=0),
                         "center_x_m":sum(p["x_m"] for p in items)/len(items) if items else None,
                         "center_y_m":sum(p["y_m"] for p in items)/len(items) if items else None})
    write_csv(out/"data/view_manifest.csv",views)
    write_csv(out/"data/pano_manifest.csv",panos)
    write_csv(out/"data/road_inventory.csv",road_out)
    write_json(out/"sources/source_manifest.json",sources)
    write_json(out/"sources/road_geometry.json",{"crs":"EPSG:2154","parts":projected})
    write_json(out/"sources/graph_edges.json",sorted(graph_edges))
    write_json(out/"configs/paths.local.json",{"paris_fixed":str(args.image_dir),"paris_erp":str(args.erp_dir)})
    write_json(out/"configs/paths.example.json",{"paris_fixed":"<server-fixed-view-root>","paris_erp":"<server-erp-root>"})
    summary={"panos":len(panos),"views":len(views),"graph_nodes":len(nodes),"graph_edges":len(graph_edges),
             "mapped_panos":sum(p["street_segment_id"] is not None for p in panos),
             "all_four_exists":sum(p["fixed_complete"] for p in panos),"erp_exists":sum(p["erp_exists"] for p in panos),
             "road_segments":len(roads),"files_listed":{k:len(v) for k,v in listings.items()},
             "image_pixels_read":0,"road_join_osmid_checked":True,"index_state":"unassigned"}
    write_json(out/"index_summary.json",summary)
    log(out,"INDEX COMPLETE "+json.dumps(summary))
    print(json.dumps(sorted([r for r in road_out if r["spaced8m_count"]>=9],key=lambda r:r["spaced8m_count"],reverse=True)[:35],ensure_ascii=False))
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--phase",choices=["index","task","review","validate","all"],default="index")
    p.add_argument("--metadata",type=Path,required=True)
    p.add_argument("--image-dir",type=Path,required=True);p.add_argument("--erp-dir",type=Path,required=True)
    p.add_argument("--point-road-dbf",type=Path,required=True);p.add_argument("--road-dbf",type=Path,required=True);p.add_argument("--road-shp",type=Path,required=True)
    p.add_argument("--graph",type=Path,required=True);p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--extra-deps",type=Path);p.add_argument("--seed",type=int,default=42);p.add_argument("--city",default="Paris")
    p.add_argument("--groups",type=int,default=6);p.add_argument("--num-samples",type=int,default=54)
    args=p.parse_args()
    if args.extra_deps:sys.path.insert(0,str(args.extra_deps))
    if hasattr(sys.stdout,"reconfigure"):sys.stdout.reconfigure(encoding="utf-8")
    if args.phase in ("index","all"):inventory(args)
    # Other phases added after inspection of the actual index.
if __name__=="__main__":main()
