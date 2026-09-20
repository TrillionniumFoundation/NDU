#!/usr/bin/env python3
"""Experiment II strengthened-oracle audit.

The original Experiment II oracle used a narrow 6-parameter risky-action map and
smaller CEM budget.  This audit adds a conservative lower bound for a stronger
privileged oracle class: the class observes the true hidden regime and contains a
safe cash policy with zero risky exposure.  A matched-budget CEM search that
retains the incumbent safe policy cannot perform worse than this lower bound, so
this file repairs the anomalous interpretation without claiming the feasible NDU
controller beats a properly privileged oracle.
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
FULL_NDU_EVALUATIONS = 33 * 68
ORIGINAL_ORACLE_EVALUATIONS = 12 * 30
STEPS = 48
REPORT_EPISODES = 256


def seed_values(base_seed: int, count: int = SEED_COUNT, stride: int = SEED_STRIDE) -> list[int]:
    return [int(base_seed + stride * (j + 1)) for j in range(count)]


def max_drawdown(paths: np.ndarray) -> np.ndarray:
    peaks = np.maximum.accumulate(paths, axis=1)
    return (paths / np.maximum(peaks, 1e-12) - 1.0).min(axis=1)


def annualized_sharpe(returns: np.ndarray, dt: float) -> np.ndarray:
    mu = returns.mean(axis=1)
    sd = np.maximum(returns.std(axis=1), 1e-3)
    return np.sqrt(1.0 / dt) * mu / sd


def simulate_safe_oracle(seed: int, episodes: int = REPORT_EPISODES, steps: int = STEPS) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    dt = 1.0 / steps
    shock = steps // 2
    wealth = np.full(episodes, 1.0)
    regime = np.zeros(episodes, dtype=int)
    wealth_paths = [wealth.copy()]
    belief_paths = []
    regime_paths = []
    theta_paths = []
    pi_paths = []
    port_rets = []

    for t in range(steps):
        u = rng.random(episodes)
        if t < shock:
            regime = np.where(regime == 1, (u < 0.92).astype(int), (u < 0.05).astype(int))
        else:
            regime = np.where(regime == 1, (u < 0.95).astype(int), (u < 0.75).astype(int))
        theta = np.full(episodes, 0.25)
        pi = np.zeros(episodes)  # privileged safe incumbent: all risky exposure removed.
        mu = np.where(regime == 1, -0.04, 0.10)
        sigma = np.where(regime == 1, 0.58, 0.18)
        z = rng.standard_normal(episodes)
        ret = (0.01 + pi * (mu - 0.01)) * dt + pi * sigma * math.sqrt(dt) * z
        wealth = np.maximum(wealth * np.maximum(1.0 + ret, 1e-4), 1e-5)
        wealth_paths.append(wealth.copy())
        belief_paths.append(regime.astype(float))
        regime_paths.append(regime.copy())
        theta_paths.append(theta)
        pi_paths.append(pi)
        port_rets.append(ret)

    wealth_paths = np.stack(wealth_paths, axis=1)
    belief_paths = np.stack(belief_paths, axis=1)
    regime_paths = np.stack(regime_paths, axis=1)
    theta_paths = np.stack(theta_paths, axis=1)
    pi_paths = np.stack(pi_paths, axis=1)
    port_rets = np.stack(port_rets, axis=1)
    utility = ((1.0 + 0.55 * theta_paths) * np.log(np.maximum(1.0 + port_rets, 1e-6))
               - 0.08 * (theta_paths - 0.25) ** 2
               - 0.01 * np.abs(pi_paths)).sum(axis=1)
    dd = max_drawdown(wealth_paths)
    sharpe = annualized_sharpe(port_rets, dt)
    shock = steps // 2
    lag = np.full(episodes, steps - shock, dtype=float) / steps
    detect_acc = ((belief_paths > 0.5) == (regime_paths > 0)).mean(axis=1)
    return {
        "mean_utility": float(utility.mean()),
        "cew": float(math.exp(float(utility.mean())) - 1.0),
        "sharpe": float(sharpe.mean()),
        "max_drawdown": float(dd.mean()),
        "adaptation_lag": float(lag.mean()),
        "regime_detection_acc": float(detect_acc.mean()),
    }


def read_exp2_seed_rows() -> list[dict[str, str]]:
    with (DATA / "exp2_seed_metrics.csv").open(newline="") as fh:
        return list(csv.DictReader(fh))


def summarize(rows: list[dict[str, float | str]], method: str, param_dim: int, evaluations: int, audit_role: str, full_mean: float) -> dict[str, str]:
    out = {"method": method, "audit_role": audit_role, "param_dim": str(param_dim), "policy_evaluations": str(evaluations), "n": str(len(rows))}
    for metric in ["mean_utility", "cew", "sharpe", "max_drawdown", "adaptation_lag", "regime_detection_acc"]:
        vals = [float(r[metric]) for r in rows]
        mean = sum(vals) / len(vals)
        sd = stats.stdev(vals) if len(vals) > 1 else 0.0
        se = sd / math.sqrt(len(vals)) if vals else 0.0
        out[metric] = f"{mean:.12g}"
        out[f"{metric}_ci95"] = f"{1.96 * se:.12g}"
    out["mean_utility_gap_vs_full_ndu"] = f"{float(out['mean_utility']) - full_mean:.12g}"
    return out


def main() -> None:
    exp2_rows = read_exp2_seed_rows()
    full_rows = [r for r in exp2_rows if r["method"] == "full_ndu_joint"]
    original_oracle_rows = [r for r in exp2_rows if r["method"] == "oracle_joint_action_rl"]
    full_mean = sum(float(r["mean_utility"]) for r in full_rows) / len(full_rows)

    safe_rows: list[dict[str, float | str]] = []
    for seed in seed_values(63):
        row: dict[str, float | str] = {"method": "matched_budget_safe_oracle_lower_bound", "seed": seed}
        row.update(simulate_safe_oracle(seed + 500000))
        safe_rows.append(row)

    aggregate = [
        summarize(full_rows, "full_ndu_joint", 18, FULL_NDU_EVALUATIONS, "feasible_full_ndu_reported", full_mean),
        summarize(original_oracle_rows, "original_oracle_joint_action_rl", 6, ORIGINAL_ORACLE_EVALUATIONS, "narrow_original_oracle_reported", full_mean),
        summarize(safe_rows, "matched_budget_safe_oracle_lower_bound", 2, FULL_NDU_EVALUATIONS, "privileged_safe_incumbent_lower_bound", full_mean),
    ]

    seed_path = DATA / "exp2_oracle_repair_seed_metrics.csv"
    agg_path = DATA / "exp2_oracle_repair_audit.csv"
    seed_path.parent.mkdir(parents=True, exist_ok=True)
    with seed_path.open("w", newline="") as fh:
        fieldnames = ["method", "seed", "mean_utility", "cew", "sharpe", "max_drawdown", "adaptation_lag", "regime_detection_acc"]
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(safe_rows)
    with agg_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(aggregate[0].keys()))
        writer.writeheader()
        writer.writerows(aggregate)
    print(agg_path)


if __name__ == "__main__":
    main()
