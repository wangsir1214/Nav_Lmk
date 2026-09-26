# Paris Candidate Route Human Review Guide

## 为什么不直接铺开全部图片

15 条路线包含 120 个 pano 和 480 张固定四视图。逐图罗列会丢失路线顺序、当前朝向和 decision-zone 语义，也容易把“视觉上显眼”误当成“对任务有用”。第一轮应以路线 board 为单位审查；只有通过 KEEP/ADAPT 的路线才从 ERP 重投影 route-aligned views。

## 第一轮：结构与视觉盲审

按以下顺序查看每条路线：

1. 打开 sequence board，确认 8 个 pano 是否构成可理解的短路线；
2. 打开 decision four-view board，确认是否真的存在多个合法出口；
3. 对照路线地图确认 provisional maneuver，但不要把它当作 gold action；
4. 填写 `_audit_outputs/candidate_route_review.csv`；
5. 暂不查看 `candidate_route_review_preliminary.csv`，避免被 Codex 初筛角色影响。

普通路线地图总览：[candidate_routes_overview.pdf](figures/candidate_routes_main/candidate_routes_overview.pdf)

Arc 路线地图总览：[arc_controls_overview.pdf](figures/arc_controls/arc_controls_overview.pdf)

## 普通路线

| Route | Provisional maneuver | Sequence | Decision four-view |
|---|---|---|---|
| main_01 | left | [sequence](figures/candidate_routes_main/main_01_sequence.jpg) | [decision](figures/candidate_routes_main/main_01_decision_4view.jpg) |
| main_02 | left | [sequence](figures/candidate_routes_main/main_02_sequence.jpg) | [decision](figures/candidate_routes_main/main_02_decision_4view.jpg) |
| main_03 | left | [sequence](figures/candidate_routes_main/main_03_sequence.jpg) | [decision](figures/candidate_routes_main/main_03_decision_4view.jpg) |
| main_04 | left | [sequence](figures/candidate_routes_main/main_04_sequence.jpg) | [decision](figures/candidate_routes_main/main_04_decision_4view.jpg) |
| main_05 | right | [sequence](figures/candidate_routes_main/main_05_sequence.jpg) | [decision](figures/candidate_routes_main/main_05_decision_4view.jpg) |
| main_06 | right | [sequence](figures/candidate_routes_main/main_06_sequence.jpg) | [decision](figures/candidate_routes_main/main_06_decision_4view.jpg) |
| main_07 | right | [sequence](figures/candidate_routes_main/main_07_sequence.jpg) | [decision](figures/candidate_routes_main/main_07_decision_4view.jpg) |
| main_08 | right | [sequence](figures/candidate_routes_main/main_08_sequence.jpg) | [decision](figures/candidate_routes_main/main_08_decision_4view.jpg) |
| main_09 | forward | [sequence](figures/candidate_routes_main/main_09_sequence.jpg) | [decision](figures/candidate_routes_main/main_09_decision_4view.jpg) |
| main_10 | forward | [sequence](figures/candidate_routes_main/main_10_sequence.jpg) | [decision](figures/candidate_routes_main/main_10_decision_4view.jpg) |
| main_11 | forward | [sequence](figures/candidate_routes_main/main_11_sequence.jpg) | [decision](figures/candidate_routes_main/main_11_decision_4view.jpg) |
| main_12 | forward | [sequence](figures/candidate_routes_main/main_12_sequence.jpg) | [decision](figures/candidate_routes_main/main_12_decision_4view.jpg) |

## Super-landmark stratum

| Route | Provisional maneuver | Sequence | Decision four-view |
|---|---|---|---|
| arc_control_01 | left | [sequence](figures/arc_controls/arc_control_01_sequence.jpg) | [decision](figures/arc_controls/arc_control_01_decision_4view.jpg) |
| arc_control_02 | right | [sequence](figures/arc_controls/arc_control_02_sequence.jpg) | [decision](figures/arc_controls/arc_control_02_decision_4view.jpg) |
| arc_control_03 | forward | [sequence](figures/arc_controls/arc_control_03_sequence.jpg) | [decision](figures/arc_controls/arc_control_03_decision_4view.jpg) |

这些 Arc 路线是 super-landmark 数据层，不是后续图像干预中的 matched control。

## 第二轮：仅处理保留路线

对第一轮 `KEEP` 或可修正 `ADAPT` 的路线：

1. 在米制 CRS 中复核 decision zone 和道路出口；
2. 从 ERP 按 route bearing 生成 front/right/back/left 四视图；
3. 填写 `route_aligned_view_quality_0_4` 和最终 `action_confidence`；
4. 冻结 strata 和排除理由；
5. 仅在 Go Gate 通过后进入 P1A/P1B。

