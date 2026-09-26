# Panoramic Papers Transfer: APRS / EAGLE-360

## Position

APRS / PanoSeeker and EAGLE-360 are not the research framework to copy. They are method references for handling single-panorama visual evidence.

The user's main question is not:

> How can a model actively find a given object in a 360° panorama?

The user's main question is:

> Which street-view visual elements become navigation-useful landmarks, and how do they anchor a cognitive map for urban understanding and navigation?

## What APRS contributes as inspiration

APRS / PanoSeeker is useful because it shows:

- passive image understanding can be turned into panoramic evidence search;
- local FoV observations can be accumulated into a geometrically consistent 360° memory;
- explicit spatial memory is better than plain text logs for panoramic search;
- search efficiency, repeated viewing, and stopping decisions are meaningful evaluation dimensions.

Transferable idea:

> Use EgoSphere-like memory as a way to organize what has been seen in a street-view panorama, but only when it helps identify or validate navigation-useful landmarks.

## What EAGLE-360 contributes as inspiration

EAGLE-360 is useful because it shows:

- a panorama is not an ordinary long image;
- left and right ERP boundaries are adjacent in the real world;
- target location should often be represented in spherical coordinates;
- global-to-local inspection can first estimate rough direction and then refine local evidence;
- BFoV / GCD-like angular evaluation is more suitable than ordinary 2D boxes for panoramic targets.

Transferable idea:

> Represent landmark candidates with azimuth / elevation / field of view, and use angular alignment to connect landmarks to road-edge headings.


## First-stage image input decision

For the user's first pilot, do not feed the raw equirectangular panorama as the default model input.

Use four perspective crops with FOV=90° as the canonical representation:

```text
front / right / back / left
or
0° / 90° / 180° / 270°
```

Reason:

- the user's existing Paris street-view/navigation assets are already organized as four views per panorama;
- perspective crops reduce ERP distortion and are easier for current VLMs to parse;
- four headings are sufficient for initial landmarkness annotation, heading-level azimuth, and road-edge alignment;
- the full panorama should be retained as raw source or future extension for continuous angular localization, BFoV/GCD evaluation, and active evidence acquisition.

Therefore, APRS/EAGLE transfer should be implemented as **angular organization over four-view evidence first**, not as a full panorama active-search task.

## What not to borrow as the main goal

Do not make the project a direct street-view version of APRS or EAGLE.

Do not make these the main targets:

- referring segmentation;
- object localization for its own sake;
- SFT / GRPO training as the first requirement;
- active exploration as the title or central claim;
- model performance leaderboard.

## How to use them correctly

Use APRS/EAGLE as technical modules:

```text
single panorama / four-view street-view
→ organize visual evidence in angular coordinates
→ identify landmark candidates
→ estimate their landmarkness
→ align landmarks to road edges
→ build a landmark-anchored cognitive graph
```

Active inspection should be treated as an experimental condition or evidence acquisition cost, not the main scientific contribution.
