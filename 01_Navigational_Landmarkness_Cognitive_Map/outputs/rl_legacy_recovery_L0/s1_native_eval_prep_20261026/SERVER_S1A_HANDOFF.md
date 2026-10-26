# S1-ENV — UR-85 原生导航环境 Smoke 交接

状态：`READY_FOR_SERVER_S1_ENV_SMOKE`。研究者于 2026-10-26 明确批准本文件所列的 environment-only smoke。此次没有 Full rollout 授权。

## 权限边界

本轮只验证历史导航环境、数据与固定 Goal adapter。允许读取源代码、路网、heading、图像；重建 UR-85 的 depth-30 图；检查 24 条候选；用预定动作核对状态转移、reward、reset 和终止语义；新增独立 smoke adapter 并输出审计报告。

严禁加载或调用 PPO / `actor_critic.act()`，读取或反序列化 checkpoint，训练，执行策略导航或任何 rollout，运行 NoImage/ShuffledImage、SAM、mask 或区域干预。不得连接 Neptune。不得根据策略效果筛题、换题或调难度。候选 episode 不得自动冻结。

Full rollout、模型加载和任何后续视觉依赖条件均需研究者另行批准。environment smoke 结束后必须停在 `WAITING_FOR_HUMAN_S1_ENV_REVIEW`。

## 交接包与版本核验

- Nav_Lmk 仓库：`wangsir1214/Nav_Lmk`
- 本交接分支：`codex/rl-ur85-s1-env-prep-20261026`
- 运行指令必须由研究者另行提供该分支的完整 commit SHA；不要用可变分支头代替指定 SHA。
- S0 批准合同：`codex/rl-legacy-s0-approved-20261023`，commit `d3ba7f2f6f412bbd3692961301e666c88ecc8899`
- S0-R 公开审核：`server-results/urbannav_ur85_s0_20261025T163610Z_a01`，commit `dafdd21bfdd97c37381344b70add301426341cfa`

在独立目录检出 Nav_Lmk 指定完整 commit，核验 HEAD、以下文件存在性和 Git 内容。读取 `HUMAN_S1_APPROVAL.md`、`task_review.csv`、本协议、`S1_EPISODES_DRAFT.jsonl`、`EPISODE_DRAFT_AUDIT.json`、`S1_METRICS_SPEC.md` 和本文件。核对 episode audit 内图 JSON SHA-256 `5bb3290d5d039c48b0cb649244bbb68d68b48ca93c741a775952dd02ccd31b55`、heading SHA-256 `00685688b909cce93259786fe8789539ebe500dce8e538ce4fa58af11b9fe539`，并与 S0 批准版数据 hash manifest 对照。任何缺件、提交不符或 hash 不符时停止。

## 指定环境和数据

- 历史执行代码根目录：`/home/wangyq/UrbanNav_neo_fromPC`
- 历史 NAS 代码副本：`/home/nas/wangyq/UrbanNav_neo_fromPC`，只读对照，不执行、不修改。
- Paris 原始 16 方向图像：`/home/nas/wangyq/GSV_Paris/0-All_GSV_3100_perspective_together`
- 新版路网 JSON：`/home/nas/wangyq/Street_view_and_points_Paris/Line_After_heading_clear_Paris_center_street_from0309_4_v1/Line_Points_3_street_view.json`
- 同版本 heading 和 SHP 五件套：按 S0 批准版 `DATA_SOURCE_HASHES.json` 定位并逐项校验，不用近似版本替代。
- Python：复用 S0 环境 `/home/wangyq/UrbanNav_neo_fromPC/landmark_probe/s0_environments/urbannav_ur85_s0_20261025T163610Z_a01/venv/bin/python`；只读使用，不安装或升级依赖。
- 新 smoke 代码只能位于 `/home/wangyq/UrbanNav_neo_fromPC/landmark_probe/s1_adapters/`；本轮轻量结果位于 `/home/wangyq/UrbanNav_neo_fromPC/landmark_probe/s1_env_runs/<UTC_RUN_ID>/`。
- Nav_Lmk 交接 checkout 可放在 `/home/wangyq/UrbanNav_neo_fromPC/landmark_probe/s1_env_handoff_checkout/`，与历史源目录保持为独立 checkout。

本轮不需要 checkpoint。不要校验、打开、加载或复制它。只用已批准源码、环境、图像与空间数据完成 environment-only smoke。

## 24 条候选的核验

完整保留 `S1_EPISODES_DRAFT.jsonl` 的 24 个原始 ID、字段和次序。它们只是草案：100–200、200–300、300–400、400–550m 四档各 6 条，不表示全部有效。服务器按 runtime 实际坐标重新计算并报告每条的初始距离和分档；严格大于 100m 才可作为候选起点。不得自动补题、替换候选或冻结最终任务清单。

逐题检查 start/goal pano 是否存在于 3058 点数据和运行图、SHP/JSON/heading pano ID 是否唯一对应、16 方向原图是否存在且能解码、runtime graph 连通性、Goal 坐标归一化是否可复现。保留 `PASS`、`NEEDS_REVIEW`、`INVALID` 三类；后两类保留原因，不当作 PPO 导航失败。

坐标来源必须分别记录：

- node-link JSON 的 `pos` 为图构造位置代理，记录原值及 `[lon, lat]` 次序；
- SHP geometry 记录原坐标、CRS 和转换过程。历史点位有投影到最近道路的处理，geometry 与原始影像 API 坐标可能有合理偏移；
- SHP `lat`/`lon` 属性分别记录原值；
- 通过读取已核验历史 runtime，说明图构造、Goal 编码和成功距离判定各自实际使用哪个字段与单位。

不要单凭坐标数值不同判定文件损坏，也不要自行挑选更“合理”的坐标。若字段冲突会改变 Goal tensor、100m 成功边界、初始有效性或难度分档，把受影响题标为 `NEEDS_REVIEW` 并停止依赖这些字段的测试，返回差异和原始证据供研究者判断。

## 朝向和预定动作检查

API/heading 表中的 heading 只是候选地理朝向。不得直接当作环境内部 yaw。沿原始 `reset()`、yaw 初值、16 方向图索引、旋转和前进实现，确定角度单位、正方向、零点及取图规则；不确定就停止并报告。

只用无模型预定动作检查少量固定状态：五个动作的原始编号/语义；旋转动作实际角度；forward 的 3-hop 候选范围、相对 bearing ±30° 条件和最近点选择；没有合法邻点时是否留在原地；状态复位和当前 pano/yaw 对应的图像索引。逐动作记录 pano、坐标、内部 yaw、视图索引、是否移动。不得把静态 BFS tree 路径当成动作可执行路径。

图像检查沿用历史 84×84、FOV 60°、16 个方向、OpenCV BGR；不得重投影、resize 或改写图像。Smoke 只验证少量清单所需图像，不预载或扫描整个巴黎图像库。

## Fixed-goal adapter 检查

在新增隔离代码中实现 environment-only fixed-goal shim，不改历史源码。必须明确对比原始 `evaluate()` / `CourierGame` 的任务采样、目标重采样、状态初始化、reward、done、auto-reset 语义。原版 evaluate 是随机多目标，`CourierGame` 成功后会选新目标，因此不能将其称为原样单目标复跑。

Shim 每个 episode 只保留清单指定的一个固定 goal；reset 后不重采、不跳转。到达实际 runtime 距离严格小于 100m 的位置时，按批准定义成功并终止；恰好 100m 不算成功。最多执行 1000 个环境动作后以 timeout 终止。用预定动作检查 goal 稳定、一步 reward、成功和 timeout 边界、reset 可重复性、无隐式 goal 切换。逐条说明哪些 legacy 语义保留、哪些被显式替代。

若不能在不修改历史源码的情况下可靠固定 goal，或无法核实 reward/done/reset 的执行顺序，停止并报告，不得声称 shim 通过。

## 新增文件、运行与报告

新增入口是 `landmark_probe/s1_adapters/s1_env_smoke.py`，使用上述 S0 隔离 Python 环境；脚本仅初始化数据/环境，不导入或构造 PPO policy，不读取 checkpoint。日志及结果写入全新 UTC run 目录，不覆盖 S0 或既有 run，不向 NAS 写入，不自动推送 GitHub。

结果至少包括：

- `ENVIRONMENT_SMOKE_SUMMARY.md`
- `COORDINATE_PROVENANCE_AUDIT.csv`
- `EPISODE_RUNTIME_VALIDATION.csv`
- `ACTION_TRANSITION_TEST.json`
- `FIXED_GOAL_SEMANTICS_DIFF.md`
- `GOAL_AND_TERMINATION_TEST.json`
- `ENVIRONMENT_EXECUTION_COMMANDS.md`
- `NEXT_S1A_RUNNER_SPEC.md`
- adapter 源码、执行日志、输入 hash 与轻量产物 hash 清单

输出分别报告 `PASS`、`NEEDS_REVIEW` 或 `BLOCKED`，给出候选题逐条状态及坐标/朝向/可达性证据。关键源码或数据 hash 不符、目标坐标不可确定、内部 yaw 或动作不可解释、固定 Goal/done/reward 机制不可靠时，保留部分有效审计并停止。

最终状态：`WAITING_FOR_HUMAN_S1_ENV_REVIEW`。环境 smoke 通过后也不得继续 Full rollout。研究者审阅 smoke 报告并另行批准后，才可准备冻结通过审核的 Full episode 清单；再之后还需单独授权 S1-A rollout。
