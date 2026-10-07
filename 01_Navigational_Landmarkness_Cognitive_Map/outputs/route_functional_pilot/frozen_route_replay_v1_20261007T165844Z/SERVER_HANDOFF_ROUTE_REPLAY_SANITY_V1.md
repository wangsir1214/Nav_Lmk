# Server handoff: route replay sanity v1

Status: `PREPARED_NOT_RUN`
Created UTC: `2026-10-07T16:59:31.620899+00:00`

This package contains two human-accepted route-replay questions: `q_main02_decision_step3` and `q_main06_decision_step3`. It is a task sanity check, not a landmark-function result. Each route contributes one accepted decision point, so same-route action diversity is not established yet.

Run exactly three conditions per question, six independent model calls total:

1. `Full`: frozen demonstration images plus `CURRENT`.
2. `NoDemo`: `CURRENT` only.
3. `NoCurrent`: demonstration images only. Omit current image slots when the processor permits it; otherwise use one documented neutral placeholder with a separate hash.

Use the route-aligned FOV=90 image specs in `demo_manifest_v1.json` and `test_observation_manifest_v1.json`. The fixed four-view paths are for audit only. Use `prompt_route_replay_v1_full.txt`, `prompt_route_replay_v1_nodemo.txt`, and `prompt_route_replay_v1_nocurrent.txt` for the matching conditions. The prompts must not include pano IDs, step IDs, GPS, route IDs, gold actions, or old Qwen answers. Parse only `{"action":...}` with `LEFT`, `RIGHT`, `FORWARD`, or `UNSURE`.

Reuse the successful Qwen3.5-9B environment and fixed model revision. Keep `do_sample=False`, `enable_thinking=False`, and load the model once. Save a new UTC `run_id`, source package commit, model revision, actual message sequence, image SHA-256 values, prompt SHA-256, raw output, parsed action, and parse status. Do not run candidate proposal or masking in this run. Do not overwrite the historical smoke run.

Return a new `server-results/<run_id>` branch with lightweight JSONL/CSV plus a `RUN_SUMMARY.md`. The independent scorer must read `scorer_gold_v1.json`; do not copy gold into model requests.
