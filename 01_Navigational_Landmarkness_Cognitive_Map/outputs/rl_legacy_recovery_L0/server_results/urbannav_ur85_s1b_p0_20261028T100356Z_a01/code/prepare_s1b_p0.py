"""Read-only source and provenance gate. No third-party/model imports."""
import argparse
import datetime
import hashlib
import json
import platform
import subprocess
import traceback
from pathlib import Path

CODE = Path('__EXECUTION_CODE_ROOT__')
BASE = CODE/'landmark_probe'
S0 = BASE/'s0_runs/urbannav_ur85_s0_20261025T163610Z_a01'
S1 = BASE/'s1_env_runs/urbannav_ur85_s1_env_r1_20261027T024829Z_a01'
FULL = BASE/'s1a_full_runs/urbannav_ur85_s1a_full_20261028T071015Z_a01'
STEP1 = BASE/'s1a_integration_runs/urbannav_ur85_s1a_step1_20261028T060452Z_a01'
COMMIT = '347ecfe8302219437b3f39b83eda6a79908302ad'
FROZEN_COMMIT = '53d4a37204231f9482985020d6067017563c7665'
FULL_COMMIT = '88dd7d474eb6ed08f3261b1a29b5f4dc1c5bf703'
PREFIX = '01_Navigational_Landmarkness_Cognitive_Map/outputs/rl_legacy_recovery_L0/'
MANIFEST = PREFIX+'s1a_frozen_v1_20261028/S1_EPISODES_FROZEN_v1.jsonl'
MANIFEST_HASH = 'f7bec0034a33345e0537b95794f78c6562db89b15532679785108ca29f636e3b'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(8*1024*1024), b''): h.update(block)
    return h.hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


def main(out, checkout):
    def git(*args): return subprocess.check_output(['git', '-C', str(checkout), *args])
    assert platform.node() == '__CONFIRMED_CONTAINER_HOSTNAME__', 'Container identity differs from user-confirmed container'
    assert git('rev-parse', 'HEAD').decode().strip() == COMMIT
    assert not git('status', '--porcelain'), 'Checkout not clean'
    package = checkout/(PREFIX+'s1b_visual_dependence_prep_20261028')
    expected = {'S1A_ACTION_DISTRIBUTION_AUDIT.csv', 'S1A_LOCAL_REVIEW.md', 'S1B_CONDITION_CONTRACT.json',
                'S1B_DIAGNOSTIC_BASELINES.md', 'S1B_PAIRED_METRICS_SPEC.md', 'S1B_VISUAL_DEPENDENCE_PROTOCOL.md', 'SERVER_S1B_HANDOFF.md'}
    assert {p.name for p in package.iterdir()} == expected
    rows = []
    for p in sorted(package.iterdir()):
        blob = git('show', COMMIT+':'+str(p.relative_to(checkout)))
        assert p.read_bytes() == blob
        rows.append({'role':'s1b_exact_commit', 'path':str(p), 'bytes':len(blob), 'sha256':sha(p)})
    contract = json.loads((package/'S1B_CONDITION_CONTRACT.json').read_text())
    assert contract['source']['full_results_commit'] == FULL_COMMIT
    assert contract['source']['frozen_tasks_commit'] == FROZEN_COMMIT
    assert contract['source']['frozen_manifest_sha256_git_blob'] == MANIFEST_HASH
    frozen = git('show', FROZEN_COMMIT+':'+MANIFEST)
    assert hashlib.sha256(frozen).hexdigest() == MANIFEST_HASH
    assert (checkout/MANIFEST).read_bytes() == frozen
    (out/'S1_EPISODES_FROZEN_v1.jsonl').write_bytes(frozen)
    # Anchor locally retained public results to their actual Git blob commit.
    public = PREFIX+'server_results/'+FULL.name+'/'
    names = git('ls-tree', '-r', '--name-only', FULL_COMMIT, public).decode().splitlines()
    assert len(names) == 11
    for name in names:
        blob = git('show', FULL_COMMIT+':'+name)
        p = FULL/'share_review'/Path(name).name
        assert p.read_bytes() == blob, 'Full publication differs: '+str(p)
        rows.append({'role':'full_published_evidence', 'path':str(p), 'bytes':len(blob), 'sha256':sha(p)})
    # Preserve and verify all existing formal+diagnostic checksum entries.
    for root, count in [(FULL,103),(STEP1,44)]:
        entries = (root/'SHA256SUMS').read_text().splitlines()
        assert len(entries) == count
        for line in entries:
            expected_hash, name = line.split(maxsplit=1)
            p = root/name.lstrip('*')
            assert sha(p) == expected_hash, 'Prior evidence changed: '+str(p)
        rows.append({'role':'original_artifact_checksums', 'path':str(root/'SHA256SUMS'), 'sha256':sha(root/'SHA256SUMS'), 'verified_artifacts':count})
    prior = json.loads((FULL/'S1A_SOURCE_AND_MANIFEST_HASHES.json').read_text())
    roles = {'legacy_source','s1_legacy_source','spatial_data','s1_adapter','environment_lock','checkpoint','s0_loader_source','approved_s0_contract'}
    seen = set()
    for row in prior['files']:
        if row['role'] not in roles or row['path'] in seen: continue
        seen.add(row['path']); p = Path(row['path']); actual = sha(p)
        record = {'role':row['role'], 'path':str(p), 'bytes':p.stat().st_size, 'sha256':actual,
                  'expected_sha256':row['sha256'], 'status':'PASS' if actual==row['sha256'] else 'FAIL'}
        rows.append(record)
        dump(out/'S1B_SOURCE_AND_MANIFEST_HASHES.json', {'status':'CHECKING','files':rows})
        assert actual == row['sha256'], 'Source/data hash changed: '+str(p)
    for name, expected_hash in [('s1a_full_runner.py','e40c2f961cf454dd208f12e4effbc65222f28b4fd56c75ee2a0e0b7115af82e5'),
                                ('s1a_formal_full_runner.py','b34929a655879da5ff6ffc566097951786c1edb9ad846dbeb3f0e90ed45f2812')]:
        p=BASE/'s1_adapters'/name
        assert sha(p)==expected_hash
        rows.append({'role':'unchanged_s1a_runner','path':str(p),'sha256':expected_hash,'bytes':p.stat().st_size})
    # Image priors are small metadata records only. Actual JPEG reads happen once in inventory.
    baselines = {}
    def add(name, digest, source):
        rec=baselines.setdefault(name, {'sha256':digest,'sources':[]})
        assert rec['sha256']==digest, 'Conflicting existing image baselines: '+name
        if source not in rec['sources']: rec['sources'].append(source)
    for e in [json.loads(x) for x in frozen.splitlines()]:
        for role, images in e['image_index'].items():
            for image in images: add(image['file_name'],image['sha256'],'frozen_manifest:'+e['episode_id']+':'+role)
    for p in [S0/'SMOKE_ASSET_HASH_CHECK.json', S1/'INPUT_IMAGE_MANIFEST.json', STEP1/'INPUT_IMAGE_MANIFEST.json', FULL/'INPUT_IMAGE_MANIFEST.json']:
        data=json.loads(p.read_text()); images=data['files'] if isinstance(data,dict) else data
        for image in images: add(Path(image['path']).name,image['sha256'],str(p))
        rows.append({'role':'prior_image_inventory','path':str(p),'sha256':sha(p),'rows':len(images)})
    dump(out/'PRIOR_IMAGE_HASH_BASELINES.json',baselines)
    result={'status':'PASS','source_commit':COMMIT,'frozen_commit':FROZEN_COMMIT,'full_results_commit':FULL_COMMIT,
            'manifest_sha256':MANIFEST_HASH,'seven_package_files':7,'legacy_source_count':54,'spatial_data_count':7,
            'checkpoint_hashed_only_not_deserialized':True,'files':rows}
    dump(out/'S1B_SOURCE_AND_MANIFEST_HASHES.json',result)
    dump(out/'RUN_SCOPE.json',{'run_id':out.name,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'container_hostname':platform.node(),'user_confirmed_container':'__CONFIRMED_CONTAINER_LABEL__','scope':'S1-B P0 only',
        'source_commit':COMMIT,'checkout':str(checkout),'model_calls_authorized':False,'rollouts_authorized':False,
        'environment_steps_authorized':False,'github_push_authorized':False,'mapping_human_approval':False,
        'stop':'WAITING_FOR_HUMAN_S1B_PREFLIGHT_REVIEW'})
    print(json.dumps({'status':'PASS','source_files':54,'data_files':7,'prior_image_hashes':len(baselines)}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',required=True,type=Path);p.add_argument('--checkout',required=True,type=Path);a=p.parse_args()
    try:main(a.output_dir,a.checkout)
    except Exception as e:
        dump(a.output_dir/'BLOCKED.json',{'status':'BLOCKED','stage':'source_gate','error':str(e),'traceback':traceback.format_exc()});raise
