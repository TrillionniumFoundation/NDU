#!/usr/bin/env python3
"""Concordance audit for the large neural guard chain.

The holdout/bootstrap audit gives three finite stability schemes per large
neural row.  This script collapses those schemes into one reviewer-facing
concordance row per experiment and requires all schemes to agree on the
positive guard direction.  It remains sampled validation-cover evidence, not an
analytic full-domain neural certificate.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "neural_guard_concordance_audit.csv"


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    stability_rows = read_csv("neural_guard_holdout_bootstrap_stability_audit.csv")
    by_experiment: dict[str, list[dict[str, str]]] = {}
    for row in stability_rows:
        by_experiment.setdefault(row["experiment"], []).append(row)

    fieldnames = [
        "experiment",
        "stability_scheme_count",
        "positive_scheme_votes",
        "required_scheme_votes",
        "min_bootstrap_sensitivity_slack_floor",
        "min_bootstrap_heldout_delta_floor",
        "min_budget_stress_margin",
        "validation_cover_route",
        "concordance_status",
        "interpretation",
    ]
    with OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for experiment, rows in sorted(by_experiment.items()):
            scheme_count = len({row["stability_scheme"] for row in rows})
            positive_votes = sum(
                1
                for row in rows
                if row["stability_status"] == "holdout_bootstrap_stability_pass"
                and float(row["bootstrap_sensitivity_slack_floor"]) > 0.0
                and float(row["bootstrap_heldout_delta_floor"]) >= 0.0
                and float(row["min_budget_stress_margin"]) >= 0.75
                and row["validation_cover_route"] == "validation-cover_not_global_lipschitz"
            )
            min_slack = min(float(row["bootstrap_sensitivity_slack_floor"]) for row in rows)
            min_heldout = min(float(row["bootstrap_heldout_delta_floor"]) for row in rows)
            min_budget = min(float(row["min_budget_stress_margin"]) for row in rows)
            route = rows[0]["validation_cover_route"]
            pass_guard = scheme_count == 3 and positive_votes == scheme_count and min_slack >= 0.015
            writer.writerow(
                {
                    "experiment": experiment,
                    "stability_scheme_count": scheme_count,
                    "positive_scheme_votes": positive_votes,
                    "required_scheme_votes": scheme_count,
                    "min_bootstrap_sensitivity_slack_floor": f"{min_slack:.12g}",
                    "min_bootstrap_heldout_delta_floor": f"{min_heldout:.12g}",
                    "min_budget_stress_margin": f"{min_budget:.6f}",
                    "validation_cover_route": route,
                    "concordance_status": "concordance_guard_pass" if pass_guard else "concordance_guard_fail",
                    "interpretation": "Three-scheme concordance guard for finite sampled neural rows; not an analytic full-domain neural certificate.",
                }
            )
    print(f"wrote {OUT.relative_to(ROOT)} rows={len(by_experiment)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
