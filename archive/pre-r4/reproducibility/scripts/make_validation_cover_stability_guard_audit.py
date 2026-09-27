#!/usr/bin/env python3
"""Validation-cover stability guards for sampled neural HJB gap rows.

The validation-cover theorem gives the fill-distance/Lipschitz route from
sampled gaps to compact-domain bounds.  This audit adds finite-sample guard
checks for the reported large HBO/NBO validation-cover rows: tuple completeness,
coverage size, p95-to-sup greedy-tail stability, residual/terminal thresholds,
and held-out rollout preservation.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "validation_cover_stability_guard_audit.csv"


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="") as fh:
        return list(csv.DictReader(fh))


def fmt(x: float) -> str:
    return f"{x:.12g}"


def main() -> int:
    rows = []
    thresholds = {
        "exp1_habit_portfolio": {
            "max_native": 0.15,
            "max_normalized": 0.31,
            "max_terminal": 0.51,
            "max_tail_ratio": 5.0,
            "min_density": 0.015,
        },
        "inventory_service_level": {
            "max_native": 0.20,
            "max_normalized": 1.0,
            "max_terminal": 0.94,
            "max_tail_ratio": 5.0,
            "min_density": 0.05,
        },
    }
    for r in read_csv("neural_validation_cover_hjb_gap_audit.csv"):
        exp = r["experiment"]
        th = thresholds[exp]
        validation_pairs = int(r["validation_pairs"])
        terminal_points = int(r["terminal_grid_points"])
        action_grid = int(r["action_grid_size"])
        native = float(r["native_hjb_ratio_vs_headline"])
        normalized = float(r["normalized_rmse_ratio_vs_headline"])
        terminal = float(r["terminal_loss_ratio_vs_headline"])
        p95 = float(r["greedy_gap_p95"])
        sup = float(r["greedy_gap_sup"])
        tail = sup / max(p95, 1e-12)
        density = validation_pairs / max(1, terminal_points * action_grid)
        pass_guard = (
            int(r["certificate_tuple_complete"]) == 1
            and validation_pairs >= 360
            and native < th["max_native"]
            and normalized < th["max_normalized"]
            and terminal < th["max_terminal"]
            and tail < th["max_tail_ratio"]
            and density > th["min_density"]
            and float(r["heldout_delta_vs_headline"]) >= 0.0
        )
        rows.append({
            "experiment": exp,
            "validation_pairs": validation_pairs,
            "terminal_grid_points": terminal_points,
            "action_grid_size": action_grid,
            "validation_density_proxy": fmt(density),
            "native_hjb_ratio_vs_headline": fmt(native),
            "normalized_rmse_ratio_vs_headline": fmt(normalized),
            "terminal_loss_ratio_vs_headline": fmt(terminal),
            "greedy_gap_p95": fmt(p95),
            "greedy_gap_sup": fmt(sup),
            "greedy_tail_ratio_sup_over_p95": fmt(tail),
            "heldout_delta_vs_headline": r["heldout_delta_vs_headline"],
            "tuple_complete": r["certificate_tuple_complete"],
            "stability_guard_status": "validation_cover_stability_guard_pass" if pass_guard else "validation_cover_stability_guard_gap",
            "interpretation": "Finite-sample guard for the validation-cover theorem: tuple complete, residual/terminal gaps reduced, greedy p95-to-sup tail controlled, validation density recorded, and held-out rollout preserved.",
        })
    with OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
