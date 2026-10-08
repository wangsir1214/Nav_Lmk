# Route-replay two-question sanity

Run: `paris_route_replay_sanity_20261008T080158Z_a01`
Status: **SUCCESS**
Source commit: `9d46f5d7a069be873ce30f13c4647f1d235a18aa`
Model revision: `c202236235762e1c871ad0ccb60c8ee5ba337b9a`

| question | gold | Full | NoDemo | NoCurrent |
|---|---|---|---|---|
| q_main02_decision_step3 | LEFT | FORWARD | FORWARD | UNSURE |
| q_main06_decision_step3 | RIGHT | FORWARD | FORWARD | UNSURE |

Main requests: 6; format retries: 0; format failures: 0.

This is a two-question task/interface sanity check. One accepted decision point per route and no within-demonstration action diversity mean NoCurrent correctness could reflect route-level shortcuts. NoDemo and NoCurrent diagnose missing information; neither measures complete navigation. No landmark functional value, cognitive-map property, or general navigation accuracy is inferred.
