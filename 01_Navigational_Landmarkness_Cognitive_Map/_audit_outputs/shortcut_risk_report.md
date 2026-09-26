# Shortcut and validity risk report

| Risk | Current evidence | Required control |
|---|---|---|
| Goal-coordinate shortcut | Historical policy embeds a 2-D goal and environment exposes target coordinates | Coordinate ablation or goal representation redesign |
| Visual dependence unknown | Images enter the CNN, but no ablation proves action dependence | Blank/shuffle/view-order tests only after baseline replay |
| Environment graph mistaken for cognitive map | Graph is used for movement, BFS, distance, goal sampling, and reward; no graph tensor is in the policy path | Distinguish environment-only topology from policy-visible memory |
| Loop removal/tree behavior | Legacy game makes graph bidirectional and uses BFS-derived structures | Preserve loops and alternate paths in any cognitive-map environment |
| Legacy multi-hop action | `move_forward` can search to depth 3 | Use canonical one-edge transitions or record transition hops |
| Historical action leakage | Qwen route-description prompt included the supplied action | Never use those descriptions as independent prediction evidence |
| Fixed view mislabeled as front | Fixed view centers follow pano heading, not route bearing | Use `view_0..3`; reproject route-aligned views from ERP |
| Opposite orientation signs | Main image path uses `yaw-heading`; one legacy branch uses `heading-bearing` | Fixed-pano pixel regression test before replay |
| Arc de Triomphe dominance | Near-Arc cases visually dominate orientation | Keep a separate super-landmark control stratum |
| Temporary cue shortcut | Construction/scaffolding appears in several candidate scenes | Exclude, stratify, or explicitly label temporary cues |
| Route/case memorization | Old ten routes are tiny and disjoint | Geographic and decision-zone-disjoint train/test split |
| Pano or filename leakage | IDs exist in data/backend; no direct policy ID input found | Prevent model/prompts from receiving IDs and test shuffled filenames |

## Credential risk

Historical source contains hard-coded service credentials. Values are intentionally
omitted. Revoke/rotate them before any execution and replace literals with secure
runtime configuration.

## Evidence boundary

The new route maneuvers are coordinate-derived and structurally checked, but remain
provisional until human confirmation. The preliminary visual statuses are not
labels for model training or scientific claims.
