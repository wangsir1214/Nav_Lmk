# Paris Panorama Projection Audit

## 官方语义

Google Street View Tile API 的 metadata 文档定义 `heading` 为：

> “The compass heading, measured in degrees, clockwise from North. Headings are returned within the range [0,360], with 0 representing due North.”

同一页面的示例 metadata 含 `heading: 94.35`。Google Maps JavaScript API 的 `StreetViewTileData.centerHeading` 进一步定义为：

> “The heading (in degrees) at the center of the panoramic tiles.”

这两条官方定义支持将 Tile metadata 的 heading 解释为“拼接全景瓦片中心对应的绝对罗盘方位”。参考：

- <https://developers.google.com/maps/documentation/tile/streetview>
- <https://developers.google.com/maps/documentation/javascript/reference/street-view#StreetViewTileData.centerHeading>

Street View Static API 的官方 metadata 示例只返回 `copyright`、`date`、`location`、`pano_id`、`status`；其请求参数 `heading` 是请求相机朝向，不是下载 ERP 的中心元数据。参考：

- <https://developers.google.com/maps/documentation/streetview/metadata>
- <https://developers.google.com/maps/documentation/streetview/request-streetview>

因此“Tile API metadata 有 heading，而 Static API metadata 示例没有 heading”的历史笔记基本正确，但两者的 `heading` 角色必须区分：前者描述全景瓦片中心，后者控制请求输出视线。

## 本地投影代码

ZIP 中的 `Equirec2Perspec.py` 只实现：

```python
GetPerspective(FOV, THETA, PHI, height, width)
```

它将 `THETA` 作为 ERP 的局部水平角；没有读取 `heading`、`centerHeading` 或 `pano_yaw_deg`，也没有执行水平循环平移/north alignment。`GSV_tiles_download_graph.ipynb` 的 tile 拼接按 `(x,y)` 直接贴到画布，同样没有北向校正。

所以对本项目的 ERP 坐标，设 `H=heading_from_api`，则：

```text
地理中心(view_i) = (H + theta_i) mod 360
```

其中 `theta_i` 是投影函数的局部 `THETA`，不是 API 请求的绝对 heading。

## 16 视图与 4 视图

历史 UrbanNav 代码审计中找到批量生成逻辑：

```python
for theta in np.arange(0, 360, 22.5):
    equ.GetPerspective(60, theta, 0, 84, 84)
```

因此旧模型输入是 **16 个中心角间隔 22.5°、每张 FOV=60°** 的视图。间隔和 FOV 是两个不同参数；旧视图之间有重叠，不能写成“每张视角 22.5°”。

当前巴黎 `0-All_GSV_3059_4per` 的四视角通过像素审计确认中心角为局部 `0/90/180/270°`，且资产为 640x640、FOV=90°。但 ZIP 和 Z 盘两个巴黎代码目录都没有找到生成该目录的批量脚本，因此其 JPEG 插值、pitch、压缩参数和执行路径仍缺 provenance。

## 正式路线方向的生成规则

设当前 pano 到下一 pano 的道路 bearing 为 `B`：

```text
local_forward = (B - H) mod 360
front = local_forward
right = local_forward + 90
back = local_forward + 180
left = local_forward + 270
```

四个角度传给 ERP 投影函数后，再记录 `H`、`B`、FOV、pitch、输出尺寸、插值和 JPEG 参数。现有固定四视角只用于总览、候选发现和第一轮人审；正式 route-choice 行为输入必须使用 route-aligned views。

## 仍需验证

- 历史16视图的批量输出目录与 JPEG provenance；
- 当前四视角批处理的原始脚本和参数；
- 个别 pano 的 ERP 水平 seam、roll/pitch 与路面方向的回归测试。

