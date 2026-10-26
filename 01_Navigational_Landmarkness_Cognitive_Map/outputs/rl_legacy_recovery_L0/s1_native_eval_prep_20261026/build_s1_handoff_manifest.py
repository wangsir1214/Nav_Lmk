#!/usr/bin/env python3
"""Create the SHA-256 inventory for the approved lightweight S1-ENV package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FILES = [
    "README.md",
    "S0_LOCAL_REVIEW.md",
    "S0_LOCAL_REVIEW_EVIDENCE.json",
    "HUMAN_S1_APPROVAL.md",
    "task_review.csv",
    "S1_EVALUATION_PROTOCOL.md",
    "S1_EPISODES_DRAFT.jsonl",
    "EPISODE_DRAFT_AUDIT.json",
    "S1_METRICS_SPEC.md",
    "SERVER_S1A_HANDOFF.md",
    "S1_PREPARATION_VALIDATION.json",
    "build_s1_handoff_manifest.py",
    "validate_s1_handoff.py",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block.replace(b"\r\n", b"\n").replace(b"\r", b"\n"))
    return digest.hexdigest()


def main() -> None:
    records = []
    for name in FILES:
        path = ROOT / name
        if not path.is_file():
            raise SystemExit(f"missing handoff file: {name}")
        canonical_size = len(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n"))
        records.append({"path": name, "size_bytes": canonical_size, "sha256": sha256(path)})
    manifest = {
        "format": "nav_lmk_s1_env_handoff_manifest_v1",
        "scope": "S1 environment-only smoke handoff; no PPO or rollout authorization",
        "manifest_self_hash": "omitted; Git commit SHA anchors this manifest",
        "files": records,
    }
    (ROOT / "S1_HANDOFF_PACKAGE_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({"file_count": len(records), "manifest": str(ROOT / "S1_HANDOFF_PACKAGE_MANIFEST.json")}, indent=2))


if __name__ == "__main__":
    main()
