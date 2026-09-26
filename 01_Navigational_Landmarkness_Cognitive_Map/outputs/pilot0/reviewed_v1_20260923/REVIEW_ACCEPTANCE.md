# 人工复核检查：可以进入开发集完整图基线

日期：2026-09-23。任务版本：paris_local_v1_20260923。原草案及用户导出原件未覆盖。

## 检查结论

两份导出的132行逐字段完全一致，JSON任务ID和复核指纹匹配；没有重复ID、漏项、空白审核人或非法字段。所有确认positive均满足clear/partial、usable和非空依据。数据条件已满足本轮开发集DINOv2+VLAD baseline；GPU环境、权重、词典和实际提取实现仍待服务器核验。

注意132是“配对审核案例”，不是132个独立query。原任务有48个query视图；同一个query可能对应多对人工审查记录。

| 审核变化 | 对数 |
|---|---:|
| 原positive继续positive | 80 |
| 原positive改ignore | 16 |
| 原negative继续negative | 24 |
| 原ignore继续ignore | 10 |
| 原ignore改positive | 2 |

人工确认共82对positive。16个否决的候选均转ignore，没有转成negative。4个query的两个原候选均被否决，按事前规则剔除：R071/R072、R075/R076、R091/R092、R095/R096对应的query。完整view_id见data/excluded_queries.csv。

## 整理后实际实验规模

| 项目 | 数量 |
|---|---:|
| Query视图 / 所属pano | 44 / 12 |
| 固定reference视图 / 所属pano | 168 / 42 |
| 需要提取特征的图像 | 212 |
| 完整query×reference关系 | 7392 |
| Positive / Negative / Ignore | 82 / 6160 / 1150 |
| 每query有1 / 2 / 3个positive | 8 / 34 / 2个query |
| 每query的negative | 140 |
| 排名时有效图库大小 | 141–143 |

六个道路组仍全部保留：D01–D04各8个query，D05、D06各6个query。原reference图库未删改，gallery_id保持gallery_e31f8e090f9576a11a7b。全量索引和空间分组未扩展，未再次扫描Z盘。

## 两个边界正例怎样处理

- R123：32.5m，用户确认纵深变化但可对应同一地点建筑。复查完整图，可见同一街道尽端立面、红色雨篷以及右侧街墙。
- R125：27.2m，用户确认画面边缘的商店对应。复查完整图可见Petit Bateau店面/字样位于两图相反边缘及邻接立面。

25m是提出候选的开发窗口，视觉审查可确认窗口外的实际对应。因此将这两对明确记录为人工确认的边界例外，不全局放宽阈值，也不把其余未审ignore提升为positive。两对对应的query原本已有合格positive，没有靠例外挽救缺正例题目。

主结果使用82对positive；另做一项预先规定的敏感性分析：仅将R123/R125恢复ignore，仍用同一44个query和168个reference，剩80对positive。直接重评分即可，不需重新提取特征。该比较检查局部边界例外是否左右总体结论。

## 证据强度与当前用途

这是可复现的、单人辅助审核的开发任务，不是独立确认性benchmark。审核人为wyq；104条依据为“认可预审提示/回答”，本地已将所引用的具体Codex提示展开保存到effective_evidence，同时保留原始文字和evidence_mode。不能把这些记录称作无提示盲审、两个独立标注者共识或人机一致性评估。

82个positive中62个clear、20个partial。少数保留项的理由较概括，例如R019、R027、R035、R084；保留用户原判定与原理由，不伪造更强证据。后续看失败案例时可针对实体身份再核对，标签修订须版本化并重跑全部条件，不能为了提高分数挑题。无需先重做整批人审才能开展本次开发基线。

24项negative抽检全部通过，但不意味着6720项原负例均逐对人工审核；剔除4query后，6160个N中23对是直接人工复核，6137对仍以几何规则为标签来源。没有发现要求重建整套负例规则的反馈。基线应返回每query最高相似的若干N供下一轮针对性检查。

六街段属于三个相邻道路片区；44view来自12query pano，不能当成44个相互独立空间样本。保留的2430潜在Paris留出仍未冻结。本轮结果只能回答：当前表示能否在这批已审核题目中建立可用的地点检索测量基线。

## 后续动作

服务器执行SERVER_BASELINE_TASK.md与configs/baseline_request.json。先验证版本/图像哈希和小样本提取，再完成212图的full-image baseline，返回逐query成绩、完整分数、排名和错误案例。当前不进行Qwen候选、区域删除、训练或模型排行榜。

源导出SHA-256、原始答案、审核校验和边界处理均在review_inputs/、validation/、review/。task_manifest.json只声明这一开发任务可开始基线，不声称已完成模型环境检查或获得科学实验结论。

validation/review_return_gate.json保留边界裁决前的原始报告，baseline_ready=false表示当时需要处理R123/R125；当前状态以新task_manifest.json和17项通过的validation/frozen_task_validation.json为准，边界裁决见review/boundary_adjudication.json。
