"""Create a resumable, provenance-tracked RGB PNG 448 cache from the frozen view index."""
import argparse
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import sys
import time

from PIL import Image, __version__ as pillow_version

CONTRACT = 'pillow_rgb_bicubic_640_to_448_png_v2'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_rows(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def check_rows(rows):
    ids, files, panos = set(), set(), {}
    for r in rows:
        idx = int(r['view_index'])
        pano = r['pano_id']
        if idx not in range(4) or any(x in pano for x in ('/', '\\', ':')):
            raise ValueError('Invalid pano/view index')
        if r['view_id'] != f'{pano}__v{idx}' or r['image_relative_path'] != f'{pano}_panorama_{idx}.jpg':
            raise ValueError('ID/physical filename mismatch: ' + r['view_id'])
        if r['view_id'] in ids or r['image_relative_path'] in files:
            raise ValueError('Duplicate ID or image filename')
        ids.add(r['view_id']); files.add(r['image_relative_path'])
        h, absolute = float(r['heading_from_api']), float(r['absolute_heading'])
        expected = (h + 90 * idx) % 360
        if not all(map(math.isfinite, (h, absolute))) or not 0 <= absolute < 360 or abs((absolute - expected + 180) % 360 - 180) > 1e-6:
            raise ValueError('Absolute heading mismatch: ' + r['view_id'])
        panos.setdefault(pano, set()).add(idx)
    if any(indices != {0, 1, 2, 3} for indices in panos.values()):
        raise ValueError('Expected complete four-view sets in full manifest')


def resize_image(raw):
    with Image.open(io.BytesIO(raw)) as im:
        if im.size != (640, 640):
            raise ValueError(f'Expected 640x640, got {im.size}')
        if im.getexif().get(274, 1) != 1:
            raise ValueError('Unexpected EXIF orientation; do not silently rotate audited views')
        return im.convert('RGB').resize((448, 448), resample=Image.Resampling.BICUBIC)


def run(args):
    source = args.source_dir.resolve()
    output = args.output_dir.resolve()
    if source == output or source in output.parents or output in source.parents:
        raise ValueError('Source and output must be separate, non-nested directories')
    rows = read_rows(args.manifest)
    check_rows(rows)
    if len(rows) != args.expected_count:
        raise ValueError(f'Expected {args.expected_count} rows, got {len(rows)}')
    # Frozen active hashes take precedence; do not silently replace originals.
    active = {}
    if args.task_dir:
        for name in ('queries.csv', 'references.csv'):
            for r in read_rows(args.task_dir / 'data' / name):
                active[r['view_id']] = r['image_sha256']
    expected_by_id = {r['view_id']: r for r in rows}
    if not set(active) <= set(expected_by_id):
        raise ValueError('Active task not contained in the resize manifest')
    for r in rows:
        if not (source / r['image_relative_path']).is_file():
            raise FileNotFoundError(source / r['image_relative_path'])
    output.mkdir(parents=True, exist_ok=True)
    meta = output / '_provenance'
    meta.mkdir(exist_ok=True)
    current = {'contract': CONTRACT, 'pillow_version': pillow_version,
               'source_dir': str(source), 'output_dir': str(output),
               'manifest_sha256': sha(args.manifest.read_bytes()),
               'expected_count': args.expected_count, 'output_format': 'PNG_RGB_8bit',
               'crop': False, 'reprojection': False, 'jpeg_recompression': False}
    cfg = meta / 'resize_config.json'
    if cfg.exists():
        if json.loads(cfg.read_text(encoding='utf-8')) != current:
            raise ValueError('Existing cache has different inputs/Pillow/config; use a new output directory')
    else:
        cfg.write_text(json.dumps(current, indent=2) + '\n', encoding='utf-8')
    journal = meta / 'resize_records.jsonl'
    prior = {}
    if journal.exists():
        raw_lines = journal.read_bytes().splitlines(keepends=True)
        # Only an unterminated last record can be a crash remnant.
        if raw_lines and not raw_lines[-1].endswith(b'\n'):
            (meta / f'partial_journal_tail_{time.time_ns()}.bin').write_bytes(raw_lines[-1])
            journal.write_bytes(b''.join(raw_lines[:-1]))
            raw_lines = raw_lines[:-1]
        for raw in raw_lines:
            record = json.loads(raw)
            if record['view_id'] in prior:
                raise ValueError('Duplicate provenance record')
            prior[record['view_id']] = record
    if not set(prior) <= set(expected_by_id):
        raise ValueError('Unexpected view in existing cache journal')
    start = time.time(); records = []; created = reused = 0
    with journal.open('a', encoding='utf-8') as log:
        for n, r in enumerate(rows, 1):
            src = source / r['image_relative_path']
            rel = Path(r['image_relative_path']).with_suffix('.png').name
            dest = output / rel
            raw = src.read_bytes(); source_hash = sha(raw)
            expected_hash = active.get(r['view_id']) or r.get('image_sha256')
            if expected_hash and source_hash != expected_hash:
                raise ValueError('Source SHA mismatch: ' + str(src))
            record = {k: r[k] for k in ('view_id', 'pano_id', 'view_index', 'heading_from_api',
                      'absolute_heading', 'image_relative_path', 'experiment_split', 'retrieval_role')}
            record.update(image_448_relative_path=rel, source_sha256=source_hash,
                          contract=CONTRACT, width=448, height=448)
            if dest.exists():
                with Image.open(dest) as cached:
                    cached.load()
                    if cached.size != (448, 448) or cached.mode != 'RGB' or cached.format != 'PNG':
                        raise ValueError('Invalid cached PNG: ' + str(dest))
                    if r['view_id'] not in prior:
                        # Recover output written just before a crash, only if pixels match.
                        if cached.tobytes() != resize_image(raw).tobytes():
                            raise ValueError('Untracked existing output differs: ' + str(dest))
                record['output_sha256'] = sha(dest.read_bytes())
                if r['view_id'] in prior and record != prior[r['view_id']]:
                    raise ValueError('Existing provenance/output changed: ' + str(dest))
                reused += 1
            else:
                if r['view_id'] in prior:
                    raise ValueError('Recorded cache file missing: ' + str(dest))
                resized = resize_image(raw)
                temp = dest.with_name(dest.name + f'.partial.{os.getpid()}')
                resized.save(temp, format='PNG', compress_level=6)
                with Image.open(temp) as decoded:
                    decoded.load()
                    if decoded.size != (448, 448) or decoded.tobytes() != resized.tobytes():
                        raise ValueError('PNG round-trip verification failed')
                if dest.exists():
                    raise FileExistsError(dest)
                temp.replace(dest)
                record['output_sha256'] = sha(dest.read_bytes())
                created += 1
            if r['view_id'] not in prior:
                log.write(json.dumps(record, ensure_ascii=False) + '\n'); log.flush(); os.fsync(log.fileno())
            records.append(record)
            if n % 250 == 0 or n == len(rows):
                print(json.dumps({'done': n, 'total': len(rows), 'created': created, 'reused': reused}), flush=True)
    manifest_dest = meta / 'resize_manifest.csv'
    with manifest_dest.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0])); writer.writeheader(); writer.writerows(records)
    summary = {'passed': True, 'contract': CONTRACT, 'count': len(records), 'created': created,
               'reused': reused, 'active_hashes_verified': len(active), 'elapsed_seconds': time.time()-start,
               'manifest_sha256': sha(manifest_dest.read_bytes()), 'python': sys.version,
               'pillow': pillow_version, 'script_sha256': sha(Path(__file__).read_bytes())}
    (meta / 'resize_summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--source-dir', type=Path, required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    p.add_argument('--task-dir', type=Path)
    p.add_argument('--expected-count', type=int, default=12236)
    a = p.parse_args()
    try:
        run(a)
    except Exception as exc:
        print(json.dumps({'passed': False, 'error': repr(exc)}, ensure_ascii=False), file=sys.stderr)
        raise
