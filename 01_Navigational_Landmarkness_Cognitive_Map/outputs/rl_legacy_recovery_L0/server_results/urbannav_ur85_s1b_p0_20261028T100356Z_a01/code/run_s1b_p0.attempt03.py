"""S1-B P0: native graph, streamed assets, observation-only tests. NO PPO."""
import argparse
import ast
import collections
import copy
import csv
import datetime
import hashlib
import importlib.metadata as md
import json
import math
import os
import pickle
import random
import sys
import traceback
import typing
from pathlib import Path

CODE=Path('__EXECUTION_CODE_ROOT__')
BASE=CODE/'landmark_probe'
S1=BASE/'s1_env_runs/urbannav_ur85_s1_env_r1_20261027T024829Z_a01'
FULL=BASE/'s1a_full_runs/urbannav_ur85_s1a_full_20261028T071015Z_a01'
IMAGES=Path('__APPROVED_DATA_ROOT__/GSV_Paris/0-All_GSV_3100_perspective_together')
SHP=Path('__APPROVED_DATA_ROOT__/Street_view_and_points_Paris/Line_After_heading_clear_Paris_center_street_from0309_4_v1/Line_Points_3_to_road.shp')
HEADING=Path('__APPROVED_DATA_ROOT__/Street_view_and_points_Paris/GoogleAPIMETADAT/Paris_Points_heading_3059/Paris_Points_heading_3059.csv')


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''): h.update(b)
    return h.hexdigest()


def default(v):
    if hasattr(v,'item'): return v.item()
    if isinstance(v,Path): return str(v)
    raise TypeError(type(v).__name__)


def dump(path,value):
    Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False,default=default)+'\n')


def table(path,rows):
    with Path(path).open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def load(path): return json.loads(Path(path).read_text())
def say(msg): print(datetime.datetime.now(datetime.timezone.utc).isoformat(),msg,flush=True)


def isolation(out):
    counts=collections.Counter()
    environment_step_files={str(CODE/'urbannav.py'),str(CODE/'urbannav_vec.py'),str(BASE/'s1_adapters/s1_fixed_goal_r1.py')}
    pano_data_file=str(CODE/'pano_data.py')
    observed_files={str(CODE/'observations.py'),pano_data_file,str(CODE/'pano_graph.py')}
    def audit(event,args):
        if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
            p=Path(os.fsdecode(args[0])).absolute(); mode,flags=args[1:3]
            if 'trained_models' in p.parts or p.suffix.lower() in {'.pt','.pth','.ckpt','.safetensors'}:
                raise PermissionError('P0 runtime cannot access checkpoint')
            writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
            if writing and not p.resolve().is_relative_to(out): raise PermissionError('Write outside P0 run: '+str(p))
        if event in {'socket.connect','socket.connect_ex','socket.bind','subprocess.Popen','os.system'}:
            raise PermissionError('P0 runtime network/subprocess disabled')
        if event=='import' and args[0].split('.')[0] in {'neptune','new_baseline_ppo','experiments_deepmind_real','ppo','ppo_trainer'}:
            raise PermissionError('P0 policy/training import disabled')
    sys.addaudithook(audit)
    def profile(frame,event,arg):
        if event!='call':return
        p=frame.f_code.co_filename; name=frame.f_code.co_name
        if p==pano_data_file and name in {'load_all_pano_data','load_all_pano_data_depth','__init__'}:
            raise PermissionError('Full image-library preload prohibited')
        if p in environment_step_files and name=='step':
            counts['environment_step_calls']+=1
            raise PermissionError('Environment actions not part of P0')
        if '/torch/nn/modules/module.py' in p and name in {'_call_impl','_wrapped_call_impl'}:
            counts['model_calls']+=1
            raise PermissionError('Model forward prohibited in P0')
        if p in observed_files:
            if name in {'observation','get_pano_perspective','fetch','build_graph','set_BFS_graph'}:counts[Path(p).name+':'+name]+=1
    sys.setprofile(profile)
    return counts


def native_graph(out):
    import yaml,networkx as nx,geopandas as gpd,pandas as pd
    import pano_graph
    from s1_fixed_goal_r1 import BoundedDataset
    config=yaml.safe_load((CODE/'new_baseline_ppo/config_deepmind_real.yml').read_text())
    config.update(max_graph_depth=30,num_actors=1)
    expected=load(FULL/'S1A_RUN_CONFIG.json')['runtime']
    for k,v in expected.items():assert config[k]==v,('runtime configuration changed',k)
    data=load(config['dataset_path'])
    dataset=BoundedDataset(IMAGES,{n['id'] for n in data['nodes']})
    pg=pano_graph.PanoGraph(prefetch_depth=0,min_graph_depth=1,max_graph_depth=30,max_cache_size=100,dataset=dataset)
    pg.build_graph(config['dataset_path']); original_graph=pg.street_view_graph.to_undirected().copy()
    assert (len(original_graph),original_graph.number_of_edges())==(3058,3310)
    pg.set_BFS_graph(config['center_pano_id'])
    assert (len(pg.street_view_graph),pg.street_view_graph.number_of_edges())==(550,549)
    assert nx.is_connected(pg.street_view_graph)
    dataset.allowed_panos=set(pg.street_view_graph)
    nodes=sorted(pg.street_view_graph,key=lambda p:p.encode('utf-8'))
    sf=gpd.read_file(SHP);hf=pd.read_csv(HEADING)
    metadata={}
    for p in nodes:
        sr=sf[sf.panoid==p];hr=hf[hf.panoid==p]
        assert len(sr)==len(hr)==1,('Missing or duplicate SHP/heading',p)
        row=sr.iloc[0];heading=float(hr.iloc[0].heading_from_api)
        assert math.isfinite(heading) and pg.get_heading(p)==pano_graph.ConstrainAngle(180,heading)
        coords=pg.get_coords(p)
        assert coords['lat']==row['lat'] and coords['lng']==row['lon']
        assert all(math.isfinite(float(x)) for x in coords.values())
        metadata[p]={'pano_id':p,'heading_from_api':heading,'internal_heading':pg.get_heading(p),
            'runtime_lat':coords['lat'],'runtime_lon':coords['lng'],
            'road_segment_index':str(row.get('nearest_st',row.get('nearest_street_segment_index',''))),
            'road_osmid':str(row.get('nearest__1',row.get('nearest_street_osmid','')))}
    prior={x['pano']:x for x in load(S1/'NATIVE_RUNTIME_NODES.json')}
    assert set(prior)==set(nodes)
    for p in nodes:
        assert prior[p]['coords']==pg.get_coords(p) and prior[p]['heading']==pg.get_heading(p)
    edges=sorted([sorted(e,key=lambda p:p.encode('utf-8')) for e in pg.street_view_graph.edges])
    dump(out/'NATIVE_RUNTIME_GRAPH.json',{'nodes':nodes,'edges':edges,'max_depth':30,'center':config['center_pano_id']})
    dump(out/'NATIVE_GRAPH_AUDIT.json',{'status':'PASS','native_methods':['PanoGraph.build_graph','PanoGraph.set_BFS_graph'],
        'original_nodes':3058,'original_edges':3310,'runtime_nodes':550,'runtime_edges':549,'connected':True,
        'S1_ENV_nodes_coords_heading_match':True,'runtime_coordinates':'SHP lat/lon attributes',
        'graph_sha256':sha(out/'NATIVE_RUNTIME_GRAPH.json'),'dataset_preloaded':False,'image_cache_panos':len(dataset.images_dict)})
    assert not dataset.images_dict
    table(out/'S1B_NODE_HEADING_AND_ROAD.csv',list(metadata.values()))
    dump(out/'RUNTIME_CONFIG.json',expected)
    return config,pg,original_graph,metadata


def donor_mapping(out,pg,original_graph,metadata):
    import networkx as nx
    from s1b_visual_adapter_v1 import mapping_bytes
    nodes=list(pg.street_view_graph)
    raw=mapping_bytes(nodes); repeated=mapping_bytes(reversed(nodes))
    assert raw==repeated
    target=out/'S1B_DONOR_MAPPING_v1.jsonl';target.write_bytes(raw)
    rows=[json.loads(x) for x in raw.splitlines()];mapping={r['source_pano_id']:r['donor_pano_id'] for r in rows}
    # Independent construction; no use of generator helper for this verification.
    ranked=sorted(nodes,key=lambda p:(hashlib.sha256(b'S1B-donor-v1|20261028|'+p.encode()).digest(),p.encode()))
    assert [r['source_pano_id'] for r in rows]==ranked
    assert all(mapping[p]==ranked[(i+1)%550] for i,p in enumerate(ranked))
    assert set(mapping)==set(mapping.values())==set(nodes) and len(set(mapping.values()))==550
    assert all(s!=d for s,d in mapping.items())
    visited=[];p=ranked[0]
    for _ in range(550):visited.append(p);p=mapping[p]
    assert p==ranked[0] and len(set(visited))==550
    road_edges=set()
    for a,b in original_graph.edges:
        if a in metadata and b in metadata:
            sa,sb=metadata[a]['road_segment_index'],metadata[b]['road_segment_index']
            if sa and sb and sa!=sb:road_edges.add(tuple(sorted([sa,sb])))
    relations=[]
    for s,d in mapping.items():
        a,b=metadata[s],metadata[d];distance=pg.distance_between_panos(s,d)
        segment_known=a['road_segment_index'] not in {'','nan','None'} and b['road_segment_index'] not in {'','nan','None'}
        osm_known=a['road_osmid'] not in {'','nan','None'} and b['road_osmid'] not in {'','nan','None'}
        relations.append({'source_pano_id':s,'donor_pano_id':d,'distance_m':distance,
            'source_lat':a['runtime_lat'],'source_lon':a['runtime_lon'],'donor_lat':b['runtime_lat'],'donor_lon':b['runtime_lon'],
            'source_road_segment':a['road_segment_index'],'donor_road_segment':b['road_segment_index'],
            'source_road_osmid':a['road_osmid'],'donor_road_osmid':b['road_osmid'],
            'same_road_segment':a['road_segment_index']==b['road_segment_index'] if segment_known else 'UNKNOWN',
            'same_osmid_attribute':a['road_osmid']==b['road_osmid'] if osm_known else 'UNKNOWN',
            'segments_linked_by_original_graph_edge':tuple(sorted([a['road_segment_index'],b['road_segment_index']])) in road_edges if segment_known else 'UNKNOWN',
            'source_donor_direct_original_graph_edge':original_graph.has_edge(s,d),
            'original_graph_shortest_hops':nx.shortest_path_length(original_graph,s,d),
            'runtime_tree_shortest_hops':nx.shortest_path_length(pg.street_view_graph,s,d),
            'within_50m_descriptive_only':distance<=50,'within_100m_descriptive_only':distance<=100})
    table(out/'S1B_DONOR_GEOGRAPHIC_RELATIONS.csv',relations)
    distances=[r['distance_m'] for r in relations]
    audit={'status':'PASS','mapping_human_approval':'PENDING','navigation_authorized':False,'source_count':550,'unique_donors':550,
        'self_mappings':0,'source_donor_sets_equal':True,'all_in_runtime_graph':True,'single_cycle_length':550,
        'repeat_generation_byte_identical':True,'independent_algorithm_check':True,'mapping_sha256':sha(target),
        'seed_prefix':'S1B-donor-v1|20261028|','row_order':'SHA-256 raw digest bytes then pano UTF-8 bytes',
        'serialization':'UTF-8, ensure_ascii=False, compact JSON separators, insertion keys rank/source_pano_id/donor_pano_id/source_sort_sha256, LF trailing newline',
        'generator_sha256':sha(Path(__file__).with_name('s1b_visual_adapter_v1.py')),
        'graph_sha256':sha(out/'NATIVE_RUNTIME_GRAPH.json'),'heading_csv_sha256':sha(HEADING),
        'distance_m':{'min':min(distances),'mean':sum(distances)/550,'max':max(distances)},
        'same_road_segment_count':sum(r['same_road_segment'] is True for r in relations),
        'same_osmid_attribute_count':sum(r['same_osmid_attribute'] is True for r in relations),
        'adjacent_segment_count':sum(r['segments_linked_by_original_graph_edge'] is True for r in relations),
        'within_50m_count':sum(d<=50 for d in distances),'within_100m_count':sum(d<=100 for d in distances),
        'road_relation_limit':'Existing nearest-road attributes and graph-linked segment relation; no new road-geometric intersection or named-street reconstruction. 50/100m are descriptive flags, never remapping criteria.',
        'outcome_based_remapping':False}
    dump(out/'S1B_DONOR_MAPPING_AUDIT.json',audit)
    return mapping,audit


def inventory(out,metadata):
    import cv2,numpy as np
    baselines=load(out/'PRIOR_IMAGE_HASH_BASELINES.json');prior_count=0;total=0;hashes={};seen=set()
    fields=['pano_id','view_index','file_name','absolute_path','bytes','sha256','decoded_hwc_sha256','width','height','channels','dtype','minimum','maximum','heading_from_api','view_center_heading','baseline_status','prior_sha256','prior_evidence_sources','status']
    with (out/'S1B_DONOR_IMAGE_INVENTORY.csv').open('x',newline='',buffering=1) as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for p in sorted(metadata,key=lambda p:p.encode()):
            for index in range(16):
                name=f'{p}_{index:02d}.jpg';path=IMAGES/name
                before=path.stat();raw=path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
                assert raw[:2]==b'\xff\xd8' and raw[-2:]==b'\xff\xd9',('Not JPEG',str(path))
                img=cv2.imread(str(path),cv2.IMREAD_COLOR)
                assert img is not None and img.shape==(84,84,3) and img.dtype==np.uint8,('Bad decoded image',str(path))
                after=path.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),('Image changed during read',str(path))
                prior=baselines.get(name)
                if prior:
                    assert digest==prior['sha256'],('Image differs from existing independent hash',str(path),prior['sha256'],digest)
                    prior_count+=1
                assert name not in seen;seen.add(name);hashes[name]=digest
                w.writerow(dict(pano_id=p,view_index=index,file_name=name,absolute_path=str(path),bytes=len(raw),sha256=digest,
                    decoded_hwc_sha256=hashlib.sha256(img.tobytes()).hexdigest(),width=84,height=84,channels='BGR',dtype='uint8',minimum=int(img.min()),maximum=int(img.max()),
                    heading_from_api=metadata[p]['heading_from_api'],view_center_heading=(metadata[p]['heading_from_api']+22.5*index)%360,
                    baseline_status='MATCHED_PREEXISTING_INDEPENDENT_HASH' if prior else 'NEW_P0_REPRODUCIBILITY_BASELINE',
                    prior_sha256=prior['sha256'] if prior else '',prior_evidence_sources=json.dumps(prior['sources'],ensure_ascii=False) if prior else '',status='PASS'))
                total+=1
                del img,raw
            if total%800==0:say(f'Image inventory {total}/8800; streamed, no decoded image cache')
    assert total==8800
    report={'status':'PASS','nodes':550,'views_per_node':16,'images':total,'missing_images':0,'missing_or_duplicate_headings':0,
        'matched_prior_hashes':prior_count,'new_baselines':total-prior_count,'prior_baselines_outside_runtime_graph':len(set(baselines)-seen),
        'streaming':True,'maximum_inventory_decoded_images_held':1,'inventory_sha256':sha(out/'S1B_DONOR_IMAGE_INVENTORY.csv'),
        'claim_limit':'Matched pre-existing records are not proof of an immutable training-time image corpus; other hashes are first established in this P0 run.'}
    dump(out/'S1B_IMAGE_INVENTORY_AUDIT.json',report)
    return hashes,report


def heading_tests(out,adapter,metadata):
    import pano_data,pano_graph
    # Independent reference reproduces the actual normalized float, including ties.
    def reference(theta):
        normalized=(theta+360)%360
        idx=min(range(17),key=lambda i:(abs(i*22.5-normalized),i))
        return idx%16
    explicit=[]
    cases=[(-720,0),(-360,0),(-0.001,0),(0,0),(0.001,0),(360,0),(720,0),
           (-11.25,15),(11.25,0),(33.75,1),(348.75,15),(348.750001,0),(11.250001,1),(11.249999,0),(-180,8),(180,8)]
    for angle,expected in cases:
        actual=pano_data.find_nearest_angle_index(angle)
        assert actual==expected==reference(angle)==pano_graph.find_nearest_angle_index(angle)
        explicit.append({'relative_angle':angle,'expected':expected,'actual':actual,'status':'PASS'})
    total=0;different_source_donor_index=0;roundoff_tie_shifts=0
    for p in sorted(metadata):
        donor=adapter.mapping[p];h=metadata[donor]['internal_heading']
        indices=[]
        for k in range(16):
            for delta in [0,11.25-1e-7,11.25,11.25+1e-7]:
                y=h+22.5*k+delta
                selected=adapter.select(p,y)
                rel=y-h;actual=selected['donor_view_index']
                assert actual==reference(rel)==pano_graph.find_nearest_angle_index(rel)
                assert adapter.select(p,y)['donor_pano_id']==donor
                if delta==0:indices.append(actual)
                if delta==11.25 and actual!=(k%16):roundoff_tie_shifts+=1
                different_source_donor_index+=selected['source_view_index']!=actual
                total+=1
        assert set(indices)==set(range(16))
    rejects=[]
    for p,y in [('P0_OUTSIDE_GRAPH',0),(next(iter(metadata)),float('nan')),(next(iter(metadata)),float('inf'))]:
        try:adapter.select(p,y)
        except ValueError as error:rejects.append(str(error))
        else:raise AssertionError('Invalid pano/yaw accepted')
    report={'status':'PASS','explicit_boundary_tests':explicit,'all_node_alignment_tests':total,'donor_pano_stable_on_revisit':True,
        'each_donor_all_16_views_observed_in_index_tests':True,'different_source_donor_view_indices':different_source_donor_index,
        'float_heading_add_subtract_exact_tie_shifts':roundoff_tie_shifts,
        'normalization':'(theta + 360) % 360','ties':'first minimum in [0,22.5,...,360]; 360 index16 becomes0; at348.75 choose15',
        'floating_point_note':'Use actual legacy float arithmetic without epsilon adjustment. Adding then subtracting a nonbinary heading can perturb an intended exact half-way input.',
        'invalid_input_rejections':rejects,'view_center_spacing_deg':22.5,'historical_view_fov_deg':60,
        'same_geographic_direction':'nearest available historical donor view, up to11.25 degrees quantization; no continuous reprojection'}
    dump(out/'S1B_HEADING_ALIGNMENT_TEST.json',report)
    return report


def observation_tests(out,pg,config,adapter):
    import cv2,numpy as np,torch,urbannav_vec
    from s1_fixed_goal_r1 import BoundedDataset,FixedGoalEnv,state
    from s1b_visual_adapter_v1 import array_hash
    # Execute only these two exact pure tensor conversion functions, not module imports.
    source=(CODE/'new_baseline_ppo/common/utils.py').read_text();tree=ast.parse(source)
    selected=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'_to_tensor','batch_obs'}]
    assert len(selected)==2
    space={'torch':torch,'np':np,'defaultdict':collections.defaultdict,'List':typing.List,'Dict':typing.Dict,'Optional':typing.Optional}
    exec(compile(ast.Module(body=selected,type_ignores=[]),str(CODE/'new_baseline_ppo/common/utils.py'),'exec'),space)
    batch_obs=space['batch_obs']
    episodes=[json.loads(x) for x in (out/'S1_EPISODES_FROZEN_v1.jsonl').read_text().splitlines()]
    cases=[];resets=0;changed=0
    for ep in [episodes[0],episodes[-1]]:
        ds=BoundedDataset(IMAGES,set(pg.street_view_graph));pg.dataset=ds
        cfg=copy.deepcopy(config);cfg['seed']=ep['evaluation_seed']
        env=FixedGoalEnv(cfg,pg,ds,ep['start_pano_id'],ep['goal_pano_id'],ep['initial_internal_yaw_deg'],1000)
        obs,_=env.reset();resets+=1
        assert set(obs)=={'view_image','goal'} and obs['goal'].dtype==np.float64
        assert np.array_equal(obs['goal'],ep['goal_normalized_2d'])
        donor=adapter.mapping[ep['start_pano_id']];dh=adapter.headings[donor]
        # Isolated observation fixtures, NOT environment actions or trajectories.
        yaws=[ep['initial_internal_yaw_deg'],0,360,-11.25,dh+11.25,dh+348.75]
        for fixture,y in enumerate(yaws):
            env.rotation_yaw_=urbannav_vec.ConstrainAngle(180,float(y))
            obs=env._get_observation();st=state(env)
            path=IMAGES/f"{st['pano']}_{st['view_index']:02d}.jpg"
            real=np.transpose(cv2.imread(str(path),cv2.IMREAD_COLOR),(2,0,1))
            assert np.array_equal(obs['view_image'],real)
            before_image=obs['view_image'].copy();before_goal=obs['goal'].copy()
            # Nonzero sentinels check adapter cannot mutate separately owned recurrent inputs.
            nonvisual={'goal_hidden':np.arange(512,dtype=np.float32).reshape(1,1,512),
                       'policy_hidden':(-np.arange(512,dtype=np.float32)).reshape(1,1,512),
                       'previous_action':np.array([[4]],np.float32),'previous_reward':np.zeros((1,1),np.float32),'mask':np.ones((1,1),np.float32)}
            def snapshot():
                return {'state':state(env),'env_reward':env._reward,'env_done':env._done,'frame':env._frame_count,
                    'game_sha256':hashlib.sha256(pickle.dumps(env._game.__dict__)).hexdigest(),
                    'nonvisual_hashes':{k:array_hash(v) for k,v in nonvisual.items()},
                    'python_rng':hashlib.sha256(repr(random.getstate()).encode()).hexdigest(),
                    'numpy_rng':hashlib.sha256(pickle.dumps(np.random.get_state())).hexdigest(),
                    'torch_cpu_rng':hashlib.sha256(torch.get_rng_state().numpy().tobytes()).hexdigest()}
            before=snapshot();full_batch=batch_obs([obs],torch.device('cpu'))
            for condition in ['Full-Passthrough','NoImage','ShuffledImage']:
                result,meta=adapter.replace(obs,condition=condition,source_pano=st['pano'],yaw=st['yaw'])
                assert set(result)==set(obs) and result['goal'] is obs['goal']
                assert np.array_equal(obs['view_image'],before_image) and np.array_equal(obs['goal'],before_goal)
                assert snapshot()==before
                batch=batch_obs([result],torch.device('cpu'))
                assert torch.equal(batch['goal'],full_batch['goal'])
                assert tuple(batch['view_image'].shape)==(1,3,84,84) and batch['view_image'].dtype==torch.float32
                assert torch.equal(batch['view_image'][0],torch.from_numpy(result['view_image']).float())
                if condition=='Full-Passthrough':
                    assert result['view_image'] is obs['view_image'] and torch.equal(batch['view_image'],full_batch['view_image'])
                elif condition=='NoImage': assert np.count_nonzero(result['view_image'])==0
                else:
                    donor_image=np.transpose(cv2.imread(str(IMAGES/meta['supplied_file_name']),cv2.IMREAD_COLOR),(2,0,1))
                    assert np.array_equal(result['view_image'],donor_image)
                    changed+=not np.array_equal(result['view_image'],real)
                cases.append({'episode_id':ep['episode_id'],'fixture':fixture,'metadata':meta,
                    'nonvisual_same_object_and_values':True,'environment_and_rng_unchanged':True,'legacy_viewimage_matches_cv2_pixels':True,
                    'legacy_batch_obs_equal_value_cast':True,'goal_dtype_before':'float64','goal_dtype_batched':'float32',
                    'runtime_state':st,'nonvisual_sha256':before['nonvisual_hashes'],'status':'PASS'})
        assert env._frame_count==0
        ds.images_dict.clear()
    report={'status':'PASS','tests':len(cases),'limited_native_state_fixtures':12,'fixed_goal_resets':resets,
        'environment_actions':0,'model_calls':0,'full_passthrough_cases':12,'noimage_cases':12,'shuffled_cases':12,
        'shuffled_differs_from_real_cases':changed,'cases':cases,
        'scope':'Observation and equal-value CPU cast only; no CNN/PPO forward, no causal action or recurrent-output claim',
        'batch_obs_source':'Exact AST nodes _to_tensor and batch_obs compiled from hash-verified legacy file; policy module not imported'}
    dump(out/'S1B_VISUAL_ADAPTER_TESTS.json',report)
    return report


def static_audit(out):
    cnn=(CODE/'new_baseline_ppo/models/simple_cnn.py').read_text();t=ast.parse(cnn)
    cls=next(n for n in t.body if isinstance(n,ast.ClassDef) and n.name=='RGBCNNOracle')
    fwd=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='forward')
    divisions=[n for n in ast.walk(fwd) if isinstance(n,ast.BinOp) and isinstance(n.op,ast.Div) and isinstance(n.right,ast.Constant) and n.right.value==255]
    assert len(divisions)==1
    runner=BASE/'s1_adapters/s1a_formal_full_runner.py';text=runner.read_text()
    checks={
        'categorical_not_argmax':'deterministic=False' in text,
        'python_numpy_torch_cuda_reset':'random.seed(seed);np.random.seed(seed);torch.manual_seed(seed);torch.cuda.manual_seed_all(seed)' in text,
        'model_previous_reward_zero':'pr=torch.zeros(1,1)' in text,
        'zero_dual_hidden':'gh=torch.zeros(1,1,512' in text and 'ph=torch.zeros_like(gh)' in text,
        'zero_initial_mask':'mask=torch.zeros(1,1' in text,
        'single_categorical_sample_assertion':"captures['sample_calls']==1" in text,
        'cnn_input_equality_assertion':"torch.equal(ins[0]['view_image'],current['batch']['view_image'])" in text,
        'normalization_assertion':"current['batch']['view_image']/255.0" in text,
    }
    assert all(checks.values()),checks
    evidence={}
    for name in ['MODEL_ENVIRONMENT_INTEGRATION.md','RNN_STATE_AUDIT.json','GOAL_DTYPE_AUDIT.json','RNG_AND_SAMPLING_AUDIT.json','S1A_PREVIOUS_REWARD_SEMANTICS.md']:
        p=FULL/name
        evidence[name]={'path':str(p),'sha256':sha(p)}
    dump(out/'S1B_STATIC_INTERFACE_CHECK.json',{'status':'PASS','checks':checks,'cnn_divide_by_255_count':1,
        'cnn_division_line':divisions[0].lineno,'legacy_runner_sha256':sha(runner),'inherited_evidence':evidence,
        'model_execution_in_P0':False,'cnn_proof':'static unchanged source plus earlier S1-A actual prehook/convolution-input assertions; not a new P0 model test'})
    (out/'S1B_ACTION_RNG_INTERFACE_AUDIT.md').write_text('''# 动作与随机性接口：静态及既有执行证据复核

原五动作：0前进，1左22.5°，2左67.5°，3右22.5°，4右67.5°。原 policy2.py 的 DeepMindOracle.act 经 action_distribution 产生 categorical 分布；deterministic=False 调用原 sample，非 mode/argmax。本轮未改变 logits、softmax、温度、动作集合或动作 mask。三种极低概率动作不能人为强化。

原 Step1/Step2 runner 的源文件哈希均一致；逐步 sample 恰一次、CUDA RNG 变化、真实 CNN 输入与 /255 的原执行断言证据保留在 S1-A。P0 不重新执行策略、不抽样动作、不更新 GRU。新 adapter 不接收策略、GRU 或 RNG 对象。

未来每个条件、每题、每次重复独立设置 frozen evaluation_seed：Python、NumPy、Torch CPU、全部 CUDA；重新建立环境、固定 Goal、初始 pano/yaw；Goal/Policy hidden 均为 float32 [1,1,512] 零张量，previous action=0，mask=0。之后按原 runner 消费 hidden 输出、更新 previous action/mask；model_previous_reward 每步恒为0，environment_reward另存。相同seed并不要求不同视觉条件产生相同动作。

目标 SHP lat/lon 的既有归一化、float64 observation→batch_obs float32 cast、原3-hop前进和 reward 保持不变。首次 distance<100m 成功，1000动作上限，成功优先，无自动换目标/重置。现阶段仅核验观察与原静态逻辑，不宣称新的干预闭环已通过。
''')


def main(out):
    assert load(out/'S1B_SOURCE_AND_MANIFEST_HASHES.json')['status']=='PASS'
    assert not (out/'S1B_DONOR_MAPPING_v1.jsonl').exists(),'Refuse overwriting existing mapping'
    counts=isolation(out)
    import torch,numpy as np,geopandas as gpd,shapely,cv2
    def no_load(*args,**kwargs):raise PermissionError('No checkpoint deserialization in P0')
    torch.load=no_load;torch.jit.load=no_load
    lock=load(S1/'S1_ENVIRONMENT_LOCK.json')
    versions={name:md.version(name) for name in lock['packages']}
    for name,record in lock['packages'].items():assert versions[name]==record['version'],('Dependency changed',name)
    assert Path(sys.executable)==Path(lock['python_executable']) and np.__version__=='1.26.4'
    dump(out/'S1B_ENVIRONMENT.json',{'python':sys.version,'executable':sys.executable,'packages':versions,
        'module_files':{m.__name__:m.__file__ for m in [torch,np,gpd,shapely,cv2]},'environment':dict(os.environ),
        'no_installs':True,'no_cuda_initialization':not torch.cuda.is_initialized(),'torch_role':'CPU tensor cast only, no model'})
    static_audit(out);say('Source/combined environment/static interface PASS')
    config,pg,original,metadata=native_graph(out);say('Native graph/heading PASS: 550 nodes,549 edges')
    mapping,mapping_audit=donor_mapping(out,pg,original,metadata);say('Deterministic donor mapping generated; awaiting human approval')
    hashes,image_audit=inventory(out,metadata);say('Streamed image inventory PASS:8800')
    from s1b_visual_adapter_v1 import VisualAdapter
    adapter=VisualAdapter(IMAGES,out/'S1B_DONOR_MAPPING_v1.jsonl',mapping_audit['mapping_sha256'],
                          {p:m['internal_heading'] for p,m in metadata.items()},hashes)
    heading_audit=heading_tests(out,adapter,metadata)
    visual=observation_tests(out,pg,config,adapter)
    assert not torch.cuda.is_initialized()
    sys.setprofile(None)
    assert counts.get('environment_step_calls',0)==counts.get('model_calls',0)==0
    dump(out/'P0_EXECUTION_SCOPE_AUDIT.json',{'status':'PASS','profile_counts':dict(counts),'checkpoint_deserializations':0,
        'ppo_imported':any(k.startswith('new_baseline_ppo') for k in sys.modules),'cuda_initialized':False,
        'model_calls':0,'navigation_environment_steps':0,'full_library_preload_calls':0,'nas_writes':0,
        'protection':'Python audit hook: output-only writes/no network/subprocess/checkpoint; profile rejects policy-forward/environment-step/preloader calls',
        'limited_reset_and_observation_fixtures_only':True})
    assert not any(k.startswith('new_baseline_ppo') for k in sys.modules)
    dump(out/'P0_TEST_STATUS.json',{'status':'PASS','run_id':out.name,'nodes':550,'images':8800,
        'image_audit':image_audit,'mapping_sha256':mapping_audit['mapping_sha256'],'visual_tests':visual['tests'],
        'heading_tests':heading_audit['all_node_alignment_tests']+len(heading_audit['explicit_boundary_tests']),
        'mapping_human_approval':False,'next_execution_authorized':False,'stop':'WAITING_FOR_HUMAN_S1B_PREFLIGHT_REVIEW'})
    say('P0 PASS; WAITING_FOR_HUMAN_S1B_PREFLIGHT_REVIEW')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=Path,required=True);args=parser.parse_args()
    out=args.output_dir.resolve()
    try:main(out)
    except Exception as e:
        sys.setprofile(None)
        dump(out/'BLOCKED.json',{'status':'BLOCKED','run_id':out.name,'error':str(e),'traceback':traceback.format_exc(),
            'stop':'WAITING_FOR_HUMAN_S1B_PREFLIGHT_REVIEW','no_automatic_fallback':True});raise
