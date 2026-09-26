# P1A / P1B 任务规范与 Go Gate

## 阶段定位

这是巴黎 feasibility audit 后的最小行为原型，不是地标消融实验，也不是 RL 复现。目标是先确认：候选线索是否可被人稳定识别，并且在一个有明确目标的任务中与路线记忆/道路延续相关。

## P1A：候选地标诱发

### 输入材料

- 每条候选路线的 8 步 incoming/continuation sequence；
- decision-zone 四视角板；
- 简化地图、当前点、合法 outgoing road segments；
- 第一轮使用固定四视角，第二轮只对保留路线使用 route-aligned views。

### 被试标注

1. 指出会用于记忆或识别此处的视觉元素；
2. 选择 `object / structural / scene-level / mixed`；
3. 标注与哪一条出口或方向相关；
4. 评分辨识度、稳定性、空间相关性和可干预性（0--4）；
5. 写出排除理由：施工、眩光、远距离凯旋门、方向不清、时间不稳定或没有可编辑对象。

P1A 的输出称为 `human-elicited candidate landmark`，不能称为 verified landmark。

## P1B：Route continuation / route-memory choice

### 学习阶段

被试观看一条完整的 8 pano 路线，或观看包含 decision zone 前后信息的序列。路线 ID 和目标出口在学习阶段明确给出。

### 测试阶段

再次呈现 decision zone 的 incoming sequence 和四视角，并展示该 zone 的两个或更多合法 outgoing edge 选项。问题固定为：

> “刚才学习的路线在这里继续走向哪条道路？”

正确答案由学习过的路线定义，不由路线挖掘程序单独定义。记录选择准确率、反应时间、置信度，以及被试是否引用了某个候选线索。

### 最小比较

- 原图/原始路线；
- 仅在 P1A 已确认候选后，构造 removal、identity replacement、location replacement；
- 同图 matched-control 作为干预控制；
- Arc de Triomphe 路线单列为 super-landmark stratum，不作为 matched control。

## 人工审查表与 Go Gate

每条路线先填写 `_audit_outputs/candidate_route_review.csv`。在 route-aligned views 生成前，`route_aligned_view_quality_0_4` 保持 `PENDING`。

普通路线进入 P1B 的最低门槛：

- `spatial_relevance_0_4 >= 3`；
- `graph_task_support_0_4 >= 3`；
- `task_definition_fit_0_4 >= 3`；
- `action_confidence = confirmed`；
- route-aligned view 清晰，无遮挡、严重眩光或方向错误；
- 至少 8 条普通路线通过，且左/右/直行每类至少 2 条；
- 至少保留 2 条低显著度对照和 2 条具有可说明身份/结构线索的路线。

低显著度对照不要求存在可干预地标，但必须满足任务和动作门槛。Arc 控制只作单独的超级地标分析，不计入普通路线 Go Gate。

若门槛不足，结论只能是 `ADAPT` 或 `REPLACE`，不得进入身份--位置消融。

## 当前人审材料

- 普通路线总览：`_audit_outputs/figures/candidate_routes_main/candidate_routes_overview.png`；
- Arc 总览：`_audit_outputs/figures/arc_controls/arc_controls_overview.png`；
- 每条路线的 sequence 与 decision four-view board 位于对应目录；
- 机器筛选仅保存在 `candidate_route_review_preliminary.csv`，不覆盖人工表。

