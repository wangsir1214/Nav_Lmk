"""Freeze an observer-stratified Phase 0 development set from the audited task.

No model inference, candidate inspection, or label change occurs here.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / 'outputs/query_coverage_audit/audit_20261010T110645Z'
TASK = ROOT / 'outputs/pilot0/reviewed_v1_20260923'
BASELINE = ROOT / 'outputs/pilot0/server_return_audit_20260924/source/baseline_g14_v2'
DEFAULT_OUTPUT = ROOT / 'outputs/pilot0/phase0_intervention_prep_20261011'
SEED = 'phase0-20261011-18correct-2diagnostic-v1'
TARGET = {'hard_correct': 5, 'easy_correct': 5}  # Remaining 8 are medium.


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def tie_key(ids: tuple[str, ...]) -> str:
    return hashlib.sha256((SEED + '|' + '|'.join(sorted(ids))).encode()).hexdigest()


def choose(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    # Three correct views per road, spanning both of its query panos.
    by_group: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_group.setdefault(row['road_group'], []).append(row)
    if len(by_group) != 6 or len({r['pano_id'] for r in rows}) != 12:
        raise ValueError('Expected the audited six roads and 12 query panos')
    states: dict[tuple[int, int], tuple[str, tuple[dict[str, str], ...]]] = {(0, 0): ('', ())}
    for group in sorted(by_group):
        panos = {r['pano_id'] for r in by_group[group]}
        if len(panos) != 2:
            raise ValueError(f'Expected two panos in {group}')
        options = []
        correct = [r for r in by_group[group] if int(r['full_positive_rank']) == 1]
        for combo in itertools.combinations(correct, 3):
            if {r['pano_id'] for r in combo} == panos:
                h = sum(r['DINO_VLAD_within_pool_difficulty'] == 'hard_correct' for r in combo)
                e = sum(r['DINO_VLAD_within_pool_difficulty'] == 'easy_correct' for r in combo)
                options.append((h, e, combo))
        if not options:
            raise ValueError(f'No full-correct three-view coverage in {group}')
        nxt: dict[tuple[int, int], tuple[str, tuple[dict[str, str], ...]]] = {}
        for (h0, e0), (_, old) in states.items():
            for h, e, combo in options:
                selected = old + combo
                ids = tuple(r['query_view_id'] for r in selected)
                key = (h0 + h, e0 + e)
                candidate = (tie_key(ids), selected)
                if key not in nxt or candidate[0] < nxt[key][0]:
                    nxt[key] = candidate
        states = nxt
    best_key = min(states, key=lambda he: (abs(he[0] - TARGET['hard_correct']) +
                                            abs(he[1] - TARGET['easy_correct']),
                                            abs(he[0] - TARGET['hard_correct']),
                                            abs(he[1] - TARGET['easy_correct']),
                                            states[he][0]))
    picked = list(states[best_key][1])
    if len(picked) != 18 or len({r['query_view_id'] for r in picked}) != 18:
        raise ValueError('Selection size or uniqueness mismatch')
    return sorted(picked, key=lambda r: (r['road_group'], r['pano_id'], int(r['view_index'])))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source = AUDIT / 'query_coverage.csv'
    rows = read_csv(source)
    summary = json.loads((AUDIT / 'audit_summary.json').read_text(encoding='utf-8'))
    if summary['status'] != 'PASS' or len(rows) != 44:
        raise ValueError('Coverage audit is not the verified 44-query result')
    selected = choose(rows)
    failures = sorted((r for r in rows if int(r['full_positive_rank']) != 1),
                      key=lambda r: r['query_view_id'])
    if len(failures) != 2:
        raise ValueError('Expected exactly two diagnostic Full failures')
    if {r['query_view_id'] for r in selected} & {r['query_view_id'] for r in failures}:
        raise ValueError('Primary/diagnostic overlap')
    manifest = {
        'package_id': 'phase0_intervention_prep_20261011_v1',
        'status': 'FROZEN_QUERY_SELECTION_PRE_INTERVENTION_NOT_EXPERIMENT_RESULT',
        'source_task_id': 'paris_local_v1_20260923',
        'observer_request_id': 'full_image_g14_l31_value_c32_urban_448png_fp32_v2',
        'selection_rule': {
            'universe': 'all 44 audited query views; preserve original P/N/I and gallery',
            'primary': '18 Full-correct views: exactly three per road, both query panos per road; minimize deviation from 5 hard + 5 easy, with 8 medium target; SHA256(SEED|sorted IDs) breaks ties',
            'diagnostic': 'both Full-failed views, excluded from Full-correct conditional estimate',
            'seed': SEED, 'target_hard': 5, 'target_easy': 5,
            'selection_uses': 'only the frozen original Full rank/margin, group/pano and view IDs; never proposal or mask outcomes',
            'expansion': 'retain remaining 24 Full-correct views in the eligible universe; decide expansion before looking at their own mask effects',
        },
        'counts': {
            'universe_views': 44, 'universe_panos': 12, 'primary_views': len(selected),
            'primary_panos': len({r['pano_id'] for r in selected}),
            'primary_roads': len({r['road_group'] for r in selected}),
            'diagnostic_views': len(failures),
            'primary_difficulty': {kind: sum(r['DINO_VLAD_within_pool_difficulty'] == kind for r in selected)
                                   for kind in ('hard_correct', 'medium_correct', 'easy_correct')},
        },
        'queries': [
            {'query_view_id': r['query_view_id'], 'pano_id': r['pano_id'],
             'view_index': int(r['view_index']), 'road_group': r['road_group'],
             'image_relative_path': r['image_relative_path'], 'image_sha256': r['image_sha256'],
             'review_image': r['review_image'], 'baseline_positive_rank': int(r['full_positive_rank']),
             'baseline_margin': float(r['full_margin']),
             'baseline_difficulty': r['DINO_VLAD_within_pool_difficulty'],
             'analysis_role': role}
            for role, bundle in (('primary_full_correct', selected), ('diagnostic_full_failure', failures))
            for r in bundle
        ],
        'source_sha256': {str(p.relative_to(ROOT)): digest(p) for p in
            (source, AUDIT / 'audit_summary.json', TASK / 'task_manifest.json',
             TASK / 'data/queries.csv', TASK / 'data/references.csv',
             TASK / 'data/retrieval_pairs.csv', TASK / 'configs/baseline_request_v2.json',
             BASELINE / 'pair_scores.csv', BASELINE / 'result_manifest.json')},
    }
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    target = output / 'selection_manifest.json'
    if target.exists():
        if json.loads(target.read_text(encoding='utf-8')) != manifest:
            raise FileExistsError('Frozen selection exists with different contents')
    else:
        target.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'path': str(target), 'counts': manifest['counts'],
                      'sha256': digest(target)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
