"""Freeze reviewed Phase 0 Stage C without model inference."""
import csv
import hashlib
import json
import shutil
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from phase0_intervention_geometry import matched_controls, overlap, qwen_1000_to_pixels

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parent
PREP = PROJECT / 'outputs/pilot0/phase0_intervention_prep_20261011'
REVIEW = PROJECT / 'outputs/pilot0/stageb_technical_review_20261011'
SOURCE_COMMIT = '7c81f717cf7ca539725e0ca777bb0dc104f41f99'
SOURCE_PATH = ('01_Navigational_Landmarkness_Cognitive_Map/server_returns/'
               'paris_phase0_stagea_20261011T070533Z_a01/20261011T071447Z/proposals.jsonl')

def digest(data):
    return hashlib.sha256(data).hexdigest()

def csv_rows(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))

def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def main():
    selection_path = PREP / 'selection_manifest.json'
    review_path = REVIEW / 'MINIMAL_HUMAN_QC.csv'
    selection = json.loads(selection_path.read_text(encoding='utf-8'))
    reviews = csv_rows(review_path)
    technical = csv_rows(REVIEW / 'TECHNICAL_REVIEW.csv')
    overlap_flags = csv_rows(REVIEW / 'OTHER_PROPOSAL_OVERLAP_FLAGS.csv')
    source_bytes = subprocess.check_output(['git', 'show', f'{SOURCE_COMMIT}:{SOURCE_PATH}'], cwd=REPO)
    proposals = [json.loads(line) for line in source_bytes.splitlines() if line.strip()]
    source_hashes = json.loads((REVIEW / 'PRECHECK_SUMMARY.json').read_text(encoding='utf-8'))['source_sha256']
    assert digest(source_bytes) == source_hashes['proposals']
    assert digest(selection_path.read_bytes()) == source_hashes['selection']
    assert len(selection['queries']) == len(reviews) == len(proposals) == 20
    assert len(technical) == 40 and len(overlap_flags) == 8
    sel = {r['query_view_id']: r for r in selection['queries']}
    rev = {r['query_view_id']: r for r in reviews}
    prop = {r['query_view_id']: r for r in proposals}
    tech = {(r['query_view_id'], r['candidate_id']): r for r in technical}
    assert len(sel) == len(rev) == len(prop) == 20 and len(tech) == 40
    assert set(sel) == set(rev) == set(prop)
    assert all(r['human_accept_edit_reject'] == 'ACCEPT' for r in reviews)
    assert all(not r['human_final_bbox_640'] for r in reviews)
    executable, dispositions = [], []
    for qid in sorted(sel):
        item, human, proposal = sel[qid], rev[qid], prop[qid]
        assert proposal['status'] == 'SUCCESS' and proposal['image_sha256'] == item['image_sha256']
        assert proposal['image_size'] == [640, 640]
        assert Path(proposal['image_path']).name == item['image_relative_path']
        assert proposal['run_id'] == 'paris_phase0_stagea_20261011T070533Z_a01'
        assert len(proposal['candidates']) == 2
        checked = []
        for index, candidate in enumerate(proposal['candidates'], 1):
            cid = f'c{index}'
            assert candidate['candidate_id'] == cid
            row = tech[qid, cid]
            assert json.loads(row['bbox_xyxy_1000']) == candidate['bbox_xyxy_1000']
            status = row['geometry_status']
            try:
                box = qwen_1000_to_pixels(candidate['bbox_xyxy_1000'])
            except ValueError:
                assert status == 'AREA_LIMIT_FAIL', (qid, cid, status)
                checked.append((cid, status, None, None))
                continue
            try:
                controls = matched_controls(box, qid)
            except ValueError:
                assert status == 'CONTROL_GEOMETRY_FAIL', (qid, cid, status)
                checked.append((cid, status, box, None))
                continue
            assert status == 'PASS', (qid, cid, status)
            assert json.loads(row['candidate_bbox_xyxy_640']) == list(box)
            assert json.loads(row['control_bboxes_xyxy_640']) == [list(c) for c in controls]
            assert all(not overlap(box, c) for c in controls)
            assert all(not overlap(controls[i], controls[j]) for i in range(3) for j in range(i+1, 3))
            checked.append((cid, status, box, controls))
        usable = next((x for x in checked if x[1] == 'PASS'), None)
        statuses = {cid: status for cid, status, _, _ in checked}
        if usable is None:
            assert human['provisional_candidate_id'] == ''
            assert human['selection_basis'] == 'NO_GEOMETRY_ELIGIBLE_CANDIDATE'
            dispositions.append({'query_view_id': qid, 'analysis_role': item['analysis_role'],
                                 'stage_c_status': 'NOT_RUN_NO_GEOMETRY_ELIGIBLE_CANDIDATE',
                                 'candidate_statuses': statuses, 'human_decision': 'ACCEPT_VISUAL_ONLY'})
            continue
        cid, _, box, controls = usable
        assert human['provisional_candidate_id'] == cid
        assert human['candidate_geometry_status'] == 'PASS'
        assert json.loads(human['candidate_bbox_xyxy_640']) == list(box)
        assert human['control_geometry_qc'].strip()
        assert item['analysis_role'] == 'primary_full_correct'
        chosen = next(c for c in proposal['candidates'] if c['candidate_id'] == cid)
        flags = [f for f in overlap_flags if f['query_view_id'] == qid and f['candidate_id'] == cid]
        assert len(flags) == len({f['control_index'] for f in flags})
        executable.append({'query_view_id': qid, 'source_image_path': proposal['image_path'],
                           'source_image_sha256': item['image_sha256'], 'source_image_size': [640, 640],
                           'candidate_id': cid, 'candidate_bbox_xyxy_1000': chosen['bbox_xyxy_1000'],
                           'candidate_bbox_xyxy_640': list(box),
                           'control_bboxes_xyxy_640': [list(c) for c in controls]})
        dispositions.append({'query_view_id': qid, 'analysis_role': item['analysis_role'],
                             'stage_c_status': 'RUN', 'candidate_id': cid,
                             'candidate_statuses': statuses, 'human_decision': 'ACCEPT',
                             'human_control_qc': human['control_geometry_qc'],
                             'human_other_overlap_qc': human['other_proposal_overlap_qc'],
                             'other_candidate_control_overlap_indices': [int(f['control_index']) for f in flags]})
    assert len(executable) == 16
    assert Counter(r['analysis_role'] for r in dispositions) == {'primary_full_correct': 18, 'diagnostic_full_failure': 2}
    assert Counter(r['stage_c_status'] for r in dispositions) == {'RUN': 16, 'NOT_RUN_NO_GEOMETRY_ELIGIBLE_CANDIDATE': 4}
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out = PROJECT / 'outputs/pilot0' / f'stagec_frozen_{stamp}'
    out.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(review_path, out / 'MINIMAL_HUMAN_QC_frozen.csv')
    write_json(out / 'stagec_execution_manifest.json', {
        'status': 'FROZEN_PRE_INTERVENTION_NOT_EXPERIMENT_RESULT',
        'stage_a_run_id': 'paris_phase0_stagea_20261011T070533Z_a01',
        'stage_a_commit': SOURCE_COMMIT, 'stage_a_proposals_sha256': digest(source_bytes),
        'base_main_commit': '1acca803418ad069c8d2123486f75046b6d41487',
        'selection_sha256': digest(selection_path.read_bytes()),
        'human_qc_sha256': digest(review_path.read_bytes()),
        'geometry_script_sha256': digest((PROJECT / 'scripts/phase0_intervention_geometry.py').read_bytes()),
        'mask_contract': {'source': 'query_image_only', 'fill_rgb': [127, 127, 127],
                          'resize': 'Pillow 12.3.0 RGB bicubic 640x640 to 448x448 PNG',
                          'reference_descriptors': 'unchanged'},
        'queries': executable})
    write_json(out / 'stageb_disposition_all20.json', {
        'status': 'PRE_INTERVENTION_AUDIT',
        'review_sha256_before_user_confirmed_patch': '8c2e1dc022ae1e28bb84279093dbfaa5cb41c2cf2d4765bc2b7f755ec0757116',
        'review_sha256_after_patch': digest(review_path.read_bytes()),
        'user_confirmed_patch': 'jqMbtUb4csuPJ3XDhARbOQ__v3 human_accept_edit_reject=ACCEPT',
        'original_selection': {'primary': 18, 'diagnostic': 2},
        'stage_c': {'runnable_primary': 16, 'unrunnable_primary': 2, 'runnable_diagnostic': 0, 'unrunnable_diagnostic': 2},
        'rows': dispositions})
    print(json.dumps({'output_dir': str(out), 'runnable': len(executable), 'unrunnable': 4}, ensure_ascii=False))

if __name__ == '__main__':
    main()
