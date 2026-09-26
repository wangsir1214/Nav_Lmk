# Paris 图质量与任务能力报告

> 2026-07-30 更新：本报告中的“十条路线”仅指历史 `trajectory_0..9`，不再作为当前 gold。全图挖掘的 12 条主候选、3 条凯旋门对照及 provisional actions 见 `route_task_report.md`。

## 总体结构

| 指标 | 结果 |
|---|---:|
| 节点 / 无向边 | 3,058 / 3,310 |
| 连通分量 / 孤立点 | 1 / 0 |
| cycle rank | 253 |
| bridges / articulation points | 257 / 258 |
| degree >= 3 节点 | 378 |
| degree 分布 | 1:13, 2:2,667, 3:256, 4:106, 5:15, 6:1 |

378 个高 degree 节点只是拓扑候选。按空间阈值合并后，5/10/15/20/25m 分别得到 295/192/128/99/84 个 decision zones，说明不能把 raw degree 直接当实验路口。

## 实际生成逻辑

附件 notebook 中可确认的运行顺序是：

1. Cell 60 创建无向 `street_view_graph`；
2. Cell 68 构造每条 OSM segment 两端最近的 pano；
3. Cell 77 在同一路段内按距离和几何条件连接 pano，写入 weight；
4. Cell 83 枚举共享 OSM 端点的相邻道路，把各自 endpoint-nearest pano 全部互连，不写 weight；
5. Cell 86 序列化 NetworkX 图；Cell 88/95 导出边表与坐标。

Cells 64、66、75 未执行，不是运行时证据。Cell 81 是旧 connector 版本；Cell 83 是其后执行的新版本。

重要限制：该 notebook 内没有任何 `Paris` 路径，保存输出含 Manhattan 坐标和 10,956 节点。因此它证明的是算法模板，不是当前 3,058 节点 Paris JSON 的直接运行 provenance。Paris 图的边结构与该算法高度一致，但仍不能写成“已由 notebook 文件直接复现”。

## Weighted edges

- 2,849 条；长度中位数 6.04m，P95 12.97m，最大 41.43m。
- 2,822 条在同一 segment 内。
- 27 条跨 segment，但 27 条均属于同一 OSM way；其中 26 条共享 OSM 端点，通常可解释为同一路的分段连续。
- 唯一异常加权边：`9cftFQVb5fe2PbUNarhlig -> xsOKmWSC8TUCB-wtrxJw7w`，34.86m，segment 133 -> 137，同 OSM ID 4293992，但不共享 segment 端点，需地图复核。

## 461 条 connector edges

- 457/461 的两侧道路共享 OSM 端点。
- 400/461 至少涉及一条 one-way segment，但最终图被无向化。
- 长度中位数 9.70m，P95 21.56m，最大 37.41m。
- 最大路口出现 5 个 endpoint pano、10 条边的完全图。这会把“可在路口转换”展开为 pano clique，不能直接等同于真实转向动作。
- 四条不共享 OSM 端点的异常 connector：

```text
w0W5CYlvcWFBJZZdhp1Elw -> tgj9jSQuZiVyq7PtZlFKZA
w0W5CYlvcWFBJZZdhp1Elw -> 3S_3crC9xaUYPvpWlNNU1A
hvZAPkSerSrqsETwOA3lyw -> ArVbAVKd93UyGkWY9Fs6BA
xsOKmWSC8TUCB-wtrxJw7w -> gyuLd-J0Zh6M6sjtWGqOEw
```

逐条属性见 `graph_connector_audit.json`。

## 十条路线对图的覆盖

- 10 条路线互不共享 pano 或物理边。
- 77 step records，67 个唯一 pano，仅覆盖全图 2.19%。
- 57 个唯一物理跳转，直接覆盖 47 条图边；10 条缺失 direct edge 的跳转全部为两跳可达。
- 10 个 left/right turn action 分布在 10 个 pano；其中 8 个 degree >= 3，2 个 degree=2。
- 20/67 个路线 pano degree >= 3。
- 只有 `trajectory_0/2/3/4` 的压缩物理路线等于当前图的 hop-shortest path；其余路线含 graph-skip 语义。

## 任务判断

| 任务 | 图/路线侧证据 | 当前判断 |
|---|---|---|
| 路口选路 | 只有 10 个 turn records，8 个在 degree>=3 | 可做小 demo/质检，不足以直接支撑论文级主实验 |
| 路线记忆 | 10 条不重叠短路线，5-9 个物理 pano | 有 pilot 潜力，需路线图册判断视觉序列价值 |
| 地点识别 | 3,058 节点、完整四视角和 embedding | 数据结构支持，视觉多样性需人审 |
| 在线探索 | 单连通、cycle rank 253 | 原始图有潜力；one-way 和 connector clique 未清洗 |
| 旧 RL | 环境把图转成 BFS tree | 不能用旧 agent 证明 loop/alternative-path cognitive map |

结论：图不是单一直线链，但它的无向化、路口 clique、异常边和 legacy depth-3 forward 语义必须显式处理。
