"""Resume only unfinished P0 observation tests; preserve mapping and inventory."""
import argparse,csv,json,sys,traceback,importlib.metadata as md
from pathlib import Path
from run_s1b_p0 import (load,dump,sha,isolation,native_graph,observation_tests,S1,IMAGES)

def main(out):
    mapping_audit=load(out/'S1B_DONOR_MAPPING_AUDIT.json')
    image_audit=load(out/'S1B_IMAGE_INVENTORY_AUDIT.json')
    heading_audit=load(out/'S1B_HEADING_ALIGNMENT_TEST.json')
    assert all(x['status']=='PASS' for x in [mapping_audit,image_audit,heading_audit])
    mapping_sha=sha(out/'S1B_DONOR_MAPPING_v1.jsonl')
    inventory_sha=sha(out/'S1B_DONOR_IMAGE_INVENTORY.csv')
    assert mapping_sha==mapping_audit['mapping_sha256'] and inventory_sha==image_audit['inventory_sha256']
    assert not (out/'S1B_VISUAL_ADAPTER_TESTS.json').exists()
    counts=isolation(out)
    import torch,numpy as np,geopandas as gpd,shapely
    def no_load(*args,**kwargs):raise PermissionError('P0 forbids checkpoint deserialization')
    torch.load=no_load;torch.jit.load=no_load
    lock=load(S1/'S1_ENVIRONMENT_LOCK.json')
    assert Path(sys.executable)==Path(lock['python_executable'])
    for name,rec in lock['packages'].items():assert md.version(name)==rec['version']
    nested=out/'observation_resume';nested.mkdir()
    config,pg,original,metadata=native_graph(nested)
    assert sha(nested/'NATIVE_RUNTIME_GRAPH.json')==sha(out/'NATIVE_RUNTIME_GRAPH.json')
    with (out/'S1B_DONOR_IMAGE_INVENTORY.csv').open() as f:rows=list(csv.DictReader(f))
    assert len(rows)==8800 and all(r['status']=='PASS' for r in rows)
    hashes={r['file_name']:r['sha256'] for r in rows}
    from s1b_visual_adapter_v1 import VisualAdapter
    adapter=VisualAdapter(IMAGES,out/'S1B_DONOR_MAPPING_v1.jsonl',mapping_sha,
                          {p:m['internal_heading'] for p,m in metadata.items()},hashes)
    visual=observation_tests(out,pg,config,adapter)
    assert not torch.cuda.is_initialized()
    sys.setprofile(None)
    assert counts.get('environment_step_calls',0)==counts.get('model_calls',0)==0
    assert not any(k.startswith('new_baseline_ppo') for k in sys.modules)
    assert sha(out/'S1B_DONOR_MAPPING_v1.jsonl')==mapping_sha
    assert sha(out/'S1B_DONOR_IMAGE_INVENTORY.csv')==inventory_sha
    dump(out/'P0_EXECUTION_SCOPE_AUDIT.json',{'status':'PASS','profile_counts_successful_observation_resume':dict(counts),
        'checkpoint_deserializations':0,'ppo_imported':False,'cuda_initialized':False,'model_calls':0,
        'navigation_environment_steps':0,'full_library_preload_calls':0,'nas_writes':0,
        'completed_native_observation_fixture_resets':2,'earlier_reset_before_checker_failure':1,
        'mapping_and_inventory_unchanged_after_resume':True,'full_image_inventory_passes':1,
        'protection':'Output-only writes; no network/subprocess/checkpoint; model forward/environment step/preload rejected',
        'limited_reset_and_observation_fixtures_only':True})
    dump(out/'P0_TEST_STATUS.json',{'status':'PASS','run_id':out.name,'nodes':550,'images':8800,'image_audit':image_audit,
        'mapping_sha256':mapping_sha,'visual_tests':visual['tests'],
        'heading_tests':heading_audit['all_node_alignment_tests']+len(heading_audit['explicit_boundary_tests']),
        'mapping_human_approval':False,'next_execution_authorized':False,'stop':'WAITING_FOR_HUMAN_S1B_PREFLIGHT_REVIEW'})
    print('P0 observation resume PASS; WAITING_FOR_HUMAN_S1B_PREFLIGHT_REVIEW',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',required=True,type=Path);a=p.parse_args()
    try:main(a.output_dir.resolve())
    except Exception as error:
        sys.setprofile(None);dump(a.output_dir/'BLOCKED.json',{'status':'BLOCKED','run_id':a.output_dir.name,
            'error':str(error),'traceback':traceback.format_exc(),'stage':'remaining_observation_tests'});raise
