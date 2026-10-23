# UR-85 S0 模型输入输出合同

本文件是 S0 批准版接口说明；原 L0 静态报告 `../MODEL_IO_CONTRACT.md` 保持原样。UR-85 的 100/200 m 半径来自研究者于 2026-10-22 的人工确认，不是归档配置文件。S0 只做结构恢复与独立 Full 前向，不运行环境轨迹。

## 图像：严格保留历史流水线

1. 一个 pano 有 `00` 至 `15` 共16张 84x84 JPEG，中心方向间隔22.5度，投影 FOV=60度。每个环境步根据 `theta=(yaw-heading) mod 360` 选择**一张**，不是16张同时输入。
2. `pano_data.py` 使用 `cv2.imread(path, cv2.IMREAD_COLOR)`，得到 HWC、`uint8`、**BGR**、像素0至255。`observations.ViewImage` 只做 HWC 到 CHW 的转置，仍为原始像素值。
3. adapter 传给 `view_image` 的应是这些**未归一化**的 BGR CHW 像素，优先保持 `uint8`；若模型边界要求 cast，只能进行等值 cast，保存原观察和进入 CNN 前的 dtype/范围/像素等价证据。
4. `new_baseline_ppo/models/simple_cnn.py` 的 `forward` 内执行**唯一一次** `/255.0`。adapter、数据加载器和任何 wrapper 均不得预先 `/255`。不得 BGR 转 RGB、ImageNet normalize、resize、重新 JPEG 编码、重投影或修改原历史模型源码。
5. S0 必须对48个 case 逐个比较原 `ViewImage` 路径产生的观察 tensor 与 adapter 的观察 tensor：shape、通道顺序、dtype、全部像素一致。可用限定于样本的旧函数/对象构造，不得初始化会预载49600张图的原 Dataset。若无法可靠建立等价性，就停止在该闸门，不继续宣称模型输入已复原。

## 非视觉输入与输出

- checkpoint 存储完整 `new_baseline_ppo.policy2.DeepMindPolicyOracle` 对象、update=80000、`obs_rms=None`；静态清单含629个参数/缓冲条目。S0须在隔离可信环境核全键、全形状，禁止部分加载或 `strict=False` 冒充恢复。
- 视觉 CNN 接两套 GRU：Goal GRU 和 Policy GRU，hidden宽度512。每次独立 smoke 使用新的零状态，并固定2D Goal fixture、prev_action=0、prev_reward=0、reset mask=0；不要把48张按顺序形成伪轨迹。
- 2D Goal 是**绝对归一化目标坐标**，非目标相对距离。当前源码中的经纬度边界仅为 smoke fixture 候选，不能称为已核实的 UR-85 原 Run 配置。服务器必须保存目标坐标、归一化公式、tensor数值/dtype与所用源码 hash。
- actor 5类：0前进、1左22.5度、2左67.5度、3右22.5度、4右67.5度。输出 raw actor linear logits、softmax probabilities、critic value、两套更新后的 hidden 和 heading 分支值。Categorical.logits 是归一化 log-prob，不等于 raw actor logits。
- 独立重复同一输入检查数值稳定。零历史单帧结构 smoke 不评价导航成功率、记忆利用或视觉依赖。

源码证据：原始字节 hash 见 `CODE_SOURCE_HASHES.json`；checkpoint 结构见 `checkpoint_structure.json`。批准版合同没有可执行历史源码，服务器必须核对其自己的原始代码与数据，并且不能把脱敏 L0 审计副本当作未经验证的源码。
