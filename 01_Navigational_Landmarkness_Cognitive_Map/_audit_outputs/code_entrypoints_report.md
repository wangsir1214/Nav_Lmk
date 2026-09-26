# Code entrypoints report

## Current audit utilities

### Candidate mining

```powershell
& "C:\Users\Admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" `
  "_audit_work\mine_candidate_routes.py" `
  --graph "Z:\wangyq\Street_view_and_points_Paris\Line_After_heading_clear_Paris_center_street_from0309_4_v1\kl.Line_Points_3.json" `
  --point-road-dbf "Z:\wangyq\Street_view_and_points_Paris\Line_After_heading_clear_Paris_center_street_from0309_4_v1\Line_Points_3_to_road.dbf" `
  --road-dbf "Z:\wangyq\Street_view_and_points_Paris\road\edges.dbf" `
  --heading-csv "Z:\wangyq\Street_view_and_points_Paris\GoogleAPIMETADAT\Paris_Points_heading_3059\Paris_Points_heading_3059.csv" `
  --image-dir "Z:\wangyq\GSV_Paris\0-All_GSV_3059_4per" `
  --connector-audit "_audit_outputs\graph_connector_audit.json" `
  --output-dir "_audit_outputs"
```

Run from `F:\Codex_local\Nav_Lmk\01_Navigational_Landmarkness_Cognitive_Map`.

### Candidate validation

```powershell
& "C:\Users\Admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" `
  "_audit_work\validate_candidate_routes.py" `
  --output-dir "_audit_outputs" `
  --image-dir "Z:\wangyq\GSV_Paris\0-All_GSV_3059_4per" `
  --heading-csv "Z:\wangyq\Street_view_and_points_Paris\GoogleAPIMETADAT\Paris_Points_heading_3059\Paris_Points_heading_3059.csv"
```

Output: `_audit_outputs/candidate_route_validation.json`.

### Heading audit

`_audit_work/audit_view_heading_alignment.py` compares ERP reprojections against
the stored four views under eight orientation hypotheses. Its report and
diagnostic are in `_audit_outputs/heading_orientation_report.md` and
`_audit_outputs/figures/view_heading_alignment_diagnostic.jpg`.

## Graph notebook

`D:\BaidudiskDownload\GSV_tiles_download_graph.ipynb` is an algorithm-template
notebook. Its executed cells show ERP tile stitching and the weighted-within-road
plus null-weight-intersection-connector graph logic. Persisted outputs are
Manhattan-specific, so it is not direct run provenance for the Paris JSON.

## CityBench

- `data_gen.py` and `eval.py` are the general outdoor-navigation generation and
  evaluation scripts.
- `toyscript_from_csv.py` consumes the manually authored `trajectory.csv` and
  generated the historical route descriptions.
- The ten `trajectory_0..9` routes are separate from the incomplete
  `citydata/outdoor_navigation_tasks` Paris state and are not current gold data.

No CityBench script is the canonical entrypoint for the new full-graph candidate
routes. The new audit scripts deliberately operate on graph/OSM/image metadata.

## Historical UrbanNav

Likely training/evaluation entry: `experiments_deepmind_real.py`; generic
checkpoint helpers are in `ppo/ppo_trainer.py`. The evaluation function can log
pano and action sequences, but samples random episodes and is not a verified
fixed-route checkpoint replay command.

The ZIP contains 15 `.pt` files, but checkpoint/config/data/code compatibility is
not established. Do not run this entrypoint until hard-coded service credentials
are revoked and replaced with secure configuration.
