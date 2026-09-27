#!/usr/bin/env python3
"""Build a compact internal-vs-external evaluator audit table.

This script does not rerun optimization. It aggregates packaged seed-level and
summary CSVs into the manuscript-facing evaluator table used to keep theta-free
or physical metrics visible beside valuation-objective metrics.
"""
from __future__ import annotations

import csv
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
OUT = DATA / 'primary_evaluator_audit.csv'


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline='') as fh:
        return list(csv.DictReader(fh))


def fmt(x: float, nd: int = 5) -> str:
    return f"{x:.{nd}f}"


def paired(seed_rows: list[dict[str, str]], exp: str, full: str, comp: str, metric: str) -> tuple[int, float, float]:
    by = defaultdict(dict)
    for row in seed_rows:
        if row['experiment'] == exp and row['method'] in {full, comp} and row.get(metric):
            by[(row['method'])][int(row['seed_index'])] = float(row[metric])
    keys = sorted(set(by[full]) & set(by[comp]))
    diffs = [by[full][k] - by[comp][k] for k in keys]
    n = len(diffs)
    mean = sum(diffs) / n
    ci = 1.96 * statistics.stdev(diffs) / math.sqrt(n) if n > 1 else 0.0
    return n, mean, ci


def bootstrap_independent_diff(
    rows_: list[dict[str, str]],
    method_a: str,
    method_b: str,
    metric: str,
    *,
    audit: str = 'equal_budget_inventory',
    variant: str = 'normal',
    reps: int = 20000,
    seed: int = 20260512,
) -> tuple[int, float, float]:
    """Return mean(method_a-method_b) and deterministic bootstrap CI half-width.

    The equal-budget inventory audit uses method-specific optimizer seeds rather
    than exact matched shock-seed identifiers, so the manuscript labels this as a
    bootstrap interval rather than a paired interval.
    """
    a = [float(r[metric]) for r in rows_ if r['audit'] == audit and r['evaluation_variant'] == variant and r['method'] == method_a]
    b = [float(r[metric]) for r in rows_ if r['audit'] == audit and r['evaluation_variant'] == variant and r['method'] == method_b]
    if not a or not b:
        raise ValueError((method_a, method_b, metric, len(a), len(b)))
    obs = statistics.mean(a) - statistics.mean(b)
    rng = random.Random(seed)
    boot = []
    for _ in range(reps):
        ma = sum(rng.choice(a) for _ in a) / len(a)
        mb = sum(rng.choice(b) for _ in b) / len(b)
        boot.append(ma - mb)
    boot.sort()
    lo = boot[int(0.025 * reps)]
    hi = boot[int(0.975 * reps) - 1]
    return min(len(a), len(b)), obs, max(obs - lo, hi - obs)


def metric_row(summary: list[dict[str, str]], exp: str, method: str) -> dict[str, str]:
    for row in summary:
        if row['experiment'] == exp and row['method'] == method:
            return row
    raise KeyError((exp, method))


def method_row(rows: list[dict[str, str]], method: str) -> dict[str, str]:
    for row in rows:
        if row['method'] == method:
            return row
    raise KeyError(method)


def main() -> None:
    seed = read_csv('same_budget_parameter_controlled_seed_metrics.csv')
    summary = read_csv('same_budget_parameter_controlled_metrics.csv')
    inv_equal = read_csv('inventory_equal_budget_theta_audit_metrics.csv')
    inv_equal_seed = read_csv('inventory_equal_budget_theta_audit_seed_metrics.csv')
    sku = read_csv('sku_inventory_baseline_metrics.csv')
    exact_class = read_csv('inventory_exact_policy_class_dp_metrics.csv')
    exact_vc = read_csv('inventory_exact_valuation_control_mdp_metrics.csv')

    n, exp1_gap, exp1_ci = paired(seed, 'exp1', 'full_ndu_joint', 'same_dim_preference_backbone', 'mean_utility')
    _, exp1_w_gap, exp1_w_ci = paired(seed, 'exp1', 'full_ndu_joint', 'same_dim_fixed_orig_rl', 'wealth_terminal')
    exp1_full = metric_row(summary, 'exp1', 'full_ndu_joint')
    exp1_fixed = metric_row(summary, 'exp1', 'same_dim_fixed_orig_rl')

    n2, exp2_gap, exp2_ci = paired(seed, 'exp2', 'full_ndu_joint', 'same_dim_fixed_pref_recurrent_rl', 'mean_utility')
    _, exp2_sharpe, exp2_sharpe_ci = paired(seed, 'exp2', 'full_ndu_joint', 'same_dim_fixed_pref_recurrent_rl', 'sharpe')
    _, exp2_draw, exp2_draw_ci = paired(seed, 'exp2', 'full_ndu_joint', 'same_dim_fixed_pref_recurrent_rl', 'max_drawdown')

    n3, exp3_gap_oracle, exp3_ci_oracle = paired(seed, 'exp3', 'full_ndu_joint', 'same_dim_oracle_factor_joint_rl', 'mean_utility')
    _, exp3_gap_feas, exp3_ci_feas = paired(seed, 'exp3', 'full_ndu_joint', 'same_dim_fixed_pref_joint_rl', 'mean_utility')
    _, exp3_sharpe_oracle, exp3_sharpe_ci = paired(seed, 'exp3', 'full_ndu_joint', 'same_dim_oracle_factor_joint_rl', 'sharpe')
    _, exp3_draw_oracle, exp3_draw_ci = paired(seed, 'exp3', 'full_ndu_joint', 'same_dim_oracle_factor_joint_rl', 'max_drawdown')
    _, exp3_turn_feas, exp3_turn_ci = paired(seed, 'exp3', 'full_ndu_joint', 'same_dim_fixed_pref_joint_rl', 'turnover')

    inv_full = next(r for r in inv_equal if r['audit'] == 'equal_budget_inventory' and r['method'] == 'full_ndu_inventory' and r['evaluation_variant'] == 'normal')
    inv_action = next(r for r in inv_equal if r['audit'] == 'equal_budget_inventory' and r['method'] == 'action_only_adaptive_base_stock')
    n_inv, inv_welfare_gap, inv_welfare_ci = bootstrap_independent_diff(inv_equal_seed, 'full_ndu_inventory', 'action_only_adaptive_base_stock', 'mean_welfare')
    _, inv_cost_gap, inv_cost_ci = bootstrap_independent_diff(inv_equal_seed, 'full_ndu_inventory', 'action_only_adaptive_base_stock', 'avg_cost_no_theta')
    _, inv_fill_gap, inv_fill_ci = bootstrap_independent_diff(inv_equal_seed, 'full_ndu_inventory', 'action_only_adaptive_base_stock', 'fill_rate')
    _, inv_backlog_gap, inv_backlog_ci = bootstrap_independent_diff(inv_equal_seed, 'full_ndu_inventory', 'action_only_adaptive_base_stock', 'ending_backlog')
    _, inv_breach_gap, inv_breach_ci = bootstrap_independent_diff(inv_equal_seed, 'full_ndu_inventory', 'action_only_adaptive_base_stock', 'service_breach_count')
    sku_full = method_row(sku, 'full_ndu_theta_service_control')
    sku_adp = method_row(sku, 'approximate_dp_inventory')
    exact_action = method_row(exact_class, 'action_only_exact_dp')
    exact_full_class = method_row(exact_class, 'full_valuation_control_exact_dp')
    exact_vc_action = method_row(exact_vc, 'exact_dp_action_only_fixed_theta')
    exact_vc_full = method_row(exact_vc, 'exact_dp_full_order_and_valuation_control')

    rows = [
        {
            'benchmark': 'exp1_habit_portfolio_same_budget',
            'internal_objective_read': f"mean utility gap vs preference-backbone = {fmt(exp1_gap)} +/- {fmt(exp1_ci)} (paired CI, n={n})",
            'external_theta_free_read': f"terminal wealth Full {float(exp1_full['wealth_terminal']):.4f} vs same-budget fixed-original {float(exp1_fixed['wealth_terminal']):.4f}; paired Full-minus-fixed-original {fmt(exp1_w_gap)} +/- {fmt(exp1_w_ci)}",
            'claim_read': 'valuation-objective gain; terminal-wealth metric is mixed',
        },
        {
            'benchmark': 'exp2_hidden_regime_same_budget',
            'internal_objective_read': f"mean utility gap vs fixed-recurrent = {exp2_gap:.7f} +/- {exp2_ci:.7f} (paired CI, n={n2})",
            'external_theta_free_read': f"Sharpe gap {fmt(exp2_sharpe)} +/- {fmt(exp2_sharpe_ci)}; drawdown gap {fmt(exp2_draw, 6)} +/- {fmt(exp2_draw_ci, 6)} vs fixed-recurrent",
            'claim_read': 'internal parity with modest physical-diagnostic advantage',
        },
        {
            'benchmark': 'exp3_high_dimensional_same_budget',
            'internal_objective_read': f"old CEM mean utility gap vs privileged reference = {fmt(exp3_gap_oracle)} +/- {fmt(exp3_ci_oracle)}; vs feasible fixed-pref = {fmt(exp3_gap_feas)} +/- {fmt(exp3_ci_feas)}",
            'external_theta_free_read': f"old CEM vs privileged-reference Sharpe gap {fmt(exp3_sharpe_oracle)} +/- {fmt(exp3_sharpe_ci)} and drawdown gap {fmt(exp3_draw_oracle)} +/- {fmt(exp3_draw_ci)}; PyTorch-AD HBO/NBO privileged factor-reference row remains higher; feasible comparator is parity",
            'claim_read': 'legacy CEM stress plus feasible-comparator gain; current HBO/NBO table supplies feasible parity and privileged-reference outcome',
        },
        {
            'benchmark': 'inventory_sku_external_costs',
            'internal_objective_read': f"equal-budget inventory welfare Full {float(inv_full['mean_welfare']):.4f} vs action-only {float(inv_action['mean_welfare']):.4f}; Full-minus-action {fmt(inv_welfare_gap)} +/- {fmt(inv_welfare_ci)} (bootstrap CI, n={n_inv} per method)",
            'external_theta_free_read': f"theta-free cost Full {float(inv_full['avg_cost_no_theta']):.4f} vs action-only {float(inv_action['avg_cost_no_theta']):.4f}; Full-minus-action {fmt(inv_cost_gap)} +/- {fmt(inv_cost_ci)} bootstrap; fill gap {fmt(inv_fill_gap, 6)} +/- {fmt(inv_fill_ci, 6)}, backlog gap {fmt(inv_backlog_gap)} +/- {fmt(inv_backlog_ci)}, breach gap {fmt(inv_breach_gap)} +/- {fmt(inv_breach_ci)}; SKU valuation welfare Full {float(sku_full['valuation_adjusted_welfare']):.4f} vs ADP {float(sku_adp['valuation_adjusted_welfare']):.4f}; SKU external cost Full {float(sku_full['external_avg_cost']):.4f} +/- {float(sku_full['external_avg_cost_ci95']):.4f} vs ADP {float(sku_adp['external_avg_cost']):.4f} +/- {float(sku_adp['external_avg_cost_ci95']):.4f}",
            'claim_read': 'service-pressure valuation welfare leads; theta-free/external cost is reported as a diagnostic',
        },
        {
            'benchmark': 'inventory_exact_dp_distinction',
            'internal_objective_read': f"exact valuation-control MDP welfare Full {float(exact_vc_full['expected_avg_welfare']):.4f} vs action-only {float(exact_vc_action['expected_avg_welfare']):.4f}",
            'external_theta_free_read': f"nested exact policy-class DP welfare Full {float(exact_full_class['expected_avg_welfare']):.4f} vs action-only {float(exact_action['expected_avg_welfare']):.4f}; valuation-control MDP theta-free cost equal at {float(exact_vc_full['theta_free_expected_avg_cost']):.4f}",
            'claim_read': 'exact-DP audits show valuation-control welfare gain under nested Full action sets',
        },
    ]
    with OUT.open('w', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=['benchmark', 'internal_objective_read', 'external_theta_free_read', 'claim_read'])
        writer.writeheader()
        writer.writerows(rows)
    print(f'wrote {OUT} rows={len(rows)}')


if __name__ == '__main__':
    main()
