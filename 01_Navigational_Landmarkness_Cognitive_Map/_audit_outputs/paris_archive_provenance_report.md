# Paris Archive Provenance Report

## Scope

本报告审查 `D:\BaidudiskDownload\Paris_check_for_Codex.zip`，目标是确定哪些巴黎资产可以进入当前的 **Paris Data and Task Feasibility Audit**，以及哪些处理步骤仍缺少原始执行记录。审查为只读；未运行历史下载、图构建或含凭据的入口。

## 选择性资产清单

| 类别 | 数量 | 当前处理 |
|---|---:|---|
| 巴黎迭代/最终资产 | 128 | 深入：图、点位、元数据、候选输出 |
| 巴黎源数据/元数据 | 55 | 深入：坐标、道路、heading、pano 连接 |
| GSV/投影共享代码 | 33 | 深入：下载接口、tile 拼接、ERP 投影 |
| 图/道路代码候选 | 28 | 深入：`GSV_tiles_download_graph.ipynb` 及替代 notebook |
| Manhattan 历史资产 | 105 | 跳过：只作为历史代码背景 |
| 缓存、IDE、`__MACOSX` | 108 | 跳过：不属于研究数据 |
| 图像/二进制测试资产 | 679 | 按需：不用于证明处理顺序 |

ZIP 共 1,193 个条目。上述分类用于控制审计范围，不表示被跳过资产已被证明无用。

## 最终图的直接 provenance

ZIP 中的

```text
Paris_check_for_Codex/Line_After_heading_clear_Paris_center_street_from0309_4_v1/kl.Line_Points_3.json
```

与工作区保存的图文件 SHA-256 完全一致：

```text
fd11bdf76268a672a2cbf93c5de2216241fc3eca09a6609c0ef23415178b5edf
```

版本链为：

| 版本 | 节点 | 边 | 说明 |
|---|---:|---:|---|
| `_1` | 3,090 | 3,324 | 早期图 |
| `_2` | 3,063 | 3,297 | 删除/清理后 |
| `_3` | 3,059 | 3,293 | 与 `_4` 同哈希 |
| `Line_Points_2` | 3,059 | 3,283 | 带 pano 属性的中间图 |
| `Line_Points_3` | 3,058 | 3,310 | 当前附件图 |

`Line_Points_2 -> Line_Points_3` 删除 1 个节点、删除 1 条边并新增 28 条边；577 条权重变化的最大绝对差约 `2.12e-12`，属于浮点重写，不是点位移动。

## 点位坐标 lineage

数据级复现显示：最终点位与“原始 GSV 坐标在 EPSG:4326 经纬度平面中投影到最近道路折线”的结果逐点吻合，最大残差 `1.44e-9 m`。这证明了当前结果的几何规则，但没有找到生成 `Line_Points_1.shp` 或 `Line_Points_2.shp` 的原始命令。

最终点相对原始 GSV 点的位移为：median `1.189 m`、P95 `5.064 m`、max `19.512 m`。若用本地米制 CRS 或 Web Mercator 重新投影，和当前结果的差异为 median `0.291 m`、P95 `1.498 m`、max `15.226 m`。15 条候选路线的 120 个 pano 差异 median `0.330 m`；15 个 decision pano median `0.280 m`，其中两个超过 1 m：

```text
s-tWQI70JSimlQwafuJYTw  1.570 m
v7BqGg7PqPES1XY99pxMLw  1.010 m
```

因此当前图可继续用于路线候选挖掘和人眼审查；正式实验前应在米制 CRS 中重算贴路，并重点复核上述两个 decision zone。

## 当前 notebook 实际能证明什么

`GSV_tiles_download_graph.ipynb` 是混合历史 notebook。巴黎相关链条从读取 `Line_Points_3.shp` 的 cell 37（execution count 33）开始，随后：

1. 在 cell 51（execution count 40）把点和道路转到 EPSG:3857，用最近道路索引写入 `nearest_street_osmid`；这一步是道路归属，不是重新移动点位。
2. 将每个 pano 作为 `nx.Graph` 节点，保存 `pos=(lon,lat)` 和道路 `osmid`。
3. 同道路内按 Haversine 距离连接邻近点，并用端点条件和锐角条件决定第二条连接。
4. 通过 OSM 端点附近的 pano 连接相邻道路段。
5. 在 cell 88（execution count 53）加入 34 组 `manual_connections`，只修改图，不修改 `end_points`。
6. 在 cell 91（execution count 55）输出 `Line_Points_3_street_view.json`，后续 cell 93 输出 CSV/flow 文件。

这些 cell 的路径和执行计数是 notebook 内部记录，不能证明它们就是最终 `kl.Line_Points_3.json` 的完整执行历史；最终 JSON 的哈希匹配和数据级复现才是当前最强证据。

## 使用分级

- **直接使用**：`kl.Line_Points_3.json`、3,059 个 pano 的 ERP、四视角、heading 和 DINOv2 连接；15 条候选路线及其 review boards。
- **浅层使用**：替代 graph notebook、旧 `street_view_graph_*.json`、旧 `trajectory_0..9`；用于历史对照和格式追踪，不作为当前 gold。
- **跳过**：Manhattan 图和测试资产、缓存/IDE、旧下载入口；不在本阶段运行。
- **安全隔离**：含硬编码服务凭据的历史代码不运行，凭据应先撤销/轮换。

## 结论

巴黎资产已经通过“文件与数据连接”审查，但尚未通过“道路语义与实验任务”审查。当前结论保持 **Provisional ADAPT**：保留巴黎，先进行路线/任务的人眼确认；不要把原始无向图直接当作真实行动图，也不要在缺少 route-memory 任务定义前宣称某个 `provisional_maneuver` 是正确动作。

