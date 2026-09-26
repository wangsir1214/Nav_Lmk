"""Package a reviewed Pilot 0 task or verify the delivered bytes (stdlib only)."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
from zipfile import ZipFile, ZIP_DEFLATED


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def verify(task_dir=None, zip_path=None):
    archive = ZipFile(zip_path) if zip_path else None
    try:
        def read(name):
            return archive.read(name) if archive else (task_dir / name).read_bytes()
        manifest = json.loads(read('package_manifest.json'))
        if archive:
            names = archive.namelist()
            expected = set(manifest['files']) | {'package_manifest.json'}
            if len(names) != len(set(names)) or set(names) != expected:
                raise ValueError('Duplicate, missing, or unexpected ZIP entry')
            if archive.testzip() is not None:
                raise ValueError('ZIP CRC check failed')
            spec = json.loads(read('delivery_spec.json'))
            if manifest.get('delivery_id') != spec.get('delivery_id'):
                raise ValueError('Package delivery ID/spec mismatch')
            for name in spec.get('extra_files', []):
                if name not in manifest['files']:
                    raise ValueError('Required supplemental file omitted: ' + name)
            for name in spec.get('extra_scripts', []):
                if 'scripts/' + name not in manifest['files']:
                    raise ValueError('Required supplemental script omitted: ' + name)
        for name, info in manifest['files'].items():
            p = PurePosixPath(name)
            if p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name:
                raise ValueError('Unsafe package entry: ' + name)
            if p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp', '.pth', '.pt', '.npy', '.npz'}:
                raise ValueError('Large image, checkpoint, or feature file must stay off-package: ' + name)
            raw = read(name)
            if digest(raw) != info['sha256'] or len(raw) != info['bytes']:
                raise ValueError('Package hash mismatch: ' + name)
        result = {'passed': True, 'files_verified': len(manifest['files']),
                  'task_id': manifest['task_id'], 'images_included': False}
        if zip_path:
            result.update(zip_path=str(zip_path), zip_sha256=digest(zip_path.read_bytes()),
                          zip_bytes=zip_path.stat().st_size)
        return result
    finally:
        if archive:
            archive.close()


def package(task_dir, scripts_dir, output_zip):
    if output_zip.exists():
        raise FileExistsError('Use a new delivery filename; will not overwrite: ' + str(output_zip))
    task = json.loads((task_dir / 'task_manifest.json').read_text(encoding='utf-8'))
    validation = json.loads((task_dir / 'validation/frozen_task_validation.json').read_text(encoding='utf-8'))
    if not task['baseline_allowed'] or not validation['passed']:
        raise ValueError('Only validated reviewed tasks can be packaged here')
    names = set(task['hashes']) | {
        'task_manifest.json', 'configs/baseline_request.json',
        'validation/frozen_task_validation.json', 'REVIEW_ACCEPTANCE.md',
        'SERVER_BASELINE_TASK.md', 'README.md', 'REPRODUCE.md',
        'official_source_check/source_manifest.json',
    }
    script_names = ['pilot0_delivery.py', 'pilot0_verify_frozen_task.py']
    specification = task_dir / 'delivery_spec.json'
    spec = json.loads(specification.read_text(encoding='utf-8')) if specification.exists() else {}
    if spec:
        names.add('delivery_spec.json')
        for name in spec['extra_files']:
            rel = PurePosixPath(name)
            if rel.is_absolute() or '..' in rel.parts or '\\' in name or ':' in name:
                raise ValueError('Unsafe additional package path')
            names.add(name)
        for name in spec['extra_scripts']:
            if Path(name).name != name or '/' in name or '\\' in name or ':' in name:
                raise ValueError('Script entry must be a basename')
            script_names.append(name)
    payload = {name: (task_dir / name).read_bytes() for name in sorted(names)}
    for name, expected in task['hashes'].items():
        if digest(payload[name]) != expected:
            raise ValueError('Frozen input changed: ' + name)
    for name in script_names:
        payload['scripts/' + name] = (scripts_dir / name).read_bytes()
    manifest = {'task_id': task['task_id'], 'format_version': 1,
                'delivery_id': spec.get('delivery_id', 'reviewed_v1_initial'),
                'scope': 'Metadata, review evidence, instructions and validators only; no images, weights or features.',
                'files': {name: {'sha256': digest(raw), 'bytes': len(raw)}
                          for name, raw in sorted(payload.items())}}
    payload['package_manifest.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    with ZipFile(output_zip, 'x', compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name, raw in sorted(payload.items()):
            archive.writestr(name, raw)
    result = verify(zip_path=output_zip)
    (task_dir / 'delivery_validation.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    build = sub.add_parser('package')
    build.add_argument('--task-dir', type=Path, required=True)
    build.add_argument('--scripts-dir', type=Path, required=True)
    build.add_argument('--output-zip', type=Path, required=True)
    check = sub.add_parser('verify')
    source = check.add_mutually_exclusive_group(required=True)
    source.add_argument('--task-dir', type=Path)
    source.add_argument('--zip', dest='zip_path', type=Path)
    args = parser.parse_args()
    if args.command == 'package':
        result = package(args.task_dir, args.scripts_dir, args.output_zip)
    else:
        result = verify(task_dir=args.task_dir, zip_path=args.zip_path)
    print(json.dumps(result, indent=2))
