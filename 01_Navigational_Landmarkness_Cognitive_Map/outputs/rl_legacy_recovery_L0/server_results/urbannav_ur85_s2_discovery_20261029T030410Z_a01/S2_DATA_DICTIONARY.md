# 数据口径

- registry/composite 表以历史 file_name + candidate_id 唯一：1413 / 135 行。评分与控制表以 state_id + candidate_id 唯一：各 1458 行。
- candidate ID 不跨视图唯一；sam_index 仅原子区有值，结构/组合由 components 溯源。
- CSV 空单元表示缺失/不适用，绝不表示零。Full_p0..4/Removed_p0..4 为原 float32 模型概率的完整保存值。JS 计算时各分布归一化；TV 保留原概率差定义。
- JS nats、TV、Δp、熵与 critic 均为当前 Full 循环状态的一步响应，不是导航任务收益。控制差为候选效应减控制效应。
- state_summary 的每阈值 fraction 为该状态的候选比例；episode_summary 先等权平均本 episode 的状态；总体对 24 episode 等权。阈值是描述尺度，不是统计显著性或有意义性的证书。
- source IDs 对应公共街景研究样本，无个人身份推断。原始图片仅私有审核。
