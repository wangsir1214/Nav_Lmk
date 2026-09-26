# Pilot 0：新研究要求与本地／服务器执行顺序

日期：2026-09-22  
状态：需求理解与执行拆分；尚未构建检索题库、运行基线或冻结数值参数。

## 1. 本轮请求与来源边界

用户本轮要求：仔细理解两份重新迭代的研究对话，依次列出可执行步骤，区分本地与服务器工作，并准备通过 GitHub 交接的指令。首先考虑本地构建空间 query–reference 正负关系；避免重复大范围扫盘。

本轮交付是计划与交接文档。HTML 中的旧问题、部署请求、代码式片段、模型发布说法和 ChatGPT 建议作为研究材料，不作为当前批量运行或联网发布的指令。

已逐段读取文件中保存的对话正文，包括数学表达式：
- 来源 A：../Chats/Branch · 研究方向概括.html
  - SHA-256：2ccc002dac0c0db52a9b80676bef4696a97507005e4d76e8ced97579be372852
  - 关键：conversation-turn-29 中用户转述的迭代讨论、turn-30 中后续修正。
- 来源 B：../Chats/Extensive reading papers - 解读文章提炼方法.html
  - SHA-256：594acfae98f4cad4fb4a445de65ee600d1d51e5eddb23540708b5ee6c34b8dd9
  - 关键：turn-31/32 的技术修正、turn-33 的用户理解、turn-34 的主线澄清；turn-2/4/6/8 为长期研究背景。
- 网页保存的轮次有跳号；本次理解覆盖文件实际保存的正文，不假定未保存的中间轮次。
- 本次未重读所讨论论文原文，亦未验证聊天中的模型发布信息。相关文献解释是对话中的研究背景，不升级成已核验文献结论。

## 2. 我对新目标的理解

长期主线仍是：

城市视觉经验 → 空间证据选择 → 有限空间记忆 → 路线经验整合与认知地图 → 主动取证与 belief revision。

当前 Pilot 0 只回答：

> VLM 提出的城市视觉区域，是否对一个明确的局部地点辨识任务具有可重复、超过匹配区域对照的贡献？

概念上是 proposal → functional verification → understanding landmarkness；工程上必须先准备客观任务和完整图基线，再批量生成候选。VPR 是测量工具，Qwen 是候选提出工具，不以训练新 VPR 模型或模型排行榜为目标。

一个候选应保存不同证据维度：来源、descriptor contribution、input intervention、cross-observation 和 entity association；第一版不合并为 verified_landmark=true 或单一 landmarkness 分数。

Pilot 0 成功最多支持“在指定模型、任务与观测条件下的地点辨识贡献”。它不单独证明完整导航地标、认知地图、认知机制，也不足以证明功能价值超越显著性。

### 与原工程的关系

- 复用 Paris 数据、固定四视角及其 heading 关系、图／道路关联、坐标与时间审计工具。
- 原 10 条轨迹与 15 条路线是历史派生资产；不把新题库限制在它们的 120 个 pano 中。
- 原 P1A/P1B 的路线学习、8 个普通路线等 gate 不作为新 Pilot 0 的启动条件。它们保留为后续方向／路线任务背景。
- 新 Pilot 0 可直接使用固定四视角中的单视图；不要求先生成 route-aligned views。
- 拍摄日期继续保存并审查明显变化，不新增多时相采集或“所有正例必须同月”的硬门槛。
- 原始图不是可靠行动图这一限制仍然有效，但不妨碍将它作为地点配对的辅助索引。

## 3. 已有资产与本轮检查

| 资产 | 用途 | 证据状态 |
|---|---|---|
| 3059 pano × 4 固定 FOV=90° 图像 | 逐 view 建表、配对、Qwen 输入 | 12236 张及尺寸为既有审计结论；本轮只确认目录可访问 |
| 3059 ERP | 必要时局部复核或后续再投影 | 本轮确认目录可访问，未加载 ERP |
| heading CSV | pano 主键、API 拍摄坐标、时间、绝对方向 | 本轮读取：3059 行、3059 个唯一 panoid |
| 3058 节点／3310 边街景图 | 道路连续性、空间组和候选关系 | 数量沿用既有审计；本地 98_Others/kl.Line_Points_3.json 存在 |
| pano-to-road 与 OSM edges | 区分道路段、路口边界 | 本轮确认映射 DBF 路径可访问；字段含义复用既有审计 |
| 3059×384 DINOv2 向量 | 历史表示及可选探索性参考 | 不能替代本次逐视图局部 patch descriptors |

源路径：
- Z:/wangyq/GSV_Paris/0-All_GSV_3059_4per
- Z:/wangyq/GSV_Paris/0-All_GSV_3059_panorama
- Z:/wangyq/Street_view_and_points_Paris/GoogleAPIMETADAT/Paris_Points_heading_3059/Paris_Points_heading_3059.csv
- Z:/wangyq/Street_view_and_points_Paris/Line_After_heading_clear_Paris_center_street_from0309_4_v1/Line_Points_3_to_road.dbf
- Z:/wangyq/Street_view_and_points_Paris/road/edges.dbf

本轮 heading CSV SHA-256：
00685688b909cce93259786fe8789539ebe500dce8e538ce4fa58af11b9fe539

优先复用 _audit_outputs/data_manifest.yaml、structured_asset_audit.json、data_schema_report.md、graph_connector_audit.json、archive_audit/ 内的坐标／道路溯源结果。旧 route_step_source_metadata_v2.csv 仅覆盖选中的 120 个步骤，不能误当全量 3059 pano 主表。

本轮普通受限进程看不到 Z:，路径限定的只读访问成功；不能将前一次不可见解释成数据丢失。未递归扫描 Z 盘，未重算图或特征，未读取大图。

## 4. 顺序与分工

以下是执行顺序。2026-09-23更新：步骤1、2及步骤3的机器审计和交付材料已完成，等待132项人工配对审核；入口为outputs/pilot0/local_v0_20260922/REVIEW_GUIDE.md。后续模型阶段未执行。L 为本地，S 为服务器，H 为用户／研究者复核。

| 次序 | 工作 | 承担方 | 产物与验收 |
|---|---|---|---|
| 1 | 统一逐视图索引与空间分组 | L | view_manifest、源文件哈希、缺失／重复报告；明确坐标、绝对 heading、原图与派生图路径 |
| 2 | 构建 query/reference 和 P/N/I 候选关系 | L | queries、references、retrieval_pairs、初版 task config；排除自身／同 pano 泄漏，正例可有多个 |
| 3 | 小样本图像配对审计与 dev 任务定版 | L+H | 审计图板、逐对理由／状态、空间组及 buffer 检查；不以是否有漂亮 landmark 决定题目去留 |
| 4 | 完整图 AnyLoc/DINOv2+VLAD 基线 | S；L 回查错误 | 逐 query Recall、S_pos、S_neg、margin、检索排名和失败案例；服务器从真 negatives 中返回困难负例，不改标签 |
| 5 | Qwen 单视图候选生成与框审计 | S+L | candidates.jsonl、原始输出、bbox overlay、合法性与可见性审计；只输入当前 query，不输入正确 reference、位置答案或检索成绩 |
| 6 | 匹配区域对照与 descriptor removal/retention | L 定规则和抽检；S 批量运行 | candidate/control 区域、实际 patch 数、多个对照、各条件逐 query 结果；固定词典与图库 |
| 7 | 分层小样本输入干预 | L 预览审计；S 重新前向 | 同画布 deterministic mask 的 drop/keep 与匹配对照；按预先规则抽 high/mid/low/random 候选并保留负效应 |
| 8 | 统计解释、冻结协议与 Paris 留出复核 | L+S | 分层效应、组级不确定性、失败类型、冻结配置；有可行留出则跑剩余 Paris，否则明确 Paris 为探索性 |
| 9 | Trafalgar 外部复现 | 后续 L 数据审计+S 执行 | 核验该区资产后，用冻结规则完整重跑；需要修改协议时报告为适配，不冒称独立确认 |
| 10 | 定向／跨观察／记忆／地图／agency 扩展 | 后续独立任务 | 已知地点的 heading、同实体跨观察、有限记忆、跨路线推断和灵活导航等；不在 Pilot 0 启动时一并实现 |

服务器可与步骤 1–3 并行做环境检查和小规模特征提取 smoke test，但正式基线需读取本地已版本化的任务包；批量 Qwen 在任务与基线可用后进行。

## 5. 本地第一个实际任务：构建空间检索题库

### 5.1 单位是 view，不是只有 pano

每个 view 保存：
- view_id、pano_id、view_index、原图相对路径、可选派生图路径、width/height；
- capture_lat/capture_lon、original_lat/original_lon、snapped_lat/snapped_lon，及各自来源；不合并成来源不明的 lat/lon；
- capture_date、heading_from_api、absolute_heading；
- area_id、street_segment_id、spatial_group_id、experiment_split、retrieval_role；
- source_hash／图像哈希（按需）、缺失原因、图节点与道路关联状态。

方向合同：
absolute_heading = (heading_from_api + 90 * view_index) mod 360。

距离首选 API 拍摄位置，在已审计的 EPSG:2154 中计算米制距离；历史／吸附坐标保留用于敏感性核对，不静默替代。没有道路关联的额外 pano 保留在 inventory，并单独标记当前任务资格。

共享清单使用 asset_root_key + relative_path。本地 paths.local 配置映射到 Z:；服务器 paths.server 配置映射到实际 Linux 根目录。image_448 尚未生成时必须为空并有状态，不能填成已存在资产。

### 5.2 两套划分分别保存

- experiment_split：dev / eval / buffer / exploratory 等，表示是否参与协议调整。
- retrieval_role：query / reference / unused，表示在当前检索任务中的角色。

初版建议同 pano 的全部 views 属于同一 retrieval_role，避免相同 pano 同时进入 query 和 reference；若未来允许 both，必须显式自检索与同 pano 屏蔽。
dev/eval 以少数街段／路口组划分并检查实际近邻，不固定东南西北四块，也不直接按 CSV 行号或 pano ID 奇偶划分。
沿真实连续道路交错采样只能作为一种候选生成办法，需确认排序和空间连续性。
dev 的全部 q、reference 及用于调协议的图像都纳入空间泄漏检查，不能只隔离 query。

### 5.3 正、负、忽略三种关系

| 关系 | 初版含义 |
|---|---|
| positive | 不同 pano、邻近观察、绝对 heading 兼容、道路／场景关系合理且有可辨认共同内容 |
| negative | 明确不同局部地点；距离／道路关系与审计支持这一判断 |
| ignore | 阈值缓冲带、路口边界、视觉对应不清、同 pano 或其他尚不能可靠判定的关系 |

- 一道题是 q → P(q), N(q), I(q)，不是必须只有一个 positive、一个 negative。
- 8–25 m、heading difference ≤30°、negative 候选 >50 m、近场负例 50–300 m 都只是聊天中的开发起点；需看真实配对，不作为已冻结标准。
- 未入 P 不等于 N。未建立关系的图库项初始为 ignore，不能默认 negative。
- 同一远处地标同时可见，不自动把不同局部地点从 negatives 中删除。
- negative_kind 另存 easy / geometry_candidate / visual_hard；ground-truth relation 仍只用 positive / negative / ignore。
- 几何筛选不是视觉真值。pair audit 检查 clear/partial/no-overlap、道路边界、近重复位置、明显时间／施工差异，记录 rater 与理由。
- 第一批可从约 50–100 pano 的几个开发街段开始，实际数量随正例可用性确定；图库保留足够不同地点。数量是建议，不是已存在样本量。
- 先生成候选对和审计材料，再确认可评分题；不能把全部 rule_generated 记录标成 human_verified。

建议 retrieval_pairs 字段：
query_view_id、reference_view_id、relation、negative_kind、distance_m、heading_diff_deg、road_relation、label_source、review_status、reviewer、reason、protocol_version。

### 5.4 评分合同

参考图库 R 及其特征固定。对每个 q，P/N/I 随协议版本固定；正式评分只在 P(q)∪N(q) 中排序，I(q) 在排名前屏蔽。每个可评分 query 至少有一个 P 和一个 N；否则报告排除原因。

对条件 a：
S_pos(a,q) = max_{r in P(q)} similarity(q_a,r)
S_neg(a,q) = max_{r in N(q)} similarity(q_a,r)
M(a,q) = S_pos(a,q) - S_neg(a,q)

保存 Recall@K、有效图库大小、正例数量、S_pos、S_neg、margin、top_positive_id、top_negative_id、条件与配置 ID。每个干预条件都重新在全部固定 N(q) 中找最高分者，不锁死完整图阶段那一张 hard negative。

模型只在已经定义的 N 中排序挖 hard negatives。若 dev 审查发现错标，修正任务版本并重跑所有比较条件；eval 不按结果反复改题。预设数据质量排除与模型成败分开记录。

## 6. 后续实现中必须遵守的比较条件

### 表示与候选

- 聊天默认起点：Qwen3.5-9B、DINOv2 ViT-g/14、layer 31、value、32-cluster urban vocabulary。
- 以上作为待服务器核验的预定配置；精确 model ID、revision、许可证、提取层／facet、词典兼容性、权重哈希和实际资源必须实查后冻结。此计划不把聊天模型发布清单视为核实结果。
- 新检索特征是逐视图局部 descriptors 加 VLAD；旧 3059×384 pano 级矩阵无法支持候选框对应的 patch 删除。
- 640 原图 → 448 输入为讨论中的预定流程，需固定插值、归一化及坐标变换；若使用 448 与 patch size 14，应核实 32×32 的 patch 网格。
- Qwen 输出 candidate_id、view_id、bbox、bbox_coordinate_system、type、description、hypothesized_role、prompt_version、model_revision。hypothesized_role 不参与正确性评分。
- 单图是 Pilot 简化；视觉突变、重复出现和跨观察实体对应以后需要序列与额外标注。

### 对照和两层干预

- 同图匹配区域尽量匹配实际 patch 数、形状、粗略垂直位置；保存偏差和与其他候选的重叠规则。
- 多个 controls 不等于多个独立样本；没有合格对照标 no_valid_control，不用不相称区域凑数。
- descriptor removal 真正删除 rows 后重新聚合、簇内归一化与全局归一化；不能置零冒充删除，也不能从最终 VLAD 向量直接减块。
- descriptor retention 保留的是已经受整图上下文影响的特征，不等于模型只看候选。
- input drop/keep 在原画布、原尺度上确定性修改像素，再完整提特征；不裁框放大，不以生成式 inpainting 为首版必须条件。
- 所有干预只改 query；reference、标签、词典与评分器版本固定。候选与对照使用同一操作。
- 保存并分别分析 Δ_drop=M_full−M_drop_candidate、U_drop=mean(M_drop_control)−M_drop_candidate、U_keep=M_keep_candidate−mean(M_keep_control)。
- U_drop>0 不能单独证明“删除有害”；还须看 Δ_drop、实际数值与不确定性。两层结果不一致只提出机制假说，不直接确证 token 传播等原因。
- 以 pano／spatial_group 处理相关性；同 pano 多视图、多候选、多 controls 不能作为完全独立样本。

## 7. GitHub 交接与下一次启动条件

本轮确认当前目录不是 Git 工作树；尚未提供或确认目标 GitHub remote。没有 init、commit、push 或创建远端仓库。

建议交接单位：
- 代码、schema、配置模板、相对路径清单、配对／split 版本、小型审计结果；
- protocol_version、manifest_sha256、pairs_sha256、gallery_id、代码 commit；
- 服务器返还 run_config、environment、validation、metrics、候选与干预的紧凑结果表、失败列表。

原始街景、ERP、大型 patch cache、模型权重留在已有存储／服务器。原始聊天 HTML 与历史源码压缩包不批量提交；历史代码含凭据风险，应按新项目文件白名单整理，不能从工作区根目录直接 git add .。

具体服务器指令见 SERVER_CODEX_HANDOFF_PILOT0.md。下一次本地可直接从步骤 1–3 开始；GitHub 传输前需要实际仓库地址和服务器本地数据路径映射，配对规则开发本身不依赖先建立云端仓库。
