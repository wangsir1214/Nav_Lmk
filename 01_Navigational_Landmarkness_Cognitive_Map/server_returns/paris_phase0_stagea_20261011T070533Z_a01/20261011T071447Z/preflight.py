#!/usr/bin/env python3
"""Stage A input-only integrity gate; does not read selection_manifest or gold."""
import hashlib,json,platform,sys,traceback
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent
IDENT=json.loads((HERE/'identity.json').read_text());OUT=Path(IDENT['nas_output_dir'])
PACKAGE=Path(IDENT['isolated_checkout'])/IDENT['package_rel']
IMAGE_ROOT=Path('/home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per')
MODEL=Path('/home/nas/wangyq/model_weights/Qwen/Qwen3.5-9B')
PRIOR=Path('/home/nas/wangyq/outputs/paris_route_replay_sanity_20261008T080158Z_a01/run_metadata.json')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def write(p,obj):Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def main():
 import torch,transformers
 inp=json.loads((PACKAGE/'proposal_input_only.json').read_text())
 assert set(inp)=={'package_id','query_count','queries'} and inp['query_count']==len(inp['queries'])==20
 old=json.loads(PRIOR.read_text());source=json.loads((MODEL/'_provenance/source.json').read_text())
 pre=json.loads((MODEL/'preprocessor_config.json').read_text())
 settings={'model_revision':source['revision'],'processor':'Qwen3VLProcessor via AutoProcessor','dtype':'torch.bfloat16','attention_implementation':'sdpa','device_map':'cuda:0','do_sample':False,'enable_thinking':False,'max_new_tokens':512,'image_processing_budget':pre['size'],'torch_version':torch.__version__,'transformers_version':transformers.__version__,'cuda_device':torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,'python':sys.version,'platform':platform.platform()}
 for k in ('model_revision','processor','dtype','attention_implementation','device_map','do_sample','enable_thinking','image_processing_budget','torch_version','transformers_version'):
  if settings[k]!=old[k]:raise RuntimeError(f'Previously successful Qwen setting mismatch {k}: {settings[k]!r} != {old[k]!r}')
 if not torch.cuda.is_available() or not settings['cuda_device'].startswith('NVIDIA L20'):raise RuntimeError('Previously successful L20 CUDA device unavailable')
 rows=[];errors=[];seen=set()
 for i,item in enumerate(inp['queries']):
  if set(item)!={'query_view_id','image_relative_path','image_sha256'}:errors.append({'index':i,'error':'manifest fields differ','actual_keys':sorted(item)});continue
  qid=item['query_view_id'];relative=item['image_relative_path']
  if qid in seen:errors.append({'index':i,'query_view_id':qid,'error':'duplicate query'});continue
  seen.add(qid)
  if '__v' not in qid:errors.append({'index':i,'query_view_id':qid,'error':'malformed query ID'});continue
  pano,view=qid.rsplit('__v',1)
  if view not in ('0','1','2','3') or relative!=f'{pano}_panorama_{view}.jpg' or Path(relative).name!=relative:
   errors.append({'index':i,'query_view_id':qid,'error':'query/image filename mismatch','relative':relative});continue
  path=IMAGE_ROOT/relative
  if not path.is_file():errors.append({'index':i,'query_view_id':qid,'error':'missing source image','path':str(path)});continue
  with Image.open(path) as im:size=list(im.size);fmt=im.format
  actual=sha(path);entry={'index':i,'query_view_id':qid,'image_relative_path':relative,'image_path':str(path),'image_size':size,'format':fmt,'expected_sha256':item['image_sha256'],'actual_sha256':actual,'size_bytes':path.stat().st_size}
  rows.append(entry)
  if size!=[640,640] or fmt!='JPEG' or actual!=item['image_sha256']:
   errors.append({'index':i,'query_view_id':qid,'error':'size/format/SHA mismatch','entry':entry})
 report={'run_id':IDENT['run_id'],'source_commit':IDENT['source_commit'],'actual_main_head':IDENT['actual_main_head'],'source_main_stage_a_diff':False,'input_manifest_sha256':sha(PACKAGE/'proposal_input_only.json'),'prompt_sha256':sha(PACKAGE/'QWEN_QUERY_PROPOSAL_V1.txt'),'protocol_sha256':sha(PACKAGE/'PHASE0_PROTOCOL.md'),'validated_images':len(rows),'errors':errors,'images':rows,'settings':settings,'status':'PASS' if not errors and len(rows)==20 else 'BLOCKED'}
 write(OUT/'preflight.json',report);write(HERE/'preflight_summary.json',{k:v for k,v in report.items() if k!='images'})
 if report['status']!='PASS':raise RuntimeError(f'Input preflight failed: {len(errors)} issues; see {OUT}/preflight.json')
 print('PASS images=20 settings=reproduced')
if __name__=='__main__':
 try:main()
 except BaseException as exc:
  write(OUT/'BLOCKED.json',{'run_id':IDENT['run_id'],'stage':'preflight','first_error':str(exc),'traceback':traceback.format_exc()});raise
