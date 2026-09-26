# Image Input Policy

## Decision

For the audit and candidate-discovery stage, the canonical image input is four
fixed FOV=90-degree perspective views per panorama:

```text
view_0 / view_1 / view_2 / view_3
```

The full equirectangular panorama should be retained as the raw source. The fixed
views are not route-relative `front/right/back/left` views. A formal route-choice
or direction-selection experiment must reproject the ERP around the route bearing
after the human task and action have been frozen.

## Why four views first

### 1. Existing asset compatibility

The Paris assets contain four 640x640 FOV=90-degree images for every graph pano.
This allows reuse of metadata, embeddings, route cases, and review tooling.

### 2. Reduced ERP distortion

Perspective crops are easier for humans and current vision models to interpret
than a raw ERP, especially near the poles and horizontal seam.

### 3. Sufficient first-stage evidence

The first question is which cues are navigation-useful and cognition-useful, not
continuous spherical localization. Four views provide complete coarse angular
coverage for candidate discovery and initial review. They are not sufficient as
the final directional input when the task requires a precise route-relative
action.

## Verified heading contract

The Paris pixel audit verifies the following relation, where `H` is
`heading_from_api`:

```text
center(view_i) = (H + 90 degrees * i) mod 360
```

Therefore, the fixed images are not permanently named front/right/back/left.
Those labels are valid only after a route or observer bearing is defined.

For exact route-aligned views:

```text
local_forward = (route_bearing - H) mod 360
front/right/back/left = local_forward + [0, 90, 180, 270] degrees
```

Reproject the ERP at these local angles. Choosing the nearest fixed view is useful
for review boards, but can leave up to 45 degrees of residual direction error and
should not be the formal direction-experiment input.

## Azimuth representation

The coarse fixed-view record should contain:

```text
view_index = 0 / 1 / 2 / 3
view_center_heading = (heading_from_api + 90 * view_index) mod 360
```

When an object location within a view is available:

```text
horizontal_offset_ratio in [-0.5, 0.5]
local_offset_deg = horizontal_offset_ratio * 90 degrees
landmark_azimuth = view_center_heading + local_offset_deg
```

When route-aligned views are generated, also record
`route_relative_direction = front/right/back/left` and the route bearing used.

## Role of full panorama

Use the ERP later for:

- exact route-aligned reprojection;
- continuous azimuth/elevation localization;
- objects crossing fixed-view boundaries;
- BFoV/GCD evaluation;
- active evidence acquisition or panoramic memory.

## Recommended observation conditions

1. single current view;
2. fixed four-view panel with absolute center headings;
3. landmark-only representation;
4. route-aligned four views plus road-edge headings;
5. optional full panorama as a later ablation.

Do not start with full active panoramic search.
