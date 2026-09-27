#!/usr/bin/env python3
"""Create a lightweight reconciliation audit for privileged oracle baselines.

The paper has three kinds of oracle evidence: the original main tables, compact
equal-evaluation/frontier diagnostics, and full same-budget/parameter-controlled
reruns.  This audit puts the relevant numbers in one CSV so the manuscript does
not over-read the old oracle rows.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'


def read_rows(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline='') as fh:
        return list(csv.DictReader(fh))


def find(rows: list[dict[str, str]], **kwargs: str) -> dict[str, str]:
    for row in rows:
        if all(row.get(k) == v for k, v in kwargs.items()):
            return row
    raise KeyError(kwargs)


def f(x: str) -> float:
    return float(x)


def main() -> None:
    exp2 = read_rows('exp2_metrics.csv')
    exp3 = read_rows('exp3_metrics.csv')
    repair = read_rows('exp2_oracle_repair_audit.csv')
    same = read_rows('same_budget_parameter_controlled_metrics.csv')
    frontier3 = read_rows('exp3_equal_evaluation_audit.csv')

    rows: list[dict[str, str]] = []

    full2 = find(exp2, method='full_ndu_joint')
    narrow2 = find(exp2, method='oracle_joint_action_rl')
    safe2 = find(repair, method='matched_budget_safe_oracle_lower_bound')
    same2_full = find(same, experiment='exp2', method='full_ndu_joint')
    same2_recurrent = find(same, experiment='exp2', method='same_dim_fixed_pref_recurrent_rl')
    same2_oracle = find(same, experiment='exp2', method='same_dim_oracle_joint_action_rl')
    rows.extend([
        {
            'experiment': 'exp2',
            'comparison': 'reported_narrow_oracle_main_table',
            'full_ndu_mean_utility': full2['mean_utility'],
            'comparator': 'oracle_joint_action_rl',
            'comparator_mean_utility': narrow2['mean_utility'],
            'full_minus_comparator': f'{f(full2["mean_utility"]) - f(narrow2["mean_utility"]):.12g}',
            'budget_full': '2244',
            'budget_comparator': '360',
            'param_dim_full': '18',
            'param_dim_comparator': '6',
            'interpretation': 'old privileged oracle is narrow and under-budgeted; diagnostic weakness not dominance evidence',
        },
        {
            'experiment': 'exp2',
            'comparison': 'matched_budget_safe_oracle_lower_bound',
            'full_ndu_mean_utility': full2['mean_utility'],
            'comparator': 'safe_oracle_lower_bound',
            'comparator_mean_utility': safe2['mean_utility'],
            'full_minus_comparator': f'{f(full2["mean_utility"]) - f(safe2["mean_utility"]):.12g}',
            'budget_full': '2244',
            'budget_comparator': safe2['policy_evaluations'],
            'param_dim_full': '18',
            'param_dim_comparator': safe2['param_dim'],
            'interpretation': 'conservative lower bound is slightly above Full NDU; not a trained same-architecture oracle',
        },
        {
            'experiment': 'exp2',
            'comparison': 'same_budget_same_dim_recurrent',
            'full_ndu_mean_utility': same2_full['mean_utility'],
            'comparator': 'same_dim_fixed_pref_recurrent_rl',
            'comparator_mean_utility': same2_recurrent['mean_utility'],
            'full_minus_comparator': f'{f(same2_full["mean_utility"]) - f(same2_recurrent["mean_utility"]):.12g}',
            'budget_full': same2_full['evaluation_budget'],
            'budget_comparator': same2_recurrent['evaluation_budget'],
            'param_dim_full': same2_full['param_dim'],
            'param_dim_comparator': same2_recurrent['param_dim'],
            'interpretation': 'primary fair result is practical parity, not Full-NDU dominance',
        },
        {
            'experiment': 'exp2',
            'comparison': 'same_budget_same_dim_oracle_diagnostic',
            'full_ndu_mean_utility': same2_full['mean_utility'],
            'comparator': 'same_dim_oracle_joint_action_rl',
            'comparator_mean_utility': same2_oracle['mean_utility'],
            'full_minus_comparator': f'{f(same2_full["mean_utility"]) - f(same2_oracle["mean_utility"]):.12g}',
            'budget_full': same2_full['evaluation_budget'],
            'budget_comparator': same2_oracle['evaluation_budget'],
            'param_dim_full': same2_full['param_dim'],
            'param_dim_comparator': same2_oracle['param_dim'],
            'interpretation': 'same-budget oracle action architecture remains poor; treated as diagnostic, not as strong oracle evidence',
        },
    ])

    full3 = find(exp3, method='full_ndu_joint')
    oracle3 = find(exp3, method='oracle_factor_joint_rl')
    same3_full = find(same, experiment='exp3', method='full_ndu_joint')
    same3_oracle = find(same, experiment='exp3', method='same_dim_oracle_factor_joint_rl')
    same3_fixed = find(same, experiment='exp3', method='same_dim_fixed_pref_joint_rl')
    frontier3_442 = find(frontier3, evaluation_budget='442')
    rows.extend([
        {
            'experiment': 'exp3',
            'comparison': 'reported_main_table_oracle',
            'full_ndu_mean_utility': full3['mean_utility'],
            'comparator': 'oracle_factor_joint_rl',
            'comparator_mean_utility': oracle3['mean_utility'],
            'full_minus_comparator': f'{f(full3["mean_utility"]) - f(oracle3["mean_utility"]):.12g}',
            'budget_full': '1242',
            'budget_comparator': '216',
            'param_dim_full': '19',
            'param_dim_comparator': '8',
            'interpretation': 'main-table oracle gap is confounded by budget/class and is not the primary oracle claim',
        },
        {
            'experiment': 'exp3',
            'comparison': 'equal_evaluation_frontier_442',
            'full_ndu_mean_utility': frontier3_442['full_ndu_joint'],
            'comparator': 'oracle_factor_joint_rl',
            'comparator_mean_utility': frontier3_442['oracle_factor_joint_rl'],
            'full_minus_comparator': frontier3_442['full_minus_best_non_ndu'],
            'budget_full': '442',
            'budget_comparator': '442',
            'param_dim_full': '19',
            'param_dim_comparator': '8',
            'interpretation': 'common-budget frontier gap is essentially zero but positive for Full NDU',
        },
        {
            'experiment': 'exp3',
            'comparison': 'same_budget_same_dim_privileged_oracle',
            'full_ndu_mean_utility': same3_full['mean_utility'],
            'comparator': 'same_dim_oracle_factor_joint_rl',
            'comparator_mean_utility': same3_oracle['mean_utility'],
            'full_minus_comparator': f'{f(same3_full["mean_utility"]) - f(same3_oracle["mean_utility"]):.12g}',
            'budget_full': same3_full['evaluation_budget'],
            'budget_comparator': same3_oracle['evaluation_budget'],
            'param_dim_full': same3_full['param_dim'],
            'param_dim_comparator': same3_oracle['param_dim'],
            'interpretation': 'primary fair oracle result: privileged oracle is slightly higher; no oracle-dominance claim',
        },
        {
            'experiment': 'exp3',
            'comparison': 'same_budget_same_dim_feasible_nonoracle',
            'full_ndu_mean_utility': same3_full['mean_utility'],
            'comparator': 'same_dim_fixed_pref_joint_rl',
            'comparator_mean_utility': same3_fixed['mean_utility'],
            'full_minus_comparator': f'{f(same3_full["mean_utility"]) - f(same3_fixed["mean_utility"]):.12g}',
            'budget_full': same3_full['evaluation_budget'],
            'budget_comparator': same3_fixed['evaluation_budget'],
            'param_dim_full': same3_full['param_dim'],
            'param_dim_comparator': same3_fixed['param_dim'],
            'interpretation': 'primary fair feasible-comparator result: Full NDU improves over non-oracle fixed preference',
        },
    ])

    out = DATA / 'oracle_baseline_reconciliation_audit.csv'
    with out.open('w', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(out)


if __name__ == '__main__':
    main()
