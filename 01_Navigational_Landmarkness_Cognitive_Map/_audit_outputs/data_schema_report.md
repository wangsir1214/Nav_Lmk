# Paris data structure and join report

## Canonical key

`pano_id/panoid` joins graph nodes, coordinates, four fixed views, ERP, API
heading, and DINOv2 embeddings. The graph's 3,058 panos have 100% coverage in
all four assets; one additional complete pano exists outside the graph.

## Fixed-view direction

```text
center(view_i) = (heading_from_api + 90 degrees * i) mod 360
```

The four stored images must use `view_0..view_3` fields. Front/right/back/left
are route-relative derived fields only.

## Coverage

| Join | Coverage |
|---|---:|
| graph node -> four fixed views | 3,058 / 3,058 |
| graph node -> ERP | 3,058 / 3,058 |
| graph node -> heading | 3,058 / 3,058 |
| graph node -> DINO ID | 3,058 / 3,058 |
| selected route pano -> four fixed views | 120 / 120 (480 files) |
| selected route pano -> heading | 120 / 120 |
| selected route -> sequence and decision board | 15 / 15 each |

## Legacy route schema

`trajectory.csv` is a UTF-8, headerless, variable-width file containing image
view/action tokens. Its actions use legacy environment semantics, including
depth-3 forward movement. The ten routes are historical examples rather than the
canonical route table for this project.

## Current candidate schema

- `candidate_routes.json`: selected main routes and Arc controls plus method and
  counts;
- `candidate_route_pool.json`: all 211 structurally valid candidates;
- `candidate_route_steps.csv`: 120 step records with heading and provisional
  maneuver;
- `candidate_route_review.csv`: blank six-dimension human review form;
- `candidate_route_review_preliminary.csv`: Codex contact-sheet pre-screening;
- `candidate_route_validation.json`: strict JSON, count, separation, image,
  heading, and board checks.

## Evidence boundary

Coordinates and graph/OSM rules support provisional action derivation. They do
not provide human-verified landmark labels, edit provenance, or gold actions.
Those fields remain intentionally absent until the human decision gate.
