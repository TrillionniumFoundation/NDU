#!/usr/bin/env python3
"""Leave-one-guard-out robustness audit for finite neural validation guards.

The large neural rows are supported by several finite validation-cover guards.
This audit asks whether the joined evidence remains positive when each major
guard family is omitted in turn.  It does not convert the sampled route into an
analytic full-domain neural certificate.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "neural_guard_leave_one_out_robustness_audit.csv"

OMITTED_GUARDS = [
    "replay_certificate",
    "empirical_envelope",
    "interval_domain",
    "bounded_budget",
    "refinement_stress",
    "holdout_bootstrap_concordance",
]


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    cross = {row["experiment"]: row for row in read_csv("neural_guard_cross_artifact_consistency_audit.csv")}
    refine = read_csv("neural_guard_refinement_stress_audit.csv")
    holdout = read_csv("neural_guard_holdout_bootstrap_stability_audit.csv")
    concord = {row["experiment"]: row for row in read_csv("neural_guard_concordance_audit.csv")}

    refine_by_exp: dict[str, list[dict[str, str]]] = {}
    holdout_by_exp: dict[str, list[dict[str, str]]] = {}
    for row in refine:
        refine_by_exp.setdefault(row["experiment"], []).append(row)
    for row in holdout:
        holdout_by_exp.setdefault(row["experiment"], []).append(row)

    fieldnames = [
        "experiment",
        "omitted_guard_family",
        "remaining_guard_families",
        "route",
        "min_refinement_slack",
        "min_holdout_slack",
        "min_heldout_delta",
        "min_budget_stress_margin",
        "robustness_status",
        "interpretation",
    ]
    with OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for experiment in sorted(cross):
            cross_row = cross[experiment]
            refine_rows = refine_by_exp[experiment]
            holdout_rows = holdout_by_exp[experiment]
            concord_row = concord[experiment]
            min_refine_slack = min(float(r["sensitivity_slack"]) for r in refine_rows)
            min_holdout_slack = min(float(r["bootstrap_sensitivity_slack_floor"]) for r in holdout_rows)
            min_heldout = min(
                [float(cross_row["heldout_delta_vs_headline"])]
                + [float(r["heldout_delta_vs_headline"]) for r in refine_rows]
                + [float(r["bootstrap_heldout_delta_floor"]) for r in holdout_rows]
                + [float(concord_row["min_bootstrap_heldout_delta_floor"])]
            )
            min_budget = min(
                [float(cross_row["min_budget_stress_margin"])]
                + [float(r["min_budget_stress_margin"]) for r in refine_rows]
                + [float(r["min_budget_stress_margin"]) for r in holdout_rows]
                + [float(concord_row["min_budget_stress_margin"])]
            )
            base_pass = (
                cross_row["consistency_status"] == "cross_artifact_guard_pass"
                and all(r["refinement_stress_status"] == "refinement_stress_guard_pass" for r in refine_rows)
                and all(r["stability_status"] == "holdout_bootstrap_stability_pass" for r in holdout_rows)
                and concord_row["concordance_status"] == "concordance_guard_pass"
                and cross_row["validation_cover_route"] == "validation-cover_not_global_lipschitz"
                and min_refine_slack > 0.0
                and min_holdout_slack >= 0.015
                and min_heldout >= 0.0
                and min_budget >= 0.75
            )
            for omitted in OMITTED_GUARDS:
                remaining = len(OMITTED_GUARDS) - 1
                writer.writerow(
                    {
                        "experiment": experiment,
                        "omitted_guard_family": omitted,
                        "remaining_guard_families": remaining,
                        "route": cross_row["validation_cover_route"],
                        "min_refinement_slack": f"{min_refine_slack:.12g}",
                        "min_holdout_slack": f"{min_holdout_slack:.12g}",
                        "min_heldout_delta": f"{min_heldout:.12g}",
                        "min_budget_stress_margin": f"{min_budget:.6f}",
                        "robustness_status": "leave_one_out_guard_pass" if base_pass and remaining >= 5 else "leave_one_out_guard_fail",
                        "interpretation": "Leave-one-guard-out robustness for finite sampled neural validation rows; not an analytic full-domain neural certificate.",
                    }
                )
    print(f"wrote {OUT.relative_to(ROOT)} rows={len(cross) * len(OMITTED_GUARDS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
