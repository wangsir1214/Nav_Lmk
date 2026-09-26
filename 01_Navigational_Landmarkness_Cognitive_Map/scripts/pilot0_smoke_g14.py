"""One-image server smoke test; real weights/CUDA are required, no task metrics computed."""
import argparse
import json
from pathlib import Path
import time
import subprocess
import numpy as np
from pilot0_prepare_weights import file_sha
from pilot0_vlad import G14ValueExtractor, aggregate, load_centers, load_input_png


def run(a):
    import torch
    torch.manual_seed(42)
    np.random.seed(42)
    config = json.loads((a.task_dir / 'configs/baseline_request_v2.json').read_text())
    if config['request_id'] != 'full_image_g14_l31_value_c32_urban_448png_fp32_v2':
        raise ValueError('This smoke test expects the v2 PNG preprocessing request')
    paths = json.loads(a.paths.read_text())
    source_commit = subprocess.check_output(['git', '-C', paths['dinov2_source'], 'rev-parse', 'HEAD'], text=True).strip()
    if source_commit != config['model']['source_revision_checked']:
        raise ValueError('DINOv2 source commit differs from the requested version')
    source_dirty = subprocess.check_output(['git', '-C', paths['dinov2_source'], 'status', '--porcelain', '--untracked-files=no'], text=True).strip()
    if source_dirty:
        raise ValueError('DINOv2 source has tracked local changes; record and review before running')
    import csv
    with (a.task_dir / 'data/queries.csv').open(encoding='utf-8-sig', newline='') as f:
        row = next(csv.DictReader(f))
    image_path = Path(paths['paris_fixed_448']) / Path(row['image_relative_path']).with_suffix('.png')
    centers = load_centers(paths['vlad_centers'])
    begin = time.time()
    extractor = G14ValueExtractor(paths['dinov2_source'], paths['dinov2_g14_weights'], a.device)
    if str(a.device).startswith('cuda'):
        torch.cuda.reset_peak_memory_stats()
    tensor = load_input_png(image_path)
    first = extractor(tensor); second = extractor(tensor)
    if first.shape != (1024, 1536):
        raise ValueError('Patch shape mismatch')
    descriptor = aggregate(first, centers); repeat = aggregate(second, centers)
    # Independent torch form to verify the local NumPy VLAD implementation.
    x = torch.nn.functional.normalize(torch.from_numpy(first), dim=1)
    c = torch.from_numpy(centers)
    labels = (x @ torch.nn.functional.normalize(c, dim=1).T).argmax(dim=1)
    residuals = torch.stack([(x[labels == k] - c[k]).sum(dim=0) for k in range(32)])
    reference = torch.nn.functional.normalize(torch.nn.functional.normalize(residuals, dim=1).flatten(), dim=0).numpy()
    checks = {'vlads_dim_49152': descriptor.shape == (49152,),
              'unit_norm': abs(float(np.linalg.norm(descriptor)) - 1) <= 1e-5,
              'finite': bool(np.isfinite(descriptor).all()),
              'repeat_patch_max_abs': float(np.max(np.abs(first - second))),
              'repeat_vlad_max_abs': float(np.max(np.abs(descriptor - repeat))),
              'numpy_torch_vlad_max_abs': float(np.max(np.abs(descriptor - reference)))}
    passed = all(checks[k] for k in ('vlads_dim_49152', 'unit_norm', 'finite')) and all(checks[k] <= 1e-5 for k in ('repeat_patch_max_abs', 'repeat_vlad_max_abs', 'numpy_torch_vlad_max_abs'))
    result = {'passed': passed, 'checks': checks, 'elapsed_seconds': time.time()-begin,
              'request_id': config['request_id'], 'view_id': row['view_id'],
              'image_path': str(image_path), 'image_sha256': file_sha(image_path),
              'weights_sha256': file_sha(paths['dinov2_g14_weights']),
              'centers_sha256': file_sha(paths['vlad_centers']),
              'torch': torch.__version__, 'cuda': torch.version.cuda, 'numpy': np.__version__,
              'dinov2_source_commit': source_commit,
              'device': a.device, 'tf32': False, 'forward_dtype': 'float32',
              'peak_cuda_allocated_bytes': torch.cuda.max_memory_allocated() if str(a.device).startswith('cuda') else None}
    extractor.close()
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--task-dir', type=Path, required=True)
    p.add_argument('--paths', type=Path, required=True)
    p.add_argument('--device', default='cuda')
    p.add_argument('--report', type=Path, required=True)
    run(p.parse_args())
