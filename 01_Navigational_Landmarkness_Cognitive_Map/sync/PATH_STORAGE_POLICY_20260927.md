# 服务器与 NAS 路径协议

这条协议适用于本项目后续所有本地 Codex 与服务器 Codex 交接。

| 内容 | 固定位置 | 说明 |
|---|---|---|
| 项目代码、脚本、schema、manifest、轻量日志和研究文档 | `/home/wangyq/Nav_Lmk/` | Git 工作树；可提交 GitHub |
| 第三方源码仓库（例如 `third_party/dinov2`） | `/home/wangyq/Nav_Lmk/third_party/` | 只放源码，不放模型权重；已有目录保留，不随意删除 |
| Python 环境及依赖元数据 | `/home/wangyq/Nav_Lmk/.venv_*`、`server_tasks/` | 环境可复用，不能替代权重或数据归档 |
| 模型权重和词典 | `/home/nas/wangyq/model_weights/` | Qwen、DINOv2、VLAD 均放这里 |
| 原始/派生图像、ERP、448 缓存、patch cache | `/home/nas/wangyq/GSV_Paris/` 及相关 NAS 目录 | 不进入 GitHub |
| 大型特征、overlay、完整推理转储和实验结果 | `/home/nas/wangyq/outputs/` | 只在项目目录留下路径、摘要和 SHA-256 |

路径映射只适用于 NAS：`/home/nas/wangyq` 对应本地 `Z:\wangyq`。项目代码 `/home/wangyq/Nav_Lmk` 不等同于 `Z:\wangyq`。

GitHub 只同步轻量文本、代码、schema、manifest、摘要和错误报告；不上传图像、权重、patch cache、ZIP 或大型 raw dump。

每个新任务开始时服务器拉取一次 `origin/main`。运行期间不轮询 GitHub、不推送中间进度。完成或阻塞时写入服务器日志并在对话中一次性回报；只有需要本地读取的轻量摘要，才在明确要求后提交并推送。
