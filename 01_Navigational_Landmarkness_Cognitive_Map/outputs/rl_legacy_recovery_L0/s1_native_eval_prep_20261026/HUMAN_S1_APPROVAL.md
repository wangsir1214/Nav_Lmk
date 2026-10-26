# S1 人工审核决定

审核人：研究者
确认日期：2026-10-26
范围：记录研究者决定，不构成机器验证或环境结果。

## 决定

| 项目 | 决定 | 说明 |
| --- | --- | --- |
| `S0_LOCAL_REVIEW` | `APPROVE` | 认可 S0 技术恢复结论及其声明边界。 |
| `S1A_FULL_ONLY_FIRST` | `APPROVE` | 后续正式评价先做 Full；本次不授权 Full rollout。 |
| `EPISODE_COUNT_24` | `APPROVE_AS_DRAFT` | 认可 24 条探索性候选，不代表冻结有效 episode。 |
| `DISTANCE_BINS_100_550M` | `APPROVE_AS_DRAFT` | 暂用 100–200、200–300、300–400、400–550m 四档，每档六题；服务器须按运行坐标重算。 |
| `JSON_PROXY_COORDINATES_PENDING_SHP_JOIN` | `APPROVE_CONDITIONAL` | 核对 JSON `pos`、SHP geometry、SHP 经纬度属性和 runtime 使用字段。因道路投影产生的差异不自动视为损坏；影响任务、Goal 或成功边界的差异须返回研究者审阅。 |
| `FIXED_GOAL_EVALUATOR_SHIM` | `APPROVE_FOR_ENV_SMOKE_ONLY` | 可新增独立固定单目标 adapter 做环境 smoke；不修改历史源码，并提供与原 `evaluate()` / `CourierGame` 的 semantics diff。 |
| `SUCCESS_RADIUS_LT_100M` | `APPROVE` | 固定 Goal 距离首次严格小于 100m 时成功并立即终止；核查并报告历史代码边界差异。 |
| `MAX_STEPS_1000` | `APPROVE` | 本轮单目标评价使用 1000 个环境动作上限，不宣称完整复原历史评价协议。 |
| `STOCHASTIC_CATEGORICAL_POLICY` | `APPROVE_FOR_FUTURE_FULL` | 后续 Full 可采用固定随机种子的 categorical sampling；本轮不调用 PPO。 |
| `SERVER_ENVIRONMENT_ONLY_SMOKE` | `APPROVE` | 明确授权无 PPO 的环境、数据与 adapter 检查，可用预定动作核对状态转移。 |
| `SERVER_S1A_FULL_ROLLOUT_LATER_APPROVAL` | `DEFER_NOT_AUTHORIZED` | environment smoke 经研究者审核后，Full rollout 仍须另行授权。 |

## 权限边界

本次授权只覆盖 environment-only smoke。服务器不得加载或调用 PPO，不得做策略 rollout、训练、NoImage/ShuffledImage、SAM 或区域遮挡。24 条任务继续保持 DRAFT；不得因 smoke 结果自动补题、改难度或冻结任务。

以上决定均记录为研究者于 2026-10-26 确认。这些决定是人工审核意见，不是机器验证结论，也不表示相关环境或数据检查已经通过。
