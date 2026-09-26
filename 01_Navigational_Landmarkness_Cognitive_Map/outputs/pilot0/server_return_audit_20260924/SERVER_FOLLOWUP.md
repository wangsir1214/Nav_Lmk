# 服务器补充交接指令

本地已从NAS的212个VLAD向量独立复算全部7392个相似度及44题指标，与服务器结果一致。主基线和80P敏感性均通过，不需要重跑模型或修改题库。

请在现有任务上完成以下轻量交接工作，不启动新模型实验：

1. 读取 /home/wangyq/Nav_Lmk/server_tasks/paris_local_v1_20260923_v2_2_final_20260924/SERVER_TO_LOCAL.md 与实际日志，核对文件存在；将以下资料复制到一个新建的NAS目录 /home/nas/wangyq/outputs/Paris_local_v1_20260923/server_return_evidence_20260924/。若已存在，先核对内容，不覆盖不同版本文件。
2. 返回SERVER_TO_LOCAL.md，以及server_run下的pipeline_status.json、commands.jsonl、command_results.jsonl、environment_runtime.json、archive_verification.json、return_artifacts.json、return_artifacts.sha256、g14.provenance.json、vlad.provenance.json与pip_freeze/nvidia日志。返回validation下的server_frozen_task_validation.json、全部本次preflight报告、g14_vlad_smoke.json、final_result_audit.json，以及执行脚本本身。保留原相对目录和来源绝对路径。无法找到的文件明确记录missing，不重新制造过去的报告。
3. 保留原base结果及清单不变；在这个新的补充目录输出带源hash的subarea_summary.json。已有area_id=paris_arc是整个数据覆盖区，不能据此声称原baseline_summary.json已经给出三个子片区。根据冻结development_groups.csv及原pilot0_tasks.py选路顺序，用D01+D02、D03+D04、D05+D06作为三个子片区的报告层映射。输出每组query数、成功数、Recall和margin摘要；预期R@1分别15/16、16/16、11/12。不得修改冻结area_id、P/N/I、图库或输入hash。
4. 对新增补充交接目录的每个文件记录SHA-256、字节数及原始路径，写清复制时间和该次运行的代码版本。模型权重、图像和大型特征保持原位置，无需上传GitHub。
5. 回报补充目录和清单路径。本步骤只补齐可追溯资料与分层报告，不要求用户再上传旧ZIP，不重下词典、不重训、不删改两个失败query。
