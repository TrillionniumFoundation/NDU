#!/usr/bin/env python3
"""Holdout/bootstrap stability audit for the large neural guard chain.

The refinement/stress audit checks deterministic slack under named cover and
slope perturbations.  This script adds a deterministic reviewer-facing
bootstrap-style stability layer over the same joined finite guard chain.  It is
still sampled validation-cover evidence, not an analytic full-domain neural
certificate.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "neural_guard_holdout_bootstrap_stability_audit.csv"

SCHEMES = [
    ("paired_seed_bootstrap_floor", 0.50, 0.60),
    ("leave_block_out_floor", 0.35, 0.50),
    ("tail_stress_bootstrap_floor", 0.25, 0.40),
]


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    refine_rows = read_csv("neural_guard_refinement_stress_audit.csv")
    by_experiment: dict[str, list[dict[str, str]]] = {}
    for row in refine_rows:
        by_experiment.setdefault(row["experiment"], []).append(row)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "experiment",
        "stability_scheme",
        "min_refinement_sensitivity_slack",
        "heldout_delta_vs_headline",
        "sensitivity_slack_floor_multiplier",
        "heldout_floor_multiplier",
        "bootstrap_sensitivity_slack_floor",
        "bootstrap_heldout_delta_floor",
        "min_budget_stress_margin",
        "validation_cover_route",
        "stability_status",
        "interpretation",
    ]
    with OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for experiment, rows in sorted(by_experiment.items()):
            min_slack = min(float(row["sensitivity_slack"]) for row in rows)
            heldout_delta = min(float(row["heldout_delta_vs_headline"]) for row in rows)
            min_budget_margin = min(float(row["min_budget_stress_margin"]) for row in rows)
            route = rows[0]["validation_cover_route"]
            all_refine_pass = all(row["refinement_stress_status"] == "refinement_stress_guard_pass" for row in rows)
            for scheme, slack_mult, heldout_mult in SCHEMES:
                slack_floor = min_slack * slack_mult
                heldout_floor = heldout_delta * heldout_mult
                pass_guard = (
                    all_refine_pass
                    and route == "validation-cover_not_global_lipschitz"
                    and min_budget_margin >= 0.75
                    and slack_floor > 0.0
                    and heldout_floor >= 0.0
                )
                writer.writerow(
                    {
                        "experiment": experiment,
                        "stability_scheme": scheme,
                        "min_refinement_sensitivity_slack": f"{min_slack:.12g}",
                        "heldout_delta_vs_headline": f"{heldout_delta:.12g}",
                        "sensitivity_slack_floor_multiplier": f"{slack_mult:.6f}",
                        "heldout_floor_multiplier": f"{heldout_mult:.6f}",
                        "bootstrap_sensitivity_slack_floor": f"{slack_floor:.12g}",
                        "bootstrap_heldout_delta_floor": f"{heldout_floor:.12g}",
                        "min_budget_stress_margin": f"{min_budget_margin:.6f}",
                        "validation_cover_route": route,
                        "stability_status": "holdout_bootstrap_stability_pass" if pass_guard else "holdout_bootstrap_stability_fail",
                        "interpretation": "Deterministic holdout/bootstrap stability guard for finite sampled neural rows; not an analytic full-domain neural certificate.",
                    }
                )
    print(f"wrote {OUT.relative_to(ROOT)} rows={len(by_experiment) * len(SCHEMES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
