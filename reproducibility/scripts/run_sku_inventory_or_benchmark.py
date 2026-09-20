#!/usr/bin/env python3
"""SKU-panel inventory benchmark and valuation-control DP audit.

This dependency-light script adds a public/semi-real SKU demand panel to the
inventory evidence for the NDU OR paper.  The raw monthly SKU panel is bundled
under ``reproducibility/data/sku_monthly_demand_source.csv`` from the public
``supplychainpy`` sample data with SKU identifiers anonymized to SKU001, SKU002,
etc. (BSD-style license in the upstream repository).
The script never downloads data at run time; it converts the bundled panel into
a normalized long trace, calibrates policies only on months 1--8, and evaluates
on months 9--12 under common bootstrapped demand perturbations.

The reported policies deliberately include strong classical OR comparators:
rolling/seasonal/service-tuned base-stock variants, an MPC scenario controller,
an approximate-DP controller, and a tabular inventory-RL controller.  The Full
NDU row uses the same observed demand panel but adds an endogenous service
pressure/shortage-penalty control theta_t.  All external cost metrics are
reported on a theta-free evaluator so the theta channel cannot win by changing
its own scoring rule.

The script also solves a small exact finite-state MDP whose state includes the
previous valuation-control level.  The Full valuation-control action space is a
Cartesian product of order-up-to targets and next theta levels, so the exact DP
is a direct Bellman test of endogenous valuation control rather than a code-path
policy-class illustration.
"""
from __future__ import annotations

import argparse
import csv
import math
import statistics as stats
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
SOURCE = DATA / 'sku_monthly_demand_source.csv'
PANEL = DATA / 'sku_monthly_demand_panel.csv'
SEED_METRICS = DATA / 'sku_inventory_baseline_seed_metrics.csv'
METRICS = DATA / 'sku_inventory_baseline_metrics.csv'
THETA_SURFACE = DATA / 'sku_theta_policy_surface.csv'
THETA_PNG = ROOT.parent / 'fig_inventory_theta_policy_surface.png'
DP_METRICS = DATA / 'inventory_exact_valuation_control_mdp_metrics.csv'
DP_POLICY = DATA / 'inventory_exact_valuation_control_mdp_policy.csv'

MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
TRAIN_MONTHS = set(range(1, 9))
TEST_MONTHS = [9, 10, 11, 12]
SEEDS = [7100 + 97 * k for k in range(24)]

METHODS = [
    'full_ndu_theta_service_control',
    'rolling_forecast_base_stock_backlog',
    'rolling_forecast_base_stock_lost_sales',
    'seasonal_service_tuned_base_stock',
    'mpc_scenario_base_stock',
    'approximate_dp_inventory',
    'tabular_inventory_rl',
]


@dataclass
class SKU:
    sku: str
    demands: list[float]  # normalized by train mean, months 1--12
    raw_demands: list[float]
    train_mean: float
    unit_cost: float
    retail_price: float
    lead_time: int
    initial_inventory: float
    initial_backlog: float
    margin_ratio: float
    shortage_weight: float
    capacity: float


def percentile(values: Iterable[float], q: float) -> float:
    xs = sorted(float(v) for v in values)
    if not xs:
        return 0.0
    pos = (len(xs) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    return xs[lo] * (hi - pos) + xs[hi] * (pos - lo)


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(-40.0, min(40.0, x))))


def load_skus() -> list[SKU]:
    rows = []
    with SOURCE.open(newline='') as fh:
        for row in csv.DictReader(fh):
            raw = [float(row[m]) for m in MONTHS]
            train_mean = max(1.0, sum(raw[:8]) / 8.0)
            demand = [x / train_mean for x in raw]
            unit_cost = float(row['unit cost'])
            retail_price = max(unit_cost + 1.0, float(row['retail_price']))
            margin_ratio = max(0.05, min(0.95, (retail_price - unit_cost) / retail_price))
            lead_time = int(float(row['lead-time']))
            initial_inventory = max(0.0, min(2.30, float(row['quantity_on_hand']) / train_mean))
            initial_backlog = max(0.0, min(0.75, float(row['backlog']) / train_mean))
            shortage_weight = 1.55 + 1.85 * margin_ratio + 0.08 * min(6, lead_time)
            # Normalized monthly order capacity; longer lead times tighten usable capacity.
            capacity = max(1.15, min(2.75, 2.25 - 0.12 * max(0, lead_time - 2) + 0.25 * margin_ratio))
            rows.append(SKU(
                sku=row['Sku'], demands=demand, raw_demands=raw, train_mean=train_mean,
                unit_cost=unit_cost, retail_price=retail_price, lead_time=lead_time,
                initial_inventory=initial_inventory, initial_backlog=initial_backlog,
                margin_ratio=margin_ratio, shortage_weight=shortage_weight, capacity=capacity,
            ))
    return rows


def write_panel(skus: list[SKU]) -> None:
    rows = []
    for s in skus:
        for j, month_name in enumerate(MONTHS, start=1):
            rows.append({
                'sku': s.sku,
                'month_index': j,
                'month_name': month_name,
                'raw_demand': f'{s.raw_demands[j-1]:.6f}',
                'normalized_demand': f'{s.demands[j-1]:.10f}',
                'split': 'train' if j in TRAIN_MONTHS else 'test',
                'unit_cost': f'{s.unit_cost:.6f}',
                'retail_price': f'{s.retail_price:.6f}',
                'lead_time': s.lead_time,
                'initial_inventory_normalized': f'{s.initial_inventory:.10f}',
                'initial_backlog_normalized': f'{s.initial_backlog:.10f}',
                'margin_ratio': f'{s.margin_ratio:.10f}',
                'shortage_weight': f'{s.shortage_weight:.10f}',
                'capacity_normalized': f'{s.capacity:.10f}',
                'source_dataset': 'supplychainpy sample complete_dataset_small.csv',
                'source_url': 'https://github.com/KevinFasusi/supplychainpy',
                'source_license': 'BSD-3-Clause-style upstream LICENSE',
            })
    write_csv(PANEL, rows)


def fit_global_seasonality(skus: list[SKU]) -> tuple[float, float, float]:
    # Fit normalized demand = beta0 + beta1 sin(2*pi*m/12)+beta2 cos(2*pi*m/12) on train months only.
    X = []
    y = []
    for s in skus:
        for m in range(1, 9):
            ang = 2.0 * math.pi * (m - 1) / 12.0
            X.append([1.0, math.sin(ang), math.cos(ang)])
            y.append(s.demands[m - 1])
    beta, *_ = np.linalg.lstsq(np.asarray(X), np.asarray(y), rcond=None)
    return float(beta[0]), float(beta[1]), float(beta[2])


def seasonal_factor(beta: tuple[float, float, float], month: int) -> float:
    ang = 2.0 * math.pi * (month - 1) / 12.0
    val = beta[0] + beta[1] * math.sin(ang) + beta[2] * math.cos(ang)
    return max(0.45, min(1.85, val))


def demand_scenario(s: SKU, month: int, seed: int, sku_index: int) -> float:
    """Held-out SKU demand with train-residual bootstrap perturbation."""
    rng = np.random.default_rng(seed + 10007 * (sku_index + 1) + 137 * month)
    residuals = [max(0.25, min(2.75, d)) for d in s.demands[:8]]
    factor = float(rng.choice(residuals))
    # Shrink perturbation toward one: the held-out month remains the real panel anchor.
    factor = 0.78 + 0.22 * factor
    noise = float(rng.lognormal(mean=-0.5 * 0.08**2, sigma=0.08))
    return max(0.0, s.demands[month - 1] * factor * noise)


def step_inventory(inv: float, backlog: float, q: float, demand: float, s: SKU, theta: float, lost_sales: bool) -> tuple[float, float, dict[str, float]]:
    q = max(0.0, min(q, 3.25))
    capacity_excess = max(0.0, q - s.capacity)
    inv += q
    need = demand if lost_sales else backlog + demand
    filled = min(max(inv, 0.0), need)
    inv = inv - filled
    unmet = max(0.0, need - filled)
    next_backlog = 0.0 if lost_sales else unmet
    lost = unmet if lost_sales else 0.0
    on_hand = max(0.0, inv)
    fill = 1.0 if need <= 1e-12 else filled / need
    external_cost = (
        0.17 * on_hand
        + s.shortage_weight * (unmet + 0.80 * lost)
        + 0.045 * q
        + 0.075 * capacity_excess * capacity_excess
        + (0.012 if q > 1e-9 else 0.0)
    )
    theta_adjustment = 0.030 * (theta - 1.0) ** 2
    target_fill = max(0.86, min(0.985, 0.875 + 0.055 * theta))
    # Valuation-control welfare must use theta as service pressure, consistent
    # with the corrected service-pressure valuation objective.  The theta-free
    # external evaluator remains below as a physical-cost diagnostic, but it is
    # not the NDU objective optimized by the Full valuation-control policy.
    valuation_welfare = -external_cost + 3.75 * theta * (fill - 0.90) - 0.035 * theta * (fill < 0.90) - theta_adjustment
    external_welfare = -external_cost + 3.75 * (fill - 0.90) - 0.035 * (fill < 0.90)
    return inv, next_backlog, {
        'order': q,
        'filled': filled,
        'demand': demand,
        'fill': fill,
        'unmet': unmet,
        'lost_sales': lost,
        'external_cost': external_cost,
        'theta_adjustment': theta_adjustment,
        'valuation_welfare': valuation_welfare,
        'external_welfare': external_welfare,
        'target_fill': target_fill,
        'capacity_excess': capacity_excess,
    }


def theta_policy(last_demand: float, ewma: float, backlog: float, capacity_tightness: float, s: SKU) -> float:
    shock = max(0.0, last_demand - ewma) / max(0.35, ewma)
    backlog_pressure = backlog / max(0.35, ewma)
    margin_pressure = (s.shortage_weight - 2.25) / 1.5
    theta = 0.82 + 0.46 * shock + 0.72 * backlog_pressure + 0.52 * capacity_tightness + 0.18 * margin_pressure
    return max(0.55, min(2.20, theta))


def order_decision(method: str, s: SKU, month: int, inv: float, backlog: float, ewma: float, last_demand: float,
                   beta: tuple[float, float, float], params: dict[str, float], adp_policy=None, q_policy=None) -> tuple[float, float, bool]:
    season = seasonal_factor(beta, month)
    shock = max(0.0, last_demand - ewma)
    forecast = max(0.05, (0.64 * ewma + 0.36 * last_demand) * season)
    capacity_tightness = max(0.0, forecast / max(0.25, s.capacity) - 1.0)
    lost_sales = False
    theta = 1.0

    if method == 'full_ndu_theta_service_control':
        theta = theta_policy(last_demand, ewma, backlog, capacity_tightness, s)
        target = forecast * (params['ndu_base'] + params['ndu_theta_gain'] * theta + params['ndu_capacity_gain'] * capacity_tightness) + backlog * (params['ndu_backlog_base'] + params['ndu_backlog_theta'] * theta)
    elif method == 'rolling_forecast_base_stock_backlog':
        target = forecast * params['rolling_multiplier'] + backlog
    elif method == 'rolling_forecast_base_stock_lost_sales':
        lost_sales = True
        target = forecast * params['lost_sales_multiplier']
    elif method == 'seasonal_service_tuned_base_stock':
        target = forecast * params['seasonal_multiplier'] + params['backlog_weight'] * backlog
    elif method == 'mpc_scenario_base_stock':
        q, theta = mpc_order(s, inv, backlog, forecast, last_demand, ewma, month, beta)
        return q, theta, False
    elif method == 'approximate_dp_inventory':
        target_mult = adp_policy(s, inv, backlog, forecast, month) if adp_policy else 1.20
        target = forecast * target_mult + 0.85 * backlog
    elif method == 'tabular_inventory_rl':
        target_mult = q_policy(s, inv, backlog, forecast, month, last_demand, ewma) if q_policy else 1.15
        target = forecast * target_mult + backlog
    else:
        raise ValueError(method)
    return max(0.0, target - inv), theta, lost_sales


def replay_method(method: str, skus: list[SKU], seed: int, beta: tuple[float, float, float], params: dict[str, float], adp_policy=None, q_policy=None,
                  months: Iterable[int] = TEST_MONTHS, bootstrapped: bool = True) -> dict[str, float]:
    totals = defaultdict(float)
    period_count = 0
    for idx, s in enumerate(skus):
        inv = s.initial_inventory
        backlog = s.initial_backlog
        ewma = sum(s.demands[:8]) / 8.0
        last = s.demands[7]
        for month in months:
            demand = demand_scenario(s, month, seed, idx) if bootstrapped else s.demands[month - 1]
            q, theta, lost_sales = order_decision(method, s, month, inv, backlog, ewma, last, beta, params, adp_policy, q_policy)
            inv, backlog, st = step_inventory(inv, backlog, q, demand, s, theta, lost_sales)
            for k, v in st.items():
                totals[k] += float(v)
            totals['ending_inventory'] += max(0.0, inv)
            totals['ending_backlog'] += backlog
            totals['theta'] += theta
            totals['theta_sq'] += theta * theta
            totals['periods'] += 1.0
            period_count += 1
            ewma = 0.72 * ewma + 0.28 * demand
            last = demand
    n = max(1.0, totals['periods'])
    fill_rate = totals['filled'] / max(1e-12, totals['demand'] + (0.0 if 'lost_sales' else 0.0))
    theta_mean = totals['theta'] / n
    theta_var = max(0.0, totals['theta_sq'] / n - theta_mean * theta_mean)
    return {
        'external_avg_cost': totals['external_cost'] / n,
        'valuation_adjusted_welfare': totals['valuation_welfare'] / n,
        'theta_free_external_welfare': totals['external_welfare'] / n,
        'fill_rate': fill_rate,
        'avg_order': totals['order'] / n,
        'avg_ending_inventory': totals['ending_inventory'] / n,
        'avg_ending_backlog': totals['ending_backlog'] / n,
        'lost_sales_rate': totals['lost_sales'] / max(1e-12, totals['demand']),
        'capacity_excess_rate': totals['capacity_excess'] / n,
        'theta_mean': theta_mean,
        'theta_std': math.sqrt(theta_var),
        'target_fill_mean': totals['target_fill'] / n,
        'periods': n,
    }


def calibrate_base_stock(skus: list[SKU], beta: tuple[float, float, float]) -> dict[str, float]:
    params = {
        'rolling_multiplier': 1.24,
        'lost_sales_multiplier': 1.18,
        'seasonal_multiplier': 1.26,
        'backlog_weight': 0.95,
        'ndu_base': 0.96,
        'ndu_theta_gain': 0.34,
        'ndu_capacity_gain': 0.08,
        'ndu_backlog_base': 0.70,
        'ndu_backlog_theta': 0.42,
    }
    grids = {
        'rolling_multiplier': [1.02, 1.12, 1.22, 1.34, 1.48],
        'lost_sales_multiplier': [0.95, 1.05, 1.15, 1.28, 1.42],
        'seasonal_multiplier': [1.04, 1.16, 1.28, 1.42, 1.58],
        'backlog_weight': [0.55, 0.80, 1.05, 1.30],
        'ndu_base': [0.88, 0.98, 1.08, 1.18],
        'ndu_theta_gain': [0.18, 0.28, 0.38, 0.50],
        'ndu_capacity_gain': [0.00, 0.08, 0.16],
        'ndu_backlog_base': [0.60, 0.85, 1.10],
        'ndu_backlog_theta': [0.20, 0.40, 0.62],
    }
    # Tune each family on train months only, using deterministic train replay.
    best_tuple, best_cost = None, 1e100
    for ndu_base in grids['ndu_base']:
        for ndu_theta_gain in grids['ndu_theta_gain']:
            for ndu_capacity_gain in grids['ndu_capacity_gain']:
                for ndu_backlog_base in grids['ndu_backlog_base']:
                    for ndu_backlog_theta in grids['ndu_backlog_theta']:
                        trial = dict(params, ndu_base=ndu_base, ndu_theta_gain=ndu_theta_gain, ndu_capacity_gain=ndu_capacity_gain, ndu_backlog_base=ndu_backlog_base, ndu_backlog_theta=ndu_backlog_theta)
                        # Tune Full NDU on valuation-control welfare, not on the
                        # theta-free external-cost diagnostic.  Otherwise the
                        # reported approximate-DP comparison is solving a
                        # different objective than the NDU policy.
                        welfare = replay_method('full_ndu_theta_service_control', skus, 999, beta, trial, months=range(3, 9), bootstrapped=False)['valuation_adjusted_welfare']
                        score = -welfare
                        if score < best_cost:
                            best_tuple, best_cost = (ndu_base, ndu_theta_gain, ndu_capacity_gain, ndu_backlog_base, ndu_backlog_theta), score
    params['ndu_base'], params['ndu_theta_gain'], params['ndu_capacity_gain'], params['ndu_backlog_base'], params['ndu_backlog_theta'] = best_tuple

    for key in ['rolling_multiplier', 'lost_sales_multiplier']:
        best, best_cost = params[key], 1e100
        for val in grids[key]:
            trial = dict(params, **{key: val})
            method = 'rolling_forecast_base_stock_backlog' if key == 'rolling_multiplier' else 'rolling_forecast_base_stock_lost_sales'
            score = replay_method(method, skus, 999, beta, trial, months=range(3, 9), bootstrapped=False)['external_avg_cost']
            if score < best_cost:
                best, best_cost = val, score
        params[key] = best
    best_pair, best_cost = (params['seasonal_multiplier'], params['backlog_weight']), 1e100
    for mult in grids['seasonal_multiplier']:
        for bw in grids['backlog_weight']:
            trial = dict(params, seasonal_multiplier=mult, backlog_weight=bw)
            score = replay_method('seasonal_service_tuned_base_stock', skus, 999, beta, trial, months=range(3, 9), bootstrapped=False)['external_avg_cost']
            if score < best_cost:
                best_pair, best_cost = (mult, bw), score
    params['seasonal_multiplier'], params['backlog_weight'] = best_pair
    return params


def mpc_order(s: SKU, inv: float, backlog: float, forecast: float, last: float, ewma: float, month: int, beta: tuple[float, float, float]) -> tuple[float, float]:
    residuals = [max(0.35, min(2.35, d)) for d in s.demands[:8]]
    scenarios = [percentile(residuals, q) for q in [0.20, 0.50, 0.80]]
    candidates = [0.0, 0.35, 0.70, 1.05, 1.40, 1.80, 2.25, 2.75, 3.25]
    best_q, best_cost = 0.0, 1e100
    for q0 in candidates:
        total = 0.0
        for r1 in scenarios:
            d1 = max(0.0, forecast * r1)
            inv1, b1, st1 = step_inventory(inv, backlog, q0, d1, s, 1.0, False)
            # Two-step recourse with a classical base-stock target, averaged over scenarios.
            future = 0.0
            ewma1 = 0.72 * ewma + 0.28 * d1
            for r2 in scenarios:
                m2 = 1 + ((month) % 12)
                f2 = max(0.05, ewma1 * seasonal_factor(beta, m2) * r2)
                q2 = max(0.0, 1.28 * f2 + b1 - inv1)
                inv2, b2, st2 = step_inventory(inv1, b1, q2, f2, s, 1.0, False)
                future += st2['external_cost'] / len(scenarios)
            total += (st1['external_cost'] + 0.82 * future) / len(scenarios)
        if total < best_cost:
            best_cost, best_q = total, q0
    return best_q, 1.0


def build_adp_policy(skus: list[SKU]):
    multipliers = [0.85, 1.00, 1.15, 1.32, 1.52, 1.75]
    # Discrete fitted value proxy: choose multiplier by SKU lead-time/margin/backlog region from train replay.
    table: dict[tuple[int, int], float] = {}
    for lead_bin in [0, 1, 2]:
        for margin_bin in [0, 1, 2]:
            subset = [s for s in skus if min(2, s.lead_time // 2) == lead_bin and min(2, int(s.margin_ratio * 3)) == margin_bin] or skus
            best_m, best_score = multipliers[0], 1e100
            for mult in multipliers:
                total = 0.0
                count = 0
                for s in subset:
                    inv = s.initial_inventory
                    backlog = s.initial_backlog
                    for month in range(3, 9):
                        forecast = sum(s.demands[max(0, month - 4):month - 1]) / max(1, len(s.demands[max(0, month - 4):month - 1]))
                        q = max(0.0, mult * forecast + 0.90 * backlog - inv)
                        inv, backlog, st = step_inventory(inv, backlog, q, s.demands[month - 1], s, 1.0, False)
                        total += st['external_cost']
                        count += 1
                score = total / max(1, count)
                if score < best_score:
                    best_m, best_score = mult, score
            table[(lead_bin, margin_bin)] = best_m

    def policy(s: SKU, inv: float, backlog: float, forecast: float, month: int) -> float:
        lead_bin = min(2, s.lead_time // 2)
        margin_bin = min(2, int(s.margin_ratio * 3))
        base = table[(lead_bin, margin_bin)]
        # Approximate marginal value correction: higher backlog and tighter capacity increase target.
        return max(0.80, min(1.90, base + 0.18 * backlog / max(0.35, forecast) + 0.08 * max(0.0, forecast / s.capacity - 1.0)))

    return policy


def build_q_policy(skus: list[SKU], seed: int = 4242):
    actions = [0.80, 1.00, 1.18, 1.38, 1.62, 1.90]
    rng = np.random.default_rng(seed)
    q_values = defaultdict(lambda: np.zeros(len(actions)))
    alpha, gamma, eps0 = 0.12, 0.88, 0.22

    def state_tuple(s: SKU, inv: float, backlog: float, forecast: float, last: float, ewma: float) -> tuple[int, int, int, int]:
        inv_bin = int(max(0, min(4, math.floor(inv))))
        backlog_bin = int(max(0, min(3, math.floor(2.0 * backlog))))
        shock_bin = 1 if last > 1.20 * max(0.25, ewma) else 0
        lead_bin = min(2, s.lead_time // 2)
        return inv_bin, backlog_bin, shock_bin, lead_bin

    for ep in range(360):
        s = skus[int(rng.integers(0, len(skus)))]
        inv = s.initial_inventory
        backlog = s.initial_backlog
        ewma = 1.0
        last = s.demands[int(rng.integers(0, 8))]
        for t in range(8):
            month = int(rng.integers(1, 9))
            forecast = max(0.05, 0.70 * ewma + 0.30 * last)
            state = state_tuple(s, inv, backlog, forecast, last, ewma)
            if rng.random() < eps0 * (1.0 - ep / 420.0):
                ai = int(rng.integers(0, len(actions)))
            else:
                ai = int(np.argmax(q_values[state]))
            q = max(0.0, actions[ai] * forecast + backlog - inv)
            residual = float(rng.choice(s.demands[:8]))
            demand = max(0.0, 0.70 * s.demands[month - 1] + 0.30 * residual)
            inv2, backlog2, st = step_inventory(inv, backlog, q, demand, s, 1.0, False)
            ewma2 = 0.72 * ewma + 0.28 * demand
            next_state = state_tuple(s, inv2, backlog2, forecast, demand, ewma2)
            reward = -st['external_cost'] + 2.0 * (st['fill'] - 0.90)
            q_values[state][ai] += alpha * (reward + gamma * float(np.max(q_values[next_state])) - q_values[state][ai])
            inv, backlog, ewma, last = inv2, backlog2, ewma2, demand

    def policy(s: SKU, inv: float, backlog: float, forecast: float, month: int, last: float, ewma: float) -> float:
        state = state_tuple(s, inv, backlog, forecast, last, ewma)
        return actions[int(np.argmax(q_values[state]))]

    return policy


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    metrics = ['external_avg_cost', 'valuation_adjusted_welfare', 'theta_free_external_welfare', 'fill_rate', 'avg_order', 'avg_ending_inventory', 'avg_ending_backlog', 'lost_sales_rate', 'capacity_excess_rate', 'theta_mean', 'theta_std', 'target_fill_mean']
    out = []
    for method in METHODS:
        rs = [r for r in rows if r['method'] == method]
        row: dict[str, object] = {'method': method, 'n_seeds': len(rs)}
        for metric in metrics:
            vals = [float(r[metric]) for r in rs]
            mean = sum(vals) / len(vals)
            ci = 1.96 * (stats.stdev(vals) / math.sqrt(len(vals)) if len(vals) > 1 else 0.0)
            row[metric] = f'{mean:.12g}'
            row[f'{metric}_ci95'] = f'{ci:.12g}'
        out.append(row)
    best_welfare = max(float(r['theta_free_external_welfare']) for r in out)
    best_cost = min(float(r['external_avg_cost']) for r in out)
    for row in out:
        row['external_welfare_gap_to_best'] = f'{best_welfare - float(row["theta_free_external_welfare"]):.12g}'
        row['external_cost_gap_to_best'] = f'{float(row["external_avg_cost"]) - best_cost:.12g}'
    return out


def write_theta_surface(skus: list[SKU]) -> None:
    # Representative SKU pressures: use median shortage/capacity attributes.
    s = sorted(skus, key=lambda z: z.shortage_weight)[len(skus) // 2]
    rows = []
    shocks = [0.0, 0.25, 0.50, 0.85]
    backlogs = [0.0, 0.35, 0.75, 1.20]
    tights = [0.0, 0.25, 0.55, 0.90]
    for shock in shocks:
        for backlog in backlogs:
            for tight in tights:
                ewma = 1.0
                last = ewma * (1.0 + shock)
                theta = theta_policy(last, ewma, backlog, tight, s)
                target_fill = max(0.86, min(0.985, 0.875 + 0.055 * theta))
                target_multiplier = 1.02 + 0.31 * theta + 0.10 * tight
                rows.append({
                    'demand_shock_ratio': f'{shock:.2f}',
                    'backlog_normalized': f'{backlog:.2f}',
                    'capacity_tightness': f'{tight:.2f}',
                    'theta_service_pressure': f'{theta:.6f}',
                    'implied_target_fill_rate': f'{target_fill:.6f}',
                    'order_target_multiplier': f'{target_multiplier:.6f}',
                    'economic_interpretation': 'theta_t is calibrated as adaptive shortage-penalty/service-pressure multiplier',
                })
    write_csv(THETA_SURFACE, rows)
    write_theta_png(rows)


def write_theta_png(rows: list[dict[str, object]]) -> None:
    # Pure-Python PNG heatmap.  The submission figure is intentionally
    # high-resolution and uses a slightly larger bitmap font so the economic
    # service-pressure interpretation remains readable after PDF scaling.
    width, height = 1200, 500
    pixels = bytearray([255, 255, 255] * width * height)

    def set_px(x: int, y: int, rgb: tuple[int, int, int]) -> None:
        if 0 <= x < width and 0 <= y < height:
            i = 3 * (y * width + x)
            pixels[i:i+3] = bytes(rgb)

    def rect(x0: int, y0: int, x1: int, y1: int, rgb: tuple[int, int, int]) -> None:
        for y in range(max(0, y0), min(height, y1)):
            for x in range(max(0, x0), min(width, x1)):
                set_px(x, y, rgb)

    def line(x0: int, y0: int, x1: int, y1: int, rgb=(0, 0, 0)) -> None:
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for k in range(steps + 1):
            x = round(x0 + (x1 - x0) * k / steps)
            y = round(y0 + (y1 - y0) * k / steps)
            set_px(x, y, rgb)

    def color(val: float) -> tuple[int, int, int]:
        z = max(0.0, min(1.0, (val - 0.75) / 1.25))
        return (int(245 - 120 * z), int(245 - 150 * z), int(255 - 35 * (1 - z)))

    # tiny 3x5 bitmap font for labels.  Include all uppercase letters used by
    # the figure title/footer to avoid silently dropping characters.
    font = {
        '0': ['111','101','101','101','111'], '1': ['010','110','010','010','111'],
        '2': ['111','001','111','100','111'], '3': ['111','001','111','001','111'],
        '4': ['101','101','111','001','001'], '5': ['111','100','111','001','111'],
        '6': ['111','100','111','101','111'], '7': ['111','001','001','001','001'],
        '8': ['111','101','111','101','111'], '9': ['111','101','111','001','111'],
        '.': ['000','000','000','000','010'], '-': ['000','000','111','000','000'],
        'T': ['111','010','010','010','010'], 'H': ['101','101','111','101','101'],
        'E': ['111','100','111','100','111'], 'A': ['010','101','111','101','101'],
        'S': ['111','100','111','001','111'], 'I': ['111','010','010','010','111'],
        'G': ['111','100','101','101','111'], 'K': ['101','110','100','110','101'],
        'B': ['110','101','110','101','110'], 'L': ['100','100','100','100','111'],
        'O': ['111','101','101','101','111'], 'C': ['111','100','100','100','111'],
        'D': ['110','101','101','101','110'], 'P': ['110','101','110','100','100'],
        'Y': ['101','101','010','010','010'], 'R': ['110','101','110','101','101'],
        'U': ['101','101','101','101','111'], 'F': ['111','100','111','100','100'],
        'N': ['101','111','111','111','101'], 'M': ['101','111','111','101','101'],
        'W': ['101','101','111','111','101'], 'V': ['101','101','101','101','010'],
        'X': ['101','101','010','101','101'],
    }

    def text(x: int, y: int, s: str, scale: int = 2, rgb=(20, 20, 20)) -> None:
        cx = x
        for ch in s.upper():
            if ch == ' ':
                cx += 4 * scale
                continue
            pat = font.get(ch)
            if not pat:
                cx += 4 * scale
                continue
            for yy, row in enumerate(pat):
                for xx, bit in enumerate(row):
                    if bit == '1':
                        rect(cx + xx*scale, y + yy*scale, cx + (xx+1)*scale, y + (yy+1)*scale, rgb)
            cx += 4 * scale

    text(38, 28, 'THETA POLICY SURFACE', 5)
    shocks = [0.0, 0.25, 0.50, 0.85]
    backlogs = [0.0, 0.35, 0.75, 1.20]
    tights = [0.0, 0.25, 0.55]
    vals = {(float(r['demand_shock_ratio']), float(r['backlog_normalized']), float(r['capacity_tightness'])): float(r['theta_service_pressure']) for r in rows}
    for pi, tight in enumerate(tights):
        x0 = 80 + pi * 360
        y0 = 125
        text(x0, y0 - 42, f'TIGHT {tight:.2f}', 3)
        cell = 72
        for i, backlog in enumerate(backlogs):
            for j, shock in enumerate(shocks):
                v = vals[(shock, backlog, tight)]
                rect(x0 + j*cell, y0 + i*cell, x0 + (j+1)*cell - 2, y0 + (i+1)*cell - 2, color(v))
        for j, shock in enumerate(shocks):
            text(x0 + j*cell + 11, y0 + len(backlogs)*cell + 14, f'{shock:.2f}', 2)
        for i, backlog in enumerate(backlogs):
            text(x0 - 58, y0 + i*cell + 27, f'{backlog:.2f}', 2)
        line(x0, y0, x0 + len(shocks)*cell, y0)
        line(x0, y0, x0, y0 + len(backlogs)*cell)
    text(75, 440, 'X SHOCK    Y BACKLOG    DARKER HIGHER THETA', 3)
    import zlib, struct
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    raw = b''.join(b'\x00' + bytes(pixels[y*width*3:(y+1)*width*3]) for y in range(height))
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b'')
    THETA_PNG.write_bytes(png)


def solve_exact_valuation_mdp() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    horizon = 8
    inv_states = list(range(-3, 8))
    regimes = [0, 1]
    theta_levels = [0.75, 1.00, 1.35, 1.70]
    order_targets = [0, 1, 2, 3, 4, 5, 6, 7]
    demand_dist = {
        0: [(0, 0.08), (1, 0.22), (2, 0.32), (3, 0.23), (4, 0.11), (5, 0.04)],
        1: [(2, 0.09), (3, 0.20), (4, 0.30), (5, 0.24), (6, 0.12), (7, 0.05)],
    }
    trans = {0: [(0, 0.84), (1, 0.16)], 1: [(0, 0.14), (1, 0.86)]}

    def clamp_inv(x: int) -> int:
        return max(min(inv_states), min(max(inv_states), x))

    def period(inv: int, regime: int, order_to: int, theta_next: float, theta_prev: float, demand: int) -> tuple[float, int, float, float, float, float]:
        q = max(0, order_to - max(inv, 0))
        pre = inv + q
        filled = min(max(pre, 0), demand + max(0, -inv))
        next_inv = clamp_inv(pre - demand)
        unmet = max(0, demand + max(0, -inv) - filled)
        fill = 1.0 if demand + max(0, -inv) <= 0 else filled / max(1, demand + max(0, -inv))
        holding = 0.22 * max(0, next_inv)
        external_shortage = 2.55 * unmet
        order_cost = 0.08 * q + 0.025 * max(0, q - 3) ** 2
        adjust = 0.09 * (theta_next - theta_prev) ** 2
        # theta_next is an economically calibrated service-pressure multiplier.
        target_fill = max(0.86, min(0.985, 0.875 + 0.055 * theta_next))
        service_penalty = (1.05 + 1.35 * theta_next) * max(0.0, target_fill - fill) ** 2
        # Calibrated valuation benefit: theta_t is a service-pressure / backlog-aversion
        # level, not a free scoring knob.  High theta is beneficial only when the
        # policy actually delivers service, and it is offset by a convex adjustment
        # and level cost.  The checker also reports theta-free external cost.
        valuation_benefit = 0.95 * theta_next * fill - 0.38 * theta_next * theta_next
        welfare = -(holding + external_shortage + order_cost + adjust + service_penalty) + valuation_benefit
        external_cost = holding + external_shortage + order_cost
        return welfare, next_inv, external_cost, filled, demand, unmet

    methods = {
        'exact_dp_action_only_fixed_theta': [(o, 1.00) for o in order_targets],
        'exact_dp_dynamic_shortage_penalty_only': [(3, th) for th in theta_levels],
        'exact_dp_full_order_and_valuation_control': [(o, th) for o in order_targets for th in theta_levels],
    }
    metric_rows = []
    policy_rows = []
    for method, actions in methods.items():
        @lru_cache(None)
        def value(t: int, inv: int, regime: int, theta_i: int) -> tuple[float, tuple[int, float] | None]:
            theta_prev = theta_levels[theta_i]
            if t == horizon:
                return 0.0, None
            best = -1e100
            best_action = None
            for order_to, theta_next in actions:
                theta_next_i = min(range(len(theta_levels)), key=lambda k: abs(theta_levels[k] - theta_next))
                total = 0.0
                for d, pd in demand_dist[regime]:
                    w, inv2, *_ = period(inv, regime, order_to, theta_next, theta_prev, d)
                    for reg2, pr in trans[regime]:
                        cont, _ = value(t + 1, inv2, reg2, theta_next_i)
                        total += pd * pr * (w + cont)
                if total > best:
                    best = total
                    best_action = (order_to, theta_next)
            return best, best_action

        dist = {(2, 0, 1): 0.5, (2, 1, 1): 0.5}
        tw = tc = filled = dem = unmet = theta_sum = 0.0
        for t in range(horizon):
            next_dist = defaultdict(float)
            for (inv, reg, thi), mass in dist.items():
                _, act = value(t, inv, reg, thi)
                assert act is not None
                order_to, theta_next = act
                policy_rows.append({'method': method, 't': t, 'inventory': inv, 'regime': reg, 'theta_previous': theta_levels[thi], 'order_up_to': order_to, 'theta_next': theta_next})
                theta_next_i = min(range(len(theta_levels)), key=lambda k: abs(theta_levels[k] - theta_next))
                for d, pd in demand_dist[reg]:
                    w, inv2, c, f, dd, un = period(inv, reg, order_to, theta_next, theta_levels[thi], d)
                    for reg2, pr in trans[reg]:
                        p = mass * pd * pr
                        next_dist[(inv2, reg2, theta_next_i)] += p
                        tw += p * w
                        tc += p * c
                        filled += p * f
                        dem += p * dd
                        unmet += p * un
                        theta_sum += p * theta_next
            dist = dict(next_dist)
        metric_rows.append({
            'method': method,
            'horizon': horizon,
            'state_count': len(inv_states) * len(regimes) * len(theta_levels),
            'action_count': len(actions),
            'expected_total_welfare': f'{tw:.12g}',
            'expected_avg_welfare': f'{tw / horizon:.12g}',
            'theta_free_expected_total_cost': f'{tc:.12g}',
            'theta_free_expected_avg_cost': f'{tc / horizon:.12g}',
            'fill_rate': f'{filled / max(1e-12, dem):.12g}',
            'expected_unmet_demand': f'{unmet:.12g}',
            'expected_theta': f'{theta_sum / horizon:.12g}',
        })
    return metric_rows, policy_rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    global DATA, PANEL, SEED_METRICS, METRICS, THETA_SURFACE, DP_METRICS, DP_POLICY
    parser = argparse.ArgumentParser()
    parser.add_argument('--outdir', default=str(ROOT / 'data'))
    args = parser.parse_args()
    DATA = Path(args.outdir).resolve()
    PANEL = DATA / 'sku_monthly_demand_panel.csv'
    SEED_METRICS = DATA / 'sku_inventory_baseline_seed_metrics.csv'
    METRICS = DATA / 'sku_inventory_baseline_metrics.csv'
    THETA_SURFACE = DATA / 'sku_theta_policy_surface.csv'
    DP_METRICS = DATA / 'inventory_exact_valuation_control_mdp_metrics.csv'
    DP_POLICY = DATA / 'inventory_exact_valuation_control_mdp_policy.csv'

    skus = load_skus()
    write_panel(skus)
    beta = fit_global_seasonality(skus)
    params = calibrate_base_stock(skus, beta)
    adp_policy = build_adp_policy(skus)
    q_policy = build_q_policy(skus)

    rows = []
    for seed in SEEDS:
        for method in METHODS:
            metrics = replay_method(method, skus, seed, beta, params, adp_policy, q_policy)
            row: dict[str, object] = {
                'method': method,
                'seed': seed,
                'sku_count': len(skus),
                'test_months': len(TEST_MONTHS),
                'training_months_per_sku': len(TRAIN_MONTHS),
                'source_dataset': 'supplychainpy sample complete_dataset_small.csv',
                'split': 'months_1_8_train_9_12_test',
            }
            row.update({k: f'{v:.12g}' if isinstance(v, float) else v for k, v in metrics.items()})
            rows.append(row)
    write_csv(SEED_METRICS, rows)
    write_csv(METRICS, summarize(rows))
    write_theta_surface(skus)
    dp_metrics, dp_policy = solve_exact_valuation_mdp()
    write_csv(DP_METRICS, dp_metrics)
    write_csv(DP_POLICY, dp_policy)
    for row in summarize(rows):
        print(row)
    for row in dp_metrics:
        print(row)


if __name__ == '__main__':
    main()
