#!/usr/bin/env python3
"""Same-benchmark direct-P versus Z-inversion inventory audit.

This audit uses the canonical inventory/service-level demand dynamics, cost
accounting, fill-rate metric, and 40-period horizon.  It does not introduce a
new task: the only change is how the service-pressure shadow price used by the
policy is represented under equal-scale prediction noise.

* direct-P: observe P_hat = P_* + eta.
* Z-inversion: observe Z_hat = sqrt(2 eps) P_* + eta and recover
  P_hat = Z_hat / sqrt(2 eps).

With equal-scale eta, the Z route amplifies the perturbation as eps decreases.
The resulting theta is then run through the same inventory simulator.
"""
from __future__ import annotations

import csv
import math
import statistics as stats
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SEED_COUNT = 30
SEED_STRIDE = 1000
HORIZON = 40
REPORT_EPISODES = 512
EPSILONS = [0.1, 0.01, 0.001]
METHODS = ["oracle_p_inventory", "direct_p_inventory", "z_inversion_inventory"]
NOISE_STD = 0.018


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40.0, 40.0)))


def seed_values(base: int = 8061) -> list[int]:
    return [base + SEED_STRIDE * (j + 1) for j in range(SEED_COUNT)]


def shadow_price(t: int, ewma, inventory, backlog, last_demand):
    shock = np.maximum(0.0, last_demand - ewma)
    tfeat = t / max(HORIZON - 1, 1) - 0.5
    p = (
        -0.05
        + 0.95 * backlog / 24.0
        + 0.42 * shock / 12.0
        + 0.22 * (ewma - 22.0) / 12.0
        - 0.18 * (inventory - 24.0) / 36.0
        + 0.10 * tfeat
    )
    return np.clip(p, -2.0, 2.0)


def theta_from_p(p_hat):
    return 0.55 + 1.65 * sigmoid(2.1 * p_hat)


def simulate(method: str, epsilon: float, seed: int, episodes: int = REPORT_EPISODES) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    noise_rng = np.random.default_rng(seed + 90917)
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
    theta_sqerr = np.zeros(episodes)
    p_sqerr = np.zeros(episodes)

    for t in range(HORIZON):
        p_star = shadow_price(t, ewma, inventory, backlog, last_demand)
        theta_star = theta_from_p(p_star)
        eta = noise_rng.normal(0.0, NOISE_STD, size=episodes)
        if method == "oracle_p_inventory":
            p_hat = p_star
        elif method == "direct_p_inventory":
            p_hat = p_star + eta
        elif method == "z_inversion_inventory":
            z_hat = math.sqrt(2.0 * epsilon) * p_star + eta
            p_hat = z_hat / math.sqrt(2.0 * epsilon)
        else:
            raise ValueError(method)
        p_hat = np.clip(p_hat, -3.0, 3.0)
        theta = theta_from_p(p_hat)
        theta_sqerr += (theta - theta_star) ** 2
        p_sqerr += (p_hat - p_star) ** 2

        shock = np.maximum(0.0, last_demand - ewma)
        action_pressure = 0.95 + 0.70 * sigmoid(p_hat + 0.35 * shock / 12.0 + 0.25 * backlog / 24.0)
        backlog_boost = 0.55 + 0.45 * theta
        demand_forecast = ewma + 0.40 * shock + 0.22 * backlog
        order_up_to = demand_forecast * (1.0 + 0.42 * theta * action_pressure) + backlog_boost * backlog
        order_up_to = np.clip(order_up_to, 0.0, 115.0)
        q = np.maximum(0.0, order_up_to - inventory)
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
        theta_cost = 0.045 * (theta - 1.0) ** 2
        total_cost += holding_cost + shortage_cost + order_cost + theta_cost
        total_demand += demand
        total_filled += filled
        total_order += q
        total_inventory += inventory
        ewma = 0.82 * ewma + 0.18 * demand
        last_demand = demand

    fill_rate = total_filled / np.maximum(total_demand, 1.0)
    avg_cost = total_cost / HORIZON
    avg_inventory = total_inventory / HORIZON
    avg_order = total_order / HORIZON
    welfare = -avg_cost + 8.0 * (fill_rate - 0.92) - 0.03 * service_breach
    return {
        "mean_welfare": float(np.mean(welfare)),
        "avg_cost": float(np.mean(avg_cost)),
        "fill_rate": float(np.mean(fill_rate)),
        "ending_backlog": float(np.mean(backlog)),
        "avg_inventory": float(np.mean(avg_inventory)),
        "avg_order": float(np.mean(avg_order)),
        "service_breach_count": float(np.mean(service_breach)),
        "theta_rmse": float(np.sqrt(np.mean(theta_sqerr / HORIZON))),
        "p_rmse": float(np.sqrt(np.mean(p_sqerr / HORIZON))),
    }


def ci95(vals: list[float]) -> float:
    return 1.96 * (stats.stdev(vals) / math.sqrt(len(vals))) if len(vals) > 1 else 0.0


def summarize(seed_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    metrics = ["mean_welfare", "avg_cost", "fill_rate", "ending_backlog", "avg_inventory", "avg_order", "service_breach_count", "theta_rmse", "p_rmse"]
    for eps in EPSILONS:
        eps_rows = [r for r in seed_rows if abs(float(r["epsilon"]) - eps) < 1e-12]
        direct_summary = None
        z_summary = None
        for method in METHODS:
            rs = [r for r in eps_rows if r["method"] == method]
            row: dict[str, object] = {
                "benchmark": "inventory_service_level",
                "epsilon": f"{eps:.8g}",
                "method": method,
                "n": len(rs),
                "noise_model": "equal_scale_noise_on_reported_P_or_Z_target",
                "noise_std": f"{NOISE_STD:.12g}",
            }
            for metric in metrics:
                vals = [float(r[metric]) for r in rs]
                row[metric] = f"{sum(vals)/len(vals):.12g}"
                row[f"{metric}_ci95"] = f"{ci95(vals):.12g}"
            out.append(row)
            if method == "direct_p_inventory":
                direct_summary = row
            if method == "z_inversion_inventory":
                z_summary = row
        if direct_summary and z_summary:
            direct_w = float(direct_summary["mean_welfare"])
            direct_theta = float(direct_summary["theta_rmse"])
            for row in out[-len(METHODS):]:
                row["welfare_gap_vs_direct_p"] = f"{float(row['mean_welfare']) - direct_w:.12g}"
                row["theta_rmse_ratio_vs_direct_p"] = f"{float(row['theta_rmse']) / max(direct_theta, 1e-12):.12g}"
                row["interpretation"] = (
                    "same_inventory_benchmark_direct_P_vs_Z_inversion; lower theta_rmse and higher welfare favor direct_P under small epsilon"
                )
    return out


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    seed_rows: list[dict[str, object]] = []
    for eps in EPSILONS:
        for method in METHODS:
            for seed in seed_values():
                row: dict[str, object] = {
                    "audit": "same_benchmark_inventory_direct_p_vs_z",
                    "epsilon": f"{eps:.8g}",
                    "method": method,
                    "seed": seed,
                }
                row.update(simulate(method, eps, seed))
                seed_rows.append(row)
    metric_rows = summarize(seed_rows)
    write_csv(DATA / "inventory_direct_p_vs_z_seed_metrics.csv", seed_rows)
    write_csv(DATA / "inventory_direct_p_vs_z_metrics.csv", metric_rows)
    print(DATA / "inventory_direct_p_vs_z_seed_metrics.csv")
    print(DATA / "inventory_direct_p_vs_z_metrics.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
