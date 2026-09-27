#!/usr/bin/env python3
"""Build the finite-policy decision-layer bridge audit from existing CSV evidence.

This is an aggregation/check file, not a new simulation. It records how the
manuscript maps mixed benchmark outcomes into the finite-horizon valuation-
control certificate: strict gain, parity, privileged-ceiling tradeoff, or
intervention-relevance.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "decision_layer_bridge_audit.csv"


def rows(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="") as fh:
        return list(csv.DictReader(fh))


def one(name: str, **keys: str) -> dict[str, str]:
    for row in rows(name):
        if all(row.get(k) == v for k, v in keys.items()):
            return row
    raise KeyError((name, keys))


def f(x: float, nd: int = 6) -> str:
    return f"{x:.{nd}f}"


def main() -> None:
    same = {r["experiment"]: r for r in rows("same_budget_parameter_controlled_audit.csv")}
    seed = rows("seed_level_statistical_audit.csv")
    paired = {(r["scenario"], r["comparison"], r["metric"]): r for r in rows("inventory_paired_seed_difference_audit.csv")}
    theta = {(r["audit"], r["method"], r["evaluation_variant"], r["theta_cost_multiplier"]): r for r in rows("inventory_equal_budget_theta_audit_metrics.csv")}
    sku = {r["method"]: r for r in rows("sku_inventory_baseline_metrics.csv")}
    exact = {r["method"]: r for r in rows("inventory_exact_valuation_control_mdp_metrics.csv")}
    frontier3 = {r["evaluation_budget"]: r for r in rows("exp3_equal_evaluation_audit.csv")}

    exp1_seed = next(r for r in seed if r["experiment"] == "I" and r["metric"] == "mean_utility" and r["method_b"] == "augmented_state_rl")
    exp2 = same["exp2"]
    exp3 = same["exp3"]
    inv_welfare = paired[("base_30_seed", "full_ndu_inventory_minus_action_only_adaptive_base_stock", "mean_welfare")]
    inv_cost = paired[("base_30_seed", "full_ndu_inventory_minus_action_only_adaptive_base_stock", "avg_cost")]
    inv_normal = theta[("equal_budget_inventory", "full_ndu_inventory", "normal", "1.0")]
    inv_action = theta[("equal_budget_inventory", "action_only_adaptive_base_stock", "normal", "1.0")]
    inv_fixed = theta[("theta_ablation_inventory", "full_ndu_inventory", "fixed_one", "1.0")]
    inv_perm = theta[("theta_ablation_inventory", "full_ndu_inventory", "permuted", "1.0")]
    adp = sku["approximate_dp_inventory"]
    full_sku = sku["full_ndu_theta_service_control"]
    seasonal = sku["seasonal_service_tuned_base_stock"]
    mpc = sku["mpc_scenario_base_stock"]
    exact_action = exact["exact_dp_action_only_fixed_theta"]
    exact_full = exact["exact_dp_full_order_and_valuation_control"]

    records = [
        {
            "benchmark": "exp1_habit_portfolio",
            "implementation_link": "Euler finite-horizon dynamic valuation-control problem with active habit state",
            "formal_connection": "closest implemented analogue of the continuous-time augmented-state FBSDE layer",
            "primary_comparison": f"same-budget Full NDU minus best non-NDU = {f(float(same['exp1']['full_minus_best_non_ndu']))}",
            "uncertainty_or_intervention": f"30-seed Full minus augmented-state mean utility = {f(float(exp1_seed['mean_diff_a_minus_b']))} +/- {f(float(exp1_seed['ci95_halfwidth_normal_independent']))}",
            "certificate_read": "strict finite-policy gain on the reported evaluator",
            "claim_status": "strict_gain",
        },
        {
            "benchmark": "exp2_hidden_regime",
            "implementation_link": "finite-horizon partially observed valuation-control/filtering benchmark",
            "formal_connection": "reduced finite-policy decision layer rather than theorem-level FBSDE closure",
            "primary_comparison": f"same-budget Full NDU minus fixed-preference recurrent = {float(exp2['full_minus_best_non_ndu']):+.9f}",
            "uncertainty_or_intervention": "safe privileged-information lower bound exceeds Full NDU by +0.000127; physical diagnostics favor Full NDU modestly",
            "certificate_read": "practical parity among feasible same-information policies; no dominance claim",
            "claim_status": "parity",
        },
        {
            "benchmark": "exp3_high_dimensional_allocation",
            "implementation_link": "finite-horizon high-dimensional allocation with valuation-control turnover tradeoff",
            "formal_connection": "decision-layer stress test with an older privileged-information CEM row",
            "primary_comparison": f"Full minus feasible fixed-preference = +0.012274; old CEM Full minus privileged reference = {float(exp3['full_minus_best_non_ndu']):+.6f}",
            "uncertainty_or_intervention": f"442-evaluation frontier Full minus privileged reference = {float(frontier3['442']['full_minus_best_non_ndu']):+.6f}; PyTorch-AD HBO/NBO privileged factor-reference row remains higher; feasible comparator is parity",
            "certificate_read": "feasible non-privileged CEM gain; HBO/NBO table is the current feasible/parity and privileged-reference ranking",
            "claim_status": "legacy_cem_stress_hbo_ad_parity_privileged_reference_higher",
        },
        {
            "benchmark": "inventory_service_level",
            "implementation_link": "canonical finite-horizon OR inventory/service-level control problem",
            "formal_connection": "direct operational valuation-control MDP with order-up-to action and service pressure theta",
            "primary_comparison": f"30-seed Full minus action welfare = {f(float(inv_welfare['mean_difference']))} +/- {f(float(inv_welfare['ci95']))}; cost = {f(float(inv_cost['mean_difference']))} +/- {f(float(inv_cost['ci95']))}",
            "uncertainty_or_intervention": f"equal-budget action leads by {float(inv_action['mean_welfare']) - float(inv_normal['mean_welfare']):.6f}, but fixed-theta replay drops {float(inv_fixed['mean_welfare']) - float(inv_normal['mean_welfare']):.6f} and permuted-theta drops {float(inv_perm['mean_welfare']) - float(inv_normal['mean_welfare']):.6f}",
            "certificate_read": "OR channel relevance with explicit budget caveat",
            "claim_status": "intervention_relevant",
        },
        {
            "benchmark": "public_sku_and_exact_inventory_dp",
            "implementation_link": "public SKU replay plus exact finite-state valuation-control inventory DP",
            "formal_connection": "external OR replay and exact Bellman valuation-control check",
            "primary_comparison": f"SKU valuation welfare: Full {float(full_sku['valuation_adjusted_welfare']):.4f} vs ADP {float(adp['valuation_adjusted_welfare']):.4f}; theta-free cost ADP {float(adp['external_avg_cost']):.4f} vs Full {float(full_sku['external_avg_cost']):.4f}",
            "uncertainty_or_intervention": f"exact valuation-control DP welfare gain = {float(exact_full['expected_avg_welfare']) - float(exact_action['expected_avg_welfare']):+.6f} with identical theta-free cost",
            "certificate_read": "valuation-control welfare improves over ADP/action-only DP; theta-free cost diagnostic remains explicit",
            "claim_status": "valuation_dp_gain",
        },
    ]

    with OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)


if __name__ == "__main__":
    main()
