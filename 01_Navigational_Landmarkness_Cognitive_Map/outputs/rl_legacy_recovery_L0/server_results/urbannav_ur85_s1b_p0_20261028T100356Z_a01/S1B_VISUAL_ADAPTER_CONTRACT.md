# P0 视觉适配器合同

唯一替换点是原环境 `_get_observation()` 返回的观察字典 `view_image`，在原 `batch_obs` 之前。原链路：`ViewImage.observation → PanoGraph.get_image_view → Dataset.get_pano_perspective → cv2.imread(IMREAD_COLOR)`，HWC转CHW；不初始化 Dataset 的全图库预载入口。

新 `VisualAdapter.replace()` 接受观察、condition、真实 pano/yaw，只返回新的浅拷贝观察字典与日志元数据。原观察实际含view_image、goal、yaw、yaw_label；全部非视觉字段使用原对象且batch后数值一致。previous action/reward、mask 和双GRU并非其参数；adapter 没有环境对象引用，不调用 reset/step、策略、采样或网络。`select()` 只使用固定映射和历史选图函数，不使用 Full 成绩。

- Full-Passthrough：原 `view_image` 同一对象，不拷贝或修改像素。
- NoImage：新建全零 NumPy BGR CHW uint8 `(3,84,84)`。这里的张量是原观察格式；原 batch_obs 随后等值 cast 为 float32 `[1,3,84,84]`。
- ShuffledImage：固定 donor 的原 JPEG，经原 cv2 IMREAD_COLOR BGR 解码和 HWC→CHW，保留0–255；文件哈希必须与本次inventory相同。没有resize、投影、色序转换、JPEG重编码或输入级normalize。

CNN `RGBCNNOracle.forward` 唯一一次 `/255.0` 保留。P0对该点的证明来自未变化的原源码和 S1-A 实际CNN输入/卷积前置断言，本轮没有再调用模型。CPU上执行的 batch_obs 两个函数由原源码AST隔离编译，未导入PPO模块。

对001/024两个起点作12个明确标记的静态 yaw 观察fixture，每个3条件，共36项。成功测试执行2次真实 fixed-goal reset、原 `_get_observation` 和读取原图；之前检查器失败另有1次reset，所有尝试均无环境step。逐像素验证原观察、Full完全相同、NoImage全零、donor与对应JPEG相同；全部非视觉字段同对象且cast相同，状态/reward/终止标志及独立非视觉哨兵、CPU随机源均不变。这是限定样本的接口测试，不是新闭环导航或模型干预结果。

donor按真实internal yaw减donor heading重新选索引，不能复用source view index。16方向间距22.5°、历史FOV60°，是最近可用视图而非任意朝向精确重投影。等距优先原列表较早索引；348.75°选15，而非0。浮点heading加减可能让理想等距点略偏；保留原浮点规则，不加epsilon纠正。

未知pano、非有限yaw、映射hash/算法改变、图像hash不符、shape/dtype错误立即报错；无Full回退或现场重映射。实际映射目前只完成生成及技术校验，仍需研究者审核并冻结hash后另行授权闭环联调。
