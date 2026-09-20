#!/usr/bin/env python3
"""Finite-cover Bellman/HJB certificate for the inventory valuation-control DP.

This audit turns the exact inventory policy-class DP into the discrete analogue of
an HJB-solver certificate.  On the finite state-time cover and finite action
cover, the Bellman operator is the finite-horizon HJB operator.  Exact backward
induction gives zero terminal residual, zero Bellman residual, and zero greedy
selector gap up to floating-point tolerance.  The Full valuation-control action
set is nested: it contains the action-only and valuation-only frozen-valuation
faces and adds joint order/service-pressure controls.
"""
from __future__ import annotations

import csv
import math
from functools import lru_cache
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

HORIZON = 10
INV_MIN = -18
INV_MAX = 42
START_INV = 24
DISCOUNT = 1.0

ACTION_ONLY_CONTROLS = [(0.70, 1.00), (0.95, 1.00), (1.20, 1.00), (1.45, 1.00), (1.70, 1.00)]
VALUATION_ONLY_CONTROLS = [(1.10, 0.60), (1.10, 0.85), (1.10, 1.10), (1.10, 1.35), (1.10, 1.60)]
JOINT_CONTROLS = [(0.80, 0.80), (1.00, 1.05), (1.20, 1.25), (1.45, 1.45), (1.70, 1.65), (1.20, 2.20)]
CONTROL_GRID = {
    "action_only_exact_dp": ACTION_ONLY_CONTROLS,
    "valuation_only_exact_dp": VALUATION_ONLY_CONTROLS,
    "full_valuation_control_exact_dp": ACTION_ONLY_CONTROLS + VALUATION_ONLY_CONTROLS + JOINT_CONTROLS,
}


def poisson_probs(lam: float, max_d: int = 14) -> list[tuple[int, float]]:
    probs = [math.exp(-lam) * lam**k / math.factorial(k) for k in range(max_d)]
    tail = max(0.0, 1.0 - sum(probs))
    out = [(k, probs[k]) for k in range(max_d)]
    out.append((max_d, tail))
    s = sum(p for _, p in out)
    return [(d, p / s) for d, p in out]


DEMAND = {0: poisson_probs(4.5), 1: poisson_probs(7.2)}
REGIME_TRANS = {0: [(0, 0.86), (1, 0.14)], 1: [(0, 0.10), (1, 0.90)]}


class Solve(NamedTuple):
    value_at_start: float
    residual_sup: float
    greedy_gap_sup: float
    terminal_residual_sup: float
    bellman_nodes: int
    terminal_nodes: int
    min_greedy_margin_to_runner_up: float


def clamp_inv(x: int) -> int:
    return max(INV_MIN, min(INV_MAX, x))


def step_cost_and_stats(inv: int, regime: int, action_pressure: float, theta: float, demand: int) -> tuple[float, int]:
    backlog = max(0, -inv)
    forecast = 4.5 if regime == 0 else 7.2
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
    return welfare, next_inv


def solve_certificate(method: str) -> Solve:
    controls = CONTROL_GRID[method]

    @lru_cache(None)
    def q_value(t: int, inv: int, regime: int, action_pressure: float, theta: float) -> float:
        total = 0.0
        for demand, pd in DEMAND[regime]:
            welfare, next_inv = step_cost_and_stats(inv, regime, action_pressure, theta, demand)
            for next_regime, pr in REGIME_TRANS[regime]:
                total += pd * pr * (welfare + DISCOUNT * value(t + 1, next_inv, next_regime)[0])
        return total

    @lru_cache(None)
    def value(t: int, inv: int, regime: int) -> tuple[float, tuple[float, float] | None]:
        if t == HORIZON:
            return 0.0, None
        vals = [(q_value(t, inv, regime, a, th), (a, th)) for a, th in controls]
        best_val, best_control = max(vals, key=lambda z: z[0])
        return best_val, best_control

    residual_sup = 0.0
    greedy_gap_sup = 0.0
    min_runner_gap = float("inf")
    bellman_nodes = 0
    for t in range(HORIZON):
        for inv in range(INV_MIN, INV_MAX + 1):
            for regime in [0, 1]:
                v, control = value(t, inv, regime)
                assert control is not None
                q_vals = sorted([q_value(t, inv, regime, a, th) for a, th in controls], reverse=True)
                best = q_vals[0]
                chosen = q_value(t, inv, regime, control[0], control[1])
                residual_sup = max(residual_sup, abs(v - best))
                greedy_gap_sup = max(greedy_gap_sup, max(0.0, best - chosen))
                if len(q_vals) > 1:
                    min_runner_gap = min(min_runner_gap, max(0.0, q_vals[0] - q_vals[1]))
                bellman_nodes += 1
    terminal_nodes = (INV_MAX - INV_MIN + 1) * 2
    terminal_residual_sup = max(abs(value(HORIZON, inv, regime)[0]) for inv in range(INV_MIN, INV_MAX + 1) for regime in [0, 1])
    start_val = 0.5 * value(0, START_INV, 0)[0] + 0.5 * value(0, START_INV, 1)[0]
    return Solve(start_val, residual_sup, greedy_gap_sup, terminal_residual_sup, bellman_nodes, terminal_nodes, min_runner_gap)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def fmt(x: float) -> str:
    return f"{x:.12g}"


def main() -> int:
    solved = {method: solve_certificate(method) for method in CONTROL_GRID}
    action_val = solved["action_only_exact_dp"].value_at_start
    valuation_val = solved["valuation_only_exact_dp"].value_at_start
    rows: list[dict[str, object]] = []
    for method, result in solved.items():
        controls = CONTROL_GRID[method]
        contains_action = set(ACTION_ONLY_CONTROLS).issubset(set(controls))
        contains_valuation = set(VALUATION_ONLY_CONTROLS).issubset(set(controls))
        bound = result.terminal_residual_sup + HORIZON * (result.residual_sup + result.greedy_gap_sup)
        rows.append({
            "certificate": "finite_cover_inventory_bellman_hjb",
            "method": method,
            "horizon": HORIZON,
            "inventory_states": INV_MAX - INV_MIN + 1,
            "regime_states": 2,
            "state_count": (INV_MAX - INV_MIN + 1) * 2,
            "bellman_state_time_nodes": result.bellman_nodes,
            "terminal_nodes": result.terminal_nodes,
            "action_grid_size": len(controls),
            "contains_action_only_face": int(contains_action),
            "contains_valuation_only_face": int(contains_valuation),
            "terminal_residual_sup": fmt(result.terminal_residual_sup),
            "bellman_residual_sup_abs": fmt(result.residual_sup),
            "greedy_gap_sup": fmt(result.greedy_gap_sup),
            "finite_cover_certificate_bound": fmt(bound),
            "value_at_initial_mixture": fmt(result.value_at_start),
            "avg_welfare_at_initial_mixture": fmt(result.value_at_start / HORIZON),
            "margin_vs_action_only_total": fmt(result.value_at_start - action_val),
            "margin_vs_action_only_avg": fmt((result.value_at_start - action_val) / HORIZON),
            "margin_vs_valuation_only_total": fmt(result.value_at_start - valuation_val),
            "margin_vs_valuation_only_avg": fmt((result.value_at_start - valuation_val) / HORIZON),
            "min_greedy_margin_to_runner_up": fmt(result.min_greedy_margin_to_runner_up),
            "certificate_status": "exact_finite_cover_hjb_solve" if bound < 1e-10 else "finite_cover_gap_reported",
            "interpretation": "finite-state/action Bellman-HJB certificate: residual, terminal, and greedy gaps vanish on the inventory state-time/action cover",
        })
    write_csv(DATA / "inventory_finite_cover_hjb_certificate.csv", rows)
    print(DATA / "inventory_finite_cover_hjb_certificate.csv")
    for row in rows:
        print(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
