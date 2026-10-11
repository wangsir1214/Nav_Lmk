#!/usr/bin/env python3
"""Whitelist one lightweight Stage A result snapshot for an isolated Git branch."""
import datetime,hashlib,json,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;IDENT=json.loads((HERE/'identity.json').read_text())
RUN=IDENT['run_id'];OUT=Path(IDENT['nas_output_dir']);REPO=Path(IDENT['isolated_checkout'])
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 metadata=json.loads((OUT/'run_metadata.json').read_text());stage=json.loads((OUT/'stage_status.json').read_text())
 if metadata['status']!='COMPLETE' or stage['state']!='COMPLETE':raise RuntimeError('Stage A is not complete')
 proposals=[json.loads(x) for x in (OUT/'proposals.jsonl').read_text().splitlines()]
 requests=[json.loads(x) for x in (OUT/'actual_requests.jsonl').read_text().splitlines()]
 if len(proposals)!=20 or len({x['query_view_id'] for x in proposals})!=20:raise RuntimeError('Expected 20 unique proposal records')
 if len(requests)!=20+metadata['counts']['format_retries']:raise RuntimeError('Request/format-retry count mismatch')
 for rec in proposals:
  if rec['status'] not in ('SUCCESS','EMPTY','FORMAT_FAILED'):raise RuntimeError('Unknown proposal status')
  for field,hashfield in [('raw_output_path','raw_output_sha256'),('overlay_path','overlay_sha256')]:
   p=Path(rec[field])
   if not p.is_file() or sha(p)!=rec[hashfield]:raise RuntimeError('Missing or mismatched NAS asset: '+str(p))
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 dest=REPO/'01_Navigational_Landmarkness_Cognitive_Map'/'server_returns'/RUN/stamp
 dest.mkdir(parents=True,exist_ok=False)
 allowed_nas=['identity.json','preflight.json','run_metadata.json','actual_requests.jsonl','proposals.jsonl','HUMAN_REVIEW_REQUIRED.csv','RUN_SUMMARY.md','stage_status.json','validation.json','events.jsonl','errors.jsonl']
 allowed_light=['preflight.py','runner.py','qwen_json_parser.py','export_stage_a.py','preflight_summary.json']
 copied=[]
 for name in allowed_nas:
  p=OUT/name
  if p.is_file():
   if p.stat().st_size>2_000_000:raise RuntimeError('Oversized export file: '+str(p))
   shutil.copy2(p,dest/name);copied.append(dest/name)
 for name in allowed_light:
  p=HERE/name
  if p.is_file():
   if p.stat().st_size>100_000:raise RuntimeError('Oversized code file: '+str(p))
   shutil.copy2(p,dest/name);copied.append(dest/name)
 for p in sorted((OUT/'raw_outputs').glob('*.txt')):
  if p.stat().st_size>20_000:raise RuntimeError('Oversized raw reply: '+str(p))
  target=dest/'raw_outputs'/p.name;target.parent.mkdir(exist_ok=True);shutil.copy2(p,target);copied.append(target)
 if sum(p.stat().st_size for p in copied)>5_000_000:raise RuntimeError('Lightweight export exceeds 5 MB')
 pre=json.loads((OUT/'preflight.json').read_text())
 assets=[{'absolute_path':r['image_path'],'size_bytes':r['size_bytes'],'sha256':r['actual_sha256'],'kind':'source_query_jpeg'} for r in pre['images']]
 for r in proposals:
  for field,hashfield,kind in [('raw_output_path','raw_output_sha256','raw_model_reply'),('overlay_path','overlay_sha256','review_overlay')]:
   p=Path(r[field]);assets.append({'absolute_path':str(p),'size_bytes':p.stat().st_size,'sha256':r[hashfield],'kind':kind})
 files=[{'relative_path':str(p.relative_to(dest)),'size_bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(copied)]
 manifest={'run_id':RUN,'export_utc':stamp,'status':'complete','source_commit':IDENT['source_commit'],'actual_main_head':IDENT['actual_main_head'],'branch':'server-results/'+RUN,'nas_result_dir':str(OUT),'windows_mapping':'/home/nas/wangyq = Z:\\wangyq','counts':metadata['counts'],'exported_files':files,'nas_assets':assets,'no_images_weights_cache_or_mask_uploaded':True,'stage_scope':'Stage A proposals only; no controls, masking, DINO, retrieval'}
 (dest/'export_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
 result={'run_id':RUN,'export_utc':stamp,'export_dir':str(dest),'files':len(files)+1,'total_bytes':sum(p.stat().st_size for p in copied)+(dest/'export_manifest.json').stat().st_size}
 (HERE/'export_location.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result))
if __name__=='__main__':main()
