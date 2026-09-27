#!/usr/bin/env python3
"""Compute bottleneck stress frontiers for large neural guard rows.

The R75 bounded-composition audit verifies that the compact-domain neural
guard chain passes.  This companion diagnostic asks a different question:
which already-audited constraint is closest to failure, and by what
multiplier?  It is a deterministic frontier over submitted finite artifacts,
not an unrestricted neural-network interval proof.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "neural_guard_stress_frontier_audit.csv"

SCENARIOS = (
    "current_cover",
    "cover_refinement_half_radius",
    "refined_cover_slope_stress_1p10x",
)


def read_rows(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="") as fh:
        return list(csv.DictReader(fh))


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


def frontier(threshold: float, score: float) -> float:
    if score <= 0.0:
        return float("inf")
    return threshold / score


def main() -> int:
    refinement_rows = read_rows("neural_guard_refinement_stress_audit.csv")
    envelope_rows = {row["experiment"]: row for row in read_rows("neural_bounded_composition_envelope_certificate.csv")}
    budget_rows = read_rows("bounded_architecture_budget_stress_audit.csv")

    budget_frontiers = [
        frontier(float(row["threshold"]), float(row["stressed_budget_product"]))
        for row in budget_rows
        if row["stress_status"] == "budget_stress_guard_pass"
    ]
    min_budget_frontier = min(budget_frontiers)

    rows: list[dict[str, Any]] = []
    experiments = sorted({row["experiment"] for row in refinement_rows})
    for experiment in experiments:
        by_scenario = {
            row["scenario"]: row
            for row in refinement_rows
            if row["experiment"] == experiment
        }
        missing = sorted(set(SCENARIOS) - set(by_scenario))
        if missing:
            raise ValueError(f"{experiment} missing scenarios: {missing}")

        current = by_scenario["current_cover"]
        half = by_scenario["cover_refinement_half_radius"]
        refined_slope = by_scenario["refined_cover_slope_stress_1p10x"]
        env = envelope_rows[experiment]

        current_score = float(current["adjusted_interval_sensitivity_score"])
        current_threshold = float(current["sensitivity_threshold"])
        half_score = float(half["adjusted_interval_sensitivity_score"])
        refined_slope_score = float(refined_slope["adjusted_interval_sensitivity_score"])
        composed_score = float(env["composed_envelope_score"])
        composed_threshold = float(env["composed_envelope_threshold"])

        current_frontier = frontier(current_threshold, current_score)
        half_frontier = frontier(float(half["sensitivity_threshold"]), half_score)
        refined_slope_frontier = frontier(float(refined_slope["sensitivity_threshold"]), refined_slope_score)
        refined_sensitivity_frontier = min(half_frontier, refined_slope_frontier)
        composed_frontier = frontier(composed_threshold, composed_score)
        current_limiter = min(current_frontier, min_budget_frontier)
        refined_limiter = min(refined_sensitivity_frontier, min_budget_frontier)

        if current_frontier <= min_budget_frontier:
            active_current_constraint = "current_cover_sensitivity"
        else:
            active_current_constraint = "bounded_budget_stress"
        if refined_sensitivity_frontier <= min_budget_frontier:
            active_refined_constraint = "refined_cover_sensitivity"
        else:
            active_refined_constraint = "bounded_budget_stress"

        guards = [
            current["refinement_stress_status"] == "refinement_stress_guard_pass",
            half["refinement_stress_status"] == "refinement_stress_guard_pass",
            refined_slope["refinement_stress_status"] == "refinement_stress_guard_pass",
            env["bounded_composition_status"] == "bounded_composition_envelope_pass",
            current_frontier > 1.0,
            half_frontier > 1.0,
            refined_slope_frontier > 1.0,
            min_budget_frontier > 1.0,
            composed_frontier > 1.0,
            current["validation_cover_route"] == "validation-cover_not_global_lipschitz",
        ]

        rows.append(
            {
                "experiment": experiment,
                "current_cover_sensitivity_score": fmt(current_score),
                "current_cover_sensitivity_threshold": fmt(current_threshold),
                "current_cover_sensitivity_frontier_multiplier": fmt(current_frontier),
                "half_radius_sensitivity_frontier_multiplier": fmt(half_frontier),
                "refined_cover_slope_frontier_multiplier": fmt(refined_slope_frontier),
                "refined_sensitivity_frontier_multiplier": fmt(refined_sensitivity_frontier),
                "bounded_budget_frontier_multiplier": fmt(min_budget_frontier),
                "composed_envelope_frontier_multiplier": fmt(composed_frontier),
                "current_limited_frontier_multiplier": fmt(current_limiter),
                "refined_limited_frontier_multiplier": fmt(refined_limiter),
                "active_current_constraint": active_current_constraint,
                "active_refined_constraint": active_refined_constraint,
                "guard_route": "validation-cover_not_global_lipschitz",
                "frontier_status": "stress_frontier_guard_pass" if all(guards) else "stress_frontier_guard_fail",
                "theorem_anchor": "Corollary neural_guard_stress_frontier",
                "interpretation": "Deterministic bottleneck frontier over submitted compact-domain neural guard artifacts; quantifies finite guard slack and is not an unrestricted analytic full-domain neural certificate.",
            }
        )

    write_csv(OUT, rows)
    print(f"wrote {OUT.relative_to(ROOT)} rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
