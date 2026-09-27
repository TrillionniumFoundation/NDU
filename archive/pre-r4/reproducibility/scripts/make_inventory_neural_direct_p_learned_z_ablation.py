#!/usr/bin/env python3
"""Trainable neural direct-P versus learned-Z inventory representation ablation.

This is the neural counterpart of ``make_inventory_direct_p_learned_z_ablation``.
It keeps the canonical inventory/service-level simulator, state cloud, target
noise scale, neural architecture, optimizer budget, policy map, and evaluation
seeds fixed.  The only changed object is the supervised representation learned
by the NBO shadow-price component:

* neural_direct_p_inventory learns P_*(x)+eta with a trainable tanh MLP;
* neural_learned_z_inventory learns Z_*(x)=sqrt(2 eps)P_*(x)+eta with the same
  MLP/optimizer budget and then recovers P by Z/sqrt(2 eps).

The audit is dependency-light (NumPy only) but uses a fully trainable neural
network rather than a ridge closed form.  It directly targets the referee
concern that direct-P should be compared against a learned-Z representation, not
only against an analytic perturbation.
"""
from __future__ import annotations

import csv
import math
import statistics as stats
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SEED_COUNT = 18
SEED_STRIDE = 1000
HORIZON = 40
TRAIN_SAMPLES = 720
REPORT_EPISODES = 512
EPSILONS = [0.1, 0.01, 0.001]
METHODS = ["oracle_p_inventory", "neural_direct_p_inventory", "neural_learned_z_inventory"]
NOISE_STD = 0.030
WIDTH = 32
TRAIN_STEPS = 850
BATCH = 160
LR = 0.012


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40.0, 40.0)))


def seed_values(base: int = 12841) -> list[int]:
    return [base + SEED_STRIDE * (j + 1) for j in range(SEED_COUNT)]


def shadow_price(t, ewma, inventory, backlog, last_demand):
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


def features(t, ewma, inventory, backlog, last_demand):
    t_arr = np.asarray(t, dtype=float)
    ewma = np.asarray(ewma, dtype=float)
    inventory = np.asarray(inventory, dtype=float)
    backlog = np.asarray(backlog, dtype=float)
    last_demand = np.asarray(last_demand, dtype=float)
    shock = np.maximum(0.0, last_demand - ewma)
    tfeat = t_arr / max(HORIZON - 1, 1) - 0.5
    cols = [
        np.ones_like(ewma),
        backlog / 24.0,
        shock / 12.0,
        (ewma - 22.0) / 12.0,
        (inventory - 24.0) / 36.0,
        tfeat,
        np.clip(backlog / 24.0, 0.0, 2.0) ** 2,
        np.clip(shock / 12.0, 0.0, 2.0) ** 2,
    ]
    return np.column_stack(cols)


def collect_training_states(seed: int, samples: int = TRAIN_SAMPLES):
    rng = np.random.default_rng(seed + 31077)
    inventory = np.full(samples, 26.0)
    backlog = np.zeros(samples)
    ewma = np.full(samples, 22.0)
    last_demand = np.full(samples, 22.0)
    high = np.zeros(samples, dtype=bool)
    x_rows = []
    p_rows = []
    per_t = max(1, samples // HORIZON)
    for t in range(HORIZON):
        take = slice(0, min(per_t, samples))
        x_rows.append(features(np.full(per_t, t), ewma[take], inventory[take], backlog[take], last_demand[take]))
        p_rows.append(shadow_price(t, ewma[take], inventory[take], backlog[take], last_demand[take]))

        p_star = shadow_price(t, ewma, inventory, backlog, last_demand)
        theta = theta_from_p(p_star + rng.normal(0.0, 0.22, size=samples))
        shock = np.maximum(0.0, last_demand - ewma)
        demand_forecast = ewma + 0.38 * shock + 0.20 * backlog
        order_up_to = demand_forecast * (1.0 + 0.36 * theta) + (0.45 + 0.42 * theta) * backlog
        order_up_to += rng.normal(0.0, 3.0, size=samples)
        order_up_to = np.clip(order_up_to, 0.0, 115.0)
        q = np.maximum(0.0, order_up_to - inventory)
        inventory = inventory + q

        flips_down = rng.random(samples) < 0.08
        flips_up = rng.random(samples) < 0.12
        high = np.where(high, ~flips_down, flips_up)
        seasonal = 2.5 * math.sin(2.0 * math.pi * t / 20.0)
        mean = 18.0 + seasonal + high.astype(float) * 10.0
        sd = 3.0 + high.astype(float) * 1.5
        demand = np.maximum(0.0, np.rint(rng.normal(mean, sd))).astype(float)
        total_need = backlog + demand
        filled = np.minimum(inventory, total_need)
        inventory = inventory - filled
        backlog = total_need - filled
        ewma = 0.82 * ewma + 0.18 * demand
        last_demand = demand
    X = np.vstack(x_rows)
    y = np.concatenate(p_rows)
    return X, y


class TinyTanhNet:
    def __init__(self, rng: np.random.Generator, in_dim: int, width: int = WIDTH):
        self.W1 = 0.20 * rng.standard_normal((in_dim, width))
        self.b1 = np.zeros(width)
        self.W2 = 0.20 * rng.standard_normal(width)
        self.b2 = 0.0
        self.m = {"W1": np.zeros_like(self.W1), "b1": np.zeros_like(self.b1), "W2": np.zeros_like(self.W2), "b2": 0.0}
        self.v = {"W1": np.zeros_like(self.W1), "b1": np.zeros_like(self.b1), "W2": np.zeros_like(self.W2), "b2": 0.0}
        self.step_count = 0

    def forward(self, X):
        H = np.tanh(X @ self.W1 + self.b1)
        y = H @ self.W2 + self.b2
        return y, H

    def fit(self, X, y, *, steps=TRAIN_STEPS, batch=BATCH, lr=LR, seed=0):
        rng = np.random.default_rng(seed)
        n = X.shape[0]
        beta1, beta2 = 0.9, 0.999
        eps = 1e-8
        for _ in range(steps):
            idx = rng.integers(0, n, size=batch)
            xb = X[idx]
            yb = y[idx]
            pred, H = self.forward(xb)
            err = pred - yb
            gy = (2.0 / batch) * err
            grad_W2 = H.T @ gy
            grad_b2 = float(gy.sum())
            gH = gy[:, None] * self.W2[None, :]
            gpre = gH * (1.0 - H * H)
            grad_W1 = xb.T @ gpre
            grad_b1 = gpre.sum(axis=0)
            grads = {"W1": grad_W1, "b1": grad_b1, "W2": grad_W2, "b2": grad_b2}
            self.step_count += 1
            for name, grad in grads.items():
                self.m[name] = beta1 * self.m[name] + (1.0 - beta1) * grad
                self.v[name] = beta2 * self.v[name] + (1.0 - beta2) * (grad * grad)
                mhat = self.m[name] / (1.0 - beta1 ** self.step_count)
                vhat = self.v[name] / (1.0 - beta2 ** self.step_count)
                setattr(self, name, getattr(self, name) - lr * mhat / (np.sqrt(vhat) + eps))

    def predict(self, X):
        return self.forward(X)[0]


def standardize_train(X):
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    sd[sd < 1e-10] = 1.0
    return mu, sd, (X - mu) / sd


def train_models(seed: int, epsilon: float):
    X, p_star = collect_training_states(seed)
    mu, sd, Xs = standardize_train(X)
    noise_rng = np.random.default_rng(seed + 771331)
    eta_direct = noise_rng.normal(0.0, NOISE_STD, size=p_star.shape)
    eta_z = noise_rng.normal(0.0, NOISE_STD, size=p_star.shape)

    direct_net = TinyTanhNet(np.random.default_rng(seed + 19001), X.shape[1])
    z_net = TinyTanhNet(np.random.default_rng(seed + 29001), X.shape[1])
    direct_net.fit(Xs, p_star + eta_direct, seed=seed + 101)
    z_net.fit(Xs, math.sqrt(2.0 * epsilon) * p_star + eta_z, seed=seed + 202)
    pred_p = direct_net.predict(Xs)
    pred_z_as_p = z_net.predict(Xs) / math.sqrt(2.0 * epsilon)
    return {
        "mu": mu,
        "sd": sd,
        "direct_net": direct_net,
        "z_net": z_net,
        "train_p_rmse_direct": float(np.sqrt(np.mean((pred_p - p_star) ** 2))),
        "train_p_rmse_z_inverted": float(np.sqrt(np.mean((pred_z_as_p - p_star) ** 2))),
    }


def predict_model(models, X, method: str, epsilon: float):
    Xs = (X - models["mu"]) / models["sd"]
    if method == "neural_direct_p_inventory":
        return models["direct_net"].predict(Xs)
    if method == "neural_learned_z_inventory":
        return models["z_net"].predict(Xs) / math.sqrt(2.0 * epsilon)
    raise ValueError(method)


def simulate(method: str, epsilon: float, seed: int, models: dict[str, object], episodes: int = REPORT_EPISODES) -> dict[str, float]:
    rng = np.random.default_rng(seed + 1193)
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
        if method == "oracle_p_inventory":
            p_hat = p_star
        else:
            X = features(np.full(episodes, t), ewma, inventory, backlog, last_demand)
            p_hat = predict_model(models, X, method, epsilon)
        p_hat = np.clip(p_hat, -3.0, 3.0)
        theta = theta_from_p(p_hat)
        theta_star = theta_from_p(p_star)
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
        sdemand = 3.0 + high.astype(float) * 1.5
        demand = np.maximum(0.0, np.rint(rng.normal(mean, sdemand))).astype(float)
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
    metrics = ["mean_welfare", "avg_cost", "fill_rate", "ending_backlog", "avg_inventory", "avg_order", "service_breach_count", "theta_rmse", "p_rmse", "train_p_rmse_direct", "train_p_rmse_z_inverted"]
    for eps in EPSILONS:
        eps_rows = [r for r in seed_rows if abs(float(r["epsilon"]) - eps) < 1e-12]
        direct_summary = None
        for method in METHODS:
            rs = [r for r in eps_rows if r["method"] == method]
            row: dict[str, object] = {
                "benchmark": "inventory_service_level",
                "epsilon": f"{eps:.8g}",
                "method": method,
                "n": len(rs),
                "training_samples": TRAIN_SAMPLES,
                "network": f"numpy_tanh_mlp_width_{WIDTH}",
                "train_steps": TRAIN_STEPS,
                "batch": BATCH,
                "learning_rate": f"{LR:.12g}",
                "noise_model": "equal_scale_noise_on_neural_P_or_Z_targets",
                "noise_std": f"{NOISE_STD:.12g}",
            }
            for metric in metrics:
                vals = [float(r[metric]) for r in rs]
                row[metric] = f"{sum(vals)/len(vals):.12g}"
                row[f"{metric}_ci95"] = f"{ci95(vals):.12g}"
            if method == "neural_direct_p_inventory":
                direct_summary = row
            out.append(row)
        if direct_summary:
            direct_w = float(direct_summary["mean_welfare"])
            direct_theta = float(direct_summary["theta_rmse"])
            direct_p = float(direct_summary["p_rmse"])
            for row in out[-len(METHODS):]:
                row["welfare_gap_vs_neural_direct_p"] = f"{float(row['mean_welfare']) - direct_w:.12g}"
                row["theta_rmse_ratio_vs_neural_direct_p"] = f"{float(row['theta_rmse']) / max(direct_theta, 1e-12):.12g}"
                row["p_rmse_ratio_vs_neural_direct_p"] = f"{float(row['p_rmse']) / max(direct_p, 1e-12):.12g}"
                row["claim_status"] = "same_architecture_neural_direct_p" if row["method"] == "neural_direct_p_inventory" else (
                    "oracle_p_reference" if row["method"] == "oracle_p_inventory" else "same_architecture_neural_z_inversion_ill_conditioned"
                )
                row["interpretation"] = "same-architecture trainable neural inventory representation ablation: direct P versus learned Z target with identical MLP/optimizer/evaluation"
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
        for seed in seed_values():
            models = train_models(seed, eps)
            for method in METHODS:
                row: dict[str, object] = {
                    "audit": "same_architecture_neural_inventory_direct_p_vs_learned_z",
                    "epsilon": f"{eps:.8g}",
                    "method": method,
                    "seed": seed,
                    "training_samples": TRAIN_SAMPLES,
                    "noise_std": NOISE_STD,
                    "network": f"numpy_tanh_mlp_width_{WIDTH}",
                }
                row.update({k: v for k, v in models.items() if k.startswith("train_")})
                row.update(simulate(method, eps, seed, models))
                seed_rows.append(row)
    metric_rows = summarize(seed_rows)
    write_csv(DATA / "inventory_neural_direct_p_learned_z_ablation_seed_metrics.csv", seed_rows)
    write_csv(DATA / "inventory_neural_direct_p_learned_z_ablation.csv", metric_rows)
    print(DATA / "inventory_neural_direct_p_learned_z_ablation_seed_metrics.csv")
    print(DATA / "inventory_neural_direct_p_learned_z_ablation.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
