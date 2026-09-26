"""Construct a small spatial development task from the cached full index."""
from __future__ import annotations
import argparse, json, math, random, sys
from pathlib import Path
from collections import Counter, defaultdict
from pilot0_local import read_csv,write_csv,write_json,digest,angle,distance,log

FLOATS={"capture_lon","capture_lat","x_m","y_m","original_lon","original_lat","snapped_lon","snapped_lat","heading_from_api","road_offset_m","chainage_m","road_length_m","absolute_heading","center_x_m","center_y_m","length"}
INTS={"street_segment_id","view_index","pano_count","spaced8m_count"}
BOOLS={"graph_member","fixed_complete","erp_exists","file_exists"}
def typed(rows):
    out=[]
    for r in rows:
        x=dict(r)
        for k,v in r.items():
            if k in FLOATS:x[k]=float(v) if v!="" else None
            elif k in INTS:x[k]=int(v) if v!="" else None
            elif k in BOOLS:x[k]=v=="True"
        out.append(x)
    return out
def compatible(a,b,maximum=30):
    return min(angle(a["heading_from_api"],b["heading_from_api"]+90*i) for i in range(4))<=maximum
def choose_windows(panos,roads,seed,n_groups):
    groups=defaultdict(list)
    for p in panos:
        if p["street_segment_id"] is not None and p["fixed_complete"] and p["road_offset_m"]<=12 and 10<=p["chainage_m"]<=p["road_length_m"]-10:
            groups[p["street_segment_id"]].append(p)
    candidates=[]
    for sid,ps in groups.items():
        road=roads[sid]
        # Only a single named, non-circular segment; retain all others in the full index.
        if not road["name"] or road["name"].startswith("[") or road["junction"]=="circular":continue
        ordered=sorted(ps,key=lambda p:(p["chainage_m"],p["pano_id"]))
        wins=[]
        for start in range(len(ordered)):
            window=[]
            for x in ordered[start:]:
                if all(distance(x,y)>=8 for y in window):window.append(x)
                if len(window)==9:break
            if len(window)<9:continue
            # Anchor indices 2 and 6; surrounding entries are reference observations.
            anchors=[window[2],window[6]]
            if distance(*anchors)<30:continue
            if any(distance(a,b)>25 for a,b in zip(window,window[1:])):continue
            cost=0.;good=True
            for qidx in (2,6):
                q=window[qidx]
                for ridx in (qidx-1,qidx+1):
                    r=window[ridx];d=distance(q,r)
                    if not 8<=d<=25 or not compatible(q,r):good=False
                    cost+=abs(d-15)
            if good:
                cost+=abs(sum(p["chainage_m"] for p in window)/9-float(road["length"])/2)*.02
                wins.append((cost,window))
        if wins:
            _,win=min(wins,key=lambda x:(x[0],x[1][0]["pano_id"]))
            candidates.append({"sid":sid,"road":road,"window":win,
                "x_m":sum(p["x_m"] for p in win)/9,"y_m":sum(p["y_m"] for p in win)/9})
    if len(candidates)<n_groups:raise ValueError("Insufficient valid road windows")
    def tie(c):return digest((str(seed)+str(c["sid"])).encode())
    first=min([c for c in candidates if c["road"]["highway"]=="primary"] or candidates,key=tie)
    selected=[first]
    while len(selected)<n_groups:
        eligible=[c for c in candidates if c not in selected and c["road"]["name"] not in {x["road"]["name"] for x in selected}]
        if len(selected)%2:
            anchor=selected[-1]
            near=[c for c in eligible if 80<=distance(c,anchor)<=250 and not ({c["road"]["u"],c["road"]["v"]}&{anchor["road"]["u"],anchor["road"]["v"]})]
            if not near:raise ValueError("No nearby distinct-street negative group; revise metadata selection explicitly")
            winner=min(near,key=lambda c:(abs(distance(c,anchor)-150),tie(c)))
        else:
            winner=max(eligible,key=lambda c:(min(distance(c,s) for s in selected),tie(c)))
        selected.append(winner)
    return selected,candidates

def build(args):
    out=args.output_dir;log(out,"START task: metadata-only spatial selection")
    panos=typed(read_csv(out/"data/pano_manifest.csv"));views=typed(read_csv(out/"data/view_manifest.csv"))
    roads={r["street_segment_id"]:r for r in typed(read_csv(out/"data/road_inventory.csv"))}
    selected,candidates=choose_windows(panos,roads,args.seed,args.groups)
    selected_sids={s["sid"] for s in selected}
    dev_panos=[p for p in panos if p["street_segment_id"] in selected_sids]
    active={};group_rows=[]
    for i,s in enumerate(selected,1):
        gid=f"D{i:02d}"
        for j,p in enumerate(s["window"]):
            active[p["pano_id"]]={"retrieval_role":"query" if j in (2,6) else "reference","dev_group_id":gid,"sequence_index":j}
        group_rows.append({"dev_group_id":gid,"street_segment_id":s["sid"],"road_name":s["road"]["name"],
            "highway":s["road"]["highway"],"selected_panos":9,"query_panos":2,"reference_panos":7,
            "center_x_m":s["x_m"],"center_y_m":s["y_m"],"selection_basis":"metadata_geometry_only",
            "all_segment_panos_in_dev":sum(p["street_segment_id"]==s["sid"] for p in panos)})
    splits=[]
    for p in panos:
        near=min(distance(p,d) for d in dev_panos)
        if p["street_segment_id"] in selected_sids:split="dev"
        elif near<args.buffer_m:split="buffer"
        elif p["street_segment_id"] is None:split="unmapped"
        else:split="eval_candidate"
        a=active.get(p["pano_id"],{})
        splits.append({"pano_id":p["pano_id"],"street_segment_id":p["street_segment_id"],"experiment_split":split,
                       "min_distance_to_dev_m":near,"retrieval_role":a.get("retrieval_role","unused"),
                       "dev_group_id":a.get("dev_group_id",""),"sequence_index":a.get("sequence_index",""),
                       "split_status":"development_selected_evaluation_not_frozen"})
    splitmap={s["pano_id"]:s for s in splits}
    for v in views:
        v.update({k:val for k,val in splitmap[v["pano_id"]].items() if k not in ("street_segment_id","pano_id")})
        v["task_id"]=args.task_id if v["retrieval_role"]!="unused" else ""
    qs=[v for v in views if v["retrieval_role"]=="query"]
    rs=[v for v in views if v["retrieval_role"]=="reference"]
    allpairs=[];qsum=[]
    for q in qs:
        positive_candidates=[]
        for r in rs:
            d=distance(q,r);h=angle(q["absolute_heading"],r["absolute_heading"])
            if q["pano_id"]!=r["pano_id"] and q["street_segment_id"]==r["street_segment_id"] and args.pos_min_m<=d<=args.pos_max_m and h<=args.heading_max_deg:
                positive_candidates.append((abs(d-15),d,r))
        chosen=sorted(positive_candidates,key=lambda t:(t[0],t[1],t[2]["view_id"]))[:2]
        posids={r["view_id"] for _,_,r in chosen}
        labels=Counter()
        for r in rs:
            d=distance(q,r);h=angle(q["absolute_heading"],r["absolute_heading"])
            same=q["street_segment_id"]==r["street_segment_id"]
            shared=bool({q["road_u"],q["road_v"]}&{r["road_u"],r["road_v"]})
            if r["view_id"] in posids:rel="positive";reason="same_segment_nearby_heading_compatible_pending_visual_audit"
            elif q["pano_id"]==r["pano_id"]:rel="ignore";reason="same_pano_excluded"
            elif not same and not shared and d>args.neg_min_m:rel="negative";reason="different_segment_no_shared_endpoint_spatially_separated"
            elif same and args.pos_min_m<=d<=args.pos_max_m and h<=args.heading_max_deg:rel="ignore";reason="additional_positive_candidate_not_in_primary_review_set"
            elif d<args.pos_min_m:rel="ignore";reason="too_close_near_duplicate"
            elif same and d<=args.pos_max_m and h>args.heading_max_deg:rel="ignore";reason="nearby_but_heading_incompatible"
            elif shared and not same:rel="ignore";reason="shared_intersection_boundary"
            else:rel="ignore";reason="local_correspondence_not_established"
            negkind=("geometry_candidate" if h<=args.heading_max_deg and d<=300 else "ordinary") if rel=="negative" else ""
            pairid="pair_"+digest((q["view_id"]+"|"+r["view_id"]).encode())[:14]
            months=lambda s:int(s[:4])*12+int(s[5:7])
            row={"pair_id":pairid,"query_view_id":q["view_id"],"reference_view_id":r["view_id"],
                "relation":rel,"negative_kind":negkind,"distance_m":round(d,6),"heading_diff_deg":round(h,6),
                "same_segment":same,"shared_osm_endpoint":shared,"road_relation":"same_segment" if same else ("shared_endpoint" if shared else "different_segment"),
                "query_capture_date":q["capture_date"],"reference_capture_date":r["capture_date"],
                "capture_month_gap":abs(months(q["capture_date"])-months(r["capture_date"])),
                "query_dev_group_id":q["dev_group_id"],"reference_dev_group_id":r["dev_group_id"],
                "reason":reason,"label_source":"geometry_rule","review_status":"pending_human" if rel=="positive" else "rule_generated",
                "human_review_required":rel=="positive","scoring_allowed":False,"protocol_version":args.task_id}
            allpairs.append(row);labels[rel]+=1
        qsum.append({"query_view_id":q["view_id"],"pano_id":q["pano_id"],"dev_group_id":q["dev_group_id"],
                      "positive_count":labels["positive"],"negative_count":labels["negative"],"ignore_count":labels["ignore"],
                      "gallery_size":len(rs),"ready_for_baseline":False,"status":"pending_pair_review" if labels["positive"] and labels["negative"] else "no_scoreable_relation"})
    review=[p for p in allpairs if p["relation"]=="positive"]
    # Include all proposed positives and a prespecified, geometry-stratified negative/ignore audit.
    for gid in [g["dev_group_id"] for g in group_rows]:
        local=[p for p in allpairs if p["query_dev_group_id"]==gid]
        for vidx in range(4):
            neg=[p for p in local if p["relation"]=="negative" and p["query_view_id"].endswith(f"__v{vidx}")]
            candidate=min(neg,key=lambda p:(p["heading_diff_deg"]>30,p["distance_m"],p["heading_diff_deg"],p["pair_id"]))
            review.append(candidate)
        ig=[p for p in local if p["relation"]=="ignore"]
        incompatible=[p for p in ig if p["reason"]=="nearby_but_heading_incompatible"]
        if incompatible:review.append(min(incompatible,key=lambda p:(abs(p["heading_diff_deg"]-90),p["distance_m"],p["pair_id"])))
        boundary=[p for p in ig if 25<p["distance_m"]<=50 and p["heading_diff_deg"]<=30]
        if boundary:review.append(min(boundary,key=lambda p:(p["distance_m"],p["pair_id"])))
    review={p["pair_id"]:p for p in review}
    order={"positive":0,"negative":1,"ignore":2}
    rows=sorted(review.values(),key=lambda p:(order[p["relation"]],p["query_dev_group_id"],p["query_view_id"],p["pair_id"]))
    for i,p in enumerate(rows,1):
        p["human_review_required"]=True
        p["review_case_id"]=f"R{i:03d}"
    idmap={p["pair_id"]:p.get("review_case_id","") for p in rows}
    for p in allpairs:p["review_case_id"]=idmap.get(p["pair_id"],"")
    review_fields=["case_id","pair_id","query_view_id","reference_view_id","proposed_relation","human_relation","overlap","quality","evidence","reviewer","notes"]
    template=[dict(zip(review_fields,[p["review_case_id"],p["pair_id"],p["query_view_id"],p["reference_view_id"],p["relation"],"","","","","",""])) for p in rows]
    reviewpath=out/"review/HUMAN_REVIEW.csv"
    if reviewpath.exists() and any(r["human_relation"] for r in read_csv(reviewpath)):raise ValueError("Human responses exist; refuse to overwrite")
    write_csv(out/"data/view_manifest.csv",views)
    write_csv(out/"data/spatial_splits.csv",splits)
    write_csv(out/"data/development_groups.csv",group_rows)
    write_csv(out/"data/queries.csv",qs)
    write_csv(out/"data/references.csv",rs)
    write_csv(out/"data/retrieval_pairs.csv",allpairs)
    write_csv(out/"data/query_eligibility.csv",qsum)
    write_csv(reviewpath,template,review_fields)
    write_json(out/"review/review_cases.json",rows)
    config={k:v for k,v in vars(args).items() if k!="output_dir"}
    config.update({"task_state":"DRAFT_PENDING_HUMAN_REVIEW","selection":"3 spatially separated development areas, 2 nearby distinct streets each, 9 observations per street; anchor positions 2 and 6; metadata only",
        "distance_crs":"EPSG:2154","coordinate_source":"Tile API capture coordinates","max_positives_per_query":2,
        "unselected_eligible_positives":"ignore","same_pano":"excluded","negative_rule":"distance>threshold AND different road segment AND no shared OSM endpoint",
        "ignore_policy":"mask before ranking","gallery_fixed_across_conditions":True,"images_modified":False,
        "date_filter":"none; recorded for review","baseline_allowed":False,"random_seed":args.seed})
    write_json(out/"configs/protocol.json",config)
    summary={"task_id":args.task_id,"groups":group_rows,"active_panos":len(active),"query_panos":len({q["pano_id"] for q in qs}),
        "reference_panos":len({r["pano_id"] for r in rs}),"queries":len(qs),"references":len(rs),"pairs":len(allpairs),
        "relation_counts":dict(Counter(p["relation"] for p in allpairs)),"review_cases":len(rows),
        "review_counts":dict(Counter(p["relation"] for p in rows)),"split_panos":dict(Counter(s["experiment_split"] for s in splits)),
        "minimum_eval_candidate_distance_m":min(s["min_distance_to_dev_m"] for s in splits if s["experiment_split"]=="eval_candidate"),
        "positive_month_gap":dict(Counter("same_month" if p["capture_month_gap"]==0 else ("1_to_12" if p["capture_month_gap"]<=12 else "over_12") for p in allpairs if p["relation"]=="positive")),
        "zero_positive_queries":sum(s["positive_count"]==0 for s in qsum),"human_reviews_completed":0,"baseline_ready":False,
        "road_window_candidates":len(candidates)}
    write_json(out/"task_summary.json",summary)
    log(out,"TASK COMPLETE "+json.dumps(summary,ensure_ascii=False))
    return summary
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir",type=Path,required=True);p.add_argument("--seed",type=int,default=42)
    p.add_argument("--groups",type=int,default=6);p.add_argument("--task-id",default="paris_local_v0_20260922")
    p.add_argument("--pos-min-m",type=float,default=8);p.add_argument("--pos-max-m",type=float,default=25)
    p.add_argument("--heading-max-deg",type=float,default=30);p.add_argument("--neg-min-m",type=float,default=50);p.add_argument("--buffer-m",type=float,default=100)
    args=p.parse_args()
    if hasattr(sys.stdout,"reconfigure"):sys.stdout.reconfigure(encoding="utf-8")
    build(args)
if __name__=="__main__":main()
