# 2026-09-23 人审回收与服务器准备记录

工作目录：F:/Codex_local/Nav_Lmk。项目：01_Navigational_Landmarkness_Cognitive_Map。
本机Python：C:/Users/Admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe。

源人审文件在D:/EgeDownload，原字节副本与SHA-256保存在review_inputs/；旧草案local_v0_20260922保留。以下为本轮成功执行命令，均从项目目录解释相对路径（将python替换为上述本机解释器）。

```text
python scripts/pilot0_validate.py --output-dir outputs/pilot0/local_v0_20260922 --review-return D:/EgeDownload/HUMAN_REVIEW_paris_local_v0_20260922.json
python scripts/pilot0_accept_review.py --draft outputs/pilot0/local_v0_20260922 --review-json D:/EgeDownload/HUMAN_REVIEW_paris_local_v0_20260922.json --review-csv D:/EgeDownload/HUMAN_REVIEW_paris_local_v0_20260922.csv --output-dir outputs/pilot0/reviewed_v1_20260923
python scripts/pilot0_verify_frozen_task.py --task-dir outputs/pilot0/reviewed_v1_20260923
python scripts/pilot0_verify_public_sources.py --output-dir outputs/pilot0/reviewed_v1_20260923/official_source_check
```

accept_review拒绝覆盖已有任务；要复现生成，请换新的输出目录，不能覆盖当前冻结输入。该生成器针对本次R123/R125人工边界裁决，不能在未复查情况下用于其他审核批次。原通用审核报告要求边界处理，最终版本已显式处理并开启开发基线。

本轮检查了两份答案逐字段一致、132项完整、82项P均合格，并以只读图像方式复查R123/R125完整图卡。生成44query/168reference/7392关系；数据验证17项通过，详见validation/frozen_task_validation.json。未再次扫描Z盘，未读取ERP，未加载GPU模型或词典，未获得DINOv2指标。

公开源码核验仅获取官方小型文本。精确URL、commit、字节数和hash在official_source_check/source_manifest.json；本地还保留下载文本。AnyLoc commit a9fda68c55083f765b019df148a1b67614f90ee2，DINOv2 commit 7764ea0f912e53c92e82eb78a2a1631e92725fc8。获取脚本查询运行时main，未来再运行不保证取得同一commit；重核本次证据应使用manifest中的固定URL和hash。服务器要独立验证实际安装源码与权重。

交付命令（只白名单小文件，自动回读ZIP并逐项检查SHA-256/大小/CRC；成功报告delivery_validation.json）：

```text
python scripts/pilot0_delivery.py package --task-dir outputs/pilot0/reviewed_v1_20260923 --scripts-dir scripts --output-zip outputs/pilot0/reviewed_v1_20260923/server_baseline_package.zip
```

完整数据hash由task_manifest.json维护，交付包新增说明、baseline_request和验证器由包内package_manifest.json维护。未建立Git仓库、上传GitHub或联系服务器。

已解决的工具错误：首次工具JS数组语法；控制台中文编码；普通受限网络Win10013后使用限定官方URL只读访问成功；DINOv2源路径最初漏dinov2/前缀导致404，修正后5文件全部成功。Git返回not a git repository为现状，无未解决数据结构错误。完整会话记录见项目WORKLOG.md和ERROR_LOG.md。
