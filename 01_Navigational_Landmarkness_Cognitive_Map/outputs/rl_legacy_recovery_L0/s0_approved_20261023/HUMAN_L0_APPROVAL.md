# L0 人工审核确认

状态：`READY_FOR_SERVER_S0`。本文件记录研究者于 **2026-10-22 人工确认**的事项；它不是 2025 年不可变 Run 配置或模型验证结果。

1. 本次只考虑 2D Goal，不恢复 32D Goal。
2. 恢复候选优先级为 UR-85、UR-79、UR-88。本次 S0 **只恢复 UR-85**，失败时停止并报告，不自动切换后备。
3. 研究者确认 UR-85 使用 Paris 新版 3058 点、BFS depth 30、2D Goal、`min_radius_meters=100`、`max_radius_meters=200`。其中新版图、depth、2D Goal 还受到历史索引、日志或权重结构支持；100/200 m 的新证据类型是研究者回忆，未找到该 Run 的不可变配置快照。
4. 研究者审核了 `IMAGE_HEADING_QA.html` 中 3 个 pano 的 00-15 序列、相邻视图重叠及可辨认街景方向，未发现明显错向或重复。这是抽样目视检查，**不是绝对 heading 真北校准**。
5. 研究者接受 `TRAINING_HISTORY.html` 和原 `RUN_CHECKPOINT_MATRIX.csv` 对历史日志的统计与解释。接受统计不等于已验证原始代码版本、完整启动参数或导航性能。

## 三个 Run 的保留顾虑

| 候选 | 当前支持 | 尚不明确或不可直接比较的方面 |
|---|---|---|
| UR-85 | 新 3058 图、depth 30、2D Goal、100/200 m 人工确认；权重内部 update 80000；同时间戳日志 | 无当年不可变源码/config/命令；当前文件为后续状态，不能断言其他配置完全相同。Goal 坐标归一化边界、运行环境、镜像与精确依赖仍需核；没有与最终权重严格绑定的 Oracle/Full 导航评价。 |
| UR-79 | 旧 3059 图、depth 30、2D Goal；权重内部 update 100000；索引称收敛 | 必须用旧 JSON 和旧 SHP，不能混入 UR-85 新图；reward 半径、原配置与源码快照不明；现有评估/Oracle 线索没有与该最终 checkpoint 严格绑定。 |
| UR-88 | 新 3058 图、depth 40、2D Goal；权重内部 update 120000；索引记 100/300 m、基本收敛 | 与 UR-85 的 depth 和 shaping 半径不同，历史 reward 不可直接排名；缺 Run 级源码/config；现有 Oracle 线索未严格绑定最终权重。 |

四份重点权重的静态结构核验不等于已加载或运行。UR-79/88 仅是后备计划，未计算整文件 SHA-256；若将来启用，须单独核验权重、源图和环境，不得自动沿用 UR-85 的 S0 结果。

来源：研究者本轮消息；原始 L0 证据保留在父目录。批准版交接位于本目录，原 `S0_INPUT_CONTRACT.json` 的 `DRAFT_FOR_HUMAN_L0_REVIEW_NOT_EXECUTED` 状态保持不变。
