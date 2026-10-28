# P0预检器修复审查

三次失败均为新增验证器问题；原始历史源码、数据、mapping生成算法及visual adapter未改。下表由原始修复JSON、BLOCKED诊断、源码逐版差异和最终机器记录交叉核对。

|修复|修改文件与前后行为|映射算法|heading/view选择|adapter输入|实际后续验证|
|---|---|---|---|---|---|
|1|run_s1b_p0.py：路径子串把Pandas RangeIndex.step属性误判为环境动作；改为三份环境源码精确路径匹配|不变；尚未生成映射|不变|不变|第二次进入原生建图，随后因第2项检查器断言退出|
|2|run_s1b_p0.py：raw API heading误与已归一化internal heading直接比较；改为验证原ConstrainAngle(180,raw)，分别存两种值；把profiler路径常量移出热循环|不变；修复后首次生成映射|测试预期改正，生产get_heading/选图公式未改|不变|第三次通过550节点、确定性映射、8800图像及35216朝向检查，随后因第3项退出|
|3|run_s1b_p0.py：误认为观察仅view_image/goal；改为原实际四字段，并检查goal/yaw/yaw_label均不变。新增resume_s1b_p0_observations.py只续做剩余检查|未重生成；续做前后hash一致|不变|adapter此前已保留所有字段，没有改写输入|续做12静态fixture×3条件=36项；原生图重建hash一致，未重扫8800图片|

第一、二次在映射生成前退出；第三次执行过一次reset后在观察键断言处退出。成功续做另有两次reset，所有尝试均无环境step、策略forward或导航。第二次尝试的停止请求发出时进程已因断言退出，实际没有发送信号。

修复涉及检查器控制流与验证假设，不改变已批准映射、最近视角选择或图像替换语义。特别是第2项确实改变了“验证什么”的表达，不能略称完全没有差异：它纠正为原运行时的[-180,180] heading，而非改变运行时heading。第3项扩大了非视觉字段断言，避免遗漏yaw/yaw_label。

AST比较确认全部版本中的donor_mapping、heading_tests、inventory函数完全相同；实际adapter/生成器文件sha与mapping audit记录相同。公开code目录含实际版本的仅路径脱敏副本、逐版diff与原始/公开hash，不是重新写的示例代码。系统sandbox的namespace调用在任何Python预检前失败，使用获准工具执行解决，未更改系统配置。
