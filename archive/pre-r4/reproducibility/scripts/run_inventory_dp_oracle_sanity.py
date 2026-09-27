#!/usr/bin/env python3
"""Exact dynamic-programming inventory oracle sanity check.

This script solves a small finite-horizon single-item lost-sales inventory model
by exact backward induction and compares it with the best stationary base-stock
policy and simple reference rules. It is intentionally dependency-free.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

HORIZON = 12
MAX_STOCK = 32
MAX_DEMAND = 34
INIT_INVENTORY = 8
DEMAND_LAMBDA = 9.5
HOLDING_COST = 0.42
SHORTAGE_COST = 4.80
UNIT_ORDER_COST = 0.06


def poisson_pmf(lam: float, max_demand: int) -> list[float]:
    probs = []
    p = math.exp(-lam)
    probs.append(p)
    for k in range(1, max_demand + 1):
        p = p * lam / k
        probs.append(p)
    s = sum(probs)
    probs[-1] += 1.0 - s  # truncate tail into final bucket
    return probs


DEMAND_PROBS = poisson_pmf(DEMAND_LAMBDA, MAX_DEMAND)
EXPECTED_DEMAND_PER_PERIOD = sum(k * p for k, p in enumerate(DEMAND_PROBS))


def one_step(order_up_to: int, demand: int) -> tuple[int, int, int]:
    ending_inventory = max(order_up_to - demand, 0)
    lost_sales = max(demand - order_up_to, 0)
    filled = demand - lost_sales
    return ending_inventory, lost_sales, filled


def immediate_cost(start_inventory: int, order_up_to: int, demand: int) -> float:
    q = max(order_up_to - start_inventory, 0)
    ending, lost, _ = one_step(order_up_to, demand)
    return UNIT_ORDER_COST * q + HOLDING_COST * ending + SHORTAGE_COST * lost


def solve_exact_dp() -> tuple[list[list[float]], list[list[int]]]:
    value = [[0.0 for _ in range(MAX_STOCK + 1)] for _ in range(HORIZON + 1)]
    policy = [[0 for _ in range(MAX_STOCK + 1)] for _ in range(HORIZON)]
    for t in range(HORIZON - 1, -1, -1):
        for inv in range(MAX_STOCK + 1):
            best_cost = float('inf')
            best_s = inv
            for s in range(inv, MAX_STOCK + 1):
                exp_cost = 0.0
                for d, prob in enumerate(DEMAND_PROBS):
                    ending, _, _ = one_step(s, d)
                    exp_cost += prob * (immediate_cost(inv, s, d) + value[t + 1][ending])
                if exp_cost < best_cost - 1e-12:
                    best_cost = exp_cost
                    best_s = s
            value[t][inv] = best_cost
            policy[t][inv] = best_s
    return value, policy


def evaluate_policy(policy_fn) -> dict[str, float]:
    # Forward dynamic evaluation over the exact inventory-state distribution.
    dist = {INIT_INVENTORY: 1.0}
    total_cost = 0.0
    total_lost = 0.0
    total_filled = 0.0
    total_demand = 0.0
    total_order = 0.0
    total_holding = 0.0
    policy_sum = 0.0
    policy_mass = 0.0
    for t in range(HORIZON):
        next_dist: dict[int, float] = {}
        for inv, mass in dist.items():
            s = int(policy_fn(t, inv))
            s = max(inv, min(MAX_STOCK, s))
            q = max(s - inv, 0)
            policy_sum += mass * s
            policy_mass += mass
            for d, prob in enumerate(DEMAND_PROBS):
                p = mass * prob
                ending, lost, filled = one_step(s, d)
                cost = immediate_cost(inv, s, d)
                next_dist[ending] = next_dist.get(ending, 0.0) + p
                total_cost += p * cost
                total_lost += p * lost
                total_filled += p * filled
                total_demand += p * d
                total_order += p * q
                total_holding += p * ending
        dist = next_dist
    fill_rate = total_filled / max(total_demand, 1e-12)
    return {
        'expected_total_cost': total_cost,
        'expected_avg_cost': total_cost / HORIZON,
        'expected_lost_sales': total_lost,
        'fill_rate': fill_rate,
        'expected_order_qty': total_order / HORIZON,
        'expected_ending_inventory': sum(inv * mass for inv, mass in dist.items()),
        'expected_holding_inventory': total_holding / HORIZON,
        'mean_order_up_to': policy_sum / max(policy_mass, 1e-12),
    }


def best_stationary_base_stock() -> tuple[int, dict[str, float]]:
    best_s = 0
    best = None
    for s in range(MAX_STOCK + 1):
        metrics = evaluate_policy(lambda _t, inv, s=s: max(inv, s))
        if best is None or metrics['expected_total_cost'] < best['expected_total_cost']:
            best_s = s
            best = metrics
    assert best is not None
    return best_s, best


def myopic_newsvendor_level() -> int:
    critical = SHORTAGE_COST / (SHORTAGE_COST + HOLDING_COST)
    cdf = 0.0
    for d, p in enumerate(DEMAND_PROBS):
        cdf += p
        if cdf >= critical:
            return d
    return MAX_DEMAND


def main() -> None:
    outdir = Path(__file__).resolve().parents[1] / 'data'
    outdir.mkdir(parents=True, exist_ok=True)
    value, policy = solve_exact_dp()
    exact = evaluate_policy(lambda t, inv: policy[t][inv])
    best_s, best_base = best_stationary_base_stock()
    news_s = myopic_newsvendor_level()
    news = evaluate_policy(lambda _t, inv: max(inv, news_s))
    no_reorder = evaluate_policy(lambda _t, inv: inv)

    rows = []
    for name, s, metrics in [
        ('exact_dynamic_programming_oracle', 'state_time_dependent', exact),
        ('best_stationary_base_stock', str(best_s), best_base),
        ('myopic_newsvendor_base_stock', str(news_s), news),
        ('no_reorder', 'none', no_reorder),
    ]:
        row = {
            'method': name,
            'order_up_to_rule': s,
            'horizon': HORIZON,
            'initial_inventory': INIT_INVENTORY,
            'demand_lambda': DEMAND_LAMBDA,
            'holding_cost': HOLDING_COST,
            'shortage_cost': SHORTAGE_COST,
            'unit_order_cost': UNIT_ORDER_COST,
        }
        row.update({k: f'{v:.12g}' for k, v in metrics.items()})
        rows.append(row)
    with (outdir / 'inventory_dp_oracle_metrics.csv').open('w', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    policy_rows = []
    for t in range(HORIZON):
        for inv in range(MAX_STOCK + 1):
            policy_rows.append({'period': t, 'inventory': inv, 'optimal_order_up_to': policy[t][inv]})
    with (outdir / 'inventory_dp_oracle_policy.csv').open('w', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=['period', 'inventory', 'optimal_order_up_to'])
        writer.writeheader()
        writer.writerows(policy_rows)

    print(outdir / 'inventory_dp_oracle_metrics.csv')
    print(rows)


if __name__ == '__main__':
    main()
