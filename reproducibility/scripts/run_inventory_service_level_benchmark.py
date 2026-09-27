#!/usr/bin/env python3
"""Canonical OR inventory/service-level benchmark for the NDU OR manuscript.

The benchmark models periodic-review inventory with stochastic regime-shifting
demand. Full NDU jointly controls the order-up-to action and an internal
service-level/shortage-penalty pressure (theta). Baselines remove one or both
channels while preserving the same demand information. The script uses only
NumPy plus the Python standard library and writes CSV files used by the paper
and reproducibility checker.
"""
from __future__ import annotations

import argparse
import csv
import math
import statistics as stats
from pathlib import Path

import numpy as np

METHODS = [
    'full_ndu_inventory',
    'action_only_adaptive_base_stock',
    'fixed_service_base_stock',
    'valuation_only_service_rule',
]
SEED_COUNT = 30
SEED_STRIDE = 1000
HORIZON = 40
SEARCH_EPISODES = 48
REPORT_EPISODES = 512


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40.0, 40.0)))


def method_dim(method: str) -> int:
    return {
        'full_ndu_inventory': 12,
        'action_only_adaptive_base_stock': 7,
        'fixed_service_base_stock': 3,
        'valuation_only_service_rule': 6,
    }[method]


def seed_values(base: int) -> list[int]:
    return [base + SEED_STRIDE * (j + 1) for j in range(SEED_COUNT)]


def policy(method: str, params: np.ndarray, t: int, ewma, inventory, backlog, last_demand):
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
        theta = 0.55 + 1.65 * sigmoid(params[:6] @ features)
        action_pressure = 0.35 + 1.95 * sigmoid(params[6:12] @ features)
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
        theta = 0.55 + 1.65 * sigmoid(params[:6] @ features)
        action_pressure = 1.05
        backlog_boost = 0.55 + 0.45 * theta
    else:
        raise ValueError(method)

    demand_forecast = ewma + 0.40 * shock + 0.22 * backlog
    order_up_to = demand_forecast * (1.0 + 0.42 * theta * action_pressure) + backlog_boost * backlog
    order_up_to = np.clip(order_up_to, 0.0, 115.0)
    q = np.maximum(0.0, order_up_to - inventory)
    return q, theta


def simulate(method: str, params: np.ndarray, seed: int, episodes: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    inventory = np.full(episodes, 26.0)
    backlog = np.zeros(episodes)
    ewma = np.full(episodes, 22.0)
    last_demand = np.full(episodes, 22.0)
    high = np.zeros(episodes, dtype=bool)
    total_cost = np.zeros(episodes)
    total_demand = np.zeros(episodes)
    total_filled = np.zeros(episodes)
    total_order = np.zeros(episodes)
    total_inventory = np.zeros(episodes)
    service_breach = np.zeros(episodes)
    theta_path = []

    for t in range(HORIZON):
        q, theta = policy(method, params, t, ewma, inventory, backlog, last_demand)
        inventory = inventory + q
        # Persistent high-demand regime.
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
        theta_cost = 0.045 * (theta - 1.0) ** 2
        total_cost += holding_cost + shortage_cost + order_cost + theta_cost
        total_demand += demand
        total_filled += filled
        total_order += q
        total_inventory += inventory
        theta_path.append(theta)
        ewma = 0.82 * ewma + 0.18 * demand
        last_demand = demand

    fill_rate = total_filled / np.maximum(total_demand, 1.0)
    avg_cost = total_cost / HORIZON
    avg_inventory = total_inventory / HORIZON
    avg_order = total_order / HORIZON
    theta_stack = np.vstack(theta_path)
    theta_std = np.std(theta_stack, axis=0)
    welfare = -avg_cost + 8.0 * (fill_rate - 0.92) - 0.03 * service_breach
    return {
        'mean_welfare': float(np.mean(welfare)),
        'avg_cost': float(np.mean(avg_cost)),
        'fill_rate': float(np.mean(fill_rate)),
        'ending_backlog': float(np.mean(backlog)),
        'avg_inventory': float(np.mean(avg_inventory)),
        'avg_order': float(np.mean(avg_order)),
        'theta_std': float(np.mean(theta_std)),
        'service_breach_count': float(np.mean(service_breach)),
    }


class CEM:
    def __init__(self, dim: int, seed: int) -> None:
        self.rng = np.random.default_rng(seed)
        self.mean = np.zeros(dim)
        self.std = np.ones(dim) * 0.85

    def run(self, score_fn, iterations: int, population: int) -> tuple[np.ndarray, float, int]:
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


def evaluate(method: str, params: np.ndarray, base_seed: int, episodes: int) -> dict[str, float]:
    return simulate(method, params, base_seed, episodes)


def optimize_and_report(method: str, seed: int) -> dict[str, float | str | int]:
    dim = method_dim(method)
    if method == 'full_ndu_inventory':
        iterations, population = 11, 26
    elif method in {'action_only_adaptive_base_stock', 'valuation_only_service_rule'}:
        iterations, population = 9, 22
    else:
        iterations, population = 8, 18
    cem = CEM(dim, seed + 17)

    def score(params: np.ndarray) -> float:
        return evaluate(method, params, seed + 100000, SEARCH_EPISODES)['mean_welfare']

    params, search_score, evaluations = cem.run(score, iterations, population)
    report = evaluate(method, params, seed + 500000, REPORT_EPISODES)
    row: dict[str, float | str | int] = {
        'method': method,
        'seed': seed,
        'param_dim': dim,
        'cem_iterations': iterations,
        'cem_population': population,
        'policy_evaluations': evaluations,
        'search_mean_welfare': search_score,
    }
    row.update(report)
    return row


def summarize(rows: list[dict[str, float | str | int]]) -> list[dict[str, str]]:
    out = []
    metrics = ['mean_welfare', 'avg_cost', 'fill_rate', 'ending_backlog', 'avg_inventory', 'avg_order', 'theta_std', 'service_breach_count']
    for method in METHODS:
        rs = [r for r in rows if r['method'] == method]
        summary: dict[str, str] = {'method': method, 'n': str(len(rs))}
        for metric in metrics:
            vals = [float(r[metric]) for r in rs]
            mean = sum(vals) / len(vals)
            sd = stats.stdev(vals) if len(vals) > 1 else 0.0
            se = sd / math.sqrt(len(vals)) if vals else 0.0
            summary[metric] = f'{mean:.12g}'
            summary[f'{metric}_ci95'] = f'{1.96 * se:.12g}'
        out.append(summary)
    best = max(float(r['mean_welfare']) for r in out)
    for row in out:
        row['welfare_gap_to_best'] = f'{best - float(row["mean_welfare"]):.12g}'
    return out


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--outdir', default=str(Path(__file__).resolve().parents[1] / 'data'))
    args = parser.parse_args()
    outdir = Path(args.outdir).resolve()
    rows: list[dict[str, float | str | int]] = []
    base_seeds = {
        'full_ndu_inventory': 61,
        'action_only_adaptive_base_stock': 161,
        'fixed_service_base_stock': 261,
        'valuation_only_service_rule': 361,
    }
    for method in METHODS:
        for seed in seed_values(base_seeds[method]):
            rows.append(optimize_and_report(method, seed))
            print(method, seed, flush=True)
    summary = summarize(rows)
    write_csv(outdir / 'inventory_service_level_seed_metrics.csv', rows)
    write_csv(outdir / 'inventory_service_level_metrics.csv', summary)
    print(outdir / 'inventory_service_level_metrics.csv')


if __name__ == '__main__':
    main()
