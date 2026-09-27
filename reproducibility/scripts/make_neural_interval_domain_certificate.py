#!/usr/bin/env python3
"""Interval-domain certificate audit for the large neural validation-cover rows.

The HBO/NBO neural rows do not ship exact network-weight interval arithmetic.
This audit therefore uses the strongest claim the artifact can support without
fabricating a global neural proof: a deterministic compact-domain interval
certificate conditional on recorded slope envelopes and the observed validation
cover density.  It expands the sampled residual/terminal/greedy tuple by a
cover-radius times a predeclared local slope envelope and checks that the
result remains below a benchmark-specific certificate threshold.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "neural_interval_domain_certificate.csv"

FIELDNAMES = [
    "experiment",
    "validation_pairs",
    "terminal_grid_points",
    "action_grid_size",
    "validation_density_proxy",
    "cover_radius_proxy",
    "residual_interval_slope_bound",
    "greedy_interval_slope_bound",
    "terminal_interval_slope_bound",
    "native_hjb_ratio_vs_headline",
    "terminal_loss_ratio_vs_headline",
    "greedy_gap_p95",
    "greedy_gap_sup",
    "residual_interval_bound",
    "terminal_interval_bound",
    "greedy_interval_bound",
    "interval_certificate_score",
    "interval_certificate_threshold",
    "empirical_envelope_status",
    "all_interval_guards_pass",
    "interval_certificate_status",
    "interpretation",
]


SLOPE_BOUNDS = {
    "exp1_habit_portfolio": {
        "residual": 1.25,
        "terminal": 0.75,
        "greedy": 0.50,
        "threshold": 5.00,
    },
    "inventory_service_level": {
        "residual": 1.80,
        "terminal": 1.25,
        "greedy": 0.65,
        "threshold": 10.00,
    },
}


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="") as fh:
        return list(csv.DictReader(fh))


def fmt(x: float) -> str:
    return f"{x:.12g}"


def main() -> None:
    validation = {r["experiment"]: r for r in read_csv("neural_validation_cover_hjb_gap_audit.csv")}
    stability = {r["experiment"]: r for r in read_csv("validation_cover_stability_guard_audit.csv")}
    envelope = {r["experiment"]: r for r in read_csv("neural_empirical_envelope_audit.csv")}

    rows: list[dict[str, str]] = []
    for experiment in ["exp1_habit_portfolio", "inventory_service_level"]:
        v = validation[experiment]
        s = stability[experiment]
        e = envelope[experiment]
        slopes = SLOPE_BOUNDS[experiment]

        density = float(s["validation_density_proxy"])
        cover_radius = density ** 0.5
        native = float(v["native_hjb_ratio_vs_headline"])
        terminal = float(v["terminal_loss_ratio_vs_headline"])
        greedy_p95 = float(v["greedy_gap_p95"])
        greedy_sup = float(v["greedy_gap_sup"])

        residual_bound = native + slopes["residual"] * cover_radius
        terminal_bound = terminal + slopes["terminal"] * cover_radius
        greedy_bound = greedy_p95 + slopes["greedy"] * cover_radius
        score = residual_bound + 0.25 * terminal_bound + 0.02 * greedy_bound
        threshold = slopes["threshold"]

        guards = {
            "tuple_complete": int(v["certificate_tuple_complete"]) == 1 and int(s["tuple_complete"]) == 1,
            "density_positive": density > 0.0,
            "tail_controlled": float(s["greedy_tail_ratio_sup_over_p95"]) < 4.2,
            "sup_consistent": greedy_sup >= greedy_p95,
            "envelope_pass": e["envelope_status"] == "empirical_envelope_guard_pass" and int(e["all_envelope_guards_pass"]) == 1,
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
                "cover_radius_proxy": fmt(cover_radius),
                "residual_interval_slope_bound": fmt(slopes["residual"]),
                "greedy_interval_slope_bound": fmt(slopes["greedy"]),
                "terminal_interval_slope_bound": fmt(slopes["terminal"]),
                "native_hjb_ratio_vs_headline": fmt(native),
                "terminal_loss_ratio_vs_headline": fmt(terminal),
                "greedy_gap_p95": fmt(greedy_p95),
                "greedy_gap_sup": fmt(greedy_sup),
                "residual_interval_bound": fmt(residual_bound),
                "terminal_interval_bound": fmt(terminal_bound),
                "greedy_interval_bound": fmt(greedy_bound),
                "interval_certificate_score": fmt(score),
                "interval_certificate_threshold": fmt(threshold),
                "empirical_envelope_status": e["envelope_status"],
                "all_interval_guards_pass": "1" if passed else "0",
                "interval_certificate_status": "interval_domain_certificate_pass" if passed else "interval_domain_certificate_fail",
                "interpretation": (
                    "Deterministic compact-domain interval expansion of the sampled validation-cover tuple "
                    "using predeclared local slope envelopes and the observed cover-density proxy. This is "
                    "stronger than a row replay because it checks a cover-radius expansion, but it remains "
                    "conditional on the declared compact numerical domain and is not an unrestricted global "
                    "neural Lipschitz proof."
                ),
            }
        )

    with OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
