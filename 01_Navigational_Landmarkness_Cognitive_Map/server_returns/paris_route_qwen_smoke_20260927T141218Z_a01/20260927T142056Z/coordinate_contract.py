"""Strict 0-1000 model-box contract and deterministic image-pixel conversion."""
import math


class CoordinateContractError(ValueError):
    def __init__(self, kind, message):
        super().__init__(message)
        self.kind = kind


def convert_bbox_1000(box, width, height):
    if not isinstance(width, int) or not isinstance(height, int) or width <= 0 or height <= 0:
        raise CoordinateContractError("image_size", "Invalid actual image dimensions")
    if not isinstance(box, list) or len(box) != 4:
        raise CoordinateContractError("structure", "bbox_xyxy_1000 must have four numbers")
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in box):
        raise CoordinateContractError("structure", "bbox_xyxy_1000 must contain finite numbers")
    x1, y1, x2, y2 = box
    if not (0 <= x1 < x2 <= 1000 and 0 <= y1 < y2 <= 1000):
        raise CoordinateContractError("out_of_bounds", f"bbox_xyxy_1000 outside 0-1000 or degenerate: {box}")
    result = [round(x1 * width / 1000, 6), round(y1 * height / 1000, 6),
              round(x2 * width / 1000, 6), round(y2 * height / 1000, 6)]
    if not (0 <= result[0] < result[2] <= width and 0 <= result[1] < result[3] <= height):
        raise CoordinateContractError("conversion", "Converted box is invalid for actual image size")
    return result


def validate_candidates(candidates, image_size, schema):
    if not isinstance(candidates, list) or len(candidates) > 3:
        raise CoordinateContractError("structure", "candidates must be a list with at most three items")
    if not candidates:
        return [], "no_clear_candidate", []
    width, height = image_size
    if (width, height) != (640, 640):
        raise CoordinateContractError("image_size", f"Expected original 640x640, got {image_size}")
    contract = schema["candidate_proposal"]
    exact = set(contract["candidate_object_exact_keys"])
    valid_types = set(contract["enums"]["type"]) - {"no_clear_candidate"}
    valid_visibility = set(contract["enums"]["visibility"])
    seen_ids = set()
    converted = []
    for index, item in enumerate(candidates):
        if not isinstance(item, dict):
            raise CoordinateContractError("structure", f"candidate {index} is not an object")
        missing, extra = exact - set(item), set(item) - exact
        if missing or extra:
            raise CoordinateContractError("extra_or_missing", f"candidate {index}: missing={sorted(missing)} extra={sorted(extra)}")
        candidate_id = item["candidate_id"]
        if (isinstance(candidate_id, bool) or not isinstance(candidate_id, (int, str))
                or isinstance(candidate_id, str) and not 0 < len(candidate_id) <= 24
                or candidate_id in seen_ids):
            raise CoordinateContractError("structure", f"candidate {index}: invalid or duplicate candidate_id")
        seen_ids.add(candidate_id)
        if not isinstance(item["type"], str) or item["type"] not in valid_types:
            raise CoordinateContractError("enum", f"candidate {index}: invalid type")
        if not isinstance(item["visibility"], str) or item["visibility"] not in valid_visibility:
            raise CoordinateContractError("enum", f"candidate {index}: invalid visibility")
        if not isinstance(item["description"], str) or not isinstance(item["hypothesized_role"], str):
            raise CoordinateContractError("structure", f"candidate {index}: invalid description or role")
        uncertainty = item["uncertainty"]
        if (isinstance(uncertainty, bool) or not isinstance(uncertainty, (int, float))
                or not math.isfinite(uncertainty) or not 0 <= uncertainty <= 1):
            raise CoordinateContractError("structure", f"candidate {index}: uncertainty outside [0,1]")
        pixel_box = convert_bbox_1000(item["bbox_xyxy_1000"], width, height)
        converted.append({**item, "bbox_xyxy_640": pixel_box, "duplicate_review_flags": []})
    pairs = []
    for i in range(len(converted)):
        for j in range(i + 1, len(converted)):
            left, right = converted[i], converted[j]
            reasons = []
            if left["bbox_xyxy_1000"] == right["bbox_xyxy_1000"]:
                reasons.append("identical_raw_bbox")
            if " ".join(left["description"].casefold().split()) == " ".join(right["description"].casefold().split()):
                reasons.append("same_description_possible_same_landmark")
            if reasons:
                pair = {"candidate_ids": [left["candidate_id"], right["candidate_id"]], "reasons": reasons,
                        "review_required": True}
                pairs.append(pair)
                for item in (left, right):
                    item["duplicate_review_flags"].extend(reasons)
    return converted, "ok", pairs
