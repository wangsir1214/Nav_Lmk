# 服务器交接修订 v2（2026-09-23）

题库仍为paris_local_v1_20260923；44query、168reference及所有P/N/I标签、图库ID和朝向不变。本修订只明确Linux路径、模型准备和全量448图像派生流程。

用户确认Z:/wangyq/映射到/home/nas/wangyq/，代码根目录/home/wangyq/Nav_Lmk/。使用image_relative_path读取真实panoid_panorama_i.jpg；view_id的__vi仅是内部ID。

原交接配置在模型前向时对归一化tensor缩放；本次按用户要求全量离线生成448图，采用Pillow RGB BICUBIC缩放、无损PNG保存，模型读取448 PNG后再ToTensor和ImageNet Normalize，不再resize。两种处理并非逐像素等价，故baseline request另立v2，不与旧特征缓存混用。尚无旧模型结果需要重算。

全量resize为12236图的确定性派生，不改变开发/缓冲/潜在留出身份，不允许在全量图上拟合词典；首轮模型特征仍只提取212活动图。
