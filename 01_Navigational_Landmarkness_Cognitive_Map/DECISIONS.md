# Decisions

## 2026-09-26 0926 研究迭代

1. 主科学问题收敛为“城市视觉元素在给定空间任务和路线经验下的功能价值”，具体先测路线经验是否帮助局部续行选择；不把 Qwen leaderboard 作为研究目标。
2. Qwen 只负责候选区域提议和行为探针；gold action 由外部路线记录、道路几何和人工确认决定。模型理由不能作为真值。
3. A 线单图候选与 B 线连续路径并行推进。B 线先用 `main_03`、`main_06` 做 feasibility smoke；两条路线都保留 mixed-month/光照/施工风险并标 provisional。
4. GitHub 同步只保存轻量代码、schema、manifest、handoff、日志索引和摘要；图像、权重、patch cache、完整结果留在 NAS。
5. 服务器任务采用阶段性后台运行：正常状态静默并写日志，只有全流程成功或不可继续时主动回报，以降低 token 消耗。

## 2026-09-27 路径与同步协议

1. `/home/wangyq/Nav_Lmk` 固定存放项目代码、脚本、研究文档、schema、manifest、轻量摘要和第三方源码；`/home/wangyq/Nav_Lmk/third_party/dinov2` 属于源码依赖，不存放权重。
2. `/home/nas/wangyq` 固定存放 Qwen、DINOv2、VLAD 权重，原始和派生图像、448 缓存、patch cache 及大型实验结果；该前缀对应本地 `Z:\wangyq`。
3. 每个服务器任务开始时从 `origin/main` 拉取一次；运行期间保持静默，不轮询或推送中间进度。完成或 BLOCKED 时一次性回报；仅在需要本地读取轻量摘要时再提交/推送。
4. 服务器现有 `/home/wangyq/Nav_Lmk` 可能不是 Git 工作树；不得在原目录 `git init` 或覆盖。此时用独立临时 clone 或手动上传同步目录，并记录同步模式与来源 commit。
5. 路线 smoke 的四视角服务器物理文件名固定为 `{panoid}_panorama_{view_index}.jpg`；`view_index` 仍为 `0..3`，不能简化为 `{panoid}_{view_index}.jpg`，也不能写成 `v0..v3`。
6. 非 Git 服务器已有旧同步包需要更新时，先将旧 `sync/` 移到带时间戳的备份目录，再安装指定新提交；不直接删除或覆盖旧同步包。
7. Qwen 候选提议采用严格 schema v1.1：`uncertainty` 必须由模型显式输出，bbox 必须在 640×640 内；首轮格式失败允许一次同图重试，但不自动补字段或裁剪坐标。
8. 所有服务器实验产物按 UTC `run_id` 分目录保存；同一 case 的重试用 attempt 后缀，禁止覆盖先前结果和阻塞诊断。

## 2026-09-24 - Qwen candidate and route pilot execution

- The existing 44-query task is sufficient for the first candidate-region assay; construct a distinct, human-reviewed same-road hard-negative version only for finer localization claims. Do not relabel frozen I as N.
- Start Qwen single-view candidates and continuous-route feasibility preparation in parallel. A 12-query-view stratified candidate run is a workflow pilot; extend to all 44 after box review rules are stable.
- Use official Qwen2.5-VL-7B-Instruct as this sprint's concrete default, with pinned revision and recorded inference environment; the previously discussed Qwen3.5-9B remains unverified and is not silently substituted.
- Route choice is framed as learned-route continuation with legal alternative exits. Provisional mined maneuvers and uncorrected route boards are not formal gold; human-confirmed actions/materials and route-aligned ERP views are required before formal scoring.
- The main route condition excludes absolute coordinates and IDs from model input. Coordinate-assisted performance is a separate diagnostic condition.

## 2026-09-24 - Pilot 0 基线接收与研究解释边界

- 接收服务器开发基线作为候选区域贡献实验的完整图参照：212个VLAD与7392分数在本地独立复算通过；两个失败query保持不变，不为降低或提高准确率改题。
- 82P主分析每题1–3P，80P敏感性每题1–2P；后续报告正例数分层及P/N原始相似度，分层现象为事后探索。当前不能从高Recall直接推断地标功能、认知地图或同街道细粒度定位。
- area_id原值paris_arc不变；三对子片区只作报告层映射D01+D02、D03+D04、D05+D06。不修改冻结标签或特征输入哈希。
- 已数值验收不等于已复现全部服务器GPU过程。补齐/home/wangyq日志至NAS是交接资料任务，不要求重新下载模型、重新跑baseline或再上传ZIP。
- 本轮仅分析与本地验收；候选模型试运行、框审核、匹配对照与干预是下一阶段建议，尚未执行。

## 2026-09-23 - 人工复核回收与 baseline 准备

- 接收132项单人有提示审核，发布paris_local_v1_20260923；4无P query按事前规则剔除，44query/168reference，82P/6160N/1150I。该版本允许开发集完整图评分，旧v0继续保留为待人审历史草案。
- R123/R125为人工确认且完整图复查支持的25m窗口外对应，逐对覆盖而不全局放宽规则；主分析82P，同时预先规定同query/gallery将这两对改I的80P敏感性。否决P仍转I，不转N。
- 首轮标准dinov2_vitg14无register，448输入，blocks[31]的value局部特征，匹配32中心urban预训练词典，cosine hard assignment VLAD；局部/簇内/全局L2，fp32且TF32关闭。版本和实际权重/词典hash由服务器核验记录。
- 不在当前query或潜在eval拟合词典；不以CLS全局向量替代本次局部描述子配置。固定q/ref/标签/词典/评分器后才比较query-only区域干预。
- Ignore在排名前屏蔽；Recall@K定义为至少命中一P。M=maxP相似度−maxN相似度；保存全分数、逐题排名、困难N、失败图卡与两个边界例的敏感性。不能用高准确率或删除难题作为人为通过标准。
- 当前为辅助人审的小规模开发任务，不宣称无提示盲审/双人共识；活动N仅23项直接审核。统计报告以44query描述，另给12pano/6道路/3片区，避免视图或配对伪重复，不据此推断城市泛化或已形成认知地图。
- 本轮只做本地验收与服务器交接准备，未上传GitHub、联系服务器或运行GPU；轻量包足以交接任务，实际GPU提取/评分器仍由服务器实现。

## 2026-09-23 - 服务器数据路径与448预处理修订

- 用户确认Z:/wangyq/到服务器为/home/nas/wangyq/，代码工作目录为/home/wangyq/Nav_Lmk/；任务包给出固定图、ERP、heading CSV、权重及词典完整Linux路径。
- 磁盘输入名为panoid_panorama_{0..3}.jpg；panoid__v{0..3}只作审查/数据表内部ID。所有文件读取按image_relative_path连接，禁止由review ID直接构造磁盘文件名。
- 绝对中心朝向唯一沿用`(heading_from_api + 90 * view_index) % 360`；服务器preflight比对heading CSV原始hash、12236条文件名/ID、视角完整性及公式。四视图不重命名为绝对的front/right/back/left。
- 已有S/14、B/14 checkpoint不能代替G/14，新增官方标准无register G/14权重；新增匹配AnyLoc G/14/layer31/value/32/urban聚类中心，不在Paris query/reference/eval拟合。
- 按用户要求对全量12236个固定视角生成独立448×448 RGB PNG派生缓存，原640 JPEG不变；按绝对heading留有哈希/来源manifest。baseline仍只提取212活动图。
- 显式改用baseline execution request v2：Pillow resize至PNG后再ToTensor/Normalize，因量化和库实现与旧torchvision tensor resize不等价；保留v1配置/包供追溯，不能混合缓存或结果。使用PNG避免再次有损JPEG压缩。
- v2包新增路径预检、断点可续resize、官方权重/词典准备、G/14局部特征、VLAD实现、smoke测试、212图提取和P/N/I打分代码；本地9项CPU测试通过，服务器GPU smoke仍为待执行。
- AnyLoc README与同commit可执行demo的中心文件名不一致（c_center vs c_centers）；以压缩包实际匹配的成员、SHA与[32,1536]验证为准，仅取正确词典，不任意解压或换文件。

## 2026-09-23 - Pilot 0 服务器交接包 v2.1

- 服务器执行合同仍为baseline request v2；交付包升级为v2.1以修复评分器哈希校验运行缺陷，并在完整预检通过后才创建特征输出目录。
- v2.1在本地通过10项CPU测试、目标脚本编译及冻结题库17项检查；这些检查不代表服务器GPU smoke、全量448处理或模型baseline已经运行。
- 服务器交接使用新建server_baseline_package_v2_1_20260923.zip；旧v2 ZIP保留用于追溯，不覆盖。

## 2026-09-24 - AnyLoc 词典入口修订

- 原AnyLoc SharePoint单文件和公开文件夹均由服务器实测返回HTTP 404，不再作为下载方案。
- 采用AnyLoc作者组织 `AnyLoc/DINO` GitHub Release v1 的固定 `dinov2_vitg14_l31_value_c32_urban_c_centers.pt`，197425 bytes，SHA-256 `a684e571f05c85c804e7301547d8620c28ae759e824adb9ac88294b080feaba0`；该文件与当前 `[32,1536]`中心格式匹配，服务器脚本自动下载并用PyTorch验证。
- 不改变G/14、layer31 value、32 urban、cosine-hard VLAD和448 PNG baseline合同；不在Paris数据上拟合词典。交接包升级为v2.2。

## 2026-09-24 - Pilot 0 scientific interpretation boundary

- Treat the completed G/14 plus urban-VLAD run as a reproducible spatial-correspondence assay, not as a verified-landmark or cognitive-map result.
- Keep the reviewed 44Q/168R/82P/6160N/1150I task frozen for development comparisons; construct a separate same-road, near-distance hard-negative version before making fine-localization claims.
- Next experiment order: Qwen single-view candidate proposals -> human bbox audit -> matched controls -> query-only descriptor/input interventions. Continuous sequence and route-edge decisions remain a later functional module.
- Any descriptor-removal implementation must use patch-level DINO descriptors aligned to the 32x32 grid; the final 49152-D VLAD vector alone is insufficient. The returned feature index already points to 1024x1536 row-major patch files, so verify and reuse that cache before considering re-extraction.

## 2026-09-23 - Pilot 0 spatial draft and human review boundary

- 用户授权的步骤1–3执行到人工复核交付物，草案paris_local_v0_20260922，全体评分关闭。
- 按元数据选三片区×两条相邻不同道路，每街段9pano含2query和7reference。初版六条远隔道路在看图前修订，所有四视图随pano统一角色，q/reference无共享pano。
- P起点同段8–25m、heading差≤30°、每query最多2个待审；额外候选或未建立关系保守I。N起点不同段、无共享OSM端点且>50m。参数尚未科学冻结，模型不定义标签。
- 六条道路全部133pano列dev，100m缓冲；其余2430仅eval_candidate。地理隔离不保证没有共同远景。
- 侧向近墙视图10–20m侧移后可能没有可靠重叠，31对优先人审。无合格P的query可剔除并报告，不强求48题或固定通过率，不把拒绝P自动变N。
- N抽检发现问题时重查组/规则；I出现共同场景时逐项讨论边界，不自动全局提升。修改进入新版本，图库/标签固定后再比较条件。
- 轻量服务器包仅可用于交接、环境/模型核验、特征smoke test，无正式评分及GitHub上传。旧路线P1A/P1B审核gate不影响本次准备。

## 2026-09-22 - Updated requirements: local-retrieval Pilot 0

- Source: the user's current request and two saved research conversations in `../Chats/`; interpretation and provenance are in `PILOT0_EXECUTION_PLAN.md`.
- Current first task becomes local place correspondence/retrieval with positive, negative and ignore relations. Task construction and a full-image baseline precede batch VLM proposal generation.
- Reuse the full Paris asset chain. The historical 10 routes and 15-route review pool are optional context; their P1B gates do not apply to starting this task.
- Retain the distinction between descriptor and input interventions. Compare candidate regions with matched regions under a fixed reference gallery, label set, vocabulary and scorer; first-version interventions change query only.
- VLM proposals are candidate cues. Their functional contributions are separate evidence dimensions, not automatic verified-landmark or cognitive-map labels.
- Local work owns spatial task construction and review; server work owns model checks, feature extraction and GPU experiments. GitHub is a planned handoff channel; no remote is configured or used in this session.
- Not frozen: distance/heading buffers, sample counts, spatial holdout feasibility, matching tolerances, exact mask operation, exact model revisions or hardware configuration. Chat suggestions are starting points, not verified experiment settings.
- The long-term Evidence → Memory → Map → Agency program is retained; orientation, flexible navigation and multi-time acquisition are not Pilot 0 prerequisites.

## 2026-09-17 - Provisional usability decision

- Retain Paris: provisional ADAPT; raw USABLE_WITH_FIXES / current15-route pool NEEDS_REMINING / stimuli REQUIRES_REPROCESSING. No formal experiment authorized by this audit result.
- Select jointly on capture month and physical observation separation, not a fixed8pano requirement. Exact sampling parameters remain pending.
- Separate API capture coordinates, historical original coordinates and snapped graph coordinates. EPSG:2154 API-position distances are v2primary; original-coordinate distances remain sensitivity evidence.
- Exclude the incoming return edge from the multiple-departure gate. main_11 fails currentP1B case; retain data for P1A/place-memory.
- main_10 has visibleArc and cannot count as a clean ordinary forward route. Arc stratum never substitutes for same-image matched controls.
- Decision test views use incoming observer pose, not correct outgoing bearing. Reviewer answer labels are not participant content.
- Replace immediate full human scoring with four semantic confirmations. Machine scores are provisional, not human annotation or functional landmark evidence.
- Reprocess/re-mine existing Paris first. Do not assume replacement observations exist. No evidence currently justifies full recollection/replacement.
- Proposal mainline unchanged; no candidate declared a verified landmark.

## Stable decisions

- The active project is navigational landmarkness and landmark-anchored cognitive maps.
- The core task is not generic active perception and not complete navigation at the first stage.
- Landmarks are defined functionally as navigation-useful and cognition-useful cues.
- Cognitive maps are operationalized as sparse landmark-anchored graphs linking street-view nodes, landmarks, road edges, and scene-level fields.
- Active inspection is optional and should be used only as an observation condition or evidence acquisition cost.
- APRS / EAGLE-360 are technical inspirations for panoramic evidence organization, not the main research framework.
- UrbanHue is archived context and review-response support, not the protagonist of this new project.
- The first prototype should be small, runnable, and evidence-grounded.
- The audit and candidate-discovery stage uses four fixed FOV=90-degree views; formal route-choice input must be route-aligned FOV=90-degree views reprojected from ERP.
- Do not prematurely split the research into three small papers. Build an integrated prototype first.
- Before selecting the first experiment, run a Paris Data and Task Feasibility Audit. Task design must follow verified data, route, graph, image, and code capacity rather than assume route choice, place recognition, route memory, or online exploration in advance.
- The feasibility audit combines machine-readable asset/join/graph checks with human review boards. File existence or graph degree alone cannot establish functional landmark suitability.
- New literature enters the candidate knowledge base first and becomes an operational step only when it solves a real data-audit, experiment-design, or validation problem.
- The historical `trajectory_0..9` routes are description-generation examples, not gold routes for the current project.
- Paris fixed views use the verified relation `center(view_i) = (heading_from_api + 90*i) mod 360`; fixed `view_0..3` must not be permanently labeled front/right/back/left.
- Navigation maneuvers are derived from signed incoming/outgoing geographic bearings and do not depend on panorama heading. Current mined maneuvers remain provisional until human confirmation.
- Formal direction-choice experiments should reproject route-aligned FOV=90-degree front/right/back/left views from ERP. Nearest fixed views are for audit/review only because residual error can reach 45 degrees.
- Candidate mining uses audited connector zones, OSM one-way legality, at least two legal departures, and separate Arc de Triomphe controls. Single-pano graph degree is not sufficient to define a decision point.
- The historical UrbanNav system is a method reference or later baseline candidate, not the first experimental carrier: it uses target coordinates, legacy multi-hop movement, BFS/tree-like graph processing, and unverified checkpoint replay.
- Current Paris decision is `provisional ADAPT`: retain Paris and stratify a small pilot, pending user/teacher human review before final GO.
- The first behavioral prototype is split into P1A human candidate-landmark elicitation and P1B learned-route continuation/route-memory choice. A road becomes the correct choice only because the participant learned that route; the mined maneuver alone does not define behavioral correctness.
- Old UrbanNav 16-view input uses centers every 22.5 degrees with FOV=60 degrees per view. Center spacing and FOV must not be conflated.
- The current fixed four-view assets are canonical for audit only. Their batch script provenance is missing even though pixel alignment and the heading relation are verified.
- The raw undirected pano graph is an indexing/mining substrate, not an unverified action graph. Formal online navigation requires a direction-correct road-level or decision-zone graph.
- Current snapped coordinates can be used for pilot review, but formal graph freezing must reproject to roads in a metric CRS and recheck the two decision panos whose metric alternative differs by more than 1 m.
- Arc de Triomphe cases are a super-landmark data stratum, not the within-image matched control for later interventions.

## 2026-09-27 - 产物版本化

- 服务器每次运行生成唯一 UTC `timestamp_utc` 和 `run_id`，结果目录使用 `/home/nas/wangyq/outputs/{run_id}/`，轻量运行目录使用 `server_run/{run_id}/`。
- 同一 case 的格式重试使用 `.attempt01`、`.attempt02` 后缀；旧结果、旧 `BLOCKED.json` 和旧同步目录必须保留，不得覆盖。
- manifest、sidecar、日志和最终回报必须携带 `run_id`、`timestamp_utc`、`attempt`、`source_commit`、`sync_mode`，以区分不同实验版本和同步来源。

## Pending decisions

- Whether provisional ADAPT becomes GO after minimal human confirmation, targeted reprocessing/re-mining and route/action quality checks.
- Whether later candidate expansion uses VLM, object/POI sources, or mixed methods after the initial human-elicited P1A set.
- Whether road-edge headings can be derived from existing road graph / navigation task data.
- Whether the P1A/P1B Go Gate retains enough routes and strata for a Paris pilot.
