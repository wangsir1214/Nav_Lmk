"""Deterministic bbox conversion, matched controls, and query-only masks.

This module does not choose candidate cues or alter the frozen P/N/I task.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

IMAGE_SIZE = 640
MAX_CANDIDATE_AREA = 0.20  # fail QC; do not quietly shrink a proposed box
MIN_SIDE = 8
FILL_RGB = (127, 127, 127)
GRID_STEP = 8
VERTICAL_CENTER_TOLERANCE = 128  # 20% of image height
HORIZONTAL_CENTER_TOLERANCE = 256  # 40% of image width


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qwen_1000_to_pixels(raw: list[int | float]) -> tuple[int, int, int, int]:
    if len(raw) != 4 or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in raw):
        raise ValueError('Expected four finite numeric bbox coordinates')
    x0, y0, x1, y1 = raw
    if not (0 <= x0 < x1 <= 1000 and 0 <= y0 < y1 <= 1000):
        raise ValueError('bbox_xyxy_1000 out of bounds or inverted')
    box = (math.floor(x0 * IMAGE_SIZE / 1000), math.floor(y0 * IMAGE_SIZE / 1000),
           math.ceil(x1 * IMAGE_SIZE / 1000), math.ceil(y1 * IMAGE_SIZE / 1000))
    validate_box(box)
    return box


def validate_box(box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    if not (0 <= x0 < x1 <= IMAGE_SIZE and 0 <= y0 < y1 <= IMAGE_SIZE):
        raise ValueError('Pixel box invalid')
    if x1 - x0 < MIN_SIDE or y1 - y0 < MIN_SIDE:
        raise ValueError('Candidate too small for the fixed protocol')
    if (x1 - x0) * (y1 - y0) > MAX_CANDIDATE_AREA * IMAGE_SIZE ** 2:
        raise ValueError('Candidate too large for the fixed protocol')


def overlap(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def matched_controls(candidate: tuple[int, int, int, int], query_id: str) -> list[tuple[int, int, int, int]]:
    """Same pixel width/height; y center within 20%; disjoint boxes.

    Geometry only. If three boxes do not fit, fail this case rather than
    broadening tolerances or manually picking an easy background region.
    """
    validate_box(candidate)
    w, h = candidate[2] - candidate[0], candidate[3] - candidate[1]
    cy = (candidate[1] + candidate[3]) / 2
    cx = (candidate[0] + candidate[2]) / 2
    xs = sorted(set(range(0, IMAGE_SIZE - w + 1, GRID_STEP)) | {IMAGE_SIZE - w})
    ys = sorted(set(range(0, IMAGE_SIZE - h + 1, GRID_STEP)) | {IMAGE_SIZE - h})
    options = []
    for y in ys:
        if abs(y + h / 2 - cy) > VERTICAL_CENTER_TOLERANCE:
            continue
        for x in xs:
            box = (x, y, x + w, y + h)
            if abs(x + w / 2 - cx) > HORIZONTAL_CENTER_TOLERANCE:
                continue
            if overlap(box, candidate):
                continue
            # The hash only resolves equally positioned deterministic ties.
            tie = hashlib.sha256(f'{query_id}|{box}'.encode()).hexdigest()
            options.append((abs(y + h / 2 - cy), abs(x + w / 2 - cx), tie, box))
    options.sort()
    controls: list[tuple[int, int, int, int]] = []
    for _, _, _, box in options:
        if all(not overlap(box, previous) for previous in controls):
            controls.append(box)
            if len(controls) == 3:
                return controls
    raise ValueError('CONTROL_GEOMETRY_FAIL: three matched disjoint boxes unavailable')


def validate_control(box: tuple[int, int, int, int], candidate: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    if not (0 <= x0 < x1 <= IMAGE_SIZE and 0 <= y0 < y1 <= IMAGE_SIZE):
        raise ValueError('Control box out of bounds')
    if (x1-x0, y1-y0) != (candidate[2]-candidate[0], candidate[3]-candidate[1]):
        raise ValueError('Control dimensions differ from candidate')
    if overlap(box, candidate):
        raise ValueError('Control overlaps candidate')


def render_masks(image_path: Path, boxes: dict[str, tuple[int, int, int, int]], output_dir: Path) -> dict:
    from PIL import Image, __version__ as pillow_version
    with Image.open(image_path) as original:
        if original.size != (IMAGE_SIZE, IMAGE_SIZE):
            raise ValueError('Expected audited 640x640 query view')
        if original.getexif().get(274, 1) != 1:
            raise ValueError('Unexpected EXIF orientation')
        original = original.convert('RGB')
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError('Use a fresh empty output directory')
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, box in boxes.items():
        if name == 'candidate':
            validate_box(box)
        else:
            validate_control(box, boxes['candidate'])
        masked = original.copy()
        masked.paste(FILL_RGB, box)
        path640 = output_dir / f'{name}_640.png'
        path448 = output_dir / f'{name}_448.png'
        masked.save(path640, format='PNG')
        masked.resize((448, 448), resample=Image.Resampling.BICUBIC).save(path448, format='PNG')
        rows.append({'variant': name, 'bbox_xyxy_640': box, 'masked_640_path': str(path640),
                     'masked_640_sha256': sha(path640), 'model_448_path': str(path448),
                     'model_448_sha256': sha(path448)})
    return {'source_path': str(image_path), 'source_sha256': sha(image_path),
            'fill_rgb': FILL_RGB, 'resize': 'Pillow RGB bicubic 640->448 PNG; no JPEG recompression',
            'pillow_version': pillow_version, 'variants': rows}


def render_review_overlay(image_path: Path, candidate: tuple[int, int, int, int],
                          controls: list[tuple[int, int, int, int]], output_path: Path) -> None:
    from PIL import Image, ImageDraw
    with Image.open(image_path) as source:
        if source.size != (IMAGE_SIZE, IMAGE_SIZE):
            raise ValueError('Expected 640x640 query view for overlay')
        canvas = source.convert('RGB')
    draw = ImageDraw.Draw(canvas)
    draw.rectangle(candidate, outline=(230, 25, 25), width=4)
    draw.text((max(0, candidate[0]), max(0, candidate[1]-14)), 'CANDIDATE', fill=(230, 25, 25))
    for idx, control in enumerate(controls, 1):
        draw.rectangle(control, outline=(20, 110, 240), width=3)
        draw.text((max(0, control[0]), max(0, control[1]-14)), f'CONTROL{idx}', fill=(20, 110, 240))
    for px, label in ((0, '0'), (320, '500'), (625, '1000')):
        draw.text((px, 0), label, fill=(255, 255, 0))
        draw.text((0, px), label, fill=(255, 255, 0))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        raise FileExistsError(output_path)
    canvas.save(output_path, format='PNG')


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--query-id', required=True)
    p.add_argument('--bbox-1000', type=str, required=True, help='JSON array [x0,y0,x1,y1]')
    p.add_argument('--source-jpeg', type=Path)
    p.add_argument('--expected-source-sha256', type=str)
    p.add_argument('--output-dir', type=Path)
    p.add_argument('--overlay-path', type=Path)
    a = p.parse_args()
    box = qwen_1000_to_pixels(json.loads(a.bbox_1000))
    controls = matched_controls(box, a.query_id)
    result = {'query_id': a.query_id, 'raw_bbox_xyxy_1000': json.loads(a.bbox_1000),
              'candidate_bbox_xyxy_640': box, 'control_bboxes_xyxy_640': controls}
    if a.overlay_path and not a.source_jpeg:
        p.error('--overlay-path requires --source-jpeg')
    if a.source_jpeg:
        if not a.expected_source_sha256 or sha(a.source_jpeg) != a.expected_source_sha256:
            raise ValueError('Source JPEG missing expected frozen SHA-256 match')
        if a.overlay_path:
            render_review_overlay(a.source_jpeg, box, controls, a.overlay_path)
            result['review_overlay_path'] = str(a.overlay_path)
    if a.output_dir and not a.source_jpeg:
        p.error('--output-dir requires --source-jpeg')
    if a.output_dir:
        result['mask_output'] = render_masks(a.source_jpeg,
            dict(candidate=box, control1=controls[0], control2=controls[1], control3=controls[2]), a.output_dir)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
