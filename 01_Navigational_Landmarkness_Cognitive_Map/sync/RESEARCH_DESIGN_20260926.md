# 最新研究设计（2026-09-26）

## 1. 研究问题

本项目研究的不是某个 VLM 的排行榜，而是城市视觉线索的空间功能：在什么任务、路线和观察条件下，一个可见元素能够成为地点、方向或通行结构的参照，并帮助把当前观察与已有路线经验联系起来，从而支持局部行动。

可操作的主问题是：

> 给定一段已经看过的短路线和一个新的路口观察，路线中可见的视觉线索是否提高正确的局部续行选择？去掉该线索后，正确率或证据一致性是否按预期下降？

Qwen 的角色分成两部分：

1. **候选发现**：提出可见的店招、建筑、街角、设施或场景结构及其像素框。
2. **任务探针**：在独立条件下根据路线经验和当前观察选择合法出口，并说明使用的证据。

Qwen 的判断不能决定 gold action，也不能单独把候选称为“地标”。候选是否可见、是否稳定、是否与道路选择相关，由图像审核、路线记录、道路几何和人工核验共同决定。

## 2. 现有证据的边界

冻结的 DINOv2 ViT-G/14 + urban VLAD 结果为 44 query、168 reference、82 positive、6160 negative、1150 ignore；Recall@1=42/44，Recall@5=Recall@10=43/44。它测的是完整视图的局部地点对应，不能单独证明地标功能、同路细粒度定位、路线选择或认知地图。

已有 212 个 448 图像 patch 特征可作为候选区域干预的开发缓存，但必须核验 `feature_index.csv`、shape、hash 和 full VLAD 重聚合。删除候选时删除 patch 行后重新聚合，不能把最终 49152 维 VLAD 向量置零。

## 3. 实验顺序

### A 线：候选区域与地点对应

1. 使用原始 640x640 四视角图做 Qwen 候选提议；不提供 GPS、panoid、P/N/I 标签、VLAD 分数或答案。
2. 先做 2 图 JSON/坐标 smoke，再做 6 个路线相关 case（两条路线各 pre-decision、decision、post-decision），通过后扩展到预先分层的 12 个单图 query，再由人工审核冻结候选。
3. 人工逐框检查：真实可见、描述与框一致、框不明显带入无关区域、无重复、无越界/边缘裁断、不是纯临时遮挡物，并记录邻近观察能否指认同一线索。`UNCERTAIN` 不进入主干预。
4. 将审核框按同一画布 640→448 映射到 ViT-G/14 的 32×32 patch 网格（448/14=32），记录 row-major patch index 和覆盖比例。少于 4 个有效 patch 的框保留为候选记录，但暂不做首版 descriptor 干预。
5. 对每个候选区域用固定 seed 搜索最多 3 个形状、patch 数、近似中心位置匹配的控制区域；找不到合格控制则标记 `no_valid_control`，不强凑。
6. 在冻结 P/N/I 上比较 full、candidate_drop、candidate_keep、control_drop、control_keep；之后对少量固定 case 做像素遮挡复跑 DINO，检查 descriptor 干预稳健性。

### B 线：连续路径/路线记忆

1. 先以 `main_03`、`main_06` 做 feasibility smoke；它们有 3 个合法出发段，动作标签为 provisional，不能写作最终 gold。
2. 学习阶段给出按顺序的短路线；测试阶段给出同路线的临近路口观察和至少两个合法、匿名的非回头出口选项。测试提示不能直接写正确的 left/right/forward，也不能用文件名泄漏答案。
3. 主条件为“路线经验 + 当前完整图像/四视图”；对照为当前图像无路线经验、路线顺序打乱、候选区域遮挡、匹配控制区域遮挡。绝对坐标只作为附加地理先验上界，不进入视觉导航主结论。
4. 输出限于 `chosen_edge_id`、`maneuver`、`evidence_view_id`、候选线索/方向、理由和 `uncertain`。评分使用外部路线/道路关系：合法边选择准确率、相对对照的差异、证据是否可见且与所选边相关、遮挡后正确率/稳定性的变化。

## 4. 方向与命名合同

- NAS 前缀 `/home/nas/wangyq` 对应本地 `Z:\wangyq`；项目代码为 `/home/wangyq/Nav_Lmk`。
- 四视角原图：`/home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/{panoid}_panorama_0.jpg` 到 `{panoid}_panorama_3.jpg`。
- 文件名中的 `_panorama_0.._panorama_3` 是服务器物理文件名；固定视图索引仍是 `0..3`，不能改称 `v0..v3`。
- 固定视图绝对中心：`(heading_from_api + 90 * view_index) mod 360`。
- 不能把固定 view 直接称为永久 front/right/back/left；正式方向任务应从 ERP 按路线 bearing 重投影。

## 5. 证据命名

本轮输出是 `smoke`、`provisional` 或 `development` 时，报告必须保留这些标签。只有完成路线人工确认、输入不泄漏检查和预先定义的对照后，才可升级为正式行为结果。少量路线只能称 feasibility，不能作城市泛化或显著性结论。
