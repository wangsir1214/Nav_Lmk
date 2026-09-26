# Paris Pilot 0 — v2.2-final server handoff

Status: **COMPLETE**; UTC: 2026-09-23T17:39:22.959851+00:00.
Last stage: `completed`.
All preparation, CUDA smoke, 212-image extraction, 82P scoring, 80P sensitivity, case cards and final integrity checks passed.

Completed stages: nvidia_before, disk_before, pip_freeze, prepare_weights_all, preflight_before_resize, existing_full_cache_complete_and_compatible, preflight_after_resize, package_before_model, nvidia_before_model, g14_vlad_smoke, extract_212, score_baseline_and_sensitivity, feature_hash_audit_boundary_delta_and_case_cards, package_final_verify, nvidia_after.

## Full server paths

- Task: `/home/wangyq/Nav_Lmk/server_tasks/paris_local_v1_20260923_v2_2_final_20260924`
- Background status: `/home/wangyq/Nav_Lmk/server_tasks/paris_local_v1_20260923_v2_2_final_20260924/server_run/pipeline_status.json`
- Commands: `/home/wangyq/Nav_Lmk/server_tasks/paris_local_v1_20260923_v2_2_final_20260924/server_run/commands.jsonl`
- Exit codes/times: `/home/wangyq/Nav_Lmk/server_tasks/paris_local_v1_20260923_v2_2_final_20260924/server_run/command_results.jsonl`
- Logs: `/home/wangyq/Nav_Lmk/server_tasks/paris_local_v1_20260923_v2_2_final_20260924/server_run/logs`
- Environment: `/home/wangyq/Nav_Lmk/server_tasks/paris_local_v1_20260923_v2_2_final_20260924/server_run/environment_runtime.json`; `/home/wangyq/Nav_Lmk/server_tasks/paris_local_v1_20260923_v2_2_final_20260924/server_run/logs/pip_freeze.log`; `/home/wangyq/Nav_Lmk/server_tasks/paris_local_v1_20260923_v2_2_final_20260924/server_run/logs/nvidia_before.log`
- ZIP verification: `/home/wangyq/Nav_Lmk/server_tasks/paris_local_v1_20260923_v2_2_final_20260924/server_run/archive_verification.json`
- Frozen task: `/home/wangyq/Nav_Lmk/server_tasks/paris_local_v1_20260923_v2_2_final_20260924/validation/server_frozen_task_validation.json`
- Raw preflight: `/home/wangyq/Nav_Lmk/server_tasks/paris_local_v1_20260923_v2_2_final_20260924/validation/server_preflight_before_resize.json`
- 12236 PNG cache: `/home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per_448_448`
- Cache contract and hashes: `/home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per_448_448/_provenance`
- Resize log: `/home/wangyq/Nav_Lmk/server_tasks/paris_local_v1_20260923_v2_2_final_20260924/validation/resize_448_run.log`
- Post-resize preflight: `/home/wangyq/Nav_Lmk/server_tasks/paris_local_v1_20260923_v2_2_final_20260924/validation/server_preflight_after_resize.json`
- G/14: `/home/nas/wangyq/model_weights/dinov2/torch/hub/checkpoints/dinov2_vitg14_pretrain.pth`
- VLAD centers: `/home/nas/wangyq/model_weights/VLAD/dinov2_vitg14/l31_value_c32/urban/c_centers.pt`
- Provenance: `/home/wangyq/Nav_Lmk/server_tasks/paris_local_v1_20260923_v2_2_final_20260924/server_run/g14.provenance.json` and `/home/wangyq/Nav_Lmk/server_tasks/paris_local_v1_20260923_v2_2_final_20260924/server_run/vlad.provenance.json`; original sidecars next to NAS assets
- Smoke: `/home/wangyq/Nav_Lmk/server_tasks/paris_local_v1_20260923_v2_2_final_20260924/validation/g14_vlad_smoke.json`
- Features: `/home/nas/wangyq/outputs/Paris_local_v1_20260923/features_g14_l31_value_c32_urban_448png_v2` (exists=True)
- Feature index/config: `/home/nas/wangyq/outputs/Paris_local_v1_20260923/features_g14_l31_value_c32_urban_448png_v2/feature_index.csv`; `/home/nas/wangyq/outputs/Paris_local_v1_20260923/features_g14_l31_value_c32_urban_448png_v2/run_config.json`
- Results: `/home/nas/wangyq/outputs/Paris_local_v1_20260923/baseline_g14_v2` (exists=True)
- Per-query/rankings: `/home/nas/wangyq/outputs/Paris_local_v1_20260923/baseline_g14_v2/baseline_per_query.csv`; `/home/nas/wangyq/outputs/Paris_local_v1_20260923/baseline_g14_v2/retrieval_rankings.jsonl`
- All 7392 similarities: `/home/nas/wangyq/outputs/Paris_local_v1_20260923/baseline_g14_v2/pair_scores.csv`
- Top5 negatives: `/home/nas/wangyq/outputs/Paris_local_v1_20260923/baseline_g14_v2/hard_negative_review.csv`
- Failures/low margin: `/home/nas/wangyq/outputs/Paris_local_v1_20260923/baseline_g14_v2/failure_and_low_margin_queries.csv`; `/home/nas/wangyq/outputs/Paris_local_v1_20260923/baseline_g14_v2/case_index.csv`; `/home/nas/wangyq/outputs/Paris_local_v1_20260923/baseline_g14_v2/failure_cases/index.html`
- 80P sensitivity: `/home/nas/wangyq/outputs/Paris_local_v1_20260923/baseline_g14_v2/boundary_sensitivity_summary.json`; `/home/nas/wangyq/outputs/Paris_local_v1_20260923/baseline_g14_v2/boundary_sensitivity_per_query.csv`; `/home/nas/wangyq/outputs/Paris_local_v1_20260923/baseline_g14_v2/boundary_sensitivity_delta.csv`
- Final audit: `/home/wangyq/Nav_Lmk/server_tasks/paris_local_v1_20260923_v2_2_final_20260924/validation/final_result_audit.json`
- Return hashes: `/home/wangyq/Nav_Lmk/server_tasks/paris_local_v1_20260923_v2_2_final_20260924/server_run/return_artifacts.json`; `/home/wangyq/Nav_Lmk/server_tasks/paris_local_v1_20260923_v2_2_final_20260924/server_run/return_artifacts.sha256`

## Identity and provenance

- Package SHA-256: `519aec73d72a37ed8027f33064917b0f6f1a2700e1048cccd12ce8e7d33df82f`.
- G/14 expected/source-verified SHA-256: `baf8467e50af277596bbbafa06887c177ee899ab46033649c383577d7e9309d3`.
- Centers pinned SHA-256: `a684e571f05c85c804e7301547d8620c28ae759e824adb9ac88294b080feaba0`; 197425 bytes; tensor `[32,1536]`.
- Centers source: https://github.com/AnyLoc/DINO/releases/download/v1/dinov2_vitg14_l31_value_c32_urban_c_centers.pt
- Release v1, release ID 127038019, asset ID 132758258. No SharePoint request, cache-zip mode, substitute model/domain or Paris vocabulary fit in this workflow.
- DINOv2 commit `7764ea0f912e53c92e82eb78a2a1631e92725fc8`; no tracked changes; zero register tokens; block31 value; hard cosine VLAD c32 urban; fp32; TF32 false; batch1; seed42.
- Server task environment: `/home/wangyq/Nav_Lmk/.venv_pilot0_v2/bin/python`; Pillow12.3.0 RGB+BICUBIC 640→448 PNG. No second resize/crop or heading change.
- v2.1 resize continues in its original task. Full-cache reuse is gated by identical frozen manifest, request, resize script, successful original worker completion and a fresh v2.2 preflight.
- Frozen inputs and shipped package files retain their hashes. The validator-generated runtime report is saved separately; packaged report bytes are preserved.
- Physical inputs use image_relative_path; fixed view indices0..3 and absolute heading `(heading_from_api + 90*view_index)%360` are preserved.
- Large features and all results remain on this server/NAS. Nothing was submitted to GitHub.

## Metrics

- Main Recall@1: 42/44 = 95.45%.
- Main Recall@5: 43/44 = 97.73%.
- Main Recall@10: 43/44 = 97.73%.
- Main margin: {"median": 0.09940183159999999, "q25": 0.060137137800000004, "q75": 0.14557631324999998, "min": -0.0685814023, "max": 0.194750547}
- 80P sensitivity Recall@1: 42/44 = 95.45%.
- 80P sensitivity Recall@5: 43/44 = 97.73%.
- 80P sensitivity Recall@10: 43/44 = 97.73%.

44 correlated query views come from 12 panos, 6 road groups and 3 areas. Group/pano summaries are in baseline_summary.json and boundary_sensitivity_summary.json; results are descriptive development evidence, not independent pairs or proof of landmarkness.

Terminal status is written to server files without LLM polling. No chat notification transport is configured.
