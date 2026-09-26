"""Download/check official G/14 weights and the matching urban VLAD vocabulary on the server."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import time
import urllib.request
from zipfile import ZipFile, is_zipfile

G14_URL = 'https://dl.fbaipublicfiles.com/dinov2/dinov2_vitg14/dinov2_vitg14_pretrain.pth'
VLAD_URL = 'https://iiitaphyd-my.sharepoint.com/:u:/g/personal/avneesh_mishra_research_iiit_ac_in/EW-ZqUeWWexNhbLEQvsCk2wBeucxNlhEpsfeUHHOreyLag'
VLAD_RELEASE_URL = 'https://github.com/AnyLoc/DINO/releases/download/v1/dinov2_vitg14_l31_value_c32_urban_c_centers.pt'
VLAD_RELEASE_API = 'https://api.github.com/repos/AnyLoc/DINO/releases/tags/v1'
VLAD_RELEASE_ASSET = 'dinov2_vitg14_l31_value_c32_urban_c_centers.pt'
VLAD_RELEASE_SHA256 = 'a684e571f05c85c804e7301547d8620c28ae759e824adb9ac88294b080feaba0'
VLAD_RELEASE_BYTES = 197425
VLAD_SUFFIX = 'vocabulary/dinov2_vitg14/l31_value_c32/urban/'


def file_sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def validate_g14(path):
    import torch
    obj = torch.load(path, map_location='cpu', weights_only=True, mmap=True)
    shapes = {'cls_token': (1, 1, 1536), 'patch_embed.proj.weight': (1536, 3, 14, 14),
              'blocks.31.attn.qkv.weight': (4608, 1536),
              'blocks.39.attn.qkv.weight': (4608, 1536)}
    if not isinstance(obj, dict) or 'register_tokens' in obj:
        raise ValueError('Expected standard non-register G/14 state dict')
    for key, shape in shapes.items():
        if key not in obj or tuple(obj[key].shape) != shape or not torch.isfinite(obj[key]).all():
            raise ValueError('G/14 checkpoint validation failed: ' + key)
    return {'checked_shapes': {k: list(v) for k, v in shapes.items()},
            'strict_full_model_load': 'required at server smoke test; not done in downloader'}


def validate_centers(path):
    from pilot0_vlad import load_centers
    centers = load_centers(path)
    return {'shape': list(centers.shape), 'finite': True, 'nonzero_centers': True}


def validate_release_asset(data):
    """Check pinned release bytes before deserialization; torch validation follows."""
    if len(data) != VLAD_RELEASE_BYTES:
        raise ValueError('Unexpected AnyLoc Release asset byte length')
    if hashlib.sha256(data).hexdigest() != VLAD_RELEASE_SHA256:
        raise ValueError('AnyLoc GitHub Release asset SHA-256 mismatch')
    return {'bytes': len(data), 'sha256': VLAD_RELEASE_SHA256}


def download_release_centers(dest):
    request = urllib.request.Request(VLAD_RELEASE_URL, headers={'User-Agent': 'Paris-Pilot0'})
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status != 200:
            raise ValueError('AnyLoc GitHub Release returned HTTP ' + str(response.status))
        data = response.read(VLAD_RELEASE_BYTES + 1)
    validate_release_asset(data)
    temp = dest.with_name(dest.name + f'.partial.{time.time_ns()}')
    with temp.open('xb') as f:
        f.write(data); f.flush()
    # Run the production loader on this server, not only the release parser.
    validation = validate_centers(temp)
    if dest.exists():
        temp.unlink()
        raise FileExistsError(dest)
    temp.replace(dest)
    return {'origin': 'downloaded_from_official_anyloc_github_release',
            'source_url': VLAD_RELEASE_URL, 'release_api_url': VLAD_RELEASE_API,
            'release_tag': 'v1', 'asset_name': VLAD_RELEASE_ASSET,
            'sha256_verified_against_source_record': VLAD_RELEASE_SHA256,
            'validation': validation}


def metadata(path, source, origin, validation, extra=None):
    sidecar = path.with_name(path.name + '.provenance.json')
    old = json.loads(sidecar.read_text(encoding='utf-8')) if sidecar.exists() else None
    digest = file_sha(path)
    if old and old['sha256'] != digest:
        raise ValueError('Previously recorded weight bytes changed: ' + str(path))
    result = {'path': str(path), 'sha256': digest, 'bytes': path.stat().st_size,
              'configured_official_source': source, 'origin': origin,
              'validation': validation, 'checked_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
              'script_sha256': file_sha(__file__)}
    if old:
        result['origin'] = old.get('origin', origin)
    if extra:
        result.update(extra)
    sidecar.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2), flush=True)


def download_g14(path, trust_existing=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    origin = 'preexisting_file_source_not_independently_verified'
    sidecar = path.with_name(path.name + '.provenance.json')
    if path.exists() and not sidecar.exists() and not trust_existing:
        raise ValueError('G/14 checkpoint already exists without source provenance; inspect it, then rerun with --trust-existing-artifacts if approved')
    if not path.exists():
        temp = path.with_name(path.name + '.partial')
        # A previous partial is restarted; the completed target is never overwritten.
        req = urllib.request.Request(G14_URL, headers={'User-Agent': 'Paris-Pilot0'})
        with urllib.request.urlopen(req, timeout=120) as response, temp.open('wb') as out:
            expected = response.headers.get('Content-Length')
            length = 0; last = time.monotonic()
            while True:
                chunk = response.read(8 * 1024 * 1024)
                if not chunk:
                    break
                out.write(chunk); length += len(chunk)
                if time.monotonic() - last > 10:
                    print(json.dumps({'downloading': 'G14', 'bytes': length}), flush=True); last = time.monotonic()
        if expected and length != int(expected):
            raise ValueError('G/14 download length mismatch')
        result = validate_g14(temp)
        if path.exists():
            raise FileExistsError(path)
        temp.replace(path); origin = 'downloaded_from_official_url_this_run'
    else:
        result = validate_g14(path)
    metadata(path, G14_URL, origin, result)


def download_centers(root, supplied_zip=None, trust_existing=False, source='release'):
    dest = root / 'dinov2_vitg14/l31_value_c32/urban/c_centers.pt'
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not supplied_zip and source == 'release':
        if dest.exists():
            validate_release_asset(dest.read_bytes())
            validation = validate_centers(dest)
            release = {'origin': 'preexisting_file_bytes_match_verified_official_release_asset',
                       'validation': validation}
        else:
            release = download_release_centers(dest)
        provenance = {'source_url': VLAD_RELEASE_URL, 'release_api_url': VLAD_RELEASE_API,
                      'release_tag': 'v1', 'release_id': 127038019, 'asset_id': 132758258,
                      'asset_name': VLAD_RELEASE_ASSET,
                      'sha256_verified_against_source_record': VLAD_RELEASE_SHA256,
                      'legacy_cache_zip_byte_equivalence': 'not_verified; old URLs return 404'}
        metadata(dest, VLAD_RELEASE_URL, release['origin'], release['validation'], provenance)
        return
    origin = 'preexisting_file_source_not_independently_verified'
    extra = {}
    sidecar = dest.with_name(dest.name + '.provenance.json')
    if dest.exists() and not sidecar.exists() and not trust_existing:
        raise ValueError('VLAD centers already exist without source provenance; inspect them, then rerun with --trust-existing-artifacts if approved')
    if not dest.exists():
        archive = supplied_zip or root / 'downloads/anyloc_official_cache.zip'
        archive_preexisting = archive.exists()
        if archive_preexisting and not supplied_zip and not trust_existing:
            raise ValueError('AnyLoc cache ZIP already exists without source provenance; inspect it, then rerun with --trust-existing-artifacts')
        if not archive.exists():
            if supplied_zip:
                raise FileNotFoundError(supplied_zip)
            from onedrivedownloader import download
            archive.parent.mkdir(parents=True, exist_ok=True)
            temp = archive.with_name(archive.name + f'.partial.{time.time_ns()}')
            download(VLAD_URL, filename=str(temp), unzip=False)
            if not is_zipfile(temp):
                raise ValueError('Official download did not return a ZIP (possibly expired link/login page)')
            temp.replace(archive)
        if not is_zipfile(archive):
            raise ValueError('Invalid cache ZIP; do not use an HTML error page')
        with ZipFile(archive) as z:
            names = [n for n in z.namelist() if n.endswith(VLAD_SUFFIX + 'c_centers.pt') or n.endswith(VLAD_SUFFIX + 'c_center.pt')]
            if len(names) != 1:
                raise ValueError('Expected exactly one G14/l31/value/c32/urban vocabulary: ' + repr(names))
            info = z.getinfo(names[0])
            if info.file_size > 16 * 1024 * 1024:
                raise ValueError('Unexpected vocabulary size')
            temp = dest.with_name(dest.name + '.partial')
            # Stream one known member; never extract arbitrary archive paths.
            with z.open(info) as inp, temp.open('wb') as out:
                shutil.copyfileobj(inp, out)
        result = validate_centers(temp)
        if dest.exists():
            raise FileExistsError(dest)
        temp.replace(dest)
        origin = ('user_supplied_zip_requires_source_confirmation' if supplied_zip else
                  'preexisting_zip_source_not_independently_verified' if archive_preexisting else
                  'downloaded_from_official_anyloc_public_link_this_run')
        extra = {'archive_path': str(archive), 'archive_sha256': file_sha(archive), 'member': names[0]}
    else:
        result = validate_centers(dest)
    metadata(dest, VLAD_URL, origin, result, extra)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--component', choices=['g14', 'vlad', 'all'], default='all')
    p.add_argument('--g14-path', type=Path, default=Path('/home/nas/wangyq/model_weights/dinov2/torch/hub/checkpoints/dinov2_vitg14_pretrain.pth'))
    p.add_argument('--vlad-root', type=Path, default=Path('/home/nas/wangyq/model_weights/VLAD'))
    p.add_argument('--vlad-zip', type=Path, help='Optional cache.zip obtained from the official AnyLoc public data')
    p.add_argument('--vlad-source', choices=['release', 'cache-zip'], default='release',
                   help='Use the pinned official GitHub Release asset; cache-zip selects the legacy SharePoint archive flow')
    p.add_argument('--trust-existing-artifacts', action='store_true', help='Explicitly accept a preexisting checkpoint, vocabulary file or cache ZIP after verifying its origin; shape checks alone do not prove provenance')
    a = p.parse_args()
    if a.component in ('g14', 'all'):
        download_g14(a.g14_path, a.trust_existing_artifacts)
    if a.component in ('vlad', 'all'):
        download_centers(a.vlad_root, a.vlad_zip, a.trust_existing_artifacts, a.vlad_source)
