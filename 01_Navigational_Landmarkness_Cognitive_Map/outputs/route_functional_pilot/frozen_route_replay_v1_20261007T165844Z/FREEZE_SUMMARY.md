# Frozen route replay package v1

Created UTC: `2026-10-07T16:59:31.620899+00:00`
Status: `FROZEN_TWO_QUESTION_SANITY_ONLY`

The package combines accepted `main_02` (replacement for the rejected original `main_03`) and accepted `main_06`. Human review fields and gold actions are stored separately from model-facing manifests. The package is ready for a server sanity run, but it does not test candidate masking and cannot support a general landmarkness claim.

Files:

- `question_manifest_v1.json`: prompt-visible labels and task contract.
- `demo_manifest_v1.json`: ordered demonstration image loader metadata.
- `test_observation_manifest_v1.json`: current observation loader metadata.
- `scorer_gold_v1.json`: independent human-accepted gold.
- `prompt_route_replay_v1.txt`: exact model prompt.
- `human_review_audit.json`: review provenance and acceptance fields.
- `SERVER_HANDOFF_ROUTE_REPLAY_SANITY_V1.md`: six-call server instructions.
