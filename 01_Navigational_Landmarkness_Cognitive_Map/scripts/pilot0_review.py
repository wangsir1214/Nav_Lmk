"""Cache selected views and create offline review cards and a review website."""
from __future__ import annotations
import argparse, base64, html, io, json, math, sys
from collections import Counter
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from pilot0_local import read_csv,write_csv,write_json,digest,log
from pilot0_tasks import typed

FONT=Path("C:/Windows/Fonts/msyh.ttc")
def font(size):return ImageFont.truetype(str(FONT),size) if FONT.exists() else ImageFont.load_default()
def wrap(draw,text,xy,maxwidth,f,fill="#243447"):
    x,y=xy;line=""
    for ch in str(text):
        if draw.textlength(line+ch,font=f)>maxwidth:
            draw.text((x,y),line,font=f,fill=fill);y+=f.size+5;line=ch
        else:line+=ch
    draw.text((x,y),line,font=f,fill=fill)
    return y+f.size+5
def make_cards(out,cases,vm):
    carddir=out/"review/cards";carddir.mkdir(parents=True,exist_ok=True)
    for c in cases:
        q,r=vm[c["query_view_id"]],vm[c["reference_view_id"]]
        card=Image.new("RGB",(1360,855),"#ffffff");d=ImageDraw.Draw(card)
        d.text((24,14),f'{c["review_case_id"]}   Query / Reference',font=font(27),fill="#162638")
        for x,v,label in [(24,q,"Query"),(696,r,"Reference")]:
            im=Image.open(out/"review"/v["review_image"]).convert("RGB");card.paste(im.resize((640,640)),(x,110))
            d.text((x,60),f'{label}   {v["dev_group_id"]} · view {v["view_index"]} · {float(v["absolute_heading"]):.1f}°',font=font(20),fill="#263749")
            d.text((x,86),v["capture_date"]+"  "+v["road_name"],font=font(15),fill="#465564")
        d.text((24,766),f'距离 {c["distance_m"]:.1f} m    朝向差 {c["heading_diff_deg"]:.1f}°    月份差 {c["capture_month_gap"]}',font=font(21),fill="#263749")
        d.text((24,804),"判断共同场景与局部地点；不需要评价地标。几何标签尚未人工确认。",font=font(20),fill="#526373")
        card.save(carddir/(c["review_case_id"]+".jpg"),quality=90)
    # Six full pair miniatures per sheet, selected in deterministic review order.
    sheets=out/"review/contact_sheets";sheets.mkdir(exist_ok=True)
    for start in range(0,len(cases),6):
        sheet=Image.new("RGB",(1440,1510),"#eaf0f5");d=ImageDraw.Draw(sheet)
        d.text((20,14),f'配对预审 {start+1}–{min(start+6,len(cases))} / {len(cases)}',font=font(26),fill="#1f3043")
        for j,c in enumerate(cases[start:start+6]):
            im=Image.open(carddir/(c["review_case_id"]+".jpg"));im.thumbnail((700,440))
            x=16+(j%2)*712;y=66+(j//2)*476;sheet.paste(im,(x,y))
        sheet.save(sheets/f"sheet_{start//6+1:02d}.jpg",quality=90)
def spatial_svg(out,panos,groups):
    geom=json.loads((out/"sources/road_geometry.json").read_text())["parts"]
    xs=[p["x_m"] for p in panos];ys=[p["y_m"] for p in panos]
    minx,maxx=min(xs)-25,max(xs)+25;miny,maxy=min(ys)-25,max(ys)+25
    W,H=1360,910;s=min((W-200)/(maxx-minx),(H-130)/(maxy-miny))
    def pt(x,y):return 75+(x-minx)*s,65+(maxy-y)*s
    elements=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="white"/>',
              '<g font-family="Arial, sans-serif" fill="#233548"><text x="28" y="30" font-size="24">Paris Pilot 0 — development streets and reserve</text>']
    for parts in geom:
        for part in parts:
            points=" ".join(f"{pt(x,y)[0]:.1f},{pt(x,y)[1]:.1f}" for x,y in part)
            elements.append(f'<polyline points="{points}" fill="none" stroke="#c8d0d7" stroke-width="2"/>')
    colors={"eval_candidate":"#b4bdc6","buffer":"#d5ad6d","dev":"#5f8cad","unmapped":"#777"}
    for p in panos:
        x,y=pt(p["x_m"],p["y_m"]);color=colors[p["experiment_split"]]
        elements.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.8" fill="{color}"/>')
    for p in panos:
        if p["retrieval_role"]!="unused":
            x,y=pt(p["x_m"],p["y_m"])
            if p["retrieval_role"]=="query":elements.append(f'<rect x="{x-3:.1f}" y="{y-3:.1f}" width="6" height="6" fill="#bc4a40"/>')
            else:elements.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#1a6980"/>')
    for g in groups:
        x,y=pt(float(g["center_x_m"]),float(g["center_y_m"]))
        elements.append(f'<text x="{x+9:.1f}" y="{y-13:.1f}" font-size="16" font-weight="bold">{g["dev_group_id"]}</text>')
    elements.extend(['<text x="1135" y="55" font-size="18">N ↑</text>',
        '<text x="28" y="844" font-size="16">Square: query   Blue dot: reference   Tan: 100 m buffer   Gray: potential evaluation</text>',
        '<text x="28" y="870" font-size="16">Distance: EPSG:2154, API capture positions. Evaluation remains unfrozen.</text>'])
    x0,y0=35,800
    elements.append(f'<path d="M{x0},{y0} h{100*s:.1f}" stroke="#233548" stroke-width="4"/><text x="{x0}" y="{y0-10}" font-size="16">100 m</text></g></svg>')
    (out/"review/spatial_overview.svg").write_text("\n".join(elements),encoding="utf-8")

def build(args):
    out=args.output_dir;log(out,"START review; read only selected 640-pixel views")
    rows=typed(read_csv(out/"data/view_manifest.csv"));vm={v["view_id"]:v for v in rows}
    cases=json.loads((out/"review/review_cases.json").read_text(encoding="utf-8"))
    paths=json.loads((out/"configs/paths.local.json").read_text())
    image_root=Path(paths["paris_fixed"])
    imdir=out/"review/images";imdir.mkdir(parents=True,exist_ok=True)
    image_checks=[];read_count=0
    active=[v for v in rows if v["retrieval_role"]!="unused"]
    for idx,v in enumerate(active):
        rel="images/"+digest(v["view_id"].encode())[:20]+".jpg";target=out/"review"/rel
        if not target.exists():
            raw=(image_root/v["image_relative_path"]).read_bytes();read_count+=1
            target.write_bytes(raw)
        else:raw=target.read_bytes()
        with Image.open(io.BytesIO(raw)) as im:
            im.load();w,h=im.size
            if (w,h)!=(640,640):raise ValueError(f"Unexpected selected image size {v['view_id']} {(w,h)}")
        v.update({"review_image":rel,"image_sha256":digest(raw),"width":w,"height":h,"dimensions_status":"decoded_this_run"})
        image_checks.append({"view_id":v["view_id"],"source_relative_path":v["image_relative_path"],"review_image":rel,"sha256":digest(raw),"width":w,"height":h,"bytes":len(raw),"decode_ok":True})
        if (idx+1)%48==0:log(out,f"images cached/verified {idx+1}/{len(active)}")
    # Consistent columns across active and unused rows.
    for v in rows:
        v.setdefault("review_image","");v.setdefault("image_sha256","")
    write_csv(out/"data/view_manifest.csv",rows)
    write_csv(out/"data/queries.csv",[v for v in rows if v["retrieval_role"]=="query"])
    write_csv(out/"data/references.csv",[v for v in rows if v["retrieval_role"]=="reference"])
    write_csv(out/"review/image_validation.csv",image_checks)
    make_cards(out,cases,vm)
    splits={s["pano_id"]:s for s in read_csv(out/"data/spatial_splits.csv")}
    panos=typed(read_csv(out/"data/pano_manifest.csv"))
    for p in panos:p.update(splits[p["pano_id"]]);p["x_m"]=float(p["x_m"]);p["y_m"]=float(p["y_m"])
    spatial_svg(out,panos,read_csv(out/"data/development_groups.csv"))
    data=[]
    for c in cases:
        q,r=vm[c["query_view_id"]],vm[c["reference_view_id"]]
        data.append({**c,"query":{k:q[k] for k in ["view_id","pano_id","view_index","absolute_heading","capture_date","road_name","review_image","dev_group_id"]},
                     "reference":{k:r[k] for k in ["view_id","pano_id","view_index","absolute_heading","capture_date","road_name","review_image","dev_group_id"]}})
    fingerprint=digest(json.dumps(data,sort_keys=True).encode())
    template=(Path(__file__).parent/"pilot0_review_template.html").read_text(encoding="utf-8")
    triage_path=out/"review/codex_visual_notes.json"
    triage=json.loads(triage_path.read_text(encoding="utf-8")) if triage_path.exists() else {"priority_cases":[],"notes":{}}
    if triage["notes"]:
        write_csv(out/"review/codex_pair_pre_review.csv",[{"case_id":c["review_case_id"],"pair_id":c["pair_id"],"proposed_relation":c["relation"],"priority":"priority" if c["review_case_id"] in triage["priority_cases"] else "routine","evidence_status":"machine_assisted_visual_not_human_verified","pre_review_note":triage["notes"].get(c["review_case_id"],""),"human_verdict":""} for c in cases])
    body=template.replace("__REVIEW_DATA__",json.dumps(data,ensure_ascii=False).replace("</","<\\/")).replace("__FINGERPRINT__",fingerprint).replace("__TASK_ID__",args.task_id).replace("__TRIAGE_DATA__",json.dumps(triage,ensure_ascii=False).replace("</","<\\/"))
    (out/"review/index.html").write_text(body,encoding="utf-8")
    write_json(out/"review/review_build_summary.json",{"cases":len(cases),"images_checked":len(active),"remote_image_reads":read_count,"erp_pixels_read":0,
        "review_fingerprint":fingerprint,"contact_sheets":math.ceil(len(cases)/6),"image_copy_bytes":sum(x["bytes"] for x in image_checks),
        "generated_review_file":"review/index.html","human_fields_prefilled":False})
    log(out,f"REVIEW COMPLETE {len(cases)} cards; {len(active)} selected images; fingerprint {fingerprint}")
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output-dir",type=Path,required=True);p.add_argument("--task-id",default="paris_local_v0_20260922")
    a=p.parse_args()
    if hasattr(sys.stdout,"reconfigure"):sys.stdout.reconfigure(encoding="utf-8")
    build(a)
if __name__=="__main__":main()
