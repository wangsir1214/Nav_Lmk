#!/usr/bin/env python3
"""Frozen Phase 0 Stage A only: 20 independent Qwen single-query proposals."""
import csv,datetime,hashlib,json,os,sys,traceback
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from qwen_json_parser import parse_model_json

HERE=Path(__file__).resolve().parent
IDENT=json.loads((HERE/'identity.json').read_text());RUN=IDENT['run_id'];OUT=Path(IDENT['nas_output_dir'])
PACKAGE=Path(IDENT['isolated_checkout'])/IDENT['package_rel']
MODEL_PATH=Path('/home/nas/wangyq/model_weights/Qwen/Qwen3.5-9B')
MAX_NEW_TOKENS=512
RETRY_SUFFIX='\nFormatting retry for the same image: return one complete JSON object with only the candidates array; each candidate must have exactly candidate_id, bbox_xyxy_1000, type, description, with integer coordinates from 0 to 1000. No Markdown or explanation.'
COLORS=['#ff4d00','#00b7ff']

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def dump(p,obj):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);temp=p.with_suffix(p.suffix+'.tmp')
 temp.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n');temp.replace(p)
def append(p,obj):
 with Path(p).open('a',buffering=1) as f:f.write(json.dumps(obj,ensure_ascii=False)+'\n')
def event(name,**kw):append(OUT/'events.jsonl',{'utc':now(),'event':name,**kw})
def status(state,**kw):dump(OUT/'stage_status.json',{'run_id':RUN,'state':state,'utc':now(),**kw})

def parse_candidates(raw,width,height):
 obj,normalization,normalized=parse_model_json(raw)
 if not isinstance(obj,dict) or set(obj)!={'candidates'} or not isinstance(obj['candidates'],list):raise ValueError('Root must be one object with only a candidates array')
 arr=obj['candidates']
 if len(arr)>2:raise ValueError('More than two candidates; no truncation allowed')
 converted=[]
 for i,c in enumerate(arr):
  if not isinstance(c,dict) or set(c)!={'candidate_id','bbox_xyxy_1000','type','description'}:raise ValueError(f'Candidate {i+1} must have exactly four specified keys')
  if c['candidate_id']!=f'c{i+1}':raise ValueError(f'Candidate ID/order mismatch at {i+1}')
  if c['type'] not in ('object','text','structure','scene'):raise ValueError(f'Candidate {i+1} type invalid')
  if not isinstance(c['description'],str) or not c['description'].strip():raise ValueError(f'Candidate {i+1} description empty')
  box=c['bbox_xyxy_1000']
  if not isinstance(box,list) or len(box)!=4 or any(type(v) is not int for v in box):raise ValueError(f'Candidate {i+1} box must be four integers')
  x1,y1,x2,y2=box
  if not (0<=x1<x2<=1000 and 0<=y1<y2<=1000):raise ValueError(f'Candidate {i+1} box out of bounds or degenerate: {box}')
  pixel=[round(x1*width/1000,3),round(y1*height/1000,3),round(x2*width/1000,3),round(y2*height/1000,3)]
  converted.append({**c,'bbox_xyxy_640':pixel,'coordinate_conversion':'x*=actual_width/1000; y*=actual_height/1000; no clipping','review_status':'PROVISIONAL'})
 if len(converted)==2:
  a,b=converted
  duplicate=a['bbox_xyxy_1000']==b['bbox_xyxy_1000'] or a['description'].strip().casefold()==b['description'].strip().casefold()
  for c in converted:c['duplicate_review_flag']=duplicate
 else:
  for c in converted:c['duplicate_review_flag']=False
 return converted,normalization,normalized

def overlay(image_path,candidates,dest,state):
 with Image.open(image_path) as im:base=im.convert('RGB')
 w,h=base.size; left,top=58,40
 canvas=Image.new('RGB',(w+left+28,h+top+56),'white');canvas.paste(base,(left,top));draw=ImageDraw.Draw(canvas)
 draw.rectangle((left,top,left+w,top+h),outline='black',width=2)
 for k in (0,160,320,480,640):
  draw.line((left+k,top+h,left+k,top+h+7),fill='black',width=1)
  draw.text((left+k-9,top+h+10),str(k),fill='black')
  draw.line((left-7,top+k,left,top+k),fill='black',width=1)
  draw.text((left-36,top+k-6),str(k),fill='black')
 for i,c in enumerate(candidates):
  x1,y1,x2,y2=c['bbox_xyxy_640'];color=COLORS[i]
  draw.rectangle((left+x1,top+y1,left+x2,top+y2),outline=color,width=3)
  draw.text((left+x1+3,top+y1+3),c['candidate_id'],fill=color,stroke_width=1,stroke_fill='white')
 draw.text((left,10),f'Stage A provisional | {state} | 640px axes',fill='black')
 dest.parent.mkdir(parents=True,exist_ok=True);canvas.save(dest)

def make_request(image,prompt,attempt):
 text=prompt if attempt==1 else prompt+RETRY_SUFFIX
 with Image.open(image['image_path']) as im:rgb=im.convert('RGB')
 messages=[{'role':'user','content':[{'type':'image','image':rgb},{'type':'text','text':text}]}]
 req={'run_id':RUN,'query_view_id':image['query_view_id'],'attempt':attempt,'role':'user','actual_message_texts':[text],'image_order':[{'path':image['image_path'],'sha256':image['actual_sha256'],'size':image['image_size']}], 'prompt_sha256':hashlib.sha256(text.encode()).hexdigest(),'uniform_prompt_sha256':sha(PACKAGE/'QWEN_QUERY_PROPOSAL_V1.txt'),'do_sample':False,'enable_thinking':False,'max_new_tokens':MAX_NEW_TOKENS,'created_utc':now()}
 append(OUT/'actual_requests.jsonl',req)
 return messages,req

def main():
 os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',CUDA_VISIBLE_DEVICES='0')
 pre=json.loads((OUT/'preflight.json').read_text())
 if pre['status']!='PASS' or pre['validated_images']!=20 or pre['errors']:raise RuntimeError('Preflight not passed')
 import torch,transformers
 from transformers import AutoProcessor,Qwen3_5ForConditionalGeneration
 settings=pre['settings'];prompt=(PACKAGE/'QWEN_QUERY_PROPOSAL_V1.txt').read_text()
 if sha(PACKAGE/'QWEN_QUERY_PROPOSAL_V1.txt')!=pre['prompt_sha256']:raise RuntimeError('Prompt changed after preflight')
 if torch.__version__!=settings['torch_version'] or transformers.__version__!=settings['transformers_version']:raise RuntimeError('Inference environment changed after preflight')
 meta={'run_id':RUN,'source_commit':IDENT['source_commit'],'actual_main_head':IDENT['actual_main_head'],'created_utc':IDENT['created_utc'],'runner_path':str(HERE/'runner.py'),'runner_sha256':sha(HERE/'runner.py'),'parser_sha256':sha(HERE/'qwen_json_parser.py'),'prior_successful_runner':'/home/wangyq/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/server_run/paris_route_qwen_smoke_20260927T141218Z_a01/runner.py','model_path':str(MODEL_PATH),'settings':settings,'prompt_sha256':pre['prompt_sha256'],'input_manifest_sha256':pre['input_manifest_sha256'],'protocol_sha256':pre['protocol_sha256'],'status':'LOADING_MODEL'}
 dump(OUT/'run_metadata.json',meta);status('LOADING_MODEL',completed=0,total=20);event('model_load_start')
 processor=AutoProcessor.from_pretrained(str(MODEL_PATH),local_files_only=True)
 model=Qwen3_5ForConditionalGeneration.from_pretrained(str(MODEL_PATH),local_files_only=True,dtype=torch.bfloat16,attn_implementation='sdpa',device_map='cuda:0');model.eval()
 if processor.__class__.__name__!='Qwen3VLProcessor':raise RuntimeError(f'Processor class changed: {processor.__class__.__name__}')
 meta['generation_config']={k:getattr(model.generation_config,k,None) for k in ('temperature','top_p','top_k','num_beams','repetition_penalty')};meta['status']='RUNNING';dump(OUT/'run_metadata.json',meta);event('model_loaded')
 counts={'success':0,'empty':0,'format_failed':0,'format_retries':0}
 for idx,image in enumerate(pre['images'],1):
  qid=image['query_view_id'];record={'run_id':RUN,'query_view_id':qid,'image_path':image['image_path'],'image_sha256':image['actual_sha256'],'image_size':image['image_size'],'status':'FORMAT_FAILED','candidates':[],'attempts':0,'error':None,'model_revision':settings['model_revision'],'prompt_sha256':pre['prompt_sha256']}
  for attempt in (1,2):
   messages,req=make_request(image,prompt,attempt)
   event('inference_start',index=idx,query_view_id=qid,attempt=attempt)
   x=processor.apply_chat_template(messages,tokenize=True,add_generation_prompt=True,return_dict=True,return_tensors='pt',enable_thinking=False)
   shapes={k:list(v.shape) for k,v in x.items() if hasattr(v,'shape')}
   with torch.inference_mode():y=model.generate(**x.to(model.device),do_sample=False,max_new_tokens=MAX_NEW_TOKENS,pad_token_id=processor.tokenizer.eos_token_id)
   raw=processor.batch_decode(y[:,x['input_ids'].shape[1]:],skip_special_tokens=True,clean_up_tokenization_spaces=False)[0]
   rawpath=OUT/'raw_outputs'/f'{qid}.attempt{attempt:02d}.txt';rawpath.parent.mkdir(exist_ok=True);rawpath.write_text(raw)
   record.update(attempts=attempt,raw_output_path=str(rawpath),raw_output_sha256=sha(rawpath),processing_shapes=shapes)
   try:
    candidates,normalization,normalized=parse_candidates(raw,*image['image_size'])
    normalized_path=rawpath.with_suffix('.normalized.txt');normalized_path.write_text(normalized)
    record.update(candidates=candidates,status='EMPTY' if not candidates else 'SUCCESS',normalization_type=normalization,normalized_path=str(normalized_path),normalized_sha256=sha(normalized_path),error=None)
    event('parsed',index=idx,query_view_id=qid,attempt=attempt,status=record['status'],candidates=len(candidates))
    break
   except (ValueError,json.JSONDecodeError) as exc:
    record['error']=str(exc);record['normalization_type']='INVALID'
    append(OUT/'errors.jsonl',{'utc':now(),'query_view_id':qid,'attempt':attempt,'category':'FORMAT','reason':str(exc),'raw_output_path':str(rawpath)})
    event('format_error',index=idx,query_view_id=qid,attempt=attempt,error=str(exc))
    if attempt==1:counts['format_retries']+=1
   finally:
    del x,y,messages
    torch.cuda.empty_cache()
  over=OUT/'overlays'/f'{qid}.png';overlay(image['image_path'],record['candidates'],over,record['status'])
  record.update(overlay_path=str(over),overlay_sha256=sha(over),completed_utc=now())
  append(OUT/'proposals.jsonl',record)
  if record['status']=='SUCCESS':counts['success']+=1
  elif record['status']=='EMPTY':counts['empty']+=1
  else:counts['format_failed']+=1
  status('RUNNING',completed=idx,total=20,counts=counts);event('query_complete',index=idx,query_view_id=qid,status=record['status'])
 review=OUT/'HUMAN_REVIEW_REQUIRED.csv'
 with review.open('w',newline='') as f:
  cols=['query_view_id','proposal_status','candidate_id','type','description','bbox_xyxy_1000','bbox_xyxy_640','duplicate_review_flag','overlay_path','human_accept_edit_reject','human_final_bbox_640','human_reason']
  w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
  for line in (OUT/'proposals.jsonl').read_text().splitlines():
   r=json.loads(line)
   for c in (r['candidates'] or [{}]):
    w.writerow({'query_view_id':r['query_view_id'],'proposal_status':r['status'],'candidate_id':c.get('candidate_id',''),'type':c.get('type',''),'description':c.get('description',''),'bbox_xyxy_1000':json.dumps(c.get('bbox_xyxy_1000','')),'bbox_xyxy_640':json.dumps(c.get('bbox_xyxy_640','')),'duplicate_review_flag':c.get('duplicate_review_flag',''),'overlay_path':r['overlay_path'],'human_accept_edit_reject':'','human_final_bbox_640':'','human_reason':''})
 summary=['# Phase 0 Stage A — provisional single-image proposals','',f'Run: `{RUN}`',f'Source/main: `{IDENT["source_commit"]}`',f'Model revision: `{settings["model_revision"]}`','',f'20 frozen input images; success: {counts["success"]}; empty candidates: {counts["empty"]}; format failed: {counts["format_failed"]}; format retries: {counts["format_retries"]}.','',f'Review candidates and coordinate overlays using `{review}` and `{OUT}/overlays/`. These are unverified proposals. No controls, masking, DINO or retrieval were run.','']
 (OUT/'RUN_SUMMARY.md').write_text('\n'.join(summary));meta.update(status='COMPLETE',completed_utc=now(),counts=counts);dump(OUT/'run_metadata.json',meta);status('COMPLETE',completed=20,total=20,counts=counts);event('stage_a_complete',counts=counts)

if __name__=='__main__':
 try:main()
 except BaseException as exc:
  obj={'run_id':RUN,'stage':'Stage A','status':'BLOCKED','utc':now(),'first_error':str(exc),'traceback':traceback.format_exc(),'last_successful_event':None}
  p=OUT/'events.jsonl'
  if p.exists():
   try:obj['last_successful_event']=json.loads(p.read_text().splitlines()[-1])
   except Exception:pass
  dump(OUT/'BLOCKED.json',obj);status('BLOCKED',first_error=str(exc));event('blocked',error=str(exc));raise
