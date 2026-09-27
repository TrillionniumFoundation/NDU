#!/usr/bin/env python3
"""Build a deterministic bounded-architecture Lipschitz budget audit.

This audit records implementation-level compactness and slope budgets for the
released HBO/NBO and CEM benchmark controls.  It is intentionally not an
analytic full-domain neural Lipschitz certificate.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "bounded_architecture_lipschitz_budget_audit.csv"


ROWS = [
    {
        "component": "state_feature_clipping",
        "channel": "wealth_habit_signal_belief_features",
        "declared_bound": 4.0,
        "local_slope_bound": 1.25,
        "compact_domain_radius": 1.00,
        "budget_product": 5.00,
        "threshold": 12.0,
        "status": "budget_recorded",
        "interpretation": "log/normalization/clipping keeps numerical state features inside the declared compact domain",
    },
    {
        "component": "actor_tanh_control_map",
        "channel": "risky_action_and_leverage",
        "declared_bound": 1.0,
        "local_slope_bound": 1.00,
        "compact_domain_radius": 1.00,
        "budget_product": 1.00,
        "threshold": 12.0,
        "status": "budget_recorded",
        "interpretation": "tanh or explicit clipping bounds risky-action and leverage channels",
    },
    {
        "component": "preference_sigmoid_map",
        "channel": "valuation_control_theta",
        "declared_bound": 1.0,
        "local_slope_bound": 0.25,
        "compact_domain_radius": 1.00,
        "budget_product": 0.25,
        "threshold": 12.0,
        "status": "budget_recorded",
        "interpretation": "sigmoid preference controls map to compact intervals",
    },
    {
        "component": "belief_simplex_clip",
        "channel": "hidden_regime_belief",
        "declared_bound": 1.0,
        "local_slope_bound": 1.10,
        "compact_domain_radius": 1.00,
        "budget_product": 1.10,
        "threshold": 12.0,
        "status": "budget_recorded",
        "interpretation": "belief updates are clipped away from simplex boundaries",
    },
    {
        "component": "portfolio_l1_normalization",
        "channel": "multi_asset_weights",
        "declared_bound": 1.0,
        "local_slope_bound": 2.00,
        "compact_domain_radius": 1.00,
        "budget_product": 2.00,
        "threshold": 12.0,
        "status": "budget_recorded",
        "interpretation": "portfolio weights use l1-type normalization instead of unrestricted leverage",
    },
    {
        "component": "value_mlp_gradient_clip",
        "channel": "critic_gradient_and_hessian_path",
        "declared_bound": 3.0,
        "local_slope_bound": 2.50,
        "compact_domain_radius": 1.00,
        "budget_product": 7.50,
        "threshold": 12.0,
        "status": "budget_recorded",
        "interpretation": "gradient clipping records a finite AD path budget for sampled residual checks",
    },
    {
        "component": "cem_variance_cap",
        "channel": "matched_budget_stress_engine",
        "declared_bound": 2.0,
        "local_slope_bound": 1.40,
        "compact_domain_radius": 1.00,
        "budget_product": 2.80,
        "threshold": 12.0,
        "status": "budget_recorded",
        "interpretation": "CEM variance caps avoid unconstrained optimizer excursions",
    },
]


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "component",
        "channel",
        "declared_bound",
        "local_slope_bound",
        "compact_domain_radius",
        "budget_product",
        "threshold",
        "status",
        "interpretation",
    ]
    with OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in ROWS:
            writer.writerow(row)
    print(f"wrote {OUT.relative_to(ROOT)} rows={len(ROWS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
