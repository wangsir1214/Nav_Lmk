# Phase 0：单视图区域干预协议 v1

状态：本地准备完成；候选框尚未提出或审核；干预尚未运行。本包不是实验结果。只沿用 paris_local_v1_20260923 原任务与原 P/N/I；不改变 reference gallery。

## 问题与样本

本轮问：在固定 DINOv2＋VLAD、朝向受限局部视觉对应任务中，遮挡一个事前提议的 query 区域，相比几何匹配遮挡会如何改变正确对应的分数与排名？该结果不直接等于导航地标、纯地点能力或认知地图。

selection_manifest.json 事前冻结18个Full正确的开发视图：每道路组三张、每组两个query pano都覆盖，共12 pano/6道路；目标为5 hard、8 medium、5 easy。原Full失败两题单列diagnostic。选择只用旧Full rank/margin与道路/pano元数据，不用未来Qwen/遮挡效应。其余24张Full正确视图仍属可扩展池，扩展决定必须在看它们的遮挡结果之前记录。

这属于条件于旧observer已检索成功的主分析。视图间不独立，按pano/道路提供描述统计，不能将20视图当成20独立地点作显著性宣称。

## 既有observer与Full

- G/14无register、block31 value局部描述子、32 urban词典、hard/cosine VLAD，既有配置在原baseline_request_v2.json。
- 原图640 JPEG经Pillow 12.3.0 RGB bicubic缩成448 PNG，然后ToTensor/ImageNet normalize；VLAD单位范数，点积等于cosine。
- 原运行task/config、词典、权重、212图索引的哈希记录在run_config.json。本地local_cache_preflight.json已核对20张原图与448缓存逐像素一致、168份reference VLAD哈希及词典哈希；4.55GB权重未在本地重哈希。
- 服务器开始干预推理时须重哈希权重/词典与运行索引，并对预先按ID排序的首/中/末三张query复算Full，与旧分数在1e-5内、rank一致，才可复用所有旧Full数值。不一致则停止并报错，不静默换observer、重训词典或把不兼容Full相减。

## Qwen单图candidate proposal

仅将每个冻结query的一张原始640×640图交给Qwen3.5-9B。每query独立、无历史对话，统一QWEN_QUERY_PROPOSAL_V1.txt。模型输入的图片ID/哈希只从proposal_input_only.json读取；完整selection_manifest.json中rank/margin仅供运行外分析，不能序列化进Qwen消息。模型请求中不能出现reference、P/N/I、检索分数、rank、road ID、其他query或既有候选。保存原回复、图哈希、实际请求、模型版本/配置和prompt哈希；格式错误最多同图重试一次。

最多两个候选，也可为空。坐标明确要求bbox_xyxy_1000，保存原框和640像素转换框；叠加带刻度overlay后人工确认坐标语义。旧route smoke的坐标结论不代替新QC。不剪裁越界值，模型理由不当作landmark真值。按返回顺序第一位作为主候选；人工只能因客观可见性、bbox、描述或类型错误而排除并记录原因，不能按Full或mask效应换框。

## 人审与三个controls

本地用phase0_intervention_geometry.py转坐标并生成同query三个控制框及审核overlay，暂不生成mask图。固定规则：候选宽/高至少8px、面积不超过20%；控制框与候选等宽等高，纵向中心偏差不超过128px、横向不超过256px，在8px网格搜索（边界另加）；候选与控制、控制之间均不重叠。按纵向、横向中心距离及query ID哈希固定次序取前三个。不满足则记CONTROL_GEOMETRY_FAIL，不手选背景、不改容差、不消失该题。

人工只核验候选可见性、框/描述、control几何及遮挡操作。control若恰是潜在有用线索，原样保留并标注，不因看起来重要而调换。候选/控制审核必须先于任何mask检索结果冻结；拒绝或无候选计入分母与原因。

## 输入级遮挡

首轮只做query-only input masking：从同一640 JPEG解码RGB，在640像素框内填固定RGB(127,127,127)，然后对整个图执行与原Full一致的Pillow bicubic 448缩图并存PNG。源JPEG必须通过原哈希。四种遮挡为CandidateMask、Control1/2/3；原Full是第五条件且不被覆盖。候选与控制同操作，禁止inpainting、训练或动态调框。

输入mask不同于patch-level descriptor removal，后者可利用已有1024×1536 patch cache，但不能与输入mask混成同一配对实验。本轮不做descriptor-only。服务器保存每张图、掩膜框、源/结果哈希和Pillow版本；合同不符即停止。

## 固定检索与readout

仅四张mask后的query重新提G/14特征并聚合VLAD；reference描述符、词典、标签、评分器不变。每variant保存全部168个reference的cosine分数与P/N/I关系；先屏蔽I，再按分数降序和reference ID升序排名。

S+ = max_P sim(q,r)，S- = max_N sim(q,r)，M=S+−S-；同时输出best-positive rank、top1 ID/关系、Recall@1。逐query计算delta_candidate=M_full−M_candidate，delta_ctrl_j=M_full−M_ctrl_j，U=mean(M_ctrl_1..3)−M_candidate。正U表示候选遮挡对固定检索仪器的margin损害超过三个控制遮挡的平均值；负U也照报。Full失败题单列。

常数灰块是分布外干预；匹配控制可比较一般遮挡损失，但不能排除全部语义/位置混杂。

## 分段交付与停止条件

阶段A：本地冻结选题与规则；服务器先返回Qwen proposal与overlay，不运行mask。阶段B：本地生成图板和controls，用户做技术QC，冻结候选。阶段C：服务器核验审核包，仅对合格题运行mask+retrieval；无候选或控制失败者报告原因。每阶段唯一UTC run_id，旧结果只读保留。服务器正常运行时低频/静默，仅在错误、需输入或阶段完成时回报。

Phase 1的(place, heading)任务不属于本协议；246个异朝向和84个同街候选仍为旧I，不能自动改成新gold。
