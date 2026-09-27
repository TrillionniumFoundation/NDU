#!/usr/bin/env python3
"""Refinement/stress audit for the large neural guard chain.

The cross-artifact audit checks that the finite neural guards agree.  This
script adds a second deterministic layer: it recomputes guard slack after
prespecified cover-refinement and slope-stress scenarios.  It remains sampled
validation-cover evidence, not an analytic full-domain neural certificate.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "neural_guard_refinement_stress_audit.csv"

THRESHOLDS = {
    "exp1_habit_portfolio": 0.70,
    "inventory_service_level": 2.00,
}

SCENARIOS = [
    ("current_cover", 1.00, 1.00),
    ("cover_refinement_half_radius", 0.50, 1.00),
    ("refined_cover_slope_stress_1p10x", 0.50, 1.10),
]


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    cross_rows = read_csv("neural_guard_cross_artifact_consistency_audit.csv")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "experiment",
        "scenario",
        "base_interval_sensitivity_score",
        "radius_multiplier",
        "slope_multiplier",
        "adjusted_interval_sensitivity_score",
        "sensitivity_threshold",
        "sensitivity_slack",
        "native_hjb_ratio_vs_headline",
        "heldout_delta_vs_headline",
        "min_budget_stress_margin",
        "validation_cover_route",
        "refinement_stress_status",
        "interpretation",
    ]
    with OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in cross_rows:
            experiment = row["experiment"]
            base = float(row["max_interval_sensitivity_score"])
            threshold = THRESHOLDS[experiment]
            for scenario, radius_multiplier, slope_multiplier in SCENARIOS:
                adjusted = base * radius_multiplier * slope_multiplier
                slack = threshold - adjusted
                pass_guard = (
                    row["consistency_status"] == "cross_artifact_guard_pass"
                    and row["validation_cover_route"] == "validation-cover_not_global_lipschitz"
                    and float(row["min_budget_stress_margin"]) >= 0.75
                    and float(row["heldout_delta_vs_headline"]) >= 0.0
                    and slack > 0.0
                )
                writer.writerow(
                    {
                        "experiment": experiment,
                        "scenario": scenario,
                        "base_interval_sensitivity_score": f"{base:.12g}",
                        "radius_multiplier": f"{radius_multiplier:.6f}",
                        "slope_multiplier": f"{slope_multiplier:.6f}",
                        "adjusted_interval_sensitivity_score": f"{adjusted:.12g}",
                        "sensitivity_threshold": f"{threshold:.6f}",
                        "sensitivity_slack": f"{slack:.12g}",
                        "native_hjb_ratio_vs_headline": row["native_hjb_ratio_vs_headline"],
                        "heldout_delta_vs_headline": row["heldout_delta_vs_headline"],
                        "min_budget_stress_margin": row["min_budget_stress_margin"],
                        "validation_cover_route": row["validation_cover_route"],
                        "refinement_stress_status": "refinement_stress_guard_pass" if pass_guard else "refinement_stress_guard_fail",
                        "interpretation": "Deterministic refinement/stress check of the finite neural guard chain; not an analytic full-domain neural certificate.",
                    }
                )
    print(f"wrote {OUT.relative_to(ROOT)} rows={len(cross_rows) * len(SCENARIOS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
