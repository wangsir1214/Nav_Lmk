# Paris UrbanNav S0：批准版服务器指令

状态：`READY_FOR_SERVER_S0`。本文件只授权 **UR-85 的严格恢复与48张原始图像独立 Full 前向 smoke**；不授权导航 rollout、成功率计算、遮挡、SAM、训练、视觉依赖分析或自动进入下一阶段。人审依据见 `HUMAN_L0_APPROVAL.md`。原 L0 草案留在父目录，不再作为服务器执行指令。

## 输入与版本闸门

在服务器独立工作目录读取**本分支指定完整 commit** 下的这个批准版目录。先记录分支、实际 HEAD、各交接文件 SHA-256，并核对 `PACKAGE_MANIFEST.json`。服务器如有未提交改动，不覆盖；如工作目录不是 Git checkout，建立独立 checkout，不在原目录 `git init` 或清理文件。

使用以下唯一权重和数据，实际 Linux/NAS 路径须先根据挂载核定，不能把候选路径当作已证实：

- 权重：`UrbanNav_neo_fromPC/WYQ/trained_models/ppo/UrbanNav_deepmind_WYQ_dpt30_20250416-032336_80000.pt`；1734776818 bytes；SHA-256 `fef170f6a01c9c9ba2361b7c7b81a4ddb9f0311a145766ed7d07006f7dc28a6e`。
- 新版3058点 `Line_Points_3_street_view.json`、同版 SHP bundle、历史 heading CSV：路径及逐文件 hash 见 `DATA_SOURCE_HASHES.json`。
- 原16方向 84x84 JPEG：仅按 `S0_SMOKE_ASSETS.json` 读取48张，逐张核 size/hash；不得预载或扫描全库。
- 原始代码：对照 `CODE_SOURCE_HASHES.json` 核确切源码路径和原始字节 hash。L0 的脱敏源码副本不可当执行源码。代码 hash 不同、资产缺失或 hash 不符时，保存差异并停止，不自行替换、修复模型或切换 UR-79/88。

UR-85 的新3058图、BFS30、2D Goal、100/200 m 半径由研究者于2026-10-22人工确认；不是完整历史 config。**不能据此声称其余代码、Goal 归一化边界、依赖版本或启动参数与当前目录相同。**后两项半径在本次 smoke 不触发导航环境奖励，仅作恢复 provenance。

## S0-1 环境与严格加载

1. 只读记录实际容器/镜像 ID、挂载、Python/PyTorch/CUDA及必需依赖；不打印 `.Config.Env`、token或旧源码中的凭证。不启动旧训练入口 `experiments_deepmind_real.py`，不连接 Neptune，不联网安装依赖，不修改现有 Qwen/DINO 环境。可用隔离兼容环境；若不存在，报告缺口并停下。
2. 对通过完整 hash 的可信自有 checkpoint，在隔离、无外网、无凭证的进程中加载；若需 `weights_only=False`，记录理由。核根对象 `[actor_critic, 80000, None]`、类别、全部629个保存条目的名称和形状。等构重新加载只能 `strict=True`，missing/unexpected/shape mismatch均须为0；不得删除未参与 forward 的 GeoCLIP 组件或重初始化参数后称恢复成功。
3. 新建独立 S0 adapter/UTC run目录；记录源码、导入路径、device与dtype适配及差异。不得修改旧工程、NAS原图或模型源码。原 Dataset 会预载图库，应限量读取48张，同时核其观察逻辑等价。

## S0-2 原始观察和唯一一次归一化

对每一张样本先核文件 hash，按历史路径：`cv2.imread(..., cv2.IMREAD_COLOR)` 得到 **BGR/HWC/uint8/0..255**，再仅转置为 **BGR/CHW/0..255**。以限定样本的原 `ViewImage` 观察路径与 adapter 逐像素比较，保存shape、dtype、通道、范围及相等计数；不得因原 Dataset 预载而读取全图库。若无法证明等价，停止，不继续做 Full smoke。

**adapter 不得预先 `/255`。**`simple_cnn.py` 的 forward 内执行唯一一次 `/255.0`；核验调用链中仅此一处归一化。不得 BGR→RGB、ImageNet normalize、resize、再压缩或加入新图像处理。若进入模型前有无损 dtype cast，记录前后原始数值等价，不能把值域变成0..1。

## S0-3 48个独立 Full 前向

每个 case 单独使用全新零 Goal/Policy hidden、prev_action=0、prev_reward=0、reset mask=0。同一个固定2D目标使用新版SHP中心点坐标和当前代码中的**候选**归一化边界作为 smoke fixture，保存原坐标、公式、tensor与源码hash；不称其为已证实的 UR-85 历史 goal config。逐例按 `S0_SMOKE_ASSETS.json` 的 heading/yaw 检查视图 index，但这些 yaw 不是导航轨迹。

在 `eval`、无梯度条件下，对同一case复制相同输入与状态做两次前向，检查 finite、softmax和数值重复性。保存 raw actor linear logits、probs、critic value、两套输出 hidden、heading 输出、deterministic argmax及全部非视觉输入。不能把 Categorical 的 normalized `.logits` 当 raw logits。48个 case 不顺次传递 hidden；不能由这些结果计算导航成功率或声称视觉依赖。

## 输出与停止

在新 UTC run 目录保存：`ENVIRONMENT_AUDIT.md`、`SOURCE_HASH_CHECK.json`、`CHECKPOINT_LOAD_REPORT.json`、`OBSERVATION_EQUIVALENCE.json`、`PREPROCESS_CHECK.json`、`FULL_SMOKE_RESULTS.jsonl`、`NUMERICAL_REPEATABILITY.json`、adapter源码/差异、命令/错误日志与轻量输出 hash 清单。权重、完整state_dict和大 tensor 不进 Git。可将轻量结果放新 `server-results/<run_id>` 分支，不覆盖旧run，并报告完整 commit。

任何闸门失败时记录具体证据并停止。完成后状态 `WAITING_FOR_HUMAN_S0_REVIEW`；不自动尝试后备权重、不执行环境轨迹、mask或下一阶段。期间仅在错误、确需输入或最终完成时向研究者简短汇报。
