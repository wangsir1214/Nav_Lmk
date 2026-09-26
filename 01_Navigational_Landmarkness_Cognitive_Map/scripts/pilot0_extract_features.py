"""Extract fixed DINOv2 G/14 layer-31 value patches and frozen AnyLoc VLAD for 212 active views."""
import argparse
import csv
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import numpy as np

from pilot0_prepare_weights import file_sha
from pilot0_server_preflight import run as preflight
from pilot0_vlad import G14ValueExtractor, aggregate, load_centers, load_input_png


def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def save_npy_atomic(path, array):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f'.partial.{os.getpid()}')
    with temp.open('wb') as f:
        np.save(f, np.asarray(array, dtype=np.float32), allow_pickle=False)
        f.flush(); os.fsync(f.fileno())
    if path.exists():
        temp.unlink()
        raise FileExistsError(path)
    temp.replace(path)


def run(a):
    import torch
    config = json.loads((a.task_dir / 'configs/baseline_request_v2.json').read_text(encoding='utf-8'))
    if config['request_id'] != 'full_image_g14_l31_value_c32_urban_448png_fp32_v2':
        raise ValueError('Unexpected request configuration')
    paths = json.loads(a.paths.read_text(encoding='utf-8'))
    dest = a.output.resolve()
    if dest.exists() and any(dest.iterdir()):
        raise FileExistsError('Output directory must be new and empty: ' + str(dest))
    smoke_path = a.smoke_report or a.task_dir/'validation/g14_vlad_smoke.json'
    smoke = json.loads(smoke_path.read_text(encoding='utf-8'))
    if not smoke.get('passed') or smoke.get('request_id') != config['request_id']:
        raise ValueError('A passing v2 G/14 + VLAD smoke report is required')
    if smoke.get('weights_sha256') != file_sha(paths['dinov2_g14_weights']) or smoke.get('centers_sha256') != file_sha(paths['vlad_centers']):
        raise ValueError('Smoke-test weights/centers differ from extraction inputs')
    report = a.report or a.task_dir/'validation/server_preflight_before_feature_extract.json'
    preflight(a.task_dir, a.paths, True, report)
    dest.mkdir(parents=True, exist_ok=False)
    queries = read_csv(a.task_dir / 'data/queries.csv')
    refs = read_csv(a.task_dir / 'data/references.csv')
    if len(queries) != 44 or len(refs) != 168:
        raise ValueError('Frozen active image counts mismatch')
    views = {r['view_id']: r for r in queries + refs}
    if len(views) != 212:
        raise ValueError('Query/reference view overlap or duplicate')
    source_commit = subprocess.check_output(['git', '-C', paths['dinov2_source'], 'rev-parse', 'HEAD'], text=True).strip()
    if source_commit != config['model']['source_revision_checked']:
        raise ValueError('DINOv2 source revision mismatch')
    if subprocess.check_output(['git', '-C', paths['dinov2_source'], 'status', '--porcelain', '--untracked-files=no'], text=True).strip():
        raise ValueError('DINOv2 source has tracked changes')
    patch_dir, vlad_dir = dest/'features/patches', dest/'features/vlad'
    patch_dir.mkdir(parents=True); vlad_dir.mkdir()
    centers_path = Path(paths['vlad_centers'])
    centers = load_centers(centers_path)
    extractor = G14ValueExtractor(paths['dinov2_source'], paths['dinov2_g14_weights'], a.device)
    torch.manual_seed(42); np.random.seed(42)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    if str(a.device).startswith('cuda'):
        torch.cuda.reset_peak_memory_stats()
    rows = []; begin = time.time()
    for i, view_id in enumerate(sorted(views), 1):
        r = views[view_id]
        png = Path(paths['paris_fixed_448']) / Path(r['image_relative_path']).with_suffix('.png')
        patch_path, vlad_path = patch_dir/f'{view_id}.npy', vlad_dir/f'{view_id}.npy'
        if patch_path.exists() or vlad_path.exists():
            raise FileExistsError('Refusing partial/stale feature cache: ' + view_id)
        tensor = load_input_png(png)
        patches = extractor(tensor)
        if patches.shape != (1024, 1536):
            raise ValueError('Local descriptor shape mismatch: ' + view_id)
        vector = aggregate(patches, centers)
        save_npy_atomic(patch_path, patches)
        save_npy_atomic(vlad_path, vector)
        rows.append({'view_id': view_id, 'pano_id': r['pano_id'], 'role': 'query' if view_id in {q['view_id'] for q in queries} else 'reference',
                     'image_relative_path': r['image_relative_path'], 'image_448_relative_path': png.name,
                     'image_sha256': r['image_sha256'], 'image_448_sha256': file_sha(png),
                     'patch_feature_path': str(patch_path), 'patch_feature_sha256': file_sha(patch_path),
                     'patch_shape': '1024x1536', 'patch_dtype': 'float32', 'patch_order': 'row_major',
                     'vlad_path': str(vlad_path), 'vlad_sha256': file_sha(vlad_path),
                     'vlad_shape': '49152', 'vlad_dtype': 'float32', 'config_id': config['request_id']})
        if i % 16 == 0 or i == len(views):
            print(json.dumps({'done': i, 'total': len(views), 'elapsed_seconds': time.time()-begin}), flush=True)
    extractor.close()
    index = dest/'feature_index.csv'
    with index.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    try:
        import torchvision
        tvver = torchvision.__version__
    except Exception as exc:
        tvver = repr(exc)
    run_cfg = {'request': config, 'task_manifest_sha256': file_sha(a.task_dir/'task_manifest.json'),
               'request_config_sha256': file_sha(a.task_dir/'configs/baseline_request_v2.json'),
               'weights_sha256': file_sha(paths['dinov2_g14_weights']), 'centers_sha256': file_sha(centers_path),
               'dinov2_commit': source_commit, 'torch': torch.__version__, 'torchvision': tvver,
               'numpy': np.__version__, 'device': a.device, 'cuda': torch.version.cuda,
               'python': sys.version, 'tf32': False, 'peak_cuda_allocated_bytes': torch.cuda.max_memory_allocated() if str(a.device).startswith('cuda') else None,
               'image_count': len(rows), 'feature_index_sha256': file_sha(index)}
    (dest/'run_config.json').write_text(json.dumps(run_cfg, indent=2) + '\n', encoding='utf-8')
    if a.log:
        (dest/'run.log').write_text(json.dumps({'completed': True, 'images': len(rows), 'elapsed_seconds': time.time()-begin}, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'passed': len(rows)==212, 'output_dir': str(dest), 'feature_index_sha256': file_sha(index),
                      'weights_sha256': run_cfg['weights_sha256'], 'centers_sha256': run_cfg['centers_sha256'],
                      'elapsed_seconds': time.time()-begin}, indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--task-dir',type=Path,required=True);p.add_argument('--paths',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--device',default='cuda')
    p.add_argument('--report',type=Path);p.add_argument('--smoke-report',type=Path);p.add_argument('--log',action='store_true')
    run(p.parse_args())
