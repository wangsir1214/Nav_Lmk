# 本次实际发送给 Qwen 的请求

审查版本：20260928T070320Z。来源 run_id：paris_route_qwen_smoke_20260927T141218Z_a01；导出 commit：253d27b047d7e421e35be56245f6d7017622c3db。以下内容从 NAS 的原始 metadata 提取；不是新实验指令。

文件路径是供人工追溯的记录字段。runner 读取图片后，只向模型提供图像、序号标签和提示词；不会将这些文件路径作为文本输入。每次调用建立新的 user message，不继承上一 case 的对话。

## stage1/candidate_raw/main_03_dec.attempt01.metadata.json

模型 revision：c202236235762e1c871ad0ccb60c8ee5ba337b9a

原始 metadata SHA-256：c155c277a3f8fefb8ba81b1b34946275f7ef41299cd531b3640c2bc9fed3983b

### 实际提示词（原文）

Review this original 640x640 street-view image. Return at most three clearly visible place or wayfinding cues using only image pixels. Describe observations, not a route choice. Respond with exactly one JSON object with only root key candidates. Every candidate has exactly these seven keys: candidate_id, bbox_xyxy_1000, type, description, hypothesized_role, visibility, uncertainty. IMPORTANT: express each bbox in a 0 to 1000 normalized coordinate frame, NOT 640 pixel coordinates; x=0 is the left image edge, x=1000 the right edge, y=0 the top edge, y=1000 the bottom edge. bbox_xyxy_1000 is [x1,y1,x2,y2] with finite values and 0<=x1<x2<=1000, 0<=y1<y2<=1000. The server will deterministically convert to pixel coordinates using the actual image size; do not output bbox_xyxy_640. candidate_id is a unique integer or short string. type is object, structural, text, or scene. visibility is clear, partial, occluded, or uncertain. uncertainty is a NUMBER from 0 to 1. Do not add view_index inside a candidate. If two signs might identify one storefront, describe each visible instance but do not claim they are separate landmarks. FORMAT TEMPLATE only, replace values with image-grounded answers: {"candidates":[{"candidate_id":1,"bbox_xyxy_1000":[100,100,300,300],"type":"object","description":"visible cue","hypothesized_role":"possible navigation cue","visibility":"clear","uncertainty":0.5}]} If nothing clear is visible, respond exactly {"candidates":[]}. No markdown, no explanation, no extra keys.

### 按顺序读取的图像（路径不会作为文字发送给模型）

- observed image: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/qxTdXHFI9twUe3Dy0bx9jA_panorama_0.jpg

## route_raw/main_03.route_plus_current.attempt01.metadata.json

模型 revision：c202236235762e1c871ad0ccb60c8ee5ba337b9a

原始 metadata SHA-256：a0f5d096bd1347b080e013adf6b97df34b34b4a159acaa453e9430911ebc2886

### 实际提示词（原文）

You are at a street intersection. Select one of the two LEGAL non-return exits listed below. IDs are anonymous. Use only the supplied images; do not guess place names or coordinates. If evidence is insufficient, set uncertain=true and make a tentative selection. Option A: path roughly straight relative to the approach. Option B: path left relative to the approach. The earlier route images are in observed travel order. Use them as visual memory together with the current four-view observation. Return exactly one JSON object with only chosen_edge_id, maneuver, evidence_view_id, evidence_candidates, reason, uncertain. chosen_edge_id must be A or B; maneuver must be left, right, forward, or unknown; evidence_view_id must be view_0..view_3 or empty string; evidence_candidates must be []; reason must describe visible evidence only; uncertain must be a JSON boolean. Example FORMAT only: {"chosen_edge_id":"A","maneuver":"unknown","evidence_view_id":"view_0","evidence_candidates":[],"reason":"visual evidence is limited","uncertain":true}. Replace values. No markdown or other text.

### 按顺序读取的图像（路径不会作为文字发送给模型）

- route memory image 1: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/uJqWESwRAW0B56iNLrmt6Q_panorama_0.jpg

- route memory image 2: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/yObsZtN-5fteyPmAWYW7TQ_panorama_0.jpg

- route memory image 3: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/1gAAqYoZDnC1rGhFh5pt6Q_panorama_0.jpg

- route memory image 4: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/cMDG1a1heD-VRW30JoofEw_panorama_0.jpg

- route memory image 5: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/2_yyvlJe9paF57ld3jbtgw_panorama_0.jpg

- current view_0: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/qxTdXHFI9twUe3Dy0bx9jA_panorama_0.jpg

- current view_1: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/qxTdXHFI9twUe3Dy0bx9jA_panorama_1.jpg

- current view_2: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/qxTdXHFI9twUe3Dy0bx9jA_panorama_2.jpg

- current view_3: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/qxTdXHFI9twUe3Dy0bx9jA_panorama_3.jpg

## route_raw/main_03.current_only.attempt01.metadata.json

模型 revision：c202236235762e1c871ad0ccb60c8ee5ba337b9a

原始 metadata SHA-256：a3990f3ee321a9f0fbc08c744f1f51f8a7b188ed98bb5260d9c11867baf68a7a

### 实际提示词（原文）

You are at a street intersection. Select one of the two LEGAL non-return exits listed below. IDs are anonymous. Use only the supplied images; do not guess place names or coordinates. If evidence is insufficient, set uncertain=true and make a tentative selection. Option A: path roughly straight relative to the approach. Option B: path left relative to the approach. Only the current four-view observation is available. Return exactly one JSON object with only chosen_edge_id, maneuver, evidence_view_id, evidence_candidates, reason, uncertain. chosen_edge_id must be A or B; maneuver must be left, right, forward, or unknown; evidence_view_id must be view_0..view_3 or empty string; evidence_candidates must be []; reason must describe visible evidence only; uncertain must be a JSON boolean. Example FORMAT only: {"chosen_edge_id":"A","maneuver":"unknown","evidence_view_id":"view_0","evidence_candidates":[],"reason":"visual evidence is limited","uncertain":true}. Replace values. No markdown or other text.

### 按顺序读取的图像（路径不会作为文字发送给模型）

- current view_0: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/qxTdXHFI9twUe3Dy0bx9jA_panorama_0.jpg

- current view_1: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/qxTdXHFI9twUe3Dy0bx9jA_panorama_1.jpg

- current view_2: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/qxTdXHFI9twUe3Dy0bx9jA_panorama_2.jpg

- current view_3: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/qxTdXHFI9twUe3Dy0bx9jA_panorama_3.jpg

## route_raw/main_03.route_shuffled.attempt01.metadata.json

模型 revision：c202236235762e1c871ad0ccb60c8ee5ba337b9a

原始 metadata SHA-256：e718b3b499eff040ed269959ad84f3084a089e4dfcebada74796f7286ea21684

### 实际提示词（原文）

You are at a street intersection. Select one of the two LEGAL non-return exits listed below. IDs are anonymous. Use only the supplied images; do not guess place names or coordinates. If evidence is insufficient, set uncertain=true and make a tentative selection. Option A: path roughly straight relative to the approach. Option B: path left relative to the approach. The earlier route images are shown out of travel order. Compare them with the current four-view observation. Return exactly one JSON object with only chosen_edge_id, maneuver, evidence_view_id, evidence_candidates, reason, uncertain. chosen_edge_id must be A or B; maneuver must be left, right, forward, or unknown; evidence_view_id must be view_0..view_3 or empty string; evidence_candidates must be []; reason must describe visible evidence only; uncertain must be a JSON boolean. Example FORMAT only: {"chosen_edge_id":"A","maneuver":"unknown","evidence_view_id":"view_0","evidence_candidates":[],"reason":"visual evidence is limited","uncertain":true}. Replace values. No markdown or other text.

### 按顺序读取的图像（路径不会作为文字发送给模型）

- route memory image 1: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/2_yyvlJe9paF57ld3jbtgw_panorama_0.jpg

- route memory image 2: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/yObsZtN-5fteyPmAWYW7TQ_panorama_0.jpg

- route memory image 3: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/uJqWESwRAW0B56iNLrmt6Q_panorama_0.jpg

- route memory image 4: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/cMDG1a1heD-VRW30JoofEw_panorama_0.jpg

- route memory image 5: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/1gAAqYoZDnC1rGhFh5pt6Q_panorama_0.jpg

- current view_0: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/qxTdXHFI9twUe3Dy0bx9jA_panorama_0.jpg

- current view_1: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/qxTdXHFI9twUe3Dy0bx9jA_panorama_1.jpg

- current view_2: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/qxTdXHFI9twUe3Dy0bx9jA_panorama_2.jpg

- current view_3: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/qxTdXHFI9twUe3Dy0bx9jA_panorama_3.jpg

## route_raw/main_06.route_plus_current.attempt01.metadata.json

模型 revision：c202236235762e1c871ad0ccb60c8ee5ba337b9a

原始 metadata SHA-256：8025c49120f5b9118e3d698280b09b1726bdaa1cd0b776054eca2701f710df6e

### 实际提示词（原文）

You are at a street intersection. Select one of the two LEGAL non-return exits listed below. IDs are anonymous. Use only the supplied images; do not guess place names or coordinates. If evidence is insufficient, set uncertain=true and make a tentative selection. Option A: path right relative to the approach. Option B: path roughly straight relative to the approach. The earlier route images are in observed travel order. Use them as visual memory together with the current four-view observation. Return exactly one JSON object with only chosen_edge_id, maneuver, evidence_view_id, evidence_candidates, reason, uncertain. chosen_edge_id must be A or B; maneuver must be left, right, forward, or unknown; evidence_view_id must be view_0..view_3 or empty string; evidence_candidates must be []; reason must describe visible evidence only; uncertain must be a JSON boolean. Example FORMAT only: {"chosen_edge_id":"A","maneuver":"unknown","evidence_view_id":"view_0","evidence_candidates":[],"reason":"visual evidence is limited","uncertain":true}. Replace values. No markdown or other text.

### 按顺序读取的图像（路径不会作为文字发送给模型）

- route memory image 1: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/oSa1tj_9Mt2_IXZ4K9fCeg_panorama_1.jpg

- route memory image 2: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/xt9pCqCZvulRwxZtecg1-g_panorama_1.jpg

- route memory image 3: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/G970Bulz6Nmd8_SOvRE0jg_panorama_1.jpg

- route memory image 4: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/Q5Bl2t-iHmndJ6I1Dh13gw_panorama_1.jpg

- route memory image 5: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/5M5peQFcX-RBZ1rw4UAKOw_panorama_1.jpg

- current view_0: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/uyE0Z2Ph9ad4xz0EENt8XQ_panorama_0.jpg

- current view_1: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/uyE0Z2Ph9ad4xz0EENt8XQ_panorama_1.jpg

- current view_2: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/uyE0Z2Ph9ad4xz0EENt8XQ_panorama_2.jpg

- current view_3: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/uyE0Z2Ph9ad4xz0EENt8XQ_panorama_3.jpg

## route_raw/main_06.current_only.attempt01.metadata.json

模型 revision：c202236235762e1c871ad0ccb60c8ee5ba337b9a

原始 metadata SHA-256：6203d8f58b863ba2df193483a8b896e33f149e365659ee42bb03b488d3d622b3

### 实际提示词（原文）

You are at a street intersection. Select one of the two LEGAL non-return exits listed below. IDs are anonymous. Use only the supplied images; do not guess place names or coordinates. If evidence is insufficient, set uncertain=true and make a tentative selection. Option A: path right relative to the approach. Option B: path roughly straight relative to the approach. Only the current four-view observation is available. Return exactly one JSON object with only chosen_edge_id, maneuver, evidence_view_id, evidence_candidates, reason, uncertain. chosen_edge_id must be A or B; maneuver must be left, right, forward, or unknown; evidence_view_id must be view_0..view_3 or empty string; evidence_candidates must be []; reason must describe visible evidence only; uncertain must be a JSON boolean. Example FORMAT only: {"chosen_edge_id":"A","maneuver":"unknown","evidence_view_id":"view_0","evidence_candidates":[],"reason":"visual evidence is limited","uncertain":true}. Replace values. No markdown or other text.

### 按顺序读取的图像（路径不会作为文字发送给模型）

- current view_0: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/uyE0Z2Ph9ad4xz0EENt8XQ_panorama_0.jpg

- current view_1: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/uyE0Z2Ph9ad4xz0EENt8XQ_panorama_1.jpg

- current view_2: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/uyE0Z2Ph9ad4xz0EENt8XQ_panorama_2.jpg

- current view_3: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/uyE0Z2Ph9ad4xz0EENt8XQ_panorama_3.jpg

## route_raw/main_06.route_shuffled.attempt01.metadata.json

模型 revision：c202236235762e1c871ad0ccb60c8ee5ba337b9a

原始 metadata SHA-256：ffcd6d79e9889273635a2f7ecbfd9fed55fb14867d4f8308053131766b4e062a

### 实际提示词（原文）

You are at a street intersection. Select one of the two LEGAL non-return exits listed below. IDs are anonymous. Use only the supplied images; do not guess place names or coordinates. If evidence is insufficient, set uncertain=true and make a tentative selection. Option A: path right relative to the approach. Option B: path roughly straight relative to the approach. The earlier route images are shown out of travel order. Compare them with the current four-view observation. Return exactly one JSON object with only chosen_edge_id, maneuver, evidence_view_id, evidence_candidates, reason, uncertain. chosen_edge_id must be A or B; maneuver must be left, right, forward, or unknown; evidence_view_id must be view_0..view_3 or empty string; evidence_candidates must be []; reason must describe visible evidence only; uncertain must be a JSON boolean. Example FORMAT only: {"chosen_edge_id":"A","maneuver":"unknown","evidence_view_id":"view_0","evidence_candidates":[],"reason":"visual evidence is limited","uncertain":true}. Replace values. No markdown or other text.

### 按顺序读取的图像（路径不会作为文字发送给模型）

- route memory image 1: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/5M5peQFcX-RBZ1rw4UAKOw_panorama_1.jpg

- route memory image 2: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/xt9pCqCZvulRwxZtecg1-g_panorama_1.jpg

- route memory image 3: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/oSa1tj_9Mt2_IXZ4K9fCeg_panorama_1.jpg

- route memory image 4: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/Q5Bl2t-iHmndJ6I1Dh13gw_panorama_1.jpg

- route memory image 5: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/G970Bulz6Nmd8_SOvRE0jg_panorama_1.jpg

- current view_0: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/uyE0Z2Ph9ad4xz0EENt8XQ_panorama_0.jpg

- current view_1: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/uyE0Z2Ph9ad4xz0EENt8XQ_panorama_1.jpg

- current view_2: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/uyE0Z2Ph9ad4xz0EENt8XQ_panorama_2.jpg

- current view_3: /home/nas/wangyq/GSV_Paris/0-All_GSV_3059_4per/uyE0Z2Ph9ad4xz0EENt8XQ_panorama_3.jpg
