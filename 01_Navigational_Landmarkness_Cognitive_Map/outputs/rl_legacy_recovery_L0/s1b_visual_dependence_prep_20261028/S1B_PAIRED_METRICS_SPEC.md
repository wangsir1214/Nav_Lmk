# S1-B 配对指标与统计口径

来源：冻结24题 commit `53d4a37204231f9482985020d6067017563c7665`，manifest SHA-256 `f7bec0034a33345e0537b95794f78c6562db89b15532679785108ca29f636e3b`；Full 结果 commit `88dd7d474eb6ed08f3261b1a29b5f4dc1c5bf703`。本规格待人工批准，尚未执行对照。

## 每题原始记录

记录 `condition, episode_id, seed, status, success, timeout, invalid_reason, steps, first_success_step, initial_distance_m, final_distance_m, minimum_distance_m, net_goal_progress_m, travelled_distance_m, forward_actions, forward_moves, forward_stays, rotations, revisit_arrivals_after_departure, unique_panos, episode_reward, mean_action_probabilities[5], mean_action_entropy_nats`，并保留逐步状态、真实/供模图像 ID、采样动作、五维 logits/概率、value、reward 和终止原因。无效输入或接口故障单列 `INVALID`，不混作导航失败或从分母静默删除。

距离为 S1-ENV 已核验的 runtime SHP 经纬度和原 Haversine 口径。`success` 为第一次严格 `<100m`，包括初态和每步在内的 `minimum_distance_m` 不得只取终态。`steps` 计所有环境动作；成功时为到达区域所需动作数，未成功的1000步 timeout 以删失/受限值报告，不称为“到达动作数”。`net_goal_progress_m = initial - final`；`travelled_distance_m` 只累加实际换 pano 的位移。`forward_stays/forward_actions` 为无效前进比例，旋转另列，不能把原地转向自动判为无效。回访先压缩连续同 pano 状态，再计离开后重新进入已见 pano 的次数。

## 24题配对比较

以 episode ID 为唯一配对键，检查三个条件各恰有一条正式结果、seed/start/goal/initial yaw/Goal vector 均与冻结清单一致。Full 直接引用既有正式结果；诊断重复不合并。对每个指标输出每题 `NoImage-Full` 和 `ShuffledImage-Full` 差值，再报告24题的均值、中位数、范围、四档描述及原始成对表。成功率同时报告每题的 `(Full成功, 对照成功)` 四格计数；Full 24/24 的天花板下重点看成功变为失败的题数和过程指标。

过程主读数：成功、到达100m的动作数、1000动作受限的 `steps_to_success_or_cap`、最小与最终距离、净目标改善、实际移动距离、无效前进比例、旋转/停留与回访。单独报告每题的动作概率与 entropy 摘要。不同条件轨迹可能分叉，不对不同位置的第 t 步概率做逐步配对差；只在预定的同状态单步诊断中比较同一输入状态的输出。

若要给不确定性，使用 episode 为抽样单位的配对 bootstrap（例如固定独立分析 seed、10000次重抽），展示差值区间而非以逐步记录伪造大样本。24题为探索性 pilot，多个相关过程指标与 Full 的100% SR 都限制推断；不作跨城市或一般地标机制结论。Reward 只作辅助，不能代替成功率。缺少兼容原生3-hop动作和100m目标区域的最短可执行路径，故不计算 SPL；`累计移动/净改善` 更不是 SPL。

## 最低结果解释

- NoImage 与 ShuffledImage 都变差：支持视觉必要性与位置匹配信息有用；仍需排除全零分布外与 donor 相似性因素，且不能定位具体地标。
- 仅 NoImage 变差：可能是全零分布外干扰，不能据此宣称真实地点视觉被利用。
- 仅 ShuffledImage 变差：支持位置匹配的图像信息对当前任务有用；检查 donor heading 对齐与图像质量。
- 两对照仍100%成功：看配对动作数、目标进展、停留/回访和概率。若过程也接近，当前题集鉴别力不足，应先设计更难任务，再考虑区域分割。
