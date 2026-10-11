"""Normalize only an optional full Markdown fence around model JSON."""

import json
import re


_FULL_JSON_FENCE = re.compile(
    r"\A```(?:json)?[ \t]*\r?\n(?P<body>.*?)\r?\n```[ \t]*\Z",
    flags=re.IGNORECASE | re.DOTALL,
)


def parse_model_json(raw: str) -> tuple[object, str, str]:
    """Return parsed value, normalization type, and exact text passed to json.loads.

    The caller must still validate the parsed value against its task schema.
    """
    normalized = raw.strip()
    normalization_type = "none"
    if normalized.startswith("```"):
        match = _FULL_JSON_FENCE.fullmatch(normalized)
        if match is None:
            raise ValueError("Model reply is not a single complete JSON code fence")
        normalized = match.group("body").strip()
        normalization_type = "full_json_fence"
    return json.loads(normalized), normalization_type, normalized
