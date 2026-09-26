# Data Schema

## Required inputs

### Street-view metadata

Minimum columns:

- `pano_id` or `node_id`;
- `lat`;
- `lon`.

Useful columns:

- `heading_from_api`;
- `road_id`;
- `city`;
- `full_panorama_path`;
- `timestamp`.

### Image files

Canonical audit/P1A format:

- four fixed FOV=90-degree perspective views per panorama;
- local ERP centers `0/90/180/270` degrees for view indices `0/1/2/3`;
- absolute centers `(heading_from_api + 90 * view_index) mod 360`.

Formal P1B derived format:

- route-aligned front/right/back/left views reprojected from ERP;

Optional formats:

- a single current view for ablation;
- raw ERP for continuous-angle experiments.

### Embeddings

- DINOv2 matrix, currently 3059 x 384 float32 for Paris;
- pano-ID index aligned by explicit ID, not assumed row order alone.

### Road graph and route data

Useful fields:

- `node_id`;
- `edge_id`;
- `from_node`;
- `to_node`;
- `bearing`;
- `road_id` / OSM segment;
- `route_id`;
- `step_idx`;
- `provisional_maneuver` or `gold_action`;
- `action_status` (`provisional`, `human_verified`, or `gold`);
- `decision_zone_id`;
- `legal_departure_count`.

## Derived outputs

### streetview_nodes.csv

Suggested columns:

- `node_id` / `pano_id`;
- `lat`, `lon`;
- `heading_from_api`;
- `image_view_0` through `image_view_3`;
- `heading_view_0` through `heading_view_3`;
- `full_panorama_path`;
- optional route-aligned image paths and `route_bearing`;
- `road_id`, `route_id`, and `scene_cluster` when available.

### road_edges.csv

Suggested columns:

- `edge_id`, `from_node`, `to_node`;
- `bearing`, `road_id`, and `edge_type`;
- `direct_graph_edge` and `transition_hops`;
- `decision_zone_id` and `legal_departure_count`;
- `action`, `action_status`, and route relation.

### landmark_candidates.jsonl

Use `LANDMARKNESS_SCHEMA.md`. Keep fixed-view identity separate from
route-relative direction.

### landmark_cognitive_graph.json

Use `LANDMARK_ANCHORED_GRAPH_SCHEMA.md` after the feasibility gate.

### edge_alignment_cases.csv

Suggested columns:

- `case_id`, `node_id`, `landmark_id`;
- landmark description/type/azimuth;
- `edge_id`, `edge_heading`, and alignment error;
- `supports_edge`, `reason`, and evidence status.

### annotation_cases.jsonl

Each case should include fixed-view image paths, their absolute center headings,
outgoing edges, candidate landmarks, task type, and evidence status. Route-choice
cases must also record route bearing and whether views are fixed or route-aligned.
