#!/usr/bin/env python3
"""Offline Qwen visual route smoke; all identity/geography/answers stay in scorer-side files."""
import csv,datetime,hashlib,json,math,os,platform,random,shutil,sys,time,traceback
from pathlib import Path
from PIL import Image,ImageDraw

RUN_DIR=Path(__file__).resolve().parent
IDENTITY=json.loads((RUN_DIR/'run_identity.json').read_text())
RUN_ID=IDENTITY['run_id']; OUT=Path(IDENTITY['nas_output_dir'])
SYNC=Path('/home/wangyq/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/sync')
sys.path.insert(0,str(SYNC))
from qwen_json_parser import parse_model_json, _FULL_JSON_FENCE
MODEL=Path('/home/nas/wangyq/model_weights/Qwen/Qwen3.5-9B')
ROAD=Path('/home/nas/wangyq/Street_view_and_points_Paris/road')
PANOROAD=Path('/home/nas/wangyq/Street_view_and_points_Paris/Line_After_heading_clear_Paris_center_street_from0309_4_v1/Line_Points_3_to_road.shp')
STAGE='preflight'; COUNTS={'stage0':0,'stage1':0,'stage2':0}
SCHEMA=None; MANIFEST=None; CASES=None; ROUTES=None; PROCESSOR=None; MODEL_OBJ=None; REVISION=None

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(path,obj):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 tmp=path.with_name(path.name+'.tmp');tmp.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n');tmp.replace(path)
def write_new(path,text):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('x') as f:f.write(text)
def line(obj):return json.dumps(obj,ensure_ascii=False)+'\n'
def log(msg):
 text=f'[{utc()}] {msg}\n'
 print(text,end='',flush=True)
 with (OUT/'run.log').open('a',buffering=1) as f:f.write(text)
def status(state,**kw):
 obj=dict(run_id=RUN_ID,timestamp_utc=IDENTITY['timestamp_utc'],attempt=IDENTITY['attempt'],source_commit=IDENTITY['source_commit'],sync_mode=IDENTITY['sync_mode'],stage=STAGE,status=state,completed=COUNTS,time=utc(),**kw)
 save(OUT/'stage_status.json',obj);save(RUN_DIR/'stage_status.json',obj)
def hashfile(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for part in iter(lambda:f.read(8*1024*1024),b''):h.update(part)
 return h.hexdigest()
def sums():
 paths=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='sha256sums.txt' and not p.name.endswith('.tmp'))
 (OUT/'sha256sums.txt').write_text(''.join(f'{hashfile(p)}  {p.relative_to(OUT).as_posix()}\n' for p in paths))
 return dict(file_count=len(paths),sha256sums_path=str(OUT/'sha256sums.txt'),sha256sums_sha256=hashfile(OUT/'sha256sums.txt'))
def block(error):
 reason=str(error)
 record=dict(run_id=RUN_ID,timestamp_utc=IDENTITY['timestamp_utc'],attempt=IDENTITY['attempt'],source_commit=IDENTITY['source_commit'],sync_mode=IDENTITY['sync_mode'],first_error=reason,stage=STAGE,completed=COUNTS,time=utc(),error_type=type(error).__name__,traceback=traceback.format_exc(),result_dir=str(OUT),minimal_reproduction='See saved raw attempt and runner source',suggested_action='Inspect saved attempt and fix the first failed contract before a new run_id.')
 with (OUT/'errors.jsonl').open('a') as f:f.write(line(record))
 save(OUT/'BLOCKED.json',record);save(RUN_DIR/'BLOCKED.json',record)
 status('BLOCKED',first_error=reason)
 log('BLOCKED '+reason)
 hashes=sums();save(RUN_DIR/'partial_hash_summary.json',hashes)

def load_contract():
 global SCHEMA,MANIFEST,CASES,ROUTES
 MANIFEST=json.loads((SYNC/'ROUTE_SMOKE_MANIFEST_20260926.json').read_text())
 SCHEMA=json.loads((SYNC/'QWEN_OUTPUT_SCHEMAS_20260926.json').read_text())
 if MANIFEST['image_pattern']!='{panoid}_panorama_{view_index}.jpg':raise ValueError('Image filename contract changed unexpectedly')
 with (RUN_DIR/'inputs/candidate_route_steps.csv').open(encoding='utf-8-sig',newline='') as f:
  records=list(csv.DictReader(f))
 lookup={(r['route_id'],int(r['step_idx'])):r for r in records}
 ROUTES={r['route_id']:r for r in MANIFEST['routes']}
 CASES={}
 for route in MANIFEST['routes']:
  for c in route['proposal_cases']:
   row=lookup.get((route['route_id'],c['step_idx']))
   pano=next(s['pano_id'] for s in route['steps'] if s['step_idx']==c['step_idx'])
   if not row or row['pano_id']!=pano:raise ValueError('Route CSV join mismatch: '+c['case_id'])
   views=[]
   for v in range(4):
    p=Path(MANIFEST['image_root_server'])/MANIFEST['image_pattern'].format(panoid=pano,view_index=v)
    if not p.is_file():raise FileNotFoundError(str(p))
    with Image.open(p) as im:
     if im.size!=(640,640):raise ValueError('Original image is not 640x640: '+str(p))
    views.append(dict(path=str(p),view_index=v,absolute_center_heading=(float(row['heading_from_api'])+90*v)%360,sha256=hashfile(p)))
   CASES[c['case_id']]=dict(case_id=c['case_id'],route_id=route['route_id'],role=c['role'],primary_view_index=c['view_index'],views=views)
 return lookup

def verify_weights():
 provenance=json.loads((MODEL/'_provenance/source.json').read_text())
 validation=json.loads((MODEL/'_provenance/validation.json').read_text())
 config=json.loads((MODEL/'config.json').read_text());processor=json.loads((MODEL/'preprocessor_config.json').read_text())
 if not validation['passed'] or not config.get('vision_config') or processor.get('processor_class')!='Qwen3VLProcessor':raise RuntimeError('Local Qwen vision checkpoint contract failed')
 manifest=json.loads((MODEL/'_provenance/file_manifest.json').read_text())
 for row in manifest:
  p=MODEL/row['path']
  if not p.is_file() or p.stat().st_size!=row['size_bytes']:raise RuntimeError('Model file size mismatch: '+row['path'])
  if hashfile(p)!=row['sha256']:raise RuntimeError('Model SHA-256 mismatch: '+row['path'])
 save(OUT/'model_verification.json',dict(run_id=RUN_ID,model_path=str(MODEL),revision=provenance['revision'],architecture=config['architectures'],vision_config_present=True,processor=processor['processor_class'],file_count=len(manifest),total_bytes=sum(x['size_bytes'] for x in manifest),all_sha256_verified=True,source_manifest_sha256=hashfile(MODEL/'_provenance/file_manifest.json'),verified_at=utc()))
 return provenance['revision']

PROMPT_TEMPLATE='{"candidates":[{"candidate_id":1,"bbox_xyxy_640":[0,0,1,1],"type":"object","description":"visible cue","hypothesized_role":"possible navigation cue","visibility":"clear","uncertainty":0.5}]}'
def candidate_prompt(retry=False,error=''):
 intro=('This is a formatting retry on the SAME original 640x640 street-view image. Re-emit a COMPLETE JSON object from the image; do not copy an earlier answer. ' if retry else 'Review the original 640x640 street-view image. ')
 instructions='Return at most three clearly visible place or wayfinding cues; use only pixels. Describe observations, not a route choice. Respond with exactly one JSON object with only root key candidates. Every candidate has exactly these seven keys: candidate_id, bbox_xyxy_640, type, description, hypothesized_role, visibility, uncertainty. candidate_id is an integer or short string unique here. type is object, structural, text, or scene. visibility is clear, partial, occluded, or uncertain. uncertainty is a NUMBER from 0 to 1. Every bbox is [x1,y1,x2,y2] with finite original-image coordinates and 0<=x1<x2<=640, 0<=y1<y2<=640. Do not add view_index inside a candidate. Here is the exact FORMAT TEMPLATE; replace every placeholder value with your own image-grounded answer: '+PROMPT_TEMPLATE+' If nothing clear is visible, respond exactly {"candidates":[]}. No markdown, no explanation, no extra keys.'
 if retry:instructions+=' The previous response violated: '+error+'. Ensure every candidate includes uncertainty and every coordinate is within 640; never omit fields or add keys.'
 return intro+instructions

class FormatError(ValueError):
 def __init__(self,kind,message):super().__init__(message);self.kind=kind

def check_candidate(obj):
 if not isinstance(obj,dict) or set(obj)!={'candidates'}:raise FormatError('extra_or_missing','Root object must contain only candidates')
 cand=obj['candidates']
 if not isinstance(cand,list) or len(cand)>3:raise FormatError('structure','candidates must be list with at most 3 items')
 if not cand:return [],'no_clear_candidate'
 exact=set(SCHEMA['candidate_proposal']['candidate_object_exact_keys'])
 ids=set()
 for idx,c in enumerate(cand):
  if not isinstance(c,dict):raise FormatError('structure',f'candidate {idx} not an object')
  miss=exact-set(c);extra=set(c)-exact
  if miss or extra:raise FormatError('extra_or_missing',f'candidate {idx}: missing={sorted(miss)} extra={sorted(extra)}')
  id_=c['candidate_id']
  if isinstance(id_,bool) or not isinstance(id_,(int,str)) or isinstance(id_,str) and not 0<len(id_)<=24 or id_ in ids:raise FormatError('structure',f'candidate {idx}: invalid candidate_id')
  ids.add(id_)
  if not isinstance(c['type'],str) or c['type'] not in set(SCHEMA['candidate_proposal']['enums']['type'])-{'no_clear_candidate'}:raise FormatError('enum',f'candidate {idx}: invalid type')
  if c['visibility'] not in SCHEMA['candidate_proposal']['enums']['visibility']:raise FormatError('enum',f'candidate {idx}: invalid visibility')
  if not isinstance(c['description'],str) or not isinstance(c['hypothesized_role'],str):raise FormatError('structure',f'candidate {idx}: invalid description/role')
  u=c['uncertainty']
  if isinstance(u,bool) or not isinstance(u,(int,float)) or not math.isfinite(u) or not 0<=u<=1:raise FormatError('structure',f'candidate {idx}: uncertainty outside [0,1]')
  b=c['bbox_xyxy_640']
  if not isinstance(b,list) or len(b)!=4 or any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) for x in b):raise FormatError('structure',f'candidate {idx}: bbox has invalid numbers')
  x1,y1,x2,y2=b
  if not(0<=x1<x2<=640 and 0<=y1<y2<=640):raise FormatError('out_of_bounds',f'candidate {idx}: bbox outside 640x640: {b}')
 return cand,'ok'

def parse_attempt(raw,rawpath,meta):
 """Audit the exact reply and the only permitted wrapper removal before schema checks."""
 rawpath=Path(rawpath)
 try:
  obj,kind,normalized=parse_model_json(raw)
 except (ValueError,json.JSONDecodeError) as exc:
  trimmed=raw.strip()
  match=_FULL_JSON_FENCE.fullmatch(trimmed) if trimmed.startswith(chr(96)*3) else None
  if match is not None:
   kind='full_json_fence';normalized=match.group('body').strip()
  elif trimmed.startswith(chr(96)*3):
   kind='rejected_wrapper';normalized=None
  else:
   kind='none';normalized=trimmed
  meta.update(normalization_type=kind,normalization_error=str(exc))
  if normalized is not None:
   normpath=rawpath.with_suffix('.normalized.txt')
   write_new(normpath,normalized)
   meta.update(normalized_path=str(normpath),normalized_sha256=hashfile(normpath))
  else:
   meta.update(normalized_path=None,normalized_sha256=None)
  save(rawpath.with_suffix('.metadata.json'),meta)
  raise FormatError('json',f'Invalid model JSON: {exc}') from exc
 normpath=rawpath.with_suffix('.normalized.txt')
 write_new(normpath,normalized)
 meta.update(normalization_type=kind,normalized_path=str(normpath),normalized_sha256=hashfile(normpath))
 save(rawpath.with_suffix('.metadata.json'),meta)
 return obj

def image_inputs(images,prompt):
 content=[]
 for label,path in images:
  with Image.open(path) as im:rgb=im.convert('RGB')
  content.extend([{'type':'text','text':label+':'},{'type':'image','image':rgb}])
 content.append({'type':'text','text':prompt})
 messages=[{'role':'user','content':content}]
 x=PROCESSOR.apply_chat_template(messages,tokenize=True,add_generation_prompt=True,return_dict=True,return_tensors='pt',enable_thinking=False)
 return x,{k:list(v.shape) for k,v in x.items() if hasattr(v,'shape')}

def infer(images,prompt,limit=512):
 import torch
 x,shapes=image_inputs(images,prompt)
 x=x.to(MODEL_OBJ.device)
 with torch.inference_mode():y=MODEL_OBJ.generate(**x,do_sample=False,max_new_tokens=limit,pad_token_id=PROCESSOR.tokenizer.eos_token_id)
 return PROCESSOR.batch_decode(y[:,x['input_ids'].shape[1]:],skip_special_tokens=True,clean_up_tokenization_spaces=False)[0],shapes

def draw_box(image_path,candidates,outpath):
 with Image.open(image_path) as im:canvas=im.convert('RGB')
 d=ImageDraw.Draw(canvas)
 for c in candidates:
  box=c['bbox_xyxy_640'];d.rectangle(box,outline=(255,0,0),width=3)
  d.text((box[0],max(0,box[1]-14)),str(c['candidate_id']),fill=(255,0,0))
 outpath.parent.mkdir(parents=True,exist_ok=True);canvas.save(outpath)

def one_candidate(case_id,phase):
 case=CASES[case_id];v=case['primary_view_index'];image=case['views'][v]
 retry_error=''
 for attempt in [1,2]:
  prompt=candidate_prompt(retry=attempt==2,error=retry_error)
  prompt_hash=hashlib.sha256(prompt.encode()).hexdigest()
  raw,shapes=infer([('observed image',image['path'])],prompt)
  rawpath=OUT/phase/'candidate_raw'/f'{case_id}.attempt{attempt:02d}.txt'
  write_new(rawpath,raw)
  meta=dict(run_id=RUN_ID,timestamp_utc=IDENTITY['timestamp_utc'],attempt=attempt,source_commit=IDENTITY['source_commit'],sync_mode=IDENTITY['sync_mode'],case_id=case_id,image_path=image['path'],view_index=v,absolute_center_heading=image['absolute_center_heading'],image_sha256=image['sha256'],prompt_hash=prompt_hash,prompt=prompt,model_revision=REVISION,processing_shapes=shapes,raw_output_path=str(rawpath),raw_sha256=hashfile(rawpath))
  save(rawpath.with_suffix('.metadata.json'),meta)
  try:candidates,parse_status=check_candidate(parse_attempt(raw,rawpath,meta))
  except FormatError as error:
   save(rawpath.with_suffix('.error.json'),dict(run_id=RUN_ID,case_id=case_id,attempt=attempt,error_kind=error.kind,error=str(error),raw_output_path=str(rawpath)))
   log(f'{phase} {case_id} attempt{attempt:02d} parse error: {error}')
   if attempt==1:
    retry_error=str(error);continue
   raise RuntimeError(f'{phase} {case_id} attempt{attempt:02d}: {error}; raw={rawpath}')
  overlay=OUT/phase/'candidate_overlays'/f'{case_id}.attempt{attempt:02d}.png'
  draw_box(image['path'],candidates,overlay)
  return dict(run_id=RUN_ID,timestamp_utc=IDENTITY['timestamp_utc'],attempt=attempt,source_commit=IDENTITY['source_commit'],sync_mode=IDENTITY['sync_mode'],case_id=case_id,image_path=image['path'],view_index=v,absolute_center_heading=image['absolute_center_heading'],candidates=candidates,model_revision=REVISION,prompt_hash=prompt_hash,parse_status=parse_status,raw_output_path=str(rawpath),raw_sha256=meta['raw_sha256'],normalization_type=meta['normalization_type'],normalized_sha256=meta['normalized_sha256'],normalized_path=meta['normalized_path'],overlay_path=str(overlay),status='smoke_provisional')
 raise AssertionError('Unreachable retry state')

def route_options(route_id,lookup):
 import shapefile
 r=ROUTES[route_id]
 a=lookup[(route_id,2)];b=lookup[(route_id,4)]
 pano_source=shapefile.Reader(str(PANOROAD))
 road_by_pano={row['panoid']:row for row in pano_source.records() for row in [row.as_dict()]}
 in_id=int(road_by_pano[a['pano_id']]['nearest_st']);correct_id=int(road_by_pano[b['pano_id']]['nearest_st'])
 roads=shapefile.Reader(str(ROAD/'edges.shp'));nodes=shapefile.Reader(str(ROAD/'nodes.shp'))
 node_coords={x['osmid']:(x['x'],x['y']) for r in nodes.records() for x in [r.as_dict()]}
 edges=[r.as_dict() for r in roads.records()]
 incoming=edges[in_id];outgoing=edges[correct_id]
 common={incoming['u'],incoming['v']}&{outgoing['u'],outgoing['v']}
 if len(common)!=1:raise RuntimeError('Cannot identify unique shared OSM decision endpoint: '+route_id)
 node=next(iter(common));origin=node_coords[node]
 def bearing(p,q):
  a,b=map(math.radians,p);c,d=map(math.radians,q);dl=c-a
  x=math.sin(dl)*math.cos(d);y=math.cos(b)*math.sin(d)-math.sin(b)*math.cos(d)*math.cos(dl)
  return (math.degrees(math.atan2(x,y))+360)%360
 def near_other(shp):
  pts=shp.points
  if len(pts)<2:raise RuntimeError('Degenerate road geometry')
  if sum((u-v)**2 for u,v in (zip(pts[0],origin)))<sum((u-v)**2 for u,v in (zip(pts[-1],origin))):return pts[1]
  return pts[-2]
 approach_bearing=(bearing(near_other(roads.shape(in_id)),origin))
 valid=[]
 for i,e in enumerate(edges):
  if i==in_id or node not in [e['u'],e['v']]:continue
  if e['oneway'] and e['u']!=node:continue
  outbound=bearing(origin,near_other(roads.shape(i)))
  relative=((outbound-approach_bearing+180)%360)-180
  descriptor='left' if relative<-30 else 'right' if relative>30 else 'roughly straight'
  valid.append(dict(road_edge_index=i,node=node,relative_degrees=round(relative,2),relative_description=descriptor,absolute_outgoing_bearing=round(outbound,2),real_osmid=e['osmid']))
 if len(valid)!=2 or correct_id not in [x['road_edge_index'] for x in valid]:raise RuntimeError('Legal nonreturn exit contract failed: '+route_id+' found='+str(len(valid)))
 valid.sort(key=lambda x:x['road_edge_index'])
 rng=random.Random(42+sum(map(ord,route_id)));rng.shuffle(valid)
 for label,item in zip(['A','B'],valid):item['option_id']=label
 return dict(route_id=route_id,decision_node=node,incoming_edge_index=in_id,provisional_continuation_edge_index=correct_id,approach_bearing=round(approach_bearing,2),options=valid,road_edges_sha256=hashfile(ROAD/'edges.shp'),road_dbf_sha256=hashfile(ROAD/'edges.dbf'),status='provisional_geometry_check_not_gold')

def route_prompt(condition,options,route_images,retry=False,error=''):
 base='You are at a street intersection. Select one of the two LEGAL non-return exits listed below. IDs are anonymous. Use only the supplied images; do not guess place names or coordinates. If evidence is insufficient, set uncertain=true and make a tentative selection. '+ ' '.join(f"Option {x['option_id']}: path {x['relative_description']} relative to the approach." for x in options)
 if condition=='route_plus_current':base+=' The earlier route images are in observed travel order. Use them as visual memory together with the current four-view observation.'
 elif condition=='route_shuffled':base+=' The earlier route images are shown out of travel order. Compare them with the current four-view observation.'
 else:base+=' Only the current four-view observation is available.'
 base+=' Return exactly one JSON object with only chosen_edge_id, maneuver, evidence_view_id, evidence_candidates, reason, uncertain. chosen_edge_id must be A or B; maneuver must be left, right, forward, or unknown; evidence_view_id must be view_0..view_3 or empty string; evidence_candidates must be []; reason must describe visible evidence only; uncertain must be a JSON boolean. Example FORMAT only: {"chosen_edge_id":"A","maneuver":"unknown","evidence_view_id":"view_0","evidence_candidates":[],"reason":"visual evidence is limited","uncertain":true}. Replace values. No markdown or other text.'
 if retry:base+=' This is a formatting retry on the SAME images. Re-emit a complete JSON object with exactly the required fields. The previous reply failed: '+error+'. No markdown or explanation.'
 return base

def check_decision(o,case_id,condition):
 expected=set(SCHEMA['route_decision']['required'])-{'case_id','condition'}
 if not isinstance(o,dict) or set(o)!=expected:raise FormatError('extra_or_missing','Route decision fields mismatch: '+str(set(o) if isinstance(o,dict) else type(o)))
 if o['chosen_edge_id'] not in ['A','B'] or o['maneuver'] not in SCHEMA['route_decision']['maneuver'] or o['evidence_view_id'] not in ['', 'view_0','view_1','view_2','view_3'] or o['evidence_candidates']!=[] or not isinstance(o['reason'],str) or not isinstance(o['uncertain'],bool):raise FormatError('structure','Route decision value contract failed')
 return dict(run_id=RUN_ID,timestamp_utc=IDENTITY['timestamp_utc'],attempt=1,source_commit=IDENTITY['source_commit'],sync_mode=IDENTITY['sync_mode'],case_id=case_id,condition=condition,**o,status='smoke_provisional')

def stage2(lookup):
 global STAGE
 STAGE='stage2';status('RUNNING');log('Stage 2: constructing provisional geometry-checked anonymous options')
 maps={route_id:route_options(route_id,lookup) for route_id in ROUTES}
 save(OUT/'route_option_mapping_SCORER_ONLY.json',dict(run_id=RUN_ID,source_commit=IDENTITY['source_commit'],mapping=maps,not_passed_to_model=True))
 # Input draft only: no occlusion result without human-approved candidate boxes.
 save(OUT/'candidate_drop_INPUT_DRAFT_ONLY.json',dict(run_id=RUN_ID,status='DRAFT_ONLY_NOT_EVALUATED',reason='Candidate boxes require human review'))
 for route_id,r in ROUTES.items():
  target_view=next(c['view_index'] for c in r['proposal_cases'] if c['role']=='decision')
  def path(step,view):
   pano=r['steps'][step]['pano_id']
   p=Path(MANIFEST['image_root_server'])/MANIFEST['image_pattern'].format(panoid=pano,view_index=view)
   if not p.is_file():raise FileNotFoundError(str(p))
   return str(p)
  learn_steps=[0,1,2,4,5]
  for condition in ['route_plus_current','current_only','route_shuffled']:
   if condition=='route_shuffled':order=[4,1,0,3,2]
   elif condition=='route_plus_current':order=list(range(len(learn_steps)))
   else:order=[]
   imgs=[(f'route memory image {j+1}',path(learn_steps[k],target_view)) for j,k in enumerate(order)]
   imgs += [(f'current view_{v}',path(3,v)) for v in range(4)]
   retry_error=''
   for attempt in [1,2]:
    prompt=route_prompt(condition,maps[route_id]['options'],imgs,retry=attempt==2,error=retry_error)
    log(f'Route decision {route_id} {condition} attempt{attempt:02d}')
    raw,shapes=infer(imgs,prompt,limit=320)
    name=f'{route_id}.{condition}.attempt{attempt:02d}.txt'
    rawpath=OUT/'route_raw'/name
    write_new(rawpath,raw)
    meta=dict(run_id=RUN_ID,timestamp_utc=IDENTITY['timestamp_utc'],attempt=attempt,source_commit=IDENTITY['source_commit'],sync_mode=IDENTITY['sync_mode'],model_revision=REVISION,route_id=route_id,condition=condition,prompt=prompt,prompt_hash=hashlib.sha256(prompt.encode()).hexdigest(),input_image_sha256=[hashfile(p) for _,p in imgs],input_image_paths=imgs,processing_shapes=shapes,raw_output_path=str(rawpath),raw_sha256=hashfile(rawpath))
    save(rawpath.with_suffix('.metadata.json'),meta)
    try:
     decision=check_decision(parse_attempt(raw,rawpath,meta),route_id+'_'+condition,condition)
    except FormatError as error:
     save(rawpath.with_suffix('.error.json'),dict(run_id=RUN_ID,route_id=route_id,condition=condition,attempt=attempt,error_kind=error.kind,error=str(error),raw_output_path=str(rawpath)))
     log(f'route {route_id} {condition} attempt{attempt:02d} parse error: {error}')
     if attempt==1:
      retry_error=str(error)
      continue
     raise RuntimeError(f'route {route_id} {condition} attempt{attempt:02d}: {error}; raw={rawpath}')
    decision.update(attempt=attempt,raw_output_path=str(rawpath),raw_sha256=meta['raw_sha256'],normalization_type=meta['normalization_type'],normalized_sha256=meta['normalized_sha256'],normalized_path=meta['normalized_path'],prompt_hash=meta['prompt_hash'],model_revision=REVISION)
    decision['provisional_correct']=next(x['road_edge_index'] for x in maps[route_id]['options'] if x['option_id']==decision['chosen_edge_id'])==maps[route_id]['provisional_continuation_edge_index']
    break
   with (OUT/'route_decisions.jsonl').open('a') as f:f.write(line(decision))
   COUNTS['stage2']+=1;status('RUNNING')
 status('COMPLETE');log('Stage 2 completed six provisional decisions')

def review_doc():
 lines=['# HUMAN_REVIEW_REQUIRED — smoke/provisional','','Run ID: `'+RUN_ID+'`','','Every candidate is an unverified visual proposal. Review each box for actual visibility, fit to the described cue, duplication, transient occlusion, and recognition from neighboring views. Enter ACCEPT/EDIT/REJECT/UNCERTAIN; record the final box, reason, and whether it is identifiable nearby.','','| Case | Candidate | View index | Proposed bbox 640 | Review (ACCEPT/EDIT/REJECT/UNCERTAIN) | Final bbox 640 | Reason | Identifiable nearby? |','|---|---|---:|---|---|---|---|---|']
 for row in (json.loads(x) for x in (OUT/'candidate_proposals.jsonl').read_text().splitlines()):
  for c in row['candidates']:
   lines.append(f"| {row['case_id']} | {c['candidate_id']} | {row['view_index']} | {c['bbox_xyxy_640']} |  |  |  |  |")
 lines+=['','## Route choices','', 'The option mapping and choices are provisional geometry checks. A human must confirm exit legality, route continuity, capture-time stability, and the actual intended continuation before treating any action as gold. No candidate-drop conclusion was computed.','']
 (OUT/'HUMAN_REVIEW_REQUIRED.md').write_text('\n'.join(lines))
 shutil.copy2(OUT/'HUMAN_REVIEW_REQUIRED.md',RUN_DIR/'HUMAN_REVIEW_REQUIRED.md')

def main():
 global STAGE,PROCESSOR,MODEL_OBJ,REVISION
 os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',CUDA_VISIBLE_DEVICES='0')
 import torch,transformers
 from transformers import AutoProcessor,Qwen3_5ForConditionalGeneration
 torch.manual_seed(42);random.seed(42);torch.backends.cuda.matmul.allow_tf32=False
 status('PREPARING');log('Starting '+RUN_ID+' source_commit='+IDENTITY['source_commit'])
 if not torch.cuda.is_available():raise RuntimeError('CUDA unavailable')
 lookup=load_contract()
 REVISION=verify_weights()
 save(OUT/'environment.json',dict(run_id=RUN_ID,timestamp_utc=IDENTITY['timestamp_utc'],attempt=1,source_commit=IDENTITY['source_commit'],sync_mode=IDENTITY['sync_mode'],python=sys.version,platform=platform.platform(),torch=torch.__version__,transformers=transformers.__version__,cuda=torch.version.cuda,gpu=torch.cuda.get_device_name(0),vram_bytes=torch.cuda.get_device_properties(0).total_memory,free_project_bytes=shutil.disk_usage('/home/wangyq').free,free_nas_bytes=shutil.disk_usage('/home/nas/wangyq').free,model_path=str(MODEL),model_revision=REVISION,processor='Qwen3VLProcessor',dtype='bfloat16',attention='sdpa',transformers_git_commit='96331a9f93b72697f160a958d2883d4b49a56739',inference_offline=True))
 save(OUT/'run_manifest.json',dict(run_id=RUN_ID,timestamp_utc=IDENTITY['timestamp_utc'],attempt=1,source_commit=IDENTITY['source_commit'],sync_mode=IDENTITY['sync_mode'],model_revision=REVISION,status='smoke_provisional',manifest_sha256=hashfile(SYNC/'ROUTE_SMOKE_MANIFEST_20260926.json'),schema_sha256=hashfile(SYNC/'QWEN_OUTPUT_SCHEMAS_20260926.json'),route_csv_sha256=hashfile(RUN_DIR/'inputs/candidate_route_steps.csv'),cases=CASES,stage0_order=MANIFEST['smoke_policy']['first_pass_cases'],model_input_excludes=['GPS','panoid','P/N/I','VLAD scores','gold action'],third_party_dinov2_read_only=True))
 (OUT/'errors.jsonl').touch(exist_ok=True)
 STAGE='stage0';status('LOADING_MODEL');log('Loading Qwen3.5-9B locally')
 PROCESSOR=AutoProcessor.from_pretrained(str(MODEL),local_files_only=True)
 MODEL_OBJ=Qwen3_5ForConditionalGeneration.from_pretrained(str(MODEL),local_files_only=True,dtype=torch.bfloat16,attn_implementation='sdpa',device_map='cuda:0');MODEL_OBJ.eval()
 status('RUNNING');log('Model loaded; stage0 begins')
 for case_id in MANIFEST['smoke_policy']['first_pass_cases']:
  log('Stage0 '+case_id)
  row=one_candidate(case_id,'stage0')
  with (OUT/'stage0_parsed.jsonl').open('a') as f:f.write(line(row))
  COUNTS['stage0']+=1;status('RUNNING')
 if COUNTS['stage0']!=2:raise RuntimeError('Stage0 count mismatch')
 log('Stage0 complete: 2 cases validated')
 STAGE='stage1';status('RUNNING')
 for r in MANIFEST['routes']:
  for c in r['proposal_cases']:
   log('Stage1 '+c['case_id'])
   row=one_candidate(c['case_id'],'stage1')
   with (OUT/'candidate_proposals.jsonl').open('a') as f:f.write(line(row))
   COUNTS['stage1']+=1;status('RUNNING')
 if COUNTS['stage1']!=6:raise RuntimeError('Stage1 count mismatch')
 log('Stage1 complete: 6 cases validated')
 stage2(lookup)
 review_doc()
 STAGE='final';status('COMPLETE');log('All requested stages completed; all outputs provisional smoke')
 h=sums();save(RUN_DIR/'hash_summary.json',h)
 print('SUCCESS '+RUN_ID+' '+json.dumps(COUNTS),flush=True)

if __name__=='__main__':
 try:main()
 except BaseException as e:block(e);sys.exit(1)
