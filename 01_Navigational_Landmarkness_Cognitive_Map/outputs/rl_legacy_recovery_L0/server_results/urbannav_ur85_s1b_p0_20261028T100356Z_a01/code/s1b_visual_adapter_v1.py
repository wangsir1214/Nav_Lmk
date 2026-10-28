"""P0 visual-only boundary; no policy, environment mutation, or RNG calls.

The observation is still NumPy uint8 CHW here. The unchanged legacy batch_obs
later casts it to equal-valued float32; the legacy CNN alone divides by 255.
Actual mapping is generated for HUMAN REVIEW, not authorized for navigation.
"""
import hashlib
import json
import math
from pathlib import Path
from types import MappingProxyType

import cv2
import numpy as np
from pano_data import find_nearest_angle_index

PREFIX = 'S1B-donor-v1|20261028|'


def mapping_bytes(nodes):
    ids = sorted(nodes, key=lambda p: p.encode('utf-8'))
    if len(ids) != 550 or len(set(ids)) != 550:
        raise ValueError('Expected exactly 550 unique runtime pano IDs')
    ranked = sorted(ids, key=lambda p: (hashlib.sha256((PREFIX+p).encode('utf-8')).digest(), p.encode('utf-8')))
    # File rows follow hash rank q, explicitly indexed; UTF-8, compact JSON, LF.
    rows = [{'rank': i, 'source_pano_id': p,
             'donor_pano_id': ranked[(i+1) % len(ranked)],
             'source_sort_sha256': hashlib.sha256((PREFIX+p).encode('utf-8')).hexdigest()}
            for i, p in enumerate(ranked)]
    return ''.join(json.dumps(r, ensure_ascii=False, separators=(',', ':'))+'\n' for r in rows).encode('utf-8')


def array_hash(value):
    return hashlib.sha256(np.ascontiguousarray(value).tobytes()).hexdigest()


def check_image(image):
    if not isinstance(image, np.ndarray) or image.shape != (3, 84, 84) or image.dtype != np.uint8:
        raise ValueError('Required visual boundary: BGR CHW uint8 (3,84,84)')


class VisualAdapter:
    def __init__(self, image_root, mapping_path, expected_mapping_sha256, headings, image_hashes):
        self.image_root = Path(image_root).resolve()
        raw = Path(mapping_path).read_bytes()
        self.mapping_sha256 = hashlib.sha256(raw).hexdigest()
        if self.mapping_sha256 != expected_mapping_sha256:
            raise ValueError('Donor mapping SHA-256 mismatch')
        rows = [json.loads(line) for line in raw.splitlines()]
        ids = [r['source_pano_id'] for r in rows]
        if raw != mapping_bytes(ids):
            raise ValueError('Mapping differs from fixed algorithm/order/serialization')
        donors = [r['donor_pano_id'] for r in rows]
        if set(ids) != set(donors) or len(set(donors)) != 550 or any(p == d for p, d in zip(ids, donors)):
            raise ValueError('Donor mapping is not a derangement bijection')
        if set(headings) != set(ids) or any(not math.isfinite(float(v)) for v in headings.values()):
            raise ValueError('Missing/nonfinite/extra runtime heading')
        self.mapping = MappingProxyType(dict(zip(ids, donors)))
        self.headings = MappingProxyType({p: float(h) for p, h in headings.items()})
        self.image_hashes = MappingProxyType(dict(image_hashes))

    def select(self, source_pano, yaw):
        if source_pano not in self.mapping:
            raise ValueError('Pano outside frozen mapping; no fallback permitted')
        if isinstance(yaw, bool) or not math.isfinite(float(yaw)):
            raise ValueError('Nonfinite/invalid internal yaw')
        donor = self.mapping[source_pano]
        source_view = find_nearest_angle_index(float(yaw)-self.headings[source_pano])
        donor_view = find_nearest_angle_index(float(yaw)-self.headings[donor])
        return {'source_pano_id': source_pano, 'current_internal_yaw': float(yaw),
                'source_heading': self.headings[source_pano], 'source_view_index': source_view,
                'donor_pano_id': donor, 'donor_heading': self.headings[donor],
                'donor_view_index': donor_view, 'mapping_sha256': self.mapping_sha256}

    def replace(self, observation, *, condition, source_pano, yaw):
        if condition not in {'Full-Passthrough', 'NoImage', 'ShuffledImage'}:
            raise ValueError('Unknown visual condition')
        check_image(observation['view_image'])
        meta = self.select(source_pano, yaw)
        source_name = f"{source_pano}_{meta['source_view_index']:02d}.jpg"
        if source_name not in self.image_hashes:
            raise ValueError('Source image absent from preflight inventory')
        supplied_name = source_name
        if condition == 'Full-Passthrough':
            image = observation['view_image']  # Exact object passthrough.
        elif condition == 'NoImage':
            image = np.zeros((3, 84, 84), dtype=np.uint8)
            supplied_name = None
        else:
            supplied_name = f"{meta['donor_pano_id']}_{meta['donor_view_index']:02d}.jpg"
            path = self.image_root / supplied_name
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != self.image_hashes.get(supplied_name):
                raise ValueError('Donor image changed since P0: '+supplied_name)
            image_hwc = cv2.imread(str(path), cv2.IMREAD_COLOR)
            if image_hwc is None:
                raise ValueError('Unreadable donor JPEG: '+supplied_name)
            image = np.transpose(image_hwc, (2, 0, 1))
        check_image(image)
        result = dict(observation)
        result['view_image'] = image
        meta.update(condition=condition, source_file_name=source_name,
                    source_jpeg_sha256=self.image_hashes[source_name], supplied_file_name=supplied_name,
                    supplied_jpeg_sha256=self.image_hashes.get(supplied_name),
                    supplied_chw_sha256=array_hash(image), shape=list(image.shape),
                    dtype=str(image.dtype), channel_order='BGR', minimum=int(image.min()), maximum=int(image.max()))
        return result, meta
