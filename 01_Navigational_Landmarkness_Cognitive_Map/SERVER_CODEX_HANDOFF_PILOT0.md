# 服务器 Codex 交接：Pilot 0

日期：2026-09-22  
状态：可复制的分阶段任务说明。尚未发送给服务器、建立 GitHub remote 或运行 GPU 实验。

2026-09-24最新交付：人审132项已回收；SharePoint词典入口404后，找到AnyLoc官方GitHub Release v1中的独立匹配urban中心，并将固定URL/SHA下载验证写入 outputs/pilot0/reviewed_v1_20260923/server_baseline_package_v2_2_final_20260924.zip。请使用该最终包，再按包内 SERVER_PREPARATION_V2.md 执行。用户无需手动下载VLAD词典；服务器脚本会自动下载并用PyTorch验证[32,1536]。当前题库仍为44query/168reference、82P/6160N/1150I；原图、G/14大权重、词典和特征不在ZIP内，服务器需自行处理。正文下方A–G是早期规划，实际操作以最新包内v2执行合同为准。

## 使用方式与角色

本地负责源数据索引、空间配对、空间分组、人工复核材料和协议维护。服务器负责环境／模型核验、特征提取、基线、Qwen 候选和批量干预。两端共享代码与版本化的轻量任务数据。

先读 PILOT0_EXECUTION_PLAN.md。当前任务是局部地点辨识的功能证据 Pilot 0；原 P1A/P1B 的路线人审 gate 不应用于此任务。计划里尚未冻结的距离、样本量和 masking 参数不能被默认为已定实验标准。

下列文件／命令接口是预定交接约定，并不声称当前已有对应 pipeline 实现。缺少本地任务包时，服务器可以准备环境和实现接口，但不能自造真实正负标签。

## A. 两端共同的任务包

建议项目相对路径：
- data/pilot0/view_manifest.csv
- data/pilot0/queries.csv
- data/pilot0/references.csv
- data/pilot0/retrieval_pairs.csv
- data/pilot0/spatial_splits.csv
- data/pilot0/pair_audit.csv
- configs/pilot0/protocol.yaml
- configs/paths.example.yaml
- handoff/LOCAL_TO_SERVER.md
- handoff/manifest.json

文件格式可在实现时统一调整，但 view_id、关系语义和版本引用必须保持一致。不要把文件名存在当成已审核完成。

handoff/manifest.json 应记录：
- protocol_version、dataset_version、gallery_id；
- 各输入文件 SHA-256、源 heading CSV 哈希、选中图像哈希或其核验状态；
- 本地与服务器代码 commit；
- split 状态、pair 规则、已复核／仅规则生成数量、未决事项；
- 当前允许运行的阶段，以及本次运行的 query 范围。

路径采用根目录别名加相对路径。服务器填写自己的数据根目录，不在共享 CSV 中批量替换为猜测的 /home 路径。大型图像、模型和 cache 不通过 GitHub 传输。

## B. 首次发给服务器的指令

下面这段可直接复制：

> 请接手 Navigational Landmarkness 项目的 Pilot 0。先读取项目 AGENTS.md、PILOT0_EXECUTION_PLAN.md、SERVER_CODEX_HANDOFF_PILOT0.md、最新 TODO/DECISIONS 和 handoff/LOCAL_TO_SERVER.md。当前目标是建立 DINOv2+VLAD 完整图局部地点检索基线，用于以后测量候选视觉区域的贡献。
>
> 1. 先盘点仓库、Python/CUDA/GPU、现有模型与数据挂载；记录环境和实际路径，不扫描无关目录。检查本地交付的 manifest、P/N/I、query/reference 和 split 文件及哈希。没有真实任务包时，仅完成环境与接口准备，并明确列出缺失项。
> 2. 按 root_key + relative_path 映射图像。核验 view_id 唯一、pano 与四视角关系、图像尺寸、绝对 heading 字段、空间组、query 自身／同 pano 排除、P/N/I 互斥与覆盖。每个可评分 query 至少有一个 positive 和一个 negative。未标关系作为 ignore，不自动判 negative。
> 3. 依据官方实现核验聊天预定的 AnyLoc 配置：DINOv2 ViT-g/14、layer 31、value、32-cluster urban vocabulary。记录仓库 commit、模型 revision、词典和权重 hash、预处理、精度与归一化。若配置不兼容或资源不足，明确报告原因和最小替代方案，不静默更换，也不要把不同配置放进同一结果表冒充同一实验。
> 4. 先在本地交付的少量 dev views 上打通 640 原图到预定 448 输入、局部特征、VLAD、检索的 smoke test；记录耗时、显存和输出 shape。旧 3059×384 pano embedding 不能作为逐 view patch cache 使用。
> 5. 在版本化的 dev query/reference 上跑完整图基线。固定图库、词典和标签；对每个 query 屏蔽 ignore 后评分。保存 Recall@1/5、S_pos、S_neg、margin、top_positive_id、top_negative_id、有效图库大小、正例数、错误／无效原因及检索排名。
> 6. 从已经定义为 negative 的 reference 中输出相似度最高的若干项供本地审计；不按模型相似度重写空间标签。每次比较仍以完整固定 N(q) 求最大负例分数。
> 7. 实现最小校验：相同输入重复运行的一致性、baseline 与空干预的一致性、坐标映射、ignore 屏蔽、同 pano 排除、缺失正例／负例报错、词典兼容性、reference 未被修改。记录容差和失败原因，不能用零分吞掉缺失数据。
> 8. 返回结果和可复现命令。本阶段不批量运行 Qwen，不训练模型，也不进行候选干预。基线数值高低不作为任意改题以追求 60%–90% 准确率的理由。

本阶段建议返回：
- handoff/SERVER_TO_LOCAL.md：运行版本、输入哈希、已完成事项、阻塞项、下一步；
- outputs/pilot0/<run_id>/run_config.json、environment.txt、validation.json；
- baseline_summary.json、baseline_per_query.csv、retrieval_rankings.jsonl；
- hard_negative_review.csv、missing_or_invalid.csv、run.log；
- 少量成功／失败案例的 ID 与图板路径。

本地收到结果后，在 dev 上检查“错标／任务歧义”与“真实视觉混淆”。若需要修订标签或配对规则，生成新版本，并重跑完整图基线；不能只修改有利于后续效应的题。

## C. 基线与任务检查完成后的候选指令

> 延续同一 Pilot 0 任务版本。部署并核验用户选定的 Qwen3.5-9B 的准确 model ID、revision 与图像处理合同，先在 dev 小样本检查，再批量处理指定 query。
>
> 每次只看当前 640×640 单视图，输出结构化候选：candidate_id、view_id、bbox、bbox_coordinate_system、type、description、hypothesized_role。保存原始输出、prompt、推理参数与模型版本。
>
> 不提供正确 reference、GPS、正负标签、检索成绩或未来路线。hypothesized_role 是候选解释，不用作功能分数。
>
> 先返回可见性与框位置审计包：越界、空框、重复框、格式异常、无候选都需显式记录。不要因为模型说重要就标注为 verified landmark。
>
> 将 bbox 统一到可追溯坐标格式，保存原始数值及变换；生成 640/448/patch-grid 对齐示例供本地核对。候选数量、重叠及去重规则在 dev 确定后冻结。

## D. Descriptor 干预指令

> 在固定任务、图库、词典和候选版本上，按本地已确认的规则产生每个候选的多个 matched regions。
>
> 优先匹配实际 patch 数、形状和粗略垂直位置；保存匹配误差、重叠与可用性。无合格对照标记 no_valid_control，不填任意区域。
>
> 跑 full、drop_candidate、keep_candidate、drop_control、keep_control。descriptor removal 真删对应行；每个条件用同一词典重新 assignment、残差聚合与归一化。不能把特征置零当删除，不能从最终归一化向量减去局部贡献。
>
> keep_descriptor 只解释为保留特定位置的上下文化描述子。所有条件只修改 query，reference 特征与 P/N/I 固定。干预后从全部固定 negatives 重新找最高分者。
>
> 对空 patch 集、全图删除、退化向量等情况明确报 invalid，不用 fallback 0 冒充有效效应。保存 candidate/control、patch indices、条件、S_pos/S_neg/margin、top IDs、配置与输入 hash。
>
> 同时给出 Δ_drop、U_drop、U_keep 和原始指标，不按单一正效应筛选“成功地标”。

## E. 输入干预与复核指令

> 按预先记录的 high/mid/low 加 random 抽样规则，选定一批候选做 input drop/keep。保留零效应与负效应，不只测试 descriptor 表现最好的候选。
>
> 首版使用同一 deterministic mask/fill 规则处理 candidate 与 controls；保留原画布和空间尺度，禁止裁剪候选再放大冒充 input retention。记录 mask 值、边界、seed、图像处理顺序与 hash。
>
> 重新执行完整 DINO→VLAD→retrieval 流程；不是复用原图局部特征作为输入干预结果。reference 和标签不变。
>
> 返回两层干预的逐候选结果和操纵图板。两层不一致只提出待检验机制；不能直接断言注意力传播或完整因果关系。若后续增加第二种遮挡或 inpainting，作为单独 robustness 配置，所有对照等同处理。
>
> 在 dev 完成调试后冻结代码／配置，再运行可行的 Paris eval。统计按 pano 或 spatial_group 处理相关性。多个 controls 不是多个独立候选。外部 Trafalgar 数据核验完成后另建确认运行，不能临时调参后仍称完全冻结复现。

## F. GitHub 中转约定

当前工作区不是 Git 仓库，目标 remote 未提供。本轮只准备交接文件，不创建／推送仓库。

接通实际仓库后：
1. 先确定一个共享协议和分支约定，例如 local/pilot0-task 与 server/pilot0-baseline；具体名称可调整。
2. 本地提交 schema、配置模板、代码与小型清单／审计数据，服务器以明确 commit 和任务包 hash 开始运行。
3. 两端每次开始均先 fetch、检查工作树，再基于约定版本工作；不能用自动 reset --hard 或 force-push 覆盖对方修改。
4. 服务器在自己的分支提交实现与紧凑结果，通过 PR／merge 同步；原始大结果、patch cache、权重只返回服务器路径和校验信息。
5. 本地审查结果、修订 dev 任务时递增版本；评估阶段发现的问题按预设协议报告，不偷偷改测试集。
6. 以 handoff/LOCAL_TO_SERVER.md 和 handoff/SERVER_TO_LOCAL.md 记录：目标 commit、输入版本、执行范围、结果、问题和下一条命令。两位 Codex 通过这些文件接续，不假设自动共享会话或持续在线。

准备仓库时使用文件白名单。不要上传 Z 盘图像、ERP、模型权重、大数组、完整聊天 HTML、历史凭据或无关旧项目。

## G. 停留在本地即可开展的下一步

当前已经知道原始路径和关键数据关系，Z: 的路径限定读取也已验证。本地可以先交付：
1. 全量 view manifest 与可用性摘要；
2. 少量 dev 空间组及 P/N/I 候选对；
3. 用于核对配对的图板、理由与审核表；
4. 版本化 queries/references/pairs/config 任务包。

上述准备不需要先跑 Qwen，也不需要修复旧 UrbanNav／RL。GitHub remote 与服务器根路径会在实际传输前补齐。
