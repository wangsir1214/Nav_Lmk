# GitHub upload manifest

上传这一版轻量 route-replay package 即可，不需要上传原图或模型数据。

应上传：

- `question_manifest_v1.json`
- `demo_manifest_v1.json`
- `test_observation_manifest_v1.json`
- `prompt_route_replay_v1.txt`
- `prompt_route_replay_v1_full.txt`
- `prompt_route_replay_v1_nodemo.txt`
- `prompt_route_replay_v1_nocurrent.txt`
- `scorer_gold_v1.json`（仅供独立 scorer；禁止进入模型请求）
- `human_review_audit.json`
- `FREEZE_SUMMARY.md`
- `SERVER_HANDOFF_ROUTE_REPLAY_SANITY_V1.md`
- `SERVER_CODEX_PROMPT_ROUTE_REPLAY_SANITY_V1.txt`

不要上传：NAS 图片、ERP、模型权重、缓存、GPU 中间结果、旧 smoke 的大结果和任何包含原图的目录。

服务器端应从该目录读取 manifest 和 prompt，并记录同步时的 Git commit。正式运行结果另推送到新的 `server-results/<run_id>` 分支，不回写本目录。
