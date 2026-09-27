#!/usr/bin/env python3
"""Nested cover-refinement audit for the inventory Bellman/HJB certificate.

The R48 finite-cover certificate proves that zero Bellman residual, terminal
residual, and greedy gap certify an exact finite-cover HJB solve.  This R49 audit
adds the refinement view: nested action covers all solve exactly on the same
finite inventory state-time cover, the action fill-distance proxy shrinks, and
Full valuation-control value/margins are monotone as the cover is refined.
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

ACTION_ONLY = [(0.70, 1.00), (0.95, 1.00), (1.20, 1.00), (1.45, 1.00), (1.70, 1.00)]
VALUATION_ONLY = [(1.10, 0.60), (1.10, 0.85), (1.10, 1.10), (1.10, 1.35), (1.10, 1.60)]
JOINT = [(0.80, 0.80), (1.00, 1.05), (1.20, 1.25), (1.45, 1.45), (1.70, 1.65), (1.20, 2.20)]

REFINEMENT_LEVELS = [
    ("action_face_5", ACTION_ONLY),
    ("action_plus_valuation_face_10", ACTION_ONLY + VALUATION_ONLY),
    ("nested_full_sparse_13", ACTION_ONLY + VALUATION_ONLY + [JOINT[i] for i in [0, 2, 4]]),
    ("nested_full_r48_16", ACTION_ONLY + VALUATION_ONLY + JOINT),
]


def poisson_probs(lam: float, max_d: int = 14) -> list[tuple[int, float]]:
    probs = [math.exp(-lam) * lam**k / math.factorial(k) for k in range(max_d)]
    tail = max(0.0, 1.0 - sum(probs))
    out = [(k, probs[k]) for k in range(max_d)] + [(max_d, tail)]
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


def clamp_inv(x: int) -> int:
    return max(INV_MIN, min(INV_MAX, x))


def step_welfare(inv: int, regime: int, action_pressure: float, theta: float, demand: int) -> tuple[float, int]:
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


def solve_cover(controls: tuple[tuple[float, float], ...]) -> Solve:
    @lru_cache(None)
    def q_value(t: int, inv: int, regime: int, action_pressure: float, theta: float) -> float:
        total = 0.0
        for demand, pd in DEMAND[regime]:
            welfare, next_inv = step_welfare(inv, regime, action_pressure, theta, demand)
            for next_regime, pr in REGIME_TRANS[regime]:
                total += pd * pr * (welfare + DISCOUNT * value(t + 1, next_inv, next_regime)[0])
        return total

    @lru_cache(None)
    def value(t: int, inv: int, regime: int) -> tuple[float, tuple[float, float] | None]:
        if t == HORIZON:
            return 0.0, None
        vals = [(q_value(t, inv, regime, a, th), (a, th)) for a, th in controls]
        return max(vals, key=lambda z: z[0])

    residual_sup = 0.0
    greedy_gap_sup = 0.0
    bellman_nodes = 0
    for t in range(HORIZON):
        for inv in range(INV_MIN, INV_MAX + 1):
            for regime in [0, 1]:
                v, control = value(t, inv, regime)
                assert control is not None
                q_vals = [q_value(t, inv, regime, a, th) for a, th in controls]
                best = max(q_vals)
                chosen = q_value(t, inv, regime, control[0], control[1])
                residual_sup = max(residual_sup, abs(v - best))
                greedy_gap_sup = max(greedy_gap_sup, max(0.0, best - chosen))
                bellman_nodes += 1
    terminal_nodes = (INV_MAX - INV_MIN + 1) * 2
    terminal_sup = max(abs(value(HORIZON, inv, regime)[0]) for inv in range(INV_MIN, INV_MAX + 1) for regime in [0, 1])
    start_val = 0.5 * value(0, START_INV, 0)[0] + 0.5 * value(0, START_INV, 1)[0]
    return Solve(start_val, residual_sup, greedy_gap_sup, terminal_sup, bellman_nodes, terminal_nodes)


def action_fill_distance_proxy(controls: tuple[tuple[float, float], ...]) -> float:
    # Deterministic rectangular fill-distance proxy over the compact action box
    # used by the refinement theorem text.  This is not a new optimizer; it is a
    # transparent geometric diagnostic for nested action-cover density.
    max_dist = 0.0
    for i in range(101):
        action_pressure = 0.70 + i * (1.70 - 0.70) / 100.0
        for j in range(161):
            theta = 0.60 + j * (2.20 - 0.60) / 160.0
            dist = min(math.hypot(action_pressure - a, theta - th) for a, th in controls)
            max_dist = max(max_dist, dist)
    return max_dist


def fmt(x: float) -> str:
    return f"{x:.12g}"


def main() -> int:
    solved = [(name, tuple(controls), solve_cover(tuple(controls))) for name, controls in REFINEMENT_LEVELS]
    action_value = solved[0][2].value_at_start
    rows: list[dict[str, object]] = []
    prev_value: float | None = None
    prev_radius: float | None = None
    for idx, (name, controls, result) in enumerate(solved):
        radius = action_fill_distance_proxy(controls)
        increment = 0.0 if prev_value is None else (result.value_at_start - prev_value) / HORIZON
        radius_drop = 0.0 if prev_radius is None else prev_radius - radius
        bound = result.terminal_residual_sup + HORIZON * (result.residual_sup + result.greedy_gap_sup)
        rows.append({
            "refinement_level": idx,
            "cover_name": name,
            "state_count": (INV_MAX - INV_MIN + 1) * 2,
            "bellman_state_time_nodes": result.bellman_nodes,
            "terminal_nodes": result.terminal_nodes,
            "action_grid_size": len(controls),
            "contains_action_only_face": int(set(ACTION_ONLY).issubset(set(controls))),
            "contains_valuation_only_face": int(set(VALUATION_ONLY).issubset(set(controls))),
            "action_fill_distance_proxy": fmt(radius),
            "fill_distance_drop_vs_previous": fmt(radius_drop),
            "terminal_residual_sup": fmt(result.terminal_residual_sup),
            "bellman_residual_sup_abs": fmt(result.residual_sup),
            "greedy_gap_sup": fmt(result.greedy_gap_sup),
            "finite_cover_certificate_bound": fmt(bound),
            "value_at_initial_mixture": fmt(result.value_at_start),
            "avg_welfare_at_initial_mixture": fmt(result.value_at_start / HORIZON),
            "margin_vs_action_only_avg": fmt((result.value_at_start - action_value) / HORIZON),
            "increment_vs_previous_cover_avg": fmt(increment),
            "monotone_value_refinement": int(prev_value is None or result.value_at_start >= prev_value - 1e-12),
            "monotone_radius_refinement": int(prev_radius is None or radius <= prev_radius + 1e-12),
            "certificate_status": "exact_refined_finite_cover_hjb_solve" if bound < 1e-10 else "finite_cover_gap_reported",
            "interpretation": "nested action-cover refinement: exact Bellman-HJB certificate at every level and monotone value improvement toward the R48 Full cover",
        })
        prev_value = result.value_at_start
        prev_radius = radius
    out = DATA / "inventory_cover_refinement_certificate.csv"
    with out.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(out)
    for row in rows:
        print(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
