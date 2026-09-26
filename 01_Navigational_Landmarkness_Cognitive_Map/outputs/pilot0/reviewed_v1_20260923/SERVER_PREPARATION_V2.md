# 给服务器 Codex：路径、模型、448 全量预处理与 baseline v2

本页为实际执行入口，覆盖并取代 SERVER_BASELINE_TASK.md 中旧 v1 的路径映射和 tensor resize 预处理段。开发题库本身不变：paris_local_v1_20260923，44 query、168 reference、82P/6160N/1150I。当前使用交接包v2.2-final：修复评分器哈希校验导入，替换失效的 AnyLoc SharePoint 词典入口，并确保提取器在预检通过后才创建输出目录。10项CPU测试、Python编译和17项冻结题库检查已通过；服务器模型分数尚未运行。

## 冻结的路径和身份合同

服务器用户确认的挂载映射是：

| Windows Z 盘 | Linux 服务器 |
|---|---|
| `Z:/wangyq/GSV_Paris/0-All_GSV_3059_4per` | `/home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per` |
| `Z:/wangyq/GSV_Paris/0-All_GSV_3059_panorama` | `/home/nas/wangyq/GSV_Paris/0-All_GSV_3059_panorama` |
| `Z:/wangyq/Street_view_and_points_Paris/GoogleAPIMETADAT/Paris_Points_heading_3059/Paris_Points_heading_3059.csv` | `/home/nas/wangyq/Street_view_and_points_Paris/GoogleAPIMETADAT/Paris_Points_heading_3059/Paris_Points_heading_3059.csv` |
| 本项目代码和配置 | `/home/wangyq/Nav_Lmk/` |

磁盘原图文件的实际命名为 `{panoid}_panorama_0.jpg` 至 `{panoid}_panorama_3.jpg`。任务/复核的内部ID是 `{panoid}__v0` 至 `{panoid}__v3`；`__vN` 是review ID，不是文件名。所有代码必须从 `image_relative_path` 读取原图，不得拿 view_id 拼路径或自然排序后猜图文对应。

固定图的绝对中心朝向沿用已核验公式：`absolute_heading = (heading_from_api + 90 * view_index) % 360`。服务器图像处理不能旋转、调换或把它们静态命名成 front/right/back/left。首先比对服务器heading CSV字节SHA-256与任务view manifest里唯一的`metadata_source_sha256`；然后检查12236条view ID、panoid文件名、四视图完整性和全部绝对朝向。之后所有使用朝向的代码统一读manifest的`absolute_heading`。本地复核图用`__vN`标签并不改变磁盘命名和绝对朝向。

## 顺序一：部署并验证小型任务包

将最新的 `server_baseline_package_v2_2_final_20260924.zip` 放进服务器可访问的传输目录；不要把原始街景、checkpoint、词典或特征放进Git。解压到下列任务目录（若服务器实际安装位置不同，统一编辑 `configs/paths.server.example.json` 中 `task_dir`，代码根保持 `/home/wangyq/Nav_Lmk/`）：

```bash
PROJECT_DIR=/home/wangyq/Nav_Lmk
TASK_DIR="$PROJECT_DIR/server_tasks/paris_local_v1_20260923_v2"
if [ -e "$TASK_DIR" ]; then echo "Task directory already exists; verify its package hash or choose a new versioned directory: $TASK_DIR"; exit 1; fi
mkdir -p "$TASK_DIR"
unzip /path/to/server_baseline_package_v2_2_final_20260924.zip -d "$TASK_DIR"
cd "$PROJECT_DIR"
```

先做离线包和冻结题库校验，再写入服务器私有路径配置：

```bash
python "$TASK_DIR/scripts/pilot0_delivery.py" verify --task-dir "$TASK_DIR"
python "$TASK_DIR/scripts/pilot0_verify_frozen_task.py" --task-dir "$TASK_DIR"
cp "$TASK_DIR/configs/paths.server.example.json" "$TASK_DIR/configs/paths.server.json"
```

在完整实验前记录服务器主机、`pwd`、`which python`、Python/torch/torchvision/NumPy/Pillow版本、`nvidia-smi`、`df -h`、GPU和显存。该任务是单卡、fp32、小batch优先的开发基线；先确认有足够磁盘空间保存12236张PNG和特征。

源码使用DINOv2固定commit `7764ea0f912e53c92e82eb78a2a1631e92725fc8`。若仓库还不存在：

```bash
mkdir -p "$PROJECT_DIR/third_party"
git clone https://github.com/facebookresearch/dinov2.git "$PROJECT_DIR/third_party/dinov2"
git -C "$PROJECT_DIR/third_party/dinov2" checkout 7764ea0f912e53c92e82eb78a2a1631e92725fc8
```

已存在时不要覆盖服务器代码；检查是否正好是该commit且没有tracked修改。AnyLoc实验仅借用固定版本源码里的提取/聚合定义，不通过`torch.hub`漂移的main分支加载模型。

先检查原图目录和服务器heading CSV：

```bash
python "$TASK_DIR/scripts/pilot0_server_preflight.py" \
  --task-dir "$TASK_DIR" \
  --paths "$TASK_DIR/configs/paths.server.json" \
  --report "$TASK_DIR/validation/server_preflight_before_resize.json"
```

该检查核对12236个ID/文件名/朝向、服务器heading CSV源hash及212张活动图逐张原图SHA-256。任一不同，先查清数据版本，不能用同名图继续运行。

## 顺序二：获取正确权重和VLAD中心

### 固定版本 AnyLoc 词典下载入口（v2.2）

原AnyLoc SharePoint单文件及公开文件夹在当前服务器环境均返回HTTP 404。不要继续重试这些链接。AnyLoc作者组织的`AnyLoc/DINO` GitHub Release v1另有独立的匹配词典资产：

- Release说明：`https://github.com/AnyLoc/DINO/releases/tag/v1`
- 固定文件：`dinov2_vitg14_l31_value_c32_urban_c_centers.pt`
- 下载URL：`https://github.com/AnyLoc/DINO/releases/download/v1/dinov2_vitg14_l31_value_c32_urban_c_centers.pt`
- Release/asset ID：`127038019` / `132758258`；文件大小197425 bytes。
- 已独立核验SHA-256：`a684e571f05c85c804e7301547d8620c28ae759e824adb9ac88294b080feaba0`。

更新到交接包v2.2后，下载脚本默认从该固定Release资产获取中心，不需要用户手动下载：

```bash
python "$TASK_DIR/scripts/pilot0_prepare_weights.py" --component vlad
```

脚本先校验文件大小和固定SHA-256，再用PyTorch安全加载并要求张量形状`[32,1536]`、有限且非零中心；最后记录来源URL、release/asset ID与文件hash到`.provenance.json`。若HTTP或SHA校验失败即停止，不能回退到其他domain、层或重新拟合。旧SharePoint cache ZIP流程仍可通过`--vlad-source cache-zip`显式选用，但已知链接现返回404。

已经下载的 `dinov2_vits14_pretrain.pth`、`dinov2_vitb14_pretrain.pth` 与本基线不匹配，不能替代G/14。需要额外取得官方标准版（0 register tokens）的G/14权重：

```text
/home/nas/wangyq/model_weights/dinov2/torch/hub/checkpoints/dinov2_vitg14_pretrain.pth
```

官方固定版本的权重来源为：
`https://dl.fbaipublicfiles.com/dinov2/dinov2_vitg14/dinov2_vitg14_pretrain.pth`

还需要下载匹配的预训练VLAD **聚类中心**；它不是在巴黎数据上重新训练整个VLAD网络。AnyLoc官方示例提供的cache压缩包包含多个词典。官方来源说明及原始分享链接见包内`official_source_check/additional_sources.json`、`AnyLoc_demo_notebook_a9fda68.json`和`AnyLoc_demo_utilities_a9fda68.py`。只抽取G/14、block31 value、32 cluster、urban中心：

```text
/home/nas/wangyq/model_weights/VLAD/dinov2_vitg14/l31_value_c32/urban/c_centers.pt
```

当前GitHub Release资产直接提供`c_centers.pt`，脚本按固定文件名和SHA获取，不依赖ZIP内路径猜测。不要拿S/B/其他层或其他domain的中心凑数。

这里称作“VLAD模型”实际是预训练**聚类词典/中心**，不是在研究样本上训练一个新的神经网络。服务器内的`pilot0_vlad.py`实现AnyLoc所需的固定赋值与残差聚合；词典按source/hash固定。

运行下载/验证脚本：

```bash
python "$TASK_DIR/scripts/pilot0_prepare_weights.py" --component all
```

若目标位置已存在文件但无由本脚本创建的provenance sidecar，程序会停下来，避免仅凭shape把来源未知的G/14权重或聚类中心当作官方文件。核实来源后，才显式加`--trust-existing-artifacts`；这会如实记录其来源是“预存文件、来源未由脚本独立验证”，请在SERVER_TO_LOCAL.md补上管理员提供/校验过的来源证据。

工具会记录权重/词典SHA-256、文件大小、来源、checkpoint关键层结构和词典`[32,1536]`形状到各自的`.provenance.json`。之后还要做真正模型`strict=True`装载的GPU smoke test。

## 顺序三：全量生成448×448视图缓存

用户指定输出目录：

```text
/home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per_448_448
```

处理固定视图清单中的**全部12236张**640×640视图（3059个pano×4），包含开发、缓冲和潜在留出条目；这只是确定性派生缓存，不改变split，不拟合VLAD词典，也不会把潜在留出加入当前212图特征或评分。输出使用Pillow RGB+BICUBIC、448×448、无损8-bit PNG：`{panoid}_panorama_{0|1|2|3}.png`。原始640 JPEG不会被覆盖或改写。朝向和角色沿用每个panoid/view_index原记录。

本机以Pillow 12.3.0实现并做确定性往返验证；服务器应在任务Python环境固定`Pillow==12.3.0`，并在运行日志记录实际版本。中途断开可以同命令续跑；代码逐图比对源/输出哈希，对异常的不完整尾日志留证，对已有异配置缓存则停止。不要用`rm -rf`清目录；若已有目录合同不同，改到新的派生目录并更新paths配置。

```bash
python -m pip install 'Pillow==12.3.0'
python "$TASK_DIR/scripts/pilot0_resize_views.py" \
  --manifest "$TASK_DIR/data/view_manifest.csv" \
  --source-dir /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per \
  --output-dir /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per_448_448 \
  --task-dir "$TASK_DIR" \
  --expected-count 12236 \
  2>&1 | tee "$TASK_DIR/validation/resize_448_run.log"
```

输出根下`_provenance/resize_manifest.csv`保存view ID、原始文件名、输出PNG名、原图/输出hash、data split与绝对heading；`resize_config.json`记录算法和Pillow版本；`resize_summary.json`报告完整数量与运行时间。

448离线PNG是本次正式v2输入契约，因此后续模型从PNG读取→转tensor→除255→ImageNet mean/std归一化，不得再执行第二次resize或裁剪。该契约把上一版“归一化tensor上用torchvision resize”的实现具体化为有哈希的磁盘派生图；量化和Pillow/Torchvision实现细节可能有小差异，所以本次请求ID是独立的`...448png...v2`，不能和v1特征混用。没有旧版实验分数要迁移。

resize结束后再做preflight，要求12236项完整、manifest hash一致，并校验212张活动原图及448 PNG的hash/尺寸：

```bash
python "$TASK_DIR/scripts/pilot0_server_preflight.py" \
  --task-dir "$TASK_DIR" \
  --paths "$TASK_DIR/configs/paths.server.json" \
  --require-resize \
  --report "$TASK_DIR/validation/server_preflight_after_resize.json"
```

## 顺序四：一张图 smoke test，再处理正式活动集

用一张query通过权重strict load、CPU/GPU前向、value维度、VLAD中心加载、NumPy与Torch独立聚合比对及重复性检查：

```bash
python "$TASK_DIR/scripts/pilot0_smoke_g14.py" \
  --task-dir "$TASK_DIR" --paths "$TASK_DIR/configs/paths.server.json" \
  --device cuda \
  --report "$TASK_DIR/validation/g14_vlad_smoke.json"
```

必须通过shape `[1,3,448,448]` → `[1024,1536]` → `[49152]`、有限值和单位范数；重复前向及Torch/NumPy VLAD数值差不高于1e-5。报错就停下来检查环境/权重/实现，不能放宽容差掩盖不一致。

只有smoke test通过后，提取**题库活动212图**而非全部12236张；448全量缓存和212图实验特征是两件不同事情。保存本地patch与VLAD向量用于以后区域干预：

```bash
FEATURE_DIR=/home/nas/wangyq/outputs/Paris_local_v1_20260923/features_g14_l31_value_c32_urban_448png_v2
python "$TASK_DIR/scripts/pilot0_extract_features.py" \
  --task-dir "$TASK_DIR" --paths "$TASK_DIR/configs/paths.server.json" \
  --device cuda --output "$FEATURE_DIR" \
  --smoke-report "$TASK_DIR/validation/g14_vlad_smoke.json" --log
```

该脚本以明确ID join，不猜特征行顺序；它拒绝非空旧输出目录，输出含patch `[1024,1536]` 和VLAD `[49152]` 的float32 `.npy`、212行`feature_index.csv`、输入hash与`run_config.json`。大特征只保存在NAS输出路径，不复制进GitHub。若显存不足，先减小batch（当前为单图前向），记录实际情况；不要改为B/14权重或改词典。

使用固定题库和v2配置打分：

```bash
python "$TASK_DIR/scripts/pilot0_score.py" \
  --task-dir "$TASK_DIR" --feature-dir "$FEATURE_DIR" \
  --output /home/nas/wangyq/outputs/Paris_local_v1_20260923/baseline_g14_v2
```

评分代码屏蔽I后对P∪N排名，保留7392个关系的相似度，输出Recall@1/5/10、逐题best positive rank与`max(P)-max(N)` margin、全排名、每题top5 negative及同44 query/168 gallery下的80P边界敏感性。不得根据模型结果删改标签或预设通过率。

## 返回本地

将验证报告、weight/词典hash与来源、环境/nvidia-smi信息、212图`feature_index.csv`、基线输出、失败/低margin图卡和`SERVER_TO_LOCAL.md`汇总给本地。权重和大型特征留服务器。先检查实现和哈希，再解释结果；44view来自12pano、6道路、3片区，应按query描述并附pano/道路分组，避免伪重复。完整图基线是线索干预的测量参照，不单独证明某线索有landmarkness。
