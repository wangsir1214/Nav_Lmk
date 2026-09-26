# Landmark-Anchored Cognitive Graph Schema

## Purpose

This schema operationalizes a cognitive map as a graph anchored by navigation-useful landmarks.

It connects:

- street-view nodes;
- visible landmarks;
- road edges;
- edge headings;
- scene clusters;
- route memory.

## Node schema

```json
{
  "node_id": "pano_001",
  "lat": 48.873,
  "lon": 2.295,
  "image_mode": "four_view_fov90",
  "image_paths": {
    "front": "...jpg",
    "right": "...jpg",
    "back": "...jpg",
    "left": "...jpg"
  },
  "full_panorama_path": null,
  "scene_cluster": "commercial_boulevard",
  "landmark_ids": ["lm_001", "lm_002"],
  "edge_ids": ["edge_001", "edge_002", "edge_003"]
}
```

## Landmark schema

```json
{
  "landmark_id": "lm_001",
  "node_id": "pano_001",
  "description": "red cafe sign on the right corner",
  "type": "sign",
  "azimuth": 72.0,
  "elevation": 4.0,
  "landmarkness_score": 0.83,
  "navigation_function": ["orientation", "edge_selection", "route_instruction"],
  "supports_edge_ids": ["edge_003"]
}
```

## Edge schema

```json
{
  "edge_id": "edge_003",
  "from_node": "pano_001",
  "to_node": "pano_002",
  "heading": 75.0,
  "road_id": "road_abc",
  "supported_by_landmarks": ["lm_001"],
  "alignment_error_deg": 3.0,
  "edge_confidence": 0.87
}
```

## Scene field schema

```json
{
  "scene_field_id": "sf_001",
  "type": "commercial_boulevard",
  "node_ids": ["pano_001", "pano_002", "pano_003"],
  "description": "continuous commercial street with dense signs and cafe terraces",
  "memory_value": 0.72,
  "route_context": "helps identify the boulevard segment"
}
```

## First prototype target

The first prototype does not need to build a complete graph for the whole city.

Start with:

- 20–100 street-view nodes;
- their outgoing road edges if available;
- 3–5 landmark candidates per node;
- simple landmark-to-edge alignment by angular difference.
