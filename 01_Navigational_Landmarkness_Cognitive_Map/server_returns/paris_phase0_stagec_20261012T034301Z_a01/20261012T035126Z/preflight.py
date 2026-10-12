#!/usr/bin/env python3
"""Read-only Stage C frozen-input and original-observer integrity gate."""
import csv,hashlib,json,subprocess,sys,traceback
from pathlib import Path
import numpy as np
from PIL import Image,__version__ as pillow_version
HERE=Path(__file__).resolve().parent;IDENT=json.loads((HERE/'identity.json').read_text());OUT=Path(IDENT['nas_output_dir'])
REPO=Path(IDENT['isolated_checkout']);PROJ=REPO/'01_Navigational_Landmarkness_Cognitive_Map'
FROZEN=PROJ/'outputs/pilot0/stagec_frozen_20261011T172946Z';PHASE0=PROJ/'outputs/pilot0/phase0_intervention_prep_20261011'
TASK=Path('/home/wangyq/Nav_Lmk/server_tasks/paris_local_v1_20260923_v2_2_final_20260924')
FEATURES=Path('/home/nas/wangyq/outputs/Paris_local_v1_20260923/features_g14_l31_value_c32_urban_448png_v2')
BASELINE=Path('/home/nas/wangyq/outputs/Paris_local_v1_20260923/baseline_g14_v2')
EXPECTED={'pair_scores':'3c3de24cc72794650f318252992c7be981c15c9726c57ff2bc9ef7e75237f29e','run_config':'a02a091f69ba95a79690e36f87746a1a833844747f1313b83801cf0e441566bf','weights':'baf8467e50af277596bbbafa06887c177ee899ab46033649c383577d7e9309d3','centers':'a684e571f05c85c804e7301547d8620c28ae759e824adb9ac88294b080feaba0'}
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for part in iter(lambda:f.read(8*1024*1024),b''):h.update(part)
 return h.hexdigest()
def rows(path):
 with Path(path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def dump(path,obj):Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def check(condition,msg):
 if not condition:raise RuntimeError(msg)
def main():
 import torch,torchvision
 manifest=json.loads((FROZEN/'stagec_execution_manifest.json').read_text())
 disposition=json.loads((FROZEN/'stageb_disposition_all20.json').read_text())
 check(manifest['status']=='FROZEN_PRE_INTERVENTION_NOT_EXPERIMENT_RESULT','Stage C manifest status changed')
 check(manifest['stage_a_run_id']=='paris_phase0_stagea_20261011T070533Z_a01' and manifest['stage_a_commit']==IDENT['stagea_result_commit'],'Stage A provenance mismatch')
 check(manifest['base_main_commit']==IDENT['phase0_base_commit'],'Phase 0 base commit mismatch')
 checks={
 'geometry_script':(PROJ/'scripts/phase0_intervention_geometry.py',manifest['geometry_script_sha256']),
 'selection':(PHASE0/'selection_manifest.json',manifest['selection_sha256']),
 'human_qc':(FROZEN/'MINIMAL_HUMAN_QC_frozen.csv',manifest['human_qc_sha256']),
 'pair_scores':(BASELINE/'pair_scores.csv',EXPECTED['pair_scores']),
 'run_config':(FEATURES/'run_config.json',EXPECTED['run_config'])}
 hashes={}
 for name,(path,expected) in checks.items():
  actual=sha(path);mode='checkout_bytes'
  # Two Windows-authored Stage B inputs were committed through Git text normalization.
  # Reconstruct original CRLF bytes only to verify the recorded frozen checksum;
  # use the checked-out JSON/CSV content unchanged for all execution.
  if actual!=expected and name in ('selection','human_qc'):
   raw=Path(path).read_bytes()
   if b'\r' not in raw and hashlib.sha256(raw.replace(b'\n',b'\r\n')).hexdigest()==expected:
    mode='git_lf_checkout_original_crlf_sha_verified'
  check(actual==expected or mode!='checkout_bytes',f'{name} SHA-256 mismatch: {path}: checkout={actual}, frozen={expected}')
  hashes[name]={'path':str(path),'checkout_sha256':actual,'frozen_original_sha256':expected,'verification_mode':mode}
 stagea_rel='01_Navigational_Landmarkness_Cognitive_Map/server_returns/paris_phase0_stagea_20261011T070533Z_a01/20261011T071447Z/proposals.jsonl'
 blob=subprocess.check_output(['git','-C',str(REPO),'show',IDENT['stagea_result_commit']+':'+stagea_rel]);stagea_hash=hashlib.sha256(blob).hexdigest()
 check(stagea_hash==manifest['stage_a_proposals_sha256'],f'Stage A proposals SHA mismatch: {stagea_hash}')
 nas_proposals=Path('/home/nas/wangyq/outputs/paris_phase0_stagea_20261011T070533Z_a01/proposals.jsonl')
 if nas_proposals.exists():check(sha(nas_proposals)==stagea_hash,'Stage A NAS proposals differ from result branch')
 check(len(manifest['queries'])==16 and len(disposition['rows'])==20,'Stage C/Stage B counts mismatch')
 dmap={x['query_view_id']:x for x in disposition['rows']};run_ids={x['query_view_id'] for x in manifest['queries']}
 check(len(dmap)==20 and len(run_ids)==16 and run_ids=={qid for qid,x in dmap.items() if x['stage_c_status']=='RUN'},'RUN/disposition ID mismatch')
 check(sum(x['analysis_role']=='primary_full_correct' for x in dmap.values())==18 and sum(x['analysis_role']=='diagnostic_full_failure' for x in dmap.values())==2,'20-case role mismatch')
 check(sum(x['stage_c_status']=='RUN' for x in dmap.values())==16 and sum(x['stage_c_status']!='RUN' for x in dmap.values())==4,'RUN/non-RUN count mismatch')
 check(all(dmap[q]['analysis_role']=='primary_full_correct' for q in run_ids),'Non-primary query in RUN list')
 overlap_count=sum(len(x.get('other_candidate_control_overlap_indices',[])) for x in disposition['rows']);check(overlap_count==8,'Frozen eight overlap flags mismatch')
 check(manifest['mask_contract']['source']=='query_image_only' and manifest['mask_contract']['fill_rgb']==[127,127,127] and manifest['mask_contract']['reference_descriptors']=='unchanged','Mask contract mismatch')
 image_checks=[]
 for q in manifest['queries']:
  qid=q['query_view_id'];p=Path(q['source_image_path']);pano,view=qid.rsplit('__v',1)
  check(view in ('0','1','2','3') and p.name==f'{pano}_panorama_{view}.jpg' and str(p).startswith('/home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/'),'Source image path mismatch: '+qid)
  check(p.is_file(),'Missing source image: '+str(p))
  with Image.open(p) as im: size=list(im.size);fmt=im.format;orientation=im.getexif().get(274,1)
  actual=sha(p);check(size==[640,640] and size==q['source_image_size'] and fmt=='JPEG' and orientation==1 and actual==q['source_image_sha256'],'Image dimensions/EXIF/hash mismatch: '+str(p))
  candidate=tuple(q['candidate_bbox_xyxy_640']);controls=[tuple(x) for x in q['control_bboxes_xyxy_640']]
  check(len(controls)==3 and dmap[qid]['candidate_id']==q['candidate_id'],'Frozen candidate/control mismatch: '+qid)
  # Validation only: never select or modify any box.
  from phase0_intervention_geometry import validate_box,validate_control,overlap,qwen_1000_to_pixels
  check(tuple(qwen_1000_to_pixels(q['candidate_bbox_xyxy_1000']))==candidate,'Frozen 1000-to-640 conversion mismatch: '+qid)
  validate_box(candidate)
  for c in controls:validate_control(c,candidate)
  check(all(not overlap(a,b) for i,a in enumerate(controls) for b in controls[i+1:]),'Frozen controls overlap: '+qid)
  image_checks.append({'query_view_id':qid,'source_image_path':str(p),'size_bytes':p.stat().st_size,'sha256':actual,'image_size':size,'candidate_bbox_xyxy_640':list(candidate),'control_bboxes_xyxy_640':[list(x) for x in controls],'other_candidate_control_overlap_indices':dmap[qid].get('other_candidate_control_overlap_indices',[])})
 cfg=json.loads((FEATURES/'run_config.json').read_text());paths=json.loads((TASK/'configs/paths.server.json').read_text())
 check(sha(TASK/'task_manifest.json')==cfg['task_manifest_sha256'],'Original task_manifest hash mismatch')
 check(sha(TASK/'configs/baseline_request_v2.json')==cfg['request_config_sha256'],'Original baseline config hash mismatch')
 for name,path in [('weights',paths['dinov2_g14_weights']),('centers',paths['vlad_centers'])]:
  actual=sha(path);check(actual==EXPECTED[name] and actual==cfg[name+'_sha256'],f'{name} SHA mismatch: {path}: {actual}');hashes[name]={'path':path,'sha256':actual,'size_bytes':Path(path).stat().st_size}
 source_commit=subprocess.check_output(['git','-C',paths['dinov2_source'],'rev-parse','HEAD'],text=True).strip()
 check(source_commit==cfg['dinov2_commit'] and source_commit=='7764ea0f912e53c92e82eb78a2a1631e92725fc8','DINO source revision mismatch')
 check(not subprocess.check_output(['git','-C',paths['dinov2_source'],'status','--porcelain','--untracked-files=no'],text=True).strip(),'DINO source tracked changes')
 check(pillow_version=='12.3.0' and torch.__version__==cfg['torch'] and torchvision.__version__==cfg['torchvision'] and np.__version__==cfg['numpy'],'Old observer environment/version mismatch')
 check(torch.cuda.is_available() and cfg['device']=='cuda' and cfg['tf32'] is False,'CUDA/numeric config mismatch')
 index_path=FEATURES/'feature_index.csv';index_sha=sha(index_path);check(index_sha==cfg['feature_index_sha256'],'212 feature index hash mismatch')
 index=rows(index_path);check(len(index)==212 and len({x['view_id'] for x in index})==212,'Feature index not 212 unique views')
 qrows=rows(TASK/'data/queries.csv');rrows=rows(TASK/'data/references.csv');pairs=rows(TASK/'data/retrieval_pairs.csv')
 task_manifest=json.loads((TASK/'task_manifest.json').read_text())
 for rel in ('data/queries.csv','data/references.csv','data/retrieval_pairs.csv'):
  check(sha(TASK/rel)==task_manifest['hashes'][rel],f'Original P/N/I task file hash mismatch: {rel}')
 check(len(qrows)==44 and len(rrows)==168 and len(pairs)==7392,'Original task counts mismatch')
 refs={x['view_id'] for x in rrows};queries={x['view_id'] for x in qrows};check(refs.isdisjoint(queries) and run_ids<=queries,'RUN IDs not frozen query IDs')
 check({x['view_id'] for x in index}==refs|queries and sum(x['role']=='reference' for x in index)==168,'Feature-index task IDs/roles mismatch')
 ref_info=[]
 for row in index:
  if row['role']!='reference':continue
  path=Path(row['vlad_path']);actual=sha(path)
  check(actual==row['vlad_sha256'],f'Reference VLAD hash mismatch: {path}')
  vec=np.load(path,allow_pickle=False)
  check(vec.shape==(49152,) and vec.dtype==np.float32 and np.isfinite(vec).all() and abs(np.linalg.norm(vec)-1)<1e-5,f'Reference VLAD invalid: {path}')
  ref_info.append({'reference_view_id':row['view_id'],'path':str(path),'sha256':actual,'size_bytes':path.stat().st_size})
 check(len(ref_info)==168,'Reference VLAD count mismatch')
 scored=rows(BASELINE/'pair_scores.csv');check(len(scored)==7392,'Original pair score count mismatch')
 key=lambda x:(x['query_view_id'],x['reference_view_id'])
 pmap={key(x):x for x in pairs};smap={key(x):x for x in scored}
 check(len(pmap)==len(smap)==7392 and set(pmap)==set(smap),'P/N/I pair key mismatch')
 for k in pmap:
  check(pmap[k]['relation']==smap[k]['relation'] and smap[k]['scoring_allowed']==str(pmap[k]['relation'] in ('positive','negative')),'P/N/I relation or scoring mask mismatch: '+str(k))
 baseline_per_query={x['query_view_id']:x for x in rows(BASELINE/'baseline_per_query.csv')}
 check(all(int(baseline_per_query[q]['best_positive_rank'])==1 for q in run_ids),'RUN query is not old Full-correct')
 report={'run_id':IDENT['run_id'],'status':'PASS','source_main_head':IDENT['source_main_head'],'frozen_stagec_commit':IDENT['frozen_stagec_commit'],'stage_a_branch_commit':IDENT['stagea_result_commit'],'stage_a_proposals_sha256':stagea_hash,'frozen_manifest_sha256':sha(FROZEN/'stagec_execution_manifest.json'),'stageb_disposition_sha256':sha(FROZEN/'stageb_disposition_all20.json'),'hashes':hashes,'image_checks':image_checks,'reference_descriptors':ref_info,'observer':{'task_dir':str(TASK),'feature_dir':str(FEATURES),'baseline_dir':str(BASELINE),'feature_index_sha256':index_sha,'task_manifest_sha256':cfg['task_manifest_sha256'],'dinov2_source_commit':source_commit,'pillow_version':pillow_version,'torch':torch.__version__,'torchvision':torchvision.__version__,'numpy':np.__version__,'cuda':torch.version.cuda,'device_name':torch.cuda.get_device_name(0)},'counts':{'original_views':20,'run_views':16,'nonrun_views':4,'reference_views':168,'old_index_views':212,'old_pairs':7392,'overlap_flags':overlap_count}}
 dump(OUT/'preflight.json',report);dump(HERE/'preflight_summary.json',{k:v for k,v in report.items() if k not in ('image_checks','reference_descriptors')})
 print('PASS: Stage C package, 16 JPEGs, old observer, 168 reference descriptors, P/N/I')
if __name__=='__main__':
 try:
  sys.path.insert(0,str(PROJ/'scripts'));main()
 except BaseException as exc:
  dump(OUT/'BLOCKED.json',{'run_id':IDENT['run_id'],'stage':'preflight','first_error':str(exc),'traceback':traceback.format_exc()});raise
