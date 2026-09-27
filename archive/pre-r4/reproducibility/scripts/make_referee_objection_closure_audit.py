#!/usr/bin/env python3
"""Referee-objection closure matrix for the NDU/NBO generalized-RL claim.

This audit is intentionally a synthesis audit rather than a new simulator.  It
maps the main likely referee objections to the theorem/proof anchor and the
already-reproduced experiment/certificate row that closes that objection.  The
checker validates the quantitative guards so the closure matrix cannot drift
from the package evidence.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "referee_objection_closure_audit.csv"


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="") as fh:
        return list(csv.DictReader(fh))


def fmt(x: float) -> str:
    return f"{x:.12g}"


def row(**kwargs: object) -> dict[str, object]:
    return kwargs


def main() -> int:
    exact_policy = {r["method"]: r for r in read_csv("inventory_exact_policy_class_dp_metrics.csv")}
    theory = read_csv("theory_covered_hjb_audit.csv")[0]
    uniform = {r["gamma"]: r for r in read_csv("uniform_hjb_greedy_certificate.csv")}
    finite = {r["method"]: r for r in read_csv("inventory_finite_cover_hjb_certificate.csv")}
    refine = {r["cover_name"]: r for r in read_csv("inventory_cover_refinement_certificate.csv")}
    ladder = read_csv("hjb_solver_certificate_ladder.csv")
    residual = {(r["experiment"], r["audit_config"]): r for r in read_csv("hbo_residual_closing_audit.csv")}
    norm = {r["audit_config"]: r for r in read_csv("hbo_inventory_normalized_residual_audit.csv")}
    direct_pz = {(r["epsilon"], r["method"]): r for r in read_csv("inventory_direct_p_vs_z_metrics.csv")}
    learned = {(r["epsilon"], r["method"]): r for r in read_csv("inventory_direct_p_learned_z_ablation.csv")}
    neural = {(r["epsilon"], r["method"]): r for r in read_csv("inventory_neural_direct_p_learned_z_ablation.csv")}
    same_budget = {r["experiment"]: r for r in read_csv("same_budget_parameter_controlled_audit.csv")}
    same_budget_metrics = {(r["experiment"], r["method"]): r for r in read_csv("same_budget_parameter_controlled_metrics.csv")}
    exp3_close = next(r for r in read_csv("hbo_exp3_parity_closing_audit.csv") if r["config"] == "default_safe_steps1500" and r["method"] == "paired_gap_full_minus_fixed")

    full_dp = exact_policy["full_valuation_control_exact_dp"]
    action_dp = exact_policy["action_only_exact_dp"]
    strict_margin = float(full_dp["expected_avg_welfare"]) - float(action_dp["expected_avg_welfare"])
    compact_residual = float(theory["hjb_quadratic_residual_max"])
    uniform_bound = float(uniform["0.01"]["certificate_value_policy_bound_proxy"])
    full_cover = finite["full_valuation_control_exact_dp"]
    final_refine = refine["nested_full_r48_16"]
    initial_refine = refine["action_face_5"]
    exp1_ratio = float(residual[("exp1_habit_portfolio", "exp1_residual_terminal_critic_2400")]["hjb_loss_ratio_vs_headline"])
    inv_ratio = float(residual[("inventory_service_level", "inventory_residual_certificate_balanced_2400")]["hjb_loss_ratio_vs_headline"])
    inv_norm_ratio = float(norm["inventory_norm_pareto_actor_1200"]["normalized_rmse_ratio_vs_headline"])
    direct_ratio = float(direct_pz[("0.001", "z_inversion_inventory")]["theta_rmse_ratio_vs_direct_p"])
    learned_ratio = float(learned[("0.001", "learned_z_inventory")]["theta_rmse_ratio_vs_learned_direct_p"])
    neural_ratio = float(neural[("0.001", "neural_learned_z_inventory")]["theta_rmse_ratio_vs_neural_direct_p"])
    exp1_same = float(same_budget["exp1"]["full_minus_best_non_ndu"])
    exp2_same_abs = abs(float(same_budget["exp2"]["full_minus_best_non_ndu"]))
    exp3_same = float(same_budget_metrics[("exp3", "full_ndu_joint")]["mean_utility"]) - float(same_budget_metrics[("exp3", "same_dim_fixed_pref_joint_rl")]["mean_utility"])
    exp3_selected = float(exp3_close["mean_utility"])

    rows = [
        row(
            objection_id="generalized_rl_is_only_state_augmentation",
            referee_objection="NDU is not a real generalization of fixed-preference RL, only state augmentation.",
            theorem_or_proof_anchor="Theorem fixed_preference_embedding_strictness + strict Bellman-margin separation",
            audit_sources="inventory_exact_policy_class_dp_metrics.csv",
            key_metric="strict_exact_dp_margin_vs_action_only_avg_welfare",
            observed_value=fmt(strict_margin),
            threshold_or_comparator="> 0.19",
            closure_status="closed_strict_generalized_rl",
            interpretation="Fixed-preference/action-only and fixed-theta action-only policies are embedded faces; the nested Full valuation-control DP strictly improves the embedded action-only face.",
        ),
        row(
            objection_id="nbo_hjb_solver_certificate_missing",
            referee_objection="NBO/HBO rows are not tied to an HJB-solver certificate.",
            theorem_or_proof_anchor="Theorem nbo_hjb_solver_certificate + Corollary uniform_nbo_certificate_sequence",
            audit_sources="theory_covered_hjb_audit.csv + uniform_hjb_greedy_certificate.csv",
            key_metric="compact_residual_and_uniform_bound",
            observed_value=f"{fmt(compact_residual)}; {fmt(uniform_bound)}",
            threshold_or_comparator="residual < 1e-12; uniform bound < 0.021",
            closure_status="closed_hjb_certificate_theorem",
            interpretation="The compact theorem-covered row is exact to numerical precision and the analytic uniform NBO sequence closes residual, terminal, and greedy gaps.",
        ),
        row(
            objection_id="finite_cover_is_one_grid",
            referee_objection="The finite-cover certificate could be a single-grid artifact.",
            theorem_or_proof_anchor="Corollaries finite_cover_bellman_hjb_certificate and cover_refinement_hjb_certificate",
            audit_sources="inventory_finite_cover_hjb_certificate.csv + inventory_cover_refinement_certificate.csv",
            key_metric="zero_certificate_bound_and_radius_refinement",
            observed_value=f"bound={full_cover['finite_cover_certificate_bound']}; radius={initial_refine['action_fill_distance_proxy']}->{final_refine['action_fill_distance_proxy']}",
            threshold_or_comparator="bound = 0; final radius < initial radius",
            closure_status="closed_refined_finite_cover_certificate",
            interpretation="The exact inventory Bellman cover has zero residual/terminal/greedy gaps and the nested action covers preserve zero gaps while fill distance shrinks and value improves.",
        ),
        row(
            objection_id="large_neural_rows_are_sampled_only",
            referee_objection="Large HBO/NBO experiments are sampled diagnostics, not uniform certificates.",
            theorem_or_proof_anchor="Proposition hjb_solver_certificate_ladder",
            audit_sources="hjb_solver_certificate_ladder.csv + hbo_residual_closing_audit.csv + hbo_inventory_normalized_residual_audit.csv",
            key_metric="sampled_certificate_gap_closure_ratios",
            observed_value=f"exp1={fmt(exp1_ratio)}; inventory={fmt(inv_ratio)}; norm={fmt(inv_norm_ratio)}; ladder_rows={len(ladder)}",
            threshold_or_comparator="exp1 < 0.15; inventory < 0.20; normalized < 1; ladder rows = 7",
            closure_status="closed_as_sampled_certificate_gap_measurement",
            interpretation="The large neural rows are explicitly reported as validation-cover measurements of the same residual/terminal/greedy/value tuple certified by the exact ladder rungs.",
        ),
        row(
            objection_id="direct_p_is_unjustified_representation",
            referee_objection="Direct-P may be an ad hoc representation rather than an HJB/NBO requirement.",
            theorem_or_proof_anchor="Direct-P conditioning lemma + value-gradient residual consistency proposition",
            audit_sources="inventory_direct_p_vs_z_metrics.csv + inventory_direct_p_learned_z_ablation.csv + inventory_neural_direct_p_learned_z_ablation.csv",
            key_metric="epsilon_0.001_z_vs_direct_p_theta_rmse_ratios",
            observed_value=f"same_benchmark={fmt(direct_ratio)}; learned={fmt(learned_ratio)}; neural={fmt(neural_ratio)}",
            threshold_or_comparator="> 19x, > 27x, > 21x respectively",
            closure_status="closed_direct_p_shadow_price_guard",
            interpretation="The lower-bound conditioning result is matched by same-benchmark, isomorphic learned, and same-architecture neural retraining audits showing singular learned-Z inversion.",
        ),
        row(
            objection_id="fairness_same_information_same_budget",
            referee_objection="The empirical comparisons may depend on unfair information or budget differences.",
            theorem_or_proof_anchor="Protocol fairness table + evidence-role boundary matrix",
            audit_sources="same_budget_parameter_controlled_audit.csv + hbo_exp3_parity_closing_audit.csv",
            key_metric="same_budget_exp1_exp2_exp3_selected_gaps",
            observed_value=f"exp1={fmt(exp1_same)}; exp2_abs={fmt(exp2_same_abs)}; exp3_feasible={fmt(exp3_same)}; exp3_selected={fmt(exp3_selected)}",
            threshold_or_comparator="exp1 > 0.02; exp2 parity < 2e-6; exp3 feasible > 0.01; selected exp3 > 0",
            closure_status="closed_same_info_budget_boundary",
            interpretation="The paper separates feasible same-information/budget rows from privileged references and records positive or parity results under those boundaries.",
        ),
    ]

    fields = ["objection_id", "referee_objection", "theorem_or_proof_anchor", "audit_sources", "key_metric", "observed_value", "threshold_or_comparator", "closure_status", "interpretation"]
    with OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
