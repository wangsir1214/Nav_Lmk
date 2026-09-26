"""Confirm current NAS outputs against the saved audit and recompute retrieval.

Read-only on NAS. Uses existing light snapshots, not a recursive NAS scan.
Writes a new confirmation JSON; never overwrites a previous confirmation.
"""
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import sys

import numpy as np


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main(args):
    if args.output.exists():
        raise FileExistsError(args.output)
    checks = []

    def check(name, passed, detail=None):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})
        if not passed:
            raise ValueError(name + ": " + str(detail))

    def from_linux(value):
        prefix = "/home/nas/wangyq/"
        if not value.startswith(prefix) or ".." in PurePosixPath(value).parts:
            raise ValueError("Unmapped NAS path: " + value)
        return args.nas_root / value[len(prefix):]

    source = args.audit_dir / "source"
    result = args.nas_root / "outputs/Paris_local_v1_20260923/baseline_g14_v2"
    features = args.nas_root / "outputs/Paris_local_v1_20260923/features_g14_l31_value_c32_urban_448png_v2"
    previous = json.loads((args.audit_dir / "audit_report.json").read_text(encoding="utf-8"))
    for name, entry in previous["evidence"].items():
        local = Path(entry.get("local", name))
        check("saved_evidence:" + str(local), digest(local) == entry["sha256"])
    current_inputs = {}
    for local in sorted((source / "baseline_g14_v2").rglob("*")):
        if local.is_file():
            relative = local.relative_to(source / "baseline_g14_v2")
            remote = result / relative
            value = digest(remote)
            check("current_NAS_result:" + relative.as_posix(), value == digest(local))
            current_inputs[str(remote)] = value
    for name in ("run_config.json", "feature_index.csv"):
        remote = features / name
        current_inputs[str(remote)] = digest(remote)
        check("current_NAS_feature_metadata:" + name, digest(remote) == digest(source / "features" / name))
    check("desktop_handoff_matches_snapshot", digest(args.handoff) == digest(source / "SERVER_TO_LOCAL.md"))

    task = json.loads((args.task_dir / "task_manifest.json").read_text(encoding="utf-8"))
    for name, expected in task["hashes"].items():
        check("frozen_input:" + name, digest(args.task_dir / name) == expected)
    config = json.loads((source / "features/run_config.json").read_text(encoding="utf-8"))
    check("task_manifest_binding", config["task_manifest_sha256"] == digest(args.task_dir / "task_manifest.json"))
    check("request_binding", config["request_config_sha256"] == digest(args.task_dir / "configs/baseline_request_v2.json"))
    index = rows(source / "features/feature_index.csv")
    queries = rows(args.task_dir / "data/queries.csv")
    refs = rows(args.task_dir / "data/references.csv")
    pairs = rows(args.task_dir / "data/retrieval_pairs.csv")
    qids, rids = [q["view_id"] for q in queries], [r["view_id"] for r in refs]
    check("active_ids", len(index) == 212 and {r["view_id"] for r in index} == set(qids + rids))
    check("pano_disjoint", not ({q["pano_id"] for q in queries} & {r["pano_id"] for r in refs}))
    check("raw_image_hash_disjoint", not ({q["image_sha256"] for q in queries} & {r["image_sha256"] for r in refs}))
    vectors = {}
    for row in index:
        raw = from_linux(row["vlad_path"]).read_bytes()
        v = np.load(io.BytesIO(raw), allow_pickle=False)
        check("current_vlad:" + row["view_id"], hashlib.sha256(raw).hexdigest() == row["vlad_sha256"] and v.shape == (49152,) and v.dtype == np.float32 and np.isfinite(v).all() and abs(float(np.linalg.norm(v)) - 1) < 1e-5)
        vectors[row["view_id"]] = v
    print("Current result bytes and 212 VLAD vectors match the saved evidence.", flush=True)
    matrix = np.stack([vectors[q] for q in qids]).astype(np.float64) @ np.stack([vectors[r] for r in rids]).astype(np.float64).T
    qposition, rposition = {q:i for i,q in enumerate(qids)}, {r:i for i,r in enumerate(rids)}
    scores = rows(source / "baseline_g14_v2/pair_scores.csv")
    labels = {(p["query_view_id"], p["reference_view_id"]):p for p in pairs}
    check("pair_coverage", len(scores) == len(labels) == 7392 and {(r["query_view_id"], r["reference_view_id"]) for r in scores} == set(labels))
    max_error = 0.0
    for row in scores:
        key = row["query_view_id"], row["reference_view_id"]
        check("label:" + ":".join(key), row["relation"] == labels[key]["relation"])
        max_error = max(max_error, abs(float(row["cosine_similarity"]) - matrix[qposition[key[0]], rposition[key[1]]]))
    check("float64_similarity_recomputation", max_error < 1e-5, max_error)
    summaries = {}
    outputs = {}
    for mode, name in (("main", "baseline_per_query.csv"), ("sensitivity", "boundary_sensitivity_per_query.csv")):
        delivered = {r["query_view_id"]:r for r in rows(source / "baseline_g14_v2" / name)}
        check(mode + ":query_ids", set(delivered) == set(qids))
        computed = []
        for q in qids:
            rel = {r:labels[q,r]["relation"] for r in rids}
            if mode == "sensitivity":
                for r in rids:
                    if labels[q,r]["review_case_id"] in {"R123","R125"}:
                        rel[r] = "ignore"
            ranked = sorted((r for r in rids if rel[r] != "ignore"), key=lambda r:(-matrix[qposition[q],rposition[r]],r))
            pos = [r for r in ranked if rel[r] == "positive"]
            neg = [r for r in ranked if rel[r] == "negative"]
            rank = ranked.index(pos[0]) + 1
            margin = float(matrix[qposition[q],rposition[pos[0]]] - matrix[qposition[q],rposition[neg[0]]])
            row = delivered[q]
            check(mode + ":rank_and_counts:" + q, rank == int(row["best_positive_rank"]) and ranked[0] == row["top1_reference_id"] and pos[0] == row["best_positive_id"] and neg[0] == row["best_negative_id"] and len(pos) == int(row["positive_count"]) and len(neg) == int(row["negative_count"]) and 168-len(ranked) == int(row["ignore_count"]))
            check(mode + ":margin:" + q, abs(margin-float(row["margin"])) < 1e-5)
            for k in (1,5,10):
                check(mode + ":recall:" + str(k) + ":" + q, int(rank<=k) == int(row[f"recall_at_{k}"]))
            computed.append({"query_view_id":q,"best_positive_rank":rank,"margin_float64":margin})
        summaries[mode] = {"queries":len(computed), "success_count":{str(k):sum(r["best_positive_rank"]<=k for r in computed) for k in (1,5,10)}, "median_margin_float64":float(np.median([r["margin_float64"] for r in computed])), "positive_count_distribution":dict(Counter(r["positive_count"] for r in delivered.values()))}
        outputs[mode] = delivered

    strata = {}
    for n in sorted({int(r["positive_count"]) for r in outputs["main"].values()}):
        group = [r for r in outputs["main"].values() if int(r["positive_count"])==n]
        strata[str(n)] = {"n_queries":len(group),"r1_successes":sum(int(r["recall_at_1"]) for r in group),"median_margin":float(np.median([float(r["margin"]) for r in group]))}
    geometry = {}
    for relation in ("positive","negative","ignore"):
        group = [p for p in pairs if p["relation"]==relation]
        geometry[relation] = {"pairs":len(group),"distance_range_m":[min(float(p["distance_m"]) for p in group),max(float(p["distance_m"]) for p in group)],"same_segment":dict(Counter(p["same_segment"] for p in group)),"review_status":dict(Counter(p["review_status"] for p in group)),"same_capture_month_pairs":sum(p["capture_month_gap"]=="0" for p in group)}

    report = {"checked_utc":datetime.now(timezone.utc).isoformat(),"status":"PASS_CURRENT_NAS_RESULTS_AND_INDEPENDENT_SCORES", "script_sha256":digest(Path(__file__)),"command":sys.argv,"python":sys.version,"numpy":np.__version__,"current_nas_hashes":current_inputs,"previous_audit_sha256":digest(args.audit_dir / "audit_report.json"),"handoff_sha256":digest(args.handoff),"checks_count":len(checks),"failed_checks":[c for c in checks if not c["passed"]],"max_float64_score_error":max_error,"summaries":summaries,"positive_count_strata_descriptive_only":strata,"geometry":geometry,"notes":["Main has 8 queries with 1 P, 34 with 2 P, and 2 with 3 P; sensitivity has 8 with 1 P and 36 with 2 P.","No model rerun; no full patch or image-cache reread. Prior audit evidence reused after snapshot hash checks.","Server-only execution logs under /home/wangyq are not visible via the NAS mapping.","Positive-count subgroup differences are post hoc and confounded; not a causal effect or independent evaluation."]}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x",encoding="utf-8") as stream:
        json.dump(report,stream,ensure_ascii=False,indent=2)
        stream.write("\n")
    print(json.dumps({k:report[k] for k in ("status","checks_count","max_float64_score_error","summaries","positive_count_strata_descriptive_only")},ensure_ascii=False,indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--nas-root",type=Path,required=True)
    p.add_argument("--audit-dir",type=Path,required=True)
    p.add_argument("--task-dir",type=Path,required=True)
    p.add_argument("--handoff",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    main(p.parse_args())
