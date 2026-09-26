# 本地复现与文件说明

所有原始来源只读。全量索引只列出两个明确图像目录的文件名一次，不读取全量像素；复核阶段只缓存216张选定固定视图。不读取ERP像素。

在 `F:/Codex_local/Nav_Lmk` 执行，使用现有 Python（需 Pillow、pyproj）。本次运行时：

```powershell
$pilotPython = 'C:/Users/Admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$pilotProject = '01_Navigational_Landmarkness_Cognitive_Map'
$pilotOutput = "$pilotProject/outputs/pilot0/local_v0_20260922"

& $pilotPython "$pilotProject/scripts/pilot0_local.py" --phase index --metadata 'Z:/wangyq/Street_view_and_points_Paris/GoogleAPIMETADAT/Paris_Points_heading_3059/Paris_Points_heading_3059.csv' --image-dir 'Z:/wangyq/GSV_Paris/0-All_GSV_3059_4per' --erp-dir 'Z:/wangyq/GSV_Paris/0-All_GSV_3059_panorama' --point-road-dbf 'Z:/wangyq/Street_view_and_points_Paris/Line_After_heading_clear_Paris_center_street_from0309_4_v1/Line_Points_3_to_road.dbf' --road-dbf 'Z:/wangyq/Street_view_and_points_Paris/road/edges.dbf' --road-shp 'Z:/wangyq/Street_view_and_points_Paris/road/edges.shp' --graph '98_Others/kl.Line_Points_3.json' --output-dir $pilotOutput --extra-deps "$pilotProject/_audit_work/feasibility_deps" --seed 42 --num-samples 54
& $pilotPython "$pilotProject/scripts/pilot0_tasks.py" --output-dir $pilotOutput --seed 42 --groups 6
& $pilotPython "$pilotProject/scripts/pilot0_review.py" --output-dir $pilotOutput
& $pilotPython "$pilotProject/scripts/pilot0_validate.py" --output-dir $pilotOutput --extra-deps "$pilotProject/_audit_work/feasibility_deps"
& $pilotPython "$pilotProject/scripts/test_pilot0_review_gate.py"
```

上面是复现记录，不建议在人审进行中覆盖当前输出；从头复现请选择新 output-dir。任务脚本检测 HUMAN_REVIEW.csv 中已有 human_relation 时拒绝覆盖，浏览器导出的答案仍应单独备份。

收到答案后只读检查（把最后路径换成实际导出文件）：

```powershell
& $pilotPython "$pilotProject/scripts/pilot0_validate.py" --output-dir $pilotOutput --review-return "$pilotOutput/review/returns/HUMAN_REVIEW_paris_local_v0_20260922.json"
```

该命令只报告，不应用标签或开启正式基线。完整填写不等于分歧已经解决。

## 文件关系

- `data/view_manifest.csv`：全量逐视图索引；`pano_id`连接元数据/图/道路，`view_id`连接图像、query/reference和配对。
- `data/pano_manifest.csv`：空间属性主表；实验划分以`spatial_splits.csv`和view_manifest为准。
- `data/road_inventory.csv`：street_segment_id为原 roads DBF 的零起始行号；OSM ID 已交叉验证。道路名称为UTF-8。
- `data/queries.csv`、`references.csv`：当前草案活动视图；fixed_root_key + image_relative_path解析原图；review_image仅供本地复核，不是模型新输入。
- `data/retrieval_pairs.csv`：完整48×168矩阵。relation含义是草案建议，label_source与review_status不得丢弃。未选入的额外近距正例候选也保守ignore。
- `data/spatial_splits.csv`：实验分组与检索角色分开；保留区尚未冻结。100m是拍摄点距离，不保证视觉实体完全不共享。
- `sources/source_manifest.json`：读取时来源哈希；小型源文件缓存用于重查，不重新扫描Z盘。
- `review/image_validation.csv`：选定216张图的实际大小、字节数和SHA-256。
- `review/codex_pair_pre_review.csv`：机器辅助预审；human_verdict始终空白，不代替human表。
- `review/HUMAN_REVIEW.csv`：空白人审表；`review/index.html`离线填写界面。
- `task_manifest.json`与`artifact_hashes.json`：草案ID、图库ID及产物/脚本哈希；`server_draft_package.zip`是白名单轻量副本。

距离采用 API capture 坐标投影至 EPSG:2154。原始采样坐标和吸附坐标另存来源字段；heading为 `(heading_from_api + 90 * view_index) % 360`，不将view0固定解释为前方。

索引阶段与建题阶段的执行日志为UTC时间，目录日期为启动日期；本地交付完成时间为北京时间2026-09-23。环境版本见environment.json。
