# TODO

## 2026-09-28T070320Z - 当前直接下一步

- [x] 说明当前Qwen用法，保存实际请求及路线顺序，核查main_03/main_06人工表仍为空。
- [ ] 本地复用两条路线图板，补齐来向、匿名出口、示范路线和拍摄时间问题的统一审核包；不要求用户重新查盘或算heading。
- [ ] 人工确认通行模式、路线连贯性、来向/视图解释、可选出口和沿演示路线的正确出口；保留UNSURE与修订理由。
- [ ] 按审核结果冻结明确的已学路线续行任务与新测试观察，制作路线对齐输入；交服务器运行全图路线对照，暂不SFT。
- [ ] 另行审核6图16候选；候选审核不阻塞全图路线基线，但必须先于区域遮挡和匹配控制实验完成。

## 2026-09-28 Completed smoke and next gates

- [x] Fetch and inspect exact server-results commit `253d27b047d7e421e35be56245f6d7017622c3db`, NAS scorer mapping, stage outputs, and the two decision overlays.
- [x] Confirm schema v1.3 coordinate conversion and completed stage counts; retain all earlier BLOCKED runs unchanged.
- [ ] Human-review the 16 unique proposals across six views: visible target, corrected text/type, box fit, repeated identity, stability, and route usefulness. Reject transient vehicles as stable landmarks unless a distinct task justifies them.
- [ ] Independently verify `main_03` and `main_06` route continuity, legal exits, intended action, capture-time confounds, and decision viewpoint; mark KEEP/ADAPT/REJECT before defining gold.
- [ ] Freeze an explicit P1B task (complete-route learning then replay, or online prefix continuation), a goal instruction, time-legal image sequence, route-aligned four views, and equivalent condition prompts. Only then rerun a small paired pilot and report scored behavior.
- [ ] After candidate approval, test approved cue versus size/position-matched control regions under fixed route conditions; measure paired choice changes, including null and adverse effects.

## 2026-09-27 Qwen coordinate calibration and rerun

- [x] Inspect the versioned partial server return for `paris_route_qwen_smoke_20260927T123059Z_a01` and preserve its `BLOCKED` status; do not count stage-0 `1/2` as visual success.
- [ ] Server: offline overlay audit of both decision images using untouched boxes and a separately labeled 0-1000-to-640 hypothesis; record per-candidate human-readable matching evidence and ambiguity.
- [ ] Server: revise the coordinate contract only after the diagnostic images establish the source convention. Test in-range 0-1000 coordinates as well as values over 640; never use a bounds-only rule to infer the convention or silently clip boxes.
- [ ] Server: create a fresh UTC `run_id`, rerun stage 0, then stages 1/2 only if the grounded candidate gate passes. Keep the previous run and all attempts immutable.
- [ ] Server: export a small, versioned results snapshot to a dedicated `server-results/{run_id}` GitHub branch, with source commit, code/schema revisions, hashes, stage counts, raw reply excerpts or small files, diagnostic overlays, and review status. Do not upload NAS images, weights, caches, or large dumps.
- [ ] Local: fetch that exact branch and commit for visual/semantic audit before any formal landmark or route interpretation.

## 2026-09-26 当前队列

- [x] 本地：针对完整 JSON 代码围栏发布 schema v1.2、解析 helper、回归检查和服务器交接修订；历史首例离线解析通过。
- [ ] 服务器：同步新 commit，先用历史 raw 验证实际 runner 的解析和严格 schema，再用新 UTC `run_id` 重跑阶段 0/1/2；保留旧 BLOCKED 结果。
- [x] 读取两份 0926 最新研究对话并固化研究问题、证据边界和本轮实验顺序。
- [x] 创建路线 smoke manifest、Qwen 输出 schema 和服务器低消耗执行交接。
- [x] 创建私有 GitHub 同步仓库并 push 轻量 commit（`wangsir1214/Nav_Lmk`，commit `e885037`）。
- [ ] 将 `sync/` 文件同步到服务器 `/home/wangyq/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/sync/`（可由服务器 Codex 按 `SERVER_SYNC_SETUP_20260927.md` 从 `origin/main` 拉取）。
- [ ] 若服务器工程保持非 Git 状态，记录 `temporary_clone` 或 `manual_upload` 的同步来源后继续 Qwen smoke。
- [ ] 服务器重新同步图像命名修订后，重跑 preflight 并开始 Qwen smoke 阶段 0。
- [ ] 服务器更新旧 sync 包时记录备份目录和本次来源 commit。
- [ ] 服务器安装 schema v1.2 后对 `main_03_dec`、`main_06_dec` 各执行最多一次格式重试，再决定是否进入阶段 1。
- [ ] 每次服务器重跑使用新的 UTC run_id，并核验旧结果未被覆盖。
- [x] 已将同步包全部产物路径统一为 UTC timestamp/run_id 目录；handoff 不再引用固定历史输出目录。
- [ ] 服务器只读核对 `/home/wangyq/Nav_Lmk/third_party` 的创建时间、内容和 Git 状态；在来源明确前不删除、不移动、不纳入实验。
- [x] 固化 `/home/wangyq` 与 `/home/nas/wangyq` 的存储分工和 GitHub 低 token 同步节奏。
- [ ] 服务器完成 Qwen 视觉权重核验、2 图 JSON/bbox smoke、六 case 候选提议和三条件路线 smoke。
- [ ] 人工审核 `HUMAN_REVIEW_REQUIRED.md` 中的候选框；审核前不运行正式候选遮挡结论。
- [ ] 路线 smoke 通过后，重新确认同月/时间稳定性、决策区和 gold action，再扩展正式路线样本。

## 2026-09-24 下一轮并行执行

- [ ] 服务器：核验硬件，自动下载并固定官方 Qwen2.5-VL-7B-Instruct；先做 2 图 smoke，再按失败/低/高/中 margin 分层生成 12 query view 候选、overlay 和审核表。
- [ ] 人工：按可见性、框准确、描述、重复、时间稳定性线索及导航作用假说审核候选；通过后扩至全部 44 query。
- [ ] 服务器：核验 212 个 patch 文件并重聚合抽样 full VLAD，冻结 640→448→32x32 映射、匹配控制和 query-only 干预。
- [ ] 本地/服务器：另建同道路 50–100 m / 100–200 m 候选困难负例并人审，形成独立任务版本；不修改当前冻结标签。
- [ ] 服务器：并行修复/筛选路线，先做 4 条左右路线 smoke，争取 6–9 条人工确认的左右直行路线与 route-aligned 图像，之后才能报告正式方向成绩。
- [ ] 见 `NEXT_STAGE_QWEN_ROUTE_HANDOFF_20260924.md` 中的完整交接指令与输出合同。

## 2026-09-24 当前优先级：基线数值验收通过，补齐执行证据并准备候选框审核

- [x] 回顾原有数据清单与关联，完整读取两份 HTML 实际保存的对话正文及数学表达式。
- [x] 形成 `PILOT0_EXECUTION_PLAN.md` 与 `SERVER_CODEX_HANDOFF_PILOT0.md`，区分当前任务、历史讨论、待定参数及本地／服务器分工。
- [x] 定点核验 Z 盘图像目录和道路映射路径；读取 heading CSV，确认 3059 行及唯一 panoid，并保存来源哈希。未递归扫盘或读取大图。
- [x] 本地：完成12236行逐view索引，保留坐标来源、heading、道路组、路径和两类划分。
- [x] 本地：54pano、48query/168reference、8064条P/N/I；132复核卡、22图板、离线页、空白审核表。
- [x] 本地：29项数据检查、132对图板预审及31优先项；6项审核回收测试；带哈希轻量服务器草案。
- [x] 用户：132项审核全部完成，JSON/CSV已导出并逐字段核对一致。
- [x] 本地接收审核：处理R123/R125逐对边界例外、剔除4个无P query，发布paris_local_v1_20260923；44query/168reference、82P/6160N/1150I，17项检查通过，允许开发基线。
- [x] 本地：核验官方源码、固定baseline请求、准备约1.39MB服务器包并逐项校验28文件；入口outputs/pilot0/reviewed_v1_20260923/SERVER_BASELINE_TASK.md。
- [x] 本地：升级服务器交接包v2.1，修复评分器hashlib导入、收紧提取前预检顺序；10项CPU测试、目标脚本编译、17项冻结题库检查通过。
- [x] 本地：处理AnyLoc SharePoint入口404，核验并接入AnyLoc/DINO Release v1 urban中心固定下载与SHA校验；准备v2.2交接包。
- [x] 本地：重打包最终 `server_baseline_package_v2_2_final_20260924.zip`，并完成45文件SHA-256/大小/CRC验收。
- [x] 协作：确定 GitHub remote 与服务器路径配置，按白名单提交轻量任务包与代码。
- [x] 服务器：报告完成G/14与词典核验、12236张448 PNG、CUDA smoke、212图提取和P/N/I评分；本地独立确认44×168分数、Recall/margin与80P敏感性。
- [x] 本地：核验当前NAS与证据副本、212个VLAD及全部7392相似度，复核11图卡、道路/pano及派生子片区、正例数分层；本轮未发现需修改标签的充分证据。
- [ ] 服务器：按outputs/pilot0/server_return_audit_20260924/SERVER_FOLLOWUP.md把原始preflight/smoke/环境/最终完整性/执行命令与脚本镜像至NAS，补齐报告层子片区汇总；无需重跑baseline或上传新ZIP。
- [ ] 本地/服务器下一阶段：先冻结候选输出schema、640/448/patch坐标映射和框审核规则，小样本候选试运行后再覆盖44query；匹配区域规则与干预参数尚未冻结，本轮未启动。
- [ ] 基线与任务可用后：Qwen 候选与框审计 → 匹配区域 → descriptor removal/retention → 分层 input intervention。
- [ ] 冻结协议并统计组级效应，评估 Paris 留出可行性；后续核验 Trafalgar 并安排外部复现。

以下为旧路线实验的历史任务和限制；其人审 gate 不阻止新 Pilot 0 的索引、配对和基线准备。

## 2026-09-17 Current Gate

- [x] Complete time/metric-spacing audits,30-board pixel review and protected-file validation.
- [x] Create codex_v2 review and blank four-question human form, preserving old review CSVs.
- [x] Decide provisional ADAPT; raw USABLE_WITH_FIXES / pool NEEDS_REMINING / stimuli REQUIRES_REPROCESSING.
- [ ] User/teacher complete HUMAN_MINIMAL_CONFIRMATION.csv using its guide. Stop here until confirmation.
- [ ] After authorization, jointly select capture month and physical spacing for accepted areas; do not enforce8pano at the expense of time continuity.
- [ ] Re-mine missing ordinary forward cases within existing Paris and resolve main_07 control legality. main_09 is confounded reserve, main_10 outside ordinary count, main_11 currentP1B case rejected.
- [ ] Confirm travel mode/signs/OSM consistency, especially main_07/arc_control_03; exclude return edge from multi-option gate.
- [ ] After approval, generate route-aligned views using incoming decision pose, not correct outgoing edge, then quality-check and re-evaluate GO before formal P1A/P1B.

## Phase 0 completed

- [x] Read project context, execution bundle, Notion research page/comments, graph, notebook, and screenshots.
- [x] Selectively scan the authorized Paris image, metadata, CityBench, and UrbanNav assets.
- [x] Audit graph construction, connector provenance, graph metrics, and legacy trajectory coverage.
- [x] Verify 100% graph coverage for four fixed views, ERP, heading, and DINO IDs.
- [x] Verify `center(view_i) = heading_from_api + 90*i (mod 360)` by pixel tests and a geographic Arc anchor.
- [x] Audit historical UrbanNav policy inputs, graph/reward/action flow, checkpoints, and orientation risks.
- [x] Mark old `trajectory_0..9` routes as historical rather than gold.
- [x] Mine 211 full-graph candidate routes and select 12 balanced main cases plus 3 Arc controls.
- [x] Generate route maps, sequence sheets, decision four-view boards, and preliminary contact-sheet screening.
- [x] Validate strict JSON, 120 route steps/panos, 480 image joins, 120 heading joins, and 30 review boards.
- [x] Selectively audit `Paris_check_for_Codex.zip`, identify the exact final graph hash/version chain, and separate relevant Paris assets from Manhattan/cache history.
- [x] Reproduce the point-to-road snapping rule from data and quantify the EPSG:4326 versus metric-CRS difference.
- [x] Verify Google Tile API `heading` and JavaScript API `centerHeading` semantics against official documentation.
- [x] Freeze the first task as P1A human candidate elicitation followed by P1B learned-route continuation/route-memory choice.
- [x] Expand the route review form and generate a 30-board blind-review index.

## Immediate human gate

- [x] Explain the audit result and human/Codex division of labor in `AUDIT_INTERPRETATION.md`.

- [ ] User and teacher confirm15cases in `_audit_outputs/HUMAN_MINIMAL_CONFIRMATION.csv`; old expanded scoring table is optional history, not required for this first pass.
- [ ] Confirm or reject every provisional left/right/forward maneuver and its decision-zone interpretation.
- [ ] Freeze KEEP, low-landmark control, scene-level, identity, and Arc-control strata.
- [ ] Reject or isolate construction, glare/distant-Arc, unstable storefront, and weak-intervention cases.
- [ ] Apply the frozen Go Gate: at least 8 ordinary routes, all three maneuvers represented, and required strong/low-landmark strata.

## First runnable pilot after the gate

- [ ] Generate route-aligned FOV=90-degree front/right/back/left views from ERP with full provenance.
- [ ] Reproject pano-to-road snapping in a metric CRS and recheck `s-tWQI70JSimlQwafuJYTw` and `v7BqGg7PqPES1XY99pxMLw`.
- [ ] Freeze raw/cleaned/decision-zone graph versions and document the 34 manual connections.
- [ ] Build the canonical `streetview_nodes.csv` and `road_edges.csv` using fixed-view and route-relative fields.
- [ ] Prepare a small human landmark-selection annotation set before any VLM call.
- [ ] Freeze geographic/decision-zone-disjoint splits and control strata.
- [ ] Run a simple human/retrieval/classification baseline before deciding whether RL is needed.

## Deferred

- [ ] Landmark removal, identity replacement, and location replacement images.
- [ ] VLM candidate generation or visual-dependency tests.
- [ ] UrbanNav checkpoint repair/replay and RL retraining.
- [ ] Online cognitive-map agent and cross-city expansion.

- [ ] 新增同道路近距离困难负例任务版本；不修改已冻结的 Pilot 0 开发题库。
- [ ] 先对少量 query 运行 Qwen 候选提议并人工审核 bbox、类别、可见性、重复和 640→448→32×32 映射。
- [ ] 核验并复用服务器已返回的 1024x1536 row-major patch cache，支持候选/控制区域的 descriptor removal；最终 VLAD 向量不能直接完成删除。
- [ ] 记录候选删除/保留相对于匹配控制区的 margin、排名和相似度效应，保留零效应与负效应。

## Security

- [ ] Revoke/rotate hard-coded historical service credentials.
- [ ] Replace literals with environment-variable or secret-manager configuration before running historical code.

## 2026-10-08 route-replay sanity handoff

- [x] Execute and return the frozen two-question, six-condition sanity run `paris_route_replay_sanity_20261008T080158Z_a01`.
- [ ] Wait for human analysis of the returned branch before changing the task or extending the question set.
