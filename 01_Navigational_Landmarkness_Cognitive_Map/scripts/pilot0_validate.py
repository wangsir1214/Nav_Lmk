"""Independently validate the draft task, cached images and human review return."""
from __future__ import annotations
import argparse, hashlib, json, math, platform, sys
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image, __version__ as pillow_version
from pilot0_local import read_csv, write_csv, write_json, digest, dbf

def validate(out, deps):
    if deps: sys.path.insert(0, str(deps.resolve()))
    from pyproj import Geod, Transformer, __version__ as proj_version
    checks=[]
    def check(name, condition):
        checks.append({'check':name, 'passed':bool(condition)})
    vs=read_csv(out/'data/view_manifest.csv'); ps=read_csv(out/'data/pano_manifest.csv')
    qs=read_csv(out/'data/queries.csv'); rs=read_csv(out/'data/references.csv')
    pairs=read_csv(out/'data/retrieval_pairs.csv'); splits=read_csv(out/'data/spatial_splits.csv')
    vm={v['view_id']:v for v in vs}; pm={p['pano_id']:p for p in ps}
    qm={v['view_id']:v for v in qs}; rm={v['view_id']:v for v in rs}
    check('unique_full_index_3059_by_4',len(pm)==len(ps)==3059 and len(vm)==len(vs)==12236)
    byp=defaultdict(list)
    for v in vs:byp[v['pano_id']].append(v)
    check('four_indices_and_consistent_pano_role_split',all({v['view_index'] for v in a}=={'0','1','2','3'} and len({(v['experiment_split'],v['retrieval_role']) for v in a})==1 for a in byp.values()))
    check('absolute_heading_formula',all(abs(float(v['absolute_heading'])-(float(v['heading_from_api'])+90*int(v['view_index']))%360)<1e-9 for v in vs))
    check('all_filenames_found_in_targeted_listing',all(v['file_exists']=='True' for v in vs) and all(p['erp_exists']=='True' for p in ps))
    check('derived_448_not_falsely_claimed',all(v['image_448_relative_path']=='' and v['image_448_status']=='not_generated' for v in vs))
    check('query_reference_panos_disjoint',not ({v['pano_id'] for v in qs}&{v['pano_id'] for v in rs}))
    check('query_reference_copies_match_manifest',all(v==vm[v['view_id']] for v in qs+rs))
    check('active_views_only_dev',all(v['experiment_split']=='dev' for v in qs+rs))
    check('exhaustive_unique_cartesian_pairs',len(pairs)==len(qs)*len(rs) and {(p['query_view_id'],p['reference_view_id']) for p in pairs}=={(q,r) for q in qm for r in rm})
    check('unique_stable_pair_ids',len({p['pair_id'] for p in pairs})==len(pairs) and all(p['pair_id']=='pair_'+digest((p['query_view_id']+'|'+p['reference_view_id']).encode())[:14] for p in pairs))
    check('all_draft_scoring_disabled',all(p['scoring_allowed']=='False' for p in pairs))
    cfg=json.loads((out/'configs/protocol.json').read_text()); counts=Counter(p['relation'] for p in pairs)
    check('only_three_relations',set(counts)=={'positive','negative','ignore'})
    margins=[]; dist_err=[]; heading_err=[]; geod_err=[]; positive_ok=True; negative_ok=True
    geod=Geod(ellps='WGS84'); qc=defaultdict(Counter)
    neg_d=[]; pos_d=[]
    for p in pairs:
        q,r=qm[p['query_view_id']],rm[p['reference_view_id']]
        d=math.hypot(float(q['x_m'])-float(r['x_m']),float(q['y_m'])-float(r['y_m']))
        h=math.degrees(math.acos(max(-1,min(1,math.cos(math.radians(float(q['absolute_heading'])-float(r['absolute_heading'])))))))
        dist_err.append(abs(d-float(p['distance_m'])));heading_err.append(abs(h-float(p['heading_diff_deg'])))
        _,_,gd=geod.inv(float(q['capture_lon']),float(q['capture_lat']),float(r['capture_lon']),float(r['capture_lat']))
        geod_err.append(abs(d-gd))
        qc[q['view_id']][p['relation']]+=1
        if p['relation']=='positive':
            pos_d.append(d)
            positive_ok &= q['pano_id']!=r['pano_id'] and q['street_segment_id']==r['street_segment_id'] and cfg['pos_min_m']<=d<=cfg['pos_max_m'] and h<=cfg['heading_max_deg']
        if p['relation']=='negative':
            neg_d.append(d)
            negative_ok &= q['street_segment_id']!=r['street_segment_id'] and not ({q['road_u'],q['road_v']}&{r['road_u'],r['road_v']}) and d>cfg['neg_min_m']
    check('metric_distances_and_circular_headings_recomputed',max(dist_err)<1e-6 and max(heading_err)<1e-5)
    check('positive_geometry_contract',positive_ok)
    check('negative_geometry_contract',negative_ok)
    check('every_query_has_candidate_P_and_N',all(c['positive']>=1 and c['negative']>=1 for c in qc.values()))
    check('metric_vs_geodesic_within_0_5m',max(geod_err)<.5)
    trans=Transformer.from_crs(4326,2154,always_xy=True)
    check('capture_coordinate_projection',all(math.hypot(*(a-b for a,b in zip(trans.transform(float(p['capture_lon']),float(p['capture_lat'])),[float(p['x_m']),float(p['y_m'])])))<1e-6 for p in ps))
    dev=[pm[s['pano_id']] for s in splits if s['experiment_split']=='dev']
    near={p['pano_id']:min(math.hypot(float(p['x_m'])-float(a['x_m']),float(p['y_m'])-float(a['y_m'])) for a in dev) for p in ps}
    check('buffer_distance_independently_recomputed',all(abs(near[s['pano_id']]-float(s['min_distance_to_dev_m']))<1e-6 for s in splits))
    check('eval_candidate_minimum_100m_from_all_dev',all(near[s['pano_id']]>=cfg['buffer_m'] for s in splits if s['experiment_split']=='eval_candidate'))
    mapping=dbf((out/'sources/point_road.dbf').read_bytes());roads=dbf((out/'sources/road_dbf.dbf').read_bytes())
    check('road_index_osm_join_3058',len(mapping)==3058 and all(str(roads[int(p['nearest_st'])]['osmid'])==str(p['nearest__1']) and str(int(p['nearest_st']))==pm[p['panoid']]['street_segment_id'] for p in mapping))
    src=json.loads((out/'sources/source_manifest.json').read_text());source_ok=True
    for k,x in src.items():
        path=Path(x['path']) if k=='graph' else out/'sources'/(k+Path(x['path']).suffix)
        source_ok &= path.exists() and digest(path.read_bytes())==x['sha256']
    check('cached_source_hashes_match_read_time_provenance',source_ok)
    ims=read_csv(out/'review/image_validation.csv');im_ok=True;image_hashes=[]
    for v in qs+rs:
        path=out/'review'/v['review_image'];raw=path.read_bytes();h=digest(raw);image_hashes.append(h)
        with Image.open(path) as im:im.load(); im_ok &= im.size==(640,640)
        im_ok &= h==v['image_sha256'] and v['dimensions_status']=='decoded_this_run'
    check('216_selected_images_decode_and_hash',len(ims)==len(qs)+len(rs)==216 and im_ok)
    check('no_identical_bytes_across_selected_views',len(set(image_hashes))==216)
    cases=json.loads((out/'review/review_cases.json').read_text(encoding='utf-8'));human=read_csv(out/'review/HUMAN_REVIEW.csv')
    check('all_96_positives_and_36_audit_cases_in_review',len(cases)==132 and Counter(c['relation'] for c in cases)==Counter(positive=96,negative=24,ignore=12) and {c['pair_id'] for c in cases if c['relation']=='positive'}=={p['pair_id'] for p in pairs if p['relation']=='positive'})
    check('human_fields_not_prefilled',len(human)==132 and all(not r[k] for r in human for k in ('human_relation','overlap','quality','evidence','reviewer','notes')))
    check('all_cards_and_contact_sheets_present',all((out/'review/cards'/(c['review_case_id']+'.jpg')).exists() for c in cases) and all((out/'review/contact_sheets'/f'sheet_{i:02d}.jpg').exists() for i in range(1,23)))
    html=(out/'review/index.html').read_text(encoding='utf-8')
    check('html_data_embedded_and_local_links_present','__REVIEW_DATA__' not in html and all((out/p).exists() for p in ['REVIEW_GUIDE.md','review/spatial_overview.svg','review/HUMAN_REVIEW.csv']))
    check('protocol_and_summary_not_ready',cfg['baseline_allowed'] is False and not json.loads((out/'task_summary.json').read_text())['baseline_ready'])
    report={'passed':all(c['passed'] for c in checks),'checks':checks,'counts':dict(counts),'negative_kind_counts':dict(Counter(p['negative_kind'] for p in pairs if p['relation']=='negative')),'positive_distance_m':[min(pos_d),max(pos_d)],'negative_distance_m':[min(neg_d),max(neg_d)],'max_metric_geodesic_difference_m':max(geod_err),'minimum_eval_candidate_distance_m':min(near[s['pano_id']] for s in splits if s['experiment_split']=='eval_candidate'),'human_semantics_verified':False,'source_scope':'Cached small source hashes checked against read-time provenance; selected images read-only copies; no source write operations.'}
    write_json(out/'validation_report.json',report)
    write_json(out/'environment.json',{'python':sys.version,'platform':platform.platform(),'pillow':pillow_version,'pyproj':proj_version})
    print(json.dumps({k:v for k,v in report.items() if k!='checks'},ensure_ascii=False))
    if not report['passed']:print([c for c in checks if not c['passed']]);raise SystemExit(1)

def check_return(out, path):
    """Read-only semantic gate: report issues; never apply or freeze labels."""
    cases=json.loads((out/'review/review_cases.json').read_text(encoding='utf-8'));cm={c['review_case_id']:c for c in cases}
    build=json.loads((out/'review/review_build_summary.json').read_text());cfg=json.loads((out/'configs/protocol.json').read_text())
    errors=[]
    if path.suffix.lower()=='.json':
        d=json.loads(path.read_text(encoding='utf-8-sig'));rows=d.get('responses',[])
        if d.get('task_id')!=cfg['task_id'] or d.get('review_fingerprint')!=build['review_fingerprint']:errors.append('task_or_fingerprint_mismatch')
    else:rows=read_csv(path)
    seen=set();complete=0;changes=[];accepted=defaultdict(int)
    for r in rows:
        ident=r.get('case_id');c=cm.get(ident)
        if not c or ident in seen:errors.append(str(ident)+':unknown_or_duplicate');continue
        seen.add(ident)
        if any(r.get(k)!=c[k] for k in ('pair_id','query_view_id','reference_view_id')) or r.get('proposed_relation')!=c['relation']:errors.append(ident+':identity_mismatch');continue
        rel=r.get('human_relation');ov=r.get('overlap');qu=r.get('quality')
        valid=rel in ('positive','negative','ignore') and ov in ('clear','partial','none','uncertain') and qu in ('usable','limited','unusable') and bool(r.get('evidence','').strip()) and bool(r.get('reviewer','').strip())
        if rel=='positive' and (ov not in ('clear','partial') or qu!='usable'):valid=False
        if not valid:errors.append(ident+':incomplete_or_invalid');continue
        complete+=1
        if c['relation']=='positive' and rel=='positive':accepted[c['query_view_id']]+=1
        if rel!=c['relation']:changes.append({'case_id':ident,'from':c['relation'],'to':rel})
    errors.extend(k+':missing_case' for k in cm.keys()-seen)
    policy_issues=[c for c in changes if c['from']=='negative' or (c['from']=='ignore' and c['to']=='positive') or (c['from']=='positive' and c['to']=='negative')]
    result={'completed':complete,'expected':len(cases),'errors':errors,'changes':changes,'rule_review_required':policy_issues,'queries_with_accepted_candidate_positive':len(accepted),'all_fields_complete':not errors,'baseline_ready':False,'labels_applied':False,'next_action':'Reconcile disputed rule cases; rejected candidate positives conservatively become ignore; retain queries with >=1 accepted P and N; create a new frozen version only after reconciliation.'}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if not errors else 2

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--extra-deps',type=Path);p.add_argument('--review-return',type=Path)
    a=p.parse_args()
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    if a.review_return:raise SystemExit(check_return(a.output_dir,a.review_return))
    validate(a.output_dir,a.extra_deps)
if __name__=='__main__':main()
