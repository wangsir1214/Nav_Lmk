# Qwen coordinate audit — diagnostic only

The two 640×640 source views support the same interpretation of the old model numbers: a 0–1000 coordinate frame. In main_03_dec, raw values below 640 nevertheless place both visible ZARA HOME signs on the roadway when interpreted as 640 pixels; multiplying by 0.64 places them on the two storefront signs. In main_06_dec, the no-entry sign at raw [776,480,800,504] is off-image under 640 interpretation and over the visible sign after 0.64 scaling.

This is evidence for a shared coordinate convention, not evidence that every candidate box is correct. The white circular sign in main_03_dec is missed by both interpretations, and the white rectangular sign claims in main_06_dec are vertically misplaced. main_03_dec candidates 1 and 2 are two visible signs for the same storefront identity. main_06_dec attempt02 candidates 2 and 3 are exact duplicate boxes and descriptions. All require human review.

The old raw replies, parsed result, overlay, BLOCKED status and GitHub snapshot remain unchanged. A new run may use a separately named bbox_xyxy_1000 input field, deterministic conversion to bbox_xyxy_640 using actual image dimensions, duplicate flags, and explicit converted overlays. No legacy box was clipped or silently accepted.
