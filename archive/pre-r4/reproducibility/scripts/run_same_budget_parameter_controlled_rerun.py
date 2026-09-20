#!/usr/bin/env python3
"""Full 30-seed same-budget, parameter-controlled CEM rerun.

The main manuscript tables intentionally use heterogeneous policy classes.  This
script creates a second audit layer in which every method in a benchmark uses
(1) the same paired seed schedule, (2) the same trainable parameter count, and
(3) the same CEM evaluation budget, chosen as the original Full-NDU budget for
that benchmark.  It is dependency-light: it reuses the released simulators when
available and writes CSVs with only the Python stdlib plus NumPy.
"""
from __future__ import annotations

import argparse
import csv
import math
import os
import sys
import time
import types
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Callable

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
REPRO_ROOT = SCRIPT_DIR.parent
DATA_DIR = REPRO_ROOT / 'data'


def _install_optional_import_stubs() -> None:
    """Allow importing generate_ndu_experiments without pandas/matplotlib."""
    try:
        import pandas  # noqa: F401
        import matplotlib  # noqa: F401
        return
    except Exception:
        pass

    class _RcParams(dict):
        pass

    matplotlib = types.ModuleType('matplotlib')
    matplotlib.use = lambda *args, **kwargs: None
    pyplot = types.ModuleType('matplotlib.pyplot')
    pyplot.rcParams = _RcParams()
    pyplot.subplots = lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError('plotting disabled in audit script'))
    pyplot.close = lambda *args, **kwargs: None
    pandas = types.ModuleType('pandas')
    sys.modules.setdefault('matplotlib', matplotlib)
    sys.modules.setdefault('matplotlib.pyplot', pyplot)
    sys.modules.setdefault('pandas', pandas)


_install_optional_import_stubs()
sys.path.insert(0, str(SCRIPT_DIR))
import generate_ndu_experiments as g  # noqa: E402


PRIMARY_METRIC = {
    'exp1': 'mean_utility',
    'exp2': 'mean_utility',
    'exp3': 'mean_utility',
}


def _clip01(x: np.ndarray) -> np.ndarray:
    return np.clip(x, 0.0, 1.0)


# ---------------------------------------------------------------------------
# Matched-dimension Experiment I policies
# ---------------------------------------------------------------------------

def exp1_decode_matched(method: str, params: np.ndarray, features_full: np.ndarray, features_orig: np.ndarray, W: np.ndarray, h: np.ndarray):
    if method == 'full_ndu_joint':
        return g.exp1_decode_policy('full_ndu_joint', params, features_full, features_orig, W, h)
    if method == 'same_dim_fixed_orig_rl':
        mat = params.reshape(5, 3)
        raw = features_orig @ mat.T
        pi = 1.15 * np.tanh(raw[:, 0] + 0.35 * np.tanh(raw[:, 2]) + 0.15 * raw[:, 4])
        c_frac = 0.02 + 0.16 * g.sigmoid(raw[:, 1] + 0.30 * np.tanh(raw[:, 3]) - 0.10 * raw[:, 4])
        c = np.maximum(1e-5, c_frac * np.maximum(W, 1e-4))
        theta = np.full_like(pi, 0.25)
        return pi, c, theta
    if method == 'same_dim_augmented_state_rl':
        mat = params.reshape(3, features_full.shape[1])
        raw = features_full @ mat.T
        surplus_pressure = np.clip(h / np.maximum(W, 1e-4), 0.0, 1.0)
        pi = 1.20 * np.tanh(raw[:, 0] - 0.25 * surplus_pressure + 0.20 * np.tanh(raw[:, 2]))
        c_frac = 0.02 + 0.16 * g.sigmoid(raw[:, 1] - 0.25 * surplus_pressure + 0.15 * raw[:, 2])
        c = np.maximum(1e-5, c_frac * np.maximum(W, 1e-4))
        theta = np.full_like(pi, 0.25)
        return pi, c, theta
    if method == 'same_dim_preference_backbone':
        w_theta = params[:5]
        act = params[5:].reshape(2, 5)
        raw = features_full @ act.T
        theta = 0.05 + 0.95 * g.sigmoid(features_full @ w_theta)
        surplus_pressure = np.clip(h / np.maximum(W, 1e-4), 0.0, 1.0)
        pi = np.clip(0.65 - (1.0 + 0.40 * g.sigmoid(raw[:, 0])) * surplus_pressure + 0.25 * np.tanh(raw[:, 1]), -0.6, 1.0)
        c_frac = 0.035 + 0.060 * g.sigmoid(raw[:, 0] - 0.50 * surplus_pressure) + 0.025 * (1.0 - surplus_pressure)
        c = np.maximum(1e-5, c_frac * np.maximum(W, 1e-4))
        return pi, c, theta
    raise ValueError(method)


def simulate_exp1_matched(method: str, params: np.ndarray, episodes: int = 96, steps: int = 40, seed: int = 0, record: bool = False):
    rng = np.random.default_rng(seed)
    dt = 1.0 / steps
    shock = steps // 2
    W = np.full(episodes, 1.0)
    h = np.full(episodes, 0.08)
    ruined = np.zeros(episodes, dtype=bool)
    total_reward = np.zeros(episodes)
    mean_surplus_ratio = np.zeros(episodes)
    surplus_counts = np.zeros(episodes)
    theta_paths, pi_paths, W_paths, h_paths = [], [], [W.copy()], [h.copy()]
    for t in range(steps):
        mu = 0.11 if t < shock else -0.05
        sigma = 0.16 if t < shock else 0.36
        t_norm = np.full(episodes, t / max(1, steps - 1))
        w_norm = np.log(np.maximum(W, 1e-6) + 1.0)
        h_norm = np.log(np.maximum(h, 1e-6) + 1.0)
        surplus_norm = np.clip((W - h) / np.maximum(W, 1e-4), -1.0, 1.0)
        features_full = np.stack([np.ones(episodes), t_norm, w_norm, h_norm, surplus_norm], axis=1)
        features_orig = np.stack([np.ones(episodes), t_norm, w_norm], axis=1)
        pi, c, theta = exp1_decode_matched(method, params, features_full, features_orig, W, h)
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
        ratio = np.maximum(surplus, 0.0) / np.maximum(W, 1e-4)
        mean_surplus_ratio += np.where(ruined, 0.0, ratio)
        surplus_counts += (~ruined).astype(float)
        W = np.where(ruined, np.maximum(W_new, 1e-5), W_new)
        h = np.where(ruined, np.maximum(h_new, 1e-5), h_new)
        theta_paths.append(theta.copy())
        pi_paths.append(pi.copy())
        W_paths.append(W.copy())
        h_paths.append(h.copy())
    total_reward += 0.45 * np.log(np.maximum(W, 1e-5))
    theta_paths = np.stack(theta_paths, axis=1)
    pi_paths = np.stack(pi_paths, axis=1)
    W_paths = np.stack(W_paths, axis=1)
    h_paths = np.stack(h_paths, axis=1)
    pre = theta_paths[:, max(0, shock - 1)]
    lag = np.full(episodes, steps - shock, dtype=float)
    for j in range(episodes):
        idx = np.where(theta_paths[j, shock:] > pre[j] + 0.10)[0]
        if idx.size:
            lag[j] = float(idx[0])
    metrics = {
        'mean_utility': float(total_reward.mean()),
        'cew': float(np.exp(total_reward.mean()) - 1.0),
        'ruin_prob': float(ruined.mean()),
        'surplus_ratio': float((mean_surplus_ratio / np.maximum(surplus_counts, 1.0)).mean()),
        'adaptation_lag': float(lag.mean() / steps),
        'wealth_terminal': float(W.mean()),
    }
    return {'metrics': metrics, 'paths': {}} if record else metrics


# ---------------------------------------------------------------------------
# Matched-dimension Experiment II policies
# ---------------------------------------------------------------------------

def exp2_decode_matched(method: str, params: np.ndarray, feat: np.ndarray, belief: np.ndarray, signal: np.ndarray, regime: np.ndarray):
    if method == 'full_ndu_joint':
        return g.exp2_decode('full_ndu_joint', params, feat, belief, signal, regime)
    if method == 'same_dim_fixed_pref_recurrent_rl':
        w_b = params[:6]
        a = params[6:18]
        theta = np.full(feat.shape[0], 0.25)
        b_next = g.sigmoid(feat @ w_b + 0.18 * np.tanh(a[0]) * signal + 0.10 * np.tanh(a[1]) * feat[:, 5])
        base_slope = 1.20 + 0.70 * g.sigmoid(a[2])
        base_pi = 0.92 - base_slope * b_next
        calm_bonus = 0.16 * g.sigmoid(a[3]) * (0.5 - b_next)
        crisis_tilt = -0.20 * g.sigmoid(a[4]) * (b_next - 0.5)
        reentry = 0.18 * np.tanh(a[5]) * np.maximum(feat[:, 5], 0.0) * (1.0 - b_next)
        wealth_mod = 0.12 * np.tanh(a[6]) * feat[:, 2]
        signal_mod = 0.09 * np.tanh(a[7]) * signal
        trend_mod = 0.08 * np.tanh(a[8]) * feat[:, 1]
        nonlinear = 0.12 * np.tanh(a[9] + a[10] * b_next + a[11] * feat[:, 5])
        pi = np.clip(base_pi + calm_bonus + crisis_tilt + reentry + wealth_mod + signal_mod + trend_mod + nonlinear, 0.0, 1.10)
        return pi, theta, b_next
    if method == 'same_dim_oracle_joint_action_rl':
        theta = np.full(feat.shape[0], 0.25)
        feat_oracle = feat.copy()
        feat_oracle[:, 3] = regime
        mat = params.reshape(3, 6)
        raw = feat_oracle @ mat.T
        b_next = regime.astype(float)
        base_pi = 0.88 - (1.25 + 0.45 * g.sigmoid(raw[:, 0])) * b_next
        calm_bonus = 0.18 * g.sigmoid(raw[:, 1]) * (0.5 - b_next)
        crisis_tilt = -0.20 * g.sigmoid(raw[:, 2]) * (b_next - 0.5)
        pi = np.clip(base_pi + calm_bonus + crisis_tilt + 0.10 * np.tanh(raw[:, 0] - raw[:, 2]), 0.0, 1.10)
        return pi, theta, b_next
    if method == 'same_dim_preference_backbone':
        w_theta = params[:6]
        w_b = params[6:12]
        a = params[12:18]
        theta = 0.05 + 0.95 * g.sigmoid(feat @ w_theta)
        b_next = g.sigmoid(feat @ w_b + 0.25 * theta + 0.10 * np.tanh(a[0]) * signal)
        slope = 1.55 + 0.45 * g.sigmoid(a[1])
        pi = np.clip(0.92 - slope * b_next + 0.16 * np.tanh(a[2]) * (theta - 0.25)
                     + 0.10 * np.tanh(a[3]) * feat[:, 5] + 0.08 * np.tanh(a[4]) * feat[:, 2]
                     + 0.08 * np.tanh(a[5]) * signal, 0.0, 1.10)
        return pi, theta, b_next
    raise ValueError(method)


def simulate_exp2_matched(method: str, params: np.ndarray, episodes: int = 128, steps: int = 48, seed: int = 0, record: bool = False):
    rng = np.random.default_rng(seed)
    dt = 1.0 / steps
    shock = steps // 2
    X = np.full(episodes, 1.0)
    regime = np.zeros(episodes, dtype=int)
    belief = np.full(episodes, 0.15)
    prev_ret = np.zeros(episodes)
    wealth_paths, belief_paths, theta_paths, pi_paths, regime_paths, port_rets = [X.copy()], [], [], [], [], []
    for t in range(steps):
        u = rng.random(episodes)
        if t < shock:
            regime = np.where(regime == 1, (u < 0.92).astype(int), (u < 0.05).astype(int))
        else:
            regime = np.where(regime == 1, (u < 0.95).astype(int), (u < 0.75).astype(int))
        signal = regime + 0.50 * rng.standard_normal(episodes)
        feat = np.stack([np.ones(episodes), np.full(episodes, t / max(1, steps - 1)), np.log(X + 1e-6), signal, belief, prev_ret], axis=1)
        pi, theta, belief = exp2_decode_matched(method, params, feat, belief, signal, regime)
        sigma = np.where(regime == 1, 0.58, 0.18)
        mu = np.where(regime == 1, -0.04, 0.10)
        z = rng.standard_normal(episodes)
        ret = (0.01 + pi * (mu - 0.01)) * dt + pi * sigma * math.sqrt(dt) * z
        X = np.maximum(X * np.maximum(1.0 + ret, 1e-4), 1e-5)
        prev_ret = ret
        wealth_paths.append(X.copy())
        belief_paths.append(belief.copy())
        theta_paths.append(theta.copy())
        pi_paths.append(pi.copy())
        regime_paths.append(regime.copy())
        port_rets.append(ret.copy())
    wealth_paths = np.stack(wealth_paths, axis=1)
    belief_paths = np.stack(belief_paths, axis=1)
    theta_paths = np.stack(theta_paths, axis=1)
    pi_paths = np.stack(pi_paths, axis=1)
    regime_paths = np.stack(regime_paths, axis=1)
    port_rets = np.stack(port_rets, axis=1)
    utility = ((1.0 + 0.55 * theta_paths) * np.log(np.maximum(1.0 + port_rets, 1e-6))
               - 0.08 * (theta_paths - 0.25) ** 2 - 0.01 * np.abs(pi_paths)).sum(axis=1)
    dd = g.max_drawdown(wealth_paths)
    sharpe = g.annualized_sharpe(port_rets, dt)
    pre_pi = pi_paths[:, max(0, shock - 1)]
    lag = np.full(episodes, steps - shock, dtype=float)
    for j in range(episodes):
        idx = np.where(pi_paths[j, shock:] < pre_pi[j] - 0.15)[0]
        if idx.size:
            lag[j] = float(idx[0])
    detect_acc = ((belief_paths > 0.5) == (regime_paths > 0)).mean(axis=1)
    metrics = {
        'mean_utility': float(utility.mean()),
        'cew': float(np.exp(utility.mean()) - 1.0),
        'sharpe': float(sharpe.mean()),
        'max_drawdown': float(dd.mean()),
        'adaptation_lag': float(lag.mean() / steps),
        'regime_detection_acc': float(detect_acc.mean()),
    }
    return {'metrics': metrics, 'paths': {}} if record else metrics


# ---------------------------------------------------------------------------
# Matched-dimension Experiment III policies
# ---------------------------------------------------------------------------

def exp3_policy_matched(method: str, params: np.ndarray, feat: np.ndarray, belief: np.ndarray, latent_factor: np.ndarray, alphas: np.ndarray, betas: np.ndarray):
    if method == 'full_ndu_joint':
        return g.exp3_policy('full_ndu_joint', params, feat, belief, latent_factor, alphas, betas)
    d = alphas.shape[0]
    alpha_dev = alphas - alphas.mean()
    beta_dev = betas - betas.mean()
    if method == 'same_dim_fixed_pref_joint_rl':
        w_b = params[:6]
        k = params[6:19]
        theta = np.full(feat.shape[0], 0.25)
        belief_next = g.sigmoid(feat @ w_b + 0.10 * np.tanh(k[0]) * feat[:, 3] + 0.06 * np.tanh(k[1]) * feat[:, 5])
        belief_mix = 0.55 * (belief_next - 0.5) + 0.45 * feat[:, 3]
        raw = (k[2] * alpha_dev[None, :] + k[3] * beta_dev[None, :] * belief_mix[:, None]
               + k[4] * beta_dev[None, :] * feat[:, 3:4]
               + k[5] * alpha_dev[None, :] * feat[:, 2:3]
               + k[6] * beta_dev[None, :] * feat[:, 5:6])
        raw = raw - raw.mean(axis=1, keepdims=True)
        weights = raw / (np.sum(np.abs(raw), axis=1, keepdims=True) + 1e-8)
        leverage = 1.45 * np.tanh(k[7] + k[8] * belief_next + k[9] * feat[:, 3] + k[10] * feat[:, 2] + k[11] * feat[:, 5] + 0.25 * np.tanh(k[12]))
        return leverage[:, None] * weights, theta, belief_next
    if method == 'same_dim_oracle_factor_joint_rl':
        k = params
        theta = np.full(feat.shape[0], 0.25)
        belief_next = latent_factor.copy()
        raw = (k[0] * alpha_dev[None, :] + k[1] * beta_dev[None, :] * latent_factor[:, None]
               + k[2] * beta_dev[None, :] * feat[:, 3:4] + k[3] * alpha_dev[None, :] * feat[:, 2:3]
               + k[4] * beta_dev[None, :] * feat[:, 5:6] + k[5] * (alpha_dev * beta_dev)[None, :] * latent_factor[:, None])
        raw = raw - raw.mean(axis=1, keepdims=True)
        weights = raw / (np.sum(np.abs(raw), axis=1, keepdims=True) + 1e-8)
        leverage = 1.45 * np.tanh(k[6] + k[7] * latent_factor + k[8] * feat[:, 3] + k[9] * feat[:, 2]
                                  + k[10] * feat[:, 5] + 0.10 * np.tanh(k[11]) + 0.10 * np.tanh(k[12]))
        return leverage[:, None] * weights, theta, belief_next
    if method == 'same_dim_signal_only_joint_rl':
        k = params
        theta = np.full(feat.shape[0], 0.25)
        belief_next = belief
        raw = (k[0] * alpha_dev[None, :] + k[1] * beta_dev[None, :] * feat[:, 3:4]
               + k[2] * alpha_dev[None, :] * feat[:, 2:3] + k[3] * beta_dev[None, :] * feat[:, 5:6]
               + k[4] * (alpha_dev * beta_dev)[None, :] * feat[:, 3:4])
        raw = raw - raw.mean(axis=1, keepdims=True)
        weights = raw / (np.sum(np.abs(raw), axis=1, keepdims=True) + 1e-8)
        leverage = 1.40 * np.tanh(k[5] + k[6] * feat[:, 3] + k[7] * feat[:, 2] + k[8] * feat[:, 5]
                                  + 0.10 * np.tanh(k[9]) + 0.10 * np.tanh(k[10]) + 0.10 * np.tanh(k[11]))
        return leverage[:, None] * weights, theta, belief_next
    raise ValueError(method)


def simulate_exp3_matched(method: str, params: np.ndarray, episodes: int = 128, steps: int = 50, assets: int = 12, seed: int = 0, record: bool = False):
    rng = np.random.default_rng(seed)
    dt = 1.0 / steps
    alphas = np.linspace(0.04, 0.09, assets)
    betas = np.linspace(0.6, 1.6, assets)
    idio = np.linspace(0.10, 0.22, assets)
    W = np.full(episodes, 1.0)
    belief = np.zeros(episodes)
    factor = np.zeros(episodes)
    prev_signal = np.zeros(episodes)
    prev_w = np.zeros((episodes, assets))
    wealth_paths, theta_paths, turnover_paths, port_rets = [W.copy()], [], [], []
    for t in range(steps):
        factor = 0.92 * factor + 0.18 * rng.standard_normal(episodes)
        signal = prev_signal * 0.4 + factor + 0.25 * rng.standard_normal(episodes)
        feat = np.stack([np.ones(episodes), np.full(episodes, t / max(1, steps - 1)), np.log(W + 1e-6), signal, belief, prev_signal], axis=1)
        weights, theta, belief = exp3_policy_matched(method, params, feat, belief, factor, alphas, betas)
        eps = rng.standard_normal((episodes, assets))
        asset_rets = alphas[None, :] * dt + betas[None, :] * factor[:, None] * dt + idio[None, :] * math.sqrt(dt) * eps
        turnover = np.sum(np.abs(weights - prev_w), axis=1)
        port_ret = np.sum(weights * asset_rets, axis=1) - 0.0025 * turnover
        W = np.maximum(W * np.maximum(1.0 + port_ret, 1e-4), 1e-5)
        prev_w = weights
        prev_signal = signal
        wealth_paths.append(W.copy())
        theta_paths.append(theta.copy())
        turnover_paths.append(turnover.copy())
        port_rets.append(port_ret.copy())
    wealth_paths = np.stack(wealth_paths, axis=1)
    theta_paths = np.stack(theta_paths, axis=1)
    turnover_paths = np.stack(turnover_paths, axis=1)
    port_rets = np.stack(port_rets, axis=1)
    utility = ((1.0 + 0.40 * theta_paths) * np.log(np.maximum(1.0 + port_rets, 1e-6))
               - 0.07 * (theta_paths - 0.25) ** 2 - 0.0015 * turnover_paths).sum(axis=1)
    metrics = {
        'mean_utility': float(utility.mean()),
        'cew': float(np.exp(utility.mean()) - 1.0),
        'sharpe': float(g.annualized_sharpe(port_rets, dt).mean()),
        'max_drawdown': float(g.max_drawdown(wealth_paths).mean()),
        'turnover': float(turnover_paths.mean()),
        'theta_stability': float(theta_paths.std()),
    }
    return {'metrics': metrics, 'paths': {}} if record else metrics


EXPERIMENTS = {
    'exp1': {
        'dim': 15,
        'base_seed': 111,
        'iterations': 18,
        'population': 46,
        'methods': ['full_ndu_joint', 'same_dim_fixed_orig_rl', 'same_dim_augmented_state_rl', 'same_dim_preference_backbone'],
        'simulate': simulate_exp1_matched,
        'eval_episodes': 72,
        'report_episodes': 256,
        'steps': 40,
    },
    'exp2': {
        'dim': 18,
        'base_seed': 223,
        'iterations': 33,
        'population': 68,
        'methods': ['full_ndu_joint', 'same_dim_fixed_pref_recurrent_rl', 'same_dim_oracle_joint_action_rl', 'same_dim_preference_backbone'],
        'simulate': simulate_exp2_matched,
        'eval_episodes': 88,
        'report_episodes': 256,
        'steps': 48,
    },
    'exp3': {
        'dim': 19,
        'base_seed': 337,
        'iterations': 23,
        'population': 54,
        'methods': ['full_ndu_joint', 'same_dim_fixed_pref_joint_rl', 'same_dim_oracle_factor_joint_rl', 'same_dim_signal_only_joint_rl'],
        'simulate': simulate_exp3_matched,
        'eval_episodes': 96,
        'report_episodes': 256,
        'steps': 50,
    },
}


def eval_factory(experiment: str, method: str, seed: int) -> Callable[[np.ndarray], float]:
    cfg = EXPERIMENTS[experiment]
    sim = cfg['simulate']
    if experiment == 'exp2':
        def evaluate(params: np.ndarray) -> float:
            vals = [sim(method, params, episodes=cfg['eval_episodes'], steps=cfg['steps'], seed=seed + off, record=False)['mean_utility'] for off in (0, 101, 202, 303)]
            return float(np.mean(vals))
        return evaluate

    def evaluate(params: np.ndarray) -> float:
        return sim(method, params, episodes=cfg['eval_episodes'], steps=cfg['steps'], seed=seed, record=False)['mean_utility']
    return evaluate


def run_one(task: tuple[str, str, int, int]) -> dict:
    experiment, method, seed_index, method_seed = task
    cfg = EXPERIMENTS[experiment]
    dim = cfg['dim']
    iterations = cfg['iterations']
    population = cfg['population']
    opt = g.CEMOptimizer(dim, eval_factory(experiment, method, method_seed), seed=method_seed)
    best, best_score, hist = opt.run(iterations=iterations, population=population, elite_frac=0.25)
    record = cfg['simulate'](method, best, episodes=cfg['report_episodes'], steps=cfg['steps'], seed=method_seed + 500000, record=False)
    row = {
        'experiment': experiment,
        'method': method,
        'seed_index': seed_index,
        'seed': method_seed,
        'param_dim': dim,
        'iterations': iterations,
        'population': population,
        'evaluation_budget': iterations * population,
        'best_in_search_utility': float(best_score),
    }
    row.update({k: float(v) for k, v in record.items()})
    return row


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open('w', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def aggregate(seed_rows: list[dict]) -> tuple[list[dict], list[dict]]:
    meta = {'experiment', 'method', 'seed_index', 'seed', 'param_dim', 'iterations', 'population', 'evaluation_budget'}
    agg_rows = []
    audit_rows = []
    for experiment in sorted({r['experiment'] for r in seed_rows}):
        exp_rows = [r for r in seed_rows if r['experiment'] == experiment]
        metric_cols = sorted(k for k in exp_rows[0] if k not in meta)
        primary = PRIMARY_METRIC[experiment]
        method_means = {}
        for method in sorted({r['method'] for r in exp_rows}):
            rows_m = [r for r in exp_rows if r['method'] == method]
            out = {
                'experiment': experiment,
                'method': method,
                'seed_count': len(rows_m),
                'param_dim': int(rows_m[0]['param_dim']),
                'evaluation_budget': int(rows_m[0]['evaluation_budget']),
            }
            for col in metric_cols:
                vals = np.array([float(r[col]) for r in rows_m], dtype=float)
                out[col] = float(vals.mean())
                out[f'{col}_se'] = float(vals.std(ddof=1) / math.sqrt(len(vals))) if len(vals) > 1 else 0.0
            agg_rows.append(out)
            method_means[method] = out[primary]
        full_value = method_means['full_ndu_joint']
        non_ndu = {m: v for m, v in method_means.items() if m != 'full_ndu_joint'}
        best_non_method, best_non_value = max(non_ndu.items(), key=lambda kv: kv[1])
        leader, leader_value = max(method_means.items(), key=lambda kv: kv[1])
        audit_rows.append({
            'experiment': experiment,
            'primary_metric': primary,
            'seed_count': len({r['seed_index'] for r in exp_rows}),
            'param_dim': EXPERIMENTS[experiment]['dim'],
            'evaluation_budget': EXPERIMENTS[experiment]['iterations'] * EXPERIMENTS[experiment]['population'],
            'leader': leader,
            'leader_value': float(leader_value),
            'full_ndu_value': float(full_value),
            'best_non_ndu_method': best_non_method,
            'best_non_ndu_value': float(best_non_value),
            'full_minus_best_non_ndu': float(full_value - best_non_value),
        })
    return agg_rows, audit_rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--jobs', type=int, default=max(1, min(12, os.cpu_count() or 1)))
    parser.add_argument('--experiments', nargs='*', default=['exp1', 'exp2', 'exp3'], choices=sorted(EXPERIMENTS))
    parser.add_argument('--seeds', type=int, default=30)
    args = parser.parse_args()

    t0 = time.time()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tasks: list[tuple[str, str, int, int]] = []
    for experiment in args.experiments:
        cfg = EXPERIMENTS[experiment]
        seed_values = g.experiment_seed_values(cfg['base_seed'], count=args.seeds)
        for seed_index, method_seed in enumerate(seed_values, start=1):
            for method in cfg['methods']:
                tasks.append((experiment, method, seed_index, method_seed))

    print(f'[same_budget_parameter_controlled] tasks={len(tasks)} jobs={args.jobs}', flush=True)
    rows: list[dict] = []
    done = 0
    with ProcessPoolExecutor(max_workers=args.jobs) as pool:
        future_map = {pool.submit(run_one, task): task for task in tasks}
        for fut in as_completed(future_map):
            task = future_map[fut]
            row = fut.result()
            rows.append(row)
            done += 1
            if done == 1 or done % 10 == 0 or done == len(tasks):
                elapsed = time.time() - t0
                print(f'[same_budget_parameter_controlled] done={done}/{len(tasks)} elapsed={elapsed:.1f}s last={task}', flush=True)
                try:
                    write_csv(DATA_DIR / 'same_budget_parameter_controlled_seed_metrics.partial.csv', rows)
                except Exception as exc:
                    print(f'[same_budget_parameter_controlled] partial-write warning: {exc}', flush=True)

    rows.sort(key=lambda r: (r['experiment'], r['method'], int(r['seed_index'])))
    agg_rows, audit_rows = aggregate(rows)
    write_csv(DATA_DIR / 'same_budget_parameter_controlled_seed_metrics.csv', rows)
    write_csv(DATA_DIR / 'same_budget_parameter_controlled_metrics.csv', agg_rows)
    write_csv(DATA_DIR / 'same_budget_parameter_controlled_audit.csv', audit_rows)
    print('[same_budget_parameter_controlled] audit rows:')
    for row in audit_rows:
        print(row)
    print(f'[same_budget_parameter_controlled] wrote outputs under {DATA_DIR} in {time.time()-t0:.1f}s')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
