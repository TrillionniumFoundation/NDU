#!/usr/bin/env python3
"""Compose bounded neural guard artifacts into a compact-domain envelope.

This is a deterministic artifact-level certificate over the declared clipped
implementation domain.  It joins the interval expansion, sensitivity stress,
bounded-architecture budget, stress-margin, concordance, and leave-one-out
guards.  It is not an unrestricted full-domain neural Lipschitz proof.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "neural_bounded_composition_envelope_certificate.csv"


THRESHOLDS = {
    "exp1_habit_portfolio": 5.0,
    "inventory_service_level": 10.0,
}


def read_rows(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="") as fh:
        return list(csv.DictReader(fh))


def by_experiment(name: str) -> dict[str, dict[str, str]]:
    return {row["experiment"]: row for row in read_rows(name)}


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


def fmt(value: float) -> str:
    return f"{value:.12g}"


def main() -> int:
    interval = by_experiment("neural_interval_domain_certificate.csv")
    sensitivity = read_rows("neural_interval_sensitivity_audit.csv")
    budget = read_rows("bounded_architecture_lipschitz_budget_audit.csv")
    stress = read_rows("bounded_architecture_budget_stress_audit.csv")
    concordance = by_experiment("neural_guard_concordance_audit.csv")
    leave_one_out = read_rows("neural_guard_leave_one_out_robustness_audit.csv")

    component_count = len({row["component"] for row in budget})
    stress_scenario_count = len({row["scenario"] for row in stress})
    max_budget_product = max(float(row["budget_product"]) for row in budget)
    max_stressed_budget_product = max(float(row["stressed_budget_product"]) for row in stress)
    min_budget_stress_margin = min(float(row["margin"]) for row in stress)

    rows: list[dict[str, Any]] = []
    for experiment, threshold in THRESHOLDS.items():
        int_row = interval[experiment]
        sens_rows = [row for row in sensitivity if row["experiment"] == experiment]
        loo_rows = [row for row in leave_one_out if row["experiment"] == experiment]
        conc_row = concordance[experiment]

        max_sensitivity_score = max(float(row["sensitivity_score"]) for row in sens_rows)
        min_sensitivity_margin = min(float(row["sensitivity_threshold"]) - float(row["sensitivity_score"]) for row in sens_rows)
        min_refinement_slack = min(float(row["min_refinement_slack"]) for row in loo_rows)
        min_holdout_slack = min(float(row["min_holdout_slack"]) for row in loo_rows)
        min_heldout_delta = min(float(row["min_heldout_delta"]) for row in loo_rows)
        min_loo_stress_margin = min(float(row["min_budget_stress_margin"]) for row in loo_rows)
        omitted_guard_families = sorted({row["omitted_guard_family"] for row in loo_rows})

        # The score composes the interval/sensitivity score with the worst
        # bounded-architecture stress budget.  It is a deterministic audit score,
        # not a value-loss claim.
        composed_score = max_sensitivity_score + 0.01 * max_stressed_budget_product
        composed_margin = threshold - composed_score

        guards = [
            int(int_row["all_interval_guards_pass"]) == 1,
            all(row["sensitivity_status"] == "interval_sensitivity_guard_pass" for row in sens_rows),
            all(row["status"] == "budget_recorded" for row in budget),
            all(row["stress_status"] == "budget_stress_guard_pass" for row in stress),
            conc_row["concordance_status"] == "concordance_guard_pass",
            all(row["robustness_status"] == "leave_one_out_guard_pass" for row in loo_rows),
            composed_margin > 0.0,
            min_sensitivity_margin > 0.0,
            min_budget_stress_margin > 0.0,
            min_refinement_slack > 0.0,
            min_holdout_slack > 0.0,
            min_heldout_delta >= 0.0,
        ]

        rows.append(
            {
                "experiment": experiment,
                "validation_pairs": int_row["validation_pairs"],
                "validation_density_proxy": int_row["validation_density_proxy"],
                "cover_radius_proxy": int_row["cover_radius_proxy"],
                "component_count": component_count,
                "stress_scenario_count": stress_scenario_count,
                "omitted_guard_family_count": len(omitted_guard_families),
                "leave_one_out_rows": len(loo_rows),
                "max_budget_product": fmt(max_budget_product),
                "max_stressed_budget_product": fmt(max_stressed_budget_product),
                "min_budget_stress_margin": fmt(min_budget_stress_margin),
                "max_sensitivity_score": fmt(max_sensitivity_score),
                "min_sensitivity_margin": fmt(min_sensitivity_margin),
                "min_refinement_slack": fmt(min_refinement_slack),
                "min_holdout_slack": fmt(min_holdout_slack),
                "min_heldout_delta": fmt(min_heldout_delta),
                "min_leave_one_out_stress_margin": fmt(min_loo_stress_margin),
                "composed_envelope_score": fmt(composed_score),
                "composed_envelope_threshold": fmt(threshold),
                "composed_envelope_margin": fmt(composed_margin),
                "guard_route": "validation-cover_not_global_lipschitz",
                "certificate_route": "bounded-composition_compact-domain_global-envelope_not_unrestricted",
                "bounded_composition_status": "bounded_composition_envelope_pass" if all(guards) else "bounded_composition_envelope_fail",
                "theorem_anchor": "Corollary bounded_composition_global_envelope",
                "source_guard_families": "|".join(omitted_guard_families),
                "interpretation": "Deterministic compact-domain global envelope over declared clipped implementation, interval, stress, concordance, and leave-one-out guards; not an unrestricted analytic full-domain neural certificate.",
            }
        )

    write_csv(OUT, rows)
    print(f"wrote {OUT.relative_to(ROOT)} rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
