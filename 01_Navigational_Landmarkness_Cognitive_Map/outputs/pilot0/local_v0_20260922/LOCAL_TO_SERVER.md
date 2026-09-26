# 本地 → 服务器：paris_local_v0_20260922

交付状态：**DRAFT_PENDING_HUMAN_REVIEW**。2026-09-23，北京时间。

## 已完成

- 全量索引 3059 pano、12236 views；关联 3058 图节点、247 道路段。未关联图节点的 1 pano 保留在索引，未进入检索任务。
- 三个开发片区、六条道路、54 pano；48 query views、168 reference views。q/reference 不共享 pano。
- 8064 条完整关系：96 positive 候选、6720 几何 negative、1248 ignore。全部 `scoring_allowed=False`。
- 216 张选定 640×640 图像已读出、解码、哈希；图库 ID 由 reference IDs 与图像哈希确定，见 `task_manifest.json`。
- 132 对图像复核材料；Codex 预审识别 31 对优先项，但人工记录为空。原始图像不在轻量服务器 ZIP 中。
- 本地结构校验、审核回收门槛测试结果见 `validation_report.json`、`quality_checks.json`。

## 当前允许服务器开展的工作

以下文字可直接发给服务器 Codex：

> 请接续 Navigational Landmarkness 的局部地点辨识 Pilot 0。先读本任务包的 LOCAL_TO_SERVER.md、configs/protocol.json 和 task_manifest.json；用 package_manifest.json 验证轻量 ZIP 内容哈希。当前 `DRAFT_PENDING_HUMAN_REVIEW`，不允许运行或汇报正式 P/N/I 检索评分。
>
> 盘点已有 Python/CUDA/GPU、模型、词典及数据挂载，建立 paths.server.json，按 configs/paths.example.json 将 paris_fixed 映射到实际服务器目录，不猜测绝对路径。用 data/queries.csv 和 references.csv 内的 image_relative_path、image_sha256 核验选定图像。缺少图像时列出精确 ID 和路径，停止依赖图像的部分。
>
> 核验 AnyLoc/DINOv2 的准确模型、提取层、facet、VLAD 词典和预处理兼容性；讨论中的预定起点是 ViT-g/14、layer 31、value、32 clusters，640→448。核验后记录版本、权重/词典哈希和参数。旧 3059×384 pano 特征不可用作本次逐视图 patch 特征。
>
> 可用一张 query 和一张 reference 做特征提取与 VLAD 的最小连通性检查，返回实际 ID、shape、耗时、显存和数值有效性；不据此发表 retrieval metrics、调配对标签或启动批量 Qwen。等待本地提供人工复核后的新任务版本，再开启正式完整图基线。
>
> 将环境、paths.server 模板（不含凭据）、检查结果和问题写入 SERVER_TO_LOCAL.md。固定 view IDs，不自动合并类别。忽略项必须在排名前屏蔽；模型只能在已定义 N(q) 内找困难负例，不能按相似度自造标签。

## 人工复核之后

本地核对 96 个正例候选及 36 个边界/负例抽样记录，处理分歧，剔除没有合格正例的 query，保持固定 reference 图库并发布新版本。此时才允许正式基线。若改变图库则生成新 gallery_id，所有条件随同一版本重跑。

`task_manifest.json` 的哈希用于本草案溯源，**不是已冻结科学协议的证明**。源全量索引保留未读像素的历史尺寸状态，只有选定 216 张是本轮解码核验。

## 轻量包范围

包含清单、P/N/I、路径模板、规则、校验/预审记录和本次新增脚本。排除街景像素、ERP、模型、特征、大型历史资料、原始聊天和 paths.local.json；没有自动上传 GitHub，也未创建 remote。

服务器可检查包内文件 SHA-256 和自身图像根目录。`pilot0_validate.py` 的全量本地检查还依赖本地 sources 缓存、全部复核卡片和原图缓存；这些不在轻量包内，不能直接把该检查成功当作服务器收包前提。服务器依照上面约定单独验证收包及图像映射。

本地完整复现命令见 REPRODUCE.md；项目总体实验步骤及正式基线指令见项目根目录的 PILOT0_EXECUTION_PLAN.md、SERVER_CODEX_HANDOFF_PILOT0.md。
