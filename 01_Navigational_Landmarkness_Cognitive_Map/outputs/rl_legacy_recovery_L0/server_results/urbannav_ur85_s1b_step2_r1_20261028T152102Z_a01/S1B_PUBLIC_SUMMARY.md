# PASS — WAITING_FOR_HUMAN_S1B_STEP2_REVIEW

Run: `urbannav_ur85_s1b_step2_r1_20261028T152102Z_a01`

48条正式对照全部独立执行一次；Full引用已有24题，未重跑。001/024四组正式轨迹在线核对Step1通过，最大数值差为 0。诊断轨迹未计入正式统计。

| 条件 | 成功/24 | 超时 | SR | 平均最终距离m | 平均最小距离m | 成功者平均动作 | 平均steps_to_success_or_cap |
|---|---:|---:|---:|---:|---:|---:|---:|
| Full | 24/24 | 0 | 100.00% | 94.901 | 94.901 | 65.67 | 65.67 |
| NoImage | 2/24 | 22 | 8.33% | 289.509 | 260.957 | 137.50 | 928.12 |
| ShuffledImage | 1/24 | 23 | 4.17% | 287.889 | 272.339 | 1.00 | 958.38 |

timeout的1000为评价上限，不是到达动作数；成功者动作均值仅纳入SUCCESS。

| 冻结距离档 | Full成功 | NoImage成功 | ShuffledImage成功 | 每条件题数 |
|---|---:|---:|---:|---:|
| [100,200) | 6 | 1 | 1 | 6 |
| [200,300) | 6 | 1 | 0 | 6 |
| [300,400) | 6 | 0 | 0 | 6 |
| [400,550] | 6 | 0 | 0 | 6 |

完整四档过程指标和逐题差值见S1B_PAIRED_METRICS.json、S1B_PAIRED_24_EPISODES.csv。

视觉替换是唯一主动实验干预。原Goal、yaw/选图、GRU、previous action、model_previous_reward=0、categorical sampling和真实环境转移逐步检查；所有输入/输出和hidden均有限。真实环境reward独立记录。不同条件随各自动作自然分叉。

ShuffledImage donor距离：

| 加权口径 | N | 中位数m | <50m | <100m | <200m |
|---|---:|---:|---:|---:|---:|
| action_step_weighted | 23001 | 186.731 | 8.57% | 23.84% | 50.90% |
| unique_source_panos_across_all_episodes | 153 | 223.090 | 4.58% | 16.99% | 43.14% |
| episode_source_pairs_equal_weight | 168 | 218.242 | 4.17% | 16.67% | 44.64% |

NoImage距离仅是对应冻结映射的地理距离，没有donor视觉暴露；动作步数加权会放大长时间停留位置，因此另报独立访问pano及episode-pano口径。

结果仅对当前24题、单次固定seed、100m成功半径成立。NoImage下降可能含全零分布外效应；ShuffledImage同时破坏位置匹配与时空连续性。不能定位特定视觉区域、证明地标或认知地图，也不能声称复现历史随机多目标成功率。

本轮结束，等待研究者审核。没有启动同状态实验、动作先验、SAM、遮挡、训练、新任务或GitHub推送。

R1修复与回归：只修改缺失参考值守卫并增加有效数值断言及证据记录，原reward算法不变。001/002/024环境初始化实测26/23/51；10个守卫单元测试通过，回归零模型前向、零环境动作。新48条记录中42条参考为空、6条非空；全部运行时amplitude与已核验Full相符。新NoImage001与旧阻塞run逐字节相同但确为独立重新执行，未拼接旧结果。父run78项校验和保持不变。

This is the reviewed public archive of a completed experiment. Full was referenced, not rerun. No follow-up experiment is implied by publication.
