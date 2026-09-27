#!/usr/bin/env python3
"""Build a deterministic stress-margin audit for bounded architecture budgets.

The audit perturbs the implementation-level Lipschitz/compactness budget by
fixed slope and radius multipliers.  It is not a full-domain neural Lipschitz
certificate; it checks that the recorded finite-budget controls retain positive
margin under named stress scenarios.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "bounded_architecture_budget_stress_audit.csv"


BASE_ROWS = [
    ("state_feature_clipping", 5.00),
    ("actor_tanh_control_map", 1.00),
    ("preference_sigmoid_map", 0.25),
    ("belief_simplex_clip", 1.10),
    ("portfolio_l1_normalization", 2.00),
    ("value_mlp_gradient_clip", 7.50),
    ("cem_variance_cap", 2.80),
]

SCENARIOS = [
    ("nominal_budget", 1.00, 1.00, 12.0),
    ("slope_stress_1p25x", 1.25, 1.00, 12.0),
    ("radius_stress_1p50x", 1.00, 1.50, 12.0),
]


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "component",
        "scenario",
        "base_budget_product",
        "slope_multiplier",
        "radius_multiplier",
        "stressed_budget_product",
        "threshold",
        "margin",
        "stress_status",
        "interpretation",
    ]
    with OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for component, base_budget in BASE_ROWS:
            for scenario, slope_multiplier, radius_multiplier, threshold in SCENARIOS:
                stressed = base_budget * slope_multiplier * radius_multiplier
                margin = threshold - stressed
                writer.writerow(
                    {
                        "component": component,
                        "scenario": scenario,
                        "base_budget_product": f"{base_budget:.6f}",
                        "slope_multiplier": f"{slope_multiplier:.6f}",
                        "radius_multiplier": f"{radius_multiplier:.6f}",
                        "stressed_budget_product": f"{stressed:.6f}",
                        "threshold": f"{threshold:.6f}",
                        "margin": f"{margin:.6f}",
                        "stress_status": "budget_stress_guard_pass" if margin > 0.0 else "budget_stress_guard_fail",
                        "interpretation": "finite implementation budget keeps positive stress margin under this deterministic perturbation",
                    }
                )
    print(f"wrote {OUT.relative_to(ROOT)} rows={len(BASE_ROWS) * len(SCENARIOS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
