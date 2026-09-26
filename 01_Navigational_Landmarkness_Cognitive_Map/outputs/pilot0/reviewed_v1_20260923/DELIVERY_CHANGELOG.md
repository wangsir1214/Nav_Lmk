# 服务器交接修订 v2（2026-09-23）

## 包版本 v2.2（2026-09-24）

- AnyLoc原SharePoint单文件和文件夹入口均返回HTTP 404；改用AnyLoc作者组织GitHub Release v1中固定的G/14、layer31、value、32-cluster、urban中心文件。
- 固定Release asset `dinov2_vitg14_l31_value_c32_urban_c_centers.pt`，197425 bytes，SHA-256 `a684e571f05c85c804e7301547d8620c28ae759e824adb9ac88294b080feaba0`。服务器脚本默认自动下载并用PyTorch加载验证[32,1536]中心，不需用户手动传VLAD文件。
- 原有题库、G/14特征、VLAD配置和448处理合同不变；不等价外部词典/Paris重训均未启用。
- 更新交接包：`server_baseline_package_v2_2_final_20260924.zip`。该包依然不含原图、模型权重、词典或特征。
- 45个文件通过SHA-256/大小/CRC校验；最终ZIP的SHA-256和字节数以同目录 `delivery_validation.json` 为准。

## 包版本 v2.1（2026-09-23）

- 修复 pilot0_score.py 缺少 hashlib 导入的问题，并新增最小端到端评分测试，覆盖特征索引、逐VLAD文件哈希及结果清单写出。
- 将特征提取器输出目录的创建移至服务器路径/原图/448图预检之后，避免预检失败留下阻塞重跑的空目录。
- 10项CPU单元测试、指定脚本Python编译、冻结题库17项检查均通过。该验证不包含服务器数据访问、GPU smoke、权重下载、全量resize或模型评分。
- 对应轻量交接包：server_baseline_package_v2_1_20260923.zip；不含图像、模型权重、词典或特征。题库仍为paris_local_v1_20260923；44query、168reference及所有P/N/I标签、图库ID和朝向不变。本修订只明确Linux路径、模型准备和全量448图像派生流程。

用户确认Z:/wangyq/映射到/home/nas/wangyq/，代码根目录/home/wangyq/Nav_Lmk/。使用image_relative_path读取真实panoid_panorama_i.jpg；view_id的__vi仅是内部ID。

原交接配置在模型前向时对归一化tensor缩放；本次按用户要求全量离线生成448图，采用Pillow RGB BICUBIC缩放、无损PNG保存，模型读取448 PNG后再ToTensor和ImageNet Normalize，不再resize。两种处理并非逐像素等价，故baseline request另立v2，不与旧特征缓存混用。尚无旧模型结果需要重算。

全量resize为12236图的确定性派生，不改变开发/缓冲/潜在留出身份，不允许在全量图上拟合词典；首轮模型特征仍只提取212活动图。

v2任务包还提供：官方G/14下载/结构检查、只取匹配AnyLoc中心的cache处理、server path/preflight、固定DINOv2 layer31 value提取器、FP32 cosine-hard VLAD、212图特征与冻结题库打分器、CPU单元测试。CPU验证不声称已通过服务器CUDA smoke test。
