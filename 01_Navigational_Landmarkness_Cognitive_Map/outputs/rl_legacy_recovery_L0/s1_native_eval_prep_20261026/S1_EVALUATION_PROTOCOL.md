# S1 UR-85 Full 原生导航复现协议草案

状态：`HUMAN APPROVAL RECORDED — ENVIRONMENT-ONLY SMOKE AUTHORIZED`。研究者于2026-10-26批准先做不加载模型的环境 smoke；24个 episode 仍为候选草案，Full rollout 未获授权。本地只审计静态证据并生成元数据候选。尚未验证服务器动态环境或执行导航episode。候选ID、坐标、朝向、图路径统计都不是冻结任务。

## 研究问题与范围

先回答一个窄问题：在固定 Paris 新版图、固定目标和固定 UR-85 权重下，冻结策略能否从已指定初始位置和朝向，通过原生街景观察与动作转移抵达目标区域？S1-A只跑 Full。只有 Full 行为及 evaluator 可解释、并经研究者另行审阅后，才准备相同 episode 的 NoImage 和 ShuffledImage 配对条件。此阶段不定位地标区域、不做SAM、不遮挡、不训练。

S0-R的PASS只证明完整模型对象和限定的单帧输入/前向接口可复核。固定2D Goal 的单帧 smoke、训练日志reward、历史SPL片段均不等于当前导航成功率。

## 必须保留的模型和数据

- UR-85 update 80000；严格模型对象恢复和动作接口按 S0 批准版。
- Paris 新版3058点 `Line_Points_3_street_view.json`，目标BFS depth 30，2D Goal，min/max reward radius 100/200m为研究者确认值。
- S0 checkpoint SHA-256：`fef170f6a01c9c9ba2361b7c7b81a4ddb9f0311a145766ed7d07006f7dc28a6e`。
- 图JSON和heading CSV的批准hash见本目录 `EPISODE_DRAFT_AUDIT.json`；SHP的五件套按 S0 `DATA_SOURCE_HASHES.json`，服务器每次读取均须核hash。
- 图像沿用S0批准的单张84×84 FOV=60°、BGR CHW uint8 0–255、CNN唯一一次`/255`。每步从16方向中按经核验的yaw-heading规则取单图。
- 五动作及编码必须来自已核验的 `streetlearn_fast_rotate` 原始 action set，不能从模型argmax概率的动作频数反推语义。完整forward observation、hidden、prev_action、prev_reward、reset mask遵循S0接口；后续条件各自创建零初态并独立运行。

## 历史代码中的固定任务障碍

历史 `evaluate()` 每次调用随机reset，连续运行10个环境episode，并累计多个goal的reward/SPL；其中源码还留有reset mask历史bug注释。它不是固定起终点评估器。

`CourierGame` 在 `on_reset()` 随机选择goal；`_compute_reward()` 找到目标后立即调用 `_pick_random_goal()` 更换goal。因而仅在reset后写入一个goal ID并直接沿用该game，会在达到100m内时改变后续goal，不构成单目标episode。旧采样另有代码常量 `ALLOWED_GOAL_DISTANCE=500`；配置中的100/200是reward半径，不是固定episode采样半径。

`UrbanNav.step()`使用旧动作推进；move-forward由 `PanoGraph.move_to_neighbor()`在当前图3-hop候选、相对bearing±30°范围内选择最近点，找不到候选则停在原pano。一个forward动作不等于走一条直接图边或一个hop。`set_BFS_graph()`从Arc de Triomphe中心构造depth-limited BFS tree并无向化。静态BFS-tree路径不是旧动作执行路径，也不是曼哈顿/合法步行route。

因此服务器必须先设计一个新的、显式声明为**固定单目标评估shim**的S1 evaluator。shim应复用通过哈希核对的模型forward、原图像选取、yaw更新和3-hop动作转移；固定goal在一个episode中不变；重现原100m成功阈值和每步reward shaping，并在成功时停止episode，不触发goal重采样。它不是历史 `evaluate()` 的原样复跑。任何无法原样保留的transition/reward/reset细节必须写入差异表；在差异会改变动作或观察输入时，先停下交研究者审核。

开发shim期间不得修改历史源码。使用独立adapter文件；禁用自动重置；每episode的终止由固定goal成功或冻结max_steps控制。起始点必须大于100m成功半径。第一次读取的goal必须与manifest固定target一致，所有step都保持一致。

## Episode设计草案

`S1_EPISODES_DRAFT.jsonl`含24条候选：四个初始Haversine距离档各6题（100–200、200–300、300–400、400–550m），start/goal pano共48个且不重复；所有候选初始直线距离>100m。seed按episode唯一固定。草案用json graph `pos=[lon,lat]`作为坐标代理、S0批准heading CSV和中心点BFS tree筛选。Node-link JSON所含3058节点/3310边，当前实现从中心按邻接插入顺序构出depth 30树，得到550节点/549树边。

重要：历史运行时从批准SHP属性取经纬度，JSON proxy坐标不可直接作为真实目标输入。服务器必须按SHP `panoid` join坐标，对start/goal核验heading及图片存在；用批准源码边界归一化SHP goal坐标后重写可执行manifest。若hash、字段、点位或图构造不同，停止并报告，不用近似坐标顶替。

草案hop count、tree path distance、path stretch仅是筛样元数据；不能声称是旧环境实际路程、最短可执行路径或成功的充分条件。旧环境的3-hop bearing transition有可能跳过/停留；服务器需要在不加载PPO的环境smoke中核对转移语义。generator原始图proxy路线字段留作审核，不应传入模型。

24题是探索性pilot规模，按起终点直线距离平衡，不是统计功效保证。S1-A只运行一次预先冻结任务manifest中的24个Full episode，不按早期模型结果换题。若SHP join、route reachability或图像有效性筛掉候选，保留原始排除及原因；是否重新抽题需研究者审核并建立新manifest版本。

## 初始状态和策略采样

episode reset时由清单给出固定start pano和候选 heading；不得直接假设 heading CSV/API heading 等于历史环境内部 yaw。先沿原始 `reset()`、视图索引及旋转实现核验坐标约定，再决定如何把候选 heading 映射到初始 yaw。2D goal是固定goal绝对坐标按批准边界归一化；坐标来源和归一化字段必须从 runtime 证据确认。未来 PPO episode 的 recurrent/previous-action 设置遵循已批准 S0 contract；本轮环境 smoke 不加载 PPO，也不执行该策略输入。

主Full条件使用 `act()` 默认的categorical stochastic sample，保持本轮S0验证过的策略调用；每题固定独立seed，environment/Python/NumPy/Torch随机源都显式设种。记录seed、sampling实现和所有动作。可额外报告greedy deterministic轨迹作为诊断，但不可与stochastic主指标合并。

未来NoImage、ShuffledImage若另行批准：同一start、goal、yaw、seed、max_steps和随机数管理；每条件从环境及两套hidden全新reset，完整独立运行自己的trajectory。不得从Full复制路径或任何中间hidden。ShuffledImage需预先冻结跨episode/pano shuffle映射，保留图像尺寸/heading格式，不能按结果选择置换。

## 最小环境smoke gate

模型推理之前，服务器先只做环境/数据/adapter smoke并停下来报告：

1. 容器、S0 commit、源码hash、checkpoint/data hash符合记录；不重载模型。
2. 建图后确认3058节点版本、中心和depth-30限定范围；固定候选start/goal均能在运行时图中查询；SHP坐标和heading有唯一、有效join。
3. 读取2–3个候选pano的少量方向，检查84×84图像decode、选图索引和BGR CHW像素路径；不预载全图库。
4. 用不触发训练/Neptune/模型的脚本固定起点与goal，确认goal observation确为manifest归一化值，逐个测试rotation动作改变yaw但不变pano，forward动作完全服从3-hop/±30°语义并能报告stay/no-neighbor；复位后重复得到相同状态。
5. 用固定goal测试game adapter：目标不会随机重采样，100m阈值/一步reward/成功后的terminal返回符合S1协议；auto-reset关闭，终止不偷偷读取新goal。
6. 测step计数、done/timeout边界、图像I/O错误、无效动作错误和episode日志字段；每个异常必须标invalid，不得当失败/成功吞掉。

环境smoke未通过前禁止任何policy rollout。通过后提交日志、semantics diff及拟用S1 runner命令，等研究者审阅批准再启动24题Full。

## 停止和解释边界

当前状态为 `READY_FOR_SERVER_S1_ENV_SMOKE`。研究者于2026-10-26仅批准无模型的environment-only smoke。smoke结果须回传并等待人工复核；24条episode仍未冻结。Full rollout仍需研究者另行授权。S1-A如获后续批准，仅回答获批固定任务集上的Full表现；不支持Paris泛化、历史成功率恢复、landmark/cognitive-map能力或因果视觉依赖结论。NoImage/ShuffledImage与区域干预均属后续独立阶段。
