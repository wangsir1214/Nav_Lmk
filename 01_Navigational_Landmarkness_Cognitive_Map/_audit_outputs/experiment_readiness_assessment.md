# Experiment readiness assessment

## Current decision

**Provisional ADAPT.** Retain Paris and adapt the first pilot to a stratified,
human-reviewed route-memory/continuation landmarkness feasibility set. Paris is no longer a
candidate for immediate replacement, but the evidence does not yet justify a
full GO for identity-location interventions or RL evaluation.

## Verified evidence

- 3,058 graph nodes and 3,310 edges, one component, cycle rank 253.
- Graph-node coverage is 100% for four-view images, ERP, heading, and DINO IDs.
- Fixed-view direction is verified as
  `center(view_i) = heading_from_api + 90*i (mod 360)`.
- 211 structurally valid route candidates were mined after connector, one-way,
  route-length, U-turn, and decision-zone filtering.
- Selected set: 12 main routes balanced 4/4/4 left/right/forward and three Arc
  controls balanced 1/1/1.
- All 120 selected panos join to 480 fixed views and 120 heading records; all 30
  route/decision review boards exist.
- Every selected decision zone has at least two legal departures; main routes are
  at least 452.16 m from the Arc reference and controls are at most 177.14 m away.

## Provisional visual evidence

Contact-sheet screening identifies strong structural, object-identity, and
scene-level cases, plus useful low-landmark and super-landmark controls. It also
identifies construction, glare/distant-Arc, and weak-intervention confounds.

This screening is not a substitute for the user's and teacher's six-dimension
human review. It is recorded separately in
`candidate_route_review_preliminary.csv`.

## Task readiness

| Task | Current judgment |
|---|---|
| Unconditioned route choice | Not scientifically defined: an unfamiliar junction has no unique correct road |
| Place recognition | Structurally supported; requires stratified similar-place sampling |
| Learned-route continuation | P1B protocol designed; pending human route/action gate and route-aligned views |
| Online exploration | Graph has loops, but one-way and connector-clique semantics need a new environment |
| Historical RL reuse | Not ready; orientation, checkpoint provenance, coordinate shortcuts, and graph-tree behavior remain |

## Remaining GO gate

1. User/teacher score all 15 cases on the expanded suitability and task-fit fields.
2. Confirm provisional maneuvers and decision-zone semantics.
3. Remove or isolate construction, Arc dominance, glare, and unstable storefronts.
4. Reproject route-aligned FOV=90-degree views from ERP.
5. Apply the P1A/P1B Go Gate and freeze the case split before VLM use or image intervention.
