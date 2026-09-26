# Landmarkness Schema

## Core definition

Landmarkness is the degree to which a visual or spatial cue functions as a
navigation-useful and cognition-useful anchor. Salience alone is not landmarkness.

## Candidate categories

- Object-level: tower, monument, bridge, station entrance, statue, distinctive
  building, shop sign.
- Structural: intersection, corner, road split, square, street-width change,
  street-wall turn, boulevard or alley entrance.
- Text/sign: road, shop, station, traffic, or building signs.
- Scene-level/atmospheric: tree-lined corridor, commercial street, residential
  facade rhythm, plaza edge, material pattern, openness, or urban texture.

## Landmarkness dimensions

- `salience`;
- `distinctiveness`;
- `describability`;
- `stability`;
- `orientation_value`;
- `action_relevance`;
- `memory_value`;
- `relational_value`;
- `scene_anchor_value`.

All scores require a named rater/source and evidence status. A visually prominent
temporary object may be salient but have weak functional landmarkness.

## Direction fields

For fixed Paris views, record:

```json
{
  "view_index": 1,
  "view_center_heading": 184.35,
  "heading_reference": "heading_from_api",
  "route_relative_direction": null,
  "azimuth_source": "fixed_view_center"
}
```

Do not write front/right/back/left unless a route or observer bearing is defined.
For route-aligned ERP crops, record that bearing and set
`route_relative_direction` explicitly.

## Candidate JSONL schema

```json
{
  "candidate_id": "lm_0001",
  "node_id": "pano_001",
  "description": "blue pharmacy sign on the right corner",
  "type": "sign",
  "view_index": 1,
  "view_center_heading": 184.35,
  "route_bearing": 95.0,
  "route_relative_direction": "right",
  "azimuth": 172.0,
  "elevation": 5.0,
  "bfov": {"theta": 172.0, "phi": 5.0, "fov_h": 25.0, "fov_v": 18.0},
  "azimuth_source": "refined_within_view_offset",
  "visibility": 0.88,
  "salience": 0.82,
  "distinctiveness": 0.80,
  "describability": 0.91,
  "stability": 0.65,
  "orientation_value": 0.84,
  "action_relevance": 0.79,
  "memory_value": 0.76,
  "relational_value": 0.70,
  "scene_anchor_value": 0.20,
  "supports_action": "right",
  "reason": "The sign is near the right outgoing street and is easy to describe.",
  "annotation_source": "human_rater_01",
  "evidence_status": "human_verified"
}
```

P1A candidate elicitation may use coarse fixed-view centers. Refined azimuth is optional.
Formal route-direction experiments should reproject ERP around the route bearing
instead of relabeling the nearest fixed view.
