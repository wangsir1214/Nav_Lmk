# Experiment Design

## 2026-09-24 Parallel next-stage pilot

Run the single-view candidate/contribution assay and a small continuous-route feasibility pilot in parallel. The frozen 44-query retrieval task remains valid for the first assay. A separate reviewed same-road hard-negative task is needed before fine-localization claims, but is not a prerequisite for Qwen candidate generation. Route-choice scores require human-confirmed legal exits/actions, route-aligned views and a non-leaking learned-route continuation task; provisional mined maneuvers are not gold labels. The concrete handoff and review gates are in `NEXT_STAGE_QWEN_ROUTE_HANDOFF_20260924.md`.

## 2026-09-22 Current first experiment

Current execution order: view manifest → spatial retrieval task with P/N/I and pair audit → full-image DINOv2+VLAD baseline → single-view Qwen candidate proposal → matched-region descriptor interventions → stratified input interventions → frozen replication.

The detailed current protocol interpretation, evidence limits, pending parameters and local/server ownership are in `PILOT0_EXECUTION_PLAN.md`. The modules below remain the broader research roadmap; they are not simultaneous Pilot 0 implementation requirements. The former 15-route human gate and route-aligned reprojection requirement belong to the route-choice task, not the new fixed-view local retrieval task.

## Core question

Which street-view visual cues become navigational landmarks, and how do they anchor cognitive maps that support place memory and route decisions?

## Module A: Landmarkness Estimation at Street-view Nodes

### Goal

Given a street-view node, estimate which visible elements have landmarkness.

### Input

- audit/candidate-discovery input: four fixed FOV=90-degree perspective views per panorama;
- formal route-choice input: four route-aligned FOV=90-degree views reprojected from ERP;
- single current view for ablation;
- full panorama only if available as raw source or later ablation;
- optional current heading;
- optional road graph context;
- optional route/navigation context.

### Output

- landmark candidates;
- candidate type;
- azimuth / direction if available;
- landmarkness dimensions;
- reason.

### Possible methods

- human annotation;
- VLM candidate generation;
- DINOv2 / scene clustering for scene-level cues;
- POI or OSM support if available.

### Evaluation

- human-model agreement;
- consistency across views;
- whether candidates are describable;
- whether candidates are stable and distinctive.

## Module B: Landmark-to-Edge Alignment at Intersections

### Goal

Connect landmark anchors to candidate road edges.

### Input

- landmark candidates with azimuth;
- road graph outgoing edges with heading;
- route instruction or target direction if available.

### Output

- supported edge;
- angular alignment error;
- evidence-action explanation;
- ambiguity score.

### Evaluation

- edge selection accuracy;
- improvement over image-only / random-object baselines;
- landmark-list vs full-image comparison;
- action consistency with human-selected landmarks.

## Module C: Landmark-Anchored Cognitive Map Evaluation

### Goal

Test whether landmarks help form a useful cognitive map.

### Candidate tasks

1. Place recognition  
   After seeing a node or its landmarks, identify whether another view is the same place or nearby.

2. Route memory  
   Given a short route, recall the sequence using landmarks.

3. Similar-place discrimination  
   Distinguish visually similar street nodes using landmark anchors.

4. Wrong-turn recovery  
   Given a mismatch between expected landmark and current view, detect possible wrong direction.

5. Area identity  
   Use scene-level landmarks to identify a corridor, plaza, boulevard, or district-like region.

## Observation conditions

Active inspection is optional and should be treated as an experimental condition, not the main contribution.

Possible conditions:

- single-view passive;
- fixed four-view passive for audit and P1A candidate elicitation;
- route-aligned four-view passive for P1B route continuation;
- four-view panel with heading labels;
- full panorama passive only as optional later ablation;
- active inspection / evidence acquisition;
- landmark-only representation;
- random-object control;
- human-selected landmark control.

## First pilot recommendation

Start with a small subset:

- 20–100 Paris street-view nodes;
- use fixed four FOV=90-degree views for audit/P1A and route-aligned views for P1B;
- preferably human-approved nodes from the audited full-graph candidate pool;
- 3–5 landmark candidates per node;
- simple road-edge alignment when outgoing edge headings are available;
- a small human or manual validation set.


## Full panorama policy

Do not make the raw equirectangular panorama the default input in the first pilot.

Use full panorama only when the experiment explicitly requires:

- continuous angular localization;
- boundary-crossing object handling;
- BFoV / GCD evaluation;
- active evidence acquisition;
- panoramic memory.

For P1A, approximate landmark direction by the fixed-view heading first. For P1B,
reproject the ERP around the route bearing before measuring a directional choice.
