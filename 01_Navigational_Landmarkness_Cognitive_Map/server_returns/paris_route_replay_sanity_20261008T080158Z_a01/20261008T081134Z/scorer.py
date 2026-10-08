#!/usr/bin/env python3
"""Independent post-inference scorer. Do not import this module from runner.py."""
import csv,datetime,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
IDENTITY=json.loads((HERE/'identity.json').read_text())
OUT=Path(IDENTITY['nas_output_dir']);PACKAGE=Path(IDENTITY['source_clone'])/IDENTITY['package_rel']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 meta=json.loads((OUT/'run_metadata.json').read_text())
 if meta['status']!='INFERENCE_COMPLETE':raise RuntimeError('Scorer must run after inference completes')
 # Gold is opened only here, in a separate process after the model is no longer running.
 gold_path=PACKAGE/'scorer_gold_v1.json';gold=json.loads(gold_path.read_text())
 records=gold['questions']
 gold_map={r['question_id']:r.get('gold_action',r.get('action',r.get('accepted_action'))) for r in records}
 expected=['q_main02_decision_step3','q_main06_decision_step3']
 if set(gold_map)!=set(expected) or any(a not in ('LEFT','RIGHT','FORWARD') for a in gold_map.values()):raise RuntimeError('Gold schema/values mismatch')
 rows=[json.loads(line) for line in (OUT/'predictions.jsonl').read_text().splitlines()]
 keys={(r['question_id'],r['condition']) for r in rows}
 if len(rows)!=6 or len(keys)!=6:raise RuntimeError('Expected six unique main-request prediction records')
 out=[]
 for r in rows:
  action=r['action'] if r['status']=='VALID' else None
  category='FORMAT_FAILED' if r['status']!='VALID' else ('UNSURE' if action=='UNSURE' else ('CORRECT' if action==gold_map[r['question_id']] else 'INCORRECT'))
  out.append({'question':r['question_id'],'condition':r['condition'],'gold':gold_map[r['question_id']],'prediction':action or '', 'category':category,'attempts':r['attempts'],'status':r['status']})
 with (OUT/'sanity_results.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['question','condition','gold','prediction','category','attempts','status']);w.writeheader();w.writerows(out)
 table=[]
 for qid in expected:
  rr={r['condition']:r for r in out if r['question']==qid}
  table.append(f"| {qid} | {gold_map[qid]} | {rr['Full']['prediction'] or 'FORMAT_FAILED'} | {rr['NoDemo']['prediction'] or 'FORMAT_FAILED'} | {rr['NoCurrent']['prediction'] or 'FORMAT_FAILED'} |")
 retries=sum(r['attempts']-1 for r in rows);fail=sum(r['status']!='VALID' for r in rows)
 status='SUCCESS' if fail==0 else 'PARTIAL'
 summary=['# Route-replay two-question sanity','',f"Run: `{IDENTITY['run_id']}`",f"Status: **{status}**",f"Source commit: `{IDENTITY['source_commit']}`",f"Model revision: `{meta['model_revision']}`",'','| question | gold | Full | NoDemo | NoCurrent |','|---|---|---|---|---|',*table,'',f'Main requests: 6; format retries: {retries}; format failures: {fail}.','', 'This is a two-question task/interface sanity check. One accepted decision point per route and no within-demonstration action diversity mean NoCurrent correctness could reflect route-level shortcuts. NoDemo and NoCurrent diagnose missing information; neither measures complete navigation. No landmark functional value, cognitive-map property, or general navigation accuracy is inferred.','']
 (OUT/'RUN_SUMMARY.md').write_text('\n'.join(summary))
 meta.update(status=status,scored_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scorer_sha256=sha(HERE/'scorer.py'),scorer_gold_sha256=sha(gold_path),main_requests=6,format_retries=retries,format_failures=fail)
 (OUT/'run_metadata.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'status':status,'retries':retries,'failures':fail,'rows':out},ensure_ascii=False))
if __name__=='__main__':main()
