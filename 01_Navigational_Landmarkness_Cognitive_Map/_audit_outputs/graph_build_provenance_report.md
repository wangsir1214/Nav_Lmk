# Paris Graph Build Provenance Report

## 结论先行

当前 `kl.Line_Points_3.json` 是一个可连接、可用于局部候选路线挖掘的无向 pano 图；它不是未经处理即可作为导航行动空间的真实道路图。

## 构图链

```text
GSV pano 坐标/属性
  -> Line_Points_1/2/3.shp
  -> 最近道路段归属 nearest_street_osmid
  -> 每 pano 一个无向图节点
  -> 同道路邻近连接
  -> OSM 端点跨道路连接
  -> 34 组人工补边
  -> Line_Points_3_street_view.json
  -> Kepler kl.Line_Points_3.json
```

notebook 中的同道路连接权重来自 Haversine 距离（单位为 km）；节点的 `pos` 仍保存经纬度。图对象是 `nx.Graph()`，因此边方向被丢弃。

## 结构审计

- 3,058 个节点、3,310 条唯一无向边；单一连通分量；无孤立节点；cycle rank 253。
- 461 条 connector edge 对连通性和回环数量影响很大。
- 由于同一 OSM 路口附近多个 pano 被跨道路连接，单个 pano 的 degree 可能只是局部 clique 规模，不等于真实路口出口数量。
- notebook 中 34 组人工补边没有逐条保存理由；`Line_Points_2 -> Line_Points_3` 的 28 条新增边与这些补边相符，但并非所有补边都能据此断言为“新边”。

## 对实验的含义

当前图可支持：

- 在后台索引中查找相邻 pano、路线连续片段和候选 decision zone；
- 生成供人眼审查的 sequence/decision boards；
- 在人工确认道路语义后构造短程 route-memory/continuation 任务。

当前图不能直接支持：

- 将所有相邻节点当作可行动的左右/前后动作；
- 证明单行道可逆；
- 仅凭 degree 定义真实路口；
- 证明 agent 已经形成 loop-aware cognitive map。

## 处理建议

第一阶段不需要立即重建全图。应先冻结 15 条候选路线的人眼结果，并对入选 decision zone 逐个核对 OSM 端点、单行道方向、入口/出口 bearing。正式在线探索或认知图实验前，再生成：

```text
paris_graph_raw.json
paris_graph_cleaned.json
paris_decision_zones.json
graph_build_config.yaml
graph_provenance.md
```

