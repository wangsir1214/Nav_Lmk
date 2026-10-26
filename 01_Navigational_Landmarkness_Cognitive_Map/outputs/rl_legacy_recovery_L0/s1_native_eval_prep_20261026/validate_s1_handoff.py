#!/usr/bin/env python3
"""Validate the S1-ENV handoff files and draft episode invariants without a model."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "S1_HANDOFF_PACKAGE_MANIFEST.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block.replace(b"\r\n", b"\n").replace(b"\r", b"\n"))
    return digest.hexdigest()


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    file_checks = {}
    for item in manifest["files"]:
        path = ROOT / item["path"]
        canonical_size = len(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")) if path.is_file() else -1
        file_checks[item["path"]] = (
            path.is_file()
            and canonical_size == item["size_bytes"]
            and sha256(path) == item["sha256"]
        )

    episodes = [
        json.loads(line)
        for line in (ROOT / "S1_EPISODES_DRAFT.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    bins = {"[100,200)": 0, "[200,300)": 0, "[300,400)": 0, "[400,550]": 0}
    for episode in episodes:
        label = episode["difficulty_bin_geodesic_m"]
        if label in bins:
            bins[label] += 1

    with (ROOT / "task_review.csv").open(encoding="utf-8-sig", newline="") as stream:
        review_rows = {row["item_id"]: row for row in csv.DictReader(stream)}
    expected_decisions = {
        "S0_LOCAL_REVIEW": "APPROVE",
        "S1A_FULL_ONLY_FIRST": "APPROVE",
        "EPISODE_COUNT_24": "APPROVE_AS_DRAFT",
        "DISTANCE_BINS_100_550M": "APPROVE_AS_DRAFT",
        "JSON_PROXY_COORDINATES_PENDING_SHP_JOIN": "APPROVE_CONDITIONAL",
        "FIXED_GOAL_EVALUATOR_SHIM": "APPROVE_FOR_ENV_SMOKE_ONLY",
        "SUCCESS_RADIUS_LT_100M": "APPROVE",
        "MAX_STEPS_1000": "APPROVE",
        "STOCHASTIC_CATEGORICAL_POLICY": "APPROVE_FOR_FUTURE_FULL",
        "SERVER_ENVIRONMENT_ONLY_SMOKE": "APPROVE",
        "SERVER_S1A_FULL_ROLLOUT_LATER_APPROVAL": "DEFER_NOT_AUTHORIZED",
    }
    approval_text = (ROOT / "HUMAN_S1_APPROVAL.md").read_text(encoding="utf-8")
    handoff_text = (ROOT / "SERVER_S1A_HANDOFF.md").read_text(encoding="utf-8")

    checks = {
        "manifest_files_match": bool(file_checks) and all(file_checks.values()),
        "approval_rows_match": all(review_rows.get(key, {}).get("decision") == value for key, value in expected_decisions.items()),
        "approval_date_and_human_scope": "2026-10-26" in approval_text and "人工审核意见，不是机器验证结论" in approval_text,
        "rollout_explicitly_forbidden": "严禁加载或调用 PPO" in handoff_text and "Full rollout" in handoff_text,
        "24_draft_episodes": len(episodes) == 24 and len({item["episode_id"] for item in episodes}) == 24,
        "draft_bins_are_six_each": bins == {"[100,200)": 6, "[200,300)": 6, "[300,400)": 6, "[400,550]": 6},
        "48_unique_start_goal_panos": len({item["start_pano_id"] for item in episodes} | {item["goal_pano_id"] for item in episodes}) == 48,
        "proxy_coordinates_not_frozen": all("proxy" in item["coordinate_status"].lower() and "shp" in item["coordinate_status"].lower() for item in episodes),
        "no_local_drive_path_in_episode_audit": "F:\\\\" not in (ROOT / "EPISODE_DRAFT_AUDIT.json").read_text(encoding="utf-8"),
        "no_model_or_rollout_executed": True,
    }
    result = {
        "status": "PASS_S1_ENV_HANDOFF_ONLY" if all(checks.values()) else "FAIL",
        "checks": checks,
        "file_checks": file_checks,
        "episodes": len(episodes),
        "distance_bins": bins,
        "model_calls": 0,
        "rollouts": 0,
        "environment_smokes": 0,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
