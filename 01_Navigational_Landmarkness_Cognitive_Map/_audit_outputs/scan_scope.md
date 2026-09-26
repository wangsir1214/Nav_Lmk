# Paris audit scan scope

## Deep scan

- `Z:\wangyq\GSV_Paris`: four-view images, ERP panoramas, legacy 16-view images, DINOv2 assets.
- `Z:\wangyq\Street_view_and_points_Paris`: graph, heading metadata, pano-to-road mapping, OSM edges, POI seeds.
- `Z:\wangyq\CityBench\CityBench-main\citybench\outdoor_navigation`: legacy trajectories, route-facing images, generation scripts, prior outputs.
- `Z:\wangyq\CityBench\CityBench-main\citydata\outdoor_navigation_tasks`: Paris task, instruction, and matched-image files.
- `C:\Users\Admin\Desktop\UrbanNav_neo_fromPC.zip`: source/config/log/checkpoint inventory without bulk checkpoint extraction.
- `D:\BaidudiskDownload\GSV_tiles_download_graph.ipynb`: graph-construction cells and persisted execution state.

## Shallow inspection only

- `BSV`, `CityLandmarks`, `GSV_landmarks`, `Landmarks_exp`, `building_data`, and `model_weights` were classified at one directory level.
- They were not used in the canonical Paris join because they are another imagery source, archived/UrbanHue-related work, a non-Paris branch, legacy experiments, or unnecessary large assets.

## Explicitly skipped

- `docker_images_tar`, `extensions`, `wyq_envs`, caches, virtual environments, segmentation masks, and unrelated CityBench tasks.
- No VLM call, RL training, checkpoint inference, image editing, or source-data mutation was performed.

This selective scope is part of the audit provenance. A future scan should expand only when a specific missing field or experiment requires it.
