# 服务器 Codex 执行交接：Qwen 路线 smoke v1

## 交接方式

请在服务器项目 `/home/wangyq/Nav_Lmk` 执行。先记录当前 commit、remote 和工作区状态。若是干净 Git 工作树且 `origin` 为 `https://github.com/wangsir1214/Nav_Lmk.git`，执行一次 `git pull --ff-only origin main`。若现有项目不是 Git 工作树，读取 `SERVER_SYNC_SETUP_20260927.md`，在独立临时目录 clone GitHub 并只同步 `01_Navigational_Landmarkness_Cognitive_Map/sync/`；若 GitHub 不可访问，等待用户手动上传该 sync 目录。不要在现有项目执行 `git init`、`git clone`、覆盖或删除文件。完成 Git 或非 Git 同步后再继续本 handoff；记录 `sync_mode` 和来源 commit。

NAS 前缀 `/home/nas/wangyq` 对应本地 `Z:\wangyq`。项目代码 `/home/wangyq/Nav_Lmk` 不等同于 Z 盘路径。读取并遵守 `PATH_STORAGE_POLICY_20260927.md`：代码和轻量文件留在项目目录，权重、图像、448 缓存、patch cache 和大型结果留在 NAS。

本轮不重新运行已通过的 G/14+VLAD baseline，不修改冻结 P/N/I，不上传图像、权重、patch cache 或大型 raw dump。`third_party/dinov2` 是既有源码目录，只读记录来源，不删除、不移动、不纳入本轮结果。

## 必须核验的输入

1. 运行环境：`pwd`、Python 版本、CUDA/GPU、可用磁盘；记录环境摘要。
2. Qwen 权重：检查 `/home/nas/wangyq/model_weights/Qwen` 下实际目录、`config.json`、processor/tokenizer 和权重文件。确认它是可接收图像的视觉模型；如果目录是 text-only Qwen 或缺少视觉 processor，标记 BLOCKED 并只回报阻塞原因，不下载替代模型、不自行改变模型版本。
3. 读取本同步包中的 `ROUTE_SMOKE_MANIFEST_20260926.json` 和 `QWEN_OUTPUT_SCHEMAS_20260926.json`。
4. 核验路线 pano ID 能在 `candidate_route_steps.csv` 中找到，并按 `{panoid}_panorama_{view_index}.jpg` 从 `/home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per` 解析图像。不得使用 `{panoid}_{view_index}.jpg` 或 `v0/v1/v2/v3` 命名。
5. 固定 view 的绝对方向只使用 `(heading_from_api + 90*view_index) mod 360`。不要把 view_0..3 直接写成 front/right/back/left。

## 执行顺序

### 阶段 0：2 图 JSON/坐标 smoke

只使用 `main_03_dec` 和 `main_06_dec` 的一个固定视图，原始输入为 640x640。提示词要求最多 3 个可见候选；允许 `no_clear_candidate`；输出严格 JSON。不给 GPS、panoid、路线动作、reference、P/N/I、VLAD 分数或正确答案。保存原始回复、解析后的 JSON、失败原因、prompt hash、模型 revision 和 bbox overlay。

阶段 0 失败时立即 BLOCKED，保留诊断和最小复现，不进入后续阶段。

### 阶段 1：六个路线候选 case

对两条候选路线各运行 pre-decision、decision、post-decision 三个 case。当前输入为 640x640 四视角图；若使用单 view，必须在记录中写明 view index 和绝对中心 heading。候选只作为视觉事实提议，不输出或推断 gold action。

保存：

- `candidate_proposals.jsonl`（一 case 一行，遵循 schema）；
- `candidate_raw/`；
- `candidate_overlays/`；
- `run_manifest.json`、`environment.json`、`run.log`、`errors.jsonl`；
- 每一框的人审表模板，字段至少包含 `ACCEPT/EDIT/REJECT/UNCERTAIN`、终框、理由和邻近可指认性。

### 阶段 2：路线决策 smoke（只在阶段 1 产物完整后）

使用同一条路线的学习序列和一个当前决策观察，比较 `route_plus_current`、`current_only`、`route_shuffled` 三个条件；候选遮挡条件在框未人工审核前只能生成输入草稿，不能报告科学结果。候选出口使用匿名 option ID，至少两个合法非回头选项；模型端不看正确 action、panoid、GPS 或真实 edge 名称。

输出严格遵循 `route_decision` schema。评分脚本在模型外使用路线/道路几何核验 `chosen_edge_id`；不要用模型自己的理由当 gold。

## 运行和回报约束

- 长任务后台执行，实时写入 `run.log` 和阶段状态文件。正常运行期间不要向用户或本对话持续发送进度消息，不轮询 GitHub，不推送中间进度。
- 只有以下两种情况主动回报：
  1. 全部请求阶段成功，回报结果目录、阶段计数、模型/环境摘要、SHA-256 清单和需要人工审核的表；
  2. 出现无法继续的错误，回报 `BLOCKED`、第一处阻塞、最小复现命令、已完成阶段和建议动作。
- 即使成功，也不要声称路线动作已成为 gold、候选已成为地标或已经证明认知地图；结果必须标注 `smoke`/`provisional`。

## 预期输出目录

建议使用：

`/home/nas/wangyq/outputs/Paris_route_qwen_smoke_20260926/`

目录至少包含：

`candidate_proposals.jsonl`、`candidate_raw/`、`candidate_overlays/`、`route_decisions.jsonl`（若阶段 2 完成）、`run_manifest.json`、`environment.json`、`run.log`、`errors.jsonl`、`sha256sums.txt`、`HUMAN_REVIEW_REQUIRED.md`。

不要把上述大型目录复制进 GitHub；只回传轻量 manifest、摘要、错误和审核表路径/哈希。

## Prompt 入口

请在 `/home/wangyq/Nav_Lmk` 执行 `01_Navigational_Landmarkness_Cognitive_Map/sync/SERVER_CODEX_HANDOFF_20260926.md`。先读取根目录 `AGENTS.md`、active project 的 `PROJECT_CONTEXT.md`、`EXPERIMENT_DESIGN.md`、`DECISIONS.md`、`TODO.md` 和本同步目录四个文件。复述研究问题与本轮边界后执行：核验 GPU、磁盘、Python 和 `/home/nas/wangyq/model_weights/Qwen` 中已下载的 Qwen 模型；确认它是可接收图像的视觉模型，否则立即 BLOCKED。读取 `ROUTE_SMOKE_MANIFEST_20260926.json`，用 `/home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/{panoid}_panorama_{view_index}.jpg` 的 640x640 原图，先只做 main_03_dec 与 main_06_dec 两图 JSON/bbox smoke，再做两条路线的六个候选提议 case，最后在产物完整时做 route_plus_current/current_only/route_shuffled 三条件决策 smoke。不要重跑 G/14+VLAD，不改 P/N/I，不给模型 GPS、panoid、reference、VLAD 分数或 gold action；固定视图绝对朝向遵循 `(heading_from_api+90*view_index) mod 360`。将原始输出、解析 JSONL、overlay、人审模板、环境摘要、日志、错误和 SHA-256 写入 `/home/nas/wangyq/outputs/Paris_route_qwen_smoke_20260926/`。候选和动作只能标为 smoke/provisional。长任务后台运行并实时写日志；正常运行期间保持安静，只有全部成功或不可继续时才回报，回报中给出结果目录和 `HUMAN_REVIEW_REQUIRED.md`，或给出 BLOCKED 的第一处错误、最小复现和已完成阶段。
