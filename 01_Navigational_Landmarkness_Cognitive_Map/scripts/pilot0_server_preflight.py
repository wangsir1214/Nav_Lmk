"""Check Linux path mappings, fixed-view IDs/headings and active raw/derived image hashes."""
import argparse
import json
from pathlib import Path
from PIL import Image
from pilot0_resize_views import CONTRACT, check_rows, read_rows, sha


def run(task, paths_file, require_resize, report):
    paths = json.loads(paths_file.read_text(encoding='utf-8'))
    if Path(paths['task_dir']).resolve() != Path(task).resolve():
        raise ValueError('paths.server.json task_dir does not match the task package in use')
    rows = read_rows(task / 'data/view_manifest.csv')
    check_rows(rows)
    if len(rows) != 12236:
        raise ValueError('Expected 12236 fixed views')
    heading = Path(paths['paris_heading_csv'])
    expected_metadata = {r['metadata_source_sha256'] for r in rows}
    if len(expected_metadata) != 1 or sha(heading.read_bytes()) not in expected_metadata:
        raise ValueError('Server heading CSV does not match frozen metadata bytes')
    active = read_rows(task / 'data/queries.csv') + read_rows(task / 'data/references.csv')
    if len(active) != 212 or len({r['view_id'] for r in active}) != 212:
        raise ValueError('Active set must contain 212 unique views')
    resized = {}
    if require_resize:
        meta = Path(paths['paris_fixed_448']) / '_provenance'
        summary = json.loads((meta / 'resize_summary.json').read_text(encoding='utf-8'))
        index = meta / 'resize_manifest.csv'
        resized_rows = read_rows(index)
        resized = {r['view_id']: r for r in resized_rows}
        if not summary['passed'] or summary['count'] != 12236 or summary['contract'] != CONTRACT:
            raise ValueError('Incomplete or mismatched full resize run')
        if len(resized) != 12236 or len(resized_rows) != 12236 or set(resized) != {r['view_id'] for r in rows}:
            raise ValueError('Resize ID inventory mismatch')
        if sha(index.read_bytes()) != summary['manifest_sha256']:
            raise ValueError('Resize index hash mismatch')
        for r in rows:
            derived = resized[r['view_id']]
            if derived['image_relative_path'] != r['image_relative_path'] or derived['absolute_heading'] != r['absolute_heading'] or derived['contract'] != CONTRACT:
                raise ValueError('Resize changed identity/heading/contract')
    for r in active:
        source = Path(paths['paris_fixed']) / r['image_relative_path']
        if sha(source.read_bytes()) != r['image_sha256']:
            raise ValueError('Active raw image hash mismatch: ' + r['view_id'])
        if require_resize:
            record = resized[r['view_id']]
            rel = Path(r['image_relative_path']).with_suffix('.png').name
            if record['image_448_relative_path'] != rel or record['source_sha256'] != r['image_sha256']:
                raise ValueError('Derived filename/source link mismatch')
            dest = Path(paths['paris_fixed_448']) / rel
            if sha(dest.read_bytes()) != record['output_sha256']:
                raise ValueError('Active resized image hash mismatch: ' + str(dest))
            with Image.open(dest) as image:
                image.load()
                if image.size != (448, 448) or image.mode != 'RGB' or image.format != 'PNG':
                    raise ValueError('Invalid derived PNG')
    result = {'passed': True, 'full_ids_headings_checked': len(rows),
              'active_raw_hashes_checked': len(active),
              'active_resized_hashes_checked': len(active) if require_resize else 0,
              'heading_csv_sha256': next(iter(expected_metadata)), 'paths': paths}
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--task-dir', type=Path, required=True)
    p.add_argument('--paths', type=Path, required=True)
    p.add_argument('--require-resize', action='store_true')
    p.add_argument('--report', type=Path, required=True)
    a = p.parse_args(); run(a.task_dir, a.paths, a.require_resize, a.report)
