# GSV_tiles_download_graph.ipynb execution audit

- Notebook: `D:\BaidudiskDownload\GSV_tiles_download_graph.ipynb`
- Cells: 132 total, 82 code, 74 executed code cells
- Cell index below is zero-based; notebook UI number is index + 1.

| Cell index | UI number | Execution count | Executed | First non-empty line |
|---:|---:|---:|:---:|---|
| 39 | 40 | 4 | yes | `import geopandas as gpd` |
| 41 | 42 | 5 | yes | `# 创建图，每个路段作为图的顶点` |
| 46 | 47 | 7 | yes | `def dist(x1, x2, y1, y2): #经纬度好像不能这么算距离` |
| 48 | 49 | 8 | yes | `import geopandas as gpd` |
| 50 | 51 | 9 | yes | `# 假设已经有了以下变量和数据` |
| 52 | 53 | 10 | yes | `#保存geo_df为shp文件，检查` |
| 55 | 56 | 10 | yes | `geo_df=gpd.read_file('/Users/fluer/Desktop/Research/code/DownloadData-main/Manhattan/panoid4090_toroad_0805.shp')` |
| 60 | 61 | 12 | yes | `import networkx as nx` |
| 64 | 65 | - | no | `# 修改中间版本` |
| 66 | 67 | - | no | `# 再次修改，更新的中间版本` |
| 68 | 69 | 13 | yes | `#更新后` |
| 69 | 70 | 14 | yes | `# 将列表转换为 DataFrame` |
| 70 | 71 | 15 | yes | `end_points_df.head()` |
| 71 | 72 | 16 | yes | `# 将 DataFrame 保存为 CSV 文件` |
| 73 | 74 | 18 | yes | `import numpy as np` |
| 75 | 76 | - | no | `#更新前的版本` |
| 77 | 78 | 19 | yes | `#更新后版本` |
| 81 | 82 | 39 | yes | `# 更新前的版本` |
| 83 | 84 | 20 | yes | `# 新的end_points的遍历方式的更新，参考：` |
| 84 | 85 | 105 | yes | `print(street_view_graph)` |
| 86 | 87 | 21 | yes | `from networkx.readwrite import json_graph` |
| 88 | 89 | 22 | yes | `#保存` |
| 95 | 96 | 61 | yes | `import pandas as pd` |

## Runtime interpretation

- Cells 64, 66, and 75 are unexecuted variants and are not runtime evidence.
- Cell 81 is an executed older connector variant; cell 83 is the later executed connector implementation.
- Cell 83 adds all neighboring-road endpoint pano pairs without a weight, explaining the null-weight connectors.
- Cell 86 serializes the NetworkX graph; cells 88 and 95 export edge/endpoint tables.
- The notebook contains no `Paris` path or identifier. Its persisted paths and cell outputs are Manhattan-specific, including longitude near -74 and a 10,956-node graph.
- Therefore the notebook is strong evidence for the graph-construction algorithm template, but not direct run provenance for the 3,058-node Paris JSON.
- Full source and captured output snippets are preserved in the companion JSON.
