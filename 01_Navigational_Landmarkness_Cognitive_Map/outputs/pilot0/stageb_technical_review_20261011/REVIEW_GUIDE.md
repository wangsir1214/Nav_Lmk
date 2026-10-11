# Phase 0 Stage B 技术审核说明（2026-10-11）

状态：`PREPARATION_NOT_EXPERIMENT_RESULT`。来源为服务器 Stage A `paris_phase0_stagea_20261011T070533Z_a01`，结果分支 `server-results/paris_phase0_stagea_20261011T070533Z_a01`，提交 `7c81f717cf7ca539725e0ca777bb0dc104f41f99`。本地叠框和控制框均为审核材料；没有运行遮挡或 DINO。

## 打开与填写

1. 打开同目录 `review_board.html`，逐题看原始红/蓝候选框及已经生成的红/蓝控制框。图板是本地技术图板；NAS 原始审核表仍为空。
2. 优先填写精简的 `MINIMAL_HUMAN_QC.csv`（20 行，每题一行）。`provisional_candidate_id` 已按冻结顺序选择：`c1` 几何通过则只列 `c1`；`c1` 几何失败而 `c2` 通过则暂列 `c2`；两者失败则留空。`human_accept_edit_reject` 填 `ACCEPT`（可见、框与描述基本对应）、`EDIT`（仅修客观框/描述错误）、`REJECT`（不可见、错误对象或不可修复）。如 `EDIT`，将最终 640×640 的 `[x0,y0,x1,y1]` 写入 `human_final_bbox_640`，说明原因。`TECHNICAL_REVIEW.csv` 是保留全部 40 候选的详细追溯表，可按需填写。不得按预测检索效应挑选。
3. `control_geometry_qc` 仅记录技术观察：是否越界、与目标重叠、互相重叠，或者覆盖另一个可见线索。后一种情形也要如实记录，不因它“看起来重要”而私下换框。`OTHER_PROPOSAL_OVERLAP_FLAGS.csv` 列出 8 个控制框与另一候选框交叠的情况，供 `other_proposal_overlap_qc` 字段参考。
4. `geometry_status=PASS` 只说明程序生成了三框，**不等于人审通过**。`AREA_LIMIT_FAIL` 和 `CONTROL_GEOMETRY_FAIL` 在当前冻结规则下不能直接进入 Stage C。若修改候选框，必须重新按同一规则生成三个控制框并重新审核，不能沿用旧框。
5. `c1` 是事先指定的主候选；若其几何或客观视觉 QC 不合格，可记录原因并核对事先提出的 `c2`。不要因为 `c2` 更像“好地标”而换。没有合格候选和三控制框的题保留为未运行，报告原因，不补造新候选。

## 预检结果

- 20 个 query、40 个候选；其中 18 个是旧 Full 正确的主分析视图，2 个是旧 Full 失败的诊断视图。服务器的 20 个 Qwen 请求均成功，但这不是候选有效性结论。
- 候选级几何检查：25 `PASS`、12 `CONTROL_GEOMETRY_FAIL`、3 `AREA_LIMIT_FAIL`。18 个主分析视图中，11 个 `c1` 几何通过；另外 5 个 `c1` 不通过而 `c2` 通过；剩余 2 个两个候选均不通过。两个诊断视图的候选均不通过。**这些是审核前的上限，不是最终合格题数。**
- 已通过的 25 套三控制框经独立范围、同尺寸、候选与控制不重叠、控制彼此不重叠复核，无此类错误。控制框与同图的另一 Qwen 候选可能重叠，具体见 `OTHER_PROPOSAL_OVERLAP_FLAGS.csv`。该标记仅是潜在混杂，不能据此事后重选控制框。
- `BrLJ2FJOw6JtoQks8TRVeQ__v1` 与 `xnVV6BHnFOXVpWAFGADsLA__v1` 是两个主分析视图，当前 `c1/c2` 均未能通过冻结几何规则；不要为了凑齐 18 题放宽容差。精简表中只有 16 行暂有几何可行候选，其余 4 行作为无可行候选保留。
- `fZ7bO6pDSX9hMw3mVdj-SA__v1` 与 `vpRGwoLifY8oPQ6oU_QPHg__v3` 为旧 Full 失败的诊断视图，且当前两候选均几何失败。不要把它们并入主分析。

## 审核边界

审核仅判断可见性、描述对应、bbox、遮挡几何。无需判断其是否真正有 landmark value；那要在候选/控制固定后由同一 DINO+VLAD observer 的配对干预检验。审核表填写并复核前，不启动服务器 Stage C。
