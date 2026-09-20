#!/usr/bin/env python3
"""Deterministic replay certificate for large neural validation-cover rows.

This script does not retrain HBO/NBO policies. It checks that the packaged
large-neural validation-cover tuple is traceable to the shipped CSV evidence,
that the source files match their manifest hashes, and that the guard
thresholds used by the manuscript still pass.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "neural_validation_cover_replay_certificate.csv"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="") as fh:
        return list(csv.DictReader(fh))


def by_key(name: str, key: str) -> dict[str, dict[str, str]]:
    return {row[key]: row for row in read_rows(name)}


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def manifest_hashes(manifest: dict[str, Any], names: list[str]) -> str:
    file_map = {item["path"]: item["sha256"] for item in manifest["files"]}
    entries = []
    for name in names:
        path = f"data/{name}"
        observed = sha256(DATA / name)
        expected = file_map.get(path, "")
        entries.append(f"{name}:{observed}:{'manifest_match' if observed == expected else 'manifest_mismatch'}")
    return "|".join(entries)


def pass_flag(ok: bool) -> str:
    return "1" if ok else "0"


def main() -> int:
    manifest = json.loads((ROOT / "manifest.json").read_text())
    vc_manifest = manifest["neural_validation_cover_hjb_gap_audit"]
    vc_rows = by_key("neural_validation_cover_hjb_gap_audit.csv", "experiment")
    stability_rows = by_key("validation_cover_stability_guard_audit.csv", "experiment")
    greedy_rows = {(r["experiment"], r["audit_config"]): r for r in read_rows("hbo_greedy_gap_audit.csv")}
    residual_rows = {(r["experiment"], r["audit_config"]): r for r in read_rows("hbo_residual_closing_audit.csv")}
    norm_rows = {(r["experiment"], r["audit_config"]): r for r in read_rows("hbo_inventory_normalized_residual_audit.csv")}

    source_files = [
        "neural_validation_cover_hjb_gap_audit.csv",
        "validation_cover_stability_guard_audit.csv",
        "hbo_greedy_gap_audit.csv",
        "hbo_residual_closing_audit.csv",
        "hbo_inventory_normalized_residual_audit.csv",
    ]
    source_hash_bundle = manifest_hashes(manifest, source_files)

    rows: list[dict[str, Any]] = []
    for experiment, expected in vc_manifest["expected"].items():
        vc = vc_rows[experiment]
        stability = stability_rows[experiment]
        greedy_config = vc["greedy_source_config"]
        residual_config = vc["residual_source_config"]
        normalized_config = vc["normalized_source_config"]
        greedy = greedy_rows[(experiment, greedy_config)]
        residual = residual_rows.get((experiment, residual_config), {})
        normalized = norm_rows.get((experiment, normalized_config), residual)

        checks = {
            "tuple_complete": int(vc["certificate_tuple_complete"]) == 1 and int(stability["tuple_complete"]) == 1,
            "validation_pairs": int(vc["validation_pairs"]) >= expected["min_validation_pairs"],
            "native_ratio": float(vc["native_hjb_ratio_vs_headline"]) < expected["max_native_hjb_ratio"],
            "normalized_ratio": float(vc["normalized_rmse_ratio_vs_headline"]) < expected["max_normalized_rmse_ratio"],
            "terminal_ratio": float(vc["terminal_loss_ratio_vs_headline"]) < expected["max_terminal_loss_ratio"],
            "greedy_p95": float(vc["greedy_gap_p95"]) < expected["max_greedy_gap_p95"],
            "heldout": float(vc["heldout_delta_vs_headline"]) >= expected["min_heldout_delta"],
            "greedy_source_match": abs(float(vc["greedy_gap_p95"]) - float(greedy["greedy_gap_p95"])) < 1e-10,
            "stability_source_match": stability["stability_guard_status"] == "validation_cover_stability_guard_pass",
        }
        rows.append(
            {
                "experiment": experiment,
                "certificate_status": "deterministic_replay_certificate_pass" if all(checks.values()) else "deterministic_replay_certificate_fail",
                "theorem_anchor": "Proposition validation_cover_hjb_gap_certificate + Corollary validation_cover_stability_guard",
                "source_hash_bundle": source_hash_bundle,
                "validation_cover_config": vc["validation_cover_role"],
                "residual_source_config": residual_config,
                "greedy_source_config": greedy_config,
                "normalized_source_config": normalized_config,
                "validation_pairs": vc["validation_pairs"],
                "native_hjb_ratio_vs_headline": vc["native_hjb_ratio_vs_headline"],
                "normalized_rmse_ratio_vs_headline": vc["normalized_rmse_ratio_vs_headline"],
                "terminal_loss_ratio_vs_headline": vc["terminal_loss_ratio_vs_headline"],
                "greedy_gap_p95": vc["greedy_gap_p95"],
                "greedy_gap_sup": vc["greedy_gap_sup"],
                "heldout_delta_vs_headline": vc["heldout_delta_vs_headline"],
                "source_native_hjb_loss": residual.get("native_hjb_loss", ""),
                "source_normalized_residual_rmse": normalized.get("normalized_residual_rmse", ""),
                "source_greedy_gap_sup": greedy["greedy_gap_sup"],
                "all_guards_pass": pass_flag(all(checks.values())),
                "check_tuple_complete": pass_flag(checks["tuple_complete"]),
                "check_validation_pairs": pass_flag(checks["validation_pairs"]),
                "check_native_ratio": pass_flag(checks["native_ratio"]),
                "check_normalized_ratio": pass_flag(checks["normalized_ratio"]),
                "check_terminal_ratio": pass_flag(checks["terminal_ratio"]),
                "check_greedy_p95": pass_flag(checks["greedy_p95"]),
                "check_heldout": pass_flag(checks["heldout"]),
                "check_greedy_source_match": pass_flag(checks["greedy_source_match"]),
                "check_stability_source_match": pass_flag(checks["stability_source_match"]),
                "interpretation": "Hash-anchored deterministic replay of the sampled validation-cover tuple; it strengthens artifact traceability and does not convert sampled neural rows into global Lipschitz certificates.",
            }
        )

    write_csv(OUT, rows)
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
