#!/usr/bin/env python3
"""Frozen Phase 0 Stage C: gate on three newly recomputed Fulls, then mask only 16 queries."""
import csv,datetime,hashlib,json,os,sys,time,traceback
from pathlib import Path
import numpy as np
from PIL import Image,__version__ as pillow_version
HERE=Path(__file__).resolve().parent;IDENT=json.loads((HERE/'identity.json').read_text());RUN=IDENT['run_id'];OUT=Path(IDENT['nas_output_dir'])
REPO=Path(IDENT['isolated_checkout']);PROJ=REPO/'01_Navigational_Landmarkness_Cognitive_Map'
FROZEN=PROJ/'outputs/pilot0/stagec_frozen_20261011T172946Z';TASK=Path('/home/wangyq/Nav_Lmk/server_tasks/paris_local_v1_20260923_v2_2_final_20260924')
FEATURES=Path('/home/nas/wangyq/outputs/Paris_local_v1_20260923/features_g14_l31_value_c32_urban_448png_v2')
BASELINE=Path('/home/nas/wangyq/outputs/Paris_local_v1_20260923/baseline_g14_v2')
sys.path.insert(0,str(PROJ/'scripts'));sys.path.insert(0,str(TASK/'scripts'))
from phase0_intervention_geometry import render_masks
from pilot0_vlad import G14ValueExtractor,aggregate,load_centers,load_input_png
VARIANTS=('candidate','control1','control2','control3')

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def rows(path):
 with Path(path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def dump(path,obj):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n');tmp.replace(p)
def append(path,obj):
 with Path(path).open('a',buffering=1) as f:f.write(json.dumps(obj,ensure_ascii=False)+'\n')
def event(name,**kw):append(OUT/'events.jsonl',{'utc':utc(),'event':name,**kw})
def state(name,**kw):dump(OUT/'stage_status.json',{'run_id':RUN,'stage':name,'utc':utc(),**kw})
def write_csv(path,records):
 if not records:raise RuntimeError('Refuse empty CSV: '+str(path))
 with Path(path).open('x',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
def score_readout(qid,items):
 eligible=[x for x in items if x['relation'] in ('positive','negative')]
 pos=[x for x in eligible if x['relation']=='positive'];neg=[x for x in eligible if x['relation']=='negative']
 if len(items)!=168 or not pos or not neg:raise RuntimeError('Incomplete P/N/I score vector: '+qid)
 ranked=sorted(eligible,key=lambda x:(-x['score'],x['reference_view_id']))
 best_pos=min(pos,key=lambda x:(-x['score'],x['reference_view_id']))
 best_neg=min(neg,key=lambda x:(-x['score'],x['reference_view_id']))
 positive_rank=min(i for i,x in enumerate(ranked,1) if x['relation']=='positive')
 return {'s_positive':best_pos['score'],'s_negative':best_neg['score'],'margin':best_pos['score']-best_neg['score'],'best_positive_rank':positive_rank,'top1_reference_view_id':ranked[0]['reference_view_id'],'top1_relation':ranked[0]['relation'],'recall_at_1':int(positive_rank==1),'positive_count':len(pos),'negative_count':len(neg),'ignore_count':168-len(eligible)}
def old_items(qid,refs,old_score_map,pair_map):
 return [{'reference_view_id':rid,'score':float(old_score_map[(qid,rid)]['cosine_similarity']),'relation':pair_map[(qid,rid)]['relation']} for rid in refs]
def new_items(qid,vector,ref_mat,refs,pair_map):
 if vector.shape!=(49152,) or not np.isfinite(vector).all() or abs(np.linalg.norm(vector)-1)>1e-5:raise RuntimeError('Non-unit or invalid query VLAD: '+qid)
 scores=(vector.reshape(1,-1) @ ref_mat.T)[0]
 if scores.shape!=(168,) or not np.isfinite(scores).all():raise RuntimeError('Invalid 168-reference cosine scores: '+qid)
 return [{'reference_view_id':rid,'score':float(scores[j]),'relation':pair_map[(qid,rid)]['relation']} for j,rid in enumerate(refs)]
def make_full_png(source,dest):
 with Image.open(source) as im:
  if im.format!='JPEG' or im.size!=(640,640) or im.getexif().get(274,1)!=1:raise RuntimeError('Full gate source JPEG invalid: '+str(source))
  image=im.convert('RGB')
 image.resize((448,448),resample=Image.Resampling.BICUBIC).save(dest,format='PNG')

def main():
 import torch,torchvision
 os.environ.update(CUDA_VISIBLE_DEVICES='0')
 pre=json.loads((OUT/'preflight.json').read_text())
 if pre['status']!='PASS' or len(pre['image_checks'])!=16 or len(pre['reference_descriptors'])!=168:raise RuntimeError('Preflight gate not passed')
 if pillow_version!='12.3.0':raise RuntimeError('Pillow version changed since preflight')
 manifest=json.loads((FROZEN/'stagec_execution_manifest.json').read_text());disp=json.loads((FROZEN/'stageb_disposition_all20.json').read_text())
 if sha(FROZEN/'stagec_execution_manifest.json')!=pre['frozen_manifest_sha256']:raise RuntimeError('Stage C manifest changed after preflight')
 cfg=json.loads((FEATURES/'run_config.json').read_text());paths=json.loads((TASK/'configs/paths.server.json').read_text())
 if cfg['request']['request_id']!='full_image_g14_l31_value_c32_urban_448png_fp32_v2':raise RuntimeError('Wrong observer request')
 if cfg['weights_sha256']!=pre['hashes']['weights']['sha256'] or cfg['centers_sha256']!=pre['hashes']['centers']['sha256']:raise RuntimeError('Observer hashes changed in config')
 rrows=rows(TASK/'data/references.csv');refs=[x['view_id'] for x in rrows]
 index={x['view_id']:x for x in rows(FEATURES/'feature_index.csv')}
 ref_mat=np.stack([np.load(index[rid]['vlad_path'],allow_pickle=False).astype(np.float32,copy=False) for rid in refs])
 if ref_mat.shape!=(168,49152):raise RuntimeError('Reference matrix shape mismatch')
 pair_map={(r['query_view_id'],r['reference_view_id']):r for r in rows(TASK/'data/retrieval_pairs.csv')}
 old_score_map={(r['query_view_id'],r['reference_view_id']):r for r in rows(BASELINE/'pair_scores.csv')}
 old_q={r['query_view_id']:r for r in rows(BASELINE/'baseline_per_query.csv')}
 torch.manual_seed(42);np.random.seed(42);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.backends.cudnn.benchmark=False
 metadata={'run_id':RUN,'source_main_head':IDENT['source_main_head'],'frozen_stagec_commit':IDENT['frozen_stagec_commit'],'stagea_result_commit':IDENT['stagea_result_commit'],'created_utc':IDENT['created_utc'],'stagec_manifest_sha256':pre['frozen_manifest_sha256'],'disposition_sha256':pre['stageb_disposition_sha256'],'preflight_sha256':sha(OUT/'preflight.json'),'runner_sha256':sha(HERE/'runner.py'),'geometry_script_sha256':pre['hashes']['geometry_script']['frozen_original_sha256'],'original_observer_run_config_sha256':pre['hashes']['run_config']['frozen_original_sha256'],'original_pair_scores_sha256':pre['hashes']['pair_scores']['frozen_original_sha256'],'weights_sha256':pre['hashes']['weights']['sha256'],'centers_sha256':pre['hashes']['centers']['sha256'],'torch':torch.__version__,'torchvision':torchvision.__version__,'numpy':np.__version__,'pillow':pillow_version,'cuda':torch.version.cuda,'device':'cuda','tf32':False,'status':'LOADING_OBSERVER'}
 dump(OUT/'run_metadata.json',metadata);state('LOADING_OBSERVER');event('observer_load_start')
 centers=load_centers(paths['vlad_centers']);extractor=G14ValueExtractor(paths['dinov2_source'],paths['dinov2_g14_weights'],'cuda')
 event('observer_loaded');metadata['status']='FULL_GATE';dump(OUT/'run_metadata.json',metadata);state('FULL_GATE')
 ordered=sorted(manifest['queries'],key=lambda x:x['query_view_id']);gate_cases=[ordered[0],ordered[len(ordered)//2],ordered[-1]]
 gate_dir=OUT/'full_gate';gate_dir.mkdir(exist_ok=False)
 comparisons=[];gate_summaries=[]
 for label,q in zip(('first','middle','last'),gate_cases):
  qid=q['query_view_id'];source=Path(q['source_image_path'])
  if sha(source)!=q['source_image_sha256']:raise RuntimeError('Full gate source image changed: '+str(source))
  png=gate_dir/f'{qid}_recomputed_448.png';make_full_png(source,png)
  old_cache=Path(paths['paris_fixed_448'])/source.with_suffix('.png').name
  with Image.open(png) as im,Image.open(old_cache) as old:
   if im.mode!='RGB' or old.mode!='RGB' or im.size!=old.size or im.tobytes()!=old.tobytes():raise RuntimeError('Fresh Full resize differs from original cache pixels: '+qid)
  vector=aggregate(extractor(load_input_png(png)),centers)
  vpath=gate_dir/f'{qid}_recomputed_vlad.npy';np.save(vpath,vector,allow_pickle=False)
  new=new_items(qid,vector,ref_mat,refs,pair_map);old=old_items(qid,refs,old_score_map,pair_map)
  diffs=[]
  for a,b in zip(new,old):
   diff=abs(a['score']-b['score']);diffs.append(diff)
   comparisons.append({'query_view_id':qid,'gate_position':label,'reference_view_id':a['reference_view_id'],'relation':a['relation'],'old_full_cosine_similarity':b['score'],'recomputed_full_cosine_similarity':a['score'],'absolute_difference':diff,'below_1e_minus_5':diff<1e-5})
  new_read=score_readout(qid,new);old_read=score_readout(qid,old)
  rank_ok=new_read['best_positive_rank']==old_read['best_positive_rank']==int(old_q[qid]['best_positive_rank'])
  passed=all(d<1e-5 for d in diffs) and rank_ok
  gate_summaries.append({'query_view_id':qid,'gate_position':label,'new_full_448_png_path':str(png),'new_full_448_png_sha256':sha(png),'new_full_vlad_path':str(vpath),'new_full_vlad_sha256':sha(vpath),'max_absolute_score_difference':max(diffs),'reference_count':len(diffs),'old_positive_rank':old_read['best_positive_rank'],'recomputed_positive_rank':new_read['best_positive_rank'],'passed':passed})
  event('full_gate_case',query_view_id=qid,gate_position=label,max_abs_diff=max(diffs),rank_ok=rank_ok,passed=passed)
  if not passed:
   write_csv(OUT/'full_equivalence_pairwise.csv',comparisons);dump(OUT/'full_equivalence_report.json',{'status':'FAIL','tolerance_strict_less_than':1e-5,'cases':gate_summaries});raise RuntimeError('Full equivalence failed for '+qid)
 write_csv(OUT/'full_equivalence_pairwise.csv',comparisons)
 dump(OUT/'full_equivalence_report.json',{'status':'PASS','selection_rule':'sorted query_view_id: indices 0, 8, 15','tolerance_strict_less_than':1e-5,'cases':gate_summaries,'compared_scores':len(comparisons),'all_ranks_match':True})
 metadata['status']='MASK_AND_RETRIEVAL';dump(OUT/'run_metadata.json',metadata);state('MASK_AND_RETRIEVAL',completed_queries=0,total_queries=16);event('full_gate_passed',compared_scores=504)
 mask_records=[];score_records=[];variant_records=[];readout_records=[];query_features=[]
 for i,q in enumerate(ordered,1):
  qid=q['query_view_id'];source=Path(q['source_image_path'])
  if sha(source)!=q['source_image_sha256']:raise RuntimeError('Masked source image changed: '+str(source))
  boxes={'candidate':tuple(q['candidate_bbox_xyxy_640']),'control1':tuple(q['control_bboxes_xyxy_640'][0]),'control2':tuple(q['control_bboxes_xyxy_640'][1]),'control3':tuple(q['control_bboxes_xyxy_640'][2])}
  mask=render_masks(source,boxes,OUT/'masked_images'/qid)
  if mask['source_sha256']!=q['source_image_sha256'] or mask['pillow_version']!='12.3.0' or mask['fill_rgb']!=(127,127,127):raise RuntimeError('Mask operation contract mismatch: '+qid)
  old_full=score_readout(qid,old_items(qid,refs,old_score_map,pair_map))
  if old_full['best_positive_rank']!=int(old_q[qid]['best_positive_rank']) or abs(old_full['margin']-float(old_q[qid]['margin']))>1e-5:raise RuntimeError('Old Full readout mismatch: '+qid)
  per_variant={'Full':old_full}
  for item in mask['variants']:
   name=item['variant'];path=Path(item['model_448_path'])
   if name not in VARIANTS or tuple(item['bbox_xyxy_640'])!=boxes[name] or sha(path)!=item['model_448_sha256'] or sha(item['masked_640_path'])!=item['masked_640_sha256']:raise RuntimeError('Masked image hash/bbox mismatch: '+qid+' '+name)
   vector=aggregate(extractor(load_input_png(path)),centers)
   vdir=OUT/'query_vlad';vdir.mkdir(exist_ok=True)
   vpath=vdir/f'{qid}.{name}.npy';np.save(vpath,vector,allow_pickle=False)
   query_features.append({'query_view_id':qid,'variant':name,'vlad_path':str(vpath),'vlad_sha256':sha(vpath),'vlad_shape':[49152],'dtype':'float32','unit_norm':float(np.linalg.norm(vector))})
   vals=new_items(qid,vector,ref_mat,refs,pair_map);per_variant[name]=score_readout(qid,vals)
   for x in vals:score_records.append({'query_view_id':qid,'variant':name,'reference_view_id':x['reference_view_id'],'relation':x['relation'],'scoring_allowed':x['relation'] in ('positive','negative'),'cosine_similarity':x['score']})
   variant_records.append({'query_view_id':qid,'variant':name,**per_variant[name]})
   mask_records.append({'query_view_id':qid,'candidate_id':q['candidate_id'],'source_image_path':mask['source_path'],'source_image_sha256':mask['source_sha256'],'fill_rgb':[127,127,127],'pillow_version':mask['pillow_version'],**item})
  d=next(x for x in disp['rows'] if x['query_view_id']==qid)
  readout={'query_view_id':qid,'analysis_role':d['analysis_role'],'candidate_id':q['candidate_id'],'other_candidate_control_overlap_indices':json.dumps(d.get('other_candidate_control_overlap_indices',[])),'full_s_positive':old_full['s_positive'],'full_s_negative':old_full['s_negative'],'full_margin':old_full['margin'],'full_best_positive_rank':old_full['best_positive_rank'],'full_top1_reference_view_id':old_full['top1_reference_view_id'],'full_top1_relation':old_full['top1_relation'],'full_recall_at_1':old_full['recall_at_1']}
  for name in VARIANTS:
   r=per_variant[name]
   readout.update({f'{name}_s_positive':r['s_positive'],f'{name}_s_negative':r['s_negative'],f'{name}_margin':r['margin'],f'{name}_best_positive_rank':r['best_positive_rank'],f'{name}_top1_reference_view_id':r['top1_reference_view_id'],f'{name}_top1_relation':r['top1_relation'],f'{name}_recall_at_1':r['recall_at_1'],f'{name}_flipped_from_full':int(old_full['recall_at_1']==1 and r['recall_at_1']==0),f'delta_{name}':old_full['margin']-r['margin']})
  readout['U']=sum(per_variant[n]['margin'] for n in ('control1','control2','control3'))/3-per_variant['candidate']['margin']
  readout_records.append(readout)
  event('query_complete',index=i,query_view_id=qid,variants=4);state('MASK_AND_RETRIEVAL',completed_queries=i,total_queries=16)
  # Checkpoint complete records so a runtime failure preserves work already finished.
  dump(OUT/'progress_counts.json',{'completed_queries':i,'masked_variants':len(mask_records),'pair_score_rows':len(score_records)})
 extractor.close()
 if len(mask_records)!=64 or len(score_records)!=10752 or len(variant_records)!=64 or len(readout_records)!=16:raise RuntimeError('Stage C output counts incorrect')
 write_csv(OUT/'masked_image_manifest.csv',mask_records)
 write_csv(OUT/'query_feature_manifest.csv',query_features)
 write_csv(OUT/'masked_pair_scores.csv',score_records)
 write_csv(OUT/'variant_readout.csv',variant_records)
 write_csv(OUT/'readout_per_query.csv',readout_records)
 disp_records=[];run_map={r['query_view_id']:r for r in readout_records}
 for d in disp['rows']:
  qid=d['query_view_id'];disp_records.append({'query_view_id':qid,'analysis_role':d['analysis_role'],'stage_c_frozen_status':d['stage_c_status'],'stage_c_execution_status':'COMPLETED' if qid in run_map else 'NOT_RUN_FROZEN_GEOMETRY','candidate_id':d.get('candidate_id',''),'human_decision':d.get('human_decision',''),'other_candidate_control_overlap_indices':json.dumps(d.get('other_candidate_control_overlap_indices',[])),'nonrun_reason':'' if qid in run_map else d['stage_c_status']})
 write_csv(OUT/'disposition_all20.csv',disp_records)
 summary={'run_id':RUN,'status':'SUCCESS','source_main_head':IDENT['source_main_head'],'full_equivalence':'PASS','full_recomputed_queries':3,'full_compared_reference_scores':504,'run_queries':16,'nonrun_queries':4,'nonrun_primary':2,'nonrun_diagnostic':2,'masked_variants':64,'masked_score_rows':10752,'overlap_flags_preserved':8,'candidate_flip_count':sum(r['candidate_flipped_from_full'] for r in readout_records),'candidate_U_positive_count':sum(r['U']>0 for r in readout_records),'candidate_U_zero_count':sum(r['U']==0 for r in readout_records),'candidate_U_negative_count':sum(r['U']<0 for r in readout_records),'scientific_scope':'development-stage fixed observer input-mask effect; not landmark truth or general navigation accuracy'}
 dump(OUT/'stagec_summary.json',summary)
 (OUT/'RUN_SUMMARY.md').write_text('# Phase 0 Stage C — frozen input mask retrieval\n\n'+f"Run `{RUN}`; status **SUCCESS**. Full equivalence passed for three freshly recomputed queries and 504 reference scores. Exactly 16/20 frozen views ran; 2 primary and 2 diagnostic views remained excluded by pre-intervention geometry. Generated 64 query-only masks and 10,752 reference scores. Eight pre-existing other-candidate/control-overlap flags were preserved.\n\nThe 16 are a geometry-eligible subset of 18 Full-correct primary views. Constant gray masking is out-of-distribution; effects are descriptive and do not validate landmark function.\n")
 metadata.update(status='COMPLETE',completed_utc=utc(),counts=summary);dump(OUT/'run_metadata.json',metadata);state('COMPLETE',counts=summary);event('stagec_complete',summary=summary)

if __name__=='__main__':
 try:main()
 except BaseException as exc:
  obj={'run_id':RUN,'status':'BLOCKED','utc':utc(),'first_error':str(exc),'traceback':traceback.format_exc(),'last_successful_event':None}
  p=OUT/'events.jsonl'
  if p.exists():
   try:obj['last_successful_event']=json.loads(p.read_text().splitlines()[-1])
   except Exception:pass
  dump(OUT/'BLOCKED.json',obj);state('BLOCKED',first_error=str(exc));event('blocked',error=str(exc));raise
