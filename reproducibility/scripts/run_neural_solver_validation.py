#!/usr/bin/env python3
"""Small neural shadow-price solver validation for the NDU observability claim.

This script compares two equally sized one-hidden-layer neural estimators on a
solvable preference-state benchmark with analytic shadow price P_u(t,u):
  * direct_p_neural: learns P_u directly;
  * z_inversion_neural: learns Z_u=sqrt(2 eps) P_u and recovers P_u by inversion;
  * exact_hjb_oracle: analytic reference with zero error.

The purpose is not to claim a full high-dimensional FBSDE benchmark.  It is a
30-seed neural validation of the numerical observability mechanism: when the
preference-noise scale eps shrinks, Z-targets become small and inversion
amplifies target noise, while the direct-P parameterization remains stable.
"""
from __future__ import annotations

import argparse
import csv
import math
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
REPRO_ROOT = SCRIPT_DIR.parent
DATA_DIR = REPRO_ROOT / 'data'

EPSILONS = [1e-1, 1e-2, 1e-3, 1e-4]
METHODS = ['exact_hjb_oracle', 'direct_p_neural', 'z_inversion_neural']
SEED_BASE = 911
SEED_STRIDE = 1000


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40, 40)))


def exact_p(t: np.ndarray, u: np.ndarray) -> np.ndarray:
    # Smooth non-flat shadow price from a solvable quadratic value profile.
    b = 0.34 * np.exp(-0.35 * t) + 0.08 * np.sin(2.0 * math.pi * t)
    c = 0.42 + 0.10 * t
    return b - c * u


def exact_value(t: np.ndarray, u: np.ndarray) -> np.ndarray:
    b = 0.34 * np.exp(-0.35 * t) + 0.08 * np.sin(2.0 * math.pi * t)
    c = 0.42 + 0.10 * t
    a = 0.12 * np.cos(math.pi * t)
    return a + b * u - 0.5 * c * u * u


def exact_theta_from_p(p: np.ndarray) -> np.ndarray:
    return np.clip(0.25 + 0.80 * p, 0.05, 1.00)


class TinyTanhNet:
    def __init__(self, rng: np.random.Generator, width: int = 24):
        self.width = width
        self.W1 = 0.35 * rng.standard_normal((2, width))
        self.b1 = np.zeros(width)
        self.W2 = 0.35 * rng.standard_normal(width)
        self.b2 = 0.0
        self.m = {name: np.zeros_like(getattr(self, name)) for name in ['W1', 'b1', 'W2']}
        self.m['b2'] = 0.0
        self.v = {name: np.zeros_like(getattr(self, name)) for name in ['W1', 'b1', 'W2']}
        self.v['b2'] = 0.0
        self.step_count = 0

    def forward(self, X: np.ndarray):
        H_pre = X @ self.W1 + self.b1
        H = np.tanh(H_pre)
        y = H @ self.W2 + self.b2
        return y, H

    def fit(self, X: np.ndarray, y: np.ndarray, *, steps: int = 900, batch: int = 160, lr: float = 0.015, seed: int = 0):
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
            scale = 2.0 / batch
            g_y = scale * err
            grad_W2 = H.T @ g_y
            grad_b2 = float(g_y.sum())
            g_H = g_y[:, None] * self.W2[None, :]
            g_pre = g_H * (1.0 - H * H)
            grad_W1 = xb.T @ g_pre
            grad_b1 = g_pre.sum(axis=0)
            grads = {'W1': grad_W1, 'b1': grad_b1, 'W2': grad_W2, 'b2': grad_b2}
            self.step_count += 1
            for name, grad in grads.items():
                self.m[name] = beta1 * self.m[name] + (1.0 - beta1) * grad
                self.v[name] = beta2 * self.v[name] + (1.0 - beta2) * (grad * grad)
                mhat = self.m[name] / (1.0 - beta1 ** self.step_count)
                vhat = self.v[name] / (1.0 - beta2 ** self.step_count)
                setattr(self, name, getattr(self, name) - lr * mhat / (np.sqrt(vhat) + eps))

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.forward(X)[0]


def make_dataset(seed: int, eps: float, n_train: int = 1536, n_test: int = 4096):
    rng = np.random.default_rng(seed)
    t_train = rng.random(n_train)
    u_train = rng.uniform(-1.4, 1.4, size=n_train)
    t_test = np.linspace(0.0, 1.0, int(math.sqrt(n_test)))
    u_test = np.linspace(-1.4, 1.4, int(math.sqrt(n_test)))
    tt, uu = np.meshgrid(t_test, u_test, indexing='ij')
    X_train = np.stack([2.0 * t_train - 1.0, u_train / 1.4], axis=1)
    X_test = np.stack([2.0 * tt.reshape(-1) - 1.0, uu.reshape(-1) / 1.4], axis=1)
    p_train = exact_p(t_train, u_train)
    p_test = exact_p(tt.reshape(-1), uu.reshape(-1))
    theta_test = exact_theta_from_p(p_test)
    value_test = exact_value(tt.reshape(-1), uu.reshape(-1))
    # Fixed observation noise approximates Monte Carlo/BSDE target noise.  The
    # same absolute target noise is benign for P but amplified by 1/sqrt(eps)
    # when recovering P from Z.
    p_noise = 0.0025 * rng.standard_normal(n_train)
    z_noise = 0.0025 * rng.standard_normal(n_train)
    return X_train, X_test, p_train, p_test, theta_test, value_test, p_noise, z_noise


def run_one(task: tuple[float, str, int, int]) -> dict:
    eps, method, seed_index, seed = task
    X_train, X_test, p_train, p_test, theta_test, value_test, p_noise, z_noise = make_dataset(seed, eps)
    if method == 'exact_hjb_oracle':
        pred_p = p_test.copy()
        pred_theta = theta_test.copy()
        pred_value = value_test.copy()
    else:
        rng = np.random.default_rng(seed + (17 if method == 'direct_p_neural' else 31))
        net = TinyTanhNet(rng, width=24)
        if method == 'direct_p_neural':
            target = p_train + p_noise
            net.fit(X_train, target, steps=900, batch=160, lr=0.012, seed=seed + 101)
            pred_p = net.predict(X_test)
        elif method == 'z_inversion_neural':
            target_z = math.sqrt(2.0 * eps) * p_train + z_noise
            # Use same architecture and optimizer budget as direct-P.
            net.fit(X_train, target_z, steps=900, batch=160, lr=0.012, seed=seed + 202)
            pred_z = net.predict(X_test)
            pred_p = pred_z / math.sqrt(2.0 * eps)
        else:
            raise ValueError(method)
        pred_theta = exact_theta_from_p(pred_p)
        # Integrate predicted P over u to get a value-profile diagnostic up to a
        # time-only constant; use the exact constant at u=0.
        u_scaled = X_test[:, 1] * 1.4
        t = (X_test[:, 0] + 1.0) / 2.0
        b = exact_p(t, np.zeros_like(u_scaled))
        # local quadratic reconstruction from predicted slope; enough for a
        # solver diagnostic, not used as a theorem claim.
        pred_value = exact_value(t, np.zeros_like(u_scaled)) + pred_p * u_scaled - 0.5 * 0.42 * u_scaled * u_scaled

    p_rmse = float(np.sqrt(np.mean((pred_p - p_test) ** 2)))
    theta_rmse = float(np.sqrt(np.mean((pred_theta - theta_test) ** 2)))
    theta_mae = float(np.mean(np.abs(pred_theta - theta_test)))
    value_rmse = float(np.sqrt(np.mean((pred_value - value_test) ** 2)))
    return {
        'epsilon': eps,
        'method': method,
        'seed_index': seed_index,
        'seed': seed,
        'hidden_width': 24 if method != 'exact_hjb_oracle' else 0,
        'train_points': 1536 if method != 'exact_hjb_oracle' else 0,
        'train_steps': 900 if method != 'exact_hjb_oracle' else 0,
        'p_rmse': p_rmse,
        'theta_rmse': theta_rmse,
        'theta_mae': theta_mae,
        'value_profile_rmse': value_rmse,
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open('w', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def aggregate(rows: list[dict]) -> list[dict]:
    out = []
    metric_cols = ['p_rmse', 'theta_rmse', 'theta_mae', 'value_profile_rmse']
    for eps in EPSILONS:
        for method in METHODS:
            subset = [r for r in rows if float(r['epsilon']) == eps and r['method'] == method]
            row = {'epsilon': eps, 'method': method, 'seed_count': len(subset)}
            for col in metric_cols:
                vals = np.array([float(r[col]) for r in subset], dtype=float)
                row[col] = float(vals.mean())
                row[f'{col}_se'] = float(vals.std(ddof=1) / math.sqrt(len(vals))) if len(vals) > 1 else 0.0
            out.append(row)
    # Add ratio rows for the audit headline.
    direct = {(float(r['epsilon']), r['method']): r for r in out}
    for eps in EPSILONS:
        d = direct[(eps, 'direct_p_neural')]
        z = direct[(eps, 'z_inversion_neural')]
        out.append({
            'epsilon': eps,
            'method': 'z_vs_direct_ratio',
            'seed_count': int(d['seed_count']),
            'p_rmse': float(z['p_rmse']) / max(float(d['p_rmse']), 1e-12),
            'theta_rmse': float(z['theta_rmse']) / max(float(d['theta_rmse']), 1e-12),
            'theta_mae': float(z['theta_mae']) / max(float(d['theta_mae']), 1e-12),
            'value_profile_rmse': float(z['value_profile_rmse']) / max(float(d['value_profile_rmse']), 1e-12),
        })
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--jobs', type=int, default=max(1, min(12, os.cpu_count() or 1)))
    parser.add_argument('--seeds', type=int, default=30)
    args = parser.parse_args()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tasks = []
    for eps in EPSILONS:
        for seed_index in range(1, args.seeds + 1):
            seed = SEED_BASE + SEED_STRIDE * seed_index
            for method in METHODS:
                tasks.append((eps, method, seed_index, seed))
    t0 = time.time()
    print(f'[neural_solver_validation] tasks={len(tasks)} jobs={args.jobs}', flush=True)
    rows = []
    done = 0
    with ProcessPoolExecutor(max_workers=args.jobs) as pool:
        futs = {pool.submit(run_one, task): task for task in tasks}
        for fut in as_completed(futs):
            rows.append(fut.result())
            done += 1
            if done == 1 or done % 20 == 0 or done == len(tasks):
                print(f'[neural_solver_validation] done={done}/{len(tasks)} elapsed={time.time()-t0:.1f}s last={futs[fut]}', flush=True)
    rows.sort(key=lambda r: (float(r['epsilon']), r['method'], int(r['seed_index'])))
    metrics = aggregate(rows)
    write_csv(DATA_DIR / 'neural_solver_validation_seed_metrics.csv', rows)
    write_csv(DATA_DIR / 'neural_solver_validation_metrics.csv', metrics)
    print('[neural_solver_validation] headline rows:')
    for r in metrics:
        if r['method'] in {'direct_p_neural', 'z_inversion_neural', 'z_vs_direct_ratio'}:
            print(r)
    print(f'[neural_solver_validation] wrote outputs under {DATA_DIR} in {time.time()-t0:.1f}s')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
