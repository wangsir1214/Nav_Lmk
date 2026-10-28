# S1-A Freeze v2 审核记录

日期：2026-10-28  
依据：研究者本轮 S1-A Freeze v2 指令。本文件由 Codex 按指令整理，不伪装成服务器机器检测或另一次独立签字。

## 决定

| 项目 | 决定 | 证据与边界 |
|---|---|---|
| 服务器来源提交 | 接受为冻结依据 | S1-ENV-R1 完整 commit b367639e7585a244233832174685398b11bfa4b6；S1-H 草案 commit fa0ce423d7c35e3f0f217c947ed502f8f014e1d3，分别引用。 |
| 24 条身份与顺序 | 通过 | 逐条核对 ID、start/goal pano、原 seed 与顺序。草案没有独立 order 字段，冻结顺序沿原 JSONL 行序，并与服务器 order 1–24 对齐。 |
| 运行坐标与 Goal | 通过 | 使用服务器核验的 SHP lat/lon 属性，EPSG:4326；Goal vector 对应验证 CSV。JSON pos 与 SHP 属性最大差0m；SHP geometry 转换最大差约2.12e-9m。 |
| 初始距离与分档 | 通过 | 全部严格大于100m，范围102.739–464.890m；100–200、200–300、300–400、400–550m各6条。 |
| 朝向与图像 | 通过 | 使用 legacy ConstrainAngle(180, API heading) 得到 runtime internal yaw；24条初始 view index 均为0。每条 start/goal 各16张图，768张图的 decode/hash 清单保留在冻结记录中。 |
| Runtime graph | 通过，但不等于策略可达 | 服务器验证24/24 topological_connected=True；runtime depth-30 BFS tree为550节点/549边。24条完整动作路径可达性均为 NOT_ESTABLISHED。 |
| Native action smoke | 范围有限 | 只对 S1A-DRAFT-001、S1A-DRAFT-013、S1A-DRAFT-024 三个 fixture 做了预定动作；不代表其余任务已做策略路径测试。 |
| RNG 接线 | 待服务器联调 | 24个整数 seed 已冻结；Python、NumPy、Torch CPU/CUDA RNG 是否控制 actor_critic.act() categorical sampling 尚未验证。 |
| Reward amplitude | 保留未测状态 | 3条 fixture 有实测；其余21条保持 null，服务器运行时按历史 _shortest_paths(fixed_goal, fixed_start) 规则计算。不得插零或推断。 |
| Goal dtype | 待服务器联调 | environment observation 记录为 float64；runner 必须核实 S0-approved batch/cast 路径，禁止静默改变归一化或数值处理。 |
| Fixed-goal 语义 | 已记录并按本 pilot 接受 | 这是新的固定单目标评价，不是历史随机多目标 evaluate() 的原样复现。完整差异见 S1-ENV-R1 来源报告。 |

## 冻结范围

24条候选原样成为探索性 S1-A Full pilot v1；不按模型表现增删。保留每条的 pano ID、runtime 坐标、归一化 Goal、internal yaw、seed、距离档、动作边界、数据版本引用和逐图 SHA-256 索引。冻结不表示 policy 成功、可执行路径、统计功效或跨城市泛化已经得到验证。

## 执行边界

本轮只做证据复核、冻结与交接准备。没有加载 PPO、没有导航 rollout、没有重扫 NAS。服务器 Step 1 integration smoke 的任务定义为 S1A-DRAFT-001 与 S1A-DRAFT-024，每题同 seed 重复2次用于接口与重复性诊断，不纳入正式24题统计。Step 2 的24题正式评价仍需研究者后续单独授权。

