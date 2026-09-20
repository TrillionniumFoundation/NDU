#!/usr/bin/env python3
"""Compact inventory equal-budget and theta-scoring robustness audits.

This script is intentionally narrower than the main inventory benchmark.  It
uses the same demand dynamics and bounded policy maps, but it runs a compact
same-CEM-evaluation audit and two theta-specific stress tests:
  * fixed/permuted theta ablations for trained Full-NDU inventory policies;
  * a small theta-adjustment-cost sweep for Full NDU versus action-only control.

The purpose is not to claim universal inventory dominance.  The audit checks
whether the OR-facing inventory conclusions survive physical metrics and whether
learned theta is acting as a useful state-dependent service-pressure channel
rather than only as a scoring rescale.
"""
from __future__ import annotations

import argparse
import csv
import math
import statistics as stats
from pathlib import Path

import numpy as np

HORIZON = 40
SEARCH_EPISODES = 32
REPORT_EPISODES = 384
EQUAL_SEEDS = 12
SWEEP_SEEDS = 8
SEED_STRIDE = 1000
COMMON_ITERATIONS = 8
COMMON_POPULATION = 24
COMMON_EVALUATIONS = COMMON_ITERATIONS * COMMON_POPULATION
METHODS = [
    'full_ndu_inventory',
    'action_only_adaptive_base_stock',
    'fixed_service_base_stock',
    'valuation_only_service_rule',
]


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40.0, 40.0)))


def method_dim(method: str) -> int:
    return {
        'full_ndu_inventory': 12,
        'action_only_adaptive_base_stock': 7,
        'fixed_service_base_stock': 3,
        'valuation_only_service_rule': 6,
    }[method]


def seed_values(base: int, count: int) -> list[int]:
    return [base + SEED_STRIDE * (j + 1) for j in range(count)]


def policy(method: str, params: np.ndarray, t: int, ewma, inventory, backlog, last_demand, rng: np.random.Generator, theta_mode: str):
    shock = np.maximum(0.0, last_demand - ewma)
    features = np.vstack([
        np.ones_like(ewma),
        np.ones_like(ewma) * (t / max(HORIZON - 1, 1) - 0.5),
        (ewma - 22.0) / 12.0,
        backlog / 24.0,
        shock / 12.0,
        (inventory - 24.0) / 36.0,
    ])

    if method == 'full_ndu_inventory':
        theta_raw = 0.55 + 1.65 * sigmoid(params[:6] @ features)
        action_pressure = 0.35 + 1.95 * sigmoid(params[6:12] @ features)
        theta = theta_raw.copy()
        if theta_mode == 'fixed_one':
            theta = np.ones_like(theta)
        elif theta_mode == 'permuted':
            theta = theta[rng.permutation(len(theta))]
        elif theta_mode != 'normal':
            raise ValueError(theta_mode)
        backlog_boost = 0.55 + 0.45 * theta
    elif method == 'action_only_adaptive_base_stock':
        theta = np.ones_like(ewma)
        action_pressure = 0.35 + 1.95 * sigmoid(params[:6] @ features)
        backlog_boost = 0.65 + 0.55 * sigmoid(params[6])
    elif method == 'fixed_service_base_stock':
        theta = np.ones_like(ewma)
        z = params[0] + params[1] * (ewma - 22.0) / 12.0 + params[2] * (t / max(HORIZON - 1, 1) - 0.5)
        action_pressure = 0.45 + 1.65 * sigmoid(z)
        backlog_boost = 0.70
    elif method == 'valuation_only_service_rule':
        theta_raw = 0.55 + 1.65 * sigmoid(params[:6] @ features)
        theta = theta_raw.copy()
        if theta_mode == 'fixed_one':
            theta = np.ones_like(theta)
        elif theta_mode == 'permuted':
            theta = theta[rng.permutation(len(theta))]
        elif theta_mode != 'normal':
            raise ValueError(theta_mode)
        action_pressure = 1.05
        backlog_boost = 0.55 + 0.45 * theta
    else:
        raise ValueError(method)

    demand_forecast = ewma + 0.40 * shock + 0.22 * backlog
    order_up_to = demand_forecast * (1.0 + 0.42 * theta * action_pressure) + backlog_boost * backlog
    order_up_to = np.clip(order_up_to, 0.0, 115.0)
    q = np.maximum(0.0, order_up_to - inventory)
    return q, theta


def simulate(method: str, params: np.ndarray, seed: int, episodes: int, theta_cost_multiplier: float = 1.0, theta_mode: str = 'normal') -> dict[str, float]:
    rng = np.random.default_rng(seed)
    theta_rng = np.random.default_rng(seed + 99173)
    inventory = np.full(episodes, 26.0)
    backlog = np.zeros(episodes)
    ewma = np.full(episodes, 22.0)
    last_demand = np.full(episodes, 22.0)
    high = np.zeros(episodes, dtype=bool)
    total_cost = np.zeros(episodes)
    total_cost_no_theta = np.zeros(episodes)
    total_demand = np.zeros(episodes)
    total_filled = np.zeros(episodes)
    total_order = np.zeros(episodes)
    total_inventory = np.zeros(episodes)
    service_breach = np.zeros(episodes)
    theta_path = []

    for t in range(HORIZON):
        q, theta = policy(method, params, t, ewma, inventory, backlog, last_demand, theta_rng, theta_mode)
        inventory = inventory + q
        flips_down = rng.random(episodes) < 0.08
        flips_up = rng.random(episodes) < 0.12
        high = np.where(high, ~flips_down, flips_up)
        seasonal = 2.5 * math.sin(2.0 * math.pi * t / 20.0)
        mean = 18.0 + seasonal + high.astype(float) * 10.0
        sd = 3.0 + high.astype(float) * 1.5
        demand = np.maximum(0.0, np.rint(rng.normal(mean, sd))).astype(float)
        total_need = backlog + demand
        filled = np.minimum(inventory, total_need)
        inventory = inventory - filled
        backlog = total_need - filled
        fill_rate_t = np.where(total_need <= 1e-9, 1.0, filled / total_need)
        service_breach += fill_rate_t < 0.92

        holding_cost = 0.28 * inventory
        shortage_cost = 2.85 * backlog
        order_cost = 0.055 * q + 0.010 * np.maximum(0.0, q - 35.0) ** 2 / 35.0
        theta_cost = (0.045 * theta_cost_multiplier) * (theta - 1.0) ** 2
        base_cost = holding_cost + shortage_cost + order_cost
        total_cost += base_cost + theta_cost
        total_cost_no_theta += base_cost
        total_demand += demand
        total_filled += filled
        total_order += q
        total_inventory += inventory
        theta_path.append(theta)
        ewma = 0.82 * ewma + 0.18 * demand
        last_demand = demand

    fill_rate = total_filled / np.maximum(total_demand, 1.0)
    avg_cost = total_cost / HORIZON
    avg_cost_no_theta = total_cost_no_theta / HORIZON
    avg_inventory = total_inventory / HORIZON
    avg_order = total_order / HORIZON
    theta_stack = np.vstack(theta_path)
    theta_std = np.std(theta_stack, axis=0)
    welfare = -avg_cost + 8.0 * (fill_rate - 0.92) - 0.03 * service_breach
    welfare_no_theta = -avg_cost_no_theta + 8.0 * (fill_rate - 0.92) - 0.03 * service_breach
    return {
        'mean_welfare': float(np.mean(welfare)),
        'mean_welfare_no_theta_cost': float(np.mean(welfare_no_theta)),
        'avg_cost': float(np.mean(avg_cost)),
        'avg_cost_no_theta': float(np.mean(avg_cost_no_theta)),
        'fill_rate': float(np.mean(fill_rate)),
        'ending_backlog': float(np.mean(backlog)),
        'avg_inventory': float(np.mean(avg_inventory)),
        'avg_order': float(np.mean(avg_order)),
        'theta_std': float(np.mean(theta_std)),
        'theta_mean_abs_deviation_from_one': float(np.mean(np.abs(theta_stack - 1.0))),
        'service_breach_count': float(np.mean(service_breach)),
    }


class CEM:
    def __init__(self, dim: int, seed: int) -> None:
        self.rng = np.random.default_rng(seed)
        self.mean = np.zeros(dim)
        self.std = np.ones(dim) * 0.85

    def run(self, score_fn, iterations: int = COMMON_ITERATIONS, population: int = COMMON_POPULATION) -> tuple[np.ndarray, float, int]:
        elite_n = max(2, int(math.ceil(population * 0.25)))
        best_params = self.mean.copy()
        best_score = -1e100
        evals = 0
        for _ in range(iterations):
            samples = self.rng.normal(self.mean, self.std, size=(population, len(self.mean)))
            scores = np.array([score_fn(samples[i]) for i in range(population)])
            evals += population
            j = int(np.argmax(scores))
            if scores[j] > best_score:
                best_score = float(scores[j])
                best_params = samples[j].copy()
            elite_idx = np.argsort(scores)[-elite_n:]
            elites = samples[elite_idx]
            emean = elites.mean(axis=0)
            estd = elites.std(axis=0)
            self.mean = 0.82 * emean + 0.18 * self.mean
            self.std = np.maximum(0.06, 0.70 * estd + 0.30 * self.std)
        return best_params, best_score, evals


def optimize(method: str, seed: int, theta_cost_multiplier: float = 1.0) -> tuple[np.ndarray, float, int]:
    cem = CEM(method_dim(method), seed + 17)

    def score(params: np.ndarray) -> float:
        return simulate(method, params, seed + 100000, SEARCH_EPISODES, theta_cost_multiplier, 'normal')['mean_welfare']

    return cem.run(score)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict[str, object]]) -> list[dict[str, str]]:
    groups: dict[tuple[str, str, str], list[dict[str, object]]] = {}
    for row in rows:
        key = (str(row['audit']), str(row['method']), str(row['evaluation_variant']), str(row['theta_cost_multiplier']))
        groups.setdefault(key, []).append(row)
    metrics = ['mean_welfare', 'mean_welfare_no_theta_cost', 'avg_cost', 'avg_cost_no_theta', 'fill_rate', 'ending_backlog', 'theta_std', 'theta_mean_abs_deviation_from_one', 'service_breach_count']
    out: list[dict[str, str]] = []
    for key in sorted(groups):
        rs = groups[key]
        summary: dict[str, str] = {'audit': key[0], 'method': key[1], 'evaluation_variant': key[2], 'n': str(len(rs))}
        summary['theta_cost_multiplier'] = str(rs[0]['theta_cost_multiplier'])
        summary['policy_evaluations'] = str(rs[0]['policy_evaluations'])
        summary['param_dim'] = str(rs[0]['param_dim'])
        for metric in metrics:
            vals = [float(r[metric]) for r in rs]
            mean = sum(vals) / len(vals)
            sd = stats.stdev(vals) if len(vals) > 1 else 0.0
            se = sd / math.sqrt(len(vals)) if vals else 0.0
            summary[metric] = f'{mean:.12g}'
            summary[f'{metric}_ci95'] = f'{1.96 * se:.12g}'
        out.append(summary)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--outdir', default=str(Path(__file__).resolve().parents[1] / 'data'))
    args = parser.parse_args()
    outdir = Path(args.outdir).resolve()
    rows: list[dict[str, object]] = []
    bases = {
        'full_ndu_inventory': 7061,
        'action_only_adaptive_base_stock': 7161,
        'fixed_service_base_stock': 7261,
        'valuation_only_service_rule': 7361,
    }

    # Compact equal-evaluation audit and full-theta ablation on the same trained policies.
    for method in METHODS:
        for seed in seed_values(bases[method], EQUAL_SEEDS):
            params, search_score, evals = optimize(method, seed, 1.0)
            variants = ['normal']
            if method == 'full_ndu_inventory':
                variants += ['fixed_one', 'permuted']
            for variant in variants:
                report = simulate(method, params, seed + 500000, REPORT_EPISODES, 1.0, variant)
                row: dict[str, object] = {
                    'audit': 'equal_budget_inventory' if variant == 'normal' else 'theta_ablation_inventory',
                    'method': method,
                    'seed': seed,
                    'param_dim': method_dim(method),
                    'policy_evaluations': evals,
                    'search_mean_welfare': search_score,
                    'theta_cost_multiplier': 1.0,
                    'evaluation_variant': variant,
                }
                row.update(report)
                rows.append(row)
            print('equal', method, seed, flush=True)

    # Small cost sweep: Full NDU versus action-only under common search budgets.
    for multiplier in [0.0, 1.0, 4.0]:
        for method in ['full_ndu_inventory', 'action_only_adaptive_base_stock']:
            for seed in seed_values(bases[method] + int(multiplier * 100), SWEEP_SEEDS):
                params, search_score, evals = optimize(method, seed, multiplier)
                report = simulate(method, params, seed + 500000, REPORT_EPISODES, multiplier, 'normal')
                row = {
                    'audit': 'theta_cost_sweep_inventory',
                    'method': method,
                    'seed': seed,
                    'param_dim': method_dim(method),
                    'policy_evaluations': evals,
                    'search_mean_welfare': search_score,
                    'theta_cost_multiplier': multiplier,
                    'evaluation_variant': 'normal',
                }
                row.update(report)
                rows.append(row)
                print('sweep', multiplier, method, seed, flush=True)

    summary = summarize(rows)
    write_csv(outdir / 'inventory_equal_budget_theta_audit_seed_metrics.csv', rows)
    write_csv(outdir / 'inventory_equal_budget_theta_audit_metrics.csv', summary)
    print(outdir / 'inventory_equal_budget_theta_audit_seed_metrics.csv')
    print(outdir / 'inventory_equal_budget_theta_audit_metrics.csv')


if __name__ == '__main__':
    main()
