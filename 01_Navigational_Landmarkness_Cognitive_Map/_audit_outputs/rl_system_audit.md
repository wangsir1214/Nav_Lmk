# Historical UrbanNav system audit

## System flow

```text
current 84x84 RGB perspective view
+ 2-D goal coordinate
+ previous action/reward
-> RGB CNN (256-D feature in the DeepMind path)
-> goal GRU (256-D)
-> 64-D goal bottleneck
-> policy GRU (256-D)
-> categorical policy + value head + heading auxiliary head
-> rotate / move-forward environment action
-> distance-shaped reward and timeout/goal termination
```

This flow is verified from the extracted source copy. The exact checkpoint/config pairing and fixed-episode replay are not verified.

## What the policy can see

- Image pixels enter `RGBCNNOracle`; the policy is not blind by design.
- The goal path embeds a two-dimensional `observations['goal']`; the environment exposes `target_latlng`, so target coordinates are a policy shortcut risk for the current scientific question.
- Previous action and previous reward can be concatenated, depending on config.
- The policy has recurrent goal and policy state, but no landmark-anchored cognitive graph module.
- No direct pano ID or full topology tensor was found in the DeepMind policy forward path.

The environment uses the graph for movement, neighbor lookup, distance, shortest paths, goal sampling, and reward. That is environment-only topology, not evidence that the agent learned or consumed a cognitive map.

## Graph and action semantics

- The legacy game makes connections bidirectional and computes BFS-derived paths.
- Legacy movement searches candidate panos up to graph depth 3 within a bearing cone, so one `move_forward` action is not equivalent to traversing one canonical graph edge.
- The old environment therefore cannot establish loop or alternate-path cognitive-map behavior without substantial redesign.
- The action space is low-level rotation/move-forward combinations, not the current provisional left/right/forward route labels.

## Image orientation

- `pano_data.py` and `pano_graph.py` use `theta = yaw - heading`, consistent with the verified ERP convention when yaw is an absolute geographic bearing.
- `courier_game.py` contains a path-generation branch using `theta = heading - bearing`, the opposite sign and a likely horizontal mirror error.
- `observations.py` explicitly leaves a comment to verify the `yaw-heading` direction.
- `urbannav_vec.py` resets yaw to the current panorama heading; another legacy path initializes yaw to zero and does not provide equally clear reset evidence.
- Old policy inputs are 16 pre-generated FOV=60-degree, 84x84 views, not the current four FOV=90-degree, 640x640 views.

Orientation must be covered by a fixed-pano regression test before any checkpoint replay.

## Checkpoints and replay status

The ZIP contains 15 `.pt` files and generic save/load utilities, but there is no verified command that binds a particular checkpoint to its exact config, data paths, code branch, and fixed Paris episodes. The evaluation script can collect pano/action sequences, yet it creates random episodes and contains historical inline bug notes.

Classification: **historical baseline candidate**, not directly loadable experimental evidence.

## The reported 32 dimensions

No 32-D landmark representation was found. The number 32 appears primarily as CNN channel counts, map-channel settings, or coordinate-bin counts. The DeepMind visual feature and recurrent states are 256-D, and the explicit goal bottleneck is 64-D.

## Security finding

Historical code contains hard-coded service credentials in at least two source locations/entry paths. Values are intentionally omitted. Rotate/revoke them and replace literal credentials with environment-variable or secret-manager reads before running any code.

## Recommendation

Do not spend the first research phase repairing UrbanNav. Use the new graph/image/route audit for a human or simple retrieval/classification pilot. Revisit UrbanNav only after the task is fixed, then require:

1. deterministic fixed-episode replay;
2. exact checkpoint/config provenance;
3. route-aligned orientation regression tests;
4. exported action probabilities and pano/yaw trajectories;
5. coordinate and visual-ablation controls;
6. graph loops preserved if claiming cognitive-map behavior.
