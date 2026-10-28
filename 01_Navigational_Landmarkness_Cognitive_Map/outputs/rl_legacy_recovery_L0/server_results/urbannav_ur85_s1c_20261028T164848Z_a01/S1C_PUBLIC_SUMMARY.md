# S1-C public audit — PASS

Run: `urbannav_ur85_s1c_20261028T164848Z_a01`

47/47个预定Full动作前状态直接从原始归档恢复；141/141次单步前向通过。没有环境step、reset、动作采样、导航rollout或训练。Full复现绝对容差1e-6、相对容差0；实际最大差值为 0，47个Full输出均通过。

隐藏状态索引：动作s前取动作s−1后的归档；动作1取已核验零状态。三个条件各自复制同一份干预前Goal/Policy hidden，非视觉输入完全相同；前向不污染其他条件。使用原始ViewImage/TargetLatLng/Yaw/YawLabel及batch_obs；只替换供模视觉。

| 条件 | 状态argmax改变（描述性） | 有argmax改变的episode | episode等权平均JS(nats) | episode等权平均TV | episode等权Δp(0) | episode等权Δp(4) |
|---|---:|---:|---:|---:|---:|---:|
| NoImage | 10/47 (21.28%) | 10/24 | 0.118205 | 0.222980 | -0.105787 | +0.105787 |
| ShuffledImage | 11/47 (23.40%) | 9/24 | 0.145298 | 0.260601 | -0.146054 | +0.146054 |

JS以自然对数计（范围0到ln2），TV为概率L1差的一半。主要统计先在每episode内部对1或2个状态平均，再对24个episode等权平均；47个状态不是47个独立导航任务。timeout等闭环指标不在本诊断中重新计算。

观察到的概率变化支持当前视觉对UR-85即时动作输出有影响。此结果不直接解释闭环收益，也不识别哪个视觉区域或具体地标发挥作用。后续若授权局部干预，应同时保留高效应与低效应状态、预先冻结区域和几何控制；不能仅按本次效应挑选有利样本。

优先人工核查：S1C_STATE_RECOVERY_AUDIT.json、S1C_ACTION_PROBABILITY_EFFECTS.csv、S1C_EPISODE_LEVEL_SUMMARY.csv。原始hidden留在私有本地NPZ，未上传。

S1-B-R已归档：分支 `server-results/urbannav_ur85_s1b_step2_r1_20261028T152102Z_a01`；commit `2205804ec8c0987f98592908455715fcffdf0eae`。本S1-C结果先保存在Docker，与该B归档通过来源清单关联。没有自动执行后续实验。

本次公开审核包仅含脱敏轻量证据。原输入以历史JPEG文件名、pano、方向索引和SHA-256对应；原内部绝对路径替换为逻辑run/产物引用。全部hidden数组、原图、权重及内部日志未发布。pano/坐标来自研究者已批准公开的同一Paris研究节点与冻结任务，保留关联用于复核。
