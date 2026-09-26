# 15 条路线最小人工确认

本轮只填写 `HUMAN_MINIMAL_CONFIRMATION.csv`，旧空白表和 preliminary 表保持原样。
每条只打开下面两个 board，不要求再找原始图片或重复计算年月、距离、heading、join 和图统计。
这些是有答案标签的审核材料，不是正式被试刺激。

## 四问

1. Q1：除已标出的月份/密采样问题外，这段街景是否像可学习的短路线？
2. Q2：decision zone 与所标行动在街景中是否可理解？有标志/地图冲突时填 UNSURE，交回机器核查，不要求你计算合法性。
3. Q3：机器建议的候选、低显著度对照或 super-landmark 角色是否合理？低显著度不等于没有任何线索。
4. Q4：机器已指出的施工、眩光、季相，以及你另外看到的严重混淆，在建议的保留/修正范围内是否可接受？需要未证实替换图才能解决时填 UNSURE。

Q1–Q4 只用 `YES / NO / UNSURE`。`human_final` 用 `ACCEPT / REJECT / DISCUSS`，备注可一句话。
ACCEPT 表示接受该路线区域/角色进入后续定向修正，不表示当前图册能直接当正式刺激，更不表示地标功能已验证。
建议四项 YES 才 ACCEPT；关键问题 NO 且不可修复才 REJECT；其余 DISCUSS。表中人填项全部留空，不替你作答。
机器只要求确认科学语义，技术字段和新材料生成由 Codex 负责。重采样/出路修正后的实质变化案例，之后仍须快速检查其正式材料，不能承诺今天确认后永不再看。

## 每条的两个入口与重点

| Route | 机器建议 | 角色/重点 | Sequence | Decision |
|---|---|---|---|---|
| main_01 | ADAPT / HIGH | structural_candidate：保留结构候选；先按月份和距离重选观察点。只用现有 8 点的 9 月子集仍需检查决策前后覆盖，不能直接视为已修好。 | [顺序板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/candidate_routes_main/main_01_sequence.jpg>) | [路口板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/candidate_routes_main/main_01_decision_4view.jpg>) |
| main_02 | ADAPT / HIGH | identity_structural_reserve：需时间重采样并决定施工是否可隔离；红绿店招可能有身份线索，不能让防护网成为主要记忆答案。当前选中 8 点没有横跨入口/出口的单月充分序列。 | [顺序板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/candidate_routes_main/main_02_sequence.jpg>) | [路口板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/candidate_routes_main/main_02_decision_4view.jpg>) |
| main_03 | ADAPT / HIGH | structural_candidate：去掉或替换 2012-06 的 step 1，并解决其余月份混合。空间上 8 点充分分离，但有一次 20.77m 间隔，需要检查学习序列跳跃而非盲目补点。 | [顺序板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/candidate_routes_main/main_03_sequence.jpg>) | [路口板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/candidate_routes_main/main_03_decision_4view.jpg>) |
| main_04 | ADAPT / HIGH | low_landmark_control_candidate：保留低显著度对照候选。至少三对相邻点不足 2m，应合并呈现/重选观察点；四个月份不应通过重复相同位置来凑成 8 步。 | [顺序板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/candidate_routes_main/main_04_sequence.jpg>) | [路口板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/candidate_routes_main/main_04_decision_4view.jpg>) |
| main_05 | ADAPT / HIGH | structural_candidate：结构路线有潜力，但现有 8 点只有约 4 个 5m 分离观察，需时间/距离重选并剔除严重眩光观察；不预设可做 object identity swap。 | [顺序板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/candidate_routes_main/main_05_sequence.jpg>) | [路口板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/candidate_routes_main/main_05_decision_4view.jpg>) |
| main_06 | ADAPT / HIGH | scene_structural_candidate：优先尝试已有 5 月子集和相邻同月观察；需保留路口前后证据。场景/结构价值不因 object-style 编辑困难而下降。 | [顺序板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/candidate_routes_main/main_06_sequence.jpg>) | [路口板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/candidate_routes_main/main_06_decision_4view.jpg>) |
| main_07 | ADAPT / MEDIUM | low_landmark_control_candidate：保留低显著度角色待定；先解决交通标志与现有 OSM 方向可能不一致的问题，再重采样跨月份及不足 1m 点。不能为了保住第二个 low control 而强行确认。 | [顺序板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/candidate_routes_main/main_07_sequence.jpg>) | [路口板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/candidate_routes_main/main_07_decision_4view.jpg>) |
| main_08 | ADAPT / HIGH | scene_structural_identity_candidate：五个拍摄月份和近重复观察需要重采样；有候选线索但其跨月广告/店面稳定性未验证，不能将场景多样性等同于干预有效性。 | [顺序板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/candidate_routes_main/main_08_sequence.jpg>) | [路口板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/candidate_routes_main/main_08_decision_4view.jpg>) |
| main_09 | ADAPT / HIGH | construction_confounded_reserve：不计入当前可信普通直行门槛。只有找到同路段可用、施工不支配的既有观察并复核，才可回到普通基线；否则换路线或隔离为施工层。 | [顺序板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/candidate_routes_main/main_09_sequence.jpg>) | [路口板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/candidate_routes_main/main_09_decision_4view.jpg>) |
| main_10 | ADAPT / HIGH | distant_super_landmark_reserve：移出干净普通路线计数，可讨论远距离 super-landmark 层。重投影不能保证消除全景中的凯旋门，不应通过任意裁掉视角伪装成普通路线。 | [顺序板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/candidate_routes_main/main_10_sequence.jpg>) | [路口板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/candidate_routes_main/main_10_decision_4view.jpg>) |
| main_11 | REJECT / HIGH | P1A_or_place_memory_only_current_zone：REJECT 仅指当前 decision-zone P1B 多出口选择材料。OSM 排除返回来路后仅1个合法出口，forward几何正确也不产生有歧义选择。保留原数据供 P1A/地点记忆；另选路口会构成新 case。 | [顺序板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/candidate_routes_main/main_11_sequence.jpg>) | [路口板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/candidate_routes_main/main_11_decision_4view.jpg>) |
| main_12 | ADAPT / HIGH | identity_candidate_with_confound_gate：纠正旧预审中仅强调店招的判断。保留 identity 候选，但必须同月重选并压低施工/眩光混淆；未证明旧店面跨期稳定或能自然 identity/location 编辑。 | [顺序板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/candidate_routes_main/main_12_sequence.jpg>) | [路口板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/candidate_routes_main/main_12_decision_4view.jpg>) |
| arc_control_01 | ADAPT / HIGH | super_landmark_stratum：仅作 super-landmark stratum；去近重复和同月取样后复核。不是 matched control，也不能计入普通路线门槛。 | [顺序板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/arc_controls/arc_control_01_sequence.jpg>) | [路口板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/arc_controls/arc_control_01_decision_4view.jpg>) |
| arc_control_02 | ADAPT / HIGH | super_landmark_stratum：时间最容易先局部修正的 Arc case：已有0-5同月跨越路口，但仍须确认转弯后的学习长度、保留观测和车辆遮挡。不能仅截断为6点就宣称正式材料 READY。 | [顺序板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/arc_controls/arc_control_02_sequence.jpg>) | [路口板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/arc_controls/arc_control_02_decision_4view.jpg>) |
| arc_control_03 | ADAPT / MEDIUM | super_landmark_stratum_with_confounds：仅作超级地标层待定，复核禁入标志、OSM方向与拍摄年份差异；明确顶部覆盖是否构成额外身份线索，再做时间重采样。 | [顺序板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/arc_controls/arc_control_03_sequence.jpg>) | [路口板](<F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/_audit_outputs/figures/arc_controls/arc_control_03_decision_4view.jpg>) |

## 机器标签的边界

KEEP：角色和序列可保留，只需普遍适用的 route-aligned 重投影等标准制作。
ADAPT：仍值得保留该区域/角色，但有路线特定的时间、采样、混淆、合法性或分层问题。
REJECT：当前 P1B case 不成立；不删除原数据，也不否定它用于 P1A/地点记忆的价值。
HIGH/MEDIUM/LOW 是机器对上述建议及问题证据的把握，不是对修复必定成功或地标功能的信心。

语义评分0–4的一般含义：0当前缺少支持；1弱或严重受限；2部分支持但需实质修正；3有清晰可见支持；4该维度非常清晰。
sequence continuity 看当前观测是否连贯，visual diversity 只看可见差异；landmark availability 仅评分候选可辨认性。
spatial relevance 只指候选与路口/道路关系的可见性，不代表功能效应。
task ambiguity 是“存在合理相似替代出口”的启发式，未经被试准确率检验；0也包括没有第二个非返回出口。
intervention feasibility 评的是现有像素下自然受控编辑的预估，未实际编辑。结构/场景候选低分不等于没有科学价值。
graph support 使用当前历史 OSM/图结构证据，task fit 评当前学习/测试素材条件，非未来修复后的假想得分。
`action_confidence=confirmed` 仅指几何、历史OSM和可见道路未发现冲突的机器确认，仍非人工 gold；uncertain 不必表示左/右计算错误。
`NOT_OBSERVED_IN_BOARDS` 只约束这两张板，不能断言整条路线所有方位没有超级地标。
Arc 三条以及 main_10 的远距 Arc 风险必须分层；它们不是同图 matched-control。
