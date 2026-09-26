"""Validate paired human exports and derive an immutable local development task."""
from __future__ import annotations
import argparse, contextlib, io, json, shutil, sys
from collections import Counter, defaultdict
from pathlib import Path
from pilot0_local import read_csv, write_csv, write_json, digest
from pilot0_validate import check_return

def build(a):
    out=a.output_dir;draft=a.draft
    source_hashes={str(p):digest(p.read_bytes()) for p in (a.review_json,a.review_csv)}
    if out.exists() and (out/'task_manifest.json').exists():raise ValueError('Version already exists; use a new output directory')
    capture=io.StringIO()
    with contextlib.redirect_stdout(capture):code=check_return(draft,a.review_json)
    gate=json.loads(capture.getvalue())
    if code or not gate['all_fields_complete']:raise ValueError(gate)
    original=json.loads(a.review_json.read_text(encoding='utf-8-sig'))
    rows=original['responses'];csvrows=read_csv(a.review_csv)
    if rows!=csvrows:raise ValueError('CSV and JSON responses differ')
    cases=json.loads((draft/'review/review_cases.json').read_text(encoding='utf-8'))
    cm={c['review_case_id']:c for c in cases};rm={r['pair_id']:r for r in rows}
    # Reviewed in the current session: genuine shared content outside the proposal radius.
    overrides={'R123':'Shared street-end building/red awning and right-hand street wall; 32.5m correspondence confirmed by human review and card recheck.',
               'R125':'Same Petit Bateau shop/sign at opposite frame edges and adjoining facade; 27.2m partial overlap confirmed by human review and card recheck.'}
    actual={c['case_id'] for c in gate['rule_review_required']}
    if actual!=set(overrides):raise ValueError('Unexpected policy dispute; do not silently apply new exceptions')
    triage=json.loads((draft/'review/codex_visual_notes.json').read_text(encoding='utf-8'))
    pairs=read_csv(draft/'data/retrieval_pairs.csv');qs=read_csv(draft/'data/queries.csv');refs=read_csv(draft/'data/references.csv')
    frozen=[];audit=[]
    for row in rows:
        adopted=row['evidence'].startswith('认可预审')
        audit.append({**row,'human_evidence_raw':row['evidence'],'pre_review_note':triage['notes'].get(row['case_id'],''),'effective_evidence':triage['notes'][row['case_id']] if adopted else row['evidence'],'evidence_mode':'human_endorsed_codex_note' if adopted else 'human_entered_reason','review_context':'single_human_with_optional_codex_hints','boundary_override':row['case_id'] in overrides})
    for p in pairs:
        x=dict(p);review=rm.get(p['pair_id']);x['draft_relation']=p['relation']
        x['human_relation']='';x['reviewer']='';x['human_overlap']='';x['human_quality']='';x['human_evidence_raw']='';x['effective_evidence']='';x['boundary_override']=False
        if review:
            x['relation']=review['human_relation'];x['human_relation']=review['human_relation'];x['reviewer']=review['reviewer'];x['human_overlap']=review['overlap'];x['human_quality']=review['quality'];x['human_evidence_raw']=review['evidence']
            x['effective_evidence']=triage['notes'][review['case_id']] if review['evidence'].startswith('认可预审') else review['evidence']
            x['review_status']='human_reviewed';x['label_source']='human_review_with_codex_assistance'
            if review['case_id'] in overrides:
                x['boundary_override']=True;x['reason']='human_confirmed_visual_overlap_beyond_proposal_radius'
            elif x['relation']!=p['relation']:x['reason']='human_rejected_positive_conservatively_ignored'
        x['protocol_version']=a.task_id
        frozen.append(x)
    totals=defaultdict(Counter)
    for p in frozen:totals[p['query_view_id']][p['relation']]+=1
    eligible={q['view_id'] for q in qs if totals[q['view_id']]['positive'] and totals[q['view_id']]['negative']}
    dropped=[];kept=[]
    for q in qs:
        if q['view_id'] not in eligible:
            dropped.append({'query_view_id':q['view_id'],'pano_id':q['pano_id'],'dev_group_id':q['dev_group_id'],'view_index':q['view_index'],'reason':'no_human_confirmed_positive','review_case_ids':'|'.join(c['review_case_id'] for c in cases if c['query_view_id']==q['view_id'] and c['relation']=='positive')})
        else:kept.append({**q,'task_id':a.task_id})
    for p in frozen:p['scoring_allowed']=p['query_view_id'] in eligible and p['relation']!='ignore'
    active=[p for p in frozen if p['query_view_id'] in eligible]
    assert len(rows)==132 and len(eligible)==44 and len(active)==7392
    assert Counter(p['relation'] for p in active)==Counter(positive=82,negative=6160,ignore=1150)
    assert {(p['query_view_id'],p['reference_view_id']) for p in active}=={(q['view_id'],r['view_id']) for q in kept for r in refs}
    assert not {q['pano_id'] for q in kept}&{r['pano_id'] for r in refs}
    assert all(p['review_status']=='human_reviewed' for p in active if p['relation']=='positive')
    assert all(not p['scoring_allowed'] for p in active if p['relation']=='ignore')
    assert all(float(p['distance_m'])<=25 or p['boundary_override'] for p in active if p['relation']=='positive')
    assert Counter(p['relation'] for p in frozen)==Counter(positive=82,negative=6720,ignore=1262)
    assert all(r['human_relation']=='negative' for r in rows if r['proposed_relation']=='negative')
    for name in ('data','configs','review_inputs','review','validation'): (out/name).mkdir(parents=True,exist_ok=True)
    shutil.copyfile(a.review_json,out/'review_inputs/HUMAN_REVIEW.json');shutil.copyfile(a.review_csv,out/'review_inputs/HUMAN_REVIEW.csv')
    write_json(out/'review_inputs/source_provenance.json',{'source_sha256':source_hashes,'exported_at':original['exported_at'],'draft_task_id':original['task_id'],'draft_review_fingerprint':original['review_fingerprint'],'CSV_JSON_exact_response_match':True})
    write_json(out/'validation/review_return_gate.json',gate)
    write_json(out/'review/boundary_adjudication.json',{'decision':'Accept only the two individually reviewed visual correspondences; do not widen the global 25m candidate threshold.','cases':[{**cm[k],'adjudication':v} for k,v in overrides.items()]})
    write_csv(out/'review/pair_audit.csv',audit)
    write_csv(out/'data/queries.csv',kept);write_csv(out/'data/references.csv',[{**r,'task_id':a.task_id} for r in refs]);write_csv(out/'data/retrieval_pairs.csv',active)
    write_csv(out/'data/all_48_queries_reviewed_pairs.csv',frozen);write_csv(out/'data/excluded_queries.csv',dropped)
    views=read_csv(draft/'data/view_manifest.csv')
    for v in views:
        if v['view_id'] in eligible or v['retrieval_role']=='reference':v['task_id']=a.task_id
        elif v['retrieval_role']=='query':v['retrieval_role']='excluded_query';v['task_id']=a.task_id
    write_csv(out/'data/view_manifest.csv',views)
    for name in ('spatial_splits.csv','development_groups.csv'):
        shutil.copyfile(draft/'data'/name,out/'data'/name)
    write_csv(out/'data/query_eligibility.csv',[{'query_view_id':q['view_id'],'pano_id':q['pano_id'],'dev_group_id':q['dev_group_id'],'area_group':'A'+str((int(q['dev_group_id'][1:])+1)//2),'positive_count':totals[q['view_id']]['positive'],'negative_count':totals[q['view_id']]['negative'],'ignore_count':totals[q['view_id']]['ignore'],'effective_gallery_size':totals[q['view_id']]['positive']+totals[q['view_id']]['negative'],'ready_for_baseline':q['view_id'] in eligible} for q in qs])
    shutil.copyfile(draft/'configs/paths.example.json',out/'configs/paths.example.json')
    protocol=json.loads((draft/'configs/protocol.json').read_text());protocol.update({'task_id':a.task_id,'parent_task_id':original['task_id'],'task_state':'FROZEN_DEV_READY_FOR_BASELINE','baseline_allowed':True,'scope':'single_rater_assisted_development_pilot_not_held_out_benchmark','positive_policy':'human_confirmed_overlap; two explicitly adjudicated radius exceptions','max_positives_per_query':3,'same_pano':'excluded','rejected_positive_policy':'ignore','negative_evidence':'geometry_rule_with_24_human_audited_pairs; not exhaustive human validation','tie_policy':'sort descending float32 cosine, then ascending reference_view_id; report tie_count','sensitivity':'secondary: treat only R123/R125 as ignore; same 44 queries and same reference gallery; never negative','split_note':'spatial_splits.csv preserves pano-level allocation; query_eligibility.csv gives view-level exclusions'})
    write_json(out/'configs/protocol.json',protocol)
    gallery='gallery_'+digest(json.dumps(sorted((v['view_id'],v['image_sha256']) for v in refs)).encode())[:20]
    summary={'task_id':a.task_id,'review_complete':132,'reviewers':dict(Counter(r['reviewer'] for r in rows)),'review_confusion':dict(Counter(r['proposed_relation']+'->'+r['human_relation'] for r in rows)),'raw_human_relation_counts':dict(Counter(r['human_relation'] for r in rows)),'human_endorsed_codex_notes':sum(r['evidence'].startswith('认可预审') for r in rows),'query_views':len(kept),'query_panos':len({q['pano_id'] for q in kept}),'references':len(refs),'reference_panos':len({r['pano_id'] for r in refs}),'pairs':len(active),'relation_counts':dict(Counter(p['relation'] for p in active)),'positive_counts_per_query':dict(Counter(totals[q['view_id']]['positive'] for q in kept)),'query_counts_by_group':dict(Counter(q['dev_group_id'] for q in kept)),'excluded_queries':dropped,'positive_review_overlap':dict(Counter(p['human_overlap'] for p in active if p['relation']=='positive')),'boundary_overrides':['R123','R125'],'gallery_id':gallery,'baseline_ready':True,'scientific_generalization_validated':False,'negative_human_reviewed_active_pairs':sum(p['relation']=='negative' and p['review_status']=='human_reviewed' for p in active),'active_images':len(kept)+len(refs),'structural_checks_passed':True,'draft_unchanged':True,'model_results_available':False}
    write_json(out/'review_summary.json',summary)
    hashes={p.relative_to(out).as_posix():digest(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file()}
    write_json(out/'task_manifest.json',{'task_id':a.task_id,'parent_task_id':original['task_id'],'task_state':'FROZEN_DEV_READY_FOR_BASELINE','gallery_id':gallery,'baseline_allowed':True,'human_reviews_completed':132,'query_views':44,'references':168,'pairs':7392,'hashes':hashes,'code_sha256':digest(Path(__file__).read_bytes()),'scientific_scope':'exploratory development only; Paris evaluation not frozen','source_review_sha256':source_hashes})
    assert all(digest(Path(p).read_bytes())==h for p,h in source_hashes.items())
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--draft',type=Path,required=True);p.add_argument('--review-json',type=Path,required=True);p.add_argument('--review-csv',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--task-id',default='paris_local_v1_20260923')
    a=p.parse_args();sys.stdout.reconfigure(encoding='utf-8');build(a)
