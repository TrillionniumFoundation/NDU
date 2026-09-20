#!/usr/bin/env python3
"""Audit that NDU does not collapse to a fixed-preference/action-only RL re-description.

The theorem-level issue is simple: fixed-preference RL embeds as a frozen
valuation face, but if the full valuation-control face attains a strictly larger
Bellman value under the same information/evaluator, no fixed-preference or
frozen-valuation action-only policy in that benchmark can be value-equivalent.
This script collects the exact-DP and same-information rollout guards that make
that non-collapse claim reproducible.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "generalized_rl_noncollapse_audit.csv"


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="") as fh:
        return list(csv.DictReader(fh))


def fmt(x: float) -> str:
    return f"{x:.12g}"


def row(**kwargs: object) -> dict[str, object]:
    return kwargs


def main() -> int:
    exact_policy = {r["method"]: r for r in read_csv("inventory_exact_policy_class_dp_metrics.csv")}
    exact_mdp = {r["method"]: r for r in read_csv("inventory_exact_valuation_control_mdp_metrics.csv")}
    finite = {r["method"]: r for r in read_csv("inventory_finite_cover_hjb_certificate.csv")}
    same_budget = {r["experiment"]: r for r in read_csv("same_budget_parameter_controlled_audit.csv")}
    same_budget_metrics = {(r["experiment"], r["method"]): r for r in read_csv("same_budget_parameter_controlled_metrics.csv")}
    selected_exp3 = next(
        r for r in read_csv("hbo_exp3_parity_closing_audit.csv")
        if r["config"] == "default_safe_steps1500" and r["method"] == "paired_gap_full_minus_fixed"
    )
    nbo = {r["benchmark"]: r for r in read_csv("nbo_full_ndu_solver_audit.csv")}

    full = exact_policy["full_valuation_control_exact_dp"]
    action = exact_policy["action_only_exact_dp"]
    valuation = exact_policy["valuation_only_exact_dp"]
    full_avg = float(full["expected_avg_welfare"])
    action_avg = float(action["expected_avg_welfare"])
    valuation_avg = float(valuation["expected_avg_welfare"])
    exact_margin_action = full_avg - action_avg
    exact_margin_best_face = full_avg - max(action_avg, valuation_avg)

    mdp_full = exact_mdp["exact_dp_full_order_and_valuation_control"]
    mdp_action = exact_mdp["exact_dp_action_only_fixed_theta"]
    mdp_margin = float(mdp_full["expected_avg_welfare"]) - float(mdp_action["expected_avg_welfare"])
    theta_free_cost_gap = abs(float(mdp_full["theta_free_expected_avg_cost"]) - float(mdp_action["theta_free_expected_avg_cost"]))

    finite_full = finite["full_valuation_control_exact_dp"]
    finite_bound = float(finite_full["finite_cover_certificate_bound"])
    finite_margin = float(finite_full["margin_vs_action_only_avg"])
    contains_faces = int(finite_full["contains_action_only_face"]) == 1 and int(finite_full["contains_valuation_only_face"]) == 1

    exp1_same = float(same_budget["exp1"]["full_minus_best_non_ndu"])
    exp2_same_abs = abs(float(same_budget["exp2"]["full_minus_best_non_ndu"]))
    exp3_feasible = float(same_budget_metrics[("exp3", "full_ndu_joint")]["mean_utility"]) - float(same_budget_metrics[("exp3", "same_dim_fixed_pref_joint_rl")]["mean_utility"])
    exp3_selected = float(selected_exp3["mean_utility"])

    nbo_exp1 = float(nbo["exp1_habit_portfolio"]["full_minus_comparator_paired"])
    nbo_exp2 = float(nbo["exp2_hidden_regime"]["full_minus_comparator_paired"])
    nbo_inventory = float(nbo["inventory_service_level"]["full_minus_comparator_paired"])

    rows = [
        row(
            noncollapse_claim="exact_policy_class_value_separation",
            theorem_anchor="Corollary noncollapse_under_positive_valuation_control_margin",
            evidence_sources="inventory_exact_policy_class_dp_metrics.csv",
            observed_guard=f"full_minus_action={fmt(exact_margin_action)}; full_minus_best_single_channel_face={fmt(exact_margin_best_face)}",
            required_guard="full_minus_action > 0.19 and full_minus_best_single_channel_face > 0.12",
            status="noncollapse_guard_pass" if exact_margin_action > 0.19 and exact_margin_best_face > 0.12 else "noncollapse_guard_gap",
            interpretation="The exact nested policy-class DP contains the frozen action-only face and still gives a strict Full valuation-control value margin, so the benchmark cannot be value-equivalent to fixed-preference/action-only RL.",
        ),
        row(
            noncollapse_claim="exact_valuation_state_mdp_value_separation",
            theorem_anchor="Corollary noncollapse_under_positive_valuation_control_margin",
            evidence_sources="inventory_exact_valuation_control_mdp_metrics.csv",
            observed_guard=f"full_minus_action={fmt(mdp_margin)}; theta_free_cost_gap={fmt(theta_free_cost_gap)}",
            required_guard="full_minus_action > 0.015 and theta_free_cost_gap < 1e-10",
            status="noncollapse_guard_pass" if mdp_margin > 0.015 and theta_free_cost_gap < 1e-10 else "noncollapse_guard_gap",
            interpretation="The exact valuation-state MDP improves valuation welfare over the frozen-theta action-only row while keeping the theta-free physical cost identical in the audited instance.",
        ),
        row(
            noncollapse_claim="finite_cover_certificate_value_separation",
            theorem_anchor="Finite-cover Bellman--HJB certificate + noncollapse corollary",
            evidence_sources="inventory_finite_cover_hjb_certificate.csv",
            observed_guard=f"finite_bound={fmt(finite_bound)}; full_minus_action={fmt(finite_margin)}; contains_both_faces={int(contains_faces)}",
            required_guard="finite_bound = 0, full_minus_action > 0.19, and both frozen faces contained",
            status="noncollapse_guard_pass" if finite_bound == 0.0 and finite_margin > 0.19 and contains_faces else "noncollapse_guard_gap",
            interpretation="The zero-gap finite-cover Bellman solve proves the strict Full margin on a cover that explicitly contains the action-only and valuation-only faces.",
        ),
        row(
            noncollapse_claim="same_information_budget_noncollapse",
            theorem_anchor="Protocol matrix + noncollapse corollary",
            evidence_sources="same_budget_parameter_controlled_audit.csv + hbo_exp3_parity_closing_audit.csv",
            observed_guard=f"exp1={fmt(exp1_same)}; exp2_abs={fmt(exp2_same_abs)}; exp3_feasible={fmt(exp3_feasible)}; selected_exp3={fmt(exp3_selected)}",
            required_guard="Exp I positive, Exp II parity, Exp III feasible/selected positive",
            status="noncollapse_guard_pass" if exp1_same > 0.02 and exp2_same_abs < 2e-6 and exp3_feasible > 0.01 and exp3_selected > 0 else "noncollapse_guard_gap",
            interpretation="Same-information and same-budget rollout rows separate the Full valuation-control class from feasible fixed-preference comparators or document practical parity where the benchmark is not strict.",
        ),
        row(
            noncollapse_claim="source_nbo_rollout_noncollapse",
            theorem_anchor="NBO HJB-solver certificate + noncollapse corollary",
            evidence_sources="nbo_full_ndu_solver_audit.csv",
            observed_guard=f"exp1={fmt(nbo_exp1)}; exp2={fmt(nbo_exp2)}; inventory={fmt(nbo_inventory)}",
            required_guard="Exp I and inventory positive with Exp II nonnegative",
            status="noncollapse_guard_pass" if nbo_exp1 > 0 and nbo_exp2 >= 0 and nbo_inventory > 0 else "noncollapse_guard_gap",
            interpretation="The PyTorch-AD HBO/NBO rollout audit shows positive held-out Full-minus-fixed/action-only margins on the main strict benchmarks, with Exp II a small positive same-information gain.",
        ),
    ]

    fields = ["noncollapse_claim", "theorem_anchor", "evidence_sources", "observed_guard", "required_guard", "status", "interpretation"]
    with OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
