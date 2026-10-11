"""Score masked-query retrieval against frozen P/N/I and the saved Full scores."""
from __future__ import annotations
import argparse, csv, json, math, statistics
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PREP=ROOT/'outputs/pilot0/phase0_intervention_prep_20261011'
TASK=ROOT/'outputs/pilot0/reviewed_v1_20260923/data'
FULL=ROOT/'outputs/pilot0/server_return_audit_20260924/source/baseline_g14_v2/pair_scores.csv'
VARIANTS=('candidate','control1','control2','control3')

def rows(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as handle:
        return list(csv.DictReader(handle))

def score(values,labels):
    if values.keys()!=labels.keys() or len(values)!=168: raise ValueError('Incomplete gallery')
    ranked=sorted(((-v,rid,labels[rid]) for rid,v in values.items() if labels[rid] in ('positive','negative')))
    pos=[-s for s,_,rel in ranked if rel=='positive']
    neg=[-s for s,_,rel in ranked if rel=='negative']
    if not pos or not neg: raise ValueError('Missing P/N')
    return {'margin':max(pos)-max(neg),'rank':next(i for i,(_,_,rel) in enumerate(ranked,1) if rel=='positive'),
            'top1_id':ranked[0][1],'top1_correct':ranked[0][2]=='positive'}

def evaluate(mask_rows,selection,pairs,full_rows):
    chosen={r['query_view_id']:r for r in selection['queries']}
    labels={qid:{} for qid in chosen}; full={qid:{} for qid in chosen}; masked={}
    for r in pairs:
        qid,ref=r['query_view_id'],r['reference_view_id']
        if qid in labels:
            if ref in labels[qid]: raise ValueError('Duplicate label')
            labels[qid][ref]=r['relation']
    for r in full_rows:
        qid,ref=r['query_view_id'],r['reference_view_id']
        if qid in full:
            if ref in full[qid]: raise ValueError('Duplicate Full')
            full[qid][ref]=float(r['cosine_similarity'])
    for r in mask_rows:
        qid,variant,ref=r['query_view_id'],r['variant'],r['reference_view_id']
        if qid not in chosen or variant not in VARIANTS or ref not in labels[qid]:
            raise ValueError('Unexpected masked pair')
        value=float(r['cosine_similarity'])
        if not math.isfinite(value) or abs(value)>1.00001: raise ValueError('Invalid cosine')
        part=masked.setdefault((qid,variant),{})
        if ref in part: raise ValueError('Duplicate masked pair')
        part[ref]=value
    if not masked: raise ValueError('No masked pairs')
    output=[]
    for qid in sorted({q for q,_ in masked}):
        if any((qid,v) not in masked or len(masked[(qid,v)])!=168 for v in VARIANTS):
            raise ValueError('Incomplete four-variant set for '+qid)
        original=score(full[qid],labels[qid]); item=chosen[qid]
        if original['rank']!=item['baseline_positive_rank']: raise ValueError('Full rank mismatch')
        tests={v:score(masked[(qid,v)],labels[qid]) for v in VARIANTS}
        control_mean=statistics.mean(tests[v]['margin'] for v in VARIANTS[1:])
        output.append({'query_view_id':qid,'pano_id':item['pano_id'],'road_group':item['road_group'],
          'analysis_role':item['analysis_role'],'difficulty':item['baseline_difficulty'],
          'full_margin':original['margin'],'full_positive_rank':original['rank'],
          'candidate_margin':tests['candidate']['margin'],'candidate_positive_rank':tests['candidate']['rank'],
          'control1_margin':tests['control1']['margin'],'control2_margin':tests['control2']['margin'],
          'control3_margin':tests['control3']['margin'],'delta_candidate':original['margin']-tests['candidate']['margin'],
          'u_candidate_minus_controls':control_mean-tests['candidate']['margin'],
          'candidate_top1_flip':original['top1_id']!=tests['candidate']['top1_id'],
          'candidate_correct_to_wrong':original['top1_correct'] and not tests['candidate']['top1_correct'],
          'controls_correct_count':sum(tests[v]['top1_correct'] for v in VARIANTS[1:])})
    return output

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--masked-scores',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    a=p.parse_args()
    if a.output_dir.exists() and any(a.output_dir.iterdir()): raise FileExistsError('Use fresh directory')
    selection=json.loads((PREP/'selection_manifest.json').read_text(encoding='utf-8'))
    result=evaluate(rows(a.masked_scores),selection,rows(TASK/'retrieval_pairs.csv'),rows(FULL))
    a.output_dir.mkdir(parents=True,exist_ok=True)
    with (a.output_dir/'paired_effects.csv').open('x',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(result[0])); writer.writeheader(); writer.writerows(result)
    summary={'status':'DESCRIPTIVE_PHASE0_RESULTS','scored_views':len(result),
      'scored_panos':len({r['pano_id'] for r in result}),
      'primary_full_correct':sum(r['analysis_role']=='primary_full_correct' for r in result),
      'diagnostic_full_failed':sum(r['analysis_role']=='diagnostic_full_failure' for r in result),
      'note':'Report missing proposals and QC failures separately; views are dependent within pano and road'}
    (a.output_dir/'analysis_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
