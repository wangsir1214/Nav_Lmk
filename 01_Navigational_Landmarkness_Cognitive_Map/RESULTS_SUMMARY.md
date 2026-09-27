# Results Summary

## 2026-09-28 Qwen route smoke complete, scientific status provisional

- GitHub snapshot verified on `origin/server-results/paris_route_qwen_smoke_20260927T141218Z_a01`, commit `253d27b047d7e421e35be56245f6d7017622c3db`; NAS source maps to `Z:\wangyq\outputs\paris_route_qwen_smoke_20260927T141218Z_a01`. The run completed 2/2 stage-0, 6/6 stage-1, and 6/6 stage-2 calls. These are successful executions, not accuracy denominators.
- Stage 1 yielded 16 candidate boxes on six distinct 640x640 fixed views. Raw 0-1000 coordinates were converted to image pixels. The two decision overlays support the coordinate convention but show wrong `CASA HOME` reading of `ZARA HOME`, a box below a circular sign, and other misplaced boxes. Candidate identities, boundaries, stability, and navigation utility are unreviewed.
- Stage 2 compared ordered route memory plus current four views, current four views only, and shuffled route memory plus current four views. Against the unverified geometry continuation, `main_03` is false/true/false and `main_06` is false/false/false. The summary intentionally reports `formal_navigation_accuracy: null`.
- The memory sequence includes post-decision steps 4 and 5; the task text does not define a destination or instruct replay of a learned route. The current-only condition therefore has no uniquely correct legal exit. Candidate proposals were not supplied to the choice prompt, and no masking or matched-control intervention was run. This experiment demonstrates a functioning input/output pipeline, not learned navigation, cognitive-map formation, or the causal value of a landmark.

## 2026-09-27 Qwen route smoke partial return

- Snapshot: run `paris_route_qwen_smoke_20260927T123059Z_a01`, export `20260927T124428Z`, commit `fb25faf78f93874d4601e6ade4027201694d0cf2`. The source run is `BLOCKED`: stage 0 reports 1/2 schema-valid cases; stages 1/2 report zero. No route-choice score exists.
- `main_06_dec` returned `[776,480,800,504]` for a no-entry sign on both attempts, outside the stated 640x640 contract. Its location after a hypothetical 1000-to-640 conversion is visually plausible. The accepted `main_03_dec` boxes are in numeric range but the saved overlay places them away from the described signs; the same conversion appears more plausible there.
- The present `1/2` is a parser/bounds count, not a validated visual-grounding rate. The candidate JSONL, overlays, and human-review draft must not be treated as accepted landmark evidence until coordinate calibration and visual review. Qwen self-reported `uncertainty` is not calibrated confidence.
- Next evidence gate: compare unmodified and explicitly scaled boxes on the two source images, document the coordinate convention and review outcome, then rerun under a new UTC `run_id`. Stage 1/2 results remain provisional even after a technically successful smoke; mined maneuvers are not gold actions.

## 2026-09-27 Qwen reply-format recovery

- The blocked stage-0 output is a complete Markdown JSON fence whose inner JSON parses. All three proposed candidates have the required fields and in-bounds boxes; visual accuracy still needs human review.
- Sync schema v1.2 permits only whole-reply fence removal, then the existing strict candidate/route schema checks. Invalid JSON or schema can trigger at most one same-image format retry.
- Local offline checks passed. No new Qwen inference or stage-0/1/2 result was produced in this session; the server must install the new sync commit and use a fresh UTC run ID.

## 2026-09-26 研究同步状态

- 0926 对话确认的主问题是：在给定路线经验和局部空间任务时，哪些城市视觉元素能作为地点、方向或通行结构参照并支持正确续行。
- Qwen 作为候选发现器和行为探针；DINOv2+VLAD 仅作为地点对应/表征辅助测量。现有 44-query 基线不能单独证明导航地标、认知地图或细粒度同路定位。
- 已写入 `sync/` 的服务器交接包，第一批路线为 `main_03`、`main_06`，六个候选提议 case；全部标记为 `candidate_smoke`/`provisional`。
- 本轮没有新增模型结果、没有修改冻结题库、没有写入 NAS 大文件。

## 2026-09-26 GitHub 交接状态

- 私有同步仓库已建立：`https://github.com/wangsir1214/Nav_Lmk`。
- `main`/`origin/main` 已同步到 `e885037`；同步包包含 0926 研究设计、路线 manifest、Qwen schema 和服务器交接文件。
- 服务器下一步只需拉取轻量同步包并执行其中的 prompt；Qwen 权重继续使用 `/home/nas/wangyq/model_weights/Qwen`，无需重新上传 ZIP 或图像。

## 2026-09-27 服务器同步核查

- 本地工作区和 Git 历史没有 `third_party`；该目录不由本地 Codex 通过 Z 盘创建的证据支持。
- 服务器项目当前未显示同步目录；首次同步改为显式检查 `origin`、工作区和 fast-forward 条件，避免覆盖服务器已有任务。

## 2026-09-27 路径协议

- 已固定 `/home/wangyq/Nav_Lmk` 用于代码、轻量文档和第三方源码；`/home/nas/wangyq` 用于模型权重、图像、派生缓存和大型结果。
- 后续服务器任务每次开始拉取一次 GitHub；中途不推送进度，结束时只回报成功或 BLOCKED。轻量返回摘要是否推送由任务需要决定。
- 已发现服务器项目目录可能不是 Git 工作树；同步说明已增加非 Git 安全模式，不要求把现有工程改造成 Git 仓库。
- Qwen 路线 smoke 尚未开始；preflight 已确认模型和路线 ID，当前唯一阻塞是 manifest 图像命名模式，已改为 `{panoid}_panorama_{view_index}.jpg`。
- 服务器更新同步包时应保留旧 `sync/` 备份；新版本来源提交为 `b877e46`。
- 阶段 0 尚无有效样本；原始 Qwen 回复同时存在缺失 uncertainty 和越界 bbox，不能通过默认填充或静默裁剪修复。
- 后续重跑将使用唯一 UTC run_id 目录，保留本次阻塞诊断和所有旧结果。

## 2026-09-27 产物版本化

- 已将 Qwen 路线 smoke 的输出统一为带 UTC `run_id` 的独立目录；handoff 末尾残留的固定历史输出路径已改为 `/home/nas/wangyq/outputs/{run_id}/`。
- 这只改变产物命名和归档方式，不改变冻结题库、模型、图像路径、评分口径或研究结论。

## 2026-09-26 研究同步状态

- 0926 对话确认的主问题是：在给定路线经验和局部空间任务时，哪些城市视觉元素能作为地点、方向或通行结构参照并支持正确续行。
- Qwen 作为候选发现器和行为探针；DINOv2+VLAD 仅作为地点对应/表征辅助测量。现有 44-query 基线不能单独证明导航地标、认知地图或细粒度同路定位。
- 已写入 `sync/` 的服务器交接包，第一批路线为 `main_03`、`main_06`，六个候选提议 case；全部标记为 `candidate_smoke`/`provisional`。
- 本轮没有新增模型结果、没有修改冻结题库、没有写入 NAS 大文件。

## 2026-09-24 - 后续设计状态（未产生新模型结果）

- 现有 44 query 基线继续作为候选区域贡献的冻结开发参照；同路困难负例需独立版本，目标是区分相邻路段/决策区，不设无科学根据的 5 m 精度门槛。
- 已有特征索引记录每图 `1024x1536` patch 文件及 SHA；本地原审计抽查 6 个 patch，服务器下一轮应核验全部 212 个并抽样重聚合。
- 单图 Qwen 与连续路径可并行推进，后者当前仅可做候选路线 smoke；人工确认合法出口、动作、路线连续性和 route-aligned 视图前不得当正式导航结果。详见 `NEXT_STAGE_QWEN_ROUTE_HANDOFF_20260924.md`。

## 2026-09-24 - Pilot 0 服务器基线已回传并独立确认

- 本地确认当前NAS结果与既有审计副本一致；212个VLAD字节/形状/范数及7392相似度独立float64复算通过，最大绝对差4.228659368221699e-7，44题排名不变。新增8136项检查全部通过。
- 主分析82P与80P敏感性同为Recall@1=42/44、@5=@10=43/44，服务器fp32 margin中位数0.0994018316。2个Top1失败的最佳P排名为2/11；11张图卡包括2失败和9低margin正确题。
- 主分析正例数分布为8题1P、34题2P、2题3P；单P组6/8正确、margin中位数0.014281。多P组全部正确，该事后关联与可见重叠/任务难度混杂，不改标签。
- 现题全部P同道路、全部N异道路；可作为线索贡献开发实验参照，不能外推同街道细粒度定位、跨城市泛化或已验证地标/认知地图。
- 原area_id仅paris_arc；本地另做报告层三子片区映射，未改冻结输入。原始CUDA smoke/preflight/完整性/环境日志在/home/wangyq下，需服务器镜像至NAS以补齐归档。详细见outputs/pilot0/server_return_audit_20260924/LOCAL_BASELINE_REVIEW.md。

## 2026-09-24 - 科学解释边界

- 当前结果支持“固定 DINOv2+VLAD 表示可以在本题库中稳定恢复空间对应”，并完成了可靠的开发测量层。
- 当前结果不支持“已发现导航地标”“已验证认知地图”或“已验证路线决策效用”。P 为同道路近邻对应，N 为异道路空间对照，且 N 明显更远，需新增同道路近距离困难负例。
- 下一步是 Qwen 单视图候选区域、人工框审计、匹配控制区和 query-only 区域干预；连续路径与道路选择属于后续功能性验证。
- 详见 `outputs/pilot0/SCIENCE_INTERPRETATION_20260924.md`。

## 2026-09-24 - 首次完整图基线与本地验收

- 本地独立复算通过：44题R@1=42/44(95.45%)，R@5和R@10=43/44(97.73%)，margin中位数0.0994018。80P敏感性相同，因R123/R125都不是相应query最高分正例。
- 全212个VLAD哈希/形状/范数与7392分数核验通过；float64对服务器float32最大误差4.23e-7，最佳正例排名/Top1稳定。22个回传清单文件、77张图卡图像绑定及6个patch/PNG抽样通过。
- 失败为fZ7bO6pDSX9hMw3mVdj-SA__v1(D05，第2，margin -0.007155)和vpRGwoLifY8oPQ6oU_QPHg__v3(D02，第11，-0.068581)；HutLgjnKQDJRjIfP417bDw__v3答对但margin仅0.000962。所有标签保留。
- 原area_id只有paris_arc；原始汇总缺三个子片区。按原成对选路设计另派生D01+D02、D03+D04、D05+D06汇总为15/16、16/16、11/12，未改原报告。
- 当前是Arc周边开发任务：所有P同路段、所有N不同路段；不能据高分推断同街道精确定位、城市泛化或landmarkness。下一阶段保留Recall并重点分析匹配对照下margin变化。
- 数值验收通过；完整运行资料归档仍待补齐/home/wangyq下的CUDA smoke、preflight、环境及424文件完整审计报告。详见outputs/pilot0/server_return_audit_20260924/LOCAL_BASELINE_REVIEW.md。

## 2026-09-24 - AnyLoc词典入口修订

- SharePoint词典入口在服务器实测404；固定采用AnyLoc/DINO GitHub Release v1 urban中心资产，已本地下载并核验197425 bytes和SHA-256 `a684e571f05c85c804e7301547d8620c28ae759e824adb9ac88294b080feaba0`。
- 服务器脚本现在默认自动下载和PyTorch验证该文件，要求[32,1536]、有限和非零中心；不需要用户手动下载VLAD词典。
- v2.2只修订词典获取来源，G/14、448 PNG、VLAD聚合和冻结题库合同不变。GPU smoke、全量resize、212图特征和评分仍待服务器执行。
- 最终交接包 `server_baseline_package_v2_2_final_20260924.zip` 已通过45文件SHA/大小/CRC校验：SHA-256 `519aec73d72a37ed8027f33064917b0f6f1a2700e1048cccd12ce8e7d33df82f`，大小1440349字节；不含图像、权重、词典或特征。
## 2026-09-23 - Pilot 0 服务器交接包 v2.1 验收

- 修复服务器评分脚本缺少hashlib导入的运行错误；新端到端CPU用例跑通合成小型query/reference任务、SHA校验、检索打分及manifest写出。
- 提取脚本现在先完成路径/图像预检，再创建特征缓存目录，支持安全重试。
- 当前本地验证：10/10 CPU测试通过，指定脚本可编译，冻结题库17/17检查通过。已复核路径、图片命名和绝对朝向合同。
- 这些是交付代码与冻结数据校验，不是DINO模型结果。服务器上G/14权重、VLAD中心、Pillow环境、全量448缓存、CUDA smoke和212图特征/评分都尚未执行。
- 最终v2.1轻量ZIP已构建并独立复核：45个文件通过SHA-256/大小/CRC检查，ZIP SHA-256 8bb6eebbf1227139c7dba66e1537b96e7e0714a2cce796d92e574961fdeb0014，大小1438318字节；不含图像、权重或特征。

## 2026-09-23 - 人工复核回收与 baseline 准备

- 当前有效版本paris_local_v1_20260923，状态FROZEN_DEV_READY_FOR_BASELINE；入口outputs/pilot0/reviewed_v1_20260923/REVIEW_ACCEPTANCE.md与SERVER_BASELINE_TASK.md。旧v0评分关闭状态只适用于旧草案。
- 132对人审完整、一致；确认82P（62clear/20partial）。剔除4个无P query后，44query、168reference、212图；7392关系=82P+6160N+1150I，每query140N，1–3P。17项校验通过。
- R123/R125为超出原25m候选窗口的人工确认例外，主分析82P，同时相同query/gallery执行80P敏感性。模型结果不得反向决定标签。
- 单人有提示审核；104项认可预审提示已展开；负例仅抽检（活动23人审/6137规则）。44view来自12pano、6道路、3片区，不能视为独立空间抽样；Paris留出仍未冻结。
- 本地核验了官方源码对应特征合同并准备约1.39MB交付包（28文件hash及CRC通过）；未运行模型，尚无Recall、margin或区域效应结果。服务器须检查标准G/14权重、匹配urban词典、图像哈希与实际CUDA前向。

## 2026-09-23 - Pilot 0 本地任务草案与复核材料

- 本地步骤1、2及步骤3的机器审计/材料完成；入口outputs/pilot0/local_v0_20260922/REVIEW_GUIDE.md和review/index.html。题库未人工定版，尚无模型结果。
- 3059pano×4=12236views全量索引；活动集54pano、48query/168reference、8064关系：96候选P/6720几何N/1248I；336个N为近场朝向兼容候选，实际N距离最低88.60m。
- 216所选图解码/哈希通过；29项数据校验及6项回收门槛测试通过。全部132复核对完成机器辅助图像预审，31对优先复核，主要为侧向近景/重复立面/边缘重叠。预审不是人工真值。
- 人审范围为96P全审、24N和12I规则抽检。每保留query至少1个确认P与N；否决P优先转I，不以模型成绩、固定通过率或48题保留率为目标。
- 六条开发道路全部133pano隔离，496buffer、2430潜在留出，最近距离100.0195m。留出未冻结，距离隔离不保证视觉语义不共享。
- 页面语法/资源检查通过；内置浏览器的file URL受安全策略阻止，未实测交互，另提供CSV+图卡审核方式。
- 轻量服务器草案已打包验证，无GitHub上传。正式评分关闭；服务器当前只可做环境/模型核验和特征连通性检查。

## 2026-09-22 - 新要求同步与执行拆分（无新实验）

- 已读取两份保存对话的正文与公式，形成 `PILOT0_EXECUTION_PLAN.md` 和可复制的 `SERVER_CODEX_HANDOFF_PILOT0.md`。
- 当前首个实验：逐 view 数据索引 → 空间 P/N/I 检索任务与审计 → 完整图基线 → Qwen 候选 → matched-control descriptor 干预 → 小样本输入干预 → 冻结复核。未来再研究定向、记忆与认知地图。
- 本轮新增核验仅为路径与元数据：明确指定的两处图像目录、heading CSV、pano-to-road DBF 可访问；CSV 为 3059 行、3059 唯一 panoid。未扫描大图或重新计算任何表征。
- 现有 3059×384 pano 特征不能替代新任务所需的逐 view 局部 patch descriptors；服务器需按核验后的配置提取。
- 尚无 retrieval_pairs、完整图基线、候选框或干预效应结果。距离阈值、样本量和模型版本均未正式冻结。
- 当前目录不是 Git 工作树，目标 GitHub remote 未确认；云端交互流程已设计，尚未建立连接。

## 2026-09-22 - 数据关系回顾（无新实验）

- 本次仅复核本地已保存审计，等待用户提供新组织目标；未重新扫描远端数据。
- 既有审计记录：3059 个 pano 对应 ERP、四视角、heading 元数据和 3059×384 DINOv2 特征；其中 3058 个 pano 在 3310 边的无向街景图内。
- 主键为 `pano_id/panoid`；embedding 通过 ID 列表定位行；街景节点通过 pano-to-road 映射关联 OSM 道路段；路线通过 `route_id + step_idx` 引用 pano。
- 原十条 trajectory、十五条后挖掘候选路线和 CityBench 正式任务文件是不同数据组织，不能混成同一套完整任务数据。
- 最新已记录限制仍保留：原始图不等于方向合法的行动图；候选路线含月份混合与近重复位置；尚无已验证的功能性地标标签或行为效应。未产生新的 GO/ADAPT 判定。

## 2026-09-17 - Current feasibility result

**Provisional ADAPT.** This is a completed machine-assisted feasibility decision, not an experimental result.

- Raw source: `USABLE_WITH_FIXES`; 15-route pool: `NEEDS_REMINING`; final P1A/P1B stimuli: `REQUIRES_REPROCESSING`.
- 120/120 dates present and source-consistent. All15 routes mix months; main_03 spans25 months due to one2012 point. Temporal metadata risk:11 HIGH,4 MEDIUM,0 LOW.
- EPSG:2154 capture-position audit:105 adjacent pairs,8<1m,16<2m,37<5m,1>20m. Counts overlap. A5m sequential separation proxy yields84 observations from120 steps; only main_03 has8 spatially separated points, but its dates fail.
- Direct pixel review of30 boards yields KEEP0/ADAPT14/REJECT1. Reject is scoped to main_11's current P1B decision zone: only1 non-return legal departure. Data remain useful for other tasks.
- main_10 is visibly affected by distant Arc; main_12 has piano-sign identity potential but also scaffolding/glare; main_07/arc_control_03 have unresolved road-sign versus OSM semantics.
- Priority ordinary areas main_01-08 and main_12 give a provisional4/4/1 maneuver distribution, not a passed GO gate. Nine areas worth review do not prove nine repaired sequences. main_09 is a confounded forward reserve; low controls04/07 remain candidates.
- No case establishes landmark functionality, longitudinal stability, editing feasibility or a cognitive-map effect.
- Review is now four YES/NO/UNSURE confirmations per route plus ACCEPT/REJECT/DISCUSS, in `_audit_outputs/HUMAN_MINIMAL_CONFIRMATION.csv`; old review forms remain untouched.
- Full interpretation and repair/new-data distinction: `_audit_outputs/PARIS_PILOT_USABILITY_DECISION.md`. No full Paris recollection or replacement is currently justified. Formal experiments remain stopped.

## Experiment

## Input data

## Command

## Output files

## Main results

## Interpretation

## What this means for navigational landmarkness / cognitive map

## Recommended next step

## 2026-07-29 Feasibility Audit Result

### Audit

Partial `Paris Data and Task Feasibility Audit` covering research context, execution specification, local workspace, uploaded Kepler topology, and remote-access status.

### Inputs

- Supplied ZIP, Notion page/comments, graph JSON, and screenshot.
- Authorized `Z:` roots were tested but were not mounted.

### Outputs

- `_audit_outputs/` reports, CSV/YAML/JSON artifacts, and a visually verified PNG/SVG topology figure.

### Main results

- Graph integrity is high: 3,058 unique nodes, 3,310 unique edges, full endpoint coverage, one component, no isolated nodes.
- The graph has 253 independent cycles and many potential decision zones, so the region is not merely a straight-chain topology.
- The 461 `weight=null` connector edges are structurally decisive and require provenance tracing.
- No case-level route-to-image/action/graph/embedding/RL join could be measured because the remote assets are inaccessible.

### Interpretation

Paris remains a plausible candidate, especially for graph-supported route choice or exploration, but visual diversity, route ambiguity, landmark availability, headings, action validity, and agent behavior are still unknown.

### Readiness

`Not ready for Phase 1`; Go / Adapt / Replace deferred.

### Recommended next step

Expose the three complete remote roots, finish the read-only scan and human-review boards, then choose the first task. Scan the RL root separately after its upload completes.

## 2026-07-30 Completed Paris machine audit

### Inputs

Paris graph/OSM metadata, 3,059 four-view and ERP panos, heading metadata,
DINOv2 assets, CityBench historical routes, graph notebook, and UrbanNav archive.

### Verified results

- Graph nodes have 100% four-view, ERP, heading, and DINO coverage.
- Fixed-view orientation is `center(view_i)=heading_from_api+90*i (mod 360)`.
- 12 main route candidates and three Arc controls were selected from 211 valid
  full-graph candidates.
- Main action balance is left/right/forward 4/4/4; controls are 1/1/1.
- All 120 selected panos join to 480 images and 120 headings; all 30 review boards
  exist; every route decision zone has at least two legal departures.

### Interpretation

Paris supports a small stratified route-choice/landmarkness feasibility pilot.
The data are not a reason to replace Paris now, but construction, super-landmark,
glare, stability, and low-salience confounds require adaptation and human review.

### Evidence status

- Verified: structure, joins, orientation mapping, route-mining constraints.
- Provisional: route suitability, maneuvers as gold actions, landmark functions.
- Missing: final user/teacher review, route-aligned derivative views, first-task
  freeze, and any behavioral experiment.

### Decision

`Provisional ADAPT`; not yet final GO for intervention or RL experiments.

## 2026-08-03 Archive and task-definition audit

### Audit

Selective provenance audit of `Paris_check_for_Codex.zip`, GSV projection code,
Google heading semantics, and the 15-route human-review workflow. No behavioral
experiment was run.

### Verified results

- The ZIP final graph is byte-identical to the working `kl.Line_Points_3.json`
  (`SHA-256 fd11bdf...b5edf`).
- The point snapping rule is data-level reproduced for all 3,059 intermediate
  points. Current geographic-degree snapping differs from a metric alternative by
  median 0.291 m and P95 1.498 m.
- Two selected decision panos differ by more than 1 m under metric snapping and
  require formal recheck.
- Official Google definitions establish Tile metadata `heading` as clockwise from
  north and `centerHeading` as the heading at the center of panoramic tiles.
- Historical 16 views are FOV=60 degrees at 22.5-degree center intervals; current
  four views are FOV=90 degrees at 90-degree center intervals.
- All 32 links in the human-review guide resolve, and the expanded 15-row review
  CSV has 27 consistent columns.

### Scientific interpretation

The 15 routes are a structured human-review pool, not gold episodes. P1 is now
split into P1A candidate-landmark elicitation and P1B learned-route continuation.
This defines a legitimate correct road choice while preserving the central claim:
landmarks are navigation- and cognition-useful cues, not merely salient objects.

### Recommended next step

User/teacher blind review of the sequence and decision boards, followed by
route-aligned reprojection only for KEEP/ADAPT cases. Identity/location
interventions and RL remain deferred until the Go Gate passes.

## 2026-09-09 Intermediate audit interpretation

### Purpose

This branch records the scientific meaning of the machine audit and the division
of labor for the next human gate. No new experiment was run.

### Main interpretation

The audit proves that Paris has connected graph, image, ERP, heading, embedding,
and candidate-route assets sufficient for a human-reviewed pilot. It does not
prove that any visual element is a verified landmark or that a mined maneuver is
a behaviorally correct action.

### Next gate

Review the 15 route boards, confirm task definition and action semantics, score
stability/spatial relevance/intervention feasibility, and freeze KEEP/ADAPT/
REJECT strata. Only then generate route-aligned views and run P1A/P1B.

## 2026-09-09 Intermediate audit interpretation

### Purpose

This branch records the scientific meaning of the machine audit and the division
of labor for the next human gate. No new experiment was run.

### Main interpretation

The audit proves that Paris has connected graph, image, ERP, heading, embedding,
and candidate-route assets sufficient for a human-reviewed pilot. It does not
prove that any visual element is a verified landmark or that a mined maneuver is
a behaviorally correct action.

### Next gate

Review the 15 route boards, confirm task definition and action semantics, score
stability/spatial relevance/intervention feasibility, and freeze KEEP/ADAPT/
REJECT strata. Only then generate route-aligned views and run P1A/P1B.

## 2026-09-09 Intermediate audit interpretation

### Purpose

This branch records the scientific meaning of the machine audit and the division
of labor for the next human gate. No new experiment was run.

### Main interpretation

The audit proves that Paris has connected graph, image, ERP, heading, embedding,
and candidate-route assets sufficient for a human-reviewed pilot. It does not
prove that any visual element is a verified landmark or that a mined maneuver is
a behaviorally correct action.

### Next gate

Review the 15 route boards, confirm task definition and action semantics, score
stability/spatial relevance/intervention feasibility, and freeze KEEP/ADAPT/
REJECT strata. Only then generate route-aligned views and run P1A/P1B.
