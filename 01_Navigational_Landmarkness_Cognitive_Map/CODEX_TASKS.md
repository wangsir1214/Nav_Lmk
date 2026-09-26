# Codex Tasks

## 2026-09-22 Current task entry

Follow `PILOT0_EXECUTION_PLAN.md` and `SERVER_CODEX_HANDOFF_PILOT0.md` for the new local-retrieval Pilot 0. The first local deliverable is view manifest + spatial groups + P/N/I candidate relations and pair-review materials, reusing completed audits instead of rerunning a broad repository/data scan. The first server deliverable is the full-image baseline on a versioned task package.

The numbered tasks below are historical planning context. They do not override the current request or require completing the old route-choice gate before Pilot 0. Current numerical parameters and model versions must be verified during development rather than inferred from chat examples.

## Task 1: Repository inventory

First run only this task.

Read the local project directory and generate `repo_inventory.md`.

Report:

1. code directories;
2. data directories;
3. available street-view images;
4. metadata files;
5. DINOv2 embedding files;
6. four-view FOV=90° structure as the primary image input;
7. road graph / route / navigation task files;
8. CityBench / outdoor_navigation scripts;
9. runnable commands;
10. missing dependencies;
11. recommended first pilot.

Do not modify code in Task 1.

## Task 2: Data schema report

Find tables or JSON files that can support the schema in `DATA_SCHEMA.md`.

Output:

- `data_schema_report.md`

Include which columns exist, which are missing, and how to join files.

## Task 3: Build four-view street-view node table

Create a table of street-view nodes organized around four FOV=90° perspective views per panorama.

Expected output:

- `streetview_nodes.csv`

Suggested fields:

- node_id / pano_id;
- lat;
- lon;
- image_front / image_right / image_back / image_left paths;
- heading information for each view;
- optional full_panorama_path if available;
- road_id if available;
- route_id if available.

## Task 3b: Generate four-view panels

If image files exist, create preview panels for annotation/evaluation.

Expected output:

- `four_view_panels/`
- `four_view_panel_index.csv`

Each panel should show front / right / back / left views with heading labels.

Do not use raw full panorama as the first-stage model input unless explicitly requested.

## Task 4: Build road-edge table

If road graph or route data is available, create outgoing edge records.

Expected output:

- `road_edges.csv`

Suggested fields:

- edge_id;
- from_node;
- to_node;
- heading;
- road_id;
- route/task relation if available.

If road graph is unavailable, report what is needed.

## Task 5: Create landmark candidate schema and sample cases

Create `landmark_candidates_sample.jsonl` following `LANDMARKNESS_SCHEMA.md`.

Use a small set of nodes first. The first version may be manual, VLM-generated, or template-based.

Do not over-engineer.

## Task 6: Build landmark-anchored cognitive graph prototype

Create a small JSON graph following `LANDMARK_ANCHORED_GRAPH_SCHEMA.md`.

Expected output:

- `landmark_cognitive_graph_sample.json`

Start with 10–20 nodes if data exists.

## Task 7: Landmark-to-edge alignment pilot

If landmark azimuth and edge heading are available, compute angular alignment.

Expected output:

- `edge_alignment_cases.csv`
- `edge_alignment_summary.md`

## Task 8: Prepare annotation/evaluation package

Prepare cases for human or model evaluation.

Expected output:

- `annotation_cases.jsonl`
- `annotation_instructions.md`
- optional image panels.

## Task 9: Result summary

After running experiments, write:

- `RESULTS_SUMMARY.md`
- `ERROR_LOG.md`
- update `WORKLOG.md`
- update `TODO.md`
