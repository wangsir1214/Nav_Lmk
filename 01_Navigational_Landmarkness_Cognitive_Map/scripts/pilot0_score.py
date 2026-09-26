"""Score cached full-image VLAD features using frozen P/N/I labels and tie policy."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import numpy as np


def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    if not rows:
        raise ValueError('Cannot write an empty result')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def summarize(rows, score_key, output):
    good=[r for r in rows if r.get('valid','True')=='True']
    values=np.asarray([float(r[score_key]) for r in good],dtype=np.float64)
    groups={}
    for key in ('road_group','area_id','pano_id'):
        bucket={}
        for r in good:bucket.setdefault(r.get(key,'unknown'),[]).append(r)
        groups[key]={g:{'n':len(v),'success_at_1':sum(int(x['recall_at_1']) for x in v),
                        'success_at_5':sum(int(x['recall_at_5']) for x in v),
                        'success_at_10':sum(int(x['recall_at_10']) for x in v),
                        'mean_margin':float(np.mean([float(x['margin']) for x in v]))}
                     for g,v in bucket.items()}
    return {'n_queries':len(rows),'n_valid':len(good),
            'success_count':{f'recall_at_{k}':sum(int(r[f'recall_at_{k}']) for r in good) for k in (1,5,10)},
            'success_rate':{f'recall_at_{k}':float(np.mean([int(r[f"recall_at_{k}"]) for r in good])) for k in (1,5,10)},
            'margin':{'median':float(np.median(values)),'q25':float(np.quantile(values,.25)),
                      'q75':float(np.quantile(values,.75)),'min':float(values.min()),'max':float(values.max())},
            'groups':groups,'protocol':'at_least_one_positive_in_top_k; ignore_masked; score_ties_by_reference_view_id'}


def evaluate(queries, references, pairs, features, *, exclude_exceptions=False):
    qids=[r['view_id'] for r in queries];rids=[r['view_id'] for r in references]
    qpanos={r['view_id']:r['pano_id'] for r in queries}; rpanos={r['view_id']:r['pano_id'] for r in references}
    if len(set(qids))!=len(qids) or len(set(rids))!=len(rids) or set(qpanos.values()) & set(rpanos.values()):
        raise ValueError('Duplicate IDs or query/reference pano leakage')
    if any(x not in features for x in qids+rids):raise ValueError('Feature ID missing')
    dim={np.asarray(features[x]).shape for x in qids+rids}
    if len(dim)!=1 or len(next(iter(dim)))!=1:raise ValueError('Expected same-dimensional 1D vectors for every view')
    mat=np.stack([features[x] for x in qids]) @ np.stack([features[x] for x in rids]).T
    if not np.isfinite(mat).all():raise ValueError('Non-finite similarity')
    norms=np.linalg.norm(np.stack([features[x] for x in qids+rids]),axis=1)
    if np.any(norms==0) or np.any(np.abs(norms-1)>1e-5):raise ValueError('Cosine scoring requires verified unit-normalized VLAD vectors')
    relations={(p['query_view_id'],p['reference_view_id']):p for p in pairs}
    if len(relations)!=len(pairs) or len(relations)!=len(queries)*len(references):raise ValueError('Pair matrix incomplete or duplicated')
    positions={q:i for i,q in enumerate(qids)};col={r:i for i,r in enumerate(rids)}
    query_rows=[];pair_scores=[];rankings=[];hard=[]
    for q in qids:
        i=positions[q];all_items=[]
        for ref in rids:
            p=relations[(q,ref)];rel=p['relation']
            if exclude_exceptions and p.get('review_case_id') in {'R123','R125'}:rel='ignore'
            score=float(mat[i,col[ref]])
            item={'query_view_id':q,'reference_view_id':ref,'relation':rel,'score':score,'scoring_allowed':rel in ('positive','negative'),'pair':p}
            pair_scores.append({'query_view_id':q,'reference_view_id':ref,'relation':rel,'scoring_allowed':str(item['scoring_allowed']),'cosine_similarity':format(score,'.9g'),'review_case_id':p.get('review_case_id',''),'distance_m':p.get('distance_m',''),'boundary_override':p.get('boundary_override','False')})
            all_items.append(item)
        eligible=[x for x in all_items if x['scoring_allowed']]
        pos=[x for x in eligible if x['relation']=='positive']; neg=[x for x in eligible if x['relation']=='negative']
        if not pos or not neg:raise ValueError('Query lacks positive or negative: '+q)
        # Reference ID is an explicit deterministic secondary key for exact score ties.
        ranked=sorted(eligible,key=lambda x:(-x['score'],x['reference_view_id']))
        for rank,x in enumerate(ranked,1):x['rank']=rank
        best_pos=sorted(pos,key=lambda x:(-x['score'],x['reference_view_id']))[0]
        best_neg=sorted(neg,key=lambda x:(-x['score'],x['reference_view_id']))[0]
        rp=min(x['rank'] for x in pos)
        qrow=next(x for x in queries if x['view_id']==q)
        success={k:int(rp<=k) for k in (1,5,10)}
        query_rows.append({'query_view_id':q,'pano_id':qrow['pano_id'],'road_group':qrow.get('dev_group_id',''),
                           'area_id':qrow.get('area_id',''),'positive_count':len(pos),'negative_count':len(neg),
                           'ignore_count':len(all_items)-len(eligible),'best_positive_rank':rp,
                           'top1_reference_id':ranked[0]['reference_view_id'],'top1_relation':ranked[0]['relation'],
                           **{f'recall_at_{k}':success[k] for k in success},
                           'best_positive_id':best_pos['reference_view_id'],'best_positive_score':format(best_pos['score'],'.9g'),
                           'best_negative_id':best_neg['reference_view_id'],'best_negative_score':format(best_neg['score'],'.9g'),
                           'margin':format(best_pos['score']-best_neg['score'],'.9g'),'exact_top_tie_count':sum(x['score']==ranked[0]['score'] for x in eligible),
                           'valid':'True'})
        rankings.append({'query_view_id':q,'ranked_scoring_gallery':[{'rank':x['rank'],'reference_view_id':x['reference_view_id'],'relation':x['relation'],'score':x['score']} for x in ranked],
                         'ignored_diagnostic':[{'reference_view_id':x['reference_view_id'],'score':x['score']} for x in all_items if x['relation']=='ignore']})
        for x in sorted([x for x in neg],key=lambda x:(-x['score'],x['reference_view_id']))[:5]:
            p=x['pair']; ref=next(r for r in references if r['view_id']==x['reference_view_id'])
            hard.append({'query_view_id':q,'reference_view_id':x['reference_view_id'],'score':format(x['score'],'.9g'),
                         'distance_m':p.get('distance_m',''),'heading_difference_deg':p.get('heading_diff_deg',''),
                         'query_road_group':qrow.get('dev_group_id',''),'query_area_id':qrow.get('area_id',''),
                         'reference_road_group':p.get('reference_dev_group_id',ref.get('dev_group_id','')),'reference_area_id':ref.get('area_id',''),
                         'reference_capture_date':ref.get('capture_date',''),'review_case_id':p.get('review_case_id','')})
    return query_rows,pair_scores,rankings,hard


def run(a):
    manifest=json.loads((a.feature_dir/'run_config.json').read_text(encoding='utf-8'))
    if manifest.get('request',{}).get('request_id')!='full_image_g14_l31_value_c32_urban_448png_fp32_v2':
        raise ValueError('Feature cache was not produced under the frozen v2 request')
    task_manifest=json.loads((a.task_dir/'task_manifest.json').read_text(encoding='utf-8'))
    if manifest.get('request',{}).get('task_id')!=task_manifest['task_id']:
        raise ValueError('Feature cache task ID mismatch')
    index=a.feature_dir/'feature_index.csv'
    if hashlib.sha256(index.read_bytes()).hexdigest()!=manifest['feature_index_sha256']:
        raise ValueError('Feature index SHA-256 mismatch')
    features={}
    with (a.feature_dir/'feature_index.csv').open(encoding='utf-8-sig',newline='') as f:
        for row in csv.DictReader(f):
            vector=np.load(row['vlad_path'],allow_pickle=False)
            if vector.shape!=(49152,) or row['view_id'] in features:raise ValueError('Invalid or duplicate feature entry')
            if hashlib.sha256(Path(row['vlad_path']).read_bytes()).hexdigest()!=row['vlad_sha256']:
                raise ValueError('Feature file SHA-256 mismatch: '+row['view_id'])
            features[row['view_id']]=vector.astype(np.float32,copy=False)
    qs=read_csv(a.task_dir/'data/queries.csv');refs=read_csv(a.task_dir/'data/references.csv');pairs=read_csv(a.task_dir/'data/retrieval_pairs.csv')
    if set(features)!={r['view_id'] for r in qs+refs}:
        raise ValueError('Feature index IDs do not exactly match the frozen active task')
    main=evaluate(qs,refs,pairs,features)
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    names=('baseline_per_query.csv','pair_scores.csv','retrieval_rankings.jsonl','hard_negative_review.csv')
    for name,rows in zip(names,main):
        path=out/name
        if name.endswith('.jsonl'):
            with path.open('x',encoding='utf-8') as f:
                for row in rows:f.write(json.dumps(row,ensure_ascii=False)+'\n')
        else:write_csv(path,rows)
    baseline_summary=summarize(main[0],'margin',out)
    (out/'baseline_summary.json').write_text(json.dumps(baseline_summary,indent=2)+'\n',encoding='utf-8')
    margins=np.asarray([float(r['margin']) for r in main[0]])
    threshold=float(np.quantile(margins,.25))
    low=[r for r in main[0] if int(r['recall_at_1'])==0 or float(r['margin'])<=threshold]
    write_csv(out/'failure_and_low_margin_queries.csv',low)
    sensitivity=evaluate(qs,refs,pairs,features,exclude_exceptions=True)
    write_csv(out/'boundary_sensitivity_per_query.csv',sensitivity[0])
    (out/'boundary_sensitivity_summary.json').write_text(json.dumps(summarize(sensitivity[0],'margin',out),indent=2)+'\n',encoding='utf-8')
    result_files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file() and p.name!='result_manifest.json'}
    result_manifest={'task_id':task_manifest['task_id'],'request_id':manifest['request']['request_id'],
                     'feature_config_sha256':hashlib.sha256((a.feature_dir/'run_config.json').read_bytes()).hexdigest(),
                     'task_manifest_sha256':hashlib.sha256((a.task_dir/'task_manifest.json').read_bytes()).hexdigest(),
                     'low_margin_threshold':threshold,'low_margin_rule':'all Recall@1 failures plus margins at or below the fixed empirical 25th percentile; descriptive only',
                     'files_sha256':result_files}
    (out/'result_manifest.json').write_text(json.dumps(result_manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':True,'queries':len(main[0]),'pairs_scored':len(main[1]),
                      'baseline':baseline_summary['success_count'],
                      'boundary_sensitivity':summarize(sensitivity[0],'margin',out)['success_count'],
                      'features':len(features),'feature_config':manifest['request']['request_id']},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--task-dir',type=Path,required=True);p.add_argument('--feature-dir',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);run(p.parse_args())
