# UR-85 S1-ENV Handoff

Status: `READY_FOR_SERVER_S1_ENV_SMOKE`.

Researcher decisions dated 2026-10-26 are recorded in `HUMAN_S1_APPROVAL.md` and `task_review.csv`. The only server authorization is an environment-only smoke with no PPO loading or policy rollout. The 24 episodes remain draft candidates.

Read `SERVER_S1A_HANDOFF.md` for the exact scope, paths, data provenance checks, stop conditions, and required outputs. Verify package file hashes with `S1_HANDOFF_PACKAGE_MANIFEST.json` and `validate_s1_handoff.py` before inspecting server assets.

`S1_EPISODES_DRAFT.jsonl` retains all candidate records. Coordinates derived from graph JSON `pos` are proxies until the runtime-relevant SHP fields are resolved. Do not freeze, replace, or performance-filter candidates in this stage.
