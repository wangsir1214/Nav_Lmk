# Code Reproducibility Guide

## Script requirements

Every new experiment script should support CLI arguments for:

- input metadata path;
- input embedding path;
- image directory;
- road graph path if needed;
- output directory;
- random seed;
- model name if applicable;
- city / subset;
- number of samples.

## Output requirements

Each experiment should write:

- result CSV or JSONL;
- run config JSON;
- log file;
- summary Markdown;
- figures if applicable.

## Environment

Record when relevant:

```bash
python --version
pip freeze > environment_freeze.txt
nvidia-smi
git status
git rev-parse HEAD
```

## Data

Do not commit large raw data. Commit small samples and schema documentation.

## Naming

Use clear filenames with parameters, for example:

```text
landmark_candidates_city-Paris_n-100_seed-42.jsonl
landmark_graph_city-Paris_subset-arc_20260706.json
edge_alignment_cases_city-Paris_v1.csv
```
