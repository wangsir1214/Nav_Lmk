# UR-85 S0-R 本地证据复核

状态：`PASS — WAITING_FOR_HUMAN_S1_REVIEW`。复核对象是公开审核提交 `dafdd21bfdd97c37381344b70add301426341cfa` 的五份轻量文件；模型没有在本地重新加载或运行。

本地复核脚本确认远端跟踪分支 `server-results/urbannav_ur85_s0_20261025T163610Z_a01` 指向报告的完整 commit，批准版 S0 commit `d3ba7f2f6f412bbd3692961301e666c88ecc8899` 是其祖先。提交只增加五份审核文件。JSON 与 CSV 交叉统计一致：48 个唯一 case 全部 PASS，每题两次前向，概率在容差内归一化、argmax 与概率最大项一致、输出 finite、逐题重复最大差为 0。75 行 artifact index 中包含 `ARTIFACT_MANIFEST.json`，其 SHA 与审核 JSON 一致。

公开证据记录：checkpoint SHA 与批准清单一致；当前执行副本和比较副本各有54/54源码匹配；490个模块、629个保存参数/buffer条目严格核验，missing/unexpected/mismatch均为0；限定48张原图的 BGR CHW uint8 0–255 输入与原观察方法逐像素相等；CNN 内唯一一次 `/255`。研究者的服务器端技术审核状态为 PASS。公开CSV的argmax分布为动作0：35题、动作4：13题；这来自固定目标、零GRU初态的单帧 smoke，不能解读为导航策略偏向。

复核边界：公开审核包仅有索引而没有75个原始payload，因此本地验证了75行索引结构及其与公开证据的关系，没有重哈希服务器原始payload。证据也明确不能证明当前代码是2025训练时不可变源码、完整导航环境等价、历史成功率、导航泛化、视觉依赖或地标功能；2D Goal 的100/200m是研究者后期确认，并非完整Run配置。完整机器可读核验见同目录 `S0_LOCAL_REVIEW_EVIDENCE.json`。
