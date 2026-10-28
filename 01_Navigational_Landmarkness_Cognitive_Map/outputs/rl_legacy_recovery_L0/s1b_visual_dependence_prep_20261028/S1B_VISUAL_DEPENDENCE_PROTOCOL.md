# S1-B 视觉必要性对照协议草案

状态：`WAITING_FOR_HUMAN_S1B_REVIEW`。本文件只定义后续实验；尚未授权或执行任何新 PPO rollout。

## 问题与主比较

在已经通过 S1-A 的固定 Paris 导航题中，真实、位置匹配的街景观察是否改善 UR-85 的闭环导航？以现有 Full 24题结果作为固定基线，后续各独立运行 NoImage 与 ShuffledImage 24题。主要判断使用 episode ID 配对的成功和过程指标；单步干预及动作先验只是辅助诊断。此阶段不声称发现功能地标。

## 不变量

冻结清单为 commit `53d4a37204231f9482985020d6067017563c7665` 的 `S1_EPISODES_FROZEN_v1.jsonl`，Git blob SHA-256 `f7bec0034a33345e0537b95794f78c6562db89b15532679785108ca29f636e3b`。24条 ID、start/goal、归一化2D Goal、initial internal yaw、evaluation seed 和顺序不改。固定 UR-85 update 80000 checkpoint（SHA-256 `fef170f6a01c9c9ba2361b7c7b81a4ddb9f0311a145766ed7d07006f7dc28a6e`）、Paris新版3058点、depth=30 runtime graph、五动作和原生转移/reward。成功为首次距离严格 `<100m`；每条最多1000个环境动作。

每个条件、每题从头 reset 环境，零初始化 Goal GRU 与 Policy GRU、previous action、reset mask，并按 S1-A 已核验时序更新。`model_previous_reward=0` **每步**，历史 `evaluate()` 如此；实际 environment reward 单独记录，不能馈回模型。保持原 categorical stochastic sampling，重置 Python/NumPy/PyTorch CPU/CUDA 的该题 frozen seed，记录设备和确定性设置。相同 seed 用于配对和复现，不保证干预后动作序列相同。禁止复用 Full 的轨迹、中途 hidden 或动作序列。除当前送入 CNN 的图像外，所有非视觉模型输入和环境状态保持原值。

历史图像入口为每步从16张84x84 JPEG中选一张，OpenCV BGR `uint8`、HWC→CHW，值0–255；模型边界只做 S0 已准许的等值 cast，CNN 内部唯一 `/255.0`。不得 RGB 转换、ImageNet normalize、resize、重投影、重新 JPEG 编码或改变模型。

## 条件

1. **Full**：引用 S1-A 已正式执行的24题结果 commit `88dd7d474eb6ed08f3261b1a29b5f4dc1c5bf703`，不重跑。它为同一冻结任务的真实图像基线。
2. **NoImage**：只在视觉适配器边界将原 BGR CHW 图像替换为形状 `(3,84,84)`、`uint8`、全零的张量；像素全为0。保持正常图像读取前的实际 pano/yaw/Goal、历史状态与环境转移。逐步断言视觉输入为零且其他输入与该条件自身真实状态一致。全零图像可能是训练分布外输入，因此性能下降只能作为视觉输入必要性的一个信号。
3. **ShuffledImage**：先在已批准的550节点 depth-30 runtime graph 上生成固定 pano→donor 的无自映射双射。节点 ID 以 UTF-8 字节序排序；对每个 ID 计算 `SHA256("S1B-donor-v1|20261028|" + pano_id)`，按 `(digest bytes, pano_id bytes)` 排序为序列 `q`；映射 `q[i] -> q[(i+1) mod N]`。算法、seed 字符串和来源图版本在任何条件运行前固定；实际映射 JSONL 先保存、SHA-256 校验并交人工审核，不能根据导航结果挑选映射。预检全部550个 runtime 节点的 heading 与16视图可读取性/文件哈希，只遍历这550个受控节点，不扫描整个 NAS 图库。任何缺失、重复、节点数变化或哈希差异停止，不补点或重新洗牌。

ShuffledImage 的真实 agent pano 为 `p`、当前 internal absolute yaw 为 `y` 时，查固定 donor `d=M[p]`，用已核验的 `find_nearest_angle_index(y-heading[d])` 和同一 legacy 等距规则选择 donor 的16视图。不能直接沿用当前 pano 的 view index。相同 `p` 始终使用相同 donor，但该 donor 的视图随 `y` 变化。记录 `p/d/y/heading[d]/donor_view_index/image_hash`；仅将 donor 图像送入 CNN，实际位置、Goal、reward、成功与动作转移仍来自 `p` 的环境。此对照保留真实街景图像分布，却破坏图像与当前位置的正确匹配； donor 仍可能偶然相似或邻近，应预先记录距离/道路关系而不据结果重映射。

## 运行前闸门与停止

服务器先只读核对 S1-A、冻结清单、checkpoint、旧源码、S1-ENV fixed-goal adapter、图/heading/图像来源哈希及 Python 环境。新视觉适配器只放隔离实验目录，提供原观察与替换观察的 shape、dtype、BGR、像素范围及非视觉输入不变的逐步断言。先对两条预定题 `S1A-DRAFT-001` 与 `S1A-DRAFT-024` 分别做受限接口联调，并在同设备/seed 下重复以核对确定性；诊断轨迹不纳入正式24题统计。任何不等价、映射未冻结、RNG/hidden 链不可靠或原始语义变化均停止。通过闸门且研究者另行授权后，每个条件以全新初态运行全部24题，包括两条诊断题；不根据成绩删题或改 seed。

## 判读

Full 已是100% SR，存在天花板。若对照 SR 降低，需要结合成功/失败和过程差值；若 SR 同为100%，配对比较到达100m所需动作数、目标进展、移动与停留、回访和动作分布。NoImage 单独下降还可能来自分布外输入；ShuffledImage 的下降更直接支持**位置匹配的真实视觉**有导航效用，但仍不能定位具体区域或证明地标。若两对照与 Full 在成功和过程上都相似，先增设有区分度、初始朝向变化或更严格任务的后续研究设计；不得把这24题的 Full 成功当作 SAM 实验的充分依据。
