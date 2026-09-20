#!/usr/bin/env python3
"""Lightweight reproducibility checker for the NDU OR manuscript.

This audit validates the packaged CSV evidence and manuscript headline values
without rerunning the expensive optimization/search routines.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
ROOT = Path(__file__).resolve().parent
SUBMISSION_ROOT = ROOT.parent
DATA = ROOT / 'data'
MANIFEST = ROOT / 'manifest.json'

checks: list[dict] = []


def add(name: str, ok: bool, observed: object = '', expected: object = '') -> None:
    checks.append({'name': name, 'ok': bool(ok), 'observed': observed, 'expected': expected})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline='') as fh:
        return list(csv.DictReader(fh))


def json_data(name: str) -> dict:
    return json.loads((DATA / name).read_text())


def method_row(name: str, method: str) -> dict[str, str]:
    for row in rows(name):
        if row.get('method') == method:
            return row
    raise KeyError((name, method))


def experiment_method_row(name: str, experiment: str, method: str) -> dict[str, str]:
    for row in rows(name):
        if row.get('experiment') == experiment and row.get('method') == method:
            return row
    raise KeyError((name, experiment, method))


def epsilon_method_row(name: str, epsilon: str, method: str) -> dict[str, str]:
    for row in rows(name):
        if row.get('epsilon') == epsilon and row.get('method') == method:
            return row
    raise KeyError((name, epsilon, method))


def scenario_method_row(name: str, scenario: str, method: str) -> dict[str, str]:
    for row in rows(name):
        if row.get('scenario') == scenario and row.get('method') == method:
            return row
    raise KeyError((name, scenario, method))


def close(a: float, b: float, tol: float = 1e-10) -> bool:
    return math.isclose(float(a), float(b), rel_tol=tol, abs_tol=tol)


def check_seed_coverage(name: str, expected_n: int) -> None:
    rs = rows(name)
    methods = sorted({r['method'] for r in rs})
    counts = {m: len({r['seed'] for r in rs if r['method'] == m}) for m in methods}
    add(f'{name}:seed_count_by_method', all(v == expected_n for v in counts.values()), counts, expected_n)
    add(f'{name}:row_count', len(rs) == expected_n * len(methods), len(rs), expected_n * len(methods))


def check_scenario_seed_coverage(name: str, expected_n: int) -> None:
    rs = rows(name)
    scenarios = sorted({r['scenario'] for r in rs})
    methods = sorted({r['method'] for r in rs})
    counts = {(s, m): len({r['seed'] for r in rs if r['scenario'] == s and r['method'] == m}) for s in scenarios for m in methods}
    add(f'{name}:scenario_method_seed_count', all(v == expected_n for v in counts.values()), counts, expected_n)
    add(f'{name}:row_count_by_scenario_method', len(rs) == expected_n * len(methods) * len(scenarios), len(rs), expected_n * len(methods) * len(scenarios))


def check_experiment_method_seed_coverage(name: str, expected_n: int) -> None:
    rs = rows(name)
    experiments = sorted({r['experiment'] for r in rs})
    counts = {}
    for exp in experiments:
        methods = sorted({r['method'] for r in rs if r['experiment'] == exp})
        for method in methods:
            counts[(exp, method)] = len({r['seed'] for r in rs if r['experiment'] == exp and r['method'] == method})
    add(f'{name}:experiment_method_seed_count', all(v == expected_n for v in counts.values()), counts, expected_n)


def check_epsilon_method_seed_coverage(name: str, expected_n: int) -> None:
    rs = rows(name)
    epsilons = sorted({r['epsilon'] for r in rs}, key=float)
    methods = sorted({r['method'] for r in rs})
    counts = {(eps, method): len({r['seed'] for r in rs if r['epsilon'] == eps and r['method'] == method}) for eps in epsilons for method in methods}
    add(f'{name}:epsilon_method_seed_count', all(v == expected_n for v in counts.values()), counts, expected_n)


def main() -> int:
    manifest = json.loads(MANIFEST.read_text())
    for item in manifest['files']:
        path = ROOT / item['path']
        add(f'exists:{item["path"]}', path.exists(), path.exists(), True)
        if path.exists():
            add(f'sha256:{item["path"]}', sha256(path) == item['sha256'], sha256(path), item['sha256'])

    for name, expected in manifest['row_counts'].items():
        add(f'row_count:{name}', len(rows(name)) == expected, len(rows(name)), expected)

    for name, expected_methods in manifest['method_sets'].items():
        observed = sorted({r['method'] for r in rows(name)})
        add(f'methods:{name}', observed == expected_methods, observed, expected_methods)

    for name in ['exp1_seed_metrics.csv', 'exp2_seed_metrics.csv', 'exp3_seed_metrics.csv', 'inventory_service_level_seed_metrics.csv']:
        check_seed_coverage(name, manifest['seed_count_per_method'])
    if 'oracle_baseline_reconciliation_audit' in manifest:
        audit = manifest['oracle_baseline_reconciliation_audit']
        recon_rows = {(r['experiment'], r['comparison']): r for r in rows('oracle_baseline_reconciliation_audit.csv')}
        add('oracle_reconciliation:row_count', len(recon_rows) == audit['row_count'], len(recon_rows), audit['row_count'])
        for item in audit['expected']:
            key = (item['experiment'], item['comparison'])
            row = recon_rows.get(key)
            add(f'oracle_reconciliation:{"/".join(key)}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'oracle_reconciliation:{"/".join(key)}:comparator', row['comparator'] == item['comparator'], row['comparator'], item['comparator'])
            add(f'oracle_reconciliation:{"/".join(key)}:full_minus_comparator', close(float(row['full_minus_comparator']), item['full_minus_comparator']), float(row['full_minus_comparator']), item['full_minus_comparator'])
            add(f'oracle_reconciliation:{"/".join(key)}:budget_full', int(row['budget_full']) == item['budget_full'], row['budget_full'], item['budget_full'])
            add(f'oracle_reconciliation:{"/".join(key)}:budget_comparator', int(row['budget_comparator']) == item['budget_comparator'], row['budget_comparator'], item['budget_comparator'])

    if 'exp2_oracle_repair_audit' in manifest:
        check_seed_coverage('exp2_oracle_repair_seed_metrics.csv', manifest['exp2_oracle_repair_audit']['safe_oracle_seed_count'])
    if 'inventory_sensitivity_grid' in manifest:
        check_scenario_seed_coverage('inventory_sensitivity_grid_seed_metrics.csv', manifest['inventory_sensitivity_grid']['seed_count_per_scenario_method'])
    if 'same_budget_parameter_controlled' in manifest:
        check_experiment_method_seed_coverage('same_budget_parameter_controlled_seed_metrics.csv', manifest['same_budget_parameter_controlled']['seed_count'])
    if 'neural_solver_validation' in manifest:
        check_epsilon_method_seed_coverage('neural_solver_validation_seed_metrics.csv', manifest['neural_solver_validation']['seed_count'])
    if 'nbo_full_ndu_solver' in manifest:
        check_experiment_method_seed_coverage('source_nbo_seed_metrics.csv', manifest['nbo_full_ndu_solver']['seed_count'])

    kv = manifest['key_values']
    comparisons = {
        'exp1_full_ndu_joint_mean_utility': ('exp1_metrics.csv', 'full_ndu_joint', 'mean_utility'),
        'exp1_full_ndu_joint_cew': ('exp1_metrics.csv', 'full_ndu_joint', 'cew'),
        'exp2_full_ndu_joint_mean_utility': ('exp2_metrics.csv', 'full_ndu_joint', 'mean_utility'),
        'exp2_full_ndu_joint_cew': ('exp2_metrics.csv', 'full_ndu_joint', 'cew'),
        'exp2_full_ndu_joint_sharpe': ('exp2_metrics.csv', 'full_ndu_joint', 'sharpe'),
        'exp2_full_ndu_joint_regime_detection_acc': ('exp2_metrics.csv', 'full_ndu_joint', 'regime_detection_acc'),
        'exp3_full_ndu_joint_mean_utility': ('exp3_metrics.csv', 'full_ndu_joint', 'mean_utility'),
        'exp3_full_ndu_joint_cew': ('exp3_metrics.csv', 'full_ndu_joint', 'cew'),
        'exp3_full_ndu_joint_turnover': ('exp3_metrics.csv', 'full_ndu_joint', 'turnover'),
        'inventory_full_ndu_mean_welfare': ('inventory_service_level_metrics.csv', 'full_ndu_inventory', 'mean_welfare'),
        'inventory_full_ndu_avg_cost': ('inventory_service_level_metrics.csv', 'full_ndu_inventory', 'avg_cost'),
        'inventory_full_ndu_fill_rate': ('inventory_service_level_metrics.csv', 'full_ndu_inventory', 'fill_rate'),
        'inventory_full_ndu_ending_backlog': ('inventory_service_level_metrics.csv', 'full_ndu_inventory', 'ending_backlog'),
        'inventory_action_only_mean_welfare': ('inventory_service_level_metrics.csv', 'action_only_adaptive_base_stock', 'mean_welfare'),
        'inventory_fixed_service_mean_welfare': ('inventory_service_level_metrics.csv', 'fixed_service_base_stock', 'mean_welfare'),
        'inventory_dp_exact_total_cost': ('inventory_dp_oracle_metrics.csv', 'exact_dynamic_programming_oracle', 'expected_total_cost'),
        'inventory_dp_exact_avg_cost': ('inventory_dp_oracle_metrics.csv', 'exact_dynamic_programming_oracle', 'expected_avg_cost'),
        'inventory_dp_exact_lost_sales': ('inventory_dp_oracle_metrics.csv', 'exact_dynamic_programming_oracle', 'expected_lost_sales'),
        'inventory_dp_exact_fill_rate': ('inventory_dp_oracle_metrics.csv', 'exact_dynamic_programming_oracle', 'fill_rate'),
        'inventory_dp_base_stock_total_cost': ('inventory_dp_oracle_metrics.csv', 'best_stationary_base_stock', 'expected_total_cost'),
        'inventory_dp_no_reorder_total_cost': ('inventory_dp_oracle_metrics.csv', 'no_reorder', 'expected_total_cost'),
        'real_trace_adaptive_test_avg_cost': ('inventory_real_demand_calibration_metrics.csv', 'adaptive_valuation_service_replay', 'test_avg_cost'),
        'real_trace_adaptive_test_fill_rate': ('inventory_real_demand_calibration_metrics.csv', 'adaptive_valuation_service_replay', 'test_fill_rate'),
        'real_trace_fixed_test_avg_cost': ('inventory_real_demand_calibration_metrics.csv', 'fixed_empirical_base_stock', 'test_avg_cost'),
        'real_trace_seasonal_test_avg_cost': ('inventory_real_demand_calibration_metrics.csv', 'seasonal_quantile_base_stock', 'test_avg_cost'),
        'real_trace_no_reorder_test_avg_cost': ('inventory_real_demand_calibration_metrics.csv', 'no_reorder', 'test_avg_cost'),
    }
    for key, (csv_name, method, col) in comparisons.items():
        observed = float(method_row(csv_name, method)[col])
        add(f'key_value:{key}', close(observed, kv[key]), observed, kv[key])

    scenario_comparisons = {
        'inventory_sensitivity_baseline_full_mean_welfare': ('baseline', 'full_ndu_inventory', 'mean_welfare'),
        'inventory_sensitivity_volatile_full_mean_welfare': ('volatile_demand', 'full_ndu_inventory', 'mean_welfare'),
        'inventory_sensitivity_high_shortage_full_mean_welfare': ('high_shortage_penalty', 'full_ndu_inventory', 'mean_welfare'),
        'inventory_sensitivity_tight_capacity_full_mean_welfare': ('tight_capacity', 'full_ndu_inventory', 'mean_welfare'),
        'inventory_sensitivity_tight_capacity_full_avg_cost': ('tight_capacity', 'full_ndu_inventory', 'avg_cost'),
        'inventory_sensitivity_high_shortage_gap_to_best': ('high_shortage_penalty', 'full_ndu_inventory', 'welfare_gap_to_best'),
    }
    for key, (scenario, method, col) in scenario_comparisons.items():
        if key not in kv:
            continue
        observed = float(scenario_method_row('inventory_sensitivity_grid_metrics.csv', scenario, method)[col])
        add(f'key_value:{key}', close(observed, kv[key]), observed, kv[key])

    if 'inventory_dp_oracle' in manifest:
        dp = manifest['inventory_dp_oracle']
        dp_rows = {r['method']: r for r in rows('inventory_dp_oracle_metrics.csv')}
        exact = dp_rows.get('exact_dynamic_programming_oracle')
        base = dp_rows.get('best_stationary_base_stock')
        add('inventory_dp:exact_row_exists', exact is not None, bool(exact), True)
        add('inventory_dp:base_stock_row_exists', base is not None, bool(base), True)
        if exact and base:
            add('inventory_dp:base_stock_rule', base['order_up_to_rule'] == str(dp['best_stationary_order_up_to']), base['order_up_to_rule'], dp['best_stationary_order_up_to'])
            add('inventory_dp:exact_matches_base_stock_cost', close(float(exact['expected_total_cost']), float(base['expected_total_cost'])), exact['expected_total_cost'], base['expected_total_cost'])
        policy_count = len(rows('inventory_dp_oracle_policy.csv'))
        add('inventory_dp:policy_row_count', policy_count == dp['policy_row_count'], policy_count, dp['policy_row_count'])

    if 'real_demand_calibration' in manifest:
        real = manifest['real_demand_calibration']
        trace_rows = rows('airpassengers_monthly_demand_trace.csv')
        add('real_trace:row_count', len(trace_rows) == real['trace_row_count'], len(trace_rows), real['trace_row_count'])
        split_counts = {split: sum(1 for r in trace_rows if r['split'] == split) for split in ['train', 'test']}
        add('real_trace:split_counts', split_counts == {'train': real['train_months'], 'test': real['test_months']}, split_counts, {'train': real['train_months'], 'test': real['test_months']})
        replay_rows = rows('inventory_real_demand_replay.csv')
        add('real_trace:replay_row_count', len(replay_rows) == real['replay_row_count'], len(replay_rows), real['replay_row_count'])
        adaptive = method_row('inventory_real_demand_calibration_metrics.csv', 'adaptive_valuation_service_replay')
        fixed = method_row('inventory_real_demand_calibration_metrics.csv', 'fixed_empirical_base_stock')
        seasonal = method_row('inventory_real_demand_calibration_metrics.csv', 'seasonal_quantile_base_stock')
        add('real_trace:adaptive_beats_fixed_cost', float(adaptive['test_avg_cost']) < float(fixed['test_avg_cost']), adaptive['test_avg_cost'], f'< {fixed["test_avg_cost"]}')
        add('real_trace:adaptive_beats_seasonal_cost', float(adaptive['test_avg_cost']) < float(seasonal['test_avg_cost']), adaptive['test_avg_cost'], f'< {seasonal["test_avg_cost"]}')

    if 'sku_inventory_or_benchmark' in manifest:
        sku = manifest['sku_inventory_or_benchmark']
        check_seed_coverage('sku_inventory_baseline_seed_metrics.csv', sku['seed_count'])
        panel_rows = rows('sku_monthly_demand_panel.csv')
        add('sku_inventory:panel_row_count', len(panel_rows) == sku['panel_row_count'], len(panel_rows), sku['panel_row_count'])
        split_counts = {split: sum(1 for r in panel_rows if r['split'] == split) for split in ['train', 'test']}
        add('sku_inventory:panel_split_counts', split_counts == {'train': sku['panel_train_rows'], 'test': sku['panel_test_rows']}, split_counts, {'train': sku['panel_train_rows'], 'test': sku['panel_test_rows']})
        source_rows = rows('sku_monthly_demand_source.csv')
        add('sku_inventory:source_sku_count', len(source_rows) == sku['sku_count'], len(source_rows), sku['sku_count'])
        baseline = {r['method']: r for r in rows('sku_inventory_baseline_metrics.csv')}
        add('sku_inventory:metrics_row_count', len(baseline) == sku['method_count'], len(baseline), sku['method_count'])
        for method, expected in sku['expected_metrics'].items():
            row = baseline.get(method)
            add(f'sku_inventory:{method}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            for col, expected_value in expected.items():
                add(f'sku_inventory:{method}:{col}', close(float(row[col]), expected_value), float(row[col]), expected_value)
        full = baseline.get('full_ndu_theta_service_control')
        adp = baseline.get('approximate_dp_inventory')
        seasonal = baseline.get('seasonal_service_tuned_base_stock')
        mpc = baseline.get('mpc_scenario_base_stock')
        if full and adp and seasonal and mpc:
            add('sku_inventory:full_beats_adp_valuation_welfare', float(full['valuation_adjusted_welfare']) > float(adp['valuation_adjusted_welfare']), full['valuation_adjusted_welfare'], f'> {adp["valuation_adjusted_welfare"]}')
            add('sku_inventory:full_close_to_adp_cost', float(full['external_avg_cost']) - float(adp['external_avg_cost']) <= sku['full_vs_adp_cost_tolerance'], float(full['external_avg_cost']) - float(adp['external_avg_cost']), f'<= {sku["full_vs_adp_cost_tolerance"]}')
            add('sku_inventory:full_beats_seasonal_cost', float(full['external_avg_cost']) < float(seasonal['external_avg_cost']), full['external_avg_cost'], f'< {seasonal["external_avg_cost"]}')
            add('sku_inventory:full_beats_mpc_cost', float(full['external_avg_cost']) < float(mpc['external_avg_cost']), full['external_avg_cost'], f'< {mpc["external_avg_cost"]}')
        surface_rows = rows('sku_theta_policy_surface.csv')
        add('sku_theta_surface:row_count', len(surface_rows) == sku['theta_surface_row_count'], len(surface_rows), sku['theta_surface_row_count'])
        surface = {(r['demand_shock_ratio'], r['backlog_normalized'], r['capacity_tightness']): r for r in surface_rows}
        prev_theta = -1.0
        for key, expected in sku['theta_surface_expected'].items():
            row = surface.get(tuple(key.split('|')))
            add(f'sku_theta_surface:{key}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'sku_theta_surface:{key}:theta', close(float(row['theta_service_pressure']), expected['theta_service_pressure']), float(row['theta_service_pressure']), expected['theta_service_pressure'])
            add(f'sku_theta_surface:{key}:target_fill', close(float(row['implied_target_fill_rate']), expected['implied_target_fill_rate']), float(row['implied_target_fill_rate']), expected['implied_target_fill_rate'])
            add(f'sku_theta_surface:{key}:theta_non_decreasing_path', float(row['theta_service_pressure']) >= prev_theta, float(row['theta_service_pressure']), f'>= {prev_theta}')
            prev_theta = float(row['theta_service_pressure'])
        dp_rows = {r['method']: r for r in rows('inventory_exact_valuation_control_mdp_metrics.csv')}
        dp_policy_rows = rows('inventory_exact_valuation_control_mdp_policy.csv')
        add('sku_exact_valuation_dp:metrics_row_count', len(dp_rows) == sku['exact_valuation_dp']['metrics_row_count'], len(dp_rows), sku['exact_valuation_dp']['metrics_row_count'])
        add('sku_exact_valuation_dp:policy_row_count', len(dp_policy_rows) == sku['exact_valuation_dp']['policy_row_count'], len(dp_policy_rows), sku['exact_valuation_dp']['policy_row_count'])
        for method, expected in sku['exact_valuation_dp']['expected'].items():
            row = dp_rows.get(method)
            add(f'sku_exact_valuation_dp:{method}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            for col, expected_value in expected.items():
                add(f'sku_exact_valuation_dp:{method}:{col}', close(float(row[col]), expected_value), float(row[col]), expected_value)
        action = dp_rows.get('exact_dp_action_only_fixed_theta')
        full_dp = dp_rows.get('exact_dp_full_order_and_valuation_control')
        if action and full_dp:
            add('sku_exact_valuation_dp:full_welfare_beats_action', float(full_dp['expected_avg_welfare']) > float(action['expected_avg_welfare']), full_dp['expected_avg_welfare'], f'> {action["expected_avg_welfare"]}')
            add('sku_exact_valuation_dp:theta_free_cost_same', close(float(full_dp['theta_free_expected_avg_cost']), float(action['theta_free_expected_avg_cost'])), full_dp['theta_free_expected_avg_cost'], action['theta_free_expected_avg_cost'])

    if 'budget_frontier_audit' in manifest:
        audit_rows = {int(r['evaluation_budget']): r for r in rows('exp3_equal_evaluation_audit.csv')}
        for budget_text, expected in manifest['budget_frontier_audit'].items():
            budget = int(budget_text)
            row = audit_rows.get(budget)
            add(f'budget_audit:{budget}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'budget_audit:{budget}:leader', row['leader'] == expected['leader'], row['leader'], expected['leader'])
            observed_margin = float(row['full_minus_best_non_ndu'])
            add(
                f'budget_audit:{budget}:full_minus_best_non_ndu',
                close(observed_margin, expected['full_minus_best_non_ndu']),
                observed_margin,
                expected['full_minus_best_non_ndu'],
            )

    if 'compact_equal_evaluation_audit' in manifest:
        compact = manifest['compact_equal_evaluation_audit']
        for exp_name, exp_cfg in compact['experiments'].items():
            audit_rows = {int(r['evaluation_budget']): r for r in rows(f'{exp_name}_equal_evaluation_audit.csv')}
            add(f'compact_equal_eval:{exp_name}:row_count', len(audit_rows) == len(exp_cfg['budgets']), len(audit_rows), len(exp_cfg['budgets']))
            for budget_text, expected in exp_cfg['budgets'].items():
                budget = int(budget_text)
                row = audit_rows.get(budget)
                add(f'compact_equal_eval:{exp_name}:{budget}:row_exists', row is not None, bool(row), True)
                if row is None:
                    continue
                add(f'compact_equal_eval:{exp_name}:{budget}:seed_count', int(row['seed_count']) == compact['seed_count'], row['seed_count'], compact['seed_count'])
                add(f'compact_equal_eval:{exp_name}:{budget}:leader', row['leader'] == expected['leader'], row['leader'], expected['leader'])
                observed_margin = float(row['full_minus_best_non_ndu'])
                add(
                    f'compact_equal_eval:{exp_name}:{budget}:full_minus_best_non_ndu',
                    close(observed_margin, expected['full_minus_best_non_ndu']),
                    observed_margin,
                    expected['full_minus_best_non_ndu'],
                )


    if 'same_budget_parameter_controlled' in manifest:
        audit = manifest['same_budget_parameter_controlled']
        audit_rows = {r['experiment']: r for r in rows('same_budget_parameter_controlled_audit.csv')}
        add('same_budget_parameter_controlled:audit_row_count', len(audit_rows) == audit['audit_row_count'], len(audit_rows), audit['audit_row_count'])
        for exp_name, expected in audit['experiments'].items():
            row = audit_rows.get(exp_name)
            add(f'same_budget_parameter_controlled:{exp_name}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'same_budget_parameter_controlled:{exp_name}:seed_count', int(row['seed_count']) == audit['seed_count'], row['seed_count'], audit['seed_count'])
            add(f'same_budget_parameter_controlled:{exp_name}:param_dim', int(row['param_dim']) == expected['param_dim'], row['param_dim'], expected['param_dim'])
            add(f'same_budget_parameter_controlled:{exp_name}:evaluation_budget', int(row['evaluation_budget']) == expected['evaluation_budget'], row['evaluation_budget'], expected['evaluation_budget'])
            add(f'same_budget_parameter_controlled:{exp_name}:leader', row['leader'] == expected['leader'], row['leader'], expected['leader'])
            add(f'same_budget_parameter_controlled:{exp_name}:best_non_ndu_method', row['best_non_ndu_method'] == expected['best_non_ndu_method'], row['best_non_ndu_method'], expected['best_non_ndu_method'])
            for col in ['full_ndu_value', 'best_non_ndu_value', 'full_minus_best_non_ndu']:
                add(f'same_budget_parameter_controlled:{exp_name}:{col}', close(float(row[col]), expected[col]), float(row[col]), expected[col])
            full_row = experiment_method_row('same_budget_parameter_controlled_metrics.csv', exp_name, 'full_ndu_joint')
            add(f'same_budget_parameter_controlled:{exp_name}:metric_matches_audit', close(float(full_row[expected['primary_metric']]), expected['full_ndu_value']), float(full_row[expected['primary_metric']]), expected['full_ndu_value'])

    if 'neural_solver_validation' in manifest:
        audit = manifest['neural_solver_validation']
        metric_rows = rows('neural_solver_validation_metrics.csv')
        epsilons = sorted({r['epsilon'] for r in metric_rows}, key=float, reverse=True)
        add('neural_solver_validation:epsilon_count', len(epsilons) == len(audit['epsilons']), epsilons, audit['epsilons'])
        for eps, expected in audit['expected'].items():
            direct = epsilon_method_row('neural_solver_validation_metrics.csv', eps, 'direct_p_neural')
            zinvert = epsilon_method_row('neural_solver_validation_metrics.csv', eps, 'z_inversion_neural')
            oracle = epsilon_method_row('neural_solver_validation_metrics.csv', eps, 'exact_hjb_oracle')
            ratio = epsilon_method_row('neural_solver_validation_metrics.csv', eps, 'z_vs_direct_ratio')
            add(f'neural_solver_validation:{eps}:direct_seed_count', int(direct['seed_count']) == audit['seed_count'], direct['seed_count'], audit['seed_count'])
            add(f'neural_solver_validation:{eps}:z_seed_count', int(zinvert['seed_count']) == audit['seed_count'], zinvert['seed_count'], audit['seed_count'])
            add(f'neural_solver_validation:{eps}:oracle_zero_theta_rmse', close(float(oracle['theta_rmse']), 0.0), oracle['theta_rmse'], 0.0)
            add(f'neural_solver_validation:{eps}:direct_theta_rmse', close(float(direct['theta_rmse']), expected['direct_p_theta_rmse']), float(direct['theta_rmse']), expected['direct_p_theta_rmse'])
            add(f'neural_solver_validation:{eps}:z_theta_rmse', close(float(zinvert['theta_rmse']), expected['z_inversion_theta_rmse']), float(zinvert['theta_rmse']), expected['z_inversion_theta_rmse'])
            add(f'neural_solver_validation:{eps}:ratio_theta_rmse', close(float(ratio['theta_rmse']), expected['z_over_direct_theta_rmse_ratio']), float(ratio['theta_rmse']), expected['z_over_direct_theta_rmse_ratio'])
            add(f'neural_solver_validation:{eps}:z_worse_than_direct', float(zinvert['theta_rmse']) > float(direct['theta_rmse']), zinvert['theta_rmse'], f'> {direct["theta_rmse"]}')



    if 'theory_constant_audit' in manifest:
        audit = manifest['theory_constant_audit']
        theory_rows = {r['instance']: r for r in rows('theory_small_coupling_constants.csv')}
        add('theory_constants:row_count', len(theory_rows) == audit['row_count'], len(theory_rows), audit['row_count'])
        for instance, expected in audit['expected'].items():
            row = theory_rows.get(instance)
            add(f'theory_constants:{instance}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            for col in ['L_alpha', 'Lambda_epsilon', 'C_X', 'C_B', 'q_epsilon']:
                add(f'theory_constants:{instance}:{col}', close(float(row[col]), expected[col]), float(row[col]), expected[col])
            add(
                f'theory_constants:{instance}:condition_holds',
                int(row['condition_holds']) == int(expected['condition_holds']),
                row['condition_holds'],
                expected['condition_holds'],
            )

    if 'theory_covered_hjb_audit' in manifest:
        audit = manifest['theory_covered_hjb_audit']
        theory_rows = rows('theory_covered_hjb_audit.csv')
        add('theory_covered_hjb:row_count', len(theory_rows) == audit['row_count'], len(theory_rows), audit['row_count'])
        if theory_rows:
            row = theory_rows[0]
            add('theory_covered_hjb:instance', row['instance'] == audit['instance'], row['instance'], audit['instance'])
            for col, expected in audit['expected'].items():
                if col == 'small_coupling_holds':
                    add(f'theory_covered_hjb:{col}', int(row[col]) == int(expected), row[col], expected)
                else:
                    add(f'theory_covered_hjb:{col}', close(float(row[col]), expected), float(row[col]), expected)
            add('theory_covered_hjb:small_coupling_true', int(row['small_coupling_holds']) == 1, row['small_coupling_holds'], 1)
            add('theory_covered_hjb:compact_control_set', int(row.get('compact_control_set', '0')) == 1, row.get('compact_control_set'), 1)
            add('theory_covered_hjb:selector_clipped', int(row.get('selector_clipped', '0')) == 1, row.get('selector_clipped'), 1)
            add('theory_covered_hjb:grid_clipping_inactive', int(row.get('grid_clipping_inactive', '0')) == 1, row.get('grid_clipping_inactive'), 1)
            add('theory_covered_hjb:unclipped_controls_inside_bound', max(abs(float(row.get('max_abs_unclipped_a_on_grid', 'inf'))), abs(float(row.get('max_abs_unclipped_theta_on_grid', 'inf')))) < float(row.get('control_bound', '0')), max(abs(float(row.get('max_abs_unclipped_a_on_grid', 'inf'))), abs(float(row.get('max_abs_unclipped_theta_on_grid', 'inf')))), f'< {row.get("control_bound")}')
            add('theory_covered_hjb:residual_tiny', float(row['hjb_quadratic_residual_max']) < audit['residual_threshold'], row['hjb_quadratic_residual_max'], f'< {audit["residual_threshold"]}')

    if 'uniform_hjb_greedy_certificate' in manifest:
        audit = manifest['uniform_hjb_greedy_certificate']
        cert_rows = {r['gamma']: r for r in rows('uniform_hjb_greedy_certificate.csv')}
        add('uniform_hjb_greedy:row_count', len(cert_rows) == audit['row_count'], len(cert_rows), audit['row_count'])
        for gamma in audit['gammas']:
            add(f'uniform_hjb_greedy:{gamma}:row_exists', gamma in cert_rows, gamma if gamma in cert_rows else 'missing', gamma)
        exact = cert_rows.get('0')
        small = cert_rows.get('0.01')
        if exact:
            add('uniform_hjb_greedy:exact_status', exact['certificate_status'] == 'exact_uniform_hjb_solve', exact['certificate_status'], 'exact_uniform_hjb_solve')
            add('uniform_hjb_greedy:exact_residual_tiny', float(exact['uniform_optimal_hamiltonian_residual_sup']) < audit['exact_residual_threshold'], exact['uniform_optimal_hamiltonian_residual_sup'], f'< {audit["exact_residual_threshold"]}')
            add('uniform_hjb_greedy:exact_terminal_zero', close(float(exact['uniform_terminal_residual_sup']), 0.0), exact['uniform_terminal_residual_sup'], 0.0)
            add('uniform_hjb_greedy:exact_greedy_zero', close(float(exact['uniform_greedy_gap_sup']), 0.0), exact['uniform_greedy_gap_sup'], 0.0)
            add('uniform_hjb_greedy:controls_inside_bound_exact', int(exact['controls_inside_compact_bound']) == 1, exact['controls_inside_compact_bound'], 1)
        prev = None
        for gamma in ['0.08', '0.04', '0.02', '0.01']:
            row = cert_rows.get(gamma)
            if not row:
                continue
            add(f'uniform_hjb_greedy:{gamma}:status', row['certificate_status'] == 'certificate_gap_sequence', row['certificate_status'], 'certificate_gap_sequence')
            add(f'uniform_hjb_greedy:{gamma}:controls_inside_bound', int(row['controls_inside_compact_bound']) == 1, row['controls_inside_compact_bound'], 1)
            bound = float(row['certificate_value_policy_bound_proxy'])
            if prev is not None:
                add(f'uniform_hjb_greedy:{gamma}:bound_decreases', bound < prev, bound, f'< {prev}')
            prev = bound
        if small:
            for col, expected_value in audit.get('expected_gamma_0_01', {}).items():
                add(f'uniform_hjb_greedy:0.01:{col}', close(float(small[col]), expected_value), float(small[col]), expected_value)
            add('uniform_hjb_greedy:small_bound_below_0_021', float(small['certificate_value_policy_bound_proxy']) < 0.021, small['certificate_value_policy_bound_proxy'], '< 0.021')

    if 'inventory_finite_cover_hjb_certificate' in manifest:
        audit = manifest['inventory_finite_cover_hjb_certificate']
        cert_rows = {r['method']: r for r in rows('inventory_finite_cover_hjb_certificate.csv')}
        add('inventory_finite_cover_hjb:row_count', len(cert_rows) == audit['row_count'], len(cert_rows), audit['row_count'])
        add('inventory_finite_cover_hjb:methods', sorted(cert_rows) == sorted(audit['methods']), sorted(cert_rows), sorted(audit['methods']))
        for method in audit['methods']:
            row = cert_rows.get(method)
            add(f'inventory_finite_cover_hjb:{method}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'inventory_finite_cover_hjb:{method}:status', row['certificate_status'] == 'exact_finite_cover_hjb_solve', row['certificate_status'], 'exact_finite_cover_hjb_solve')
            add(f'inventory_finite_cover_hjb:{method}:terminal_zero', close(float(row['terminal_residual_sup']), 0.0), row['terminal_residual_sup'], 0.0)
            add(f'inventory_finite_cover_hjb:{method}:bellman_residual_zero', close(float(row['bellman_residual_sup_abs']), 0.0), row['bellman_residual_sup_abs'], 0.0)
            add(f'inventory_finite_cover_hjb:{method}:greedy_gap_zero', close(float(row['greedy_gap_sup']), 0.0), row['greedy_gap_sup'], 0.0)
            add(f'inventory_finite_cover_hjb:{method}:certificate_bound_zero', float(row['finite_cover_certificate_bound']) <= audit['residual_threshold'], row['finite_cover_certificate_bound'], f'<= {audit["residual_threshold"]}')
        full = cert_rows.get('full_valuation_control_exact_dp')
        if full:
            for col, expected_value in audit.get('expected_full', {}).items():
                add(f'inventory_finite_cover_hjb:full:{col}', close(float(full[col]), expected_value), float(full[col]), expected_value)
            add('inventory_finite_cover_hjb:full_contains_action_only', int(full['contains_action_only_face']) == 1, full['contains_action_only_face'], 1)
            add('inventory_finite_cover_hjb:full_contains_valuation_only', int(full['contains_valuation_only_face']) == 1, full['contains_valuation_only_face'], 1)
            add('inventory_finite_cover_hjb:full_margin_positive', float(full['margin_vs_action_only_avg']) > audit['min_full_margin_vs_action_only_avg'], full['margin_vs_action_only_avg'], f'> {audit["min_full_margin_vs_action_only_avg"]}')

    if 'inventory_cover_refinement_certificate' in manifest:
        audit = manifest['inventory_cover_refinement_certificate']
        refine_rows = {r['cover_name']: r for r in rows('inventory_cover_refinement_certificate.csv')}
        add('inventory_cover_refinement:row_count', len(refine_rows) == audit['row_count'], len(refine_rows), audit['row_count'])
        add('inventory_cover_refinement:covers', sorted(refine_rows) == sorted(audit['covers']), sorted(refine_rows), sorted(audit['covers']))
        prev_value = None
        prev_radius = None
        for cover in audit['covers']:
            row = refine_rows.get(cover)
            add(f'inventory_cover_refinement:{cover}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'inventory_cover_refinement:{cover}:status', row['certificate_status'] == 'exact_refined_finite_cover_hjb_solve', row['certificate_status'], 'exact_refined_finite_cover_hjb_solve')
            add(f'inventory_cover_refinement:{cover}:terminal_zero', close(float(row['terminal_residual_sup']), 0.0), row['terminal_residual_sup'], 0.0)
            add(f'inventory_cover_refinement:{cover}:bellman_zero', close(float(row['bellman_residual_sup_abs']), 0.0), row['bellman_residual_sup_abs'], 0.0)
            add(f'inventory_cover_refinement:{cover}:greedy_zero', close(float(row['greedy_gap_sup']), 0.0), row['greedy_gap_sup'], 0.0)
            value = float(row['avg_welfare_at_initial_mixture'])
            radius = float(row['action_fill_distance_proxy'])
            if prev_value is not None:
                add(f'inventory_cover_refinement:{cover}:value_monotone', value >= prev_value - 1e-10, value, f'>= {prev_value}')
                add(f'inventory_cover_refinement:{cover}:radius_monotone', radius <= prev_radius + 1e-10, radius, f'<= {prev_radius}')
            prev_value = value
            prev_radius = radius
        final = refine_rows.get('nested_full_r48_16')
        if final:
            for col, expected_value in audit.get('expected_final', {}).items():
                add(f'inventory_cover_refinement:final:{col}', close(float(final[col]), expected_value), float(final[col]), expected_value)
            add('inventory_cover_refinement:final_margin_positive', float(final['margin_vs_action_only_avg']) > audit['min_final_margin_vs_action_only_avg'], final['margin_vs_action_only_avg'], f'> {audit["min_final_margin_vs_action_only_avg"]}')
            add('inventory_cover_refinement:final_radius_below_threshold', float(final['action_fill_distance_proxy']) < audit['max_final_fill_distance_proxy'], final['action_fill_distance_proxy'], f'< {audit["max_final_fill_distance_proxy"]}')

    if 'hjb_solver_certificate_ladder' in manifest:
        audit = manifest['hjb_solver_certificate_ladder']
        ladder_rows = rows('hjb_solver_certificate_ladder.csv')
        ladder_by_rung = {r['rung']: r for r in ladder_rows}
        add('hjb_solver_certificate_ladder:row_count', len(ladder_rows) == audit['row_count'], len(ladder_rows), audit['row_count'])
        add('hjb_solver_certificate_ladder:rungs', sorted(ladder_by_rung) == sorted(audit['rungs']), sorted(ladder_by_rung), sorted(audit['rungs']))
        orders = [int(r['ladder_order']) for r in ladder_rows]
        add('hjb_solver_certificate_ladder:orders_consecutive', orders == list(range(1, len(ladder_rows) + 1)), orders, list(range(1, len(ladder_rows) + 1)))
        for rung, expected_status in audit.get('expected_statuses', {}).items():
            row = ladder_by_rung.get(rung)
            add(f'hjb_solver_certificate_ladder:{rung}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'hjb_solver_certificate_ladder:{rung}:status', row['status'] == expected_status, row['status'], expected_status)
            for token in audit.get('required_interpretation_tokens', {}).get(rung, []):
                add(f'hjb_solver_certificate_ladder:{rung}:token:{token}', token in row['interpretation'], row['interpretation'], f'contains {token}')
        finite = ladder_by_rung.get('exact_inventory_finite_cover_certificate')
        if finite:
            add('hjb_solver_certificate_ladder:finite_bound_zero', finite['residual_or_bound'] == '0', finite['residual_or_bound'], '0')
            add('hjb_solver_certificate_ladder:finite_margin_positive', '0.19769026726' in finite['policy_or_welfare'], finite['policy_or_welfare'], 'contains 0.19769026726')
        refine = ladder_by_rung.get('nested_inventory_cover_refinement_sequence')
        if refine:
            add('hjb_solver_certificate_ladder:refinement_radius_reported', '1.20598507453->0.54626001135' in refine['terminal_or_guard'], refine['terminal_or_guard'], 'radius shrink string')
            add('hjb_solver_certificate_ladder:refinement_margin_reported', '0->0.19769026726' in refine['policy_or_welfare'], refine['policy_or_welfare'], 'margin string')
        exp1 = ladder_by_rung.get('sampled_exp1_hbo_nbo_certificate_gap_closure')
        if exp1:
            add('hjb_solver_certificate_ladder:exp1_residual_ratio_below_0_15', float(exp1['residual_or_bound'].split('=')[1]) < 0.15, exp1['residual_or_bound'], '< 0.15')
        inv = ladder_by_rung.get('sampled_inventory_hbo_nbo_certificate_gap_closure')
        if inv:
            native_part = inv['residual_or_bound'].split(';')[0].split('=')[1]
            add('hjb_solver_certificate_ladder:inventory_native_ratio_below_0_20', float(native_part) < 0.20, inv['residual_or_bound'], '< 0.20')

    if 'referee_objection_closure_audit' in manifest:
        audit = manifest['referee_objection_closure_audit']
        objection_rows = {r['objection_id']: r for r in rows('referee_objection_closure_audit.csv')}
        add('referee_objection_closure:row_count', len(objection_rows) == audit['row_count'], len(objection_rows), audit['row_count'])
        add('referee_objection_closure:objections', sorted(objection_rows) == sorted(audit['objections']), sorted(objection_rows), sorted(audit['objections']))
        for objection_id, expected in audit.get('expected', {}).items():
            row = objection_rows.get(objection_id)
            add(f'referee_objection_closure:{objection_id}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'referee_objection_closure:{objection_id}:status', row['closure_status'] == expected['closure_status'], row['closure_status'], expected['closure_status'])
            for token in expected.get('required_tokens', []):
                text = ' '.join([row.get('theorem_or_proof_anchor', ''), row.get('audit_sources', ''), row.get('observed_value', ''), row.get('interpretation', '')])
                add(f'referee_objection_closure:{objection_id}:token:{token}', token in text, text, f'contains {token}')
        gen = objection_rows.get('generalized_rl_is_only_state_augmentation')
        if gen:
            add('referee_objection_closure:strict_margin_gt_0_19', float(gen['observed_value']) > 0.19, gen['observed_value'], '> 0.19')
        cert = objection_rows.get('nbo_hjb_solver_certificate_missing')
        if cert:
            compact, uniform = [float(x.strip()) for x in cert['observed_value'].split(';')]
            add('referee_objection_closure:compact_residual_lt_1e-12', compact < 1e-12, compact, '< 1e-12')
            add('referee_objection_closure:uniform_bound_lt_0_021', uniform < 0.021, uniform, '< 0.021')
        sampled = objection_rows.get('large_neural_rows_are_sampled_only')
        if sampled:
            parts = dict(part.split('=') for part in sampled['observed_value'].split('; '))
            add('referee_objection_closure:sampled_exp1_lt_0_15', float(parts['exp1']) < 0.15, parts['exp1'], '< 0.15')
            add('referee_objection_closure:sampled_inventory_lt_0_20', float(parts['inventory']) < 0.20, parts['inventory'], '< 0.20')
            add('referee_objection_closure:ladder_rows_7', int(parts['ladder_rows']) == 7, parts['ladder_rows'], 7)
        fairness = objection_rows.get('fairness_same_information_same_budget')
        if fairness:
            parts = dict(part.split('=') for part in fairness['observed_value'].split('; '))
            add('referee_objection_closure:fairness_exp1_positive', float(parts['exp1']) > 0.02, parts['exp1'], '> 0.02')
            add('referee_objection_closure:fairness_exp2_parity', float(parts['exp2_abs']) < 2e-6, parts['exp2_abs'], '< 2e-6')
            add('referee_objection_closure:fairness_exp3_feasible_positive', float(parts['exp3_feasible']) > 0.01, parts['exp3_feasible'], '> 0.01')
            add('referee_objection_closure:fairness_selected_exp3_positive', float(parts['exp3_selected']) > 0.0, parts['exp3_selected'], '> 0')

    if 'neural_validation_cover_hjb_gap_audit' in manifest:
        audit = manifest['neural_validation_cover_hjb_gap_audit']
        vc_rows = {r['experiment']: r for r in rows('neural_validation_cover_hjb_gap_audit.csv')}
        add('neural_validation_cover:row_count', len(vc_rows) == audit['row_count'], len(vc_rows), audit['row_count'])
        add('neural_validation_cover:experiments', sorted(vc_rows) == sorted(audit['experiments']), sorted(vc_rows), sorted(audit['experiments']))
        for experiment, expected in audit.get('expected', {}).items():
            row = vc_rows.get(experiment)
            add(f'neural_validation_cover:{experiment}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'neural_validation_cover:{experiment}:status', row['guard_status'] == expected['guard_status'], row['guard_status'], expected['guard_status'])
            add(f'neural_validation_cover:{experiment}:tuple_complete', int(row['certificate_tuple_complete']) == 1, row['certificate_tuple_complete'], 1)
            add(f'neural_validation_cover:{experiment}:validation_pairs', int(row['validation_pairs']) >= expected['min_validation_pairs'], row['validation_pairs'], f'>= {expected["min_validation_pairs"]}')
            add(f'neural_validation_cover:{experiment}:native_ratio', float(row['native_hjb_ratio_vs_headline']) < expected['max_native_hjb_ratio'], row['native_hjb_ratio_vs_headline'], f'< {expected["max_native_hjb_ratio"]}')
            add(f'neural_validation_cover:{experiment}:normalized_ratio', float(row['normalized_rmse_ratio_vs_headline']) < expected['max_normalized_rmse_ratio'], row['normalized_rmse_ratio_vs_headline'], f'< {expected["max_normalized_rmse_ratio"]}')
            add(f'neural_validation_cover:{experiment}:terminal_ratio', float(row['terminal_loss_ratio_vs_headline']) < expected['max_terminal_loss_ratio'], row['terminal_loss_ratio_vs_headline'], f'< {expected["max_terminal_loss_ratio"]}')
            add(f'neural_validation_cover:{experiment}:greedy_p95', float(row['greedy_gap_p95']) < expected['max_greedy_gap_p95'], row['greedy_gap_p95'], f'< {expected["max_greedy_gap_p95"]}')
            add(f'neural_validation_cover:{experiment}:heldout_nonnegative', float(row['heldout_delta_vs_headline']) >= expected['min_heldout_delta'], row['heldout_delta_vs_headline'], f'>= {expected["min_heldout_delta"]}')

    if 'neural_validation_cover_replay_certificate' in manifest:
        audit = manifest['neural_validation_cover_replay_certificate']
        replay_rows = {r['experiment']: r for r in rows('neural_validation_cover_replay_certificate.csv')}
        add('neural_validation_cover_replay:row_count', len(replay_rows) == audit['row_count'], len(replay_rows), audit['row_count'])
        add('neural_validation_cover_replay:experiments', sorted(replay_rows) == sorted(audit['experiments']), sorted(replay_rows), sorted(audit['experiments']))
        for experiment in audit['experiments']:
            row = replay_rows.get(experiment)
            add(f'neural_validation_cover_replay:{experiment}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'neural_validation_cover_replay:{experiment}:status', row['certificate_status'] == audit['certificate_status'], row['certificate_status'], audit['certificate_status'])
            add(f'neural_validation_cover_replay:{experiment}:all_guards_pass', int(row['all_guards_pass']) == 1, row['all_guards_pass'], 1)
            add(f'neural_validation_cover_replay:{experiment}:source_hashes_manifest_match', 'manifest_mismatch' not in row['source_hash_bundle'], row['source_hash_bundle'], 'all manifest_match')
            for col in [
                'check_tuple_complete',
                'check_validation_pairs',
                'check_native_ratio',
                'check_normalized_ratio',
                'check_terminal_ratio',
                'check_greedy_p95',
                'check_heldout',
                'check_greedy_source_match',
                'check_stability_source_match',
            ]:
                add(f'neural_validation_cover_replay:{experiment}:{col}', int(row[col]) == 1, row[col], 1)

    if 'validation_cover_stability_guard_audit' in manifest:
        audit = manifest['validation_cover_stability_guard_audit']
        guard_rows = {r['experiment']: r for r in rows('validation_cover_stability_guard_audit.csv')}
        add('validation_cover_stability:row_count', len(guard_rows) == audit['row_count'], len(guard_rows), audit['row_count'])
        add('validation_cover_stability:experiments', sorted(guard_rows) == sorted(audit['experiments']), sorted(guard_rows), sorted(audit['experiments']))
        for experiment, expected in audit.get('expected', {}).items():
            row = guard_rows.get(experiment)
            add(f'validation_cover_stability:{experiment}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'validation_cover_stability:{experiment}:status', row['stability_guard_status'] == expected['stability_guard_status'], row['stability_guard_status'], expected['stability_guard_status'])
            add(f'validation_cover_stability:{experiment}:tuple_complete', int(row['tuple_complete']) == 1, row['tuple_complete'], 1)
            add(f'validation_cover_stability:{experiment}:density', float(row['validation_density_proxy']) > expected['min_validation_density_proxy'], row['validation_density_proxy'], f'> {expected["min_validation_density_proxy"]}')
            add(f'validation_cover_stability:{experiment}:tail_ratio', float(row['greedy_tail_ratio_sup_over_p95']) < expected['max_greedy_tail_ratio'], row['greedy_tail_ratio_sup_over_p95'], f'< {expected["max_greedy_tail_ratio"]}')
            add(f'validation_cover_stability:{experiment}:native_ratio', float(row['native_hjb_ratio_vs_headline']) < expected['max_native_hjb_ratio'], row['native_hjb_ratio_vs_headline'], f'< {expected["max_native_hjb_ratio"]}')
            add(f'validation_cover_stability:{experiment}:normalized_ratio', float(row['normalized_rmse_ratio_vs_headline']) < expected['max_normalized_rmse_ratio'], row['normalized_rmse_ratio_vs_headline'], f'< {expected["max_normalized_rmse_ratio"]}')
            add(f'validation_cover_stability:{experiment}:terminal_ratio', float(row['terminal_loss_ratio_vs_headline']) < expected['max_terminal_loss_ratio'], row['terminal_loss_ratio_vs_headline'], f'< {expected["max_terminal_loss_ratio"]}')
            add(f'validation_cover_stability:{experiment}:heldout_nonnegative', float(row['heldout_delta_vs_headline']) >= expected['min_heldout_delta'], row['heldout_delta_vs_headline'], f'>= {expected["min_heldout_delta"]}')

    if 'neural_empirical_envelope_audit' in manifest:
        audit = manifest['neural_empirical_envelope_audit']
        envelope_rows = {r['experiment']: r for r in rows('neural_empirical_envelope_audit.csv')}
        add('neural_empirical_envelope:row_count', len(envelope_rows) == audit['row_count'], len(envelope_rows), audit['row_count'])
        add('neural_empirical_envelope:experiments', sorted(envelope_rows) == sorted(audit['experiments']), sorted(envelope_rows), sorted(audit['experiments']))
        for experiment, expected in audit.get('expected', {}).items():
            row = envelope_rows.get(experiment)
            add(f'neural_empirical_envelope:{experiment}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'neural_empirical_envelope:{experiment}:status', row['envelope_status'] == expected['envelope_status'], row['envelope_status'], expected['envelope_status'])
            add(f'neural_empirical_envelope:{experiment}:all_guards_pass', int(row['all_envelope_guards_pass']) == 1, row['all_envelope_guards_pass'], 1)
            add(f'neural_empirical_envelope:{experiment}:score', float(row['empirical_envelope_score']) < expected['max_empirical_envelope_score'], row['empirical_envelope_score'], f'< {expected["max_empirical_envelope_score"]}')
            add(f'neural_empirical_envelope:{experiment}:tail_ratio', float(row['greedy_tail_ratio_sup_over_p95']) < expected['max_greedy_tail_ratio'], row['greedy_tail_ratio_sup_over_p95'], f'< {expected["max_greedy_tail_ratio"]}')
            add(f'neural_empirical_envelope:{experiment}:heldout_nonnegative', float(row['heldout_delta_vs_headline']) >= expected['min_heldout_delta'], row['heldout_delta_vs_headline'], f'>= {expected["min_heldout_delta"]}')
            add(f'neural_empirical_envelope:{experiment}:replay_status', row['replay_certificate_status'] == 'deterministic_replay_certificate_pass', row['replay_certificate_status'], 'deterministic_replay_certificate_pass')
            add(f'neural_empirical_envelope:{experiment}:stability_status', row['stability_guard_status'] == 'validation_cover_stability_guard_pass', row['stability_guard_status'], 'validation_cover_stability_guard_pass')

    if 'neural_interval_domain_certificate' in manifest:
        audit = manifest['neural_interval_domain_certificate']
        interval_rows = {r['experiment']: r for r in rows('neural_interval_domain_certificate.csv')}
        add('neural_interval_domain:row_count', len(interval_rows) == audit['row_count'], len(interval_rows), audit['row_count'])
        add('neural_interval_domain:experiments', sorted(interval_rows) == sorted(audit['experiments']), sorted(interval_rows), sorted(audit['experiments']))
        for experiment, expected in audit.get('expected', {}).items():
            row = interval_rows.get(experiment)
            add(f'neural_interval_domain:{experiment}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'neural_interval_domain:{experiment}:status', row['interval_certificate_status'] == expected['interval_certificate_status'], row['interval_certificate_status'], expected['interval_certificate_status'])
            add(f'neural_interval_domain:{experiment}:all_guards_pass', int(row['all_interval_guards_pass']) == 1, row['all_interval_guards_pass'], 1)
            add(f'neural_interval_domain:{experiment}:score', float(row['interval_certificate_score']) < expected['max_interval_certificate_score'], row['interval_certificate_score'], f'< {expected["max_interval_certificate_score"]}')
            add(f'neural_interval_domain:{experiment}:residual_bound', float(row['residual_interval_bound']) < expected['max_residual_interval_bound'], row['residual_interval_bound'], f'< {expected["max_residual_interval_bound"]}')
            add(f'neural_interval_domain:{experiment}:terminal_bound', float(row['terminal_interval_bound']) < expected['max_terminal_interval_bound'], row['terminal_interval_bound'], f'< {expected["max_terminal_interval_bound"]}')
            add(f'neural_interval_domain:{experiment}:greedy_bound', float(row['greedy_interval_bound']) < expected['max_greedy_interval_bound'], row['greedy_interval_bound'], f'< {expected["max_greedy_interval_bound"]}')
            add(f'neural_interval_domain:{experiment}:envelope_status', row['empirical_envelope_status'] == 'empirical_envelope_guard_pass', row['empirical_envelope_status'], 'empirical_envelope_guard_pass')

    if 'neural_interval_sensitivity_audit' in manifest:
        audit = manifest['neural_interval_sensitivity_audit']
        sensitivity_rows = rows('neural_interval_sensitivity_audit.csv')
        add('neural_interval_sensitivity:row_count', len(sensitivity_rows) == audit['row_count'], len(sensitivity_rows), audit['row_count'])
        observed_experiments = sorted({r['experiment'] for r in sensitivity_rows})
        observed_scenarios = sorted({r['scenario'] for r in sensitivity_rows})
        add('neural_interval_sensitivity:experiments', observed_experiments == sorted(audit['experiments']), observed_experiments, sorted(audit['experiments']))
        add('neural_interval_sensitivity:scenarios', observed_scenarios == sorted(audit['scenarios']), observed_scenarios, sorted(audit['scenarios']))
        for row in sensitivity_rows:
            key = f"{row['experiment']}:{row['scenario']}"
            expected = audit.get('expected', {}).get(row['experiment'], {})
            add(f'neural_interval_sensitivity:{key}:status', row['sensitivity_status'] == 'interval_sensitivity_guard_pass', row['sensitivity_status'], 'interval_sensitivity_guard_pass')
            add(f'neural_interval_sensitivity:{key}:all_guards_pass', int(row['all_sensitivity_guards_pass']) == 1, row['all_sensitivity_guards_pass'], 1)
            add(f'neural_interval_sensitivity:{key}:score', float(row['sensitivity_score']) < float(row['sensitivity_threshold']), row['sensitivity_score'], f"< {row['sensitivity_threshold']}")
            if expected:
                add(f'neural_interval_sensitivity:{key}:score_cap', float(row['sensitivity_score']) < expected['max_sensitivity_score'], row['sensitivity_score'], f'< {expected["max_sensitivity_score"]}')
                add(f'neural_interval_sensitivity:{key}:slope_multiplier_capacity', float(row['max_slope_multiplier_at_current_cover']) > expected['min_max_slope_multiplier'], row['max_slope_multiplier_at_current_cover'], f'> {expected["min_max_slope_multiplier"]}')
        for experiment, expected in audit.get('expected', {}).items():
            stress = [r for r in sensitivity_rows if r['experiment'] == experiment and r['scenario'] == 'slope_stress_1p5x_current_cover']
            add(f'neural_interval_sensitivity:{experiment}:stress_row_exists', len(stress) == 1, len(stress), 1)
            if stress:
                add(f'neural_interval_sensitivity:{experiment}:stress_score', float(stress[0]['sensitivity_score']) < expected['max_1p5_slope_stress_score'], stress[0]['sensitivity_score'], f'< {expected["max_1p5_slope_stress_score"]}')

    if 'bounded_architecture_lipschitz_budget_audit' in manifest:
        audit = manifest['bounded_architecture_lipschitz_budget_audit']
        budget_rows = rows('bounded_architecture_lipschitz_budget_audit.csv')
        observed_components = sorted({r['component'] for r in budget_rows})
        add('bounded_architecture_lipschitz_budget:row_count', len(budget_rows) == audit['row_count'], len(budget_rows), audit['row_count'])
        add('bounded_architecture_lipschitz_budget:components', observed_components == sorted(audit['components']), observed_components, sorted(audit['components']))
        max_budget = max(float(r['budget_product']) for r in budget_rows) if budget_rows else float('inf')
        add('bounded_architecture_lipschitz_budget:max_budget_product', max_budget <= audit['max_budget_product'], max_budget, f"<= {audit['max_budget_product']}")
        for row in budget_rows:
            component = row['component']
            add(f'bounded_architecture_lipschitz_budget:{component}:status', row['status'] == 'budget_recorded', row['status'], 'budget_recorded')
            add(f'bounded_architecture_lipschitz_budget:{component}:threshold', float(row['budget_product']) <= float(row['threshold']), row['budget_product'], f"<= {row['threshold']}")
            add(f'bounded_architecture_lipschitz_budget:{component}:interpretation', bool(row['interpretation']), row['interpretation'], 'nonempty interpretation')

    if 'bounded_architecture_budget_stress_audit' in manifest:
        audit = manifest['bounded_architecture_budget_stress_audit']
        stress_rows = rows('bounded_architecture_budget_stress_audit.csv')
        observed_components = sorted({r['component'] for r in stress_rows})
        observed_scenarios = sorted({r['scenario'] for r in stress_rows})
        add('bounded_architecture_budget_stress:row_count', len(stress_rows) == audit['row_count'], len(stress_rows), audit['row_count'])
        add('bounded_architecture_budget_stress:components', observed_components == sorted(audit['components']), observed_components, sorted(audit['components']))
        add('bounded_architecture_budget_stress:scenarios', observed_scenarios == sorted(audit['scenarios']), observed_scenarios, sorted(audit['scenarios']))
        max_stressed = max(float(r['stressed_budget_product']) for r in stress_rows) if stress_rows else float('inf')
        min_margin = min(float(r['margin']) for r in stress_rows) if stress_rows else float('-inf')
        add('bounded_architecture_budget_stress:max_stressed_budget', max_stressed <= audit['max_stressed_budget_product'], max_stressed, f"<= {audit['max_stressed_budget_product']}")
        add('bounded_architecture_budget_stress:min_margin', min_margin >= audit['min_margin'], min_margin, f">= {audit['min_margin']}")
        for row in stress_rows:
            key = f"{row['component']}:{row['scenario']}"
            add(f'bounded_architecture_budget_stress:{key}:status', row['stress_status'] == 'budget_stress_guard_pass', row['stress_status'], 'budget_stress_guard_pass')
            add(f'bounded_architecture_budget_stress:{key}:margin_positive', float(row['margin']) > 0.0, row['margin'], '> 0')
            add(f'bounded_architecture_budget_stress:{key}:interpretation', bool(row['interpretation']), row['interpretation'], 'nonempty interpretation')

    if 'neural_guard_cross_artifact_consistency_audit' in manifest:
        audit = manifest['neural_guard_cross_artifact_consistency_audit']
        cross_rows = {r['experiment']: r for r in rows('neural_guard_cross_artifact_consistency_audit.csv')}
        add('neural_guard_cross_artifact:row_count', len(cross_rows) == audit['row_count'], len(cross_rows), audit['row_count'])
        add('neural_guard_cross_artifact:experiments', sorted(cross_rows) == sorted(audit['experiments']), sorted(cross_rows), sorted(audit['experiments']))
        for experiment, expected in audit.get('expected', {}).items():
            row = cross_rows.get(experiment)
            add(f'neural_guard_cross_artifact:{experiment}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'neural_guard_cross_artifact:{experiment}:status', row['consistency_status'] == 'cross_artifact_guard_pass', row['consistency_status'], 'cross_artifact_guard_pass')
            add(f'neural_guard_cross_artifact:{experiment}:required_artifacts', int(row['required_artifacts_present']) == 1, row['required_artifacts_present'], 1)
            add(f'neural_guard_cross_artifact:{experiment}:route', row['validation_cover_route'] == 'validation-cover_not_global_lipschitz', row['validation_cover_route'], 'validation-cover_not_global_lipschitz')
            add(f'neural_guard_cross_artifact:{experiment}:budget_components', int(row['budget_component_count']) == audit['budget_component_count'], row['budget_component_count'], audit['budget_component_count'])
            add(f'neural_guard_cross_artifact:{experiment}:stress_scenarios', int(row['budget_stress_scenario_count']) == audit['budget_stress_scenario_count'], row['budget_stress_scenario_count'], audit['budget_stress_scenario_count'])
            add(f'neural_guard_cross_artifact:{experiment}:stress_margin', float(row['min_budget_stress_margin']) >= audit['min_budget_stress_margin'], row['min_budget_stress_margin'], f">= {audit['min_budget_stress_margin']}")
            add(f'neural_guard_cross_artifact:{experiment}:stressed_budget', float(row['max_stressed_budget_product']) <= audit['max_stressed_budget_product'], row['max_stressed_budget_product'], f"<= {audit['max_stressed_budget_product']}")
            add(f'neural_guard_cross_artifact:{experiment}:sensitivity_score', float(row['max_interval_sensitivity_score']) <= expected['max_interval_sensitivity_score'], row['max_interval_sensitivity_score'], f"<= {expected['max_interval_sensitivity_score']}")
            add(f'neural_guard_cross_artifact:{experiment}:heldout_nonnegative', float(row['heldout_delta_vs_headline']) >= expected['min_heldout_delta'], row['heldout_delta_vs_headline'], f">= {expected['min_heldout_delta']}")
            add(f'neural_guard_cross_artifact:{experiment}:native_ratio', float(row['native_hjb_ratio_vs_headline']) <= expected['max_native_hjb_ratio'], row['native_hjb_ratio_vs_headline'], f"<= {expected['max_native_hjb_ratio']}")
            add(f'neural_guard_cross_artifact:{experiment}:interpretation_boundary', 'not an analytic full-domain neural certificate' in row['interpretation'], row['interpretation'], 'boundary phrase')

    if 'neural_guard_refinement_stress_audit' in manifest:
        audit = manifest['neural_guard_refinement_stress_audit']
        refine_rows = rows('neural_guard_refinement_stress_audit.csv')
        experiments = sorted({r['experiment'] for r in refine_rows})
        scenarios = sorted({r['scenario'] for r in refine_rows})
        add('neural_guard_refinement_stress:row_count', len(refine_rows) == audit['row_count'], len(refine_rows), audit['row_count'])
        add('neural_guard_refinement_stress:experiments', experiments == sorted(audit['experiments']), experiments, sorted(audit['experiments']))
        add('neural_guard_refinement_stress:scenarios', scenarios == sorted(audit['scenarios']), scenarios, sorted(audit['scenarios']))
        for row in refine_rows:
            key = f"{row['experiment']}:{row['scenario']}"
            expected = audit['expected'][row['experiment']]
            add(f'neural_guard_refinement_stress:{key}:status', row['refinement_stress_status'] == 'refinement_stress_guard_pass', row['refinement_stress_status'], 'refinement_stress_guard_pass')
            add(f'neural_guard_refinement_stress:{key}:route', row['validation_cover_route'] == 'validation-cover_not_global_lipschitz', row['validation_cover_route'], 'validation-cover_not_global_lipschitz')
            add(f'neural_guard_refinement_stress:{key}:slack_positive', float(row['sensitivity_slack']) > 0.0, row['sensitivity_slack'], '> 0')
            add(f'neural_guard_refinement_stress:{key}:score_threshold', float(row['adjusted_interval_sensitivity_score']) <= expected['max_adjusted_interval_sensitivity_score'], row['adjusted_interval_sensitivity_score'], f"<= {expected['max_adjusted_interval_sensitivity_score']}")
            add(f'neural_guard_refinement_stress:{key}:stress_margin', float(row['min_budget_stress_margin']) >= audit['min_budget_stress_margin'], row['min_budget_stress_margin'], f">= {audit['min_budget_stress_margin']}")
            add(f'neural_guard_refinement_stress:{key}:heldout_nonnegative', float(row['heldout_delta_vs_headline']) >= expected['min_heldout_delta'], row['heldout_delta_vs_headline'], f">= {expected['min_heldout_delta']}")
            add(f'neural_guard_refinement_stress:{key}:interpretation_boundary', 'not an analytic full-domain neural certificate' in row['interpretation'], row['interpretation'], 'boundary phrase')

    if 'neural_guard_holdout_bootstrap_stability_audit' in manifest:
        audit = manifest['neural_guard_holdout_bootstrap_stability_audit']
        stability_rows = rows('neural_guard_holdout_bootstrap_stability_audit.csv')
        experiments = sorted({r['experiment'] for r in stability_rows})
        schemes = sorted({r['stability_scheme'] for r in stability_rows})
        add('neural_guard_holdout_bootstrap:row_count', len(stability_rows) == audit['row_count'], len(stability_rows), audit['row_count'])
        add('neural_guard_holdout_bootstrap:experiments', experiments == sorted(audit['experiments']), experiments, sorted(audit['experiments']))
        add('neural_guard_holdout_bootstrap:schemes', schemes == sorted(audit['stability_schemes']), schemes, sorted(audit['stability_schemes']))
        for row in stability_rows:
            key = f"{row['experiment']}:{row['stability_scheme']}"
            expected = audit['expected'][row['experiment']]
            add(f'neural_guard_holdout_bootstrap:{key}:status', row['stability_status'] == 'holdout_bootstrap_stability_pass', row['stability_status'], 'holdout_bootstrap_stability_pass')
            add(f'neural_guard_holdout_bootstrap:{key}:route', row['validation_cover_route'] == 'validation-cover_not_global_lipschitz', row['validation_cover_route'], 'validation-cover_not_global_lipschitz')
            add(f'neural_guard_holdout_bootstrap:{key}:slack_floor', float(row['bootstrap_sensitivity_slack_floor']) >= audit['min_bootstrap_sensitivity_slack_floor'], row['bootstrap_sensitivity_slack_floor'], f">= {audit['min_bootstrap_sensitivity_slack_floor']}")
            add(f'neural_guard_holdout_bootstrap:{key}:heldout_floor', float(row['bootstrap_heldout_delta_floor']) >= expected['min_bootstrap_heldout_delta_floor'], row['bootstrap_heldout_delta_floor'], f">= {expected['min_bootstrap_heldout_delta_floor']}")
            add(f'neural_guard_holdout_bootstrap:{key}:stress_margin', float(row['min_budget_stress_margin']) >= audit['min_budget_stress_margin'], row['min_budget_stress_margin'], f">= {audit['min_budget_stress_margin']}")
            add(f'neural_guard_holdout_bootstrap:{key}:interpretation_boundary', 'not an analytic full-domain neural certificate' in row['interpretation'], row['interpretation'], 'boundary phrase')

    if 'neural_guard_concordance_audit' in manifest:
        audit = manifest['neural_guard_concordance_audit']
        concordance_rows = rows('neural_guard_concordance_audit.csv')
        experiments = sorted({r['experiment'] for r in concordance_rows})
        add('neural_guard_concordance:row_count', len(concordance_rows) == audit['row_count'], len(concordance_rows), audit['row_count'])
        add('neural_guard_concordance:experiments', experiments == sorted(audit['experiments']), experiments, sorted(audit['experiments']))
        for row in concordance_rows:
            key = row['experiment']
            add(f'neural_guard_concordance:{key}:status', row['concordance_status'] == 'concordance_guard_pass', row['concordance_status'], 'concordance_guard_pass')
            add(f'neural_guard_concordance:{key}:scheme_count', int(row['stability_scheme_count']) == audit['required_scheme_count'], row['stability_scheme_count'], audit['required_scheme_count'])
            add(f'neural_guard_concordance:{key}:positive_votes', int(row['positive_scheme_votes']) == int(row['required_scheme_votes']) == audit['required_scheme_count'], {'positive': row['positive_scheme_votes'], 'required': row['required_scheme_votes']}, audit['required_scheme_count'])
            add(f'neural_guard_concordance:{key}:route', row['validation_cover_route'] == 'validation-cover_not_global_lipschitz', row['validation_cover_route'], 'validation-cover_not_global_lipschitz')
            add(f'neural_guard_concordance:{key}:slack_floor', float(row['min_bootstrap_sensitivity_slack_floor']) >= audit['min_bootstrap_sensitivity_slack_floor'], row['min_bootstrap_sensitivity_slack_floor'], f">= {audit['min_bootstrap_sensitivity_slack_floor']}")
            add(f'neural_guard_concordance:{key}:heldout_floor', float(row['min_bootstrap_heldout_delta_floor']) >= audit['min_bootstrap_heldout_delta_floor'], row['min_bootstrap_heldout_delta_floor'], f">= {audit['min_bootstrap_heldout_delta_floor']}")
            add(f'neural_guard_concordance:{key}:stress_margin', float(row['min_budget_stress_margin']) >= audit['min_budget_stress_margin'], row['min_budget_stress_margin'], f">= {audit['min_budget_stress_margin']}")
            add(f'neural_guard_concordance:{key}:interpretation_boundary', 'not an analytic full-domain neural certificate' in row['interpretation'], row['interpretation'], 'boundary phrase')

    if 'neural_guard_leave_one_out_robustness_audit' in manifest:
        audit = manifest['neural_guard_leave_one_out_robustness_audit']
        loo_rows = rows('neural_guard_leave_one_out_robustness_audit.csv')
        experiments = sorted({r['experiment'] for r in loo_rows})
        omitted = sorted({r['omitted_guard_family'] for r in loo_rows})
        add('neural_guard_leave_one_out:row_count', len(loo_rows) == audit['row_count'], len(loo_rows), audit['row_count'])
        add('neural_guard_leave_one_out:experiments', experiments == sorted(audit['experiments']), experiments, sorted(audit['experiments']))
        add('neural_guard_leave_one_out:omitted_guard_families', omitted == sorted(audit['omitted_guard_families']), omitted, sorted(audit['omitted_guard_families']))
        for row in loo_rows:
            key = f"{row['experiment']}:{row['omitted_guard_family']}"
            add(f'neural_guard_leave_one_out:{key}:status', row['robustness_status'] == 'leave_one_out_guard_pass', row['robustness_status'], 'leave_one_out_guard_pass')
            add(f'neural_guard_leave_one_out:{key}:remaining_guard_count', int(row['remaining_guard_families']) == audit['required_remaining_guard_families'], row['remaining_guard_families'], audit['required_remaining_guard_families'])
            add(f'neural_guard_leave_one_out:{key}:route', row['route'] == 'validation-cover_not_global_lipschitz', row['route'], 'validation-cover_not_global_lipschitz')
            add(f'neural_guard_leave_one_out:{key}:refinement_slack', float(row['min_refinement_slack']) > 0, row['min_refinement_slack'], '> 0')
            add(f'neural_guard_leave_one_out:{key}:holdout_slack', float(row['min_holdout_slack']) >= audit['min_holdout_slack_floor'], row['min_holdout_slack'], f">= {audit['min_holdout_slack_floor']}")
            add(f'neural_guard_leave_one_out:{key}:heldout_delta', float(row['min_heldout_delta']) >= audit['min_heldout_delta_floor'], row['min_heldout_delta'], f">= {audit['min_heldout_delta_floor']}")
            add(f'neural_guard_leave_one_out:{key}:stress_margin', float(row['min_budget_stress_margin']) >= audit['min_budget_stress_margin'], row['min_budget_stress_margin'], f">= {audit['min_budget_stress_margin']}")
            add(f'neural_guard_leave_one_out:{key}:interpretation_boundary', 'not an analytic full-domain neural certificate' in row['interpretation'], row['interpretation'], 'boundary phrase')

    if 'neural_bounded_composition_envelope_certificate' in manifest:
        audit = manifest['neural_bounded_composition_envelope_certificate']
        envelope_rows = rows('neural_bounded_composition_envelope_certificate.csv')
        experiments = sorted({r['experiment'] for r in envelope_rows})
        add('neural_bounded_composition_envelope:row_count', len(envelope_rows) == audit['row_count'], len(envelope_rows), audit['row_count'])
        add('neural_bounded_composition_envelope:experiments', experiments == sorted(audit['experiments']), experiments, sorted(audit['experiments']))
        for row in envelope_rows:
            experiment = row['experiment']
            expected = audit['expected'][experiment]
            add(f'neural_bounded_composition_envelope:{experiment}:status', row['bounded_composition_status'] == 'bounded_composition_envelope_pass', row['bounded_composition_status'], 'bounded_composition_envelope_pass')
            add(f'neural_bounded_composition_envelope:{experiment}:component_count', int(row['component_count']) == audit['component_count'], row['component_count'], audit['component_count'])
            add(f'neural_bounded_composition_envelope:{experiment}:stress_scenario_count', int(row['stress_scenario_count']) == audit['stress_scenario_count'], row['stress_scenario_count'], audit['stress_scenario_count'])
            add(f'neural_bounded_composition_envelope:{experiment}:guard_family_count', int(row['omitted_guard_family_count']) == audit['omitted_guard_family_count'], row['omitted_guard_family_count'], audit['omitted_guard_family_count'])
            add(f'neural_bounded_composition_envelope:{experiment}:leave_one_out_rows', int(row['leave_one_out_rows']) == audit['leave_one_out_rows_per_experiment'], row['leave_one_out_rows'], audit['leave_one_out_rows_per_experiment'])
            add(f'neural_bounded_composition_envelope:{experiment}:guard_route', row['guard_route'] == 'validation-cover_not_global_lipschitz', row['guard_route'], 'validation-cover_not_global_lipschitz')
            add(f'neural_bounded_composition_envelope:{experiment}:certificate_route', row['certificate_route'] == 'bounded-composition_compact-domain_global-envelope_not_unrestricted', row['certificate_route'], 'bounded-composition_compact-domain_global-envelope_not_unrestricted')
            add(f'neural_bounded_composition_envelope:{experiment}:budget_product', float(row['max_budget_product']) <= audit['max_budget_product'], row['max_budget_product'], f"<= {audit['max_budget_product']}")
            add(f'neural_bounded_composition_envelope:{experiment}:stressed_budget_product', float(row['max_stressed_budget_product']) <= audit['max_stressed_budget_product'], row['max_stressed_budget_product'], f"<= {audit['max_stressed_budget_product']}")
            add(f'neural_bounded_composition_envelope:{experiment}:stress_margin', float(row['min_budget_stress_margin']) >= audit['min_budget_stress_margin'], row['min_budget_stress_margin'], f">= {audit['min_budget_stress_margin']}")
            add(f'neural_bounded_composition_envelope:{experiment}:sensitivity_score', float(row['max_sensitivity_score']) <= expected['max_sensitivity_score'], row['max_sensitivity_score'], f"<= {expected['max_sensitivity_score']}")
            add(f'neural_bounded_composition_envelope:{experiment}:sensitivity_margin', float(row['min_sensitivity_margin']) >= expected['min_sensitivity_margin'], row['min_sensitivity_margin'], f">= {expected['min_sensitivity_margin']}")
            add(f'neural_bounded_composition_envelope:{experiment}:refinement_slack', float(row['min_refinement_slack']) >= expected['min_refinement_slack'], row['min_refinement_slack'], f">= {expected['min_refinement_slack']}")
            add(f'neural_bounded_composition_envelope:{experiment}:holdout_slack', float(row['min_holdout_slack']) >= expected['min_holdout_slack'], row['min_holdout_slack'], f">= {expected['min_holdout_slack']}")
            add(f'neural_bounded_composition_envelope:{experiment}:heldout_delta', float(row['min_heldout_delta']) >= expected['min_heldout_delta'], row['min_heldout_delta'], f">= {expected['min_heldout_delta']}")
            add(f'neural_bounded_composition_envelope:{experiment}:composed_score', float(row['composed_envelope_score']) <= expected['max_composed_envelope_score'], row['composed_envelope_score'], f"<= {expected['max_composed_envelope_score']}")
            add(f'neural_bounded_composition_envelope:{experiment}:composed_margin', float(row['composed_envelope_margin']) >= expected['min_composed_envelope_margin'], row['composed_envelope_margin'], f">= {expected['min_composed_envelope_margin']}")
            add(f'neural_bounded_composition_envelope:{experiment}:guard_families', row['source_guard_families'] == audit['source_guard_families'], row['source_guard_families'], audit['source_guard_families'])
            add(f'neural_bounded_composition_envelope:{experiment}:interpretation_boundary', 'not an unrestricted analytic full-domain neural certificate' in row['interpretation'], row['interpretation'], 'boundary phrase')

    if 'neural_guard_stress_frontier_audit' in manifest:
        audit = manifest['neural_guard_stress_frontier_audit']
        frontier_rows = rows('neural_guard_stress_frontier_audit.csv')
        experiments = sorted({r['experiment'] for r in frontier_rows})
        add('neural_guard_stress_frontier:row_count', len(frontier_rows) == audit['row_count'], len(frontier_rows), audit['row_count'])
        add('neural_guard_stress_frontier:experiments', experiments == sorted(audit['experiments']), experiments, sorted(audit['experiments']))
        for row in frontier_rows:
            experiment = row['experiment']
            expected = audit['expected'][experiment]
            add(f'neural_guard_stress_frontier:{experiment}:status', row['frontier_status'] == 'stress_frontier_guard_pass', row['frontier_status'], 'stress_frontier_guard_pass')
            add(f'neural_guard_stress_frontier:{experiment}:route', row['guard_route'] == 'validation-cover_not_global_lipschitz', row['guard_route'], 'validation-cover_not_global_lipschitz')
            add(f'neural_guard_stress_frontier:{experiment}:current_frontier', float(row['current_cover_sensitivity_frontier_multiplier']) >= expected['min_current_cover_sensitivity_frontier_multiplier'], row['current_cover_sensitivity_frontier_multiplier'], f">= {expected['min_current_cover_sensitivity_frontier_multiplier']}")
            add(f'neural_guard_stress_frontier:{experiment}:refined_frontier', float(row['refined_sensitivity_frontier_multiplier']) >= expected['min_refined_sensitivity_frontier_multiplier'], row['refined_sensitivity_frontier_multiplier'], f">= {expected['min_refined_sensitivity_frontier_multiplier']}")
            add(f'neural_guard_stress_frontier:{experiment}:budget_frontier', float(row['bounded_budget_frontier_multiplier']) >= audit['min_bounded_budget_frontier_multiplier'], row['bounded_budget_frontier_multiplier'], f">= {audit['min_bounded_budget_frontier_multiplier']}")
            add(f'neural_guard_stress_frontier:{experiment}:composed_frontier', float(row['composed_envelope_frontier_multiplier']) >= expected['min_composed_envelope_frontier_multiplier'], row['composed_envelope_frontier_multiplier'], f">= {expected['min_composed_envelope_frontier_multiplier']}")
            add(f'neural_guard_stress_frontier:{experiment}:current_limited_frontier', float(row['current_limited_frontier_multiplier']) >= expected['min_current_limited_frontier_multiplier'], row['current_limited_frontier_multiplier'], f">= {expected['min_current_limited_frontier_multiplier']}")
            add(f'neural_guard_stress_frontier:{experiment}:active_current_constraint', row['active_current_constraint'] == expected['active_current_constraint'], row['active_current_constraint'], expected['active_current_constraint'])
            add(f'neural_guard_stress_frontier:{experiment}:active_refined_constraint', row['active_refined_constraint'] == expected['active_refined_constraint'], row['active_refined_constraint'], expected['active_refined_constraint'])
            add(f'neural_guard_stress_frontier:{experiment}:interpretation_boundary', 'not an unrestricted analytic full-domain neural certificate' in row['interpretation'], row['interpretation'], 'boundary phrase')

    if 'package_self_replay_certificate' in manifest:
        audit = manifest['package_self_replay_certificate']
        cert = json_data('package_self_replay_certificate.json')
        add('package_self_replay:status', cert['status'] == 'PASS', cert['status'], 'PASS')
        add('package_self_replay:command_count', cert['command_count'] == audit['command_count'], cert['command_count'], audit['command_count'])
        add('package_self_replay:artifact_count', cert['artifact_count'] == audit['artifact_count'], cert['artifact_count'], audit['artifact_count'])
        observed_commands = [command['name'] for command in cert['commands']]
        add('package_self_replay:commands', observed_commands == audit['commands'], observed_commands, audit['commands'])
        for command in cert['commands']:
            add(f'package_self_replay:{command["name"]}:status', command['status'] == 'PASS', command['status'], 'PASS')
        artifacts = {item['path']: item for item in cert['artifacts']}
        add('package_self_replay:artifacts', sorted(artifacts) == sorted(audit['artifacts']), sorted(artifacts), sorted(audit['artifacts']))
        for rel in audit['artifacts']:
            item = artifacts.get(rel)
            add(f'package_self_replay:{rel}:exists', item is not None, bool(item), True)
            if item is None:
                continue
            expected_rows = manifest['row_counts'][Path(rel).name]
            add(f'package_self_replay:{rel}:rows', item['rows'] == expected_rows, item['rows'], expected_rows)
            add(f'package_self_replay:{rel}:sha256', item['sha256'] == sha256(ROOT / rel), item['sha256'], sha256(ROOT / rel))
        add('package_self_replay:boundary', 'Does not rerun full PyTorch training' in cert['boundary'], cert['boundary'], 'boundary phrase')

    if 'reproducibility_environment_audit' in manifest:
        audit = manifest['reproducibility_environment_audit']
        env = json_data('reproducibility_environment_audit.json')
        add('environment_audit:status', env['status'] == audit['status'], env['status'], audit['status'])
        add('environment_audit:lightweight_gate', env['lightweight_gate']['status'] == 'PASS', env['lightweight_gate']['status'], 'PASS')
        add('environment_audit:python_minimum', tuple(int(x) for x in env['python']['major_minor'].split('.')) >= tuple(int(x) for x in audit['minimum_python'].split('.')), env['python']['major_minor'], f">= {audit['minimum_python']}")
        observed_tools = sorted(row['tool'] for row in env['toolchain'] if row.get('available'))
        add('environment_audit:required_tools_available', all(tool in observed_tools for tool in audit['required_tools']), observed_tools, audit['required_tools'])
        observed_stdlib = sorted(row['module'] for row in env['stdlib_modules'] if row.get('available'))
        add('environment_audit:required_stdlib_available', all(module in observed_stdlib for module in audit['required_stdlib_modules']), observed_stdlib, audit['required_stdlib_modules'])
        req_rows = env['requirements']
        add('environment_audit:declared_requirement_count', len(req_rows) == audit['declared_requirement_count'], len(req_rows), audit['declared_requirement_count'])
        declared_packages = sorted(row['package'] for row in req_rows)
        add('environment_audit:declared_packages', declared_packages == sorted(audit['declared_packages']), declared_packages, sorted(audit['declared_packages']))
        boundary = env['full_regeneration_dependency_boundary']
        add('environment_audit:full_dependency_boundary_status', boundary['status'] in audit['allowed_full_dependency_statuses'], boundary['status'], audit['allowed_full_dependency_statuses'])
        add('environment_audit:boundary_phrase', audit['boundary_phrase'] in boundary['boundary'], boundary['boundary'], f"contains {audit['boundary_phrase']}")
        add('environment_audit:external_boundary', 'no external review' in env['external_boundary'], env['external_boundary'], 'external boundary phrase')

    if 'lightweight_replay_dependency_closure_audit' in manifest:
        audit = manifest['lightweight_replay_dependency_closure_audit']
        closure_rows = rows('lightweight_replay_dependency_closure_audit.csv')
        add('lightweight_dependency_closure:row_count', len(closure_rows) == audit['row_count'], len(closure_rows), audit['row_count'])
        observed_scripts = sorted(row['script'] for row in closure_rows)
        add('lightweight_dependency_closure:scripts', observed_scripts == sorted(audit['scripts']), observed_scripts, sorted(audit['scripts']))
        forbidden = set(audit['forbidden_optional_full_regeneration_imports'])
        for row in closure_rows:
            script = row['script']
            imported = set(filter(None, row['imported_top_level_modules'].split(';')))
            observed_forbidden = set(filter(None, row['forbidden_optional_full_regeneration_imports'].split(';')))
            add(f'lightweight_dependency_closure:{script}:status', row['status'] == audit['required_status'], row['status'], audit['required_status'])
            add(f'lightweight_dependency_closure:{script}:no_forbidden_imports', not observed_forbidden and imported.isdisjoint(forbidden), sorted(observed_forbidden or (imported & forbidden)), [])
            add(f'lightweight_dependency_closure:{script}:source_hash', row['sha256'] == sha256(ROOT / script), row['sha256'], sha256(ROOT / script))
            add(f'lightweight_dependency_closure:{script}:boundary', audit['boundary_phrase'] in row['boundary'], row['boundary'], audit['boundary_phrase'])

    if 'strong_form_generalized_rl_hjb_solver_claim_audit' in manifest:
        audit = manifest['strong_form_generalized_rl_hjb_solver_claim_audit']
        pillar_rows = {r['pillar']: r for r in rows('strong_form_generalized_rl_hjb_solver_claim_audit.csv')}
        add('strong_form_claim_closure:row_count', len(pillar_rows) == audit['row_count'], len(pillar_rows), audit['row_count'])
        add('strong_form_claim_closure:pillars', sorted(pillar_rows) == sorted(audit['pillars']), sorted(pillar_rows), sorted(audit['pillars']))
        passed = sum(1 for r in pillar_rows.values() if r['status'] == 'strong_form_pillar_pass')
        add('strong_form_claim_closure:all_pillars_pass', passed == audit['row_count'], passed, audit['row_count'])
        for pillar, expected in audit.get('expected', {}).items():
            row = pillar_rows.get(pillar)
            add(f'strong_form_claim_closure:{pillar}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'strong_form_claim_closure:{pillar}:status', row['status'] == expected['status'], row['status'], expected['status'])
            text = ' | '.join([row.get('theorem_anchor', ''), row.get('evidence_sources', ''), row.get('observed_guard', ''), row.get('interpretation', '')])
            for token in expected.get('required_tokens', []):
                add(f'strong_form_claim_closure:{pillar}:token:{token}', token in text, text if token in text else 'missing', f'contains {token}')
        gen = pillar_rows.get('policy_class_generalization')
        if gen:
            parts = dict(part.split('=') for part in gen['observed_guard'].split('; '))
            add('strong_form_claim_closure:strict_dp_gt_0_19', float(parts['strict_dp']) > 0.19, parts['strict_dp'], '> 0.19')
            add('strong_form_claim_closure:exact_mdp_gt_0_015', float(parts['exact_mdp']) > 0.015, parts['exact_mdp'], '> 0.015')
        hjb = pillar_rows.get('proof_certified_hjb_solver_core')
        if hjb:
            parts = dict(part.split('=') for part in hjb['observed_guard'].split('; '))
            add('strong_form_claim_closure:compact_lt_1e_12', float(parts['compact']) < 1e-12, parts['compact'], '< 1e-12')
            add('strong_form_claim_closure:uniform_bound_lt_0_021', float(parts['uniform_bound']) < 0.021, parts['uniform_bound'], '< 0.021')
            add('strong_form_claim_closure:finite_bound_zero', float(parts['finite_bound']) == 0.0, parts['finite_bound'], 0.0)
        cover = pillar_rows.get('cover_refinement_sequence')
        if cover:
            radius_text = cover['observed_guard'].split('; ')[0].split('=')[1]
            start, end = [float(x) for x in radius_text.split('->')]
            margin = float(cover['observed_guard'].split('; ')[1].split('=')[1])
            add('strong_form_claim_closure:cover_radius_shrinks', end < start, radius_text, 'end < start')
            add('strong_form_claim_closure:cover_margin_gt_0_19', margin > 0.19, margin, '> 0.19')
        vc = pillar_rows.get('large_neural_validation_cover_route')
        if vc:
            parts = dict(part.split('=') for part in vc['observed_guard'].split('; '))
            pass_num, pass_den = [int(x) for x in parts['passes'].split('/')]
            add('strong_form_claim_closure:validation_guards_all_pass', pass_num == pass_den == 2, parts['passes'], '2/2')
            add('strong_form_claim_closure:validation_max_tail_lt_4_2', float(parts['max_tail']) < 4.2, parts['max_tail'], '< 4.2')
            add('strong_form_claim_closure:validation_max_native_lt_0_20', float(parts['max_native_ratio']) < 0.20, parts['max_native_ratio'], '< 0.20')
        rep = pillar_rows.get('shadow_price_representation_guard')
        if rep:
            parts = dict(part.split('=') for part in rep['observed_guard'].split('; '))
            add('strong_form_claim_closure:direct_ratio_gt_19', float(parts['same_benchmark']) > 19, parts['same_benchmark'], '> 19')
            add('strong_form_claim_closure:learned_ratio_gt_27', float(parts['learned']) > 27, parts['learned'], '> 27')
            add('strong_form_claim_closure:neural_ratio_gt_21', float(parts['neural']) > 21, parts['neural'], '> 21')
        rollout = pillar_rows.get('same_information_rollout_support')
        if rollout:
            parts = dict(part.split('=') for part in rollout['observed_guard'].split('; '))
            add('strong_form_claim_closure:same_budget_exp1_positive', float(parts['same_budget_exp1']) > 0.02, parts['same_budget_exp1'], '> 0.02')
            add('strong_form_claim_closure:exp2_practical_parity', float(parts['exp2_abs']) < 2e-6, parts['exp2_abs'], '< 2e-6')
            add('strong_form_claim_closure:exp3_feasible_positive', float(parts['exp3_feasible']) > 0.01, parts['exp3_feasible'], '> 0.01')
            add('strong_form_claim_closure:selected_exp3_positive', float(parts['selected_exp3']) > 0.0, parts['selected_exp3'], '> 0')
            add('strong_form_claim_closure:nbo_exp1_positive', float(parts['nbo_exp1']) > 0.0, parts['nbo_exp1'], '> 0')
            add('strong_form_claim_closure:nbo_inventory_positive', float(parts['nbo_inventory']) > 0.0, parts['nbo_inventory'], '> 0')

    if 'generalized_rl_noncollapse_audit' in manifest:
        audit = manifest['generalized_rl_noncollapse_audit']
        nc_rows = {r['noncollapse_claim']: r for r in rows('generalized_rl_noncollapse_audit.csv')}
        add('generalized_rl_noncollapse:row_count', len(nc_rows) == audit['row_count'], len(nc_rows), audit['row_count'])
        add('generalized_rl_noncollapse:claims', sorted(nc_rows) == sorted(audit['claims']), sorted(nc_rows), sorted(audit['claims']))
        passed = sum(1 for r in nc_rows.values() if r['status'] == 'noncollapse_guard_pass')
        add('generalized_rl_noncollapse:all_guards_pass', passed == audit['row_count'], passed, audit['row_count'])
        for claim, expected in audit.get('expected', {}).items():
            row = nc_rows.get(claim)
            add(f'generalized_rl_noncollapse:{claim}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'generalized_rl_noncollapse:{claim}:status', row['status'] == expected['status'], row['status'], expected['status'])
            text = ' | '.join([row.get('theorem_anchor', ''), row.get('evidence_sources', ''), row.get('observed_guard', ''), row.get('interpretation', '')])
            for token in expected.get('required_tokens', []):
                add(f'generalized_rl_noncollapse:{claim}:token:{token}', token in text, text if token in text else 'missing', f'contains {token}')
        exact = nc_rows.get('exact_policy_class_value_separation')
        if exact:
            parts = dict(part.split('=') for part in exact['observed_guard'].split('; '))
            add('generalized_rl_noncollapse:exact_full_minus_action_gt_0_19', float(parts['full_minus_action']) > 0.19, parts['full_minus_action'], '> 0.19')
            add('generalized_rl_noncollapse:exact_full_minus_best_face_gt_0_12', float(parts['full_minus_best_single_channel_face']) > 0.12, parts['full_minus_best_single_channel_face'], '> 0.12')
        mdp = nc_rows.get('exact_valuation_state_mdp_value_separation')
        if mdp:
            parts = dict(part.split('=') for part in mdp['observed_guard'].split('; '))
            add('generalized_rl_noncollapse:mdp_margin_gt_0_015', float(parts['full_minus_action']) > 0.015, parts['full_minus_action'], '> 0.015')
            add('generalized_rl_noncollapse:theta_free_cost_gap_zero', float(parts['theta_free_cost_gap']) < 1e-10, parts['theta_free_cost_gap'], '< 1e-10')
        finite_nc = nc_rows.get('finite_cover_certificate_value_separation')
        if finite_nc:
            parts = dict(part.split('=') for part in finite_nc['observed_guard'].split('; '))
            add('generalized_rl_noncollapse:finite_bound_zero', float(parts['finite_bound']) == 0.0, parts['finite_bound'], 0.0)
            add('generalized_rl_noncollapse:finite_margin_gt_0_19', float(parts['full_minus_action']) > 0.19, parts['full_minus_action'], '> 0.19')
            add('generalized_rl_noncollapse:finite_contains_faces', int(parts['contains_both_faces']) == 1, parts['contains_both_faces'], 1)
        same = nc_rows.get('same_information_budget_noncollapse')
        if same:
            parts = dict(part.split('=') for part in same['observed_guard'].split('; '))
            add('generalized_rl_noncollapse:same_exp1_positive', float(parts['exp1']) > 0.02, parts['exp1'], '> 0.02')
            add('generalized_rl_noncollapse:same_exp2_parity', float(parts['exp2_abs']) < 2e-6, parts['exp2_abs'], '< 2e-6')
            add('generalized_rl_noncollapse:same_exp3_feasible_positive', float(parts['exp3_feasible']) > 0.01, parts['exp3_feasible'], '> 0.01')
            add('generalized_rl_noncollapse:same_selected_exp3_positive', float(parts['selected_exp3']) > 0, parts['selected_exp3'], '> 0')
        nbo_nc = nc_rows.get('source_nbo_rollout_noncollapse')
        if nbo_nc:
            parts = dict(part.split('=') for part in nbo_nc['observed_guard'].split('; '))
            add('generalized_rl_noncollapse:nbo_exp1_positive', float(parts['exp1']) > 0, parts['exp1'], '> 0')
            add('generalized_rl_noncollapse:nbo_exp2_nonnegative', float(parts['exp2']) >= 0, parts['exp2'], '>= 0')
            add('generalized_rl_noncollapse:nbo_inventory_positive', float(parts['inventory']) > 0, parts['inventory'], '> 0')

    if 'reward_shaping_state_augmentation_closure_audit' in manifest:
        audit = manifest['reward_shaping_state_augmentation_closure_audit']
        sr_rows = {r['closure_claim']: r for r in rows('reward_shaping_state_augmentation_closure_audit.csv')}
        add('state_reward_closure:row_count', len(sr_rows) == audit['row_count'], len(sr_rows), audit['row_count'])
        add('state_reward_closure:claims', sorted(sr_rows) == sorted(audit['claims']), sorted(sr_rows), sorted(audit['claims']))
        passed = sum(1 for r in sr_rows.values() if r['status'] == 'state_reward_closure_pass')
        add('state_reward_closure:all_guards_pass', passed == audit['row_count'], passed, audit['row_count'])
        for claim, expected in audit.get('expected', {}).items():
            row = sr_rows.get(claim)
            add(f'state_reward_closure:{claim}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'state_reward_closure:{claim}:status', row['status'] == expected['status'], row['status'], expected['status'])
            text = ' | '.join([row.get('theorem_anchor', ''), row.get('evidence_sources', ''), row.get('observed_guard', ''), row.get('interpretation', '')])
            for token in expected.get('required_tokens', []):
                add(f'state_reward_closure:{claim}:token:{token}', token in text, text if token in text else 'missing', f'contains {token}')
        same_eval = sr_rows.get('same_evaluator_reward_shaping_exclusion')
        if same_eval:
            parts = dict(part.split('=') for part in same_eval['observed_guard'].split('; '))
            add('state_reward_closure:same_eval_margin_gt_0_19', float(parts['full_minus_action']) > 0.19, parts['full_minus_action'], '> 0.19')
            add('state_reward_closure:same_eval_best_face_gt_0_12', float(parts['full_minus_best_single_channel_face']) > 0.12, parts['full_minus_best_single_channel_face'], '> 0.12')
            add('state_reward_closure:evaluator_preserved', int(parts['evaluator_preserved']) == 1, parts['evaluator_preserved'], 1)
        face = sr_rows.get('augmented_state_fixed_theta_face_contained')
        if face:
            parts = dict(part.split('=') for part in face['observed_guard'].split('; '))
            add('state_reward_closure:finite_bound_zero', float(parts['finite_bound']) == 0.0, parts['finite_bound'], 0.0)
            add('state_reward_closure:finite_margin_gt_0_19', float(parts['full_minus_action']) > 0.19, parts['full_minus_action'], '> 0.19')
            add('state_reward_closure:contains_both_faces', int(parts['contains_both_faces']) == 1, parts['contains_both_faces'], 1)
        phys = sr_rows.get('physical_cost_not_reward_relabeling')
        if phys:
            parts = dict(part.split('=') for part in phys['observed_guard'].split('; '))
            add('state_reward_closure:valuation_margin_gt_0_015', float(parts['valuation_margin']) > 0.015, parts['valuation_margin'], '> 0.015')
            add('state_reward_closure:theta_free_cost_gap_zero', float(parts['theta_free_cost_gap']) < 1e-10, parts['theta_free_cost_gap'], '< 1e-10')
        proto = sr_rows.get('same_protocol_information_budget_guard')
        if proto:
            parts = dict(part.split('=') for part in proto['observed_guard'].split('; '))
            add('state_reward_closure:protocol_exp1_positive', float(parts['exp1']) > 0.02, parts['exp1'], '> 0.02')
            add('state_reward_closure:protocol_exp2_parity', float(parts['exp2_abs']) < 2e-6, parts['exp2_abs'], '< 2e-6')
            add('state_reward_closure:protocol_exp3_feasible_positive', float(parts['exp3_feasible']) > 0.01, parts['exp3_feasible'], '> 0.01')
            add('state_reward_closure:protocol_selected_exp3_positive', float(parts['selected_exp3']) > 0, parts['selected_exp3'], '> 0')
        hjb = sr_rows.get('hjb_solver_not_reward_relabeling')
        if hjb:
            parts = dict(part.split('=') for part in hjb['observed_guard'].split('; '))
            pass_num, pass_den = [int(x) for x in parts['strong_pillars'].split('/')]
            add('state_reward_closure:strong_pillars_all_pass', pass_num == pass_den == 6, parts['strong_pillars'], '6/6')
            add('state_reward_closure:nbo_exp1_positive', float(parts['nbo_exp1']) > 0, parts['nbo_exp1'], '> 0')
            add('state_reward_closure:nbo_inventory_positive', float(parts['nbo_inventory']) > 0, parts['nbo_inventory'], '> 0')

    if 'policy_class_face_hierarchy_audit' in manifest:
        audit = manifest['policy_class_face_hierarchy_audit']
        face_rows = {r['hierarchy_claim']: r for r in rows('policy_class_face_hierarchy_audit.csv')}
        add('face_hierarchy:row_count', len(face_rows) == audit['row_count'], len(face_rows), audit['row_count'])
        add('face_hierarchy:claims', sorted(face_rows) == sorted(audit['claims']), sorted(face_rows), sorted(audit['claims']))
        passed = sum(1 for r in face_rows.values() if r['status'] == 'face_hierarchy_pass')
        add('face_hierarchy:all_guards_pass', passed == audit['row_count'], passed, audit['row_count'])
        for claim, expected in audit.get('expected', {}).items():
            row = face_rows.get(claim)
            add(f'face_hierarchy:{claim}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'face_hierarchy:{claim}:status', row['status'] == expected['status'], row['status'], expected['status'])
            text = ' | '.join([row.get('theorem_anchor', ''), row.get('evidence_sources', ''), row.get('observed_guard', ''), row.get('interpretation', '')])
            for token in expected.get('required_tokens', []):
                add(f'face_hierarchy:{claim}:token:{token}', token in text, text if token in text else 'missing', f'contains {token}')
        strict = face_rows.get('strict_single_channel_face_dominance')
        if strict:
            parts = dict(part.split('=') for part in strict['observed_guard'].split('; '))
            add('face_hierarchy:valuation_minus_action_positive', float(parts['valuation_minus_action']) > 0, parts['valuation_minus_action'], '> 0')
            add('face_hierarchy:full_minus_action_gt_0_19', float(parts['full_minus_action']) > 0.19, parts['full_minus_action'], '> 0.19')
            add('face_hierarchy:full_minus_valuation_gt_0_12', float(parts['full_minus_valuation']) > 0.12, parts['full_minus_valuation'], '> 0.12')
        finite_face = face_rows.get('finite_cover_exact_face_certificates')
        if finite_face:
            parts = dict(part.split('=') for part in finite_face['observed_guard'].split('; '))
            add('face_hierarchy:zero_certificate_gaps', int(parts['zero_certificate_gaps']) == 1, parts['zero_certificate_gaps'], 1)
            add('face_hierarchy:contains_both_faces', int(parts['contains_both_faces']) == 1, parts['contains_both_faces'], 1)
            add('face_hierarchy:finite_full_minus_action_gt_0_19', float(parts['full_minus_action']) > 0.19, parts['full_minus_action'], '> 0.19')
            add('face_hierarchy:finite_full_minus_valuation_gt_0_12', float(parts['full_minus_valuation']) > 0.12, parts['full_minus_valuation'], '> 0.12')
        refine = face_rows.get('joint_control_refinement_sequence')
        if refine:
            parts = dict(part.split('=') for part in refine['observed_guard'].split('; '))
            r0, r1 = [float(x) for x in parts['radius'].split('->')]
            margins = [float(x) for x in parts['margins'].split('->')]
            add('face_hierarchy:radius_shrinks', r1 < r0, parts['radius'], 'end < start')
            add('face_hierarchy:margins_monotone', all(b >= a - 1e-12 for a, b in zip(margins, margins[1:])), parts['margins'], 'monotone')
            add('face_hierarchy:final_margin_gt_0_19', margins[-1] > 0.19, margins[-1], '> 0.19')
            add('face_hierarchy:refinement_zero_bounds', int(parts['zero_bounds']) == 1, parts['zero_bounds'], 1)
        service = face_rows.get('service_pressure_joint_control_diagnostics')
        if service:
            parts = dict(part.split('=') for part in service['observed_guard'].split('; '))
            fills = [float(x) for x in parts['fill_rate'].split('->')]
            breaches = [float(x) for x in parts['breaches'].split('->')]
            add('face_hierarchy:fill_rate_monotone', all(b >= a for a, b in zip(fills, fills[1:])), parts['fill_rate'], 'monotone increasing')
            add('face_hierarchy:breaches_monotone', all(b <= a for a, b in zip(breaches, breaches[1:])), parts['breaches'], 'monotone decreasing')
        closure = face_rows.get('closure_stack_consistency')
        if closure:
            parts = dict(part.split('=') for part in closure['observed_guard'].split('; '))
            sp0, sp1 = [int(x) for x in parts['strong_pillars'].split('/')]
            sr0, sr1 = [int(x) for x in parts['state_reward_guards'].split('/')]
            add('face_hierarchy:strong_pillars_all_pass', sp0 == sp1 == 6, parts['strong_pillars'], '6/6')
            add('face_hierarchy:state_reward_guards_all_pass', sr0 == sr1 == 5, parts['state_reward_guards'], '5/5')
            add('face_hierarchy:full_minus_best_face_gt_0_12', float(parts['full_minus_best_face']) > 0.12, parts['full_minus_best_face'], '> 0.12')

    if 'referee_full_support_synthesis_audit' in manifest:
        audit = manifest['referee_full_support_synthesis_audit']
        synth_rows = {r['support_claim']: r for r in rows('referee_full_support_synthesis_audit.csv')}
        add('full_support_synthesis:row_count', len(synth_rows) == audit['row_count'], len(synth_rows), audit['row_count'])
        add('full_support_synthesis:claims', sorted(synth_rows) == sorted(audit['claims']), sorted(synth_rows), sorted(audit['claims']))
        passed = sum(1 for r in synth_rows.values() if r['status'] == 'full_support_synthesis_pass')
        add('full_support_synthesis:all_guards_pass', passed == audit['row_count'], passed, audit['row_count'])
        for claim, expected in audit.get('expected', {}).items():
            row = synth_rows.get(claim)
            add(f'full_support_synthesis:{claim}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'full_support_synthesis:{claim}:status', row['status'] == expected['status'], row['status'], expected['status'])
            text = ' | '.join([row.get('theorem_stack', ''), row.get('audit_sources', ''), row.get('observed_guard', ''), row.get('referee_response', '')])
            for token in expected.get('required_tokens', []):
                add(f'full_support_synthesis:{claim}:token:{token}', token in text, text if token in text else 'missing', f'contains {token}')
        policy = synth_rows.get('policy_class_generalized_rl_strictness')
        if policy:
            parts = dict(part.split('=') for part in policy['observed_guard'].split('; '))
            nc0, nc1 = [int(x) for x in parts['noncollapse'].split('/')]
            fh0, fh1 = [int(x) for x in parts['face_hierarchy'].split('/')]
            add('full_support_synthesis:strict_dp_gt_0_19', float(parts['strict_dp']) > 0.19, parts['strict_dp'], '> 0.19')
            add('full_support_synthesis:exact_mdp_gt_0_015', float(parts['exact_mdp']) > 0.015, parts['exact_mdp'], '> 0.015')
            add('full_support_synthesis:noncollapse_all_pass', nc0 == nc1 == 5, parts['noncollapse'], '5/5')
            add('full_support_synthesis:face_hierarchy_all_pass', fh0 == fh1 == 5, parts['face_hierarchy'], '5/5')
        relabel = synth_rows.get('no_state_reward_single_channel_relabeling')
        if relabel:
            parts = dict(part.split('=') for part in relabel['observed_guard'].split('; '))
            sr0, sr1 = [int(x) for x in parts['state_reward'].split('/')]
            add('full_support_synthesis:state_reward_all_pass', sr0 == sr1 == 5, parts['state_reward'], '5/5')
            add('full_support_synthesis:best_single_channel_margin_gt_0_12', float(parts['full_minus_best_single_channel_face']) > 0.12, parts['full_minus_best_single_channel_face'], '> 0.12')
            add('full_support_synthesis:full_minus_valuation_gt_0_12', float(parts['full_minus_valuation']) > 0.12, parts['full_minus_valuation'], '> 0.12')
        hjb = synth_rows.get('hjb_solver_certificate_core')
        if hjb:
            parts = dict(part.split('=') for part in hjb['observed_guard'].split('; '))
            sp0, sp1 = [int(x) for x in parts['strong_pillars'].split('/')]
            ld0, ld1 = [int(x) for x in parts['ladder'].split('/')]
            add('full_support_synthesis:strong_pillars_all_pass', sp0 == sp1 == 6, parts['strong_pillars'], '6/6')
            add('full_support_synthesis:ladder_all_pass', ld0 == ld1 == 7, parts['ladder'], '7/7')
            add('full_support_synthesis:compact_lt_1e_12', float(parts['compact']) < 1e-12, parts['compact'], '< 1e-12')
            add('full_support_synthesis:uniform_bound_lt_0_021', float(parts['uniform_bound']) < 0.021, parts['uniform_bound'], '< 0.021')
            add('full_support_synthesis:finite_bound_zero', float(parts['finite_bound']) == 0.0, parts['finite_bound'], 0.0)
        finite = synth_rows.get('finite_cover_refinement_not_one_grid')
        if finite:
            parts = dict(part.split('=') for part in finite['observed_guard'].split('; '))
            r0, r1 = [float(x) for x in parts['radius'].split('->')]
            margins = [float(x) for x in parts['margins'].split('->')]
            add('full_support_synthesis:finite_zero_gaps', int(parts['zero_certificate_gaps']) == 1, parts['zero_certificate_gaps'], 1)
            add('full_support_synthesis:finite_contains_faces', int(parts['contains_both_faces']) == 1, parts['contains_both_faces'], 1)
            add('full_support_synthesis:finite_radius_shrinks', r1 < r0, parts['radius'], 'end < start')
            add('full_support_synthesis:finite_final_margin_gt_0_19', margins[-1] > 0.19, margins[-1], '> 0.19')
        neural = synth_rows.get('neural_validation_cover_route_without_overclaiming')
        if neural:
            parts = dict(part.split('=') for part in neural['observed_guard'].split('; '))
            vg0, vg1 = [int(x) for x in parts['validation_stability'].split('/')]
            add('full_support_synthesis:validation_all_pass', vg0 == vg1 == 2, parts['validation_stability'], '2/2')
            add('full_support_synthesis:max_tail_lt_4_2', float(parts['max_tail']) < 4.2, parts['max_tail'], '< 4.2')
            add('full_support_synthesis:max_native_lt_0_20', float(parts['max_native_ratio']) < 0.20, parts['max_native_ratio'], '< 0.20')
            add('full_support_synthesis:validation_route_explicit', parts['route'] == 'validation-cover_not_fake_global_lipschitz', parts['route'], 'validation-cover_not_fake_global_lipschitz')
        direct = synth_rows.get('direct_p_shadow_price_representation_for_nbo')
        if direct:
            parts = dict(part.split('=') for part in direct['observed_guard'].split('; '))
            add('full_support_synthesis:same_ratio_gt_19', float(parts['same_benchmark_ratio']) > 19, parts['same_benchmark_ratio'], '> 19')
            add('full_support_synthesis:learned_ratio_gt_27', float(parts['learned_ratio']) > 27, parts['learned_ratio'], '> 27')
            add('full_support_synthesis:neural_ratio_gt_21', float(parts['neural_ratio']) > 21, parts['neural_ratio'], '> 21')
        empirical = synth_rows.get('same_information_empirical_support')
        if empirical:
            parts = dict(part.split('=') for part in empirical['observed_guard'].split('; '))
            add('full_support_synthesis:empirical_exp1_positive', float(parts['exp1']) > 0.02, parts['exp1'], '> 0.02')
            add('full_support_synthesis:empirical_exp2_parity', float(parts['exp2_abs']) < 2e-6, parts['exp2_abs'], '< 2e-6')
            add('full_support_synthesis:empirical_exp3_feasible_positive', float(parts['exp3_feasible']) > 0.01, parts['exp3_feasible'], '> 0.01')
            add('full_support_synthesis:empirical_selected_exp3_positive', float(parts['selected_exp3']) > 0, parts['selected_exp3'], '> 0')
            add('full_support_synthesis:empirical_nbo_exp1_positive', float(parts['nbo_exp1']) > 0, parts['nbo_exp1'], '> 0')
            add('full_support_synthesis:empirical_nbo_inventory_positive', float(parts['nbo_inventory']) > 0, parts['nbo_inventory'], '> 0')
        trace = synth_rows.get('claim_to_artifact_traceability')
        if trace:
            parts = dict(part.split('=') for part in trace['observed_guard'].split('; '))
            add('full_support_synthesis:certificate_rows_ge_25', int(parts['certificate_rows']) >= 25, parts['certificate_rows'], '>= 25')
            add('full_support_synthesis:synthesis_rows_8', int(parts['synthesis_rows']) == 8, parts['synthesis_rows'], 8)
            add('full_support_synthesis:source_audits_registered', int(parts['all_source_audits_registered']) == 1, parts['all_source_audits_registered'], 1)

    if 'shadow_price_observability_audit' in manifest:
        audit = manifest['shadow_price_observability_audit']
        shadow_rows = {r['epsilon']: r for r in rows('shadow_price_observability_audit.csv')}
        add('shadow_observability:row_count', len(shadow_rows) == audit['row_count'], len(shadow_rows), audit['row_count'])
        prev_ratio = -1.0
        for eps, expected in sorted(audit['expected'].items(), key=lambda kv: float(kv[0]), reverse=True):
            row = shadow_rows.get(eps)
            add(f'shadow_observability:{eps}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'shadow_observability:{eps}:z_theta_rmse', close(float(row['z_inversion_theta_rmse']), expected['z_inversion_theta_rmse']), float(row['z_inversion_theta_rmse']), expected['z_inversion_theta_rmse'])
            add(f'shadow_observability:{eps}:direct_p_theta_rmse', close(float(row['direct_p_theta_rmse']), expected['direct_p_theta_rmse']), float(row['direct_p_theta_rmse']), expected['direct_p_theta_rmse'])
            ratio = float(row['z_over_direct_theta_rmse_ratio'])
            add(f'shadow_observability:{eps}:ratio', close(ratio, expected['z_over_direct_theta_rmse_ratio']), ratio, expected['z_over_direct_theta_rmse_ratio'])
            if prev_ratio >= 0:
                add(f'shadow_observability:{eps}:ratio_increases', ratio > prev_ratio, ratio, f'> {prev_ratio}')
            prev_ratio = ratio


    if 'inventory_direct_p_vs_z_audit' in manifest:
        audit = manifest['inventory_direct_p_vs_z_audit']
        seed_rows = rows('inventory_direct_p_vs_z_seed_metrics.csv')
        metric_rows = rows('inventory_direct_p_vs_z_metrics.csv')
        add('inventory_direct_p_vs_z:seed_row_count', len(seed_rows) == audit['seed_row_count'], len(seed_rows), audit['seed_row_count'])
        add('inventory_direct_p_vs_z:metrics_row_count', len(metric_rows) == audit['metrics_row_count'], len(metric_rows), audit['metrics_row_count'])
        epsilons = sorted({r['epsilon'] for r in metric_rows}, key=float)
        add('inventory_direct_p_vs_z:epsilons', epsilons == sorted(audit['epsilons'], key=float), epsilons, audit['epsilons'])
        metric = {(r['epsilon'], r['method']): r for r in metric_rows}
        prev_ratio = None
        for eps in sorted(audit['epsilons'], key=float, reverse=True):
            direct = metric.get((eps, 'direct_p_inventory'))
            zinvert = metric.get((eps, 'z_inversion_inventory'))
            oracle = metric.get((eps, 'oracle_p_inventory'))
            add(f'inventory_direct_p_vs_z:{eps}:direct_exists', direct is not None, bool(direct), True)
            add(f'inventory_direct_p_vs_z:{eps}:z_exists', zinvert is not None, bool(zinvert), True)
            add(f'inventory_direct_p_vs_z:{eps}:oracle_exists', oracle is not None, bool(oracle), True)
            if not (direct and zinvert and oracle):
                continue
            add(f'inventory_direct_p_vs_z:{eps}:direct_seed_count', int(direct['n']) == audit['seed_count'], direct['n'], audit['seed_count'])
            add(f'inventory_direct_p_vs_z:{eps}:z_seed_count', int(zinvert['n']) == audit['seed_count'], zinvert['n'], audit['seed_count'])
            add(f'inventory_direct_p_vs_z:{eps}:oracle_theta_zero', close(float(oracle['theta_rmse']), 0.0), oracle['theta_rmse'], 0.0)
            add(f'inventory_direct_p_vs_z:{eps}:z_theta_worse', float(zinvert['theta_rmse']) > float(direct['theta_rmse']), zinvert['theta_rmse'], f'> {direct["theta_rmse"]}')
            add(f'inventory_direct_p_vs_z:{eps}:z_welfare_lower', float(zinvert['mean_welfare']) < float(direct['mean_welfare']), zinvert['mean_welfare'], f'< {direct["mean_welfare"]}')
            ratio = float(zinvert['theta_rmse']) / max(float(direct['theta_rmse']), 1e-12)
            add(f'inventory_direct_p_vs_z:{eps}:ratio_matches', close(ratio, float(zinvert['theta_rmse_ratio_vs_direct_p']), tol=1e-8), ratio, zinvert['theta_rmse_ratio_vs_direct_p'])
            if prev_ratio is not None:
                add(f'inventory_direct_p_vs_z:{eps}:ratio_increases_as_epsilon_falls', ratio > prev_ratio, ratio, f'> {prev_ratio}')
            prev_ratio = ratio
            expected = audit.get('expected', {}).get(eps, {})
            for key, expected_value in expected.items():
                method, col = key.split(':', 1)
                row = metric.get((eps, method))
                add(f'inventory_direct_p_vs_z:{eps}:{key}', row is not None and close(float(row[col]), expected_value), float(row[col]) if row else 'missing', expected_value)

    if 'inventory_direct_p_learned_z_ablation' in manifest:
        audit = manifest['inventory_direct_p_learned_z_ablation']
        seed_rows = rows('inventory_direct_p_learned_z_ablation_seed_metrics.csv')
        metric_rows = rows('inventory_direct_p_learned_z_ablation.csv')
        add('inventory_direct_p_learned_z:seed_row_count', len(seed_rows) == audit['seed_row_count'], len(seed_rows), audit['seed_row_count'])
        add('inventory_direct_p_learned_z:metrics_row_count', len(metric_rows) == audit['metrics_row_count'], len(metric_rows), audit['metrics_row_count'])
        epsilons = sorted({r['epsilon'] for r in metric_rows}, key=float)
        add('inventory_direct_p_learned_z:epsilons', epsilons == sorted(audit['epsilons'], key=float), epsilons, audit['epsilons'])
        metric = {(r['epsilon'], r['method']): r for r in metric_rows}
        prev_ratio = None
        for eps in sorted(audit['epsilons'], key=float, reverse=True):
            direct = metric.get((eps, 'learned_direct_p_inventory'))
            learned_z = metric.get((eps, 'learned_z_inventory'))
            oracle = metric.get((eps, 'oracle_p_inventory'))
            add(f'inventory_direct_p_learned_z:{eps}:direct_exists', direct is not None, bool(direct), True)
            add(f'inventory_direct_p_learned_z:{eps}:z_exists', learned_z is not None, bool(learned_z), True)
            add(f'inventory_direct_p_learned_z:{eps}:oracle_exists', oracle is not None, bool(oracle), True)
            if not (direct and learned_z and oracle):
                continue
            add(f'inventory_direct_p_learned_z:{eps}:direct_seed_count', int(direct['n']) == audit['seed_count'], direct['n'], audit['seed_count'])
            add(f'inventory_direct_p_learned_z:{eps}:z_seed_count', int(learned_z['n']) == audit['seed_count'], learned_z['n'], audit['seed_count'])
            add(f'inventory_direct_p_learned_z:{eps}:z_theta_worse', float(learned_z['theta_rmse']) > float(direct['theta_rmse']), learned_z['theta_rmse'], f'> {direct["theta_rmse"]}')
            add(f'inventory_direct_p_learned_z:{eps}:z_p_worse', float(learned_z['p_rmse']) > float(direct['p_rmse']), learned_z['p_rmse'], f'> {direct["p_rmse"]}')
            add(f'inventory_direct_p_learned_z:{eps}:z_welfare_lower', float(learned_z['mean_welfare']) < float(direct['mean_welfare']), learned_z['mean_welfare'], f'< {direct["mean_welfare"]}')
            ratio = float(learned_z['theta_rmse_ratio_vs_learned_direct_p'])
            if prev_ratio is not None:
                add(f'inventory_direct_p_learned_z:{eps}:ratio_increases_as_epsilon_falls', ratio > prev_ratio, ratio, f'> {prev_ratio}')
            prev_ratio = ratio
            expected = audit.get('expected', {}).get(eps, {})
            for key, expected_value in expected.items():
                method, col = key.split(':', 1)
                row = metric.get((eps, method))
                add(f'inventory_direct_p_learned_z:{eps}:{key}', row is not None and close(float(row[col]), expected_value), float(row[col]) if row else 'missing', expected_value)

    if 'inventory_neural_direct_p_learned_z_ablation' in manifest:
        audit = manifest['inventory_neural_direct_p_learned_z_ablation']
        seed_rows = rows('inventory_neural_direct_p_learned_z_ablation_seed_metrics.csv')
        metric_rows = rows('inventory_neural_direct_p_learned_z_ablation.csv')
        add('inventory_neural_direct_p_learned_z:seed_row_count', len(seed_rows) == audit['seed_row_count'], len(seed_rows), audit['seed_row_count'])
        add('inventory_neural_direct_p_learned_z:metrics_row_count', len(metric_rows) == audit['metrics_row_count'], len(metric_rows), audit['metrics_row_count'])
        epsilons = sorted({r['epsilon'] for r in metric_rows}, key=float)
        add('inventory_neural_direct_p_learned_z:epsilons', epsilons == sorted(audit['epsilons'], key=float), epsilons, audit['epsilons'])
        metric = {(r['epsilon'], r['method']): r for r in metric_rows}
        prev_ratio = None
        for eps in sorted(audit['epsilons'], key=float, reverse=True):
            direct = metric.get((eps, 'neural_direct_p_inventory'))
            learned_z = metric.get((eps, 'neural_learned_z_inventory'))
            oracle = metric.get((eps, 'oracle_p_inventory'))
            add(f'inventory_neural_direct_p_learned_z:{eps}:direct_exists', direct is not None, bool(direct), True)
            add(f'inventory_neural_direct_p_learned_z:{eps}:z_exists', learned_z is not None, bool(learned_z), True)
            add(f'inventory_neural_direct_p_learned_z:{eps}:oracle_exists', oracle is not None, bool(oracle), True)
            if not (direct and learned_z and oracle):
                continue
            add(f'inventory_neural_direct_p_learned_z:{eps}:direct_seed_count', int(direct['n']) == audit['seed_count'], direct['n'], audit['seed_count'])
            add(f'inventory_neural_direct_p_learned_z:{eps}:z_seed_count', int(learned_z['n']) == audit['seed_count'], learned_z['n'], audit['seed_count'])
            add(f'inventory_neural_direct_p_learned_z:{eps}:same_network', direct['network'] == learned_z['network'] == audit['network'], (direct['network'], learned_z['network']), audit['network'])
            add(f'inventory_neural_direct_p_learned_z:{eps}:same_optimizer_budget', int(direct['train_steps']) == int(learned_z['train_steps']) == audit['train_steps'], (direct['train_steps'], learned_z['train_steps']), audit['train_steps'])
            add(f'inventory_neural_direct_p_learned_z:{eps}:z_theta_worse', float(learned_z['theta_rmse']) > float(direct['theta_rmse']), learned_z['theta_rmse'], f'> {direct["theta_rmse"]}')
            add(f'inventory_neural_direct_p_learned_z:{eps}:z_p_worse', float(learned_z['p_rmse']) > float(direct['p_rmse']), learned_z['p_rmse'], f'> {direct["p_rmse"]}')
            ratio = float(learned_z['theta_rmse_ratio_vs_neural_direct_p'])
            if prev_ratio is not None:
                add(f'inventory_neural_direct_p_learned_z:{eps}:ratio_increases_as_epsilon_falls', ratio > prev_ratio, ratio, f'> {prev_ratio}')
            prev_ratio = ratio
            if eps == audit['near_deterministic_epsilon']:
                add(f'inventory_neural_direct_p_learned_z:{eps}:near_deterministic_welfare_lower', float(learned_z['mean_welfare']) < float(direct['mean_welfare']), learned_z['mean_welfare'], f'< {direct["mean_welfare"]}')
            expected = audit.get('expected', {}).get(eps, {})
            for key, expected_value in expected.items():
                method, col = key.split(':', 1)
                row = metric.get((eps, method))
                add(f'inventory_neural_direct_p_learned_z:{eps}:{key}', row is not None and close(float(row[col]), expected_value), float(row[col]) if row else 'missing', expected_value)

    if 'common_external_evaluator_audit' in manifest:
        audit = manifest['common_external_evaluator_audit']
        common_rows = {(r['benchmark'], r['metric']): r for r in rows('common_external_evaluator_audit.csv')}
        add('common_external:row_count', len(common_rows) == audit['row_count'], len(common_rows), audit['row_count'])
        for item in audit['expected']:
            key = (item['benchmark'], item['metric'])
            row = common_rows.get(key)
            add(f'common_external:{"/".join(key)}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'common_external:{"/".join(key)}:full_value', close(float(row['full_ndu_value']), item['full_ndu_value']), float(row['full_ndu_value']), item['full_ndu_value'])
            add(f'common_external:{"/".join(key)}:best_method', row['best_non_ndu_method'] == item['best_non_ndu_method'], row['best_non_ndu_method'], item['best_non_ndu_method'])
            add(f'common_external:{"/".join(key)}:best_value', close(float(row['best_non_ndu_value']), item['best_non_ndu_value']), float(row['best_non_ndu_value']), item['best_non_ndu_value'])

    if 'oracle_baseline_reconciliation_audit' in manifest:
        audit = manifest['oracle_baseline_reconciliation_audit']
        recon_rows = {(r['experiment'], r['comparison']): r for r in rows('oracle_baseline_reconciliation_audit.csv')}
        add('oracle_reconciliation:row_count', len(recon_rows) == audit['row_count'], len(recon_rows), audit['row_count'])
        for item in audit['expected']:
            key = (item['experiment'], item['comparison'])
            row = recon_rows.get(key)
            add(f'oracle_reconciliation:{"/".join(key)}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'oracle_reconciliation:{"/".join(key)}:comparator', row['comparator'] == item['comparator'], row['comparator'], item['comparator'])
            add(f'oracle_reconciliation:{"/".join(key)}:full_minus_comparator', close(float(row['full_minus_comparator']), item['full_minus_comparator']), float(row['full_minus_comparator']), item['full_minus_comparator'])
            add(f'oracle_reconciliation:{"/".join(key)}:budget_full', int(row['budget_full']) == item['budget_full'], row['budget_full'], item['budget_full'])
            add(f'oracle_reconciliation:{"/".join(key)}:budget_comparator', int(row['budget_comparator']) == item['budget_comparator'], row['budget_comparator'], item['budget_comparator'])

    if 'exp2_oracle_repair_audit' in manifest:
        audit = manifest['exp2_oracle_repair_audit']
        agg_rows = {r['method']: r for r in rows('exp2_oracle_repair_audit.csv')}
        add('exp2_oracle_repair:row_count', len(agg_rows) == audit['row_count'], len(agg_rows), audit['row_count'])
        for method, expected in audit['expected'].items():
            row = agg_rows.get(method)
            add(f'exp2_oracle_repair:{method}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'exp2_oracle_repair:{method}:evaluations', int(row['policy_evaluations']) == expected['policy_evaluations'], row['policy_evaluations'], expected['policy_evaluations'])
            add(f'exp2_oracle_repair:{method}:mean_utility', close(float(row['mean_utility']), expected['mean_utility']), float(row['mean_utility']), expected['mean_utility'])
            add(f'exp2_oracle_repair:{method}:gap_vs_full', close(float(row['mean_utility_gap_vs_full_ndu']), expected['mean_utility_gap_vs_full_ndu']), float(row['mean_utility_gap_vs_full_ndu']), expected['mean_utility_gap_vs_full_ndu'])
        safe = agg_rows.get('matched_budget_safe_oracle_lower_bound')
        full = agg_rows.get('full_ndu_joint')
        original = agg_rows.get('original_oracle_joint_action_rl')
        if safe and full and original:
            add('exp2_oracle_repair:safe_beats_original', float(safe['mean_utility']) > float(original['mean_utility']), safe['mean_utility'], f'> {original["mean_utility"]}')
            add('exp2_oracle_repair:safe_at_least_full', float(safe['mean_utility']) >= float(full['mean_utility']), safe['mean_utility'], f'>= {full["mean_utility"]}')

    if 'seed_level_statistical_audit' in manifest:
        audit = manifest['seed_level_statistical_audit']
        key = lambda r: (r['experiment'], r['metric'], r['method_a'], r['method_b'])
        audit_rows = {key(r): r for r in rows('seed_level_statistical_audit.csv')}
        add('seed_audit:row_count', len(audit_rows) == audit['row_count'], len(audit_rows), audit['row_count'])
        for item in audit.get('expected', []):
            row_key = (item['experiment'], item['metric'], item['method_a'], item['method_b'])
            row = audit_rows.get(row_key)
            add(f'seed_audit:{"/".join(row_key)}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'seed_audit:{"/".join(row_key)}:ci_excludes_zero', row['ci_excludes_zero'] == item['ci_excludes_zero'], row['ci_excludes_zero'], item['ci_excludes_zero'])
            add(f'seed_audit:{"/".join(row_key)}:mean_diff', close(float(row['mean_diff_a_minus_b']), item['mean_diff_a_minus_b']), float(row['mean_diff_a_minus_b']), item['mean_diff_a_minus_b'])
            add(f'seed_audit:{"/".join(row_key)}:ci95_halfwidth', close(float(row['ci95_halfwidth_normal_independent']), item['ci95_halfwidth_normal_independent']), float(row['ci95_halfwidth_normal_independent']), item['ci95_halfwidth_normal_independent'])

    if 'inventory_sensitivity_grid' in manifest:
        grid = manifest['inventory_sensitivity_grid']
        metrics_rows = rows('inventory_sensitivity_grid_metrics.csv')
        scenarios = sorted({r['scenario'] for r in metrics_rows})
        add('inventory_sensitivity:scenario_count', len(scenarios) == grid['scenario_count'], len(scenarios), grid['scenario_count'])
        add('inventory_sensitivity:scenarios', scenarios == sorted(grid['scenarios']), scenarios, sorted(grid['scenarios']))
        full_best_or_close = []
        for scenario in grid['scenarios']:
            full = scenario_method_row('inventory_sensitivity_grid_metrics.csv', scenario, 'full_ndu_inventory')
            full_best_or_close.append(float(full['welfare_gap_to_best']) <= grid['full_gap_tolerance'])
        add('inventory_sensitivity:full_best_or_close_all_scenarios', all(full_best_or_close), full_best_or_close, True)

    if 'inventory_exact_policy_class_dp' in manifest:
        audit = manifest['inventory_exact_policy_class_dp']
        metrics = {r['method']: r for r in rows('inventory_exact_policy_class_dp_metrics.csv')}
        policy_rows = rows('inventory_exact_policy_class_dp_policy.csv')
        add('inventory_policy_dp:metrics_row_count', len(metrics) == audit['metrics_row_count'], len(metrics), audit['metrics_row_count'])
        add('inventory_policy_dp:policy_row_count', len(policy_rows) == audit['policy_row_count'], len(policy_rows), audit['policy_row_count'])
        for method in audit['methods']:
            add(f'inventory_policy_dp:{method}:row_exists', method in metrics, bool(method in metrics), True)
        for method, expected in audit['expected'].items():
            row = metrics.get(method)
            if row is None:
                continue
            add(f'inventory_policy_dp:{method}:state_count', int(row['state_count']) == audit['state_count'], row['state_count'], audit['state_count'])
            expected_control_count = audit.get('control_counts', {}).get(method, audit.get('control_count_per_method'))
            add(f'inventory_policy_dp:{method}:control_count', int(row['control_count']) == expected_control_count, row['control_count'], expected_control_count)
            for col, expected_value in expected.items():
                add(f'inventory_policy_dp:{method}:{col}', close(float(row[col]), expected_value), float(row[col]), expected_value)
        action = metrics.get('action_only_exact_dp')
        full = metrics.get('full_valuation_control_exact_dp')
        valuation = metrics.get('valuation_only_exact_dp')
        if action and full and valuation:
            ranking = [full['expected_avg_welfare'], valuation['expected_avg_welfare'], action['expected_avg_welfare']]
            add('inventory_policy_dp:full_best_in_nested_class', float(full['expected_avg_welfare']) > float(valuation['expected_avg_welfare']) > float(action['expected_avg_welfare']), ranking, 'full > valuation > action')

    if 'inventory_equal_budget_theta_audit' in manifest:
        audit = manifest['inventory_equal_budget_theta_audit']
        seed_rows = rows('inventory_equal_budget_theta_audit_seed_metrics.csv')
        metric_rows = rows('inventory_equal_budget_theta_audit_metrics.csv')
        add('inventory_theta_audit:seed_row_count', len(seed_rows) == audit['seed_row_count'], len(seed_rows), audit['seed_row_count'])
        add('inventory_theta_audit:metrics_row_count', len(metric_rows) == audit['metrics_row_count'], len(metric_rows), audit['metrics_row_count'])
        summary = {(r['audit'], r['method'], r['evaluation_variant'], r['theta_cost_multiplier']): r for r in metric_rows}
        for item in audit['expected']:
            key = (item['audit'], item['method'], item['evaluation_variant'], item['theta_cost_multiplier'])
            row = summary.get(key)
            add(f'inventory_theta_audit:{"/".join(key)}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'inventory_theta_audit:{"/".join(key)}:n', int(row['n']) == item['n'], row['n'], item['n'])
            add(f'inventory_theta_audit:{"/".join(key)}:policy_evaluations', int(row['policy_evaluations']) == item['policy_evaluations'], row['policy_evaluations'], item['policy_evaluations'])
            for col in ['mean_welfare', 'avg_cost', 'avg_cost_no_theta']:
                add(f'inventory_theta_audit:{"/".join(key)}:{col}', close(float(row[col]), item[col]), float(row[col]), item[col])
        normal = summary.get(('equal_budget_inventory', 'full_ndu_inventory', 'normal', '1.0'))
        fixed = summary.get(('theta_ablation_inventory', 'full_ndu_inventory', 'fixed_one', '1.0'))
        permuted = summary.get(('theta_ablation_inventory', 'full_ndu_inventory', 'permuted', '1.0'))
        action = summary.get(('equal_budget_inventory', 'action_only_adaptive_base_stock', 'normal', '1.0'))
        if normal and fixed and permuted and action:
            add('inventory_theta_audit:fixed_theta_worse_than_normal', float(fixed['mean_welfare']) < float(normal['mean_welfare']), fixed['mean_welfare'], f'< {normal["mean_welfare"]}')
            add('inventory_theta_audit:permuted_theta_worse_than_normal', float(permuted['mean_welfare']) < float(normal['mean_welfare']), permuted['mean_welfare'], f'< {normal["mean_welfare"]}')
            add('inventory_theta_audit:equal_budget_action_beats_full', float(action['mean_welfare']) > float(normal['mean_welfare']), action['mean_welfare'], f'> {normal["mean_welfare"]}')

    if 'inventory_equal_budget_pareto_audit' in manifest:
        audit = manifest['inventory_equal_budget_pareto_audit']
        pareto_rows = {r['config']: r for r in rows('inventory_equal_budget_pareto_audit.csv')}
        seed_rows = rows('inventory_equal_budget_pareto_seed_metrics.csv')
        add('inventory_equal_budget_pareto:row_count', len(pareto_rows) == audit['row_count'], len(pareto_rows), audit['row_count'])
        add('inventory_equal_budget_pareto:seed_row_count', len(seed_rows) == audit['seed_row_count'], len(seed_rows), audit['seed_row_count'])
        confirm = pareto_rows.get(audit['confirm_config'])
        add('inventory_equal_budget_pareto:confirm_row_exists', confirm is not None, bool(confirm), True)
        if confirm:
            add('inventory_equal_budget_pareto:confirm_status', confirm['claim_status'] == audit['confirm_claim_status'], confirm['claim_status'], audit['confirm_claim_status'])
            add('inventory_equal_budget_pareto:confirm_n', int(confirm['n']) == audit['confirm_seed_count'], confirm['n'], audit['confirm_seed_count'])
            add('inventory_equal_budget_pareto:confirm_policy_evaluations', int(confirm['policy_evaluations']) == audit['policy_evaluations'], confirm['policy_evaluations'], audit['policy_evaluations'])
            for col, expected_value in audit.get('expected_values', {}).items():
                add(f'inventory_equal_budget_pareto:{col}', close(float(confirm[col]), expected_value), float(confirm[col]), expected_value)
            add('inventory_equal_budget_pareto:welfare_favors_full', float(confirm['delta_mean_welfare']) > 0, confirm['delta_mean_welfare'], '> 0')
            add('inventory_equal_budget_pareto:theta_free_cost_favors_full', float(confirm['delta_avg_cost_no_theta']) > 0, confirm['delta_avg_cost_no_theta'], '> 0 (action minus Full)')
            add('inventory_equal_budget_pareto:physical_guard_pass', confirm.get('physical_guard_pass') == 'True', confirm.get('physical_guard_pass'), 'True')
        methods = sorted({r['method'] for r in seed_rows if r.get('config') == audit['confirm_config']})
        counts = {m: len({r['seed_index'] for r in seed_rows if r.get('config') == audit['confirm_config'] and r['method'] == m}) for m in methods}
        add('inventory_equal_budget_pareto:confirm_seed_count_by_method', all(v == audit['confirm_seed_count'] for v in counts.values()), counts, audit['confirm_seed_count'])

    if 'inventory_paired_seed_difference_audit' in manifest:
        audit = manifest['inventory_paired_seed_difference_audit']
        paired_rows = {(r['scenario'], r['comparison'], r['metric']): r for r in rows('inventory_paired_seed_difference_audit.csv')}
        add('inventory_paired:row_count', len(paired_rows) == audit['row_count'], len(paired_rows), audit['row_count'])
        for item in audit['expected']:
            key = (item['scenario'], item['comparison'], item['metric'])
            row = paired_rows.get(key)
            add(f'inventory_paired:{"/".join(key)}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'inventory_paired:{"/".join(key)}:n_pairs', int(row['n_pairs']) == item['n_pairs'], row['n_pairs'], item['n_pairs'])
            add(f'inventory_paired:{"/".join(key)}:mean_difference', close(float(row['mean_difference']), item['mean_difference']), float(row['mean_difference']), item['mean_difference'])
            add(f'inventory_paired:{"/".join(key)}:ci95', close(float(row['ci95']), item['ci95']), float(row['ci95']), item['ci95'])

    if 'decision_layer_bridge_audit' in manifest:
        audit = manifest['decision_layer_bridge_audit']
        bridge_rows = {r['benchmark']: r for r in rows('decision_layer_bridge_audit.csv')}
        add('decision_bridge:row_count', len(bridge_rows) == audit['row_count'], len(bridge_rows), audit['row_count'])
        add('decision_bridge:benchmarks', sorted(bridge_rows) == sorted(audit['benchmarks']), sorted(bridge_rows), sorted(audit['benchmarks']))
        for benchmark, expected in audit['expected'].items():
            row = bridge_rows.get(benchmark)
            add(f'decision_bridge:{benchmark}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'decision_bridge:{benchmark}:claim_status', row['claim_status'] == expected['claim_status'], row['claim_status'], expected['claim_status'])
            for token in expected.get('must_contain', []):
                observed_text = ' | '.join([row['primary_comparison'], row['uncertainty_or_intervention'], row['certificate_read']])
                add(f'decision_bridge:{benchmark}:contains:{token}', token in observed_text, observed_text if token in observed_text else 'missing', token)

    if 'primary_evaluator_audit' in manifest:
        audit = manifest['primary_evaluator_audit']
        primary_rows = {r['benchmark']: r for r in rows('primary_evaluator_audit.csv')}
        add('primary_evaluator:row_count', len(primary_rows) == audit['row_count'], len(primary_rows), audit['row_count'])
        add('primary_evaluator:benchmarks', sorted(primary_rows) == sorted(audit['benchmarks']), sorted(primary_rows), sorted(audit['benchmarks']))
        for benchmark, expected in audit['expected'].items():
            row = primary_rows.get(benchmark)
            add(f'primary_evaluator:{benchmark}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            observed_text = ' | '.join([row['internal_objective_read'], row['external_theta_free_read'], row['claim_read']])
            for token in expected.get('must_contain', []):
                add(f'primary_evaluator:{benchmark}:contains:{token}', token in observed_text, observed_text if token in observed_text else 'missing', token)

    if 'nbo_full_ndu_solver' in manifest:
        audit = manifest['nbo_full_ndu_solver']
        nbo_rows = {r['benchmark']: r for r in rows('nbo_full_ndu_solver_audit.csv')}
        add('nbo_solver:audit_row_count', len(nbo_rows) == audit['audit_row_count'], len(nbo_rows), audit['audit_row_count'])
        add('nbo_solver:benchmarks', sorted(nbo_rows) == sorted(audit['benchmarks']), sorted(nbo_rows), sorted(audit['benchmarks']))
        metric_rows = {(r['experiment'], r['method']): r for r in rows('source_nbo_metrics.csv')}
        diag_rows = {(r['experiment'], r['method'], int(r['iteration'])): r for r in rows('source_nbo_training_diagnostics.csv')}
        for benchmark, expected in audit['expected'].items():
            row = nbo_rows.get(benchmark)
            add(f'nbo_solver:{benchmark}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'nbo_solver:{benchmark}:solver', row['solver'] == audit['solver'], row['solver'], audit['solver'])
            add(f'nbo_solver:{benchmark}:claim_status', row['claim_status'] == expected['claim_status'], row['claim_status'], expected['claim_status'])
            add(f'nbo_solver:{benchmark}:full_method', row['full_method'] == expected['full_method'], row['full_method'], expected['full_method'])
            add(f'nbo_solver:{benchmark}:comparator_method', row['comparator_method'] == expected['comparator_method'], row['comparator_method'], expected['comparator_method'])
            add(f'nbo_solver:{benchmark}:primary_metric', row['primary_metric'] == expected['primary_metric'], row['primary_metric'], expected['primary_metric'])
            if 'automatic_differentiation' in audit or 'automatic_differentiation' in expected:
                exp_ad = expected.get('automatic_differentiation', audit.get('automatic_differentiation'))
                add(f'nbo_solver:{benchmark}:automatic_differentiation', row.get('automatic_differentiation') == exp_ad, row.get('automatic_differentiation'), exp_ad)
            if 'initialization' in audit or 'initialization' in expected:
                exp_init = expected.get('initialization', audit.get('initialization'))
                add(f'nbo_solver:{benchmark}:initialization', row.get('initialization') == exp_init, row.get('initialization'), exp_init)
            add(f'nbo_solver:{benchmark}:full_value', close(float(row['full_value']), expected['full_value']), float(row['full_value']), expected['full_value'])
            add(f'nbo_solver:{benchmark}:comparator_value', close(float(row['comparator_value']), expected['comparator_value']), float(row['comparator_value']), expected['comparator_value'])
            add(f'nbo_solver:{benchmark}:full_minus_comparator', close(float(row['full_minus_comparator_paired']), expected['full_minus_comparator_paired']), float(row['full_minus_comparator_paired']), expected['full_minus_comparator_paired'])
            add(f'nbo_solver:{benchmark}:paired_ci95', close(float(row['paired_ci95']), expected['paired_ci95']), float(row['paired_ci95']), expected['paired_ci95'])
            metric = metric_rows.get((benchmark, expected['full_method']))
            diag = diag_rows.get((benchmark, expected['full_method'], audit['train_steps']))
            add(f'nbo_solver:{benchmark}:metric_row_exists', metric is not None, bool(metric), True)
            add(f'nbo_solver:{benchmark}:diagnostic_row_exists', diag is not None, bool(diag), True)
            if metric is not None:
                add(f'nbo_solver:{benchmark}:seed_count', int(metric['seed_count']) == audit['seed_count'], metric['seed_count'], audit['seed_count'])
                add(f'nbo_solver:{benchmark}:algorithm', metric['algorithm'] == audit['solver'], metric['algorithm'], audit['solver'])
                for beaten_method in expected.get('beats_methods', []):
                    beaten = metric_rows.get((benchmark, beaten_method))
                    add(f'nbo_solver:{benchmark}:beats:{beaten_method}:row_exists', beaten is not None, bool(beaten), True)
                    if beaten is not None:
                        col = expected['primary_metric']
                        add(f'nbo_solver:{benchmark}:beats:{beaten_method}:{col}', float(metric[col]) > float(beaten[col]), metric[col], f'> {beaten[col]}')
            if diag is not None:
                add(f'nbo_solver:{benchmark}:final_hjb_loss', close(float(diag['hjb_loss']), expected['full_final_hjb_loss']), float(diag['hjb_loss']), expected['full_final_hjb_loss'])
                add(f'nbo_solver:{benchmark}:hjb_loss_finite', math.isfinite(float(diag['hjb_loss'])), diag['hjb_loss'], 'finite')
            observed_text = ' | '.join([row.get('solver', ''), row.get('algorithm_source', ''), row.get('claim_status', ''), row.get('interpretation', '')])
            for token in expected.get('must_contain', []):
                add(f'nbo_solver:{benchmark}:contains:{token}', token in observed_text, observed_text if token in observed_text else 'missing', token)

    if 'hbo_exp3_parity_closing_audit' in manifest:
        audit = manifest['hbo_exp3_parity_closing_audit']
        exp3_rows = {(r['config'], r['method']): r for r in rows('hbo_exp3_parity_closing_audit.csv')}
        add('hbo_exp3_parity_closing:row_count', len(exp3_rows) == audit['row_count'], len(exp3_rows), audit['row_count'])
        for item in audit.get('expected', []):
            key = (item['config'], item['method'])
            row = exp3_rows.get(key)
            add(f'hbo_exp3_parity_closing:{"/".join(key)}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'hbo_exp3_parity_closing:{"/".join(key)}:claim_status', row['claim_status'] == item['claim_status'], row['claim_status'], item['claim_status'])
            add(f'hbo_exp3_parity_closing:{"/".join(key)}:seed_count', int(row['seed_count']) == item['seed_count'], row['seed_count'], item['seed_count'])
            for col, expected_value in item.get('values', {}).items():
                add(f'hbo_exp3_parity_closing:{"/".join(key)}:{col}', close(float(row[col]), expected_value), float(row[col]), expected_value)
        gap1500 = exp3_rows.get(('default_safe_steps1500', 'paired_gap_full_minus_fixed'))
        gap1800 = exp3_rows.get(('default_safe_steps1800', 'paired_gap_full_minus_fixed'))
        if gap1500 and gap1800:
            add('hbo_exp3_parity_closing:gap1500_positive', float(gap1500['mean_utility']) > 0, gap1500['mean_utility'], '> 0')
            add('hbo_exp3_parity_closing:gap1800_positive', float(gap1800['mean_utility']) > 0, gap1800['mean_utility'], '> 0')

    if 'hbo_residual_diagnostics' in manifest:
        audit = manifest['hbo_residual_diagnostics']
        residual_rows = {r['experiment']: r for r in rows('hbo_residual_diagnostics.csv')}
        add('hbo_residual:row_count', len(residual_rows) == audit['row_count'], len(residual_rows), audit['row_count'])
        add('hbo_residual:benchmarks', sorted(residual_rows) == sorted(audit['benchmarks']), sorted(residual_rows), sorted(audit['benchmarks']))
        expected_by_experiment = audit.get('expected', {})
        for experiment in audit['benchmarks']:
            row = residual_rows.get(experiment)
            add(f'hbo_residual:{experiment}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(
                f'hbo_residual:{experiment}:interpretation',
                row['interpretation'] == 'residual_certificate_gap_reported',
                row['interpretation'],
                'residual_certificate_gap_reported',
            )
            for col, expected_value in expected_by_experiment.get(experiment, {}).items():
                add(f'hbo_residual:{experiment}:{col}', close(float(row[col]), expected_value), float(row[col]), expected_value)


    if 'hbo_residual_weight_audit' in manifest:
        audit = manifest['hbo_residual_weight_audit']
        residual_weight_rows = rows('hbo_residual_weight_audit.csv')
        add('hbo_residual_weight:row_count', len(residual_weight_rows) == audit['row_count'], len(residual_weight_rows), audit['row_count'])
        by_config = {(r['experiment'], r['audit_config']): r for r in residual_weight_rows}
        for item in audit.get('expected', []):
            key = (item['experiment'], item['audit_config'])
            row = by_config.get(key)
            add(f'hbo_residual_weight:{key}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            for col, expected_value in item.get('values', {}).items():
                add(f'hbo_residual_weight:{key}:{col}', close(float(row[col]), expected_value), float(row[col]), expected_value)
        exp1_base = by_config.get(('exp1_habit_portfolio', 'headline_performance_run'))
        exp1_resid = by_config.get(('exp1_habit_portfolio', 'exp1_residual_only_critic_no_terminal_guardrail'))
        inv_base = by_config.get(('inventory_service_level', 'headline_performance_run'))
        inv_resid = by_config.get(('inventory_service_level', 'inventory_residual_balanced_long'))
        if exp1_base and exp1_resid:
            add('hbo_residual_weight:exp1_hjb_reduced', float(exp1_resid['native_hjb_loss']) < float(exp1_base['native_hjb_loss']), exp1_resid['native_hjb_loss'], f'< {exp1_base["native_hjb_loss"]}')
            add('hbo_residual_weight:exp1_terminal_tradeoff_visible', float(exp1_resid['terminal_boundary_loss']) > float(exp1_base['terminal_boundary_loss']), exp1_resid['terminal_boundary_loss'], f'> {exp1_base["terminal_boundary_loss"]}')
        if inv_base and inv_resid:
            add('hbo_residual_weight:inventory_hjb_reduced', float(inv_resid['native_hjb_loss']) < float(inv_base['native_hjb_loss']), inv_resid['native_hjb_loss'], f'< {inv_base["native_hjb_loss"]}')
            add('hbo_residual_weight:inventory_welfare_similar', abs(float(inv_resid['heldout_value']) - float(inv_base['heldout_value'])) < audit['inventory_welfare_tolerance'], inv_resid['heldout_value'], f'within {audit["inventory_welfare_tolerance"]} of {inv_base["heldout_value"]}')

    if 'hbo_residual_closing_audit' in manifest:
        audit = manifest['hbo_residual_closing_audit']
        closing_rows = {(r['experiment'], r['audit_config']): r for r in rows('hbo_residual_closing_audit.csv')}
        add('hbo_residual_closing:row_count', len(closing_rows) == audit['row_count'], len(closing_rows), audit['row_count'])
        for item in audit.get('expected', []):
            key = (item['experiment'], item['audit_config'])
            row = closing_rows.get(key)
            add(f'hbo_residual_closing:{key}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'hbo_residual_closing:{key}:claim_status', row['claim_status'] == item['claim_status'], row['claim_status'], item['claim_status'])
            for col, expected_value in item.get('values', {}).items():
                add(f'hbo_residual_closing:{key}:{col}', close(float(row[col]), expected_value), float(row[col]), expected_value)
        exp1 = closing_rows.get(('exp1_habit_portfolio', 'exp1_residual_terminal_critic_2400'))
        inv = closing_rows.get(('inventory_service_level', 'inventory_residual_certificate_balanced_2400'))
        if exp1:
            add('hbo_residual_closing:exp1_hjb_ratio_below_0_15', float(exp1['hjb_loss_ratio_vs_headline']) < 0.15, exp1['hjb_loss_ratio_vs_headline'], '< 0.15')
            add('hbo_residual_closing:exp1_terminal_ratio_below_0_55', float(exp1['terminal_loss_ratio_vs_headline']) < 0.55, exp1['terminal_loss_ratio_vs_headline'], '< 0.55')
            add('hbo_residual_closing:exp1_heldout_preserved', float(exp1['heldout_delta_vs_headline']) > -audit['heldout_tolerance'], exp1['heldout_delta_vs_headline'], f'> -{audit["heldout_tolerance"]}')
        if inv:
            add('hbo_residual_closing:inventory_hjb_ratio_below_0_20', float(inv['hjb_loss_ratio_vs_headline']) < 0.20, inv['hjb_loss_ratio_vs_headline'], '< 0.20')
            add('hbo_residual_closing:inventory_terminal_ratio_below_1', float(inv['terminal_loss_ratio_vs_headline']) < 1.0, inv['terminal_loss_ratio_vs_headline'], '< 1.0')
            add('hbo_residual_closing:inventory_heldout_preserved', float(inv['heldout_delta_vs_headline']) > -audit['heldout_tolerance'], inv['heldout_delta_vs_headline'], f'> -{audit["heldout_tolerance"]}')

    if 'hbo_inventory_normalized_residual_audit' in manifest:
        audit = manifest['hbo_inventory_normalized_residual_audit']
        norm_rows = {r['audit_config']: r for r in rows('hbo_inventory_normalized_residual_audit.csv')}
        add('hbo_inventory_norm:row_count', len(norm_rows) == audit['row_count'], len(norm_rows), audit['row_count'])
        for label, expected in audit.get('expected', {}).items():
            row = norm_rows.get(label)
            add(f'hbo_inventory_norm:{label}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'hbo_inventory_norm:{label}:claim_status', row['claim_status'] == expected['claim_status'], row['claim_status'], expected['claim_status'])
            for col, expected_value in expected.get('values', {}).items():
                add(f'hbo_inventory_norm:{label}:{col}', close(float(row[col]), expected_value), float(row[col]), expected_value)
        guard = norm_rows.get(audit['guarded_label'])
        if guard:
            add('hbo_inventory_norm:guard_norm_below_headline', float(guard['normalized_rmse_ratio_vs_headline']) < 1.0, guard['normalized_rmse_ratio_vs_headline'], '< 1')
            add('hbo_inventory_norm:guard_native_below_headline', float(guard['hjb_loss_ratio_vs_headline']) < 1.0, guard['hjb_loss_ratio_vs_headline'], '< 1')
            add('hbo_inventory_norm:guard_terminal_below_headline', float(guard['terminal_loss_ratio_vs_headline']) < 1.0, guard['terminal_loss_ratio_vs_headline'], '< 1')
            add('hbo_inventory_norm:guard_heldout_preserved', float(guard['heldout_delta_vs_headline']) > -audit['heldout_tolerance'], guard['heldout_delta_vs_headline'], f'> -{audit["heldout_tolerance"]}')

    if 'hbo_greedy_gap_audit' in manifest:
        audit = manifest['hbo_greedy_gap_audit']
        gap_rows = {(r['experiment'], r['audit_config']): r for r in rows('hbo_greedy_gap_audit.csv')}
        add('hbo_greedy_gap:row_count', len(gap_rows) == audit['row_count'], len(gap_rows), audit['row_count'])
        for item in audit.get('expected', []):
            key = (item['experiment'], item['audit_config'])
            row = gap_rows.get(key)
            add(f'hbo_greedy_gap:{"/".join(key)}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'hbo_greedy_gap:{"/".join(key)}:claim_status', row['claim_status'] == item['claim_status'], row['claim_status'], item['claim_status'])
            for col, expected_value in item.get('values', {}).items():
                add(f'hbo_greedy_gap:{"/".join(key)}:{col}', close(float(row[col]), expected_value), float(row[col]), expected_value)
        exp1_head = gap_rows.get(('exp1_habit_portfolio', 'headline_like_exp1_full_ndu_450'))
        exp1_gap = gap_rows.get(('exp1_habit_portfolio', 'exp1_actor_lr_gap_reduced_900'))
        inv_head = gap_rows.get(('inventory_service_level', 'headline_like_inventory_full_ndu_450'))
        inv_gap = gap_rows.get(('inventory_service_level', 'inventory_actor_lr_gap_reduced_900'))
        inv_resid = gap_rows.get(('inventory_service_level', 'strong_inventory_residual_balanced_2400'))
        if exp1_head and exp1_gap:
            add('hbo_greedy_gap:exp1_gap_reduced_p95', float(exp1_gap['greedy_gap_p95']) < float(exp1_head['greedy_gap_p95']), exp1_gap['greedy_gap_p95'], f'< {exp1_head["greedy_gap_p95"]}')
        if inv_head and inv_gap:
            add('hbo_greedy_gap:inventory_gap_reduced_p95', float(inv_gap['greedy_gap_p95']) < float(inv_head['greedy_gap_p95']), inv_gap['greedy_gap_p95'], f'< {inv_head["greedy_gap_p95"]}')
        if inv_resid:
            add('hbo_greedy_gap:inventory_residual_run_gap_not_closed', float(inv_resid['greedy_gap_p95']) > audit['inventory_gap_not_closed_p95_min'], inv_resid['greedy_gap_p95'], f'> {audit["inventory_gap_not_closed_p95_min"]}')

    if 'ndu_nbo_generalization_certificate' in manifest:
        audit = manifest['ndu_nbo_generalization_certificate']
        cert_rows = {r['claim']: r for r in rows('ndu_nbo_generalization_certificate.csv')}
        add('ndu_nbo_certificate:row_count', len(cert_rows) == audit['row_count'], len(cert_rows), audit['row_count'])
        add('ndu_nbo_certificate:claims', sorted(cert_rows) == sorted(audit['claims']), sorted(cert_rows), sorted(audit['claims']))
        for claim, expected in audit['expected'].items():
            row = cert_rows.get(claim)
            add(f'ndu_nbo_certificate:{claim}:row_exists', row is not None, bool(row), True)
            if row is None:
                continue
            add(f'ndu_nbo_certificate:{claim}:status', row['status'] == expected['status'], row['status'], expected['status'])
            if 'metric' in expected:
                add(f'ndu_nbo_certificate:{claim}:metric', row['metric'] == expected['metric'], row['metric'], expected['metric'])
            if 'margin' in expected:
                add(f'ndu_nbo_certificate:{claim}:margin', close(float(row['margin']), expected['margin']), float(row['margin']), expected['margin'])
            if 'ndu_value' in expected:
                add(f'ndu_nbo_certificate:{claim}:ndu_value', close(float(row['ndu_value']), expected['ndu_value']), float(row['ndu_value']), expected['ndu_value'])
            for token in expected.get('must_contain', []):
                observed_text = ' | '.join([row.get('interpretation', ''), row.get('status', ''), row.get('evidence_source', '')])
                add(f'ndu_nbo_certificate:{claim}:contains:{token}', token in observed_text, observed_text if token in observed_text else 'missing', token)

    main_tex = SUBMISSION_ROOT / 'main.tex'
    if main_tex.exists():
        tex = main_tex.read_text(encoding='utf-8', errors='ignore')
        for token in manifest['manuscript_value_strings']:
            add(f'manuscript_contains:{token}', token in tex, token if token in tex else 'missing', token)
    else:
        add('manuscript_exists', False, str(main_tex), 'main.tex')

    failures = [c for c in checks if not c['ok']]
    report = {'status': 'PASS' if not failures else 'FAIL', 'checks': len(checks), 'failures': failures[:20]}
    out = ROOT / 'check_ndu_reproducibility_results.json'
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == '__main__':
    raise SystemExit(main())
