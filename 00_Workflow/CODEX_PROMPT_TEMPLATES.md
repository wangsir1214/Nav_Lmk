# Codex Prompt Templates

## Inventory

```text
请先只读不改，扫描项目结构。
生成 repo_inventory.md，列出：
1. 代码目录；
2. 数据目录；
3. 街景图像和四视角/panorama 数据；
4. DINOv2 embeddings；
5. road graph / route / navigation task 数据；
6. 可运行脚本；
7. 缺失文件；
8. 最适合快速跑通的第一个 pilot。
```

## Safe coding

```text
在修改代码前，请先说明你打算修改哪些文件、为什么修改、预期输出是什么。
不要修改 99_Archive。
```

## Build schema

```text
请根据 LANDMARKNESS_SCHEMA.md 和 LANDMARK_ANCHORED_GRAPH_SCHEMA.md，先生成最小数据结构和样例 JSONL，不要训练模型。
```

## Run pilot

```text
请根据 EXPERIMENT_DESIGN.md 执行最小可运行 pilot。
运行前确认输入文件存在。
运行后保存命令、输出、错误和结果摘要。
```

## End session

```text
请更新：
- WORKLOG.md
- RESULTS_SUMMARY.md
- ERROR_LOG.md
- TODO.md
如果产生新的研究或工程决策，也更新 DECISIONS.md。
```

## Ask for missing data

```text
如果缺少数据，不要虚构路径。
请列出缺少的文件、必须包含的字段、建议的文件名、以及我该如何准备。
```
