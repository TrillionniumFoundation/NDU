#!/usr/bin/env python3
"""Compact inventory sensitivity grid for the NDU OR manuscript.

The script reuses the periodic-review inventory mechanism with three policy
classes and re-optimizes each class under a small set of OR-relevant stress
settings.  It is intentionally compact: the goal is to test whether the core
inventory/service-level conclusion survives changes in demand variability,
shortage pressure, and capacity friction, not to provide a full industrial
calibration study.
"""
from __future__ import annotations

import argparse
import csv
import math
import statistics as stats
from dataclasses import dataclass
from pathlib import Path

import numpy as np

METHODS = [
    "full_ndu_inventory",
    "action_only_adaptive_base_stock",
    "fixed_service_base_stock",
]
SEED_COUNT = 10
SEED_STRIDE = 1000
HORIZON = 40
SEARCH_EPISODES = 40
REPORT_EPISODES = 384


@dataclass(frozen=True)
class Scenario:
    name: str
    demand_base: float = 18.0
    high_increment: float = 10.0
    sd_base: float = 3.0
    sd_high: float = 1.5
    flip_down: float = 0.08
    flip_up: float = 0.12
    seasonal_amp: float = 2.5
    holding_cost: float = 0.28
    shortage_cost: float = 2.85
    order_linear: float = 0.055
    order_quad: float = 0.010
    soft_capacity: float = 35.0
    theta_cost: float = 0.045
    service_reward: float = 8.0
    service_threshold: float = 0.92
    breach_penalty: float = 0.03


SCENARIOS = [
    Scenario("baseline"),
    Scenario("volatile_demand", high_increment=13.5, sd_base=4.8, sd_high=2.7, seasonal_amp=4.0, flip_down=0.10, flip_up=0.16),
    Scenario("high_shortage_penalty", shortage_cost=4.35, service_reward=9.5, breach_penalty=0.055),
    Scenario("tight_capacity", order_quad=0.030, soft_capacity=24.0, shortage_cost=3.35, service_reward=9.0),
]


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40.0, 40.0)))


def method_dim(method: str) -> int:
    return {
        "full_ndu_inventory": 12,
        "action_only_adaptive_base_stock": 7,
        "fixed_service_base_stock": 3,
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

    if method == "full_ndu_inventory":
        theta = 0.55 + 1.65 * sigmoid(params[:6] @ features)
        action_pressure = 0.35 + 1.95 * sigmoid(params[6:12] @ features)
        backlog_boost = 0.55 + 0.45 * theta
    elif method == "action_only_adaptive_base_stock":
        theta = np.ones_like(ewma)
        action_pressure = 0.35 + 1.95 * sigmoid(params[:6] @ features)
        backlog_boost = 0.65 + 0.55 * sigmoid(params[6])
    elif method == "fixed_service_base_stock":
        theta = np.ones_like(ewma)
        z = params[0] + params[1] * (ewma - 22.0) / 12.0 + params[2] * (t / max(HORIZON - 1, 1) - 0.5)
        action_pressure = 0.45 + 1.65 * sigmoid(z)
        backlog_boost = 0.70
    else:
        raise ValueError(method)

    demand_forecast = ewma + 0.40 * shock + 0.22 * backlog
    order_up_to = demand_forecast * (1.0 + 0.42 * theta * action_pressure) + backlog_boost * backlog
    order_up_to = np.clip(order_up_to, 0.0, 115.0)
    q = np.maximum(0.0, order_up_to - inventory)
    return q, theta


def simulate(method: str, params: np.ndarray, seed: int, episodes: int, scenario: Scenario) -> dict[str, float]:
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
        flips_down = rng.random(episodes) < scenario.flip_down
        flips_up = rng.random(episodes) < scenario.flip_up
        high = np.where(high, ~flips_down, flips_up)
        seasonal = scenario.seasonal_amp * math.sin(2.0 * math.pi * t / 20.0)
        mean = scenario.demand_base + seasonal + high.astype(float) * scenario.high_increment
        sd = scenario.sd_base + high.astype(float) * scenario.sd_high
        demand = np.maximum(0.0, np.rint(rng.normal(mean, sd))).astype(float)
        total_need = backlog + demand
        filled = np.minimum(inventory, total_need)
        inventory = inventory - filled
        backlog = total_need - filled
        fill_rate_t = np.divide(filled, total_need, out=np.ones_like(filled), where=total_need > 1e-9)
        service_breach += fill_rate_t < scenario.service_threshold

        holding_cost = scenario.holding_cost * inventory
        shortage_cost = scenario.shortage_cost * backlog
        order_cost = scenario.order_linear * q + scenario.order_quad * np.maximum(0.0, q - scenario.soft_capacity) ** 2 / max(scenario.soft_capacity, 1.0)
        theta_cost = scenario.theta_cost * (theta - 1.0) ** 2
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
    welfare = -avg_cost + scenario.service_reward * (fill_rate - scenario.service_threshold) - scenario.breach_penalty * service_breach
    return {
        "mean_welfare": float(np.mean(welfare)),
        "avg_cost": float(np.mean(avg_cost)),
        "fill_rate": float(np.mean(fill_rate)),
        "ending_backlog": float(np.mean(backlog)),
        "avg_inventory": float(np.mean(avg_inventory)),
        "avg_order": float(np.mean(avg_order)),
        "theta_std": float(np.mean(theta_std)),
        "service_breach_count": float(np.mean(service_breach)),
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


def optimize_and_report(method: str, seed: int, scenario: Scenario) -> dict[str, float | str | int]:
    dim = method_dim(method)
    if method == "full_ndu_inventory":
        iterations, population = 10, 24
    elif method == "action_only_adaptive_base_stock":
        iterations, population = 9, 22
    else:
        iterations, population = 8, 18
    cem = CEM(dim, seed + 17)

    def score(params: np.ndarray) -> float:
        return simulate(method, params, seed + 100000, SEARCH_EPISODES, scenario)["mean_welfare"]

    params, search_score, evaluations = cem.run(score, iterations, population)
    report = simulate(method, params, seed + 500000, REPORT_EPISODES, scenario)
    row: dict[str, float | str | int] = {
        "scenario": scenario.name,
        "method": method,
        "seed": seed,
        "param_dim": dim,
        "cem_iterations": iterations,
        "cem_population": population,
        "policy_evaluations": evaluations,
        "search_mean_welfare": search_score,
    }
    row.update(report)
    return row


def summarize(rows: list[dict[str, float | str | int]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    metrics = ["mean_welfare", "avg_cost", "fill_rate", "ending_backlog", "avg_inventory", "avg_order", "theta_std", "service_breach_count"]
    for scenario in [s.name for s in SCENARIOS]:
        scenario_rows = [r for r in rows if r["scenario"] == scenario]
        scenario_summaries: list[dict[str, str]] = []
        for method in METHODS:
            rs = [r for r in scenario_rows if r["method"] == method]
            summary: dict[str, str] = {"scenario": scenario, "method": method, "n": str(len(rs))}
            for metric in metrics:
                vals = [float(r[metric]) for r in rs]
                mean = sum(vals) / len(vals)
                sd = stats.stdev(vals) if len(vals) > 1 else 0.0
                se = sd / math.sqrt(len(vals)) if vals else 0.0
                summary[metric] = f"{mean:.12g}"
                summary[f"{metric}_ci95"] = f"{1.96 * se:.12g}"
            scenario_summaries.append(summary)
        best = max(float(r["mean_welfare"]) for r in scenario_summaries)
        for summary in scenario_summaries:
            summary["welfare_gap_to_best"] = f"{best - float(summary['mean_welfare']):.12g}"
            out.append(summary)
    return out


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default=str(Path(__file__).resolve().parents[1] / "data"))
    args = parser.parse_args()
    outdir = Path(args.outdir).resolve()
    rows: list[dict[str, float | str | int]] = []
    base_seeds = {
        "full_ndu_inventory": 761,
        "action_only_adaptive_base_stock": 1761,
        "fixed_service_base_stock": 2761,
    }
    for scenario in SCENARIOS:
        for method in METHODS:
            for seed in seed_values(base_seeds[method]):
                rows.append(optimize_and_report(method, seed + 97 * SCENARIOS.index(scenario), scenario))
                print(scenario.name, method, seed, flush=True)
    summary = summarize(rows)
    write_csv(outdir / "inventory_sensitivity_grid_seed_metrics.csv", rows)
    write_csv(outdir / "inventory_sensitivity_grid_metrics.csv", summary)
    print(outdir / "inventory_sensitivity_grid_metrics.csv")


if __name__ == "__main__":
    main()
