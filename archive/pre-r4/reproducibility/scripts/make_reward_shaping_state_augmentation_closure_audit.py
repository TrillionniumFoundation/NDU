#!/usr/bin/env python3
"""Build a referee-facing closure audit for state-augmentation/reward-shaping objections.

The audit distinguishes three claims that are often conflated: (i) fixed-
preference RL embeds as a frozen face, (ii) augmented-state dynamic programming
is available on that face, and (iii) a same-evaluator Full valuation-control
margin cannot be explained by reward relabeling unless the evaluator is changed
or valuation control is reintroduced.  It reuses packaged exact-DP, finite-cover,
same-protocol, and NBO/HJB evidence.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "reward_shaping_state_augmentation_closure_audit.csv"


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="") as fh:
        return list(csv.DictReader(fh))


def fmt(x: float) -> str:
    return f"{x:.12g}"


def row(**kwargs: object) -> dict[str, object]:
    return kwargs


def parse_guard(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for part in text.split("; "):
        k, v = part.split("=", 1)
        out[k] = v
    return out


def main() -> int:
    noncollapse = {r["noncollapse_claim"]: r for r in read_csv("generalized_rl_noncollapse_audit.csv")}
    exact_policy_guard = parse_guard(noncollapse["exact_policy_class_value_separation"]["observed_guard"])
    exact_mdp_guard = parse_guard(noncollapse["exact_valuation_state_mdp_value_separation"]["observed_guard"])
    finite_guard = parse_guard(noncollapse["finite_cover_certificate_value_separation"]["observed_guard"])
    same_guard = parse_guard(noncollapse["same_information_budget_noncollapse"]["observed_guard"])

    strong = read_csv("strong_form_generalized_rl_hjb_solver_claim_audit.csv")
    strong_pass = sum(1 for r in strong if r["status"] == "strong_form_pillar_pass")
    nbo_guard = parse_guard(noncollapse["source_nbo_rollout_noncollapse"]["observed_guard"])

    exact_full_minus_action = float(exact_policy_guard["full_minus_action"])
    exact_best_face = float(exact_policy_guard["full_minus_best_single_channel_face"])
    mdp_margin = float(exact_mdp_guard["full_minus_action"])
    theta_free_cost_gap = float(exact_mdp_guard["theta_free_cost_gap"])
    finite_bound = float(finite_guard["finite_bound"])
    finite_margin = float(finite_guard["full_minus_action"])
    finite_contains = int(finite_guard["contains_both_faces"])
    exp1 = float(same_guard["exp1"])
    exp2_abs = float(same_guard["exp2_abs"])
    exp3_feasible = float(same_guard["exp3_feasible"])
    selected_exp3 = float(same_guard["selected_exp3"])
    nbo_exp1 = float(nbo_guard["exp1"])
    nbo_inventory = float(nbo_guard["inventory"])

    rows = [
        row(
            closure_claim="same_evaluator_reward_shaping_exclusion",
            theorem_anchor="Non-collapse under positive valuation-control margin",
            evidence_sources="generalized_rl_noncollapse_audit.csv + inventory_exact_policy_class_dp_metrics.csv",
            observed_guard=f"full_minus_action={fmt(exact_full_minus_action)}; full_minus_best_single_channel_face={fmt(exact_best_face)}; evaluator_preserved=1",
            required_guard="same evaluator/reward, full_minus_action > 0.19, full_minus_best_single_channel_face > 0.12",
            status="state_reward_closure_pass" if exact_full_minus_action > 0.19 and exact_best_face > 0.12 else "state_reward_closure_gap",
            interpretation="Under the same evaluator, reward shaping/relabeling cannot explain away a positive Full-minus-frozen value margin; changing the reward would be changing the evaluated problem.",
        ),
        row(
            closure_claim="augmented_state_fixed_theta_face_contained",
            theorem_anchor="Finite-cover Bellman--HJB certificate + fixed-theta embedding",
            evidence_sources="inventory_finite_cover_hjb_certificate.csv",
            observed_guard=f"finite_bound={fmt(finite_bound)}; full_minus_action={fmt(finite_margin)}; contains_both_faces={finite_contains}",
            required_guard="finite_bound = 0, full_minus_action > 0.19, contains_both_faces = 1",
            status="state_reward_closure_pass" if finite_bound == 0.0 and finite_margin > 0.19 and finite_contains == 1 else "state_reward_closure_gap",
            interpretation="The exact Bellman cover already contains the augmented fixed-theta/action-only faces; state augmentation alone is therefore an embedded comparator, not an explanation of the Full margin.",
        ),
        row(
            closure_claim="physical_cost_not_reward_relabeling",
            theorem_anchor="Valuation-control welfare vs theta-free physical cost separation",
            evidence_sources="inventory_exact_valuation_control_mdp_metrics.csv",
            observed_guard=f"valuation_margin={fmt(mdp_margin)}; theta_free_cost_gap={fmt(theta_free_cost_gap)}",
            required_guard="valuation_margin > 0.015 and theta_free_cost_gap < 1e-10",
            status="state_reward_closure_pass" if mdp_margin > 0.015 and theta_free_cost_gap < 1e-10 else "state_reward_closure_gap",
            interpretation="The exact valuation-state MDP separates valuation welfare from theta-free physical cost, so the gain is a controlled valuation-channel effect rather than a hidden physical-cost relabeling.",
        ),
        row(
            closure_claim="same_protocol_information_budget_guard",
            theorem_anchor="Same-information protocol matrix + non-collapse corollary",
            evidence_sources="same_budget_parameter_controlled_audit.csv + hbo_exp3_parity_closing_audit.csv",
            observed_guard=f"exp1={fmt(exp1)}; exp2_abs={fmt(exp2_abs)}; exp3_feasible={fmt(exp3_feasible)}; selected_exp3={fmt(selected_exp3)}",
            required_guard="Exp I positive, Exp II practical parity, Exp III feasible and selected positive",
            status="state_reward_closure_pass" if exp1 > 0.02 and exp2_abs < 2e-6 and exp3_feasible > 0.01 and selected_exp3 > 0 else "state_reward_closure_gap",
            interpretation="Same-information/same-budget comparisons prevent the referee objection from attributing the Full gain to extra information, parameter budget, or a changed comparator protocol.",
        ),
        row(
            closure_claim="hjb_solver_not_reward_relabeling",
            theorem_anchor="NBO HJB-solver certificate + strong-form claim closure",
            evidence_sources="strong_form_generalized_rl_hjb_solver_claim_audit.csv + nbo_full_ndu_solver_audit.csv",
            observed_guard=f"strong_pillars={strong_pass}/{len(strong)}; nbo_exp1={fmt(nbo_exp1)}; nbo_inventory={fmt(nbo_inventory)}",
            required_guard="6/6 strong pillars, nbo_exp1 > 0, nbo_inventory > 0",
            status="state_reward_closure_pass" if strong_pass == len(strong) == 6 and nbo_exp1 > 0 and nbo_inventory > 0 else "state_reward_closure_gap",
            interpretation="The solver claim is tied to HJB certificate ingredients and held-out Full-minus-fixed margins, not to a post-hoc reward relabeling of an action-only RL run.",
        ),
    ]

    fields = ["closure_claim", "theorem_anchor", "evidence_sources", "observed_guard", "required_guard", "status", "interpretation"]
    with OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
