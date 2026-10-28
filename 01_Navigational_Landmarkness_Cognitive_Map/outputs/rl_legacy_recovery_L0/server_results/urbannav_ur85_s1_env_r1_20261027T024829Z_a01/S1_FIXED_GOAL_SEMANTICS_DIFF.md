# Fixed-goal shim 与历史代码的语义差异

状态：环境接口及限定测试 PASS；原代码不变。实际历史 evaluate 使用 urbannav_vec.UrbanNav，不是另一个旧 urbannav.py 构造入口。

| 项目 | 原 evaluate / CourierGame / UrbanNav | 本轮隔离 shim 与证据 |
| --- | --- | --- |
| 模型及任务范围 | evaluate 调用策略并累积 10 个随机多目标 episode | 未导入训练入口、未加载 PPO；仅 3 个指定接口状态和少量预定动作 |
| 配置 | 当前 YAML 的 depth=50、num_actors=8、curriculum game | 按 UR-85 已批准合同显式使用 depth=30、单状态接口；不声称当前 YAML 就是完整历史 Run 配置 |
| 建图 | 原 PanoGraph.build_graph/set_BFS_graph；读取 SHP lat/lon 和 heading | 原方法实际执行，3058/3310 源图转为 550/549 runtime tree；未用近似图替代 |
| 图像 IO | Dataset 构造器预载所有图像 | 新 BoundedDataset 仅懒加载访问 pano；委托原 Dataset.fetch、get_pano_perspective 与 ViewImage，像素/选图逻辑不变；不启动后台预取缓存 |
| Reset | 原 reset 随机选起点，并调用游戏 on_reset 随机选目标 | 固定 start/goal/yaw；调用原 reset 的计数和观察流程，覆盖目标采样为固定初始化；显式清零 reward/done/pitch，避免旧状态残留 |
| Goal | SHP 属性经历史 bbox 归一化 | 同一原 TargetLatLng 观察路径，24 题与 JSON proxy 编码一致，固定目标不重采样 |
| Yaw / 图像 | 内部北向 0°、顺时针为正，约束 [-180,180]；最近 (yaw-heading) 的 22.5°方向 | 原 GetYaw、RotateObserver、取图逻辑保留；reset 重复一致；原图 BGR CHW uint8 0–255，无 resize/归一化 |
| 动作 | 0 前进、1 -22.5°、2 -67.5°、3 +22.5°、4 +67.5° | 委托原 UrbanNav.step/MoveToNextPano；3-hop、角差严格 <30°、最近候选、无候选停留均验证 |
| Reward 初值 | _pick_random_goal 用原 _shortest_paths 返回路径计数赋值 reward_current_goal | 固定 start/goal 后调用同一 _shortest_paths 初始化；不直接拿配置 max_reward 常数顶替。路径统计含历史 extended graph/backfill，不宣称为真实最短可执行路径 |
| 每步 Reward | 原 _compute_reward；重复 pano 零奖励，100–200m 改善时 shaping，<100m 完成奖励 | 直接复用原函数；30 次真实动作奖励逐次与独立原函数实例一致；synthetic 重访零奖励通过 |
| 恰好 100m | 严格 <100m 才 found；100m 仍可能取得完整 shaping reward | 保留该区别：100m 不是成功，99m 才成功；reward 不当作 success |
| 目标切换 | 原 get_reward 成功/goal timeout 后选择新目标 | 不调用重采样；单目标首次 <100m 即终止，goal 始终不变 |
| Timeout | 原 frame_count > frame_cap，且有游戏目标 timeout；可自动 reset | 新 wrapper 在第 1000 个动作使用 >=1000；成功优先于同一步 timeout；禁用 auto-reset，终态后拒绝继续 step |
| 统计与 info | 多目标 SPL、next-pano guidance，成功后新目标 info | 只给固定目标距离、步数、reward 和终止状态；不计算导航成功率/SPL，不把旧 guidance 当作 gold |
| 错误 | 原 step 接受数组索引，负索引可能合法访问数组 | 外层先拒绝非整数/越界动作；缺图或坏尺寸抛错；invalid 不计作导航失败 |

真实测试：3 个状态各两次 [1,3,2,4,0] 共 30 次动作，加 1 次停留测试。每个前进都实际移动，观察与状态逐像素对应。完整动作路径可达性仍未建立；静态连通不是动作导航保证。

合成边界：单独 metric graph 与标量观察，不更改任何真实题、坐标或图像；验证 200/150/100/99m、重访奖励、初始距离必须 >100m、999/1000 步和终止后拒绝动作。Timeout 用隔离计数器从 998 开始测试两个动作；未跑 1000 步导航。合成测试不是 NoImage 或策略消融。

## 本次交接状态

研究者已接受上述环境 smoke。候选任务尚未正式冻结；每题策略 seed 接线与完整 PPO runner 未测试。停止于 READY_FOR_LOCAL_S1A_FREEZE_REVIEW。
