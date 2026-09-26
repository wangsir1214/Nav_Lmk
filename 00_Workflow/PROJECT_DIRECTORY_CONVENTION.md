# Project Directory Convention

## Recommended project structure

```text
<ProjectName>/
├── Research_Workspaces_v3/
├── code/ or src/
├── scripts/
├── configs/
├── data/
│   ├── samples/
│   └── README.md
├── outputs/
│   ├── summary/
│   ├── tables/
│   ├── figures/
│   └── cases/
├── docs/
└── README.md
```

## For large server-side projects

```text
/home/nas/wangyq/projects/<ProjectName>/
├── Research_Workspaces_v3/
├── CityBench-main/
├── scripts/
├── configs/
├── outputs/
└── README.md

/home/nas/wangyq/data/<ProjectName>/
├── streetview_images/
├── embeddings/
├── metadata/
└── navigation_tasks/
```

## Path documentation

Every experiment should write down:

- input path;
- output path;
- command;
- Python environment;
- model name;
- data version;
- timestamp.

Use `WORKLOG.md` and `RESULTS_SUMMARY.md` for this.
