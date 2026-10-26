# S1 指标定义草案

所有位置距离使用经核验的SHP pano坐标间Haversine距离；如果后续服务器评估也提供metric CRS距离，二者分别报告并声明主指标。成功阈值采用确认的 `min_radius_meters=100m`，成功定义为episode执行中第一次到达距固定goal `<100m` 的pano；恰好100m不算成功，起点必须在100m之外。成功时立即结束这个固定goal episode，不重抽goal。

- `success`: 成功episode数 / 全部有效冻结episode数；按难度档逐档报告。24题只作探索性结果，附Wilson 95%区间，不宣称正式功效。
- `final_distance_m`: 成功时首个成功pano到goal的距离；未成功时第max_steps终态距离。另报告所有episode的best distance。
- `initial_distance_m`: 固定start到goal直线地理距离，用于任务分层，不等同路网距离。
- `actual_traveled_distance_m`: 实际观察到的pano序列逐相邻位置Haversine长度总和；重复停留贡献0。若动作触发3-hop跳转，按实际相邻位置的直线距离计并另报告动作步数，不能把pano hop误称道路距离。
- `static_bfs_tree_route_distance_m`: 候选选择阶段BFS tree路径边长之和，仅作任务难度描述，不是实际路径或oracle最短路径。
- `path_excess_m`: `actual_traveled_distance_m - initial_distance_m`；`path_stretch = actual_traveled_distance_m / initial_distance_m`。仅对初始距离>0的有效题计算。它不是相对可行最短步行路径的regret。
- `episode_steps`: 从reset后到成功/step cap之前调用的环境step数；rotation、no-op/stay均计一步。
- `reward_sum`: evaluator固定goal适配器按历史reward公式逐步重现的累计reward，作为辅助指标。与success分开报告，不能把reward称为成功率。
- `timeout`: 到max_steps仍未成功；和环境异常分开。
- `stuck_diagnostic`: 只作为诊断标签：连续50次动作没有位置变化，或连续50步best distance改善小于5m；不提前终止episode、不作为另一种失败定义。由于允许原地旋转，这项依赖同时报告pano变化和heading变化。
- `invalid_transition`: 动作索引越界、缺图/坏图、pano不在图内、环境状态不一致、goal意外改变、非有限输出等协议/运行错误。invalid单独列出，不并入性能分母；任何invalid需报告并停止分析。

每episode保存固定配置、seed、start/goal、真实初末坐标、goal tensor、step级动作/概率/奖励/remaining distance/yaw/current pano/hidden诊断摘要、termination、静态与真实轨迹长度。原始逐步hidden可只保留在服务器受控目录；对外轻量结果不发布内部绝对路径或大张量。

未来条件比较以同episode的差值为基本单位，按episode配对报告 Full 与 NoImage、ShuffledImage 的成功翻转、final distance、travel length及step差。stateful policy各条件是独立完整轨迹；不能逐时刻对不同轨迹action probability直接相减。单纯24题的聚合均值不能作为landmark causal evidence。
