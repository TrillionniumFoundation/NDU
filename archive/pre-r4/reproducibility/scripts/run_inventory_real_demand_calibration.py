#!/usr/bin/env python3
"""Real-demand calibration bridge for the NDU OR inventory sanity check.

The script uses the public R `datasets::AirPassengers` monthly demand trace
(available through Rdatasets) as a compact external demand series. It scales the
passenger-count trace to the demand scale used by the inventory sanity check,
calibrates simple policies on the first 108 months, and reports replay metrics
on the final 36 months. This is intentionally a calibration bridge, not a new
claim of external industrial validation.
"""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from urllib.request import urlopen

SOURCE_URL = 'https://raw.githubusercontent.com/vincentarelbundock/Rdatasets/master/csv/datasets/AirPassengers.csv'
DATA_DIR = Path(__file__).resolve().parents[1] / 'data'
TRACE_PATH = DATA_DIR / 'airpassengers_monthly_demand_trace.csv'
METRICS_PATH = DATA_DIR / 'inventory_real_demand_calibration_metrics.csv'
REPLAY_PATH = DATA_DIR / 'inventory_real_demand_replay.csv'
SCALE = 20.0
TRAIN_MONTHS = 108

METHODS = [
    'adaptive_valuation_service_replay',
    'seasonal_quantile_base_stock',
    'fixed_empirical_base_stock',
    'no_reorder',
]


def percentile(values: list[float], q: float) -> float:
    xs = sorted(values)
    if not xs:
        return 0.0
    pos = (len(xs) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    return xs[lo] * (hi - pos) + xs[hi] * (pos - lo)


def fetch_source() -> str:
    with urlopen(SOURCE_URL, timeout=30) as response:
        return response.read().decode('utf-8')


def write_trace_from_source(text: str) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    source_rows = list(csv.DictReader(text.splitlines()))
    with TRACE_PATH.open('w', newline='') as fh:
        fieldnames = ['month_index', 'year', 'month', 'raw_passengers', 'scaled_demand', 'split', 'source']
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for j, row in enumerate(source_rows, start=1):
            time = float(row['time'])
            year = int(math.floor(time + 1e-9))
            month = ((j - 1) % 12) + 1
            raw = float(row['value'])
            scaled = raw / SCALE
            writer.writerow({
                'month_index': j,
                'year': year,
                'month': month,
                'raw_passengers': f'{raw:.0f}',
                'scaled_demand': f'{scaled:.6f}',
                'split': 'train' if j <= TRAIN_MONTHS else 'test',
                'source': 'R datasets::AirPassengers via Rdatasets',
            })


def load_trace() -> list[dict[str, float | int | str]]:
    if not TRACE_PATH.exists():
        write_trace_from_source(fetch_source())
    rows = []
    with TRACE_PATH.open(newline='') as fh:
        for row in csv.DictReader(fh):
            rows.append({
                'month_index': int(row['month_index']),
                'year': int(row['year']),
                'month': int(row['month']),
                'raw_passengers': float(row['raw_passengers']),
                'scaled_demand': float(row['scaled_demand']),
                'split': row['split'],
            })
    return rows


def costs(q: float, inventory: float, backlog: float, theta: float) -> float:
    holding = 0.28 * inventory
    shortage = 2.85 * backlog
    order = 0.055 * q + 0.010 * max(0.0, q - 35.0) ** 2 / 35.0
    theta_cost = 0.045 * (theta - 1.0) ** 2
    return holding + shortage + order + theta_cost


def replay(rows: list[dict[str, float | int | str]], method: str, params: dict[str, float], seasonal_targets: dict[int, float]) -> tuple[dict[str, float], list[dict[str, str]]]:
    inventory = params.get('initial_inventory', 22.0)
    backlog = 0.0
    ewma = params.get('initial_ewma', 22.0)
    last_demand = ewma
    total_cost = total_demand = total_filled = total_order = 0.0
    total_inventory = service_breaches = 0.0
    replay_rows: list[dict[str, str]] = []

    for t, row in enumerate(rows, start=1):
        demand = float(row['scaled_demand'])
        month = int(row['month'])
        shock = max(0.0, last_demand - ewma)
        theta = 1.0
        if method == 'adaptive_valuation_service_replay':
            seasonal_target = seasonal_targets.get(month, params['global_target'])
            theta = max(0.55, min(2.20, params['theta_base'] + params['shock_gain'] * shock / max(params['train_mean'], 1.0)))
            target = ((1.0 - params['season_blend']) * ewma + params['season_blend'] * seasonal_target) * (1.0 + params['service_pressure'] * theta) + params['backlog_gain'] * backlog
        elif method == 'seasonal_quantile_base_stock':
            target = seasonal_targets.get(month, params['global_target']) + backlog
        elif method == 'fixed_empirical_base_stock':
            target = params['base_stock'] + backlog
        elif method == 'no_reorder':
            target = 0.0
        else:
            raise ValueError(method)

        q = max(0.0, target - inventory)
        inventory += q
        need = backlog + demand
        filled = min(inventory, need)
        inventory -= filled
        backlog = need - filled
        fill_t = 1.0 if need <= 1e-12 else filled / need
        service_breach = 1.0 if fill_t < 0.92 else 0.0
        cost = costs(q, inventory, backlog, theta)

        total_cost += cost
        total_demand += demand
        total_filled += filled
        total_order += q
        total_inventory += inventory
        service_breaches += service_breach
        ewma = params['ewma_alpha'] * demand + (1.0 - params['ewma_alpha']) * ewma
        last_demand = demand
        welfare_t = -cost + 8.0 * (fill_t - 0.92) - 0.03 * service_breach
        replay_rows.append({
            'method': method,
            'month_index': str(row['month_index']),
            'year': str(row['year']),
            'month': str(month),
            'scaled_demand': f'{demand:.6f}',
            'order_quantity': f'{q:.6f}',
            'theta': f'{theta:.6f}',
            'ending_inventory': f'{inventory:.6f}',
            'ending_backlog': f'{backlog:.6f}',
            'fill_rate': f'{fill_t:.6f}',
            'period_cost': f'{cost:.6f}',
            'period_welfare': f'{welfare_t:.6f}',
        })

    n = max(1, len(rows))
    fill_rate = total_filled / max(total_demand, 1e-12)
    avg_cost = total_cost / n
    mean_welfare = -avg_cost + 8.0 * (fill_rate - 0.92) - 0.03 * service_breaches / n
    return {
        'months': float(n),
        'total_cost': total_cost,
        'avg_cost': avg_cost,
        'fill_rate': fill_rate,
        'ending_backlog': backlog,
        'avg_inventory': total_inventory / n,
        'avg_order': total_order / n,
        'service_breaches': service_breaches,
        'mean_welfare': mean_welfare,
    }, replay_rows


def calibrate(train: list[dict[str, float | int | str]]) -> tuple[dict[str, dict[str, float]], dict[int, float]]:
    demands = [float(r['scaled_demand']) for r in train]
    train_mean = sum(demands) / len(demands)
    global_target = percentile(demands, 0.90)
    seasonal_targets = {}
    for month in range(1, 13):
        month_demands = [float(r['scaled_demand']) for r in train if int(r['month']) == month]
        seasonal_targets[month] = percentile(month_demands, 0.90)

    common = {
        'initial_inventory': train_mean,
        'initial_ewma': train_mean,
        'train_mean': train_mean,
        'global_target': global_target,
        'ewma_alpha': 0.24,
    }

    best_fixed = None
    best_score = float('inf')
    for base_stock in [x * 0.5 for x in range(10, 121)]:
        p = dict(common, base_stock=base_stock)
        score = replay(train, 'fixed_empirical_base_stock', p, seasonal_targets)[0]['avg_cost']
        if score < best_score:
            best_score = score
            best_fixed = base_stock

    grid = {
        'theta_base': [0.75, 0.95, 1.15],
        'shock_gain': [0.25, 0.55, 0.85],
        'service_pressure': [0.12, 0.22, 0.32],
        'backlog_gain': [0.45, 0.75, 1.05],
        'season_blend': [0.25, 0.50, 0.75],
        'ewma_alpha': [0.18, 0.28, 0.38],
    }
    best_adaptive = None
    best_adaptive_score = float('inf')
    for theta_base in grid['theta_base']:
        for shock_gain in grid['shock_gain']:
            for service_pressure in grid['service_pressure']:
                for backlog_gain in grid['backlog_gain']:
                    for season_blend in grid['season_blend']:
                        for ewma_alpha in grid['ewma_alpha']:
                            p = dict(common, theta_base=theta_base, shock_gain=shock_gain, service_pressure=service_pressure, backlog_gain=backlog_gain, season_blend=season_blend, ewma_alpha=ewma_alpha)
                            score = replay(train, 'adaptive_valuation_service_replay', p, seasonal_targets)[0]['avg_cost']
                            if score < best_adaptive_score:
                                best_adaptive_score = score
                                best_adaptive = p

    params = {
        'fixed_empirical_base_stock': dict(common, base_stock=float(best_fixed)),
        'seasonal_quantile_base_stock': dict(common),
        'adaptive_valuation_service_replay': dict(best_adaptive),
        'no_reorder': dict(common),
    }
    return params, seasonal_targets


def write_outputs(refresh_source: bool = False) -> None:
    if refresh_source or not TRACE_PATH.exists():
        write_trace_from_source(fetch_source())
    trace = load_trace()
    train = [r for r in trace if r['split'] == 'train']
    test = [r for r in trace if r['split'] == 'test']
    params, seasonal_targets = calibrate(train)

    metrics_rows = []
    all_replay_rows: list[dict[str, str]] = []
    for method in METHODS:
        train_metrics, _ = replay(train, method, params[method], seasonal_targets)
        test_metrics, method_replay = replay(test, method, params[method], seasonal_targets)
        row = {'method': method, 'train_months': str(len(train)), 'test_months': str(len(test))}
        for prefix, metrics in [('train', train_metrics), ('test', test_metrics)]:
            for key in ['avg_cost', 'fill_rate', 'ending_backlog', 'avg_inventory', 'avg_order', 'service_breaches', 'mean_welfare', 'total_cost']:
                row[f'{prefix}_{key}'] = f'{metrics[key]:.10f}'
        row['source_dataset'] = 'R datasets::AirPassengers via Rdatasets'
        row['source_url'] = SOURCE_URL
        if method == 'adaptive_valuation_service_replay':
            for key in ['theta_base', 'shock_gain', 'service_pressure', 'backlog_gain', 'season_blend', 'ewma_alpha']:
                row[f'calibrated_{key}'] = f'{params[method][key]:.6f}'
        elif method == 'fixed_empirical_base_stock':
            row['calibrated_base_stock'] = f'{params[method]["base_stock"]:.6f}'
        metrics_rows.append(row)
        all_replay_rows.extend(method_replay)

    with METRICS_PATH.open('w', newline='') as fh:
        fieldnames = sorted({k for row in metrics_rows for k in row})
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metrics_rows)
    with REPLAY_PATH.open('w', newline='') as fh:
        fieldnames = ['method', 'month_index', 'year', 'month', 'scaled_demand', 'order_quantity', 'theta', 'ending_inventory', 'ending_backlog', 'fill_rate', 'period_cost', 'period_welfare']
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_replay_rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--refresh-source', action='store_true', help='download the source AirPassengers CSV from Rdatasets before regenerating outputs')
    args = parser.parse_args()
    write_outputs(refresh_source=args.refresh_source)
    print(f'wrote {TRACE_PATH}')
    print(f'wrote {METRICS_PATH}')
    print(f'wrote {REPLAY_PATH}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
