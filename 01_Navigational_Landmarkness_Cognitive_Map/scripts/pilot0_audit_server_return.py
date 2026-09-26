"""Read-only NAS audit of returned Pilot 0 scores, with local evidence outputs."""
import argparse
import base64
import csv
import hashlib
import io
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


class CardParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'img':
            self.images.append(attrs.get('src', ''))

    def handle_data(self, data):
        if data.strip():
            self.text.append(data.strip())


def run(a):
    out = a.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    src = out / 'source'
    results = src / 'baseline_g14_v2'
    metadata = src / 'features'
    checks = []
    evidence = {}

    def check(name, ok, detail=None):
        checks.append({'name': name, 'passed': bool(ok), 'detail': detail})
        if not ok:
            raise ValueError(name + ': ' + str(detail))

    def snapshot(path, name):
        raw = path.read_bytes()
        target = src / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_bytes() != raw:
            raise ValueError('Snapshot would overwrite different data: ' + str(target))
        target.write_bytes(raw)
        evidence[str(path)] = {'sha256': sha(raw), 'bytes': len(raw), 'local': str(target)}
        return target

    def nas_path(linux):
        prefix = '/home/nas/wangyq/'
        if not linux.startswith(prefix) or '..' in PurePosixPath(linux).parts:
            raise ValueError('Unmapped NAS path: ' + linux)
        return a.nas_root / linux[len(prefix):]

    task = read_json(a.task / 'task_manifest.json')
    cfg = read_json(metadata / 'run_config.json')
    request = read_json(a.task / 'configs/baseline_request_v2.json')
    for name, expected in task['hashes'].items():
        check('frozen:' + name, sha((a.task / name).read_bytes()) == expected)
    check('feature_task_manifest', cfg['task_manifest_sha256'] == sha((a.task / 'task_manifest.json').read_bytes()))
    check('feature_request', cfg['request'] == request and cfg['request_config_sha256'] == sha((a.task / 'configs/baseline_request_v2.json').read_bytes()))
    check('feature_index_hash', cfg['feature_index_sha256'] == sha((metadata / 'feature_index.csv').read_bytes()))
    check('extractor_contract', cfg['dinov2_commit'] == request['model']['source_revision_checked'] and not cfg['tf32'] and cfg['image_count'] == 212)
    for name in ('result_manifest.json', 'supplementary_manifest.json'):
        manifest = read_json(results / name)
        for rel, expected in manifest['files_sha256'].items():
            check('result:' + rel, sha((results / rel).read_bytes()) == expected)
    manifest = read_json(results / 'result_manifest.json')
    check('result_links_to_features', manifest['feature_config_sha256'] == sha((metadata / 'run_config.json').read_bytes()))
    check('result_links_to_task', manifest['task_manifest_sha256'] == cfg['task_manifest_sha256'])

    queries = read_csv(a.task / 'data/queries.csv')
    refs = read_csv(a.task / 'data/references.csv')
    pairs = read_csv(a.task / 'data/retrieval_pairs.csv')
    qmap = {r['view_id']: r for r in queries}
    rmap = {r['view_id']: r for r in refs}
    active = dict(qmap, **rmap)
    check('query_reference_pano_disjoint', not ({r['pano_id'] for r in queries} & {r['pano_id'] for r in refs}))
    check('query_reference_image_hash_disjoint', not ({r['image_sha256'] for r in queries} & {r['image_sha256'] for r in refs}))
    index = read_csv(metadata / 'feature_index.csv')
    check('feature_ids_exact', len(index) == 212 and {r['view_id'] for r in index} == set(active))
    vectors = {}
    max_norm_error = 0.0
    for row in index:
        raw = nas_path(row['vlad_path']).read_bytes()
        vector = np.load(io.BytesIO(raw), allow_pickle=False)
        check('vlad:' + row['view_id'], sha(raw) == row['vlad_sha256'] and vector.shape == (49152,) and vector.dtype == np.float32 and np.isfinite(vector).all())
        max_norm_error = max(max_norm_error, abs(float(np.linalg.norm(vector)) - 1))
        vectors[row['view_id']] = vector
        expected = active[row['view_id']]
        check('image_identity:' + row['view_id'], row['image_relative_path'] == expected['image_relative_path'] and row['image_sha256'] == expected['image_sha256'] and row['pano_id'] == expected['pano_id'] and row['role'] == ('query' if row['view_id'] in qmap else 'reference'))
    check('vlad_unit_norms', max_norm_error <= 1e-5, max_norm_error)
    print('Verified all 212 VLAD hashes, shapes, IDs and norms.', flush=True)

    qids, rids = list(qmap), list(rmap)
    qi, ri = {q: i for i, q in enumerate(qids)}, {r: i for i, r in enumerate(rids)}
    # Accumulate independently in float64, rather than invoke the production scorer.
    matrix = np.stack([vectors[q] for q in qids]).astype(np.float64) @ np.stack([vectors[r] for r in rids]).astype(np.float64).T
    scores = read_csv(results / 'pair_scores.csv')
    frozen = {(p['query_view_id'], p['reference_view_id']): p for p in pairs}
    observed = {(p['query_view_id'], p['reference_view_id']): p for p in scores}
    check('pair_ids_exact', len(observed) == len(scores) == 7392 and set(observed) == set(frozen))
    check('pair_counts', Counter(p['relation'] for p in scores) == {'positive': 82, 'negative': 6160, 'ignore': 1150})
    max_score_error = 0.0
    for key, row in observed.items():
        check('pair_label:' + row['query_view_id'] + ':' + row['reference_view_id'], row['relation'] == frozen[key]['relation'] and row['scoring_allowed'] == str(row['relation'] != 'ignore'))
        max_score_error = max(max_score_error, abs(float(row['cosine_similarity']) - matrix[qi[key[0]], ri[key[1]]]))
    check('all_cosine_scores_float64', max_score_error <= 1e-5, max_score_error)
    full_rankings = {r['query_view_id']: r for r in map(json.loads, (results / 'retrieval_rankings.jsonl').read_text().splitlines())}
    per_query = {r['query_view_id']: r for r in read_csv(results / 'baseline_per_query.csv')}
    sensitivity = {r['query_view_id']: r for r in read_csv(results / 'boundary_sensitivity_per_query.csv')}
    check('query_result_ids', set(per_query) == set(sensitivity) == set(full_rankings) == set(qids))
    recomputed = {}
    sensitivity_details = []
    for mode, delivered in [('main', per_query), ('sensitivity', sensitivity)]:
        rows = []
        for q in qids:
            labels = {r: frozen[q, r]['relation'] for r in rids}
            if mode == 'sensitivity':
                labels.update({r: 'ignore' for r in rids if frozen[q, r]['review_case_id'] in {'R123', 'R125'}})
            ranked = sorted((r for r in rids if labels[r] != 'ignore'), key=lambda r: (-float(observed[q, r]['cosine_similarity']), r))
            pos = [r for r in ranked if labels[r] == 'positive']
            neg = [r for r in ranked if labels[r] == 'negative']
            rank = ranked.index(pos[0]) + 1
            ranked64 = sorted(ranked, key=lambda r: (-matrix[qi[q], ri[r]], r))
            check(mode + ':float64_top1_rank:' + q, ranked64[0] == ranked[0] and next(i for i, r in enumerate(ranked64, 1) if labels[r] == 'positive') == rank)
            margin = float(observed[q, pos[0]]['cosine_similarity']) - float(observed[q, neg[0]]['cosine_similarity'])
            expected = delivered[q]
            check(mode + ':ranks:' + q, rank == int(expected['best_positive_rank']) and ranked[0] == expected['top1_reference_id'] and pos[0] == expected['best_positive_id'] and neg[0] == expected['best_negative_id'])
            check(mode + ':counts:' + q, len(pos) == int(expected['positive_count']) and len(neg) == int(expected['negative_count']) and 168 - len(ranked) == int(expected['ignore_count']))
            check(mode + ':margin:' + q, abs(margin - float(expected['margin'])) < 2e-9)
            for k in (1, 5, 10):
                check(mode + ':recall' + str(k) + ':' + q, int(rank <= k) == int(expected[f'recall_at_{k}']))
            if mode == 'main':
                rr = full_rankings[q]
                check('ranked_gallery:' + q, [x['reference_view_id'] for x in rr['ranked_scoring_gallery']] == ranked and {x['reference_view_id'] for x in rr['ignored_diagnostic']} == {r for r in rids if labels[r] == 'ignore'})
                for k, item in enumerate(rr['ranked_scoring_gallery'], 1):
                    check('ranking_detail:' + q + ':' + str(k), item['rank'] == k and item['relation'] == labels[item['reference_view_id']] and abs(item['score'] - float(observed[q, item['reference_view_id']]['cosine_similarity'])) <= 1e-9)
            rows.append({'query_view_id': q, 'rank': rank, 'margin': float(expected['margin']), 'positive_count': len(pos), 'negative_count': len(neg)})
        summary = read_json(results / ('baseline_summary.json' if mode == 'main' else 'boundary_sensitivity_summary.json'))
        counts = {f'recall_at_{k}': sum(r['rank'] <= k for r in rows) for k in (1, 5, 10)}
        check(mode + ':summary', summary['n_valid'] == 44 and counts == summary['success_count'] and abs(float(np.median([r['margin'] for r in rows])) - summary['margin']['median']) < 1e-12)
        recomputed[mode] = {'counts': counts, 'median_margin': summary['margin']['median'], 'rows': rows}
    for key, row in frozen.items():
        if row['review_case_id'] in {'R123', 'R125'}:
            sensitivity_details.append({'case_id': row['review_case_id'], 'query': key[0], 'removed_positive': key[1], 'removed_positive_score': observed[key]['cosine_similarity'], 'retained_best_positive': sensitivity[key[0]]['best_positive_id'], 'retained_best_positive_score': sensitivity[key[0]]['best_positive_score']})
    hard = read_csv(results / 'hard_negative_review.csv')
    expected_hard = {(q, item['reference_view_id']) for q, rr in full_rankings.items() for item in [x for x in rr['ranked_scoring_gallery'] if x['relation'] == 'negative'][:5]}
    check('hard_negative_top5', len(hard) == 220 and {(r['query_view_id'], r['reference_view_id']) for r in hard} == expected_hard)

    provenance = a.nas_root / 'GSV_Paris/0-All_GSV_3059_4per_448_448/_provenance'
    cache = {name: snapshot(provenance / name, 'cache/' + name) for name in ('resize_summary.json', 'resize_config.json', 'resize_manifest.csv')}
    cache_rows = read_csv(cache['resize_manifest.csv'])
    cache_map = {r['view_id']: r for r in cache_rows}
    full_views = read_csv(a.task / 'data/view_manifest.csv')
    resize_summary, resize_config = read_json(cache['resize_summary.json']), read_json(cache['resize_config.json'])
    check('cache_manifest', len(cache_rows) == len(cache_map) == 12236 and set(cache_map) == {r['view_id'] for r in full_views} and sha(cache['resize_manifest.csv'].read_bytes()) == resize_summary['manifest_sha256'])
    check('cache_config', resize_summary['passed'] and resize_config['manifest_sha256'] == task['hashes']['data/view_manifest.csv'] and resize_config['contract'] == 'pillow_rgb_bicubic_640_to_448_png_v2' and resize_config['pillow_version'] == '12.3.0')
    for r in full_views:
        cached = cache_map[r['view_id']]
        check('cache_heading:' + r['view_id'], cached['image_relative_path'] == r['image_relative_path'] and abs(float(cached['absolute_heading']) - (float(r['heading_from_api']) + 90 * int(r['view_index'])) % 360) < 1e-6)
    for r in index:
        cached = cache_map[r['view_id']]
        check('active_cache_hash:' + r['view_id'], cached['output_sha256'] == r['image_448_sha256'] and cached['source_sha256'] == r['image_sha256'])
    for key, linux in [('g14', request['model']['weights_path']), ('vlad', request['vlad']['centers_path'])]:
        p = snapshot(Path(str(nas_path(linux)) + '.provenance.json'), key + '.provenance.json')
        check(key + '_provenance_hash', read_json(p)['sha256'] == cfg['weights_sha256' if key == 'g14' else 'centers_sha256'])
    centers_raw = nas_path(request['vlad']['centers_path']).read_bytes()
    check('actual_vlad_centers_hash', sha(centers_raw) == cfg['centers_sha256'] == 'a684e571f05c85c804e7301547d8620c28ae759e824adb9ac88294b080feaba0')

    chosen = sorted(per_query, key=lambda q: float(per_query[q]['margin']))[:4] + [max(per_query, key=lambda q: float(per_query[q]['margin'])), rids[0]]
    samples = []
    for q in chosen:
        row = next(r for r in index if r['view_id'] == q)
        raw = nas_path(row['patch_feature_path']).read_bytes()
        patch = np.load(io.BytesIO(raw), allow_pickle=False)
        check('sample_patch:' + q, sha(raw) == row['patch_feature_sha256'] and patch.shape == (1024, 1536) and patch.dtype == np.float32 and np.isfinite(patch).all() and np.max(np.abs(np.linalg.norm(patch, axis=1) - 1)) < 1e-5)
        png = a.nas_root / 'GSV_Paris/0-All_GSV_3059_4per_448_448' / row['image_448_relative_path']
        raw_png = png.read_bytes()
        im = Image.open(io.BytesIO(raw_png))
        check('sample_png:' + q, sha(raw_png) == row['image_448_sha256'] and im.size == (448, 448) and im.mode == 'RGB' and im.format == 'PNG')
        samples.append(q)
    print('Independent score, ranking, sensitivity, cache-manifest and six patch/PNG checks passed.', flush=True)

    cards = []
    card_images_verified = 0
    feature_rows = {r['view_id']: r for r in index}
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 17)
    previews = out / 'case_previews'
    previews.mkdir(exist_ok=True)
    for row in read_csv(results / 'case_index.csv'):
        name = PurePosixPath(row['card_path']).name
        parser = CardParser()
        parser.feed((results / 'failure_cases' / name).read_text(encoding='utf-8'))
        images = []
        q = row['query_view_id']
        expected_ids = [q, per_query[q]['best_positive_id']] + [r['reference_view_id'] for r in hard if r['query_view_id'] == q]
        check('card_image_count:' + name, len(parser.images) == len(expected_ids) == 7)
        for source, view_id in zip(parser.images, expected_ids):
            if source.startswith('data:image/') and ';base64,' in source:
                image_bytes = base64.b64decode(source.split(',', 1)[1])
                check('card_image_binding:' + name + ':' + view_id, sha(image_bytes) == feature_rows[view_id]['image_448_sha256'])
                images.append(Image.open(io.BytesIO(image_bytes)).convert('RGB'))
                card_images_verified += 1
            else:
                raise ValueError('Expected self-contained image: ' + name)
        # Preview the supplied card images without executing its HTML.
        width, tile, header = 3 * 448, 448 + 26, 60
        canvas = Image.new('RGB', (width, header + ((len(images) + 2) // 3) * tile), 'white')
        draw = ImageDraw.Draw(canvas)
        draw.text((10, 8), name + ' | ' + row['query_view_id'], fill='black', font=font)
        draw.text((10, 32), 'margin=' + row['margin'] + ' | original HTML image order; labels in card_text.json', fill='black', font=font)
        for i, im in enumerate(images):
            x, y = (i % 3) * 448, header + (i // 3) * tile
            draw.text((x + 4, y), 'Image ' + str(i + 1), fill='black', font=font)
            canvas.paste(im.resize((448, 448)), (x, y + 26))
        canvas.save(previews / (Path(name).stem + '.jpg'), quality=92)
        cards.append({'case': name, 'query': row['query_view_id'], 'images': len(images), 'text': parser.text})
    (out / 'card_text.json').write_text(json.dumps(cards, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    road_summary = {}
    for group in read_csv(a.task / 'data/development_groups.csv'):
        selected = [v for q, v in per_query.items() if qmap[q]['dev_group_id'] == group['dev_group_id']]
        road_summary[group['dev_group_id']] = {'road': group['road_name'], 'n': len(selected), 'recall_at_1_count': sum(int(r['recall_at_1']) for r in selected), 'median_margin': float(np.median([float(r['margin']) for r in selected]))}
    subareas = {}
    for name, groups in [('A1_D01_D02', {'D01', 'D02'}), ('A2_D03_D04', {'D03', 'D04'}), ('A3_D05_D06', {'D05', 'D06'})]:
        selected = [r for r in per_query.values() if r['road_group'] in groups]
        subareas[name] = {'road_groups': sorted(groups), 'n': len(selected), 'recall_at_1_count': sum(int(r['recall_at_1']) for r in selected), 'median_margin': float(np.median([float(r['margin']) for r in selected]))}
    low = read_csv(results / 'failure_and_low_margin_queries.csv')
    check('low_margin_selection', {r['query_view_id'] for r in low} == {q for q, r in per_query.items() if float(r['margin']) <= manifest['low_margin_threshold'] or int(r['recall_at_1']) == 0})
    hard_counts = Counter(r['reference_view_id'] for r in hard)
    report = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'status': 'NUMERICAL_AUDIT_PASS_WITH_DOCUMENTATION_GAPS', 'script_sha256': sha(Path(__file__).read_bytes()), 'command': sys.argv,
              'checks_count': len(checks), 'checks_failed': sum(not r['passed'] for r in checks), 'max_float64_score_error': max_score_error, 'max_vlad_norm_error': max_norm_error,
              'main': recomputed['main'], 'sensitivity': recomputed['sensitivity'], 'sensitivity_details': sensitivity_details,
              'road_summary': road_summary, 'derived_subarea_summary': subareas, 'subarea_mapping_basis': 'pilot0_tasks.py choose_windows/build: consecutive pairs of nearby roads; reporting overlay only, frozen area_id unchanged', 'card_images_hash_verified': card_images_verified,
              'failures': [r for r in per_query.values() if int(r['recall_at_1']) == 0], 'six_patch_png_samples': samples,
              'negative_distance_range_m': [min(float(r['distance_m']) for r in pairs if r['relation'] == 'negative'), max(float(r['distance_m']) for r in pairs if r['relation'] == 'negative')],
              'hard_negative_repeated_references': hard_counts.most_common(10), 'raw_area_counts': dict(Counter(r['area_id'] for r in queries)),
              'limitations': ['Server-only /home/wangyq task logs, preflight, CUDA smoke and final audit reports are not mirrored in this NAS results directory.', 'All 212 VLAD files verified locally; six of 212 patch files sampled. The reported 424-file full audit remains server-reported.', 'Full 12236-row PNG provenance checked, with six actual PNG files sampled; full image cache was not rescanned.', 'No local DINO forward run or 4.55GB G/14 byte rehash; G/14 provenance sidecar was inspected.', 'area_id has one value paris_arc; claimed three-subarea summaries are absent.'], 'evidence': evidence}
    for p in sorted(src.rglob('*')):
        if p.is_file():
            report['evidence'].setdefault(str(p), {'sha256': sha(p.read_bytes()), 'bytes': p.stat().st_size})
    (out / 'audit_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('status', 'checks_count', 'checks_failed', 'max_float64_score_error', 'road_summary', 'failures', 'sensitivity_details')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--nas-root', type=Path, required=True)
    p.add_argument('--task', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    run(p.parse_args())
