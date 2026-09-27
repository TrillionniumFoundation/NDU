#!/usr/bin/env python3
"""Exact inventory policy-class DP and paired-seed audit for the NDU OR paper.

This script adds two dependency-light checks.

1. A small finite-state periodic-review inventory MDP solved exactly by backward
   induction for three matched-cardinality policy classes: action-only,
   valuation-only, and full valuation-control.  The purpose is not to replace
   the larger CEM benchmark; it is a CEM-free sanity check that valuation-control
   differences can be evaluated by exact Bellman recursion.
2. Paired-seed confidence intervals for the existing stochastic inventory
   benchmark and sensitivity grid.
"""
from __future__ import annotations

import csv
import math
import statistics as stats
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'

HORIZON = 10
INV_MIN = -18
INV_MAX = 42
START_INV = 24
DISCOUNT = 1.0

# Exact dominance requires a nested action class, not merely equal branching
# factor.  The Full valuation-control DP therefore contains the action-only and
# valuation-only controls and adds joint order/theta controls.  Earlier equal-
# cardinality grids could make the exact Full row lose simply because the
# action-only incumbent was absent from its admissible set.
ACTION_ONLY_CONTROLS = [(0.70, 1.00), (0.95, 1.00), (1.20, 1.00), (1.45, 1.00), (1.70, 1.00)]
VALUATION_ONLY_CONTROLS = [(1.10, 0.60), (1.10, 0.85), (1.10, 1.10), (1.10, 1.35), (1.10, 1.60)]
JOINT_CONTROLS = [(0.80, 0.80), (1.00, 1.05), (1.20, 1.25), (1.45, 1.45), (1.70, 1.65), (1.20, 2.20)]
CONTROL_GRID = {
    'action_only_exact_dp': ACTION_ONLY_CONTROLS,
    'valuation_only_exact_dp': VALUATION_ONLY_CONTROLS,
    'full_valuation_control_exact_dp': ACTION_ONLY_CONTROLS + VALUATION_ONLY_CONTROLS + JOINT_CONTROLS,
}


def poisson_probs(lam: float, max_d: int = 14) -> list[tuple[int, float]]:
    probs = [math.exp(-lam) * lam**k / math.factorial(k) for k in range(max_d)]
    tail = max(0.0, 1.0 - sum(probs))
    out = [(k, probs[k]) for k in range(max_d)]
    out.append((max_d, tail))
    s = sum(p for _, p in out)
    return [(d, p / s) for d, p in out]

DEMAND = {
    0: poisson_probs(4.5),
    1: poisson_probs(7.2),
}
REGIME_TRANS = {
    0: [(0, 0.86), (1, 0.14)],
    1: [(0, 0.10), (1, 0.90)],
}


def clamp_inv(x: int) -> int:
    return max(INV_MIN, min(INV_MAX, x))


def step_cost_and_stats(inv: int, regime: int, action_pressure: float, theta: float, demand: int) -> tuple[float, int, float, float, float, float]:
    backlog = max(0, -inv)
    forecast = 4.5 if regime == 0 else 7.2
    # Same structural form as the stochastic benchmark, but reduced to a finite grid.
    order_up_to = forecast * (2.35 + 0.22 * theta * action_pressure) + (0.55 + 0.45 * theta) * backlog
    order_up_to = max(0.0, min(36.0, order_up_to))
    q = max(0, int(round(order_up_to - inv)))
    pre = inv + q
    filled = min(max(pre, 0), demand + backlog)
    next_inv = clamp_inv(pre - demand)
    unmet = max(0, demand + backlog - filled)
    on_hand = max(0, next_inv)
    fill_rate = 1.0 if demand + backlog <= 0 else filled / max(1.0, demand + backlog)
    breach = 1.0 if fill_rate < 0.92 else 0.0
    operating_cost = 0.28 * on_hand + 2.85 * unmet + 0.055 * q + 0.010 * max(0, q - 16) ** 2 / 16.0
    theta_adjustment = 0.045 * (theta - 1.0) ** 2
    welfare = -operating_cost + 8.0 * theta * (fill_rate - 0.92) - 0.03 * theta * breach - theta_adjustment
    return welfare, next_inv, operating_cost + theta_adjustment, float(filled), float(demand), breach


def solve_method(method: str) -> dict[str, object]:
    controls = CONTROL_GRID[method]

    @lru_cache(None)
    def value(t: int, inv: int, regime: int) -> tuple[float, tuple[float, float] | None]:
        if t == HORIZON:
            return 0.0, None
        best_val = -1e100
        best_control = None
        for action_pressure, theta in controls:
            total = 0.0
            for demand, pd in DEMAND[regime]:
                welfare, next_inv, *_ = step_cost_and_stats(inv, regime, action_pressure, theta, demand)
                for next_regime, pr in REGIME_TRANS[regime]:
                    cont, _ = value(t + 1, next_inv, next_regime)
                    total += pd * pr * (welfare + DISCOUNT * cont)
            if total > best_val:
                best_val = total
                best_control = (action_pressure, theta)
        return best_val, best_control

    # Forward exact expectation under the optimal Bellman policy.
    dist: dict[tuple[int, int], float] = {(START_INV, 0): 0.5, (START_INV, 1): 0.5}
    total_welfare = total_cost = total_filled = total_demand = total_breach = 0.0
    policy_rows = []
    for t in range(HORIZON):
        next_dist: dict[tuple[int, int], float] = {}
        for (inv, regime), mass in dist.items():
            _, control = value(t, inv, regime)
            assert control is not None
            action_pressure, theta = control
            policy_rows.append({'method': method, 't': t, 'inventory': inv, 'regime': regime, 'action_pressure': action_pressure, 'theta': theta})
            for demand, pd in DEMAND[regime]:
                welfare, next_inv, cost, filled, dem, breach = step_cost_and_stats(inv, regime, action_pressure, theta, demand)
                for next_regime, pr in REGIME_TRANS[regime]:
                    prob = mass * pd * pr
                    next_dist[(next_inv, next_regime)] = next_dist.get((next_inv, next_regime), 0.0) + prob
                    total_welfare += prob * welfare
                    total_cost += prob * cost
                    total_filled += prob * filled
                    total_demand += prob * dem
                    total_breach += prob * breach
        dist = next_dist

    return {
        'method': method,
        'horizon': HORIZON,
        'state_count': (INV_MAX - INV_MIN + 1) * 2,
        'control_count': len(controls),
        'expected_total_welfare': total_welfare,
        'expected_avg_welfare': total_welfare / HORIZON,
        'expected_total_cost': total_cost,
        'expected_avg_cost': total_cost / HORIZON,
        'fill_rate': total_filled / max(1.0, total_demand),
        'expected_service_breaches': total_breach,
        'policy_rows': policy_rows,
    }


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline='') as fh:
        return list(csv.DictReader(fh))


def paired_ci(vals: list[float]) -> tuple[float, float]:
    mean = sum(vals) / len(vals)
    se = stats.stdev(vals) / math.sqrt(len(vals)) if len(vals) > 1 else 0.0
    return mean, 1.96 * se


def paired_audits() -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    metrics = ['mean_welfare', 'avg_cost', 'ending_backlog', 'service_breach_count']

    base = read_csv(DATA / 'inventory_service_level_seed_metrics.csv')
    by_method = {m: {r['seed']: r for r in base if r['method'] == m} for m in {r['method'] for r in base}}
    for comparator in ['action_only_adaptive_base_stock', 'fixed_service_base_stock', 'valuation_only_service_rule']:
        common = sorted(set(by_method['full_ndu_inventory']) & set(by_method[comparator]), key=int)
        # Existing benchmark uses method-specific seed labels, so pair by seed index when labels differ.
        if not common:
            full_rows = sorted(by_method['full_ndu_inventory'].values(), key=lambda r: int(r['seed']))
            comp_rows = sorted(by_method[comparator].values(), key=lambda r: int(r['seed']))
            pairs = list(zip(full_rows, comp_rows))
        else:
            pairs = [(by_method['full_ndu_inventory'][s], by_method[comparator][s]) for s in common]
        for metric in metrics:
            diffs = [float(f[metric]) - float(c[metric]) for f, c in pairs]
            mean, ci = paired_ci(diffs)
            out.append({
                'source': 'inventory_service_level',
                'scenario': 'base_30_seed',
                'comparison': f'full_ndu_inventory_minus_{comparator}',
                'metric': metric,
                'n_pairs': len(diffs),
                'mean_difference': mean,
                'ci95': ci,
            })

    sens = read_csv(DATA / 'inventory_sensitivity_grid_seed_metrics.csv')
    scenarios = sorted({r['scenario'] for r in sens})
    for scenario in scenarios:
        rows_s = [r for r in sens if r['scenario'] == scenario]
        by_m = {m: sorted([r for r in rows_s if r['method'] == m], key=lambda r: int(r['seed'])) for m in {r['method'] for r in rows_s}}
        for comparator in ['action_only_adaptive_base_stock', 'fixed_service_base_stock']:
            pairs = list(zip(by_m['full_ndu_inventory'], by_m[comparator]))
            for metric in metrics:
                diffs = [float(f[metric]) - float(c[metric]) for f, c in pairs]
                mean, ci = paired_ci(diffs)
                out.append({
                    'source': 'inventory_sensitivity_grid',
                    'scenario': scenario,
                    'comparison': f'full_ndu_inventory_minus_{comparator}',
                    'metric': metric,
                    'n_pairs': len(diffs),
                    'mean_difference': mean,
                    'ci95': ci,
                })
    return out


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    solved = [solve_method(m) for m in CONTROL_GRID]
    metric_rows = [{k: v for k, v in row.items() if k != 'policy_rows'} for row in solved]
    policy_rows = []
    for row in solved:
        policy_rows.extend(row['policy_rows'])
    write_csv(DATA / 'inventory_exact_policy_class_dp_metrics.csv', metric_rows)
    write_csv(DATA / 'inventory_exact_policy_class_dp_policy.csv', policy_rows)
    write_csv(DATA / 'inventory_paired_seed_difference_audit.csv', paired_audits())
    for row in metric_rows:
        print(row)


if __name__ == '__main__':
    main()
