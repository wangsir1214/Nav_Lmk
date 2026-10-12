#!/usr/bin/env python3
"""One whitelisted lightweight Stage C export; no image or feature bytes in Git."""
import csv,datetime,hashlib,json,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;IDENT=json.loads((HERE/'identity.json').read_text());RUN=IDENT['run_id'];OUT=Path(IDENT['nas_output_dir'])
REPO=Path(IDENT['isolated_checkout']);PROJ=REPO/'01_Navigational_Landmarkness_Cognitive_Map'
FROZEN=PROJ/'outputs/pilot0/stagec_frozen_20261011T172946Z';PHASE0=PROJ/'outputs/pilot0/phase0_intervention_prep_20261011'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def rows(p):
 with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def main():
 meta=json.loads((OUT/'run_metadata.json').read_text());validation=json.loads((OUT/'validation.json').read_text())
 if meta['status']!='COMPLETE' or validation['validation']!='PASS':raise RuntimeError('Refuse export before terminal validation')
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 dest=PROJ/'server_returns'/RUN/stamp;dest.mkdir(parents=True,exist_ok=False)
 sources={
 'run_identity.json':OUT/'identity.json',
 'frozen_stagec_execution_manifest.json':FROZEN/'stagec_execution_manifest.json',
 'frozen_stageb_disposition_all20.json':FROZEN/'stageb_disposition_all20.json',
 'frozen_human_qc.csv':FROZEN/'MINIMAL_HUMAN_QC_frozen.csv',
 'frozen_read_me_first.md':FROZEN/'READ_ME_FIRST.md',
 'PHASE0_PROTOCOL.md':PHASE0/'PHASE0_PROTOCOL.md',
 'phase0_intervention_geometry.py':PROJ/'scripts/phase0_intervention_geometry.py',
 'preflight.json':OUT/'preflight.json',
 'run_metadata.json':OUT/'run_metadata.json',
 'stage_status.json':OUT/'stage_status.json',
 'full_equivalence_pairwise.csv':OUT/'full_equivalence_pairwise.csv',
 'full_equivalence_report.json':OUT/'full_equivalence_report.json',
 'masked_image_manifest.csv':OUT/'masked_image_manifest.csv',
 'query_feature_manifest.csv':OUT/'query_feature_manifest.csv',
 'masked_pair_scores.csv':OUT/'masked_pair_scores.csv',
 'variant_readout.csv':OUT/'variant_readout.csv',
 'readout_per_query.csv':OUT/'readout_per_query.csv',
 'disposition_all20.csv':OUT/'disposition_all20.csv',
 'stagec_summary.json':OUT/'stagec_summary.json',
 'validation.json':OUT/'validation.json',
 'execution_diagnostics.json':OUT/'execution_diagnostics.json',
 'RUN_SUMMARY.md':OUT/'RUN_SUMMARY.md',
 'events.jsonl':OUT/'events.jsonl',
 'COMMANDS.txt':HERE/'COMMANDS.txt',
 'preflight.py':HERE/'preflight.py',
 'runner.py':HERE/'runner.py',
 'validate_outputs.py':HERE/'validate_outputs.py',
 'export_stage_c.py':HERE/'export_stage_c.py',
 'preflight.log':HERE/'preflight.log',
 'runner.log':HERE/'runner.log',
 'validation.log':HERE/'validation.log',
 }
 copied=[]
 for name,src in sources.items():
  if not src.is_file() or src.stat().st_size>5_000_000:raise RuntimeError('Missing/oversized light output: '+str(src))
  target=dest/name;shutil.copy2(src,target);copied.append(target)
 if sum(p.stat().st_size for p in copied)>12_000_000:raise RuntimeError('Export over 12 MB cap')
 pre=json.loads((OUT/'preflight.json').read_text());assets=[]
 for x in pre['image_checks']:
  assets.append({'kind':'source_query_jpeg','absolute_path':x['source_image_path'],'size_bytes':x['size_bytes'],'sha256':x['sha256']})
 for x in rows(OUT/'masked_image_manifest.csv'):
  for kind,path_key,sha_key in [('masked_640_png','masked_640_path','masked_640_sha256'),('masked_448_png','model_448_path','model_448_sha256')]:
   p=Path(x[path_key]);assets.append({'kind':kind,'absolute_path':str(p),'size_bytes':p.stat().st_size,'sha256':x[sha_key]})
 for x in rows(OUT/'query_feature_manifest.csv'):
  p=Path(x['vlad_path']);assets.append({'kind':'masked_query_vlad','absolute_path':str(p),'size_bytes':p.stat().st_size,'sha256':x['vlad_sha256']})
 gate=json.loads((OUT/'full_equivalence_report.json').read_text())
 for x in gate['cases']:
  for kind,path_key,sha_key in [('recomputed_full_png','new_full_448_png_path','new_full_448_png_sha256'),('recomputed_full_vlad','new_full_vlad_path','new_full_vlad_sha256')]:
   p=Path(x[path_key]);assets.append({'kind':kind,'absolute_path':str(p),'size_bytes':p.stat().st_size,'sha256':x[sha_key]})
 files=[{'relative_path':p.name,'size_bytes':p.stat().st_size,'sha256':sha(p)} for p in copied]
 manifest={'run_id':RUN,'export_utc':stamp,'status':'complete','source_main_head':IDENT['source_main_head'],'frozen_stagec_commit':IDENT['frozen_stagec_commit'],'stagea_result_commit':IDENT['stagea_result_commit'],'branch':'server-results/'+RUN,'nas_output_dir':str(OUT),'windows_mapping':'/home/nas/wangyq = Z:\\wangyq','stage_scope':'Phase 0 Stage C only','counts':json.loads((OUT/'stagec_summary.json').read_text()),'exported_files':files,'nas_assets':assets,'reference_assets_documented_in_preflight_json':True,'no_images_features_weights_or_cache_uploaded':True}
 (dest/'export_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
 result={'run_id':RUN,'export_utc':stamp,'export_dir':str(dest),'file_count':len(files)+1,'total_bytes':sum(p.stat().st_size for p in copied)+(dest/'export_manifest.json').stat().st_size}
 (HERE/'export_location.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
