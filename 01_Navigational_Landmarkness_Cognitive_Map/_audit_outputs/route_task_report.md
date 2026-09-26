# Paris candidate route and action report

## Decision

The historical `trajectory_0` to `trajectory_9` routes are retained as **historical description-generation examples**, not gold routes for the current study. They cover only 67 unique panos (2.19% of the graph), contain legacy depth-3 movement semantics, and include at least one action/transition alignment concern.

The current audit instead mines the full graph and produces a **provisional, human-reviewable route-choice pool**. Structural validity is verified; scientific suitability and landmark labels remain provisional.

## Mining contract

Candidate routes are generated from graph connector edges after excluding four invalid connectors and one invalid weighted edge. Each route contains three same-segment weighted steps before a connector, the connector transition, and three same-segment weighted steps after it, for eight panos total.

Filters require:

- connector length at most 25 m and route length 35-220 m;
- no U-turn geometry;
- OSM one-way-compatible incoming and outgoing traversal;
- at least two legally traversable departure segments at the shared OSM endpoint;
- non-overlapping selected routes, unique OSM decision endpoints, and at least 120 m between selected decision points;
- main cases at least 450 m from the Arc de Triomphe reference point;
- separate Arc controls within 220 m.

The full pool has 211 raw candidates, including 72 main-pool candidates and 63 Arc-control-pool candidates. The selected review set has 12 main routes balanced as 4 left, 4 right, and 4 forward, plus three Arc controls balanced 1/1/1.

## Action semantics

Bearings are absolute geographic bearings, clockwise from north. For an incoming bearing `B_in` and outgoing bearing `B_out`:

```text
turn = wrap_to_[-180, 180](B_out - B_in)
positive turn -> right
negative turn -> left
small magnitude -> forward
```

These actions do not depend on the panorama heading. Heading is needed only to select or reproject the image view that faces a route bearing.

The generated labels are named `provisional_maneuver`, not `gold_action`. The formal experiment must freeze action thresholds and obtain human/teacher confirmation of connector semantics before treating them as gold.

## Why node degree is insufficient

The graph-construction notebook connects endpoint-nearest panos from adjacent OSM road segments as a clique. A real intersection can therefore span several panos, while an individual decision pano can have degree 2 even when the shared OSM endpoint has three or more road segments.

For route selection, use both:

- `decision_node_degree`: direct graph degree of the incoming pano;
- `decision_zone_segment_count` and `legal_departure_segment_count`: road-level complexity at the shared OSM endpoint.

`main_04` demonstrates the distinction: direct node degree is 2, but its decision zone contains three segments and three legal departures.

## Selected main routes

| Route | Action | Turn | Arc distance | Node degree | Zone segments | Legal departures | Preliminary review |
|---|---:|---:|---:|---:|---:|---:|---|
| main_01 | left | -91.4 deg | 632 m | 4 | 4 | 4 | KEEP: strong structural case |
| main_02 | left | -94.0 deg | 611 m | 3 | 3 | 2 | ADAPT: construction confound |
| main_03 | left | -90.0 deg | 640 m | 3 | 3 | 3 | KEEP: clear conventional intersection |
| main_04 | left | -90.7 deg | 453 m | 2 | 3 | 3 | ADAPT: low-landmark control |
| main_05 | right | +89.2 deg | 452 m | 4 | 4 | 3 | KEEP: object/structural corner |
| main_06 | right | +68.1 deg | 493 m | 3 | 3 | 3 | KEEP: strong scene anchor |
| main_07 | right | +73.4 deg | 473 m | 3 | 3 | 2 | ADAPT: low-salience contrast |
| main_08 | right | +116.3 deg | 577 m | 4 | 4 | 4 | KEEP: strong boulevard decision context |
| main_09 | forward | -4.5 deg | 712 m | 4 | 4 | 4 | ADAPT: construction confound |
| main_10 | forward | +0.8 deg | 487 m | 3 | 3 | 3 | ADAPT: possible distant Arc/glare |
| main_11 | forward | +1.6 deg | 588 m | 3 | 3 | 2 | KEEP: scene-boundary cue |
| main_12 | forward | +4.5 deg | 537 m | 3 | 3 | 3 | KEEP: storefront identity candidate |

The preliminary statuses are Codex contact-sheet screening, not final human scores. The blank six-dimension form remains in `candidate_route_review.csv`; the separate `candidate_route_review_preliminary.csv` preserves machine-assisted pre-review without overwriting teacher judgments.

## View-direction contract

Pixel audit verifies:

```text
center(view_i) = (heading_from_api + 90 deg * i) mod 360
```

The fixed views are therefore `view_0..view_3`, not permanent front/right/back/left views. Sequence sheets show the nearest fixed view and its angular residual; the worst theoretical residual is 45 degrees.

For formal direction-choice experiments, reproject the ERP around each route bearing:

```text
local_forward = (route_bearing - heading_from_api) mod 360
front/right/back/left = local_forward + [0, 90, 180, 270] deg
```

## Task correctness contract

The mined route does not make its outgoing edge behaviorally correct by itself.
If a participant sees an unfamiliar intersection without a learned route, target,
map, or instruction, multiple outgoing roads can all be valid. The first behavior
task is therefore frozen as route continuation / route-memory choice:

1. the participant studies an eight-pano route;
2. the test presents the incoming sequence and decision zone;
3. the participant selects which legal outgoing edge continues the learned route.

Only under this task does the learned route define the correct choice. The
geometric label remains a `provisional_maneuver` until the decision zone and
outgoing edge are human-confirmed.

## Current task judgment

Paris now has verified structural support for a small route-memory/continuation
feasibility pilot, and the selected cases span structural, object-identity,
scene-level, low-landmark, and super-landmark conditions. This supports a
provisional **ADAPT** decision: retain Paris, but stratify the first pilot and
remove or isolate temporary construction, Arc dominance, and weak-intervention
cases.

It is not yet a final GO for the identity-location intervention experiment.
Remaining gates are expanded human task-fit scoring, action/decision-zone
confirmation, temporal-stability review, and route-aligned ERP reprojection.
