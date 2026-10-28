# S1-A UR-85 Full 固定单目标评价协议 v1

状态：24条 exploratory pilot 任务已冻结；本地未加载模型或执行导航。服务器 runner integration smoke 按 SERVER_S1A_FULL_HANDOFF.md 执行；24题正式 Step 2 需要研究者后续单独授权。

## 研究目标和解释边界

本阶段仅复现 UR-85 在固定 Paris 单目标任务上的 Full 视觉导航表现。它不等于历史随机多目标 evaluate() 原样复跑，也不证明视觉依赖、功能地标、认知地图或 Paris/跨城市泛化。历史 PPO reward 不能替代导航成功率。S0 单帧前向 smoke 只验证模型结构与输入接口，不代表导航能力已经恢复。

24题是探索性 pilot，不支持强统计结论。所有初始 view index 都是0；本版不检验不同初始朝向的鲁棒性。静态图连通和 environment smoke 通过，不证明 PPO 可沿原生动作转移到达目标。

## 冻结配置

- Run：UR-85，update 80000；唯一模型候选是 S0 已核验的 checkpoint，SHA-256 fef170f6a01c9c9ba2361b7c7b81a4ddb9f0311a145766ed7d07006f7dc28a6e。
- Paris 新版3058点数据；原历史 CNN+GRU+PPO，2D Goal，BFS depth=30。
- 原始街景观察：84×84、16方向、BGR、uint8 0–255；遵循 S0 输入合同，不做 RGB 转换、resize、额外 normalize 或重新投影。
- 每条 task 固定 start、goal、runtime SHP 经纬度归一化 Goal、internal yaw 与 evaluation seed；每条独立 reset。
- 成功：第一次到达固定目标距离严格小于100m即终止。距离恰为100m不成功。
- 最多1000个环境动作，所有 action 均计数；成功优先于同一步 timeout；无自动 Goal 重采样、auto-reset 或跳题。
- 采样：历史 actor_critic.act() 的 categorical stochastic sampling。实际 sampling 及 RNG 接线在服务器 Step 1 联调时验证。
- 全程只含 Full 输入；不运行 NoImage、ShuffledImage、SAM、mask 或其他视觉干预。

## Episode 来源

冻结清单共24条，保持原草案行序、episode ID、start/goal pano 和整数 seed。实际运行坐标为 S1-ENV-R1 核验的 SHP lat/lon 属性（EPSG:4326）；Goal 顺序为 [normalized_lat, normalized_lon]，按已记录 bounds 线性归一化。初始 yaw 使用已核验 legacy ConstrainAngle(180, API heading) 规则，24条初始 view index 均为0。清单保留每个 start/goal pano 的16方向图像文件名、字节数及 SHA-256。

距离档按服务器 runtime Haversine 距离：100–200m、200–300m、300–400m、400–550m，各6条。最短初始距离102.739m。所有24条 environment validation 和 runtime topological connectivity 均通过；完整动作路径可达性尚未建立。

## 输入与 recurrent state

每题 reset 后独立初始化 Goal GRU hidden、Policy GRU hidden、previous action、previous reward 和 reset mask，沿 S0-approved 模型接口更新。每步只将本题当前实际 observation 输入模型；不跨 episode 复用 hidden，不读取其他 condition 的状态。

冻结清单的环境 Goal observation 记录为 float64。Step 1 必须先对照原模型 batch/cast 约定检查 dtype、shape、数值和 batch 流程；禁止擅自更改归一化或数值处理来适配模型。

## RNG 与重复性

对每个 frozen evaluation_seed 分别设置适用的 Python、NumPy、PyTorch CPU 与 CUDA 随机源。必须沿历史 actor_critic.act() 代码确认 action 是从 categorical distribution 采样，不以 argmax 代替。记录设备、模型模式、sampling 调用、随机源设置、backend determinism flags、每步 observation/state 输入、hidden 更新摘要、previous action/reward、reset mask、概率、value、采样 action 与环境反馈。

Step 1 对同一 checkpoint、episode、设备和 seed 各重跑两次。若初始输入、逐步状态、采样 action 或结果不可重复，停止并报告差异；不要改 seed、模型、动作分布、任务或环境语义以追求通过。

## 指标

正式24题 Step 2 逐题输出 success、最终目标距离、action/step 数、实际 travelled distance、forward 成功移动数与无效/停留数、逐步 goal progress、timeout 与失败类型、episode reward（辅助）。奖励不参与 episode 筛选，也不定义 success。trajectory 至少保存时间步、当前 pano/坐标/yaw/view index、action、概率/value、奖励、remaining distance、移动/停留和终止状态；GRU hidden 原始张量仅服务器本地保留。

## 版本和来源

- S1-H 草案：fa0ce423d7c35e3f0f217c947ed502f8f014e1d3。
- S1-ENV-R1：b367639e7585a244233832174685398b11bfa4b6。
- S0-R：dafdd21bfdd97c37381344b70add301426341cfa；S0-approved contract：d3ba7f2f6f412bbd3692961301e666c88ecc8899。
- 精确源文件和SHA-256列在 S1A_MANIFEST_HASHES.json。冻结清单SHA-256：f7bec0034a33345e0537b95794f78c6562db89b15532679785108ca29f636e3b。

