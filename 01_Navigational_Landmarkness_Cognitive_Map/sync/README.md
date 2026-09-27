# 2026-09-26 研究同步包

本目录是本地 Codex、服务器 Codex 与网页版 ChatGPT 之间的轻量同步层。

当前研究问题：

> 哪些城市视觉元素在给定空间任务和路线经验时，能够提供地点、方向或通行结构参照，并帮助观察者把当前观察与路线经验联系起来，支持正确的局部行动？

Qwen 是候选区域提议器和行为探针，不是地标真值生成器；DINOv2+VLAD 是地点对应/表征辅助测量，不是导航地标结论本身。正式路线动作必须由路线记录、道路几何和人工核验确定，当前候选路线仍是 provisional。

文件说明：

- `RESEARCH_DESIGN_20260926.md`：最新研究问题、实验顺序、条件和证据边界。
- `ROUTE_SMOKE_MANIFEST_20260926.json`：第一批连续路线 smoke 的轻量清单。
- `QWEN_OUTPUT_SCHEMAS_20260926.json`：候选提议和路线选择的 JSON 结构。
- `SERVER_CODEX_HANDOFF_20260926.md`：可直接交给服务器 Codex 的执行说明。
- `SERVER_SYNC_SETUP_20260927.md`：服务器首次同步及 `third_party` 只读溯源说明。
- `PATH_STORAGE_POLICY_20260927.md`：代码、源码、权重、图像和结果的固定存储路径及低 token 同步规则。

服务器项目即使不是 Git 工作树，也不要在原目录初始化 Git；按 `SERVER_SYNC_SETUP_20260927.md` 使用独立临时 clone 或手动上传 `sync/`。

大文件保留在服务器/NAS，不进入 GitHub：原始图像、ERP、模型权重、patch cache、完整推理转储和大型 overlay 集合。
