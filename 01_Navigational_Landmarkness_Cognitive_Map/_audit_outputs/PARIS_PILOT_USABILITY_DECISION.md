# Paris Pilot Usability Decision v2

日期：2026-09-17。结论：**provisional ADAPT**。

本轮完成时间、空间采样和逐图机器预审，已足以作可行性分流，不等待地标消融。
ADAPT 的具体含义是：保留 Paris，修正现有数据的观察采样，并在同一 Paris 资产中补挖普通直行/低显著度候选。
不是“继续不确定地等人工”，也不是已经获准运行正式 P1A/P1B。现在停止，等待四问人工确认。

## A. Raw Paris source data

**USABLE_WITH_FIXES**。

- 保留 ERP、固定四视角、heading、原始 metadata 和图。当前 120 个 selected pano 的年月三源一致，heading 与 route steps 一致；120 ERP 和 480 固定视图经授权 Z 盘读取复核存在。
- Z 盘 heading 文件与附件中的 3,059 行 metadata SHA256 相同。此前全图 3,058 节点的连接完整性及 heading 像素审计作为历史证据沿用，本轮不冒称重新检查了全量 12,236 张图。
- 所有 15 对本地图册和两张总览地图本轮已直接查看像素；这不是外部 VLM 批处理，也不是正式人工标注。
- 原始历史坐标、API 返回拍摄位置、贴路图坐标分开保留。主距离使用 API 坐标，经 EPSG:2154 计算；历史原始坐标另列敏感性结果。
- 图仍是无向 pano 索引，不是完整交通行动图。仅清理入选 decision zones，核对历史 one-way 与像素路牌即可推进局部 pilot；本轮不重建全城环境。
- 既有四视角生成脚本的完整 provenance 仍缺失，方向关系沿用已验证结论。正式 stimulus 需从 ERP 重投影并留存参数和 hash。

没有发现足以否定 Paris 的影像/heading/metadata 根本损坏。数据使用/编辑/对外再分发许可本轮未作法律核验，不能据“文件可读”宣称已获发布许可。

## B. Current 15-route candidate pool

**NEEDS_REMINING**，但仍值得用当前 15 对图册做一次快速人工确认。该状态不是要求扔掉15条重新开始。

机器预审：**KEEP 0 / ADAPT 14 / REJECT 1**。这里 KEEP 指不需要路线特定修正，所有当前序列都有时间或采样问题，因此没有直接 KEEP。

| 范围 | KEEP | ADAPT | REJECT |
|---|---:|---:|---:|
| 普通12条 | 0 | 11 | 1 |
| Arc超级地标3条 | 0 | 3 | 0 |

高置信 ADAPT：main_01–06、main_08–10、main_12、arc_control_01–02。
高置信 REJECT：main_11，仅拒绝当前 P1B 路口选择 case；原数据和 P1A/地点记忆用途保留。
中置信 ADAPT：main_07、arc_control_03，主要有可见禁入标志与历史 OSM 出口语义需要核查。
置信度指对建议及现存问题的把握，不代表一定修好，更不代表地标有效。

### 与旧审计相比的新证据

1. 15/15 全部混月，main_03 跨25个月。时间字段完整不是时间一致。
2. 105个相邻对中37个小于5m、16个小于2m、8个小于1m；5m规则下只有84个空间分离代理观察，不是120个独立空间位置。
3. 采用道路 u/v/oneway 重新列举出口后，main_11 排除返回来路只剩1个出口。过去“至少2个合法出口”没有排除返回边，不能保证任务有两个前进选项。其余14个zone在该规则下有2–4个非返回选项。
4. API未吸附坐标的长基线入/出方向复算，15/15仍与旧 left/right/forward 标签一致。这支持几何标签，不足以把它们升级成 gold。
5. main_10 的远处凯旋门在 decision view 0 明确可见，应移到远距超级地标备用层，不计普通直行门槛。
6. main_12 的钢琴店招确实清楚，但脚手架及强光切换也清楚；main_09 施工和湿路变化明显，二者不能凭候选显眼就免除混淆审查。
7. arc_control_02 的凯旋门受树和大巴局部遮挡，并非每一步都支配画面；arc_control_03 的凯旋门顶部有覆盖设施。三条仍属于 super-landmark stratum，不是 matched control。

### 普通路线的计数边界

- 优先继续审查 main_01–08 与 main_12，共9条候选区域：left4、right4、forward1。这只是区域/角色保留意向，不是已证明9条可修复。
- main_09 为施工混淆备用，不先计入合格直行；只有找到可接受的原有观察并复核才能恢复计数。
- main_10 不计普通路线；main_11 当前P1B case拒绝。
- low-landmark control候选是 main_04/07。main_04需去冗余，main_07尚有道路合法语义问题，不能预先宣称已有两个通过的对照。
- 至少 main_01/03/05 有清楚的结构候选；main_12有可读身份候选。视觉上可辨认不等于减少任务不确定性已经被验证。

NEEDS_REMINING 的核心是普通直行和可靠对照不能被当前数量表保证，且重采样要加入月份约束。
先对通过快速确认的区域做针对性重选，缺项再在已有211候选/全Paris索引中补挖，不扩大城市或调用模型。

## C. Final P1A/P1B experimental stimuli

**REQUIRES_REPROCESSING**，不是 READY，也未到 REQUIRES_NEW_DATA。

所需“重处理已有数据”如下，全部是后续任务，本轮没有执行：

1. 联合拍摄年月与实际间距选择 observation points，优先同月。保留决策前、决策位置、决策后证据，不再机械要求8个pano；统一学习时长/呈现量。
2. 排除 main_03 的跨年点。施工、严重眩光、季相突变需要选替代观察或隔离，不用图像编辑假装消除采集差异。
3. 明确出行模式。当前合法性沿用原挖掘的 OSM 机动车单行假设，不等于行人权限，也不保证与2014年路牌同时期。main_07/arc_control_03的可见标志需先核查，不为通过门槛临时改为行人任务。
4. 在通过的 decision zones 中列出不含返回来路的实际出口，复核路牌、道路口形状及图的连接语义；保留所有备选出口，不能只检查正确路线的那条边。
5. ERP重投影为FOV=90度四视角。**测试decision frame使用进入路口的观察朝向，不以被选中的下一条出口作为front**；在各备选答案之间视图/顺序保持相同，避免泄漏。局部角仍为 `(target_heading - H) mod 360`。
6. 生成参数/来源记录：ERP哈希、heading文件版本、输入pose、FOV/pitch、尺寸、插值、JPEG、时间、可用出口。去掉审核板中的动作答案、红框或路线文字等泄漏标签。
7. 对选中素材修正UTF-8道路显示名、形成selected-route action graph，不覆盖原始路线与图。
8. 冻结角色和学习后续选择协议。学习过的路线才定义测试答案；无目标看路口猜动作不成立。基线还可能使用转向/运动记忆，不能据此证明地标因果作用或完整认知地图。
9. 正式呈现前复核新增材料的方向、出口可见性、学习长度和混淆；需要人类实验时另行确认伦理/同意及数据使用边界。

### 现有数据能修到什么程度：证据而非保证

只检查当前8点已有的同月子集，不新增数据，可找到同时有至少2个入口侧点、2个出口侧点和4个5m分离代理观察的7个子集：

| Route | 年月 | 原step子集 | 限制 |
|---|---|---|---|
| main_01 | 2014-09 | 0,3,5,7 | 可保留原decision；仍需检查学习长度和投影 |
| main_06 | 2014-05 | 1,3,4,5,6 | 可保留原decision；仍需控制呈现量 |
| main_10 | 2014-09 | 1,3,4,5,6 | 时间可减混，但不能消除凯旋门角色 |
| main_11 | 2014-09 | 0,1,2,4,7 | 不含原decision；不能修复单出口问题 |
| main_12 | 2014-09 | 0,2,4,6,7 | 不含原decision；需新观察pose和眩光审核 |
| arc_control_01 | 2014-09 | 0,3,4,5 | 仍有逆光；仅超级地标层 |
| arc_control_02 | 2014-09 | 0,1,2,3,4,5 | 局部可行性较强；出口学习长度待核查 |

这些是metadata子集可用性证据，不是新采样路线已经生成或验证。main_02/03/04/05/07/08/09/arc_control_03 尚无满足此粗筛的当前8点单月子集；须查同路段现存点或重新挖掘，不能猜测替代图一定存在。

## Provisional Go Gate

| 条件 | 本轮证据 | 判定 |
|---|---|---|
| >=8普通路线可保留/修正 | 9个优先区域值得继续，但未证实修复后数量 | 未通过，条件性潜力 |
| left/right/forward各>=2 | 优先区域4/4/1；直行备用main_09有高混淆 | 未通过 |
| >=2 low-landmark controls | main_04/07是候选，07动作语义未解决 | 未通过 |
| >=2 identity/structural候选路线 | 01/03/05等有可见结构候选 | 候选层通过，不是功能证据 |
| learned-route continuation逻辑成立 | 学习阶段提供路线目标，测试选延续出口 | 设计层通过，表现未测试 |
| 时间/采样可用现有数据解决 | 部分同月子集存在，不能覆盖全部门槛 | 部分支持，需处理验证 |
| 不必重采全部Paris | 未发现源级致命缺损 | 目前无重采依据 |

**因此选择 ADAPT。** GO需要先补齐普通直行/对照，并证实定向重处理后的可用数；不要求等到消融有显著结果才判断GO。
REPLACE目前证据不足。只有在既有数据定向重采样/补挖后仍严重不足，或权限/heading/图像出现根本不可修复问题时再考虑换数据。
这些数量门槛是feasibility启发式，不是样本量/统计功效论证。

## 人工现在只做什么

使用 `HUMAN_MINIMAL_REVIEW_GUIDE.md` 的15对链接，在 `HUMAN_MINIMAL_CONFIRMATION.csv` 逐条确认路线连贯、路口/动作合理、候选/对照角色、重大混淆是否可接受。
四问用YES/NO/UNSURE，结论用ACCEPT/REJECT/DISCUSS。机器未代填任何人工答案。
ACCEPT是同意继续保留/定向修正的判断，不能越过本报告的重处理和正式材料质检门槛。

本轮不调用VLM、不做移除/身份/位置编辑、不运行人类实验、不修复或训练UrbanNav、不改Proposal主线、不删除原数据。
所有候选仍为 candidate，尚无 verified landmark。

## 复现与证据文件

数值脚本：`../_audit_work/audit_route_feasibility_v2.py`；逐图观察：`../_audit_work/route_visual_observations_v2.json`；表和报告构建：`../_audit_work/build_route_review_v2.py`。
数值命令、软件版本、ZIP/成员/原始图哈希、30板路径和哈希、出口列表及同月子集见 `route_feasibility_v2_provenance.json`。
注意数值脚本重跑会刷新本轮新CSV，应随后运行review builder恢复视觉备注；builder发现人工四问已有填写时拒绝覆盖。

```powershell
$auditPython = 'C:/Users/Admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$auditProject = 'F:/Codex_local/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map'
& $auditPython "$auditProject/_audit_work/audit_route_feasibility_v2.py" --archive 'D:/BaidudiskDownload/Paris_check_for_Codex.zip' --graph 'F:/Codex_local/Nav_Lmk/98_Others/kl.Line_Points_3.json' --output-dir "$auditProject/_audit_outputs" --image-root 'Z:/wangyq/GSV_Paris' --remote-heading 'Z:/wangyq/Street_view_and_points_Paris/GoogleAPIMETADAT/Paris_Points_heading_3059/Paris_Points_heading_3059.csv'
& $auditPython "$auditProject/_audit_work/build_route_review_v2.py" --output-dir "$auditProject/_audit_outputs" --observations "$auditProject/_audit_work/route_visual_observations_v2.json"
& $auditPython "$auditProject/_audit_work/validate_route_feasibility_v2.py" --output-dir "$auditProject/_audit_outputs"
```

本地新增pyproj依赖隔离在 `_audit_work/feasibility_deps/`，没有修改bundled runtime。首次安装命令为 bundled Python `-m pip install --target <project>/_audit_work/feasibility_deps pyproj==3.7.2`。
