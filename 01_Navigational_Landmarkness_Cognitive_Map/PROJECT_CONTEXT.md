# Project Context: Navigational Landmarkness and Cognitive Map

## 2026-09-22 Current entry point: Pilot 0

2026-09-24当前状态：服务器已回传v2.2-final完整图基线。44query/168reference、82P/6160N/1150I保持冻结。本地核对当前NAS结果，并从212个VLAD独立复算7392相似度；最大差4.23e-7，主分析及80P敏感性均为Recall@1=42/44、@5=@10=43/44，margin中位数约0.099402。两项失败保留。主分析正例数为8题1P、34题2P、2题3P；样本来自12pano、6道路，原area_id仅paris_arc，另以道路成对关系做三子片区报告层汇总。该结果可作候选区域贡献实验的开发参照，尚不能证明同街道细粒度定位或地标/认知地图功能。原始CUDA smoke、preflight、完整性及环境日志仍需从服务器/home/wangyq镜像至NAS。详见outputs/pilot0/server_return_audit_20260924/LOCAL_BASELINE_REVIEW.md。

The user supplied two updated research conversations. The current first experiment is local place retrieval as an assay of candidate visual-cue contribution: build a view manifest and positive/negative/ignore task, run a full-image baseline, then generate VLM candidates and compare descriptor/input interventions against matched regions.

See `PILOT0_EXECUTION_PLAN.md` for the Chinese requirements synthesis and `SERVER_CODEX_HANDOFF_PILOT0.md` for handoff. Human labels and the v1 task remain frozen; the server ran baseline_request_v2.json. The development baseline is complete and its scores are independently confirmed locally; server execution reports still need archiving. Candidate generation, region interventions and an independent evaluation benchmark have not run.

The long-term Evidence → Memory → Map → Agency direction is retained. Prior route-continuation P1A/P1B gates remain historical/task-specific and do not block this new Pilot 0.

## Working title

Navigational Landmarkness in Street-View Environments: From Visual Cues to Landmark-Anchored Cognitive Maps

## Core research goal

This project studies how humans or agents recognize, understand, remember, and navigate urban environments through landmarks.

The core question is:

> Which visual elements in street-view environments become navigational landmarks, and how do these landmarks serve as anchors for cognitive maps that support localization, orientation, place memory, and route decisions?

## Functional definition of landmarkness

A visual element gains landmarkness when it helps a human or agent reduce spatial uncertainty or organize spatial knowledge.

A landmark can be:

- an object, such as a tower, sign, bridge, or church;
- a structural cue, such as a corner, intersection, square, street width, or road hierarchy;
- a textual cue, such as shop signs, road signs, or station names;
- a scene-level cue, such as a commercial street, residential facade pattern, tree-lined corridor, or open plaza;
- an atmospheric or visual field, such as a recognizable style, density, openness, color/material pattern, or urban texture.

## Core shift from previous thinking

The project is not primarily about active perception.

Active inspection, panoramic search, and tool-use can be useful experimental conditions, but the central scientific object is:

> landmarkness as a functional role in urban cognitive mapping.

## Why cognitive map matters

A cognitive map is not a precise GIS map or a full SLAM reconstruction. In this project, it is operationalized as a sparse, landmark-anchored representation that connects:

- street-view nodes;
- road edges;
- landmark anchors;
- scene-level fields;
- spatial relations;
- route memory.

This allows the project to move from single-view visual analysis to navigation-relevant spatial understanding without immediately building a full navigation agent.

## Minimal contribution target

The first target is a small but convincing prototype:

1. estimate landmarkness at street-view nodes;
2. represent object / structural / scene-level landmarks with direction and function;
3. align landmark anchors to candidate road edges;
4. build a small landmark-anchored cognitive graph;
5. test whether these landmarks support place memory or navigation decisions.


## First-stage image input

The audit and candidate-discovery stage should use four fixed FOV=90-degree
perspective views per street-view panorama. A formal route-choice task should use
route-aligned FOV=90-degree views reprojected from the ERP.

The full panorama, if available, should be preserved as raw source and future extension, but the first experiments should not depend on full equirectangular panorama input.

This keeps the project aligned with existing Paris navigation assets and avoids making panoramic active search the main task too early.
