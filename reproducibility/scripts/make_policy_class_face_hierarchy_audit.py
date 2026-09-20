#!/usr/bin/env python3
"""Audit the strict policy-face hierarchy behind the generalized-RL claim.

The audit uses packaged exact Bellman solves and finite-cover certificates to
show that Full NDU is not only larger than action-only fixed-preference RL, but
strictly above all audited frozen/single-channel faces under the same evaluator.
This supports the theorem-level claim that NDU is a strict generalized RL class
with joint action/valuation control rather than a relabeled single-channel RL
model.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "policy_class_face_hierarchy_audit.csv"


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="") as fh:
        return list(csv.DictReader(fh))


def fmt(x: float) -> str:
    return f"{x:.12g}"


def row(**kwargs: object) -> dict[str, object]:
    return kwargs


def main() -> int:
    exact = {r["method"]: r for r in read_csv("inventory_exact_policy_class_dp_metrics.csv")}
    finite = {r["method"]: r for r in read_csv("inventory_finite_cover_hjb_certificate.csv")}
    refinement = read_csv("inventory_cover_refinement_certificate.csv")
    strong = read_csv("strong_form_generalized_rl_hjb_solver_claim_audit.csv")
    state_reward = read_csv("reward_shaping_state_augmentation_closure_audit.csv")

    action = exact["action_only_exact_dp"]
    valuation = exact["valuation_only_exact_dp"]
    full = exact["full_valuation_control_exact_dp"]
    action_w = float(action["expected_avg_welfare"])
    valuation_w = float(valuation["expected_avg_welfare"])
    full_w = float(full["expected_avg_welfare"])
    full_minus_action = full_w - action_w
    full_minus_valuation = full_w - valuation_w
    valuation_minus_action = valuation_w - action_w

    action_breaches = float(action["expected_service_breaches"])
    valuation_breaches = float(valuation["expected_service_breaches"])
    full_breaches = float(full["expected_service_breaches"])
    action_fill = float(action["fill_rate"])
    valuation_fill = float(valuation["fill_rate"])
    full_fill = float(full["fill_rate"])

    full_cover = finite["full_valuation_control_exact_dp"]
    action_cover = finite["action_only_exact_dp"]
    valuation_cover = finite["valuation_only_exact_dp"]
    zero_gaps = all(
        float(r["terminal_residual_sup"]) == 0.0 and
        float(r["bellman_residual_sup_abs"]) == 0.0 and
        float(r["greedy_gap_sup"]) == 0.0 and
        float(r["finite_cover_certificate_bound"]) == 0.0
        for r in (action_cover, valuation_cover, full_cover)
    )
    contains_faces = int(full_cover["contains_action_only_face"]) == 1 and int(full_cover["contains_valuation_only_face"]) == 1
    finite_full_minus_action = float(full_cover["margin_vs_action_only_avg"])
    finite_full_minus_valuation = float(full_cover["margin_vs_valuation_only_avg"])

    radii = [float(r["action_fill_distance_proxy"]) for r in refinement]
    margins = [float(r["margin_vs_action_only_avg"]) for r in refinement]
    zero_refined_gaps = all(float(r["finite_cover_certificate_bound"]) == 0.0 for r in refinement)
    monotone_margins = all(b >= a - 1e-12 for a, b in zip(margins, margins[1:]))
    radius_shrinks = radii[-1] < radii[0]

    strong_pass = sum(1 for r in strong if r["status"] == "strong_form_pillar_pass")
    sr_pass = sum(1 for r in state_reward if r["status"] == "state_reward_closure_pass")

    rows = [
        row(
            hierarchy_claim="strict_single_channel_face_dominance",
            theorem_anchor="Theorem fixed_preference_embedding_strictness + strict face hierarchy proposition",
            evidence_sources="inventory_exact_policy_class_dp_metrics.csv",
            observed_guard=f"valuation_minus_action={fmt(valuation_minus_action)}; full_minus_action={fmt(full_minus_action)}; full_minus_valuation={fmt(full_minus_valuation)}",
            required_guard="valuation_minus_action > 0, full_minus_action > 0.19, full_minus_valuation > 0.12",
            status="face_hierarchy_pass" if valuation_minus_action > 0 and full_minus_action > 0.19 and full_minus_valuation > 0.12 else "face_hierarchy_gap",
            interpretation="The exact policy-class DP orders the audited faces action-only < valuation-only < Full; Full strictly beats every frozen/single-channel face under the same valuation evaluator.",
        ),
        row(
            hierarchy_claim="finite_cover_exact_face_certificates",
            theorem_anchor="Finite-cover Bellman--HJB certificate",
            evidence_sources="inventory_finite_cover_hjb_certificate.csv",
            observed_guard=f"zero_certificate_gaps={int(zero_gaps)}; contains_both_faces={int(contains_faces)}; full_minus_action={fmt(finite_full_minus_action)}; full_minus_valuation={fmt(finite_full_minus_valuation)}",
            required_guard="zero_certificate_gaps = 1, contains_both_faces = 1, full_minus_action > 0.19, full_minus_valuation > 0.12",
            status="face_hierarchy_pass" if zero_gaps and contains_faces and finite_full_minus_action > 0.19 and finite_full_minus_valuation > 0.12 else "face_hierarchy_gap",
            interpretation="All three audited faces are exact finite-cover Bellman solves; the Full cover contains the frozen faces and still has certified positive margins over both.",
        ),
        row(
            hierarchy_claim="joint_control_refinement_sequence",
            theorem_anchor="Cover-refinement HJB certificate sequence",
            evidence_sources="inventory_cover_refinement_certificate.csv",
            observed_guard=f"radius={fmt(radii[0])}->{fmt(radii[-1])}; margins={fmt(margins[0])}->{fmt(margins[1])}->{fmt(margins[2])}->{fmt(margins[3])}; zero_bounds={int(zero_refined_gaps)}",
            required_guard="radius shrinks, margins monotone to > 0.19, zero_bounds = 1",
            status="face_hierarchy_pass" if radius_shrinks and monotone_margins and margins[-1] > 0.19 and zero_refined_gaps else "face_hierarchy_gap",
            interpretation="Nested action/valuation covers form a zero-gap HJB certificate sequence whose value increases as the joint-control cover is refined, supporting joint control rather than a one-grid artifact.",
        ),
        row(
            hierarchy_claim="service_pressure_joint_control_diagnostics",
            theorem_anchor="Inventory exact policy-class diagnostics",
            evidence_sources="inventory_exact_policy_class_dp_metrics.csv",
            observed_guard=f"fill_rate={fmt(action_fill)}->{fmt(valuation_fill)}->{fmt(full_fill)}; breaches={fmt(action_breaches)}->{fmt(valuation_breaches)}->{fmt(full_breaches)}",
            required_guard="Full fill rate highest and Full service breaches lowest across audited faces",
            status="face_hierarchy_pass" if full_fill >= valuation_fill >= action_fill and full_breaches <= valuation_breaches <= action_breaches else "face_hierarchy_gap",
            interpretation="The strict valuation-welfare hierarchy is accompanied by monotone service-pressure diagnostics, while physical cost remains separately reported rather than hidden in a relabeled reward.",
        ),
        row(
            hierarchy_claim="closure_stack_consistency",
            theorem_anchor="Strong-form claim closure + state/reward equivalence exclusion",
            evidence_sources="strong_form_generalized_rl_hjb_solver_claim_audit.csv + reward_shaping_state_augmentation_closure_audit.csv",
            observed_guard=f"strong_pillars={strong_pass}/{len(strong)}; state_reward_guards={sr_pass}/{len(state_reward)}; full_minus_best_face={fmt(full_minus_valuation)}",
            required_guard="6/6 strong pillars, 5/5 state/reward guards, full_minus_best_face > 0.12",
            status="face_hierarchy_pass" if strong_pass == len(strong) == 6 and sr_pass == len(state_reward) == 5 and full_minus_valuation > 0.12 else "face_hierarchy_gap",
            interpretation="The hierarchy audit is consistent with the existing six-pillar HJB-solver closure and the state-augmentation/reward-shaping exclusion audit.",
        ),
    ]

    fields = ["hierarchy_claim", "theorem_anchor", "evidence_sources", "observed_guard", "required_guard", "status", "interpretation"]
    with OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
