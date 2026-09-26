"""Validate a reviewed task with the Python standard library; no model/image loading."""
import argparse, csv, hashlib, json, math
from collections import Counter, defaultdict
from pathlib import Path

def csvrows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(out):
    manifest=json.loads((out/'task_manifest.json').read_text());cfg=json.loads((out/'configs/protocol.json').read_text());checks=[]
    def check(k,v):checks.append({'check':k,'passed':bool(v)})
    check('all_frozen_input_hashes',all((out/k).is_file() and sha(out/k)==v for k,v in manifest['hashes'].items()))
    qs=csvrows(out/'data/queries.csv');refs=csvrows(out/'data/references.csv');pairs=csvrows(out/'data/retrieval_pairs.csv');allpairs=csvrows(out/'data/all_48_queries_reviewed_pairs.csv')
    audit=csvrows(out/'review/pair_audit.csv');am={r['pair_id']:r for r in audit};counts=defaultdict(Counter)
    qids={q['view_id'] for q in qs};rids={r['view_id'] for r in refs}
    check('unique_query_reference_ids',len(qids)==len(qs) and len(rids)==len(refs))
    check('query_reference_panos_disjoint',not {q['pano_id'] for q in qs}&{r['pano_id'] for r in refs})
    check('full_unique_cartesian',len(pairs)==len(qs)*len(refs) and {(p['query_view_id'],p['reference_view_id']) for p in pairs}=={(q,r) for q in qids for r in rids})
    for p in pairs:counts[p['query_view_id']][p['relation']]+=1
    check('P_and_N_for_every_query',all(c['positive'] and c['negative'] for c in counts.values()) and len(counts)==len(qs))
    check('only_P_N_scored',all((p['scoring_allowed']=='True')==(p['relation'] in ('positive','negative')) for p in pairs))
    check('all_P_have_complete_human_confirmation',all(p['pair_id'] in am and am[p['pair_id']]['human_relation']=='positive' and am[p['pair_id']]['overlap'] in ('clear','partial') and am[p['pair_id']]['quality']=='usable' and am[p['pair_id']]['reviewer'].strip() and am[p['pair_id']]['evidence'].strip() for p in pairs if p['relation']=='positive'))
    check('human_labels_applied_exactly',all(p['relation']==am[p['pair_id']]['human_relation'] for p in allpairs if p['pair_id'] in am))
    check('unreviewed_labels_unchanged',all(p['relation']==p['draft_relation'] for p in allpairs if p['pair_id'] not in am))
    check('negative_rule_preserved',all(p['draft_relation']=='negative' and p['same_segment']=='False' and p['shared_osm_endpoint']=='False' and float(p['distance_m'])>cfg['neg_min_m'] for p in pairs if p['relation']=='negative'))
    exceptions={p['review_case_id'] for p in pairs if p['boundary_override']=='True'}
    check('explicit_boundary_exceptions_only',exceptions=={'R123','R125'} and all(float(p['distance_m'])<=25 or p['review_case_id'] in exceptions for p in pairs if p['relation']=='positive'))
    exclusions=csvrows(out/'data/excluded_queries.csv');allcounts=defaultdict(Counter)
    for p in allpairs:allcounts[p['query_view_id']][p['relation']]+=1
    check('exclusion_only_no_positive',all(allcounts[x['query_view_id']]['positive']==0 and x['query_view_id'] not in qids for x in exclusions) and len(allcounts)==len(qids)+len(exclusions))
    check('manifest_counts_match',manifest['query_views']==len(qs) and manifest['references']==len(refs) and manifest['pairs']==len(pairs))
    check('baseline_enabled_for_dev_only',cfg['baseline_allowed'] is True and manifest['task_state']=='FROZEN_DEV_READY_FOR_BASELINE')
    check('source_exports_match',csvrows(out/'review_inputs/HUMAN_REVIEW.csv')==json.loads((out/'review_inputs/HUMAN_REVIEW.json').read_text(encoding='utf-8-sig'))['responses'])
    retained_P=Counter(p['query_view_id'] for p in pairs if p['relation']=='positive' and p['review_case_id'] not in exceptions)
    check('sensitivity_keeps_all_queries_scoreable',set(retained_P)==qids and sum(retained_P.values())==80)
    gallery='gallery_'+hashlib.sha256(json.dumps(sorted((v['view_id'],v['image_sha256']) for v in refs)).encode()).hexdigest()[:20]
    check('reference_gallery_identity_matches',gallery==manifest['gallery_id'])
    chance={}
    for k in (1,5,10):chance['random_success_at_'+str(k)]=sum(1-math.comb(c['negative'],k)/math.comb(c['positive']+c['negative'],k) for c in counts.values())/len(counts)
    result={'passed':all(x['passed'] for x in checks),'checks':checks,'counts':dict(Counter(p['relation'] for p in pairs)),'queries':len(qs),'references':len(refs),'excluded_queries':len(exclusions),'random_ranking_expectation':chance,'note':'Random-rank expectation is analytical, not a DINOv2 result. No images or model weights loaded.'}
    dest=out/'validation/frozen_task_validation.json';dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if not result['passed']:raise SystemExit(1)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--task-dir',type=Path,required=True);a=p.parse_args();verify(a.task_dir)
