# Paris Pilot 0：已人工复核的完整图基线任务

任务版本：paris_local_v1_20260923。44 query / 168 reference；82 P / 6160 N / 1150 I。当前交接包为v2.2-final（`server_baseline_package_v2_2_final_20260924.zip`）；包含NAS路径、真实文件名/ID映射、绝对朝向、G/14权重、从固定AnyLoc GitHub Release自动获取VLAD词典的脚本，以及全量448 PNG预处理。尚无模型运行结果。执行入口为SERVER_PREPARATION_V2.md。

解压后在该目录运行（仅Python标准库，不需GPU）：

```bash
python scripts/pilot0_delivery.py verify --task-dir .
python scripts/pilot0_verify_frozen_task.py --task-dir .
```

先验证交付字节，再验证题库。第一条须在修改任何包内文件之前运行；本地服务器路径配置另存为paths.server.json，运行输出另建目录。第二条会写回validation/frozen_task_validation.json。

然后阅读REVIEW_ACCEPTANCE.md与SERVER_PREPARATION_V2.md，按configs/baseline_request_v2.json执行路径/权重/词典/全量resize检查、单图smoke、212图提取及完整评分。v2包已提供预处理、G/14提取、VLAD与baseline评分代码；大图、weights、词典和特征仍放服务器/NAS，不在ZIP中。

本包不含图像、权重或大特征。按image_relative_path映射服务器图像目录，并核对image_sha256；review_image是历史本机缓存位置，不能用作服务器输入。完整全量索引保留用于数据溯源，此次仅提取queries.csv和references.csv的212张图。

validation/review_return_gate.json是应用边界裁决前的原始审核报告，其中baseline_ready=false已由review/boundary_adjudication.json和新task_manifest.json处理。以v1 task_manifest.json的FROZEN_DEV_READY_FOR_BASELINE及最终17项检查通过为当前状态。baseline_request.json保留原v1 tensor-resize配置；本轮指定的离线PNG执行使用baseline_request_v2.json，不能混用特征缓存。

大型特征留服务器，返回逐题结果、全分数、困难负例/失败图卡及运行环境记录。本地复算后再进入候选区域与干预阶段。
