#!/usr/bin/env python3
"""Sensitivity/refinement audit for neural interval-domain certificate rows.

The interval-domain certificate is conditional on declared local slope
envelopes and cover-radius proxies.  This audit stress-tests that dependence:
it recomputes the interval score under slope multipliers and cover-radius
refinement scenarios, without claiming unrestricted neural-network interval
arithmetic.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "neural_interval_sensitivity_audit.csv"

FIELDNAMES = [
    "experiment",
    "scenario",
    "slope_multiplier",
    "cover_radius_multiplier",
    "native_hjb_ratio_vs_headline",
    "terminal_loss_ratio_vs_headline",
    "greedy_gap_p95",
    "residual_sensitivity_bound",
    "terminal_sensitivity_bound",
    "greedy_sensitivity_bound",
    "sensitivity_score",
    "sensitivity_threshold",
    "max_slope_multiplier_at_current_cover",
    "cover_radius_multiplier_needed_at_2x_slope",
    "all_sensitivity_guards_pass",
    "sensitivity_status",
    "interpretation",
]

SCENARIOS = [
    ("nominal_interval", 1.00, 1.00),
    ("slope_stress_1p5x_current_cover", 1.50, 1.00),
    ("cover_refinement_2x_slope_half_radius", 2.00, 0.50),
]


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="") as fh:
        return list(csv.DictReader(fh))


def fmt(x: float) -> str:
    return f"{x:.12g}"


def main() -> None:
    interval_rows = {r["experiment"]: r for r in read_csv("neural_interval_domain_certificate.csv")}
    out_rows: list[dict[str, str]] = []

    for experiment in ["exp1_habit_portfolio", "inventory_service_level"]:
        row = interval_rows[experiment]
        native = float(row["native_hjb_ratio_vs_headline"])
        terminal = float(row["terminal_loss_ratio_vs_headline"])
        greedy = float(row["greedy_gap_p95"])
        cover_radius = float(row["cover_radius_proxy"])
        residual_slope = float(row["residual_interval_slope_bound"])
        terminal_slope = float(row["terminal_interval_slope_bound"])
        greedy_slope = float(row["greedy_interval_slope_bound"])
        threshold = float(row["interval_certificate_threshold"])

        sampled_score = native + 0.25 * terminal + 0.02 * greedy
        slope_weight = cover_radius * (residual_slope + 0.25 * terminal_slope + 0.02 * greedy_slope)
        if slope_weight > 0:
            max_slope_multiplier = (threshold - sampled_score) / slope_weight
            cover_needed_2x = (threshold - sampled_score) / (2.0 * slope_weight)
        else:
            max_slope_multiplier = float("inf")
            cover_needed_2x = 1.0
        cover_needed_2x = min(1.0, max(0.0, cover_needed_2x))

        for scenario, slope_multiplier, cover_multiplier in SCENARIOS:
            effective_radius = cover_radius * cover_multiplier
            residual_bound = native + slope_multiplier * residual_slope * effective_radius
            terminal_bound = terminal + slope_multiplier * terminal_slope * effective_radius
            greedy_bound = greedy + slope_multiplier * greedy_slope * effective_radius
            score = residual_bound + 0.25 * terminal_bound + 0.02 * greedy_bound
            guards = {
                "base_interval_passed": row["interval_certificate_status"] == "interval_domain_certificate_pass",
                "score_below_threshold": score < threshold,
                "max_multiplier_ge_scenario": max_slope_multiplier >= slope_multiplier * cover_multiplier,
                "bounds_nonnegative": min(residual_bound, terminal_bound, greedy_bound) >= 0.0,
            }
            passed = all(guards.values())
            out_rows.append(
                {
                    "experiment": experiment,
                    "scenario": scenario,
                    "slope_multiplier": fmt(slope_multiplier),
                    "cover_radius_multiplier": fmt(cover_multiplier),
                    "native_hjb_ratio_vs_headline": fmt(native),
                    "terminal_loss_ratio_vs_headline": fmt(terminal),
                    "greedy_gap_p95": fmt(greedy),
                    "residual_sensitivity_bound": fmt(residual_bound),
                    "terminal_sensitivity_bound": fmt(terminal_bound),
                    "greedy_sensitivity_bound": fmt(greedy_bound),
                    "sensitivity_score": fmt(score),
                    "sensitivity_threshold": fmt(threshold),
                    "max_slope_multiplier_at_current_cover": fmt(max_slope_multiplier),
                    "cover_radius_multiplier_needed_at_2x_slope": fmt(cover_needed_2x),
                    "all_sensitivity_guards_pass": "1" if passed else "0",
                    "sensitivity_status": "interval_sensitivity_guard_pass" if passed else "interval_sensitivity_guard_fail",
                    "interpretation": (
                        "Deterministic sensitivity/refinement audit for the compact-domain interval certificate. "
                        "The row perturbs declared local slope envelopes and cover-radius proxies; it is a "
                        "stability guard for the submitted sampled certificate, not analytic full-domain interval "
                        "arithmetic for the trained neural network."
                    ),
                }
            )

    with OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(out_rows)


if __name__ == "__main__":
    main()
