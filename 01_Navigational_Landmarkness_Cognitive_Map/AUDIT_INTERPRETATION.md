# Paris 数据审计：中间结果解释

## 这一步在整个研究中处于什么位置

当前项目的科学问题是：哪些城市视觉线索会在特定任务中成为具有导航和认知功能的地标，并如何连接地点、方向、道路和路线记忆，形成可检验的地标锚定认知地图。

数据审计不是地标实验本身，而是实验入口的可行性判断。它回答的是：巴黎现有数据是否有足够可靠的节点、图、图像、方位和路线条件，让后续任务有机会产生可信解释。

当前阶段结论是：

> 巴黎在技术资产层面可以继续使用，但还没有通过功能性地标和行为任务的人工可行性审查。因此状态是 `Provisional ADAPT`，不是 `GO`，也不是 `REPLACE`。

## 审计已经证明了什么

### 1. 数据资产能够连接起来

当前可以形成以下链条：

```text
graph node
-> coordinates
-> ERP panorama
-> fixed four views
-> heading metadata
-> DINO feature
-> candidate route
-> decision zone
-> provisional maneuver
```

图有 3,058 个节点和 3,310 条无向边，所有节点都能连接到 ERP、四视角、heading 和 DINO ID。15 条候选路线共覆盖 120 个 pano，并且对应的 480 张固定视图、120 条 heading 和 30 张 review boards 都已通过连接验证。

这说明“文件存在但彼此无法组成 case”的风险已经基本排除。

### 2. 巴黎图具有空间结构，但不是现成的导航行动图

图是单一连通分量，并有回环和大量 connector edge，因此巴黎不只是连续直线，具备开展局部路线记忆或地点辨识原型的结构潜力。

但是，原图是无向 pano 图。路口附近的多个 pano 可能因为同一 OSM 端点被连接成局部 clique，单个 pano 的 degree 也不等于真实道路出口数量。单行道方向在无向化过程中被抹去。

因此当前图适合作为：

- 空间索引；
- 路线候选挖掘工具；
- 人工审查的后台拓扑；

暂时不适合作为未经人工确认的 agent action graph。

### 3. 四视角的方向关系已经确认，但历史处理 provenance 不完整

Google Tile API 的 `heading` 是从正北顺时针测量的罗盘方位，JavaScript Street View API 的 `centerHeading` 是全景瓦片中心的 heading。结合本地 tile 拼接和像素审计，当前四视角满足：

```text
geographic_center(view_i) = (heading_from_api + 90*i) mod 360
```

所以 `view_0..view_3` 不是固定的北、东、南、西，也不能永久叫 front、right、back、left。

历史 UrbanNav 的 16 视图是中心间隔 22.5°、每张 FOV=60°；中心间隔不等于 FOV。当前巴黎四视角的方向和 FOV=90°产物已由输出审计确认，但批量生成脚本、插值和 JPEG 参数仍没有找到。

### 4. 旧路线和旧 RL 都不能直接承担当前结论

旧 `trajectory_0..9` 只保留为历史描述生成样例，不能作为当前 gold route。

UrbanNav 可以作为未来的历史 baseline candidate，但目前存在目标坐标 shortcut、旧图处理、方向分支不一致、checkpoint/config provenance 不完整等问题。因此不能用它证明 agent 已经使用了视觉地标，更不能用它直接证明认知地图形成。

## 审计没有证明什么

以下结论目前都不能声称：

- 某个建筑、招牌或结构已经是 verified landmark；
- 某个 `left/right/forward` 是行为学上的正确动作；
- 参与者在没有目标或已学习路线的情况下应该选择哪条道路；
- 四视角足以支持正式的路线方向实验；
- 巴黎一定适合身份替换、位置替换或地标移除；
- 旧 RL agent 已经构建了 loop-aware cognitive map；
- 巴黎数据已经通过最终 Go Gate。

特别需要区分：候选路线的 `provisional_maneuver` 只是根据入口和出口 bearing 推导出的几何标签。一个陌生路口通常有多个合法方向，除非任务提供目标、地图、指令、预探索或学习路线，否则不存在唯一的“正确道路”。

## 为什么下一步先做人眼审查

机器可以验证文件、坐标、边、朝向和图像是否存在，但不能可靠判断：

- 视觉元素是否自然、稳定、可辨认；
- 线索是否与某个出口或路线方向有空间关系；
- 施工、眩光、远距离凯旋门或店铺变化是否造成混淆；
- 某条路线是否真的适合路线记忆，而不是仅仅“画面好看”；
- 某个候选能否自然地做 removal、identity replacement 或 location replacement。

这些判断正是功能性地标定义的一部分，必须由人完成并记录理由。

## 人工审查要做什么

### 第一轮：逐路线审查

使用 `HUMAN_ROUTE_REVIEW_GUIDE.md` 中的 15 条路线板。每条路线先看：

1. 8 步 sequence board：路线是否连续、可理解、具有记忆价值；
2. decision four-view board：当前点、道路出口和视觉线索是否清楚；
3. 路线地图：provisional maneuver 是否与真实决策区一致。

然后在 `candidate_route_review.csv` 填写：

- visual diversity；
- landmark availability；
- spatial relevance；
- task ambiguity；
- intervention feasibility；
- graph/task support；
- task-definition fit；
- action confidence；
- candidate type；
- temporal stability；
- super-landmark presence；
- exclude reason。

Arc de Triomphe 路线要单列为 super-landmark stratum，不要把它们当成后续图像干预中的 matched control。

### 第二轮：只处理保留路线

对 `KEEP` 或可修正的 `ADAPT` 路线：

1. 复核道路出口、单行道和 decision zone；
2. 在 ERP 上按路线 bearing 生成 route-aligned front/right/back/left views；
3. 确认 action confidence 和 route-aligned view quality；
4. 冻结普通路线、低地标对照、结构/身份/场景 strata 和排除理由。

Go Gate 的当前草案是：至少 8 条普通路线通过，左/右/直行均有代表，每类有任务有效性，并至少保留低显著度对照及可解释的结构或身份线索案例。

## 第一项行为任务应该是什么

当前最稳妥的入口是：

```text
P1A 候选地标诱发
-> 学习一条短路线
-> P1B route continuation / route-memory choice
```

学习阶段让被试看完整的 8 pano 路线，测试阶段重新呈现 decision zone，让被试选择“刚才学习的路线从这里继续走向哪条道路”。这样正确答案由学习路线定义，而不是由路线挖掘程序任意指定。

P1A 产生的是 `human-elicited candidate landmark`，还不是 verified landmark。只有当原图任务基线成立后，才有理由进入 removal、identity replacement、location replacement 和 matched-control 干预。

## Codex 能够继续帮助什么

### 现在可以做

- 根据人工评分汇总 KEEP/ADAPT/REJECT，并检查 Go Gate 是否满足；
- 对保留路线生成 route-aligned FOV=90° views，并记录 ERP hash、heading、route bearing、pitch、FOV、输出尺寸和插值参数；
- 在米制 CRS 中重算贴路位置，重点复核两个差异超过 1 m 的 decision pano；
- 建立 `streetview_nodes.csv`、`road_edges.csv` 和 decision-zone manifest；
- 根据人工标注整理 object / structural / scene-level / mixed 候选地标表；
- 生成地标与出口 edge 的 azimuth/alignment 检查；
- 设计简单的人类、检索或分类 baseline，先验证路线记忆任务是否有信号。

### 现在不应该做

- 立即调用 VLM 批量生成地标；
- 立即制作完整 identity/location 消融；
- 立即修复或重训 UrbanNav；
- 把 Arc 路线混入普通路线平均准确率；
- 把结构合格路线称为 gold route 或 verified landmark case。

## 一句话给老师或合作者

> 这次审计没有证明巴黎已经有可直接用于实验的地标；它证明了巴黎数据在资产连接、全景方向和局部图结构上足以进入人工任务审查。下一步不是继续加模型，而是由人确认哪些路线具有明确的任务目标、空间歧义和稳定候选线索，再由 Codex 只对通过审查的路线生成正式方向输入和可复现实验材料。

