# Paris Data and Task Feasibility Audit: 资产清单

审计日期：2026-07-30（Asia/Shanghai）

## 状态

核心机器扫描已完成，候选路线的 Codex 接触表预审已完成；用户/老师的六维人眼评分尚未完成。`Z:` 映射盘在普通沙箱中不可见，但经用户批准的路径限定只读访问可正常读取。

## 选择性扫描边界

### 深入扫描

- `Z:\wangyq\GSV_Paris`：四视角、ERP、旧 16 视角、DINOv2。
- `Z:\wangyq\Street_view_and_points_Paris`：图、heading、点到道路映射、OSM edges、POI seed。
- `Z:\wangyq\CityBench\CityBench-main\citybench\outdoor_navigation`：十条轨迹、route-facing 图像、VLM 描述脚本和已有输出。
- `Z:\wangyq\CityBench\CityBench-main\citydata\outdoor_navigation_tasks`：Paris task/instruction/matched-image 文件。
- `C:\Users\Admin\Desktop\UrbanNav_neo_fromPC.zip`：RL 源码、配置、日志和 checkpoint 清单；未整体解压 checkpoint。
- `D:\BaidudiskDownload\GSV_tiles_download_graph.ipynb`：图生成算法与执行状态。

### 仅看一层、未深入

- `BSV`：另一街景源，只有 `image_4per_latest` 和 `metadata` 被确认存在。
- `CityLandmarks`：含 CIELAB 图件和既有城市视觉实验，判定为 UrbanHue/旧方法旁支。
- `GSV_landmarks`：当前只有 UK 子目录，不是巴黎核心数据。
- `Landmarks_exp`：旧 landmark/POI/census 实验，不进入本轮 canonical chain。
- `building_data`、`model_weights`：只确认存在；当前审计不需要读取权重或全球建筑数据。

### 明确跳过

- `docker_images_tar`、`extensions`、`wyq_envs`。
- CityBench 的 mobility、remote sensing、GeoQA 等非 outdoor-navigation 模块。
- segmentation masks、cache、虚拟环境、`.pyc`、UrbanHue 历史图件。

## 核心资产

| 资产 | 实际状态 | 关键结论 |
|---|---:|---|
| Kepler/NetworkX 无向图 | 3,058 节点，3,310 边 | 本地附件与 Z 盘文件 SHA-256 完全一致 |
| 四视角 | 3,059 pano，12,236 JPG | 每个 pano 4 张，图中 3,058 节点覆盖 100%；抽样尺寸 640x640 |
| ERP | 3,059 JPG | 图中节点覆盖 100%；抽样尺寸 13,312x6,656 |
| 旧 RL 视角 | 3,100 pano x 16 | 84x84，供旧 agent 使用，不作为新研究默认输入 |
| heading | 3,059 行 | 图中节点覆盖 100%，无空值；像素审计验证 `center(view_i)=heading_from_api+90*i` |
| DINOv2 | 3,059 x 384 float32 | `exp0_arc/dino_k200` 为全量；`dino` 仅是 200 个代表样本 |
| 十条路线 | 77 step records | 67 个唯一 pano、57 个物理跳转；位于 `trajectory.csv` |
| route-facing 图像 | 335 JPG | 67 个路线 pano x 5（四视角 + ERP），按 `trajectory_0..9` 分目录 |
| 已有 landmark descriptions | 最新一次 77/77 | Qwen2.5-VL 在 prompt 中直接获得 gold action，只可作候选/历史输出，不能作独立验证 |
| POI seed | 32 行 | `landmarks_paris.csv`，是地理 POI 种子，不是 verified landmark |
| UrbanNav ZIP | 247 entries | 57 `.py`、8 notebook、15 `.pt`；约 16.2 GB 压缩、26.8 GB 解压后 |

多出的完整 pano 为 `hPkSPYp9nAAQFuAi-1UKfA`，它具备四视角、ERP、heading 和 embedding，但未进入 3,058 节点图。

## CityBench 资产分裂

`citydata/outdoor_navigation_tasks` 中的 Paris 正式任务只有 1 条 road-ID route，matched image 只有 5 行，且对应 JPG 不存在；6,731 行 instructions 与这 1 条 task 不是同一完整运行状态。

用户所说的十条人工路线实际位于：

`Z:\wangyq\CityBench\CityBench-main\citybench\outdoor_navigation\trajectory.csv`

它们由 `toyscript_from_csv.py` 消费，与 `citydata` 下的 1 条 Paris task 是两套不同的数据组织。

## 当前资产结论

巴黎核心数据不是“空中楼阁”：node、四视角、ERP、heading、embedding 已完整连接，且已从全图挖掘 12 条主候选和 3 条凯旋门对照路线。旧十条短路线仅作为历史样例保留。真正尚未完成的是：

1. 用户/老师对候选路线的六维评分与去留确认；
2. 将 provisional maneuver 确认为 human-verified action；
3. 从 ERP 生成正式 route-aligned 四视角；
4. 冻结第一项实验与样本分层。
