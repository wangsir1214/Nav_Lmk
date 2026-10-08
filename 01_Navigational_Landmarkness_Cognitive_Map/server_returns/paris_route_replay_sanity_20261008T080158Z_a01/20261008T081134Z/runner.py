#!/usr/bin/env python3
"""Frozen two-question route replay. This process never reads scorer_gold_v1.json."""
import csv, datetime, hashlib, json, os, platform, sys, traceback
from pathlib import Path
from PIL import Image
from Equirec2Perspec import Equirectangular
from qwen_json_parser import parse_model_json

HERE=Path(__file__).resolve().parent
IDENTITY=json.loads((HERE/'identity.json').read_text())
RUN=IDENTITY['run_id']; OUT=Path(IDENTITY['nas_output_dir'])
PACKAGE=Path(IDENTITY['source_clone'])/IDENTITY['package_rel']
ERP_ROOT=Path('/home/nas/wangyq/GSV_Paris/0-All_GSV_3059_panorama')
HEADING_CSV=Path('/home/nas/wangyq/Street_view_and_points_Paris/GoogleAPIMETADAT/Paris_Points_heading_3059/Paris_Points_heading_3059.csv')
MODEL_PATH=Path('/home/nas/wangyq/model_weights/Qwen/Qwen3.5-9B')
CONDITIONS=(('Full','prompt_route_replay_v1_full.txt'),('NoDemo','prompt_route_replay_v1_nodemo.txt'),('NoCurrent','prompt_route_replay_v1_nocurrent.txt'))
VIEW_ORDER=('front','right','back','left')
MAX_NEW_TOKENS=320

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def dump(path,obj):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');temp.replace(path)
def append(path,obj):
 with Path(path).open('a',buffering=1) as f:f.write(json.dumps(obj,ensure_ascii=False)+'\n')
def log(event,**fields):append(OUT/'events.jsonl',dict(utc=now(),event=event,**fields))
def load_inputs():
 q=json.loads((PACKAGE/'question_manifest_v1.json').read_text())['questions']
 d=json.loads((PACKAGE/'demo_manifest_v1.json').read_text())['questions']
 t=json.loads((PACKAGE/'test_observation_manifest_v1.json').read_text())['questions']
 expected=('q_main02_decision_step3','q_main06_decision_step3')
 assert tuple(x['question_id'] for x in q)==expected
 assert tuple(x['question_id'] for x in d)==expected
 assert tuple(x['question_id'] for x in t)==expected
 for question,demo,test in zip(q,d,t):
  assert [x['demo_label'] for x in demo['demonstrations']]==question['demonstration_labels']==[f'D{i:02d}' for i in range(1,7)]
  assert [x['sequence_index'] for x in demo['demonstrations']]==list(range(1,7))
  assert test['pano_id'] not in {x['pano_id'] for x in demo['demonstrations']}
  assert question['current_label']==test['current_label']=='CURRENT'
  assert demo['route_id_internal']==test['route_id_internal']==question['route_id_internal']
  for obs in demo['demonstrations']+[test]:
   assert [v['view_label'] for v in obs['route_aligned_views']]==list(VIEW_ORDER)
   assert all(v['source_pano_id']==obs['pano_id'] and v['projection']=='perspective_from_erp' and v['fov_deg']==90 for v in obs['route_aligned_views'])
   assert all(abs((obs['route_aligned_views'][i]['center_heading_deg']-obs['route_aligned_views'][0]['center_heading_deg'])%360-90*i)<1e-6 for i in range(4))
 return q,d,t

def project_all(demos,tests):
 with HEADING_CSV.open(encoding='utf-8-sig',newline='') as f: headings={r['panoid']:float(r['heading_from_api']) for r in csv.DictReader(f)}
 all_obs=[]; records=[]; mapping={}
 for demo,test in zip(demos,tests):
  all_obs += [(demo['question_id'],o['demo_label'],o) for o in demo['demonstrations']]
  all_obs += [(test['question_id'],'CURRENT',test)]
 for qid,label,obs in all_obs:
  pano=obs['pano_id']; erp=ERP_ROOT/(pano+'_panorama.jpg')
  if not erp.is_file() or pano not in headings:raise RuntimeError(f'Missing ERP or heading for {qid} {label}: {erp}')
  with Image.open(erp) as im:
   if im.width!=2*im.height or im.width<640:raise RuntimeError(f'Invalid ERP dimensions for {qid} {label}: {im.size}')
   source_size=list(im.size)
  equ=Equirectangular(str(erp)); output=[]
  for spec in obs['route_aligned_views']:
   absolute=float(spec['center_heading_deg']);local=(absolute-headings[pano])%360
   # Geographic center = (ERP center heading_from_api + local THETA) mod 360.
   dest=OUT/'projected_views'/qid/f'{label}_{spec["view_label"]}.png'
   dest.parent.mkdir(parents=True,exist_ok=True)
   import cv2
   frame=equ.GetPerspective(90,local,0,640,640)
   if frame.shape!=(640,640,3) or not cv2.imwrite(str(dest),frame):raise RuntimeError(f'Projection write failed: {dest}')
   rec={'question_id':qid,'anonymous_label':label,'view_label':spec['view_label'],'source_erp':str(erp),'source_erp_size':source_size,'source_erp_sha256':sha(erp),'source_heading_csv':str(HEADING_CSV),'heading_from_api':headings[pano],'center_heading_deg':absolute,'local_theta_deg':local,'phi_deg':0,'fov_deg':90,'output_size':[640,640],'projector':'Equirec2Perspec.Equirectangular.GetPerspective','interpolation':'cv2.INTER_CUBIC','border_mode':'cv2.BORDER_WRAP','projected_path':str(dest),'projected_size_bytes':dest.stat().st_size,'projected_sha256':sha(dest)}
   records.append(rec);output.append(rec)
  mapping[(qid,label)]=output
  del equ
  log('projected_observation',question=qid,label=label,views=4)
 if len(records)!=56:raise RuntimeError(f'Expected 56 projected images, got {len(records)}')
 dump(OUT/'input_image_manifest.json',{'run_id':RUN,'heading_csv_sha256':sha(HEADING_CSV),'projector_sha256':sha(HERE/'Equirec2Perspec.py'),'images':records})
 return mapping

def check_no_leak(texts,all_panos):
 alltext='\n'.join(texts)
 banned=list(all_panos)+['q_main02_decision_step3','q_main06_decision_step3','main_02','main_06','scorer_gold','gold action']
 leaked=[token for token in banned if token in alltext]
 if leaked:raise RuntimeError('Request text contains forbidden identifier: '+repr(leaked[:2]))

def make_request(qid,condition,prompt,mapping,demo,all_panos,retry=False):
 text=prompt if not retry else prompt+'\nFormatting retry for the same images: return exactly one JSON object with only the action key and a valid action value. No Markdown or explanation.'
 labels=[x['demo_label'] for x in demo['demonstrations']] if condition!='NoDemo' else []
 if condition!='NoCurrent':labels+=['CURRENT']
 images=[];content=[]
 for label in labels:
  for rec in mapping[(qid,label)]:
   image_label=f'{label} {rec["view_label"]}'
   content.append({'type':'text','text':image_label+':'})
   with Image.open(rec['projected_path']) as im:img=im.convert('RGB')
   content.append({'type':'image','image':img})
   images.append({'anonymous_label':label,'view_label':rec['view_label'],'sha256':rec['projected_sha256'],'path':rec['projected_path']})
 content.append({'type':'text','text':text})
 texts=[v['text'] for v in content if v['type']=='text'];check_no_leak(texts,all_panos)
 req={'run_id':RUN,'question_id':qid,'condition':condition,'attempt':2 if retry else 1,'actual_message_texts':texts,'image_order':images,'prompt_sha256':hashlib.sha256(text.encode()).hexdigest(),'role':'user','enable_thinking':False,'do_sample':False,'max_new_tokens':MAX_NEW_TOKENS,'gold_not_loaded':True,'created_utc':now()}
 append(OUT/'actual_requests.jsonl',req)
 return [{'role':'user','content':content}],req

def parse_action(raw):
 obj,kind,normal=parse_model_json(raw)
 if not isinstance(obj,dict) or set(obj)!={'action'} or type(obj['action']) is not str or obj['action'] not in ('LEFT','RIGHT','FORWARD','UNSURE'):
  raise ValueError('Output must be one JSON object with exactly action=LEFT|RIGHT|FORWARD|UNSURE')
 return obj['action'],kind,normal

def main():
 os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',CUDA_VISIBLE_DEVICES='0')
 questions,demos,tests=load_inputs()
 package_hashes={p.name:sha(p) for p in PACKAGE.iterdir() if p.is_file() and (p.name.endswith('.json') or p.name.startswith('prompt_route_replay_v1_'))}
 revision=json.loads((MODEL_PATH/'_provenance/source.json').read_text())['revision']
 pre=json.loads((MODEL_PATH/'preprocessor_config.json').read_text())
 metadata={'run_id':RUN,'created_utc':IDENTITY['created_utc'],'source_commit':IDENTITY['source_commit'],'source_repo':'https://github.com/wangsir1214/Nav_Lmk','package_path':str(PACKAGE),'package_file_sha256':package_hashes,'runner_path':str(HERE/'runner.py'),'runner_sha256':sha(HERE/'runner.py'),'parser_sha256':sha(HERE/'qwen_json_parser.py'),'projector_sha256':sha(HERE/'Equirec2Perspec.py'),'model_path':str(MODEL_PATH),'model_revision':revision,'processor':'Qwen3VLProcessor via AutoProcessor','dtype':'torch.bfloat16','attention_implementation':'sdpa','device_map':'cuda:0','do_sample':False,'enable_thinking':False,'max_new_tokens':MAX_NEW_TOKENS,'image_processing_budget':pre.get('size'),'output_image_size':[640,640],'projection_fov_deg':90,'python':sys.version,'platform':platform.platform(),'status':'PREPARING'}
 dump(OUT/'run_metadata.json',metadata);log('start',run_id=RUN)
 mapping=project_all(demos,tests)
 metadata['status']='PROJECTED';dump(OUT/'run_metadata.json',metadata)
 import torch,transformers
 from transformers import AutoProcessor,Qwen3_5ForConditionalGeneration
 metadata.update(torch_version=torch.__version__,transformers_version=transformers.__version__,cuda_device=torch.cuda.get_device_name(0));dump(OUT/'run_metadata.json',metadata)
 processor=AutoProcessor.from_pretrained(str(MODEL_PATH),local_files_only=True)
 model=Qwen3_5ForConditionalGeneration.from_pretrained(str(MODEL_PATH),local_files_only=True,dtype=torch.bfloat16,attn_implementation='sdpa',device_map='cuda:0');model.eval()
 metadata['status']='INFERENCE';dump(OUT/'run_metadata.json',metadata);log('model_loaded',revision=revision)
 all_panos={o['pano_id'] for d in demos for o in d['demonstrations']}|{t['pano_id'] for t in tests}
 for question,demo in zip(questions,demos):
  qid=question['question_id']
  for condition,filename in CONDITIONS:
   prompt=(PACKAGE/filename).read_text();record={'run_id':RUN,'question_id':qid,'condition':condition,'action':None,'status':'FORMAT_FAILED','attempts':0,'model_revision':revision,'time_utc':now()}
   for attempt in (1,2):
    messages,req=make_request(qid,condition,prompt,mapping,demo,all_panos,retry=attempt==2)
    log('request_start',question=qid,condition=condition,attempt=attempt,images=len(req['image_order']))
    x=processor.apply_chat_template(messages,tokenize=True,add_generation_prompt=True,return_dict=True,return_tensors='pt',enable_thinking=False)
    shapes={k:list(v.shape) for k,v in x.items() if hasattr(v,'shape')}
    with torch.inference_mode():y=model.generate(**x.to(model.device),do_sample=False,max_new_tokens=MAX_NEW_TOKENS,pad_token_id=processor.tokenizer.eos_token_id)
    raw=processor.batch_decode(y[:,x['input_ids'].shape[1]:],skip_special_tokens=True,clean_up_tokenization_spaces=False)[0]
    rawpath=OUT/'raw_outputs'/f'{qid}.{condition}.attempt{attempt:02d}.txt';rawpath.parent.mkdir(exist_ok=True);rawpath.write_text(raw)
    record.update(attempts=attempt,raw_output_path=str(rawpath),raw_output_sha256=sha(rawpath),processing_shapes=shapes,request_prompt_sha256=req['prompt_sha256'])
    try:
     action,kind,normal=parse_action(raw)
     normalized_path=rawpath.with_suffix('.normalized.txt');normalized_path.write_text(normal)
     record.update(action=action,status='VALID',normalization_type=kind,normalized_sha256=sha(normalized_path),normalized_path=str(normalized_path),error=None)
     log('request_valid',question=qid,condition=condition,attempt=attempt,action=action)
     break
    except (ValueError,json.JSONDecodeError) as exc:
     record.update(error=str(exc),normalization_type='invalid')
     log('request_format_error',question=qid,condition=condition,attempt=attempt,error=str(exc))
    finally:
     del x,y,messages
     torch.cuda.empty_cache()
   append(OUT/'predictions.jsonl',record)
 metadata['status']='INFERENCE_COMPLETE';metadata['completed_utc']=now();dump(OUT/'run_metadata.json',metadata)
 log('inference_complete')

if __name__=='__main__':
 try:main()
 except BaseException as exc:
  obj={'run_id':RUN,'status':'BLOCKED','utc':now(),'first_error':str(exc),'error_type':type(exc).__name__,'traceback':traceback.format_exc(),'last_successful_event':None}
  if (OUT/'events.jsonl').exists():
   try:obj['last_successful_event']=json.loads((OUT/'events.jsonl').read_text().splitlines()[-1])
   except Exception:pass
  dump(OUT/'BLOCKED.json',obj);log('blocked',error=str(exc));raise
