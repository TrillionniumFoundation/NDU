#!/usr/bin/env python3
"""Compact equal-evaluation frontier audits for Experiments I and II.

The full 30-seed held-out tables remain the primary reported evidence.  This
script addresses a compute-fairness objection for the two lower-dimensional
benchmarks by regenerating lightweight CEM best-so-far training frontiers on the
same policy classes, objectives, budget rules, and seed schedule prefixes used
by the main experiment generator.  It intentionally depends only on numpy and
stdlib so it can run in a clean checkout without matplotlib/pandas.
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path
from typing import Callable

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SEED_STRIDE = 1000


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40, 40)))


def dim_scaled_budget(dim: int, base_iterations: int, base_population: int, ref_dim: int = 6) -> tuple[int, int]:
    scale = max(1.0, math.sqrt(dim / ref_dim))
    iterations = int(math.ceil(base_iterations * scale))
    population = int(math.ceil(base_population * scale / 2.0) * 2)
    return iterations, population


def search_budget(method: str, dim: int, base_iterations: int, base_population: int) -> tuple[int, int]:
    iterations, population = dim_scaled_budget(dim, base_iterations, base_population)
    if method == "full_ndu_joint":
        iterations = int(math.ceil(1.35 * iterations))
        population = int(math.ceil(1.20 * population / 2.0) * 2)
    return iterations, population


def experiment_seed_values(base_seed: int, count: int, stride: int = SEED_STRIDE) -> list[int]:
    return [int(base_seed + stride * (j + 1)) for j in range(count)]


class CEMOptimizer:
    def __init__(self, dim: int, eval_fn: Callable[[np.ndarray], float], seed: int = 0, init_scale: float = 0.7):
        self.dim = dim
        self.eval_fn = eval_fn
        self.rng = np.random.default_rng(seed)
        self.mean = np.zeros(dim, dtype=float)
        self.std = np.ones(dim, dtype=float) * init_scale

    def run(self, iterations: int, population: int, elite_frac: float = 0.25,
            mean_mix: float = 0.85, std_mix: float = 0.70, min_std: float = 0.05) -> tuple[list[int], list[float]]:
        elite_n = max(2, int(population * elite_frac))
        best_score = -1e18
        evaluations: list[int] = []
        best_scores: list[float] = []
        total_evals = 0
        for _ in range(iterations):
            samples = self.mean + self.std * self.rng.standard_normal((population, self.dim))
            scores = np.array([self.eval_fn(s) for s in samples], dtype=float)
            total_evals += population
            elite = samples[np.argsort(scores)[-elite_n:]]
            elite_mean = elite.mean(axis=0)
            elite_std = elite.std(axis=0) + 1e-3
            self.mean = mean_mix * elite_mean + (1.0 - mean_mix) * self.mean
            self.std = np.maximum(std_mix * elite_std + (1.0 - std_mix) * self.std, min_std)
            local_best = float(scores.max())
            if local_best > best_score:
                best_score = local_best
            evaluations.append(total_evals)
            best_scores.append(best_score)
        return evaluations, best_scores


# =============================
# Experiment I simulator/objective
# =============================

def exp1_decode_policy(method: str, params: np.ndarray, features_full: np.ndarray, features_orig: np.ndarray,
                       W: np.ndarray, h: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if method == "full_ndu_joint":
        mat = params.reshape(3, features_full.shape[1])
        raw = features_full @ mat.T
        pi = 1.25 * np.tanh(raw[:, 0])
        c_frac = 0.02 + 0.16 * sigmoid(raw[:, 1])
        theta = 0.05 + 0.95 * sigmoid(raw[:, 2])
        c = np.maximum(1e-5, c_frac * np.maximum(W, 1e-4))
        return pi, c, theta
    if method == "fixed_pref_rl":
        mat = params.reshape(2, features_orig.shape[1])
        raw = features_orig @ mat.T
        pi = 1.25 * np.tanh(raw[:, 0])
        c_frac = 0.02 + 0.16 * sigmoid(raw[:, 1])
        c = np.maximum(1e-5, c_frac * np.maximum(W, 1e-4))
        theta = np.full_like(pi, 0.25)
        return pi, c, theta
    if method == "augmented_state_rl":
        mat = params.reshape(2, features_full.shape[1])
        raw = features_full @ mat.T
        pi = 1.25 * np.tanh(raw[:, 0])
        c_frac = 0.02 + 0.16 * sigmoid(raw[:, 1])
        c = np.maximum(1e-5, c_frac * np.maximum(W, 1e-4))
        theta = np.full_like(pi, 0.25)
        return pi, c, theta
    if method == "preference_only":
        raw_theta = features_full @ params[:features_full.shape[1]]
        theta = 0.05 + 0.95 * sigmoid(raw_theta)
        surplus_pressure = np.clip(h / np.maximum(W, 1e-4), 0.0, 1.0)
        pi = np.clip(0.75 - 1.2 * surplus_pressure, -0.5, 1.0)
        c = np.maximum(1e-5, (0.045 + 0.03 * (1.0 - surplus_pressure)) * np.maximum(W, 1e-4))
        return pi, c, theta
    raise ValueError(method)


def simulate_exp1_mean_utility(method: str, params: np.ndarray, episodes: int = 72, steps: int = 40, seed: int = 0) -> float:
    rng = np.random.default_rng(seed)
    dt = 1.0 / steps
    shock = steps // 2
    W = np.full(episodes, 1.0)
    h = np.full(episodes, 0.08)
    ruined = np.zeros(episodes, dtype=bool)
    total_reward = np.zeros(episodes)
    for t in range(steps):
        mu = 0.11 if t < shock else -0.05
        sigma = 0.16 if t < shock else 0.36
        t_norm = np.full(episodes, t / max(1, steps - 1))
        w_norm = np.log(np.maximum(W, 1e-6) + 1.0)
        h_norm = np.log(np.maximum(h, 1e-6) + 1.0)
        surplus_norm = np.clip((W - h) / np.maximum(W, 1e-4), -1.0, 1.0)
        features_full = np.stack([np.ones(episodes), t_norm, w_norm, h_norm, surplus_norm], axis=1)
        features_orig = np.stack([np.ones(episodes), t_norm, w_norm], axis=1)
        pi, c, theta = exp1_decode_policy(method, params, features_full, features_orig, W, h)
        z = rng.standard_normal(episodes)
        dW = (0.02 * W + pi * W * (mu - 0.02) - c) * dt + pi * W * sigma * math.sqrt(dt) * z
        W_new = np.maximum(W + dW, 1e-5)
        h_new = np.maximum(h + theta * (c - h) * dt, 1e-5)
        surplus = c - h
        newly_ruined = (surplus <= 1e-4) | (W_new <= 1e-5)
        reward = ((1.0 + 0.65 * theta) * np.log(np.maximum(surplus, 1e-4))
                  - 0.10 * (theta - 0.25) ** 2
                  - 0.02 * pi ** 2
                  - 0.01 * (c / np.maximum(W, 1e-4)) ** 2) * dt
        reward = np.where(newly_ruined, reward - 2.5, reward)
        total_reward += np.where(ruined, 0.0, reward)
        ruined = ruined | newly_ruined
        W = np.where(ruined, np.maximum(W_new, 1e-5), W_new)
        h = np.where(ruined, np.maximum(h_new, 1e-5), h_new)
    total_reward += 0.45 * np.log(np.maximum(W, 1e-5))
    return float(total_reward.mean())


# =============================
# Experiment II simulator/objective
# =============================

def exp2_decode(method: str, params: np.ndarray, feat: np.ndarray, belief: np.ndarray,
                signal: np.ndarray, regime: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if method == "full_ndu_joint":
        w_theta = params[:6]
        w_b = params[6:12]
        a = params[12:18]
        theta = 0.05 + 0.95 * sigmoid(feat @ w_theta)
        theta_ctr = theta - 0.25
        b_next = sigmoid(feat @ w_b + 0.25 * theta + 0.12 * signal * theta_ctr + 0.05 * feat[:, 5])
        base_slope = 1.45 + 0.35 * sigmoid(a[0] + theta_ctr)
        base_pi = 0.95 - base_slope * b_next
        calm_bonus = 0.10 * sigmoid(a[1]) * (0.5 - b_next)
        theta_tilt = 0.10 * np.tanh(a[2]) * theta_ctr
        crisis_tilt = -0.16 * sigmoid(a[3]) * (b_next - 0.5) * (0.35 + theta)
        reentry = 0.12 * np.tanh(a[4]) * np.maximum(feat[:, 5], 0.0) * (1.0 - b_next)
        wealth_mod = 0.08 * np.tanh(a[5]) * feat[:, 2]
        pi = np.clip(base_pi + calm_bonus + theta_tilt + crisis_tilt + reentry + wealth_mod, 0.0, 1.10)
        return pi, theta, b_next
    if method == "fixed_pref_recurrent_rl":
        w_pi = params[:6]
        w_b = params[6:12]
        theta = np.full(feat.shape[0], 0.25)
        pi = 1.35 * np.tanh(feat @ w_pi + 1.0 * (belief - 0.5))
        b_next = sigmoid(feat @ w_b)
        return pi, theta, b_next
    if method == "oracle_joint_action_rl":
        feat_oracle = feat.copy()
        feat_oracle[:, 3] = regime
        w_pi = params[:6]
        theta = np.full(feat.shape[0], 0.25)
        pi = 1.35 * np.tanh(feat_oracle @ w_pi + 1.1 * (regime - 0.5))
        b_next = regime.astype(float)
        return pi, theta, b_next
    if method == "preference_only":
        w_theta = params[:6]
        w_b = params[6:12]
        theta = 0.05 + 0.95 * sigmoid(feat @ w_theta)
        b_next = sigmoid(feat @ w_b + 0.25 * theta)
        pi = np.clip(0.95 - 1.8 * b_next, -1.2, 1.2)
        return pi, theta, b_next
    raise ValueError(method)


def simulate_exp2_mean_utility(method: str, params: np.ndarray, episodes: int = 88, steps: int = 48, seed: int = 0) -> float:
    rng = np.random.default_rng(seed)
    dt = 1.0 / steps
    shock = steps // 2
    X = np.full(episodes, 1.0)
    regime = np.zeros(episodes, dtype=int)
    belief = np.full(episodes, 0.15)
    prev_ret = np.zeros(episodes)
    theta_paths = []
    pi_paths = []
    port_rets = []
    for t in range(steps):
        u = rng.random(episodes)
        if t < shock:
            regime = np.where(regime == 1, (u < 0.92).astype(int), (u < 0.05).astype(int))
        else:
            regime = np.where(regime == 1, (u < 0.95).astype(int), (u < 0.75).astype(int))
        signal = regime + 0.50 * rng.standard_normal(episodes)
        feat = np.stack([
            np.ones(episodes),
            np.full(episodes, t / max(1, steps - 1)),
            np.log(X + 1e-6),
            signal,
            belief,
            prev_ret,
        ], axis=1)
        pi, theta, belief = exp2_decode(method, params, feat, belief, signal, regime)
        sigma = np.where(regime == 1, 0.58, 0.18)
        mu = np.where(regime == 1, -0.04, 0.10)
        z = rng.standard_normal(episodes)
        ret = (0.01 + pi * (mu - 0.01)) * dt + pi * sigma * math.sqrt(dt) * z
        X = np.maximum(X * np.maximum(1.0 + ret, 1e-4), 1e-5)
        prev_ret = ret
        theta_paths.append(theta.copy())
        pi_paths.append(pi.copy())
        port_rets.append(ret.copy())
    theta_paths = np.stack(theta_paths, axis=1)
    pi_paths = np.stack(pi_paths, axis=1)
    port_rets = np.stack(port_rets, axis=1)
    utility = ((1.0 + 0.55 * theta_paths) * np.log(np.maximum(1.0 + port_rets, 1e-6))
               - 0.08 * (theta_paths - 0.25) ** 2
               - 0.01 * np.abs(pi_paths)).sum(axis=1)
    return float(utility.mean())


def exp2_eval_factory(method: str, seed: int) -> Callable[[np.ndarray], float]:
    def evaluate(params: np.ndarray) -> float:
        vals = [
            simulate_exp2_mean_utility(method, params, episodes=88, steps=48, seed=seed + off)
            for off in (0, 101, 202, 303)
        ]
        return float(np.mean(vals))
    return evaluate


def average_histories(histories: list[tuple[list[int], list[float]]]) -> tuple[list[int], list[float]]:
    evaluations = histories[0][0]
    scores = np.mean(np.stack([np.asarray(h[1], dtype=float) for h in histories], axis=0), axis=0)
    return evaluations, scores.tolist()


def compact_frontier(experiment: str, specs: dict[str, int], seed_base: int, seed_step: int,
                     base_iterations: int, base_population: int, seed_count: int) -> dict[str, tuple[list[int], list[float]]]:
    out: dict[str, tuple[list[int], list[float]]] = {}
    for i, (method, dim) in enumerate(specs.items()):
        sys.stderr.write(f"{experiment}: {method} ({seed_count} seeds)\n")
        histories = []
        for method_seed in experiment_seed_values(seed_base + seed_step * i, seed_count):
            if experiment == "exp1":
                eval_fn = lambda p, m=method, s=method_seed: simulate_exp1_mean_utility(m, p, episodes=72, steps=40, seed=s)
            elif experiment == "exp2":
                eval_fn = exp2_eval_factory(method, method_seed)
            else:
                raise ValueError(experiment)
            opt = CEMOptimizer(dim, eval_fn, seed=method_seed)
            iterations, population = search_budget(method, dim, base_iterations, base_population)
            if experiment == "exp2" and method == "full_ndu_joint":
                iterations += 4
                population += 4
            histories.append(opt.run(iterations=iterations, population=population, elite_frac=0.25))
        out[method] = average_histories(histories)
    return out


def write_frontier(path: Path, frontier: dict[str, tuple[list[int], list[float]]]) -> list[dict[str, str]]:
    methods = list(frontier)
    grid = sorted({ev for evals, _ in frontier.values() for ev in evals})
    rows = []
    last = {m: None for m in methods}
    idx = {m: 0 for m in methods}
    for ev in grid:
        row = {"evaluations": str(ev)}
        for m in methods:
            evals, scores = frontier[m]
            while idx[m] < len(evals) and evals[idx[m]] <= ev:
                last[m] = scores[idx[m]]
                idx[m] += 1
            row[m] = "" if last[m] is None else f"{last[m]:.17g}"
        rows.append(row)
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["evaluations", *methods])
        writer.writeheader()
        writer.writerows(rows)
    return rows


def value_at_or_before(rows: list[dict[str, str]], method: str, budget: int) -> float:
    value: float | None = None
    for row in rows:
        if int(row["evaluations"]) <= budget and row.get(method):
            value = float(row[method])
    if value is None:
        raise RuntimeError(f"missing {method} at budget {budget}")
    return value


def write_audit(path: Path, experiment: str, rows: list[dict[str, str]], methods: list[str], budgets: list[int], seed_count: int) -> None:
    out_rows = []
    for budget in budgets:
        values = {m: value_at_or_before(rows, m, budget) for m in methods}
        non_ndu_best = max(v for m, v in values.items() if m != "full_ndu_joint")
        leader = max(values, key=lambda m: values[m])
        sorted_vals = sorted(values.values(), reverse=True)
        out_rows.append({
            "experiment": experiment,
            "seed_count": str(seed_count),
            "evaluation_budget": str(budget),
            **{m: f"{values[m]:.17g}" for m in methods},
            "leader": leader,
            "second_best": f"{sorted_vals[1]:.17g}",
            "full_minus_best_non_ndu": f"{values['full_ndu_joint'] - non_ndu_best:.17g}",
        })
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-count", type=int, default=6)
    args = parser.parse_args()
    DATA.mkdir(parents=True, exist_ok=True)

    exp1_specs = {
        "full_ndu_joint": 15,
        "fixed_pref_rl": 6,
        "augmented_state_rl": 10,
        "preference_only": 5,
    }
    exp2_specs = {
        "full_ndu_joint": 18,
        "fixed_pref_recurrent_rl": 12,
        "oracle_joint_action_rl": 6,
        "preference_only": 12,
    }

    exp1_frontier = compact_frontier("exp1", exp1_specs, seed_base=11, seed_step=10,
                                     base_iterations=8, base_population=24, seed_count=args.seed_count)
    exp1_rows = write_frontier(DATA / "exp1_training_frontier_compact.csv", exp1_frontier)
    write_audit(DATA / "exp1_equal_evaluation_audit.csv", "exp1", exp1_rows, list(exp1_specs), [192, 352, 828], args.seed_count)

    exp2_frontier = compact_frontier("exp2", exp2_specs, seed_base=23, seed_step=20,
                                     base_iterations=12, base_population=30, seed_count=args.seed_count)
    exp2_rows = write_frontier(DATA / "exp2_training_frontier_compact.csv", exp2_frontier)
    write_audit(DATA / "exp2_equal_evaluation_audit.csv", "exp2", exp2_rows, list(exp2_specs), [360, 748, 2244], args.seed_count)

    print(DATA / "exp1_equal_evaluation_audit.csv")
    print(DATA / "exp2_equal_evaluation_audit.csv")


if __name__ == "__main__":
    main()
