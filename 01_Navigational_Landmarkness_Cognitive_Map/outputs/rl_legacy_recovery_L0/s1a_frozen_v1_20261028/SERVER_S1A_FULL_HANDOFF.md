# SERVER S1-A FULL HANDOFF

状态：READY_FOR_SERVER_S1A_INTEGRATION_SMOKE。本 handoff 只开放 Step 1 的两题 runner integration smoke；Step 2 正式24题 Full rollout 未获授权，必须等待研究者另行书面批准。

## 1. 获取并核验交接包

仓库：wangsir1214/Nav_Lmk  
分支：codex/rl-ur85-s1a-frozen-v1-20261027  
交接提交：以本分支实际 HEAD 为准；运行前记录完整 commit SHA。  
目录：01_Navigational_Landmarkness_Cognitive_Map/outputs/rl_legacy_recovery_L0/s1a_frozen_v1_20261028/

服务器应在旧工程隔离子目录下独立 checkout，例如 /home/wangyq/UrbanNav_neo_fromPC/landmark_probe/s1a_handoff_checkout/；不得在旧工程根目录运行 reset/clean/checkout。逐文件核对 S1A_MANIFEST_HASHES.json，并验证冻结清单 SHA-256 为 f7bec0034a33345e0537b95794f78c6562db89b15532679785108ca29f636e3b。缺件、SHA 不符、提交来源不同即停止。

## 2. 固定执行来源

- 历史执行代码根目录：/home/wangyq/UrbanNav_neo_fromPC。
- 只读 NAS 数据根目录：/home/nas/wangyq。
- S0 隔离 Python：/home/wangyq/UrbanNav_neo_fromPC/landmark_probe/s0_environments/urbannav_ur85_s0_20261025T163610Z_a01/venv/bin/python。
- S0-R checkpoint：/home/wangyq/UrbanNav_neo_fromPC/WYQ/trained_models/ppo/UrbanNav_deepmind_WYQ_dpt30_20250416-032336_80000.pt，SHA-256 fef170f6a01c9c9ba2361b7c7b81a4ddb9f0311a145766ed7d07006f7dc28a6e。
- 16视图源图、3058点 JSON、SHP 五件套、heading CSV 必须使用 S1A_MANIFEST_HASHES.json 指定版本和 SHA；从批准的 NAS 路径读取，禁止重新扫描全图库。
- S1-ENV-R1 fixed-goal adapter SHA-256 d8af5cce993f3872b449edd4c1eaa185e38950a0854fecb2adc6a8a7b198c29d。不得修改旧源码；如复制到新隔离 adapter 目录，逐字节 hash 必须相同。

## 3. Step 1 — PPO runner integration smoke

在新目录新增独立入口：
/home/wangyq/UrbanNav_neo_fromPC/landmark_probe/s1_adapters/s1a_full_runner.py。
该入口通过 S0-approved strict loader 加载 UR-85，复用经 hash 核验的 fixed-goal adapter，不执行训练、不调用 Neptune。

预先固定的两条诊断 task：
- S1A-DRAFT-001：100–200m 档；
- S1A-DRAFT-024：400–550m 档。

每条以冻结 seed 做两次完整独立 Full 执行，用于检查接口和同 seed 重复性；共4条诊断轨迹，不纳入正式24题统计，不据表现替换题目。命令接口建议：

    RUN_ID="ur85_s1a_integration_$(date -u +%Y%m%dT%H%M%SZ)_a01"
    PYTHON=/home/wangyq/UrbanNav_neo_fromPC/landmark_probe/s0_environments/urbannav_ur85_s0_20261025T163610Z_a01/venv/bin/python
    HANDOFF=/home/wangyq/UrbanNav_neo_fromPC/landmark_probe/s1a_handoff_checkout/01_Navigational_Landmarkness_Cognitive_Map/outputs/rl_legacy_recovery_L0/s1a_frozen_v1_20261028/
    OUT=/home/wangyq/UrbanNav_neo_fromPC/landmark_probe/s1a_integration_runs/$RUN_ID
    mkdir -p "$OUT"
    "$PYTHON" /home/wangyq/UrbanNav_neo_fromPC/landmark_probe/s1_adapters/s1a_full_runner.py \
      --manifest "$HANDOFF/S1_EPISODES_FROZEN_v1.jsonl" \
      --episode-ids S1A-DRAFT-001,S1A-DRAFT-024 \
      --mode integration-smoke --repeats 2 --output-dir "$OUT"

该命令是目标入口规格，不是现存已验证 runner。服务器必须先实现并 code-review 新入口，再执行 Step 1。结果只写入本人 Docker 的 /home/wangyq/UrbanNav_neo_fromPC/landmark_probe/s1a_integration_runs/<UTC_RUN_ID>/；NAS 保持只读。

### Step 1 必须通过的检查

1. 容器、源提交、checkpoint、模型结构、legacy source/data hashes、Python 环境与 S0/S1-ENV 记录匹配；不使用 NAS 代码/权重覆盖 Docker。
2. 两个 frozen task 的 start、goal、Goal vector、initial yaw/view 00、输入图像 hash、距离、success 和 max-step 规则逐项与 manifest 相同。
3. Goal float64 observation 到原模型 batch/cast 的 dtype/shape/value 路径与 S0-approved contract 一致；不新增 normalize/clip/resize。
4. 原双 GRU、prev action、prev reward、reset mask 独立初始化和逐步更新；同一 episode 结束后无 hidden/state 泄漏。
5. 源码确认 actor_critic.act() 使用 categorical stochastic sampling。对每个 task 设置 Python、NumPy、Torch CPU/CUDA RNG；保存实际 seed 和 backend 状态。
6. 相同 checkpoint、设备、task、seed 重复运行时，对齐每一步起始 state/observation、recurrent diagnostics、action distribution、sampled action、reward、state transition、termination。若任一关键输出无法重复，或采样不是批准的 categorical 行为，立即停止并交 BLOCKED/PARTIAL 报告。
7. 每题 reward amplitude 在初始化时按历史 _shortest_paths(fixed_goal, fixed_start) 计算和记录；其余21个候选源 null 不做任何推断。检查 reward 和成功/timeout 优先级。
8. 不以成功率做 smoke 通过门槛，不按轨迹表现改题。Step 1 不是正式 pilot 结果。

建议产物：新 runner、运行配置、source/checkpoint/hash report、Goal dtype report、RNG/repeatability report、4条诊断 trajectory 摘要和完整本地日志、final gate JSON。公开仓库只回传脱敏摘要，不上传 hidden tensors、完整轨迹不必要的内部路径或权重。

Step 1 失败时保留所有已有产物，停止。不得自动换 UR-79/UR-88、改 manifest、goal、seed、reward 或 success 边界。Step 1 通过后也停止并等待人工审核；不得自动运行 Step 2。

## 4. Step 2 — 正式24条 Full 评价（未授权）

只有研究者后续明确授权后才能执行。获批后从全新 run 起点重新运行 frozen manifest 的全部24条 Full task（包括001与024），每题独立 reset 和 seed；Step 1 的4条轨迹完全不计入。不得执行 NoImage、ShuffledImage、遮挡或训练。

## 5. 结果解释边界

历史训练 reward、S0 单帧 smoke、S1 environment-only smoke 和 Step 1 runner smoke 都不能替代正式导航成功率。即便 Step 2 Full 成功，也不能单独证明视觉依赖或功能地标；NoImage/ShuffledImage 和视觉区域因果干预属于后续独立授权阶段。

