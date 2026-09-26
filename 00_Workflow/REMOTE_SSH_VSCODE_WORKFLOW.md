# Remote SSH / VSCode / Codex Workflow

## Principle

Local machine is for:

- lightweight editing;
- note organization;
- prompt preparation;
- paper writing;
- Git operations when convenient.

Remote server is for:

- large street-view image data;
- model weights;
- embeddings;
- GPU inference;
- long-running experiments;
- Docker execution.

Codex should usually run in the same environment where the code will be executed.

If the task requires server paths, GPU, Docker, or large data, start Codex inside the remote SSH terminal or VSCode Remote SSH session rather than only on the local Windows copy.

## Recommended server layout

```text
/home/nas/wangyq/
├── git/
│   └── <ProjectName>.git
├── projects/
│   └── <ProjectName>/
├── data/
│   └── <ProjectName>/
├── model_weights/
│   └── <ModelName>/
└── outputs/
    └── <ProjectName>/
```

## Recommended local layout

```text
C:\Users\<User>\Desktop\<ProjectName>\
```

The exact paths may vary. Keep placeholders in docs when the server or local paths are not fixed.

## Docker notes

Docker container names may vary across servers. Do not hard-code names such as `wyq_pku4090`.

Before running experiments, Codex should check:

```bash
pwd
which python
python --version
nvidia-smi
docker ps
```

If inside a container, also check:

```bash
hostname
ls /home/nas/wangyq
```

## Large data rule

Large raw images, embeddings, model checkpoints, and caches should stay on the server.

Git should store:

- source code;
- configs;
- scripts;
- small samples;
- README;
- environment files;
- summaries and selected outputs.

Git should not store:

- full street-view image folders;
- full embeddings if large;
- checkpoints;
- temporary caches;
- raw experiment dumps.

Use `.gitignore` to exclude them.
