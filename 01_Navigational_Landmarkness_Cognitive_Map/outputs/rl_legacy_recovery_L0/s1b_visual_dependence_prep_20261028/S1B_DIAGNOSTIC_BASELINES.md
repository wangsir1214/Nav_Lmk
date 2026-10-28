# S1-B 辅助诊断设计

本文件是待审方案；两种诊断本轮都未执行，也不替代 NoImage/ShuffledImage 闭环实验。

## 同状态单步视觉干预

选择规则在观察干预输出前固定：对每条 S1-A Full 轨迹取动作前状态的第1步及 `floor((n+1)/2)` 步，去重后按 episode ID 和 step 排序。第006题只有一步，故合计最多47个不同状态。此规则使用已记录轨迹长度定位状态，不能再按显著性挑步。为每个选中状态保持当步真实 Goal、previous action、`model_previous_reward=0`、reset mask、两套 GRU 干预前 hidden 和所有非视觉输入；分别输入 Full、零图、已冻结 donor 图，只比较一次前向，不调用环境 step。

服务器私有 hidden archive 若能按 episode/step 取回，必须对照原轨迹中的张量 hash、形状和当前状态；否则从相同 checkpoint、设备、seed、确定性设置和真实 Full 图像自初态重放到该步，逐步比较动作、概率、位置/yaw、reward 与保存 trace/hash，再取真实干预前 hidden。RNG hash 不能反推出中间 RNG 或 hidden；重放不一致则停止该诊断。不得借用 NoImage 或 ShuffledImage 闭环的中途 hidden。

比较原始 actor logits、五维概率、`p(0)`/`p(4)` 差值、argmax 改变率、entropy 改变量与 JS divergence（稳定化后以 nats 计；KL 可作方向性补充）。对同状态图像替换后分布改变，说明视觉对**即时动作输出**有影响；它不证明完整轨迹的导航效益。若不变，也不能排除视觉在其他未抽样状态或训练中的作用。

## 无 PPO 简单动作先验

探索性先验仅在研究者以后另行批准时运行：每步从 `{0:前进,4:右转67.5度}` 以固定 `0.5/0.5` 抽样，不读取图像、不调用 PPO。相同24题与原生 fixed-goal 环境、100m成功和1000步上限；每题用独立命名的动作先验 RNG 流（种子由冻结 `evaluation_seed` 与固定字符串 `S1B-action-prior-v1` 派生），保存算法、版本和种子。不得用 Full 动作频率或结果拟合 `p(0)`、调整转角、挑选好 seed。先只做每题一次轻量诊断；随机策略方差大，任何后续重复次数须另行预定。

此先验测试环境、宽成功半径与长步数上限是否允许简单搜索成功；其结果不是预注册的视觉主对照，也不能把简单策略偶然失败解释为 PPO 使用视觉。若实现会延误 NoImage/ShuffledImage，推迟该诊断。
