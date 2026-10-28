# 服务器 S1-B 待批准交接

状态：`WAITING_FOR_HUMAN_S1B_REVIEW`。这份 handoff 仅供审核、接口预检和未来任务规划；当前**不授权**运行 NoImage、ShuffledImage、单步干预、动作先验或新 Full rollout。

## 来源与不可变项

在 `UrbanNav_wyq` 容器的独立 checkout 中读取本分支 `codex/rl-ur85-s1b-visual-dependence-20261028`，记录实际完整 commit 与本目录七份文件的 SHA-256。S1-A 公开结果必须是 `88dd7d474eb6ed08f3261b1a29b5f4dc1c5bf703`；冻结24题来源必须是 `53d4a37204231f9482985020d6067017563c7665` 且 manifest Git blob SHA-256 为 `f7bec0034a33345e0537b95794f78c6562db89b15532679785108ca29f636e3b`。后续运行仍只用 S0/S1 已核验的 Docker 原代码、UR-85 checkpoint、NAS原始3058路网与84x84图像、固定 Goal adapter 和原 S1-A 环境。不要以 NAS 代码覆盖 Docker，不要改历史源码或权重。绝对路径以 S1-A 已通过的服务器实际记录为准；新增 adapter、映射与轻量结果仅写入 `landmark_probe/` 新版本目录。

## 研究者批准后服务器先完成的接口闸门

1. **原始动作与采样**：核对五动作编码、actor raw logits→softmax→categorical sample 调用链、无额外 action mask/temperature/argmax 改写。S1-A trace 中三动作概率虽极小仍非零；如源码/runner出现未解释限制，先报告。
2. **图像唯一替换点**：在进入 CNN 前保留原 OpenCV BGR CHW `uint8` 0–255 接口；零图和 donor 图只替换此图像张量。用受限样本逐像素、shape/dtype 和其他 observation 字段对照，确认 CNN 仍只 `/255` 一次。不得触发全图库预载或重新投影。
3. **donor 映射**：从已批准 depth-30 的550节点运行图提取 ID，按 `S1B_VISUAL_DEPENDENCE_PROTOCOL.md` 固定算法和 seed 字符串生成一份完整映射；无 self、无重复 donor。只在550个节点及其16方向图范围预检 heading、可解码与来源 hash。保存映射 JSONL、生成器版本、源图/heading hash、排序规则、映射 SHA-256；**在导航执行前**提交映射摘要与 hash 给研究者审核。不能据 Full 或对照表现修改映射。
4. **朝向与状态**：用实际 internal yaw 减 donor heading 调用已核验的 legacy 最近视角规则，不复用当前 view index；检查 0/360 与等距边界。每题每条件独立 reset 环境、双 GRU、previous action、`model_previous_reward=0`、mask、全部适用 RNG；reward 只记在环境侧。相同种子和设备做受限重复，核对日志与 hidden 链。
5. **可追溯运行**：先对冻结的001与024做接口诊断，诊断文件与正式24题统计严格隔离。所有闸门经审核通过后，需研究者后续明确授权才可各自从初始状态运行 NoImage 和 ShuffledImage 全部24题；Full 使用现有正式记录，不重跑。失败时保留产物并停止，绝不改冻结题、checkpoint、映射、reward 或终止规则求通过。

## 后续正式结果规格

为每个条件写版本化 run config、源/代码/模型/data hash、donor mapping hash、逐题结果与逐步 trace、执行命令、环境版本及失败日志。每步含真实 pano/yaw/view、供模图像 ID/哈希、Goal、previous action/reward、reset mask、双 GRU 诊断 hash、五维 raw logits/概率、entropy、sampled action、环境 reward、下一状态、距离及终止。GRU 原始张量只留服务器。最终按 `S1B_PAIRED_METRICS_SPEC.md` 输出24题配对表和描述性结果；公开 GitHub 只回传经过脱敏且必要的轻量证据，不自动推送内部路径、原始图像、checkpoint、hidden 或大日志。

额外同状态干预与动作先验见 `S1B_DIAGNOSTIC_BASELINES.md`，需单独批准；不得先行运行。任何对照成绩都不能直接声称发现功能性地标。
