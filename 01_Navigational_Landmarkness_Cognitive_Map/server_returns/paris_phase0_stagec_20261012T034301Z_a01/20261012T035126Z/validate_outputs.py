#!/usr/bin/env python3
"""Independent Stage C terminal audit: dimensions, hashes, all scores, P/N/I, readout."""
import ast,csv,hashlib,json,math
from collections import defaultdict
from pathlib import Path
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;IDENT=json.loads((HERE/'identity.json').read_text());OUT=Path(IDENT['nas_output_dir'])
TASK=Path('/home/wangyq/Nav_Lmk/server_tasks/paris_local_v1_20260923_v2_2_final_20260924')
def rows(p):
 with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 meta=json.loads((OUT/'run_metadata.json').read_text());gate=json.loads((OUT/'full_equivalence_report.json').read_text());pre=json.loads((OUT/'preflight.json').read_text())
 if meta['status']!='COMPLETE' or gate['status']!='PASS' or pre['status']!='PASS':raise RuntimeError('Run/preflight/Full gate not complete')
 comp=rows(OUT/'full_equivalence_pairwise.csv')
 if len(comp)!=504 or any(not math.isfinite(float(x['absolute_difference'])) or float(x['absolute_difference'])>=1e-5 or x['below_1e_minus_5']!='True' for x in comp):raise RuntimeError('Full score equivalence audit failed')
 if len(gate['cases'])!=3 or not all(x['passed'] and x['old_positive_rank']==x['recomputed_positive_rank'] for x in gate['cases']):raise RuntimeError('Full rank equivalence audit failed')
 mask=rows(OUT/'masked_image_manifest.csv');feature=rows(OUT/'query_feature_manifest.csv');scores=rows(OUT/'masked_pair_scores.csv');readout=rows(OUT/'readout_per_query.csv');disp=rows(OUT/'disposition_all20.csv')
 if (len(mask),len(feature),len(scores),len(readout),len(disp))!=(64,64,10752,16,20):raise RuntimeError('Output row counts differ from frozen contract')
 expected={'candidate','control1','control2','control3'}
 grouped=defaultdict(dict);source_cache={}
 for r in mask:
  q,v=r['query_view_id'],r['variant']
  if v not in expected or v in grouped[q]:raise RuntimeError('Duplicate/missing mask variant: '+q)
  grouped[q][v]=r;src=Path(r['source_image_path'])
  if q not in source_cache:
   if sha(src)!=r['source_image_sha256']:raise RuntimeError('Source hash mismatch: '+str(src))
   with Image.open(src) as im:source_cache[q]=np.asarray(im.convert('RGB'))
  a=source_cache[q];box=ast.literal_eval(r['bbox_xyxy_640']);x0,y0,x1,y1=box
  with Image.open(r['masked_640_path']) as im:b=np.asarray(im.convert('RGB'))
  if b.shape!=(640,640,3) or sha(r['masked_640_path'])!=r['masked_640_sha256']:raise RuntimeError('640 mask hash/dim mismatch: '+q+' '+v)
  test=a.copy();test[y0:y1,x0:x1]=127
  if not np.array_equal(test,b):raise RuntimeError('Mask pixels differ from exact frozen gray rectangle: '+q+' '+v)
  with Image.open(r['model_448_path']) as im:c=np.asarray(im.convert('RGB'))
  if c.shape!=(448,448,3) or sha(r['model_448_path'])!=r['model_448_sha256']:raise RuntimeError('448 mask hash/dim mismatch: '+q+' '+v)
  expected448=np.asarray(Image.fromarray(test).resize((448,448),resample=Image.Resampling.BICUBIC))
  if not np.array_equal(expected448,c):raise RuntimeError('448 RGB bicubic pixels mismatch: '+q+' '+v)
 if len(grouped)!=16 or any(set(v)!=expected for v in grouped.values()):raise RuntimeError('Incomplete 16×4 masks')
 seen_feat=set()
 for r in feature:
  key=(r['query_view_id'],r['variant'])
  if key in seen_feat or key not in {(q,v) for q,vs in grouped.items() for v in vs}:raise RuntimeError('Duplicate or foreign VLAD feature')
  seen_feat.add(key);p=Path(r['vlad_path']);vec=np.load(p,allow_pickle=False)
  if sha(p)!=r['vlad_sha256'] or vec.shape!=(49152,) or vec.dtype!=np.float32 or not np.isfinite(vec).all() or abs(np.linalg.norm(vec)-1)>1e-5:raise RuntimeError('VLAD feature invalid: '+str(p))
 pairs={(x['query_view_id'],x['reference_view_id']):x for x in rows(TASK/'data/retrieval_pairs.csv')};refs={x['view_id'] for x in rows(TASK/'data/references.csv')}
 by_variant=defaultdict(list);seen_score=set()
 for r in scores:
  key=(r['query_view_id'],r['variant'],r['reference_view_id'])
  if key in seen_score or r['reference_view_id'] not in refs:raise RuntimeError('Duplicate/foreign score key')
  seen_score.add(key);p=pairs[(r['query_view_id'],r['reference_view_id'])]
  if r['relation']!=p['relation'] or r['scoring_allowed']!=str(p['relation'] in ('positive','negative')) or not math.isfinite(float(r['cosine_similarity'])):raise RuntimeError('P/N/I or score invalid: '+str(key))
  by_variant[(r['query_view_id'],r['variant'])].append(r)
 if len(by_variant)!=64 or any(len(x)!=168 or {y['reference_view_id'] for y in x}!=refs for x in by_variant.values()):raise RuntimeError('168-reference coverage incomplete')
 read={x['query_view_id']:x for x in readout}
 if len(read)!=16 or set(read)!=set(grouped):raise RuntimeError('Per-query readout IDs mismatch')
 for (q,v),rr in by_variant.items():
  eligible=[x for x in rr if x['relation']!='ignore'];pos=[x for x in eligible if x['relation']=='positive'];neg=[x for x in eligible if x['relation']=='negative']
  splus=max(float(x['cosine_similarity']) for x in pos);sminus=max(float(x['cosine_similarity']) for x in neg);margin=splus-sminus
  rank=sorted(eligible,key=lambda x:(-float(x['cosine_similarity']),x['reference_view_id']))
  pr=next(i for i,x in enumerate(rank,1) if x['relation']=='positive')
  r=read[q]
  if abs(float(r[f'{v}_s_positive'])-splus)>1e-6 or abs(float(r[f'{v}_s_negative'])-sminus)>1e-6 or abs(float(r[f'{v}_margin'])-margin)>1e-6 or int(r[f'{v}_best_positive_rank'])!=pr or r[f'{v}_top1_reference_view_id']!=rank[0]['reference_view_id']:
   raise RuntimeError('Readout inconsistent with all-reference score matrix: '+q+' '+v)
 for q,r in read.items():
  calc=sum(float(r[f'control{i}_margin']) for i in (1,2,3))/3-float(r['candidate_margin'])
  if abs(calc-float(r['U']))>1e-9 or abs(float(r['full_margin'])-float(r['candidate_margin'])-float(r['delta_candidate']))>1e-9:raise RuntimeError('Effect readout mismatch: '+q)
 if sum(x['stage_c_execution_status']=='COMPLETED' for x in disp)!=16 or sum(x['stage_c_execution_status']!='COMPLETED' for x in disp)!=4:raise RuntimeError('20-case disposition mismatch')
 if sum(len(json.loads(x['other_candidate_control_overlap_indices'])) for x in disp)!=8:raise RuntimeError('Eight frozen overlap flags missing')
 report={'run_id':IDENT['run_id'],'validation':'PASS','full_equivalence_scores':504,'full_gate_queries':3,'run_queries':16,'nonrun_queries':4,'masked_images_640':64,'masked_images_448':64,'query_vlad_vectors':64,'all_reference_score_rows':10752,'reference_coverage_each_variant':168,'readout_queries':16,'disposition_rows':20,'preserved_overlap_flags':8,'mask_pixels_and_448_resizes_exact':True,'pni_and_readout_consistent':True}
 (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
