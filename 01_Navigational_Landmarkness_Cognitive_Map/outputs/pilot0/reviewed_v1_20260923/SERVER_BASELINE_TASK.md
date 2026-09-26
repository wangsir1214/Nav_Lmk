# 给服务器 Codex：Pilot 0 完整图 DINOv2+VLAD baseline

**路径映射、真实文件名、权重/词典下载、全量448 PNG预处理及可执行代码以同目录`SERVER_PREPARATION_V2.md`为准。** 本文原始v1描述了“归一化tensor后torchvision resize”；v2改成全量离线Pillow448 PNG，再tensor归一化。不要混用两套预处理或特征。人审题库与评分定义不变。

**路径映射、真实文件名、权重/词典下载、全量448 PNG预处理及可执行代码以同目录`SERVER_PREPARATION_V2.md`为准。** 本文原始v1描述了“归一化tensor后torchvision resize”；v2改成全量离线Pillow448 PNG，再tensor归一化。不要混用两套预处理或特征。人审题库与评分定义不变。

## 本次目标与输入

请在服务器运行paris_local_v1_20260923开发集的完整图局部地点检索基线。先读REVIEW_ACCEPTANCE.md、task_manifest.json、configs/protocol.json及configs/baseline_request.json。确认包哈希，再使用data/queries.csv、references.csv、retrieval_pairs.csv。

本地已完成132对人审和分歧整理：44query、168reference、82P/6160N/1150I，完整关系7392行。请使用新版本，不要使用v0的48query草案。图像只需212张，不需要全量12236张重新提特征。此阶段不训练DINOv2，不批量Qwen，不做区域干预。

## 第一步：服务器资源与版本

1. 盘点实际工作目录、GPU显存、CUDA/PyTorch/torchvision/xformers、已存在模型和AnyLoc代码。记录代码commit、完整依赖版本、GPU型号、dtype、随机种子42和确定性设置。不预设服务器路径或容器名称。
2. 建立本地paths.server.json，将paris_fixed映射到固定640视图目录；按image_relative_path拼路径。review_image只是原本地审核缓存路径，不是服务器输入路径。逐一核验212张的image_sha256，不能用同名但经过重新压缩的图静默替代。
3. 加载官方标准dinov2_vitg14（非register版本、patch14）权重，保存来源及SHA-256。使用strict load；输出missing/unexpected keys。服务器若已有兼容固定版本可复用，但需记录实际commit并检查结构/提取位置，不直接torch.hub跟随main漂移。
4. 加载匹配的32-cluster urban词典，预期中心形状[32,1536]，记录SHA-256和来源。官方demo目录约定cache/vocabulary/dinov2_vitg14/l31_value_c32/urban/c_centers.pt；README有c_center.pt的拼写差异，以实际文件和代码加载检查为准。
5. 不在这44query或潜在eval上重新fit词典。缺词典先取得官方兼容预训练词典；若确需自建，应先提出独立训练数据、抽样和新的baseline配置，不静默替代。

## 第二步：固定预处理和特征合同

本项目选择640×640→448×448。448是当前实验设计，不是G/14模型唯一允许尺寸。输入为单张固定FOV90视图，不拼四视图，不重投影，不做随机增强，不裁框放大。

固定顺序：PIL读取并convert RGB → torchvision ToTensor到[0,1] → ImageNet Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225]) → torchvision functional.resize到[448,448]，BICUBIC、antialias=True。这遵循本次核对的AnyLoc demo先归一化再resize的顺序；显式固定antialias避免torchvision默认变化。448已可被14整除，不执行改变视野的裁剪。原640图不覆盖，448图无需另存JPEG后再次读入；可保存无损PNG供少量QA，模型直接使用固定tensor。

提取标准G/14的blocks[31].attn.qkv输出中的value分量（零起始索引31，即第32个block）；不把最终CLS向量或最终block patch token当作同一配置。排除CLS，模型无register tokens，逐patch L2归一化。预期每图[1024,1536]，空间网格32×32，保留row-major顺序和patch坐标，方便后续bbox与patch干预。

聚合采用AnyLoc匹配实现：归一化局部描述子、cosine距离的hard assignment到32中心、每簇残差求和、簇内L2，再拼接并全局L2。不额外做PCA、signed square root或量化；若未来增加则另立配置。预期每图49152维（32×1536）。DINO前向和VLAD/相似度计算第一轮用float32、batch1或小batch，固定TF32开关并记录。若资源要求混合精度，先比较少量同图FP32/混合精度的向量差异、分数和排名，再明确冻结新dtype，不能悄悄混用。

官方demo的DINO提取器内部torch.hub.load不固定revision，需要改为本地固定源码/权重加载或明确固定引用；记录这项工程修改。本地核验是源码文本检查，没有替服务器完成权重、CUDA或真实前向验证。

## 第三步：先连通性检查再提取全量活动图

先用1query+1reference做端到端检查：解码640、tensor[1,3,448,448]、patch[1,1024,1536]、centers[32,1536]、VLAD[49152]；均为有限数值，最终向量非零且L2范数约1（FP32误差≤1e-5）。同图重复前向向量/分数误差建议≤1e-5，超出须说明硬件与实现原因，不能直接放宽后不记录。

通过后提取全部212图：query描述子44行、reference描述子168行，显式保存view_id顺序。不依赖文件名自然排序猜测行对应关系。至少缓存44query的1024×1536局部特征及patch网格、固定reference VLAD，便于后续干预；212图全patch缓存FP32约1.24GiB，可留服务器，不经GitHub。无需保存[patch,cluster,dim]完整残差大张量作为常规产物。

## 第四步：检索和评分

对于L2归一化VLAD，点积即cosine similarity。先保存44×168原始分数矩阵及其行/列ID；每query根据本任务版本屏蔽I，再仅在P∪N中排序。

- P有1–3个，N固定140个；有效图库141–143，不能把168全当作可评分图库。
- q与reference不共享pano；全部相同pano禁止参与检索。缺P或N、缺图、NaN/零向量均报错，不以0分吞掉。
- 排名按float32分数降序、reference_view_id升序打破精确平局；保存tie_count。接近零的margin需连同数值误差解读。
- Recall@K定义为前K是否命中至少一个P（检索success@K约定，不是取回所有P的比例）。报告K=1/5/10，及最优P的排名；可附MRR。
- S_pos(q)=max_{r∈P(q)}s(q,r)，S_neg(q)=max_{r∈N(q)}s(q,r)，M(q)=S_pos−S_neg。M>0表示最佳P严格超过全部N；平局时M=0，需结合固定tie规则看Recall@1。
- 挖hard negatives只能在固定N内取top5，携带distance、heading、road/group、日期和原有标签来源。不得将ignore放进N。
- 同一批特征追加边界敏感性：R123/R125从P改I，保持相同44query与reference，80P；不重新训练或提取。

最小评分测试：最高分I不进入排名；多个P取max；没有P/N报错；相同pano拦截；ID重复/错位拦截；已知分数fixture能得到预期Recall/margin；精确平局行为确定。baseline与后续空干预将使用相同评分器。

## 返回哪些结果

| 文件 | 必须包含 |
|---|---|
| run_config.json、environment.txt、validation.json、run.log | 任务/图库/代码/模型/词典哈希，所有预处理与精度设置，样例shape、范数、重复性、耗时、峰值显存 |
| baseline_per_query.csv | 44行；query/pano/道路组/片区；P/N/I数量；top1 ID/关系；best_positive_rank；Recall@1/5/10；S_pos/S_neg/margin；top_positive_id/top_negative_id；无效或平局原因 |
| baseline_summary.json | 成功数/44和百分比；总体与每道路组/片区结果；每pano汇总；margin中位数/IQR/范围；有效query数与排除表引用 |
| pair_scores.csv 或 scores.npy + score_ids.json | 全7392个未屏蔽分数与对应ID，relation、scoring_allowed，便于本地复算；不得只保存top1 |
| retrieval_rankings.jsonl | 每query可评分项目完整顺序和分数；I可另存diagnostic字段，不能混进正式rank |
| hard_negative_review.csv | 每query固定N内top5，分数、距离、组别、朝向与日期；不更改标签 |
| boundary_sensitivity_per_query.csv、boundary_sensitivity_summary.json | 主82P与保守80P相同query下的结果差异 |
| failure_cases/ 和 case_index.csv | 全部失败与低margin例，配query、最佳P、top负例，附ID/分数/日期；若全成功仍展示最低margin与高相似N |
| feature_index.csv | view_id、原图hash、特征路径/hash、shape、dtype、patch顺序和配置ID；大型cache只返服务器路径 |
| SERVER_TO_LOCAL.md | 实际执行命令、产物路径、完成/异常、解释边界、下一步建议 |

成功案例可按事先确定的ID抽少量，每组至少1例且注明若该组无成功。不得只展示漂亮成功图，不要求baseline达到某个预设准确率。

## 收到结果后如何分析

1. 先判技术正确性：完整212图、44个有效query、hash/shape/归一化/ignore屏蔽/ID顺序正确。模型高分不能抵消标签泄漏或词典不兼容。
2. 再看任务能否形成测量尺度：Recall说明整图能否找对；margin区分强正例、接近混淆与被负例超过的题。高Recall不必然没有干预空间；若margin也很大，则应报告这批任务偏容易，后续在新任务版本中增加难例，不能事后删掉容易题制造效应。低Recall先分清实现问题、标注歧义和真实混淆。
3. 看分层和失败：三个片区、六道路、12query pano；正例clear/partial、拍摄月份差、近场负例与重复立面。日期差/重叠是pair属性，统计时注明使用最优正例还是全部正例。不要按model top_positive选择后把它当成独立样本作显著性推断。
4. 统计以44query作描述性分母，同时给12pano与6道路/3片区汇总；这些视图相关，7392pair更不是7392独立样本。三个片区不足以支持稳健城市外推；首轮优先报告组间差异/逐pano原始值，不把窄bootstrap区间当强证据。以后冻结更大空间留出再检验泛化。
5. 核对边界敏感性。R123/R125纳入与否若只改变2个query的细节，直接报告；若影响解释，保留两套结果说明，不挑更好看的口径。
6. 在错标/任务边界与技术问题处理后固定full-image基线，才能进入Qwen区域候选及matched-control干预。此时full margin为M_full；后续只改query，固定reference、P/N/I、词典与评分器，并在每个条件重新求全体N的最高分。

基线能证明当前表示在已审核局部地点题库中的检索表现，尚不能证明某个对象具有landmarkness、功能价值超越显著性或已经形成认知地图。后续区域干预才检验哪些视觉证据实际贡献了该基线表现。

## 本轮核验的官方来源

- AnyLoc demo与说明，commit a9fda68c55083f765b019df148a1b67614f90ee2：https://github.com/AnyLoc/AnyLoc/blob/a9fda68c55083f765b019df148a1b67614f90ee2/demo/anyloc_vlad_generate.py
- AnyLoc特征与VLAD实现：https://github.com/AnyLoc/AnyLoc/blob/a9fda68c55083f765b019df148a1b67614f90ee2/utilities.py
- DINOv2 G/14入口，commit 7764ea0f912e53c92e82eb78a2a1631e92725fc8：https://github.com/facebookresearch/dinov2/blob/7764ea0f912e53c92e82eb78a2a1631e92725fc8/dinov2/hub/backbones.py
- DINOv2 giant2维度1536、40blocks：https://github.com/facebookresearch/dinov2/blob/7764ea0f912e53c92e82eb78a2a1631e92725fc8/dinov2/models/vision_transformer.py

以上仅核验小型公开源码文本；未下载/运行模型权重或VLAD词典。服务器需核验其实际安装源码、权重和词典，并记录版本差异。
