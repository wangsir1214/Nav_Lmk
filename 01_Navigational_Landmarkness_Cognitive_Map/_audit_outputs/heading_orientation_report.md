# Paris ERP / Four-View Heading Audit

## 结论

现有巴黎数据不是“ERP 已经北向对齐”。当前可验证的方向关系是：

```text
view_i 的地理中心方位 = (heading_from_api + 90° * i) mod 360
i = 0, 1, 2, 3
```

因此：

- `view_0` 对应 Google Street View 元数据中的 panorama center heading；
- `view_1` 是其顺时针右转 90°；
- `view_2` 是其顺时针 180°；
- `view_3` 是其顺时针 270°，等价于左转 90°；
- 四张图不是固定的北、东、南、西，除非该 pano 的 `heading_from_api` 恰好接近 0°。

## Google 官方术语校准

Street View Tile API 将 metadata `heading` 定义为从正北顺时针量取的
罗盘方位角，范围 `[0,360]`，其中 `0` 为正北。Google Maps JavaScript API
将等价的 `centerHeading` 定义为全景瓦片中心的 heading。因此本报告中的
`heading_from_api` 是 ERP 水平中心对应的绝对地理方位，不是“相机输出已经
旋转到北向”的标志。

官方参考：

- <https://developers.google.com/maps/documentation/tile/streetview>
- <https://developers.google.com/maps/documentation/javascript/reference/street-view#StreetViewTileData.centerHeading>
- <https://developers.google.com/maps/documentation/streetview/metadata>
- <https://developers.google.com/maps/documentation/streetview/request-streetview>

## 证据链

### 1. ERP 下载与拼接没有北向校正

附件 `GSV_tiles_download_graph.ipynb` 的 cell 2：

- 按 Google panorama tile 的 `(x, y)` 原顺序下载；
- 创建 `26 * 512` by `13 * 512` 画布；
- 将 tile 直接粘贴到 `(x * 512, y * 512)`；
- 没有读取 `heading`、`centerHeading` 或 `pano_yaw_deg`；
- 没有执行水平 roll、循环平移或 north alignment。

该 notebook 证明 ERP 保留 Google tile 的原始局部坐标系，而不是正北居中的 ERP。

### 2. heading CSV 来自 Google Street View Tile API metadata

`GoogleAPIMETADAT/code/get_panoid_heading*.py` 和
`query_streetview_metadata.py` 调用：

```text
https://tile.googleapis.com/v1/streetview/metadata?panoId=...
```

最终 `Paris_Points_heading_3059.csv` 的 `heading_from_api` 与上游
`GSV_3100_heading_results.csv` 同名同值；最终文件只是删除 41 个 pano 后的 3,059 行版本。

### 3. 透视投影代码把 theta=0 映射到 ERP 水平中心

UrbanNav ZIP 中的 `Equirec2Perspec.py` 使用：

```python
X = (longitude / (2 * pi) + 0.5) * (width - 1)
```

所以 `THETA=0` 映射到 ERP 的 `x = 0.5 * width`。正 `THETA` 通过 y 轴旋转后映射到更大的 ERP x，即局部顺时针/向右方向。

`generate_perspective_data.py` 直接用局部角生成 16 个视角：

```python
for theta in np.arange(0, 360, 22.5):
    equ.GetPerspective(60, theta, 0, 84, 84)
```

它没有在切图阶段加入 heading。heading 是在消费图像时用于“绝对 yaw -> ERP 局部角”的。
这里的 `22.5°` 是相邻视图中心间隔；实际单图 FOV 是 `60°`，两者不能
混为一谈。

### 4. 现有 4x640 文件的像素级验证

审计脚本 `_audit_work/audit_view_heading_alignment.py` 对 6 个 pano 测试了：

```text
base offset in {0, 90, 180, 270}
x index order in {clockwise, counterclockwise}
```

共 8 种假设。结果：

- 6/6 的最优假设都是 `offset_0_clockwise`；
- 最优平均 RGB MAE 为 1.83–2.07；
- 第二名 MAE 为 19.39–25.91；
- 第二名误差是最优值的 10.1–13.4 倍。

这直接证明现有 `*_panorama_0..3.jpg` 确实来自 ERP 局部中心角
`0°/90°/180°/270°`，索引随顺时针方向增加。

可复核文件：

- `_audit_outputs/view_heading_alignment_audit.json`
- `_audit_outputs/figures/view_heading_alignment_diagnostic.jpg`

### 5. 独立地理锚点验证

样本 pano `mtTyLJmH81urjPeTJoalyg`：

```text
heading_from_api = 296.55°
pano -> Arc de Triomphe bearing = 294.94°
```

两者相差约 1.61°，且凯旋门位于 `view_0` 中央附近。另一些样本中，按
`(Arc bearing - heading_from_api) mod 360` 预测的 view index 也与凯旋门实际出现的视图一致。

## 导航任务应如何计算视图

设当前 pano 到下一 pano 的地理 bearing 为 `B_forward`，元数据中心朝向为 `H`：

```text
local_forward = (B_forward - H) mod 360
```

若要从 ERP 精确生成 route-aligned 四视角：

```text
front theta = local_forward
right theta = local_forward + 90°
back  theta = local_forward + 180°
left  theta = local_forward + 270°
```

不应简单把既有 `view_0` 永久命名为 front。既有四视角的中心间隔为 90°，只能选最接近路线 bearing 的一张，最大可能残差为 45°。正式方向选择实验最好从 ERP 按每一步的 route bearing 重新投影。

## action 应如何计算

方向动作可以完全基于坐标 bearing 推导，不依赖 panorama heading：

```text
turn = wrap_to_[-180,180](B_out - B_in)
turn > 0  -> right
turn < 0  -> left
abs(turn) small -> forward
```

heading 的作用是把绝对方向映射到图像局部坐标，不应参与左/右动作本身的正负判断。

## 旧 UrbanNav 中的方向风险

旧代码不是全部一致：

- `pano_data.py` 使用 `theta = yaw - heading`，若 yaw 是绝对地理方位，这个公式正确；
- `courier_game.py` 的一段随机路径数据生成使用 `theta = heading - bearing`，正负号相反，疑似水平镜像方向错误；
- `observations.py` 注释本身写有“注意检查 yaw-heading 的方向是否正确”；
- `rotation_yaw_` 在环境初始化时设为 0，但 reset 路径未见明确重新赋值，固定 episode replay 前需单测；
- 旧 RL 的预生成输入是 16 张 FOV=60°、84x84 图像，不是当前 4 张 FOV=90°、640x640 图像。

所以旧 RL 的主取图公式提供了设计意图，但不能替代固定 pano/yaw 的回归测试。

## 仍缺失的 provenance

在已授权并选择性扫描的目录中，尚未找到生成 `0-All_GSV_3059_4per` 的原始脚本。像素审计已经确认产物的方向关系，但后续仍应回收该脚本或重写一个可复现版本，并记录：

- ERP 输入哈希；
- `FOV=90°`；
- `theta=[0,90,180,270]`；
- pitch、输出尺寸、插值方法和 JPEG 参数；
- `heading_from_api` 的来源与版本。

## 安全问题

`query_streetview_metadata.py` 中存在硬编码、看起来可用的 Google API key。报告不复述该 key；应立即撤销/轮换，并改为环境变量或密钥管理器读取。
