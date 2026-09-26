# Worklog

## 2026-09-24 - 下一阶段实验细化与服务器交接

- 针对用户八项问题核对本地基线审计、212 图 feature_index、路线候选/人工 gate 与输入朝向合同。
- 决定现有 44 query 足以启动单图候选；同路困难负例另立版本。明确 12 view 试运行、人审标准、640/448/patch 映射、匹配对照与结果指标。
- 为老师关注的连续导航并行安排路线可行性试验，并区分路线 smoke 与需人工确认的正式方向实验。
- 产出 `NEXT_STAGE_QWEN_ROUTE_HANDOFF_20260924.md`。本次未下载模型、未运行 Qwen、未改冻结题库或 NAS 结果；当前会话中 Z: 未挂载，采用已审计本地副本核对。

## 2026-09-26 - 0926 研究迭代同步包

- 读取 `Chats/Branch · 研究方向概括_0926.html` 与 `Chats/Extensive reading papers - 解读文章提炼方法_0926.html`，确认研究主线为路线经验条件下的视觉线索空间功能与局部行动支持。
- 新增 `sync/RESEARCH_DESIGN_20260926.md`、`sync/ROUTE_SMOKE_MANIFEST_20260926.json`、`sync/QWEN_OUTPUT_SCHEMAS_20260926.json` 和 `sync/SERVER_CODEX_HANDOFF_20260926.md`。
- 将 `main_03`、`main_06` 固定为候选路线 smoke；明确其动作仍为 provisional，不能作为 gold。
- 服务器侧复用已下载的 `/home/nas/wangyq/model_weights/Qwen`，先检查视觉模型有效性，再进行 2 图 smoke、6 个候选 case 和三条件路线决策 smoke；正常运行不主动轮询，只有成功或 BLOCKED 回报。
- 尚未创建远程 GitHub 仓库：本机 `gh auth status` 显示账户 token 已失效，需重新认证后才能创建和推送。

## 2026-09-26 - 0926 研究迭代同步包

- 读取 `Chats/Branch · 研究方向概括_0926.html` 与 `Chats/Extensive reading papers - 解读文章提炼方法_0926.html`，确认研究主线为路线经验条件下的视觉线索空间功能与局部行动支持。
- 新增 `sync/RESEARCH_DESIGN_20260926.md`、`sync/ROUTE_SMOKE_MANIFEST_20260926.json`、`sync/QWEN_OUTPUT_SCHEMAS_20260926.json` 和 `sync/SERVER_CODEX_HANDOFF_20260926.md`。
- 将 `main_03`、`main_06` 固定为候选路线 smoke；明确其动作仍为 provisional，不能作为 gold。
- 服务器侧复用已下载的 `/home/nas/wangyq/model_weights/Qwen`，先检查视觉模型有效性，再进行 2 图 smoke、6 个候选 case 和三条件路线决策 smoke；正常运行不主动轮询，只有成功或 BLOCKED 回报。
- 尚未创建远程 GitHub 仓库：本机 `gh auth status` 显示账户 token 已失效，需重新认证后才能创建和推送。

## 2026-09-24 - 服务器基线回传与本地独立复算

- 续检新增scripts/pilot0_confirm_server_return.py及current_nas_confirmation.json；已有证据副本与当前NAS结果逐项相同，212个VLAD再次只读核验，7392相似度独立复算最大差4.23e-7，8136检查通过。模型、图像、标签与服务器输出未写入。
- 修正本地报告“每题1或2P”的文字错误：82P主分析为8题1P、34题2P、2题3P；80P敏感性为8题1P、36题2P。单P组6/8、margin中位数0.014281；多P两组均全对。该分层为事后描述，不能作因果结论。
- 本轮逐一查看11张既有case预览，核对R031/R055/R067原人审证据；不重复发起132项人审，不自动删除或重标失败题。
- 接收桌面SERVER_TO_LOCAL.md，仅定点读取用户指定Z:/wangyq/outputs/Paris_local_v1_20260923及对应缓存/权重来源元数据。轻量回传副本和验收报告保存于outputs/pilot0/server_return_audit_20260924；NAS产物、冻结题库和原ZIP未改。
- 新增scripts/pilot0_audit_server_return.py；以项目绑定Python运行，NAS只读、本地输出。212个VLAD逐个hash/shape/norm通过；float64独立复算7392相似度最大误差4.23e-7，主/敏感性44题排名与指标一致。
- 结果主/补充清单22文件hash通过；核对12236条缓存manifest/heading及212活动图hash连接，抽查6个patch与6张448 PNG，实际词典SHA核对通过。未重复扫描全部图像、全部patch或4.55GB G/14。
- 11张失败/低margin图卡已视觉复核，77张内嵌图与特征输入逐项hash相同。两项失败保留为困难例，没有发现推翻既有人审标签的充分依据。R123/R125非最高分P，因此敏感性指标不变。
- 发现area_id全部paris_arc，原分层并未区分3个子片区；依据原选路配对另做报告层汇总15/16、16/16、11/12，不改冻结表。
- SERVER_FOLLOWUP.md已准备：请服务器把/home/wangyq下原始smoke、preflight、环境、最终完整性与命令日志镜像至NAS新目录。尚未执行该指令或启动Qwen/区域干预。

## 2026-09-24 - AnyLoc词典404与固定Release修订

- 将服务器准备说明统一到最终交接包 `server_baseline_package_v2_2_final_20260924.zip`；重新生成并验证45个文件，ZIP SHA-256为 `519aec73d72a37ed8027f33064917b0f6f1a2700e1048cccd12ce8e7d33df82f`，大小1440349字节。
- 服务器实测确认AnyLoc原SharePoint单文件和公开文件夹均返回HTTP 404；没有让服务器使用其他domain、层或Paris重训词典。
- 核验AnyLoc作者组织 `AnyLoc/DINO` GitHub Release v1的独立资产 `dinov2_vitg14_l31_value_c32_urban_c_centers.pt`：197425 bytes，SHA-256 `a684e571f05c85c804e7301547d8620c28ae759e824adb9ac88294b080feaba0`；本地检查其PyTorch ZIP tensor存储为[32,1536] float32、有限且中心非零。
- 更新服务器词典准备脚本，默认自动下载该固定Release并记录release/asset ID、URL和hash；旧SharePoint ZIP仅保留为显式备用路径。
- 交接说明、项目决策和状态同步改为v2.2；服务器仍可自行完成词典下载，不需要用户手动传文件。
- v2.2 ZIP已生成并通过45文件SHA/大小/CRC校验：SHA-256 `3ec37830e04bcc1ef51766aeede25b61966e48c0c3aefe4abbb578820b2f5fbf`，大小1440228字节。
## 2026-09-23 - Pilot 0 服务器交接包 v2.1 验收

- 复核用户确认的服务器映射路径、panoid_panorama_0至3物理文件名与panoid__v0至3内部ID区别，以及绝对朝向公式；交接说明均一致，未扫描Z盘或连接服务器。
- 发现评分器引用hashlib但未导入；补齐导入，并新增小型端到端评分测试，验证任务/request ID、特征索引hash、每个VLAD向量hash、单位范数、忽略关系屏蔽和输出manifest路径。
- 将特征提取输出目录创建移至v2服务器预检通过之后，避免失败后留下阻塞重试的空目录。
- 10项CPU测试通过；resize/权重准备/VLAD/preflight/smoke/extraction/scoring/delivery目标脚本编译通过；冻结题库17项检查通过（44 query、168 reference、82P/6160N/1150I）。
- 更新服务器准备页与轻量包说明，生成server_baseline_package_v2_1_20260923.zip，旧ZIP不覆盖。
- 最终包已生成并从ZIP独立复核：45个清单文件hash/大小与ZIP CRC通过；ZIP SHA-256 8bb6eebbf1227139c7dba66e1537b96e7e0714a2cce796d92e574961fdeb0014，大小1438318字节；未包含图像、权重或特征。
- 独立检查确认ZIP内含服务器执行说明、v2配置、修复后评分器和10项CPU测试；没有引用旧v2 ZIP作为执行包。
- 未扫描Z盘、访问服务器、下载权重或词典、运行448全量resize或GPU baseline。

## 2026-09-23 - 人工复核回收与 baseline 准备

- 接收D:/EgeDownload/HUMAN_REVIEW_paris_local_v0_20260922.csv及.json；132项完整且逐字段一致，任务ID/指纹匹配。保留原件与旧草案，生成outputs/pilot0/reviewed_v1_20260923。
- 80项原P保留、16项P转I、24项N保持、10项I保持、2项I转P；R123/R125分别32.5m/27.2m，复查完整图支持人审，作为逐对边界例外，不全局放宽25m窗口。预设80P保守敏感性重评分。
- 4query没有合格P，按原规则剔除；v1为44query/12pano、168reference/42pano、212图、7392关系，82P/6160N/1150I。图库ID不变；只允许探索性开发基线。17项冻结数据校验通过。
- 单人wyq辅助审核；104条引用预审提示已展开为effective_evidence并保留原文。活动N中23项直接人审、6137项规则来源；未把全矩阵称作全人工真值。
- 定点读取官方AnyLoc和DINOv2五个源码文本并锁定commit/hash；确认标准G/14、blocks[31] value、32 urban词典、cosine hard assignment、448输入及49152维VLAD。没有加载权重、词典或执行GPU前向。
- 新增审核接收、冻结任务检查、官方来源检查和交付脚本；实际命令、来源和错误见该版本REPRODUCE.md。服务器参数及分析要求在SERVER_BASELINE_TASK.md与configs/baseline_request.json。
- 服务器轻量包server_baseline_package.zip为1393815字节；28文件逐项hash/大小及ZIP CRC通过。包不含图像/模型/特征，未上传、未联系服务器，未再次扫描Z盘。
- 同步PROJECT_CONTEXT、SERVER_CODEX_HANDOFF_PILOT0、DECISIONS和状态日志：v1人审已结束，等待服务器核验实际环境并执行完整图baseline，后续才进行候选与干预。

## 2026-09-23 - Pilot 0 本地步骤 1–3：交付人工复核

- 用户授权连续执行本地索引、配对和复核材料，停在人工语义审核处；本轮完成到该位置。
- 复用已有审计，定点读取小型源表及两个影像目录的非递归文件名清单：3059 pano、12236固定视图、3059 ERP路径；3058图节点、3310边、247道路段。没有全盘扫描或读取ERP像素。
- 新增scripts/pilot0_local.py、pilot0_tasks.py、pilot0_review.py、离线模板、pilot0_validate.py、审核回收测试和轻量打包脚本。具体命令、来源路径、字段关系在outputs/pilot0/local_v0_20260922/REPRODUCE.md，执行记录在run.log，环境在environment.json。
- 在看图前按元数据将初稿六条远隔街段改为三片区×两条相邻不同道路，纳入附近负例；seed42，54pano，48query/168reference。8064条关系：96候选P、6720规则N、1248I；336个N为几何近场候选。
- 六个道路段全部133pano划为dev，496buffer，2430eval_candidate；最近保留点距全部dev点100.0195m。留出尚未冻结，距离隔离不代表语义独立。
- 只缓存216张所选固定图，全部640×640解码/哈希通过。生成132逐对卡、22图板、SVG空间图及离线审核页；全132对图板预审，R019/R051/R071/R095追加完整图检查，31对列优先复核。人工答案保持空白。
- 29项结构/哈希/坐标/距离/分组检查通过；EPSG2154与WGS84椭球距离最大差0.122m。6项审核回收测试通过，仅使用临时合成记录。页面JavaScript语法、唯一ID和本地链接通过；内置浏览器阻止file URL，未实测交互，未绕过限制。
- 交付REVIEW_GUIDE.md、review/index.html、HUMAN_REVIEW.csv、Codex预审、LOCAL_TO_SERVER.md、task_manifest.json及约1.69MB轻量ZIP。ZIP逐项哈希通过，无图像/权重/特征或paths.local配置，没有上传。
- 状态DRAFT_PENDING_HUMAN_REVIEW，全矩阵scoring_allowed=False。按用户要求停在图像语义审核，收到132项答案后解决分歧、剔除无合格P的query并发布新版本，不强求48题。
- SVG空间图另用bundled Node sharp渲染至qa/spatial_overview.png并目视核验，六组、图例、比例尺及缓冲点正常；这是静态SVG图核验，不是被阻止的HTML浏览器预览。

## 2026-09-22 - 新研究对话读取与 Pilot 0 分工

- 用户要求读取两份 Chats HTML，按新要求列实验顺序、划分本地／服务器工作并准备 GitHub 交接；本轮停留在需求理解与任务拆分，没有启动配对挖掘或模型实验。
- 使用 research-workflow 的证据分级。逐段读完文件实际保存正文：Branch 8 个 section（含一个无正文停止状态）、Extensive reading 13 个 section；提取时保留 `data-math-source` 的公式。两份源文件 SHA-256 见新执行计划。
- 明确当前 Pilot 0 为局部地点检索中的候选视觉线索贡献；先建 P/N/I 题库和完整图基线，再接 Qwen、两层干预和复现。旧 P1A/P1B 路线 gate 保留为历史任务边界。
- 命令：`Get-ChildItem -LiteralPath Chats -File`；Python stdlib `HTMLParser` 只读提取并在会话内分段读取；`Get-Content` 复用本地审计；对四个明确 Z 路径 `Test-Path`；对 heading CSV `Import-Csv` 与 `Get-FileHash`；`git -C F:/Codex_local/Nav_Lmk rev-parse --show-toplevel`。
- 普通受限进程看不到 Z:，限定路径的只读访问成功。heading CSV 3059 行、3059 唯一 ID，SHA-256 `00685688b909cce93259786fe8789539ebe500dce8e538ce4fa58af11b9fe539`。无递归扫盘、无图像读取。
- Git 检查确认当前目录不在工作树中；没有仓库初始化、提交、push 或服务器远程任务。
- 新建 `PILOT0_EXECUTION_PLAN.md` 和 `SERVER_CODEX_HANDOFF_PILOT0.md`；同步 PROJECT_CONTEXT、EXPERIMENT_DESIGN、CODEX_TASKS、DECISIONS 入口与四份状态日志。实际代码、原始数据和旧审计结果未更改。
- 校验：两份源 HTML 哈希未变，两份新文档结构正常，八份入口／状态文档本轮标题各一个；记录于 `_audit_outputs/pilot0_requirements_sync_20260922.json`。未决仍为配对开发与人工审计、数值参数、模型／词典及资源、GitHub remote 和 Linux 路径映射。当前没有新科学实验结果。

## 2026-09-22 - 新目标到来前的数据关系回顾

- 用户明确本轮仅需理解原有数据及关联关系；新的实验组织目标将另行提供。本轮未重组实验、修改代码或运行模型。
- 已读根目录及项目必读上下文，并核对 `_audit_outputs/repo_inventory.md`、`data_manifest.yaml`、`data_schema_report.md`、`structured_asset_audit.json`、`graph_build_provenance_report.md` 与最新可行性总结。
- 核心关联：`pano_id/panoid` 连接 ERP、固定四视角、heading/日期/坐标、DINO ID 与图节点；pano-to-road 映射连接道路段；`route_id + step_idx` 组织路线中的 pano 引用。
- 区分 API 拍摄坐标、历史原始坐标与吸附后的图坐标；固定视角与路线相对方向；旧十条轨迹与后来十五条候选路线。
- 本轮证据来自本地已保存审计和表头，没有重新访问或验证 Z 盘原始数据；数量沿用此前审计。
- 命令：`Get-Content -Raw/-TotalCount` 读取报告及 CSV 表头；`Get-ChildItem .../_audit_outputs -File` 定位实际文件；`rg -n` 核对审计脚本中的 embedding 文件和道路字段。
- 输出：会话中的数据关系说明及四份会话状态日志。实验设计与既有科研决策未改动；检索与日志写入的已解决错误见 ERROR_LOG。

## 2026-09-17 - Paris feasibility audit v2

- Scope: Tasks 1-6, provisional usability decision and minimal human confirmation only. No VLM, intervention, UrbanNav or participant experiment.
- Read mandatory root/project context and all user-specified audit documents; parsed complete candidate JSON and CSV inputs.
- Used research-workflow evidence classification and scientific CSV conventions from the spreadsheets skill. Kept requested plain CSV outputs rather than adding a workbook.
- Audited 120 step dates against graph year/month, original point CSV and Tile API metadata. All dates agree, all 15 routes mix months, main_03 contains one 2012-06 pano.
- Recomputed 105 distances from Tile API capture coordinates in EPSG:2154 using pyproj 3.7.2, with original/snapped coordinate sensitivities and WGS84 geodesic cross-check (maximum difference 0.00202 m).
- Directly inspected all 30 existing sequence/decision boards and both overview maps. Recorded fresh pixel observations in `_audit_work/route_visual_observations_v2.json`; earlier preliminary review was not used as ground truth.
- Re-read selected OSM road records. All 15 long-baseline turns agree with existing maneuver classes, but main_11 has only one non-return departure. main_07 and arc_control_03 need road-sign/OSM temporal semantics checks.
- Scoped elevated Z-drive check verified 120 ERP and 480 fixed-view paths. Remote heading CSV equals the ZIP metadata hash. No unrelated Z folders scanned.
- Generated the 10 requested deliverables plus step source metadata, provenance, run log and validation JSON. Old human/preliminary CSVs and source input hashes unchanged.
- Machine result: KEEP 0 / ADAPT 14 / REJECT 1 (main_11 current P1B case only). Provisional ADAPT; raw USABLE_WITH_FIXES, pool NEEDS_REMINING, final stimuli REQUIRES_REPROCESSING.
- Validation: 120 date rows, 105 pair rows, 15 per-route rows, 30 board hashes, all evidence paths and enums, 90 blank human response cells, source preservation and missing/threshold fixtures PASS.

### Commands and environment

Bundled Python: `C:/Users/Admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`.
Installed `pyproj==3.7.2` into project-only `_audit_work/feasibility_deps/`; bundled runtime unchanged.
Executed `_audit_work/audit_route_feasibility_v2.py --archive D:/BaidudiskDownload/Paris_check_for_Codex.zip --graph F:/Codex_local/Nav_Lmk/98_Others/kl.Line_Points_3.json --output-dir <project>/_audit_outputs --image-root Z:/wangyq/GSV_Paris --remote-heading Z:/wangyq/Street_view_and_points_Paris/GoogleAPIMETADAT/Paris_Points_heading_3059/Paris_Points_heading_3059.csv`.
Executed `_audit_work/build_route_review_v2.py --output-dir <project>/_audit_outputs --observations <project>/_audit_work/route_visual_observations_v2.json` and `_audit_work/validate_route_feasibility_v2.py --output-dir <project>/_audit_outputs`.
Full numeric command and software/source versions: `_audit_outputs/route_feasibility_v2_provenance.json`; printed results: `route_feasibility_v2_run.log`; checks: `route_feasibility_v2_validation.json`. Transient tool/access errors are recorded in ERROR_LOG.md.

Stop condition reached: awaiting user/teacher four-question confirmation. No route resampling, reprojection, re-mining or formal experiment executed this turn.

## Initialization

This project workspace was generated for Codex use.

Initial goal:

- study navigational landmarkness in street-view environments;
- connect landmarks to cognitive maps;
- build a small landmark-anchored cognitive graph prototype;
- treat APRS/EAGLE as technical inspiration, not a research template;
- treat UrbanHue as prior archived work and review-response support.

Future Codex sessions should append here with:

- date/time;
- user task;
- files read;
- files modified;
- commands run;
- outputs generated;
- results;
- errors;
- next steps;
- what ChatGPT web should know.

## 2026-07-29 - Partial Paris Data and Task Feasibility Audit

### User task

- Read the supplied research-execution bundle and the latest Notion research page.
- Begin a feasibility-first scan of Paris data, CityBench, the uploaded topology, and the historical RL area.
- Do not run VLM/RL, train, edit source data, or preselect an experiment.

### Sources read

- All mandatory local project/context/workflow files.
- All seven files inside `C:\Users\Admin\Downloads\01_Research_Mainline_and_Execution.zip` without extracting or modifying the ZIP.
- Notion page `Navigational Landmarkness and Landmark-Anchored Cognitive Map`, including all four comment discussions.
- `C:\Users\Admin\Desktop\kl.Line_Points_3.json`.
- The supplied Kepler screenshot.

### Main commands/checks

- `rg --files` and PowerShell inventory/schema checks.
- Notion search, fetch, and comment retrieval; no Notion writes.
- `Get-PSDrive`, `Test-Path`, `net use`, and SMB mapping checks for `Z:`.
- Kepler schema parsing and graph analysis with bundled Python 3.12.13 using only the standard library.
- Reproducible PowerShell graph rendering to PNG/SVG and three bounded visual-QA rounds.

### Outputs generated

- Complete partial-audit package in `_audit_outputs/`, including inventory, manifest, asset classification, schema, graph, join, image, code, shortcut, readiness, next-action, context, error, and figure files.

### Main results

- 3,058 unique pano nodes and 3,310 unique undirected edges; all endpoint joins and coordinates are consistent.
- One connected component, no isolated nodes, cycle rank 253, and 378 raw degree-at-least-3 nodes.
- 2,849 weighted edges alone form 209 path components with no cycles; 461 null-weight connectors create the connected cycle-rich topology.
- Spatial grouping reduces 378 raw high-degree nodes to 192/128/99 candidate zones at 10/15/20 m.
- `Z:` is not mounted; images, routes/actions, embeddings, CityBench, and RL assets are blocked/unscanned rather than missing.

### Decision

- Project status is `Not ready for Phase 1`; Go / Adapt / Replace is deferred.
- The graph is structurally promising but cannot select the first task without route, image, heading, action, and human-review evidence.

### Errors

- Remote mount absent; SSH config blocked by sandbox; workspace not visible as a Git worktree.
- Optional Matplotlib dependency absent; audit figure generated with built-in Windows drawing.
- Initial PowerShell execution-policy and coordinate-binding errors were fixed and logged.

### What ChatGPT web should know

- The older Landmark Assistance Pilot is now a conditional candidate, not the project entry point.
- The next work is to complete Phase 0 after remote access, then produce human-review boards and select the task from evidence.

## 2026-07-30 - Completed machine audit and full-graph route candidate mining

### User task

- Recheck the mounted Z drive with path-scoped sandbox-external permission.
- Determine the relationship between GSV metadata heading and stored four-view angles.
- Treat the old ten manual trajectories as historical and search the full graph for more suitable routes/actions.
- Selectively scan only assets relevant to the Paris feasibility audit.

### Sources read

- Authorized Paris roots under `Z:\wangyq\GSV_Paris`, `Street_view_and_points_Paris`, and CityBench `outdoor_navigation`.
- `GSV_tiles_download_graph.ipynb` and the uploaded `UrbanNav_neo_fromPC.zip`.
- Extracted, source-only UrbanNav audit copy; large checkpoints were not bulk-extracted.
- Existing graph, connector, join, route, heading, and image audit outputs.

### Work performed

- Verified fixed-view orientation through code tracing, six-pano/eight-hypothesis pixel comparison, and an Arc de Triomphe geographic anchor.
- Audited old RL inputs, recurrent policy, environment-only graph usage, reward, action semantics, checkpoint state, and orientation inconsistencies.
- Mined full-graph route candidates with connector validity, one-way legality, decision-zone, route-length, Arc-buffer, and spatial-diversity filters.
- Generated 12 balanced main routes and three balanced Arc controls with maps, sequences, and decision boards.
- Added strict route validation and verified 480 image files plus 120 heading records through approved Z-drive read access.
- Rewrote stale blocked-access reports and updated direction/data schemas.

### Outputs

- `_audit_outputs/route_task_report.md`
- `_audit_outputs/candidate_routes.json`
- `_audit_outputs/candidate_route_pool.json`
- `_audit_outputs/candidate_route_steps.csv`
- `_audit_outputs/candidate_route_review.csv`
- `_audit_outputs/candidate_route_review_preliminary.csv`
- `_audit_outputs/candidate_route_validation.json`
- `_audit_outputs/rl_system_audit.md`
- `_audit_outputs/heading_orientation_report.md`
- `_audit_outputs/figures/candidate_routes_main/`
- `_audit_outputs/figures/arc_controls/`

### Results

- Fixed view `i` has geographic center `(heading_from_api + 90*i) mod 360`; it is not inherently north/east/south/west or route front/right/back/left.
- 211 raw candidates passed structural filters; 72 entered the main pool and 63 the Arc-control pool.
- Selected main routes are balanced left/right/forward 4/4/4; controls are 1/1/1.
- All selected routes have at least two legal departures; all route/image/heading/board validations pass.
- Current Paris decision is provisional ADAPT, pending the user's and teacher's six-dimension review.

### Errors and security

- PowerShell's default local-code-page read initially made valid UTF-8 JSON appear malformed; explicit UTF-8 and strict Python parsing pass.
- Historical source contains hard-coded service credentials; values were not copied into reports and must be revoked/rotated.

### What ChatGPT web should know

- The old ten routes must not be treated as gold.
- The new route actions are structurally derived but still provisional.
- Formal direction experiments should regenerate route-aligned views from ERP.
- Do not repair or train RL before the human route/task gate.

## 2026-08-03 - Paris archive provenance, heading semantics, and task freeze

### User task

- Decide how the 15 mined routes should be reviewed without losing route context.
- Selectively audit `Paris_check_for_Codex.zip` for Paris graph, snapping, and projection provenance.
- Confirm the relationship between ERP local angle, Google metadata heading, old 16 views, and current four views.
- Keep all execution results explainable and aligned with navigational landmarkness/cognitive-map research.

### Sources and commands

- Read-only ZIP inventory and graph/Shapefile comparisons using the bundled Python runtime.
- Selective Z-drive search limited to code/notebook files under `GSV_Paris` and `Street_view_and_points_Paris`.
- Google official Tile API, Static API, and JavaScript Street View documentation through approved read-only network access.
- Pixel/graph/route audit outputs and the 30 existing sequence/decision boards.

### Work performed

- Located the exact final `kl.Line_Points_3.json` copy and verified its SHA-256.
- Reconstructed the graph version chain and `Line_Points_2 -> Line_Points_3` delta.
- Reproduced the point-to-road snapping geometry for all 3,059 intermediate points and compared it with metric-CRS projection.
- Traced the executed Paris graph cells, 34 manual connections, and final graph export.
- Added `_audit_work/trace_projection_calls.py`; confirmed the Paris archive and two Z-drive code roots do not contain the current four-view batch script.
- Verified official heading/centerHeading semantics and distinguished Tile metadata from Static API request heading.
- Froze P1A human candidate elicitation and P1B learned-route continuation/route-memory choice.
- Expanded the human review table and produced a 30-board blind-review guide.

### Outputs

- `_audit_outputs/paris_archive_provenance_report.md`
- `_audit_outputs/graph_build_provenance_report.md`
- `_audit_outputs/panorama_projection_audit.md`
- `_audit_outputs/HUMAN_ROUTE_REVIEW_GUIDE.md`
- `P1A_P1B_TASK_SPEC.md`
- `_audit_outputs/archive_audit/projection_call_trace.json`
- Updated image policy, route task report, decisions, TODO, results, and error logs.

### Results and interpretation

- The current graph is a verified final asset and a suitable mining/index substrate, but not a direction-correct action graph.
- Raw-to-road snapping was performed with geographic-degree projection; current route review remains usable, but formal freezing needs metric-CRS snapping and two decision-zone rechecks.
- Tile metadata heading is the absolute compass heading at the panorama tile center. ERP local `theta=0` therefore maps to `H`, not automatically north.
- Old UrbanNav 16-view inputs use FOV=60 degrees with 22.5-degree center spacing; current fixed four views use FOV=90 degrees and 90-degree center spacing.
- The first scientifically defined behavior task is learned-route continuation, so a correct edge is defined by the study phase rather than by an arbitrary mined route.
- Paris remains `provisional ADAPT`; human review is the next gate.

### Verification

- `validate_candidate_routes.py`: PASS for 12 main routes, 3 Arc controls, 120
  panos, 480 images, 120 heading joins, and 30 boards.
- All four audit JSON outputs parse; all 32 local review-guide links resolve.
- The human review CSV has 27 columns and 15 valid rows.
- Updated/new Python audit scripts pass `py_compile`.

## 2026-09-09 - Intermediate audit interpretation branch

### User task

- Explain what the Paris data audit means for the original landmarkness and
  cognitive-map research line.
- Separate what the machine audit proved from what still requires human judgment.
- Clarify what the human reviewer and Codex should do next.

### Work performed

- Applied the research-workflow evidence classification: verified, provisional,
  missing, and not yet scientifically defined.
- Wrote `AUDIT_INTERPRETATION.md` as a branch-level handoff document.
- Kept the current `Provisional ADAPT` status unchanged and did not start VLM,
  RL, or image intervention work.

### Result

The audit establishes technical feasibility and a reviewable candidate pool, not
functional landmark validity. Human review must freeze task-valid routes and
candidate strata before Codex generates route-aligned views or intervention data.

## 2026-09-24 - Pilot 0 scientific interpretation

### Work performed

- Read the final v2.2 server return from the uploaded Nav_Lmk archive and reconciled it with the local audit.
- Interpreted the 44-query P/N/I task, the DINOv2 G/14 plus urban VLAD pipeline, and the limits of the current retrieval score.
- Defined the next handoff as Qwen candidate proposals followed by matched-control region interventions; continuous-path route decisions remain a later functional test.

### Result

The baseline is technically reproducible and supports using the current task as a spatial-correspondence assay. It does not yet establish verified landmarks, cognitive-map formation, or route-choice utility. See `outputs/pilot0/SCIENCE_INTERPRETATION_20260924.md`.

## 2026-09-09 - Intermediate audit interpretation branch

### User task

- Explain what the Paris data audit means for the original landmarkness and
  cognitive-map research line.
- Separate what the machine audit proved from what still requires human judgment.
- Clarify what the human reviewer and Codex should do next.

### Work performed

- Applied the research-workflow evidence classification: verified, provisional,
  missing, and not yet scientifically defined.
- Wrote `AUDIT_INTERPRETATION.md` as a branch-level handoff document.
- Kept the current `Provisional ADAPT` status unchanged and did not start VLM,
  RL, or image intervention work.

### Result

The audit establishes technical feasibility and a reviewable candidate pool, not
functional landmark validity. Human review must freeze task-valid routes and
candidate strata before Codex generates route-aligned views or intervention data.

## 2026-09-09 - Intermediate audit interpretation branch

### User task

- Explain what the Paris data audit means for the original landmarkness and
  cognitive-map research line.
- Separate what the machine audit proved from what still requires human judgment.
- Clarify what the human reviewer and Codex should do next.

### Work performed

- Applied the research-workflow evidence classification: verified, provisional,
  missing, and not yet scientifically defined.
- Wrote `AUDIT_INTERPRETATION.md` as a branch-level handoff document.
- Kept the current `Provisional ADAPT` status unchanged and did not start VLM,
  RL, or image intervention work.

### Result

The audit establishes technical feasibility and a reviewable candidate pool, not
functional landmark validity. Human review must freeze task-valid routes and
candidate strata before Codex generates route-aligned views or intervention data.
