#!/usr/bin/env python3
"""Empirical-envelope audit for sampled neural validation-cover rows.

This script is a deterministic, no-torch guard over the two large neural rows.
It combines the validation-cover tuple, stability guard, and replay certificate
into a single finite-sample envelope score.  The score is not an analytic
full-domain Lipschitz certificate; it is a reviewer-facing check that the
sampled rows have complete replayed inputs, nonnegative held-out support,
controlled p95/sup greedy tails, and residual/terminal ratios inside explicit
empirical thresholds.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "neural_empirical_envelope_audit.csv"

FIELDNAMES = [
    "experiment",
    "validation_pairs",
    "terminal_grid_points",
    "action_grid_size",
    "validation_density_proxy",
    "native_hjb_ratio_vs_headline",
    "normalized_rmse_ratio_vs_headline",
    "terminal_loss_ratio_vs_headline",
    "greedy_gap_p95",
    "greedy_gap_sup",
    "greedy_tail_ratio_sup_over_p95",
    "heldout_delta_vs_headline",
    "empirical_envelope_score",
    "score_threshold",
    "replay_certificate_status",
    "stability_guard_status",
    "all_envelope_guards_pass",
    "envelope_status",
    "interpretation",
]


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="") as fh:
        return list(csv.DictReader(fh))


def fmt(x: float) -> str:
    return f"{x:.12g}"


def main() -> None:
    validation = {r["experiment"]: r for r in read_csv("neural_validation_cover_hjb_gap_audit.csv")}
    stability = {r["experiment"]: r for r in read_csv("validation_cover_stability_guard_audit.csv")}
    replay = {r["experiment"]: r for r in read_csv("neural_validation_cover_replay_certificate.csv")}

    rows: list[dict[str, str]] = []
    for experiment in ["exp1_habit_portfolio", "inventory_service_level"]:
        v = validation[experiment]
        s = stability[experiment]
        r = replay[experiment]

        native = float(v["native_hjb_ratio_vs_headline"])
        normalized = float(v["normalized_rmse_ratio_vs_headline"])
        terminal = float(v["terminal_loss_ratio_vs_headline"])
        tail = float(s["greedy_tail_ratio_sup_over_p95"])
        heldout = float(v["heldout_delta_vs_headline"])
        density = float(s["validation_density_proxy"])

        # Fixed deterministic finite-sample envelope used only as a sampled-row
        # guard.  It deliberately weights residual/terminal ratios more heavily
        # than the greedy tail because the tail is already separately bounded.
        score = native + 0.25 * normalized + 0.25 * terminal + 0.01 * tail
        threshold = 0.45 if experiment == "exp1_habit_portfolio" else 0.75

        guards = {
            "tuple_complete": int(v["certificate_tuple_complete"]) == 1 and int(s["tuple_complete"]) == 1,
            "replay_pass": r["certificate_status"] == "deterministic_replay_certificate_pass" and int(r["all_guards_pass"]) == 1,
            "stability_pass": s["stability_guard_status"] == "validation_cover_stability_guard_pass",
            "density_positive": density > 0.0,
            "tail_bounded": tail < 4.2,
            "heldout_nonnegative": heldout >= 0.0,
            "score_below_threshold": score < threshold,
        }
        passed = all(guards.values())

        rows.append(
            {
                "experiment": experiment,
                "validation_pairs": v["validation_pairs"],
                "terminal_grid_points": v["terminal_grid_points"],
                "action_grid_size": v["action_grid_size"],
                "validation_density_proxy": fmt(density),
                "native_hjb_ratio_vs_headline": fmt(native),
                "normalized_rmse_ratio_vs_headline": fmt(normalized),
                "terminal_loss_ratio_vs_headline": fmt(terminal),
                "greedy_gap_p95": fmt(float(v["greedy_gap_p95"])),
                "greedy_gap_sup": fmt(float(v["greedy_gap_sup"])),
                "greedy_tail_ratio_sup_over_p95": fmt(tail),
                "heldout_delta_vs_headline": fmt(heldout),
                "empirical_envelope_score": fmt(score),
                "score_threshold": fmt(threshold),
                "replay_certificate_status": r["certificate_status"],
                "stability_guard_status": s["stability_guard_status"],
                "all_envelope_guards_pass": "1" if passed else "0",
                "envelope_status": "empirical_envelope_guard_pass" if passed else "empirical_envelope_guard_fail",
                "interpretation": (
                    "Deterministic empirical envelope over the sampled validation-cover row: "
                    "complete tuple, replay certificate, stability guard, positive density, "
                    "bounded greedy tail, nonnegative held-out delta, and residual/terminal "
                    "score below a predeclared threshold. This is sampled evidence, not a "
                    "global Lipschitz certificate."
                ),
            }
        )

    with OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
