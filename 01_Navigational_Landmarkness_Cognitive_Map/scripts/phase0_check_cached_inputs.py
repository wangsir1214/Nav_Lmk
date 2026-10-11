"""Targeted local read-only cache check for the frozen Phase 0 preparation.

Validates 20 selected query sources and 168 reference VLAD files on mounted NAS.
The remote runner must still hash the live model and centers before inference.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
import sys

from PIL import Image, __version__ as PILLOW_VERSION

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / 'outputs/pilot0/reviewed_v1_20260923'
AUDIT = ROOT / 'outputs/pilot0/server_return_audit_20260924/source'
PREP = ROOT / 'outputs/pilot0/phase0_intervention_prep_20261011'
NAS = Path('Z:/wangyq')


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def records(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def mapped(server_path: str) -> Path:
    prefix = '/home/nas/wangyq/'
    if not server_path.startswith(prefix):
        raise ValueError('NAS path outside expected prefix')
    return NAS / server_path[len(prefix):]


def main() -> None:
    selection = json.loads((PREP / 'selection_manifest.json').read_text(encoding='utf-8'))
    run = json.loads((AUDIT / 'features/run_config.json').read_text(encoding='utf-8'))
    request = TASK / 'configs/baseline_request_v2.json'
    if run['request_config_sha256'] != digest(request):
        raise ValueError('Baseline request config does not match saved run')
    if run['task_manifest_sha256'] != digest(TASK / 'task_manifest.json'):
        raise ValueError('Task manifest does not match saved run')
    if run['request']['request_id'] != selection['observer_request_id']:
        raise ValueError('Selected task requests another observer')
    index = records(AUDIT / 'features/feature_index.csv')
    if len(index) != 212 or len({r['view_id'] for r in index}) != 212:
        raise ValueError('Expected 212 indexed feature rows')
    refs = records(TASK / 'data/references.csv')
    queries = records(TASK / 'data/queries.csv')
    ix = {r['view_id']: r for r in index}
    if len(refs) != 168 or len(queries) != 44:
        raise ValueError('Frozen query/gallery count changed')
    chosen = selection['queries']
    if len(chosen) != 20:
        raise ValueError('Selection count changed')
    failures = []
    checked = {'reference_vlad': 0, 'source_jpeg': 0, 'cached_png': 0, 'resize_pixel_equal': 0}
    for row in refs:
        view = row['view_id']
        entry = ix[view]
        path = mapped(entry['vlad_path'])
        if not path.is_file() or digest(path) != entry['vlad_sha256']:
            failures.append(f'reference VLAD hash: {view}')
        else:
            checked['reference_vlad'] += 1
    fixed640 = NAS / 'GSV_Paris/0-All_GSV_3059_4per'
    fixed448 = NAS / 'GSV_Paris/0-All_GSV_3059_4per_448_448'
    for row in chosen:
        view = row['query_view_id']
        entry = ix[view]
        original = fixed640 / row['image_relative_path']
        resized = fixed448 / entry['image_448_relative_path']
        if not original.is_file() or digest(original) != row['image_sha256']:
            failures.append(f'original JPEG hash: {view}')
            continue
        checked['source_jpeg'] += 1
        if not resized.is_file() or digest(resized) != entry['image_448_sha256']:
            failures.append(f'cached 448 PNG hash: {view}')
            continue
        checked['cached_png'] += 1
        with Image.open(io.BytesIO(original.read_bytes())) as a, Image.open(resized) as b:
            if a.size != (640, 640) or b.size != (448, 448) or b.mode != 'RGB':
                failures.append(f'image dimensions/mode: {view}')
            elif a.convert('RGB').resize((448, 448), Image.Resampling.BICUBIC).tobytes() != b.tobytes():
                failures.append(f'Pillow full resize pixel mismatch: {view}')
            else:
                checked['resize_pixel_equal'] += 1
    centers = mapped(run['request']['vlad']['centers_path'])
    centers_ok = centers.is_file() and digest(centers) == run['centers_sha256']
    if not centers_ok:
        failures.append('VLAD center hash')
    report = {'status': 'PASS_LOCAL_CACHE_CHECK' if not failures else 'FAIL_LOCAL_CACHE_CHECK',
              'scope': 'selected 20 query images + all 168 reference VLAD files + small centers file; no GPU',
              'checked': checked, 'pillow_version': PILLOW_VERSION,
              'pillow_version_expected': run['request']['preprocessing']['pillow_version'],
              'centers_hash_match': centers_ok, 'model_weight_hash_status': 'RECORDED_NOT_REHASHED_LOCAL_4.55GB',
              'feature_index_sha256': digest(AUDIT / 'features/feature_index.csv'),
              'expected_feature_index_sha256': run['feature_index_sha256'],
              'failures': failures, 'python': sys.version}
    if PILLOW_VERSION != report['pillow_version_expected']:
        report['failures'].append('Pillow version mismatch with saved run')
        report['status'] = 'FAIL_LOCAL_CACHE_CHECK'
    path = PREP / 'local_cache_preflight.json'
    if path.exists():
        raise FileExistsError('Do not overwrite existing preflight')
    path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'report': str(path), 'status': report['status'], 'checked': checked,
                      'failures': report['failures']}, indent=2))
    if report['failures']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
