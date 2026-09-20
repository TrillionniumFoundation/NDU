import argparse
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent

plt.rcParams.update({
    'font.size': 14.5,
    'axes.titlesize': 18,
    'axes.labelsize': 15,
    'xtick.labelsize': 13,
    'ytick.labelsize': 13,
    'legend.fontsize': 13,
    'figure.dpi': 220,
    'savefig.dpi': 320,
})
ALGO_VARIANT = "algo_fix_joint_search_v7_exp2_backbone_plus_joint"
EXPERIMENT_SEED_COUNT = 30
EXPERIMENT_SEED_STRIDE = 1000


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40, 40)))


def softmax(x, axis=-1):
    z = x - np.max(x, axis=axis, keepdims=True)
    e = np.exp(np.clip(z, -50, 50))
    return e / np.sum(e, axis=axis, keepdims=True)


def max_drawdown(paths):
    peaks = np.maximum.accumulate(paths, axis=1)
    dd = paths / np.maximum(peaks, 1e-12) - 1.0
    return dd.min(axis=1)


def annualized_sharpe(returns, dt):
    mu = returns.mean(axis=1)
    sd = np.maximum(returns.std(axis=1), 1e-3)
    return np.sqrt(1.0 / dt) * mu / sd


def save_figure(fig, stem):
    for ext in ('png', 'pdf', 'eps'):
        fig.savefig(ROOT / f'{stem}.{ext}', bbox_inches='tight', dpi=220)
    plt.close(fig)


@dataclass
class CEMHistory:
    evaluations: list
    best_scores: list
    mean_scores: list


class CEMOptimizer:
    def __init__(self, dim, eval_fn, seed=0, init_scale=0.7):
        self.dim = dim
        self.eval_fn = eval_fn
        self.rng = np.random.default_rng(seed)
        self.mean = np.zeros(dim, dtype=float)
        self.std = np.ones(dim, dtype=float) * init_scale

    def run(self, iterations=10, population=28, elite_frac=0.25, mean_mix=0.85, std_mix=0.70, min_std=0.05):
        elite_n = max(2, int(population * elite_frac))
        best_params = None
        best_score = -1e18
        evaluations = []
        best_scores = []
        mean_scores = []
        total_evals = 0
        for _ in range(iterations):
            samples = self.mean + self.std * self.rng.standard_normal((population, self.dim))
            scores = np.array([self.eval_fn(s) for s in samples], dtype=float)
            total_evals += population
            elite_idx = np.argsort(scores)[-elite_n:]
            elite = samples[elite_idx]
            elite_mean = elite.mean(axis=0)
            elite_std = elite.std(axis=0) + 1e-3
            self.mean = mean_mix * elite_mean + (1.0 - mean_mix) * self.mean
            self.std = np.maximum(std_mix * elite_std + (1.0 - std_mix) * self.std, min_std)
            local_best_idx = int(np.argmax(scores))
            if scores[local_best_idx] > best_score:
                best_score = float(scores[local_best_idx])
                best_params = samples[local_best_idx].copy()
            evaluations.append(total_evals)
            best_scores.append(best_score)
            mean_scores.append(float(scores.mean()))
        return best_params, best_score, CEMHistory(evaluations, best_scores, mean_scores)


def dim_scaled_budget(dim, base_iterations, base_population, ref_dim=6):
    scale = max(1.0, math.sqrt(dim / ref_dim))
    iterations = int(math.ceil(base_iterations * scale))
    population = int(math.ceil(base_population * scale / 2.0) * 2)
    return iterations, population


def search_budget(method, dim, base_iterations, base_population):
    iterations, population = dim_scaled_budget(dim, base_iterations, base_population)
    if method == 'full_ndu_joint':
        iterations = int(math.ceil(1.35 * iterations))
        population = int(math.ceil(1.20 * population / 2.0) * 2)
    return iterations, population


def experiment_seed_values(base_seed, count=EXPERIMENT_SEED_COUNT, stride=EXPERIMENT_SEED_STRIDE):
    return [int(base_seed + stride * (j + 1)) for j in range(count)]


def summarize_metric_records(method, records):
    row = {'method': method}
    keys = list(records[0]['metrics'].keys())
    for key in keys:
        row[key] = float(np.mean([rec['metrics'][key] for rec in records]))
    return row


def per_seed_metric_rows(method, seed_values, records):
    rows = []
    for s, rec in zip(seed_values, records):
        rows.append({'method': method, 'seed': int(s), **rec['metrics']})
    return rows


def concat_path_records(records):
    path_keys = list(records[0]['paths'].keys())
    return {key: np.concatenate([rec['paths'][key] for rec in records], axis=0) for key in path_keys}


def average_histories(histories):
    return CEMHistory(
        evaluations=list(histories[0].evaluations),
        best_scores=np.mean(np.stack([np.asarray(h.best_scores, dtype=float) for h in histories], axis=0), axis=0).tolist(),
        mean_scores=np.mean(np.stack([np.asarray(h.mean_scores, dtype=float) for h in histories], axis=0), axis=0).tolist(),
    )


# =============================
# Experiment I: joint habit-portfolio control
# =============================

def exp1_decode_policy(method, params, features_full, features_orig, W, h):
    if method == 'full_ndu_joint':
        mat = params.reshape(3, features_full.shape[1])
        raw = features_full @ mat.T
        pi = 1.25 * np.tanh(raw[:, 0])
        c_frac = 0.02 + 0.16 * sigmoid(raw[:, 1])
        theta = 0.05 + 0.95 * sigmoid(raw[:, 2])
        c = np.maximum(1e-5, c_frac * np.maximum(W, 1e-4))
        return pi, c, theta
    if method == 'fixed_pref_rl':
        mat = params.reshape(2, features_orig.shape[1])
        raw = features_orig @ mat.T
        pi = 1.25 * np.tanh(raw[:, 0])
        c_frac = 0.02 + 0.16 * sigmoid(raw[:, 1])
        c = np.maximum(1e-5, c_frac * np.maximum(W, 1e-4))
        theta = np.full_like(pi, 0.25)
        return pi, c, theta
    if method == 'augmented_state_rl':
        mat = params.reshape(2, features_full.shape[1])
        raw = features_full @ mat.T
        pi = 1.25 * np.tanh(raw[:, 0])
        c_frac = 0.02 + 0.16 * sigmoid(raw[:, 1])
        c = np.maximum(1e-5, c_frac * np.maximum(W, 1e-4))
        theta = np.full_like(pi, 0.25)
        return pi, c, theta
    if method == 'preference_only':
        w = params[:features_full.shape[1]]
        raw_theta = features_full @ w
        theta = 0.05 + 0.95 * sigmoid(raw_theta)
        surplus_pressure = np.clip(h / np.maximum(W, 1e-4), 0.0, 1.0)
        pi = np.clip(0.75 - 1.2 * surplus_pressure, -0.5, 1.0)
        c = np.maximum(1e-5, (0.045 + 0.03 * (1.0 - surplus_pressure)) * np.maximum(W, 1e-4))
        return pi, c, theta
    raise ValueError(method)


def simulate_exp1(method, params, episodes=96, steps=40, seed=0, record=False):
    rng = np.random.default_rng(seed)
    dt = 1.0 / steps
    shock = steps // 2
    W = np.full(episodes, 1.0)
    h = np.full(episodes, 0.08)
    ruined = np.zeros(episodes, dtype=bool)
    total_reward = np.zeros(episodes)
    mean_surplus_ratio = np.zeros(episodes)
    surplus_counts = np.zeros(episodes)
    theta_paths = []
    pi_paths = []
    W_paths = [W.copy()]
    h_paths = [h.copy()]

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
        dW = (0.02 * W + pi * W * (mu - 0.02) - c) * dt + pi * W * sigma * np.sqrt(dt) * z
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
    surplus_ratio = mean_surplus_ratio / np.maximum(surplus_counts, 1.0)

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
        'surplus_ratio': float(surplus_ratio.mean()),
        'adaptation_lag': float(lag.mean() / steps),
        'wealth_terminal': float(W.mean()),
    }
    payload = {
        'metrics': metrics,
        'paths': {
            'theta': theta_paths,
            'pi': pi_paths,
            'wealth': W_paths,
            'habit': h_paths,
        }
    }
    return payload if record else metrics


def exp1_eval_factory(method, dim, seed):
    def evaluate(params):
        return simulate_exp1(method, params, episodes=72, steps=40, seed=seed, record=False)['mean_utility']
    return evaluate


def run_experiment_1(seed=11):
    specs = {
        'full_ndu_joint': 15,
        'fixed_pref_rl': 6,
        'augmented_state_rl': 10,
        'preference_only': 5,
    }
    rows = []
    raw_rows = []
    traces = {}
    for i, (method, dim) in enumerate(specs.items()):
        seed_values = experiment_seed_values(seed + 10 * i)
        method_records = []
        for method_seed in seed_values:
            opt = CEMOptimizer(dim, exp1_eval_factory(method, dim, method_seed), seed=method_seed)
            iterations, population = search_budget(method, dim, base_iterations=8, base_population=24)
            best, _, _ = opt.run(iterations=iterations, population=population, elite_frac=0.25)
            record = simulate_exp1(method, best, episodes=256, steps=40, seed=method_seed + 500000, record=True)
            method_records.append(record)
        rows.append(summarize_metric_records(method, method_records))
        raw_rows.extend(per_seed_metric_rows(method, seed_values, method_records))
        traces[method] = concat_path_records(method_records)
    df = pd.DataFrame(rows).sort_values('cew', ascending=False).reset_index(drop=True)
    df['reference_gap'] = df['mean_utility'].max() - df['mean_utility']
    df.to_csv(ROOT / 'exp1_metrics.csv', index=False)
    pd.DataFrame(raw_rows).to_csv(ROOT / 'exp1_seed_metrics.csv', index=False)

    methods_plot = ['full_ndu_joint', 'fixed_pref_rl', 'augmented_state_rl']
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.6))
    for m in methods_plot:
        axes[0].plot(traces[m]['wealth'].mean(axis=0), label=m)
        axes[1].plot(traces[m]['habit'].mean(axis=0), label=m)
    axes[0].set_title('Mean wealth path')
    axes[1].set_title('Mean habit path')
    for ax in axes:
        ax.legend(fontsize=13)
        ax.grid(alpha=0.25)
    save_figure(fig, 'fig_exp1_habit_paths')

    fig, axes = plt.subplots(1, 2, figsize=(14, 6.6))
    for m in methods_plot:
        axes[0].plot(traces[m]['theta'].mean(axis=0), label=m)
        surplus = (traces[m]['wealth'][:, 1:] - traces[m]['habit'][:, 1:]).mean(axis=0)
        axes[1].plot(surplus, label=m)
    axes[0].axvline(20, ls='--', c='k', lw=1)
    axes[0].set_title('Mean preference-control path', pad=14)
    axes[1].set_title('Mean wealth-habit surplus', pad=14)
    for ax in axes:
        ax.legend(fontsize=13)
        ax.grid(alpha=0.25)
    save_figure(fig, 'fig_exp1_habit_control')

    fig, ax = plt.subplots(figsize=(8.8, 6.6))
    theta = traces['full_ndu_joint']['theta'].reshape(-1)
    surplus = (traces['full_ndu_joint']['wealth'][:, 1:] - traces['full_ndu_joint']['habit'][:, 1:]).reshape(-1)
    idx = np.random.default_rng(seed).choice(len(theta), size=min(2000, len(theta)), replace=False)
    ax.scatter(np.clip(surplus[idx], -0.5, 1.0), theta[idx], s=12, alpha=0.40)
    ax.set_xlabel('wealth - habit')
    ax.set_ylabel('theta')
    ax.set_title('Mechanism diagnostic: theta vs surplus', pad=14)
    ax.grid(alpha=0.25)
    save_figure(fig, 'fig_app_exp1_mechanism')
    return df


# =============================
# Experiment II: regime uncertainty
# =============================

def exp2_decode(method, params, feat, belief, signal, regime):
    if method == 'full_ndu_joint':
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
    if method == 'fixed_pref_recurrent_rl':
        w_pi = params[:6]
        w_b = params[6:12]
        theta = np.full(feat.shape[0], 0.25)
        pi = 1.35 * np.tanh(feat @ w_pi + 1.0 * (belief - 0.5))
        b_next = sigmoid(feat @ w_b)
        return pi, theta, b_next
    if method == 'oracle_joint_action_rl':
        feat_oracle = feat.copy()
        feat_oracle[:, 3] = regime
        w_pi = params[:6]
        theta = np.full(feat.shape[0], 0.25)
        pi = 1.35 * np.tanh(feat_oracle @ w_pi + 1.1 * (regime - 0.5))
        b_next = regime.astype(float)
        return pi, theta, b_next
    if method == 'preference_only':
        w_theta = params[:6]
        w_b = params[6:12]
        theta = 0.05 + 0.95 * sigmoid(feat @ w_theta)
        b_next = sigmoid(feat @ w_b + 0.25 * theta)
        pi = np.clip(0.95 - 1.8 * b_next, -1.2, 1.2)
        return pi, theta, b_next
    raise ValueError(method)


def simulate_exp2(method, params, episodes=128, steps=48, seed=0, record=False):
    rng = np.random.default_rng(seed)
    dt = 1.0 / steps
    shock = steps // 2
    X = np.full(episodes, 1.0)
    regime = np.zeros(episodes, dtype=int)
    belief = np.full(episodes, 0.15)
    prev_ret = np.zeros(episodes)
    wealth_paths = [X.copy()]
    belief_paths = []
    theta_paths = []
    pi_paths = []
    regime_paths = []
    port_rets = []
    for t in range(steps):
        # hidden regime transition
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
        ret = (0.01 + pi * (mu - 0.01)) * dt + pi * sigma * np.sqrt(dt) * z
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
               - 0.08 * (theta_paths - 0.25) ** 2
               - 0.01 * np.abs(pi_paths)).sum(axis=1)
    dd = max_drawdown(wealth_paths)
    sharpe = annualized_sharpe(port_rets, dt)
    # reaction latency from shock to substantial de-risking
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
    payload = {
        'metrics': metrics,
        'paths': {
            'wealth': wealth_paths,
            'belief': belief_paths,
            'theta': theta_paths,
            'pi': pi_paths,
            'regime': regime_paths,
        }
    }
    return payload if record else metrics


def exp2_eval_factory(method, seed):
    def evaluate(params):
        vals = [
            simulate_exp2(method, params, episodes=88, steps=48, seed=seed + off, record=False)['mean_utility']
            for off in (0, 101, 202, 303)
        ]
        return float(np.mean(vals))
    return evaluate


def run_experiment_2(seed=23):
    specs = {
        'full_ndu_joint': 18,
        'fixed_pref_recurrent_rl': 12,
        'oracle_joint_action_rl': 6,
        'preference_only': 12,
    }
    rows = []
    raw_rows = []
    traces = {}
    for i, (method, dim) in enumerate(specs.items()):
        seed_values = experiment_seed_values(seed + 20 * i)
        method_records = []
        for method_seed in seed_values:
            opt = CEMOptimizer(dim, exp2_eval_factory(method, method_seed), seed=method_seed)
            iterations, population = search_budget(method, dim, base_iterations=12, base_population=30)
            if method == 'full_ndu_joint':
                iterations += 4
                population += 4
            best, _, _ = opt.run(iterations=iterations, population=population, elite_frac=0.25)
            record = simulate_exp2(method, best, episodes=256, steps=48, seed=method_seed + 500000, record=True)
            method_records.append(record)
        rows.append(summarize_metric_records(method, method_records))
        raw_rows.extend(per_seed_metric_rows(method, seed_values, method_records))
        traces[method] = concat_path_records(method_records)
    df = pd.DataFrame(rows).sort_values('cew', ascending=False).reset_index(drop=True)
    df.to_csv(ROOT / 'exp2_metrics.csv', index=False)
    pd.DataFrame(raw_rows).to_csv(ROOT / 'exp2_seed_metrics.csv', index=False)

    methods_plot = ['full_ndu_joint', 'fixed_pref_recurrent_rl', 'oracle_joint_action_rl']
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.6))
    axes[0].plot(traces['full_ndu_joint']['regime'].mean(axis=0), label='true crisis prob', c='k', ls='--')
    for m in methods_plot:
        axes[0].plot(traces[m]['belief'].mean(axis=0), label=m)
    axes[0].set_title('Latent regime vs inferred belief', pad=14)
    for m in methods_plot:
        axes[1].plot(traces[m]['wealth'].mean(axis=0), label=m)
    axes[1].set_title('Mean wealth path', pad=14)
    for ax in axes:
        ax.legend(fontsize=13)
        ax.grid(alpha=0.25)
    save_figure(fig, 'fig_exp2_regime')

    fig, axes = plt.subplots(1, 2, figsize=(14, 6.6))
    for m in methods_plot:
        axes[0].plot(traces[m]['pi'].mean(axis=0), label=m)
    axes[0].set_title('Mean action path', pad=14)
    for m in ['full_ndu_joint', 'preference_only']:
        axes[1].plot(traces[m]['theta'].mean(axis=0), label=m)
    axes[1].set_title('Mean preference-control path', pad=14)
    for ax in axes:
        ax.legend(fontsize=13)
        ax.grid(alpha=0.25)
    save_figure(fig, 'fig_exp2_control')

    fig, ax = plt.subplots(figsize=(8.8, 6.6))
    b = traces['full_ndu_joint']['belief'].reshape(-1)
    r = traces['full_ndu_joint']['regime'].reshape(-1)
    idx = np.random.default_rng(seed).choice(len(b), size=min(2500, len(b)), replace=False)
    ax.scatter(b[idx], r[idx] + 0.04 * np.random.default_rng(seed + 1).standard_normal(idx.size), s=12, alpha=0.40)
    ax.set_xlabel('belief')
    ax.set_ylabel('latent regime')
    ax.set_title('Mechanism diagnostic: belief vs hidden regime', pad=14)
    ax.grid(alpha=0.25)
    save_figure(fig, 'fig_app_exp2_mechanism')
    return df


# =============================
# Experiment III: high-dimensional joint control
# =============================

def exp3_policy(method, params, feat, belief, latent_factor, alphas, betas):
    d = alphas.shape[0]
    if method == 'full_ndu_joint':
        w_theta = params[:6]
        f = params[6:12]
        k = params[12:19]
        theta = 0.05 + 0.95 * sigmoid(feat @ w_theta)
        theta_ctr = theta - 0.25
        alpha_dev = alphas - alphas.mean()
        beta_dev = betas - betas.mean()
        belief_logit = np.log(np.clip(belief, 1e-4, 1.0 - 1e-4) / np.clip(1.0 - belief, 1e-4, 1.0 - 1e-4))
        persist = 0.55 + 0.30 * sigmoid(f[0])
        signal_gain = 0.95 + 0.85 * sigmoid(f[1] + theta_ctr)
        prev_signal_gain = 0.20 * np.tanh(f[2])
        wealth_adj = 0.08 * np.tanh(f[3]) * feat[:, 2]
        bias = 0.25 * np.tanh(f[4])
        cross = (0.20 + 0.35 * sigmoid(f[5])) * theta_ctr * feat[:, 3]
        belief_next = sigmoid(persist * belief_logit + signal_gain * feat[:, 3] + prev_signal_gain * feat[:, 5] + wealth_adj + bias + cross)
        belief_mix = 0.60 * (belief_next - 0.5) + 0.40 * feat[:, 3]
        raw = (k[0] * alpha_dev[None, :]
               + k[1] * beta_dev[None, :] * belief_mix[:, None]
               + k[2] * beta_dev[None, :] * feat[:, 3:4]
               + k[3] * theta_ctr[:, None] * (alpha_dev[None, :] + 0.65 * beta_dev[None, :] * feat[:, 3:4] + 0.45 * beta_dev[None, :] * belief_mix[:, None]))
        raw = raw - raw.mean(axis=1, keepdims=True)
        weights = raw / (np.sum(np.abs(raw), axis=1, keepdims=True) + 1e-8)
        leverage = 1.55 * np.tanh(k[4] + 0.85 * np.tanh(k[5]) * feat[:, 3] + 0.55 * np.tanh(k[6]) * (belief_next - 0.5) + 0.30 * theta_ctr)
        weights = leverage[:, None] * weights
        return weights, theta, belief_next
    if method == 'fixed_pref_joint_rl':
        w_b = params[:6]
        k = params[6:12]
        theta = np.full(feat.shape[0], 0.25)
        belief_next = sigmoid(feat @ w_b)
        raw = (k[0] * alphas[None, :]
               + k[1] * betas[None, :] * (belief[:, None] - 0.5)
               + k[2] * feat[:, 3:4])
        raw = raw - raw.mean(axis=1, keepdims=True)
        weights = raw / (np.sum(np.abs(raw), axis=1, keepdims=True) + 1e-8)
        leverage = 1.35 * np.tanh(k[3] + k[4] * belief + k[5] * feat[:, 3])
        weights = leverage[:, None] * weights
        return weights, theta, belief_next
    if method == 'oracle_factor_joint_rl':
        k = params[:6]
        theta = np.full(feat.shape[0], 0.25)
        belief_next = latent_factor.copy()
        raw = (k[0] * alphas[None, :]
               + k[1] * betas[None, :] * latent_factor[:, None]
               + k[2] * feat[:, 3:4])
        raw = raw - raw.mean(axis=1, keepdims=True)
        weights = raw / (np.sum(np.abs(raw), axis=1, keepdims=True) + 1e-8)
        leverage = 1.35 * np.tanh(k[3] + k[4] * latent_factor + k[5] * feat[:, 3])
        weights = leverage[:, None] * weights
        return weights, theta, belief_next
    if method == 'signal_only_joint_rl':
        k = params[:6]
        theta = np.full(feat.shape[0], 0.25)
        belief_next = belief
        raw = (k[0] * alphas[None, :]
               + k[1] * betas[None, :] * feat[:, 3:4]
               + k[2] * feat[:, 2:3])
        raw = raw - raw.mean(axis=1, keepdims=True)
        weights = raw / (np.sum(np.abs(raw), axis=1, keepdims=True) + 1e-8)
        leverage = 1.30 * np.tanh(k[3] + k[4] * feat[:, 3] + k[5] * feat[:, 2])
        weights = leverage[:, None] * weights
        return weights, theta, belief_next
    raise ValueError(method)


def simulate_exp3(method, params, episodes=128, steps=50, assets=12, seed=0, record=False):
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
    wealth_paths = [W.copy()]
    theta_paths = []
    factor_paths = []
    signal_paths = []
    turnover_paths = []
    port_rets = []
    for t in range(steps):
        factor = 0.92 * factor + 0.18 * rng.standard_normal(episodes)
        signal = prev_signal * 0.4 + factor + 0.25 * rng.standard_normal(episodes)
        feat = np.stack([
            np.ones(episodes),
            np.full(episodes, t / max(1, steps - 1)),
            np.log(W + 1e-6),
            signal,
            belief,
            prev_signal,
        ], axis=1)
        weights, theta, belief = exp3_policy(method, params, feat, belief, factor, alphas, betas)
        eps = rng.standard_normal((episodes, assets))
        asset_rets = (alphas[None, :] * dt
                      + betas[None, :] * factor[:, None] * dt
                      + idio[None, :] * np.sqrt(dt) * eps)
        turnover = np.sum(np.abs(weights - prev_w), axis=1)
        port_ret = np.sum(weights * asset_rets, axis=1) - 0.0025 * turnover
        W = np.maximum(W * np.maximum(1.0 + port_ret, 1e-4), 1e-5)
        prev_w = weights
        prev_signal = signal
        wealth_paths.append(W.copy())
        theta_paths.append(theta.copy())
        factor_paths.append(factor.copy())
        signal_paths.append(signal.copy())
        turnover_paths.append(turnover.copy())
        port_rets.append(port_ret.copy())
    wealth_paths = np.stack(wealth_paths, axis=1)
    theta_paths = np.stack(theta_paths, axis=1)
    factor_paths = np.stack(factor_paths, axis=1)
    signal_paths = np.stack(signal_paths, axis=1)
    turnover_paths = np.stack(turnover_paths, axis=1)
    port_rets = np.stack(port_rets, axis=1)
    utility = ((1.0 + 0.40 * theta_paths) * np.log(np.maximum(1.0 + port_rets, 1e-6))
               - 0.07 * (theta_paths - 0.25) ** 2
               - 0.0015 * turnover_paths).sum(axis=1)
    sharpe = annualized_sharpe(port_rets, dt)
    dd = max_drawdown(wealth_paths)
    metrics = {
        'mean_utility': float(utility.mean()),
        'cew': float(np.exp(utility.mean()) - 1.0),
        'sharpe': float(sharpe.mean()),
        'max_drawdown': float(dd.mean()),
        'turnover': float(turnover_paths.mean()),
        'theta_stability': float(theta_paths.std()),
    }
    payload = {
        'metrics': metrics,
        'paths': {
            'wealth': wealth_paths,
            'theta': theta_paths,
            'factor': factor_paths,
            'signal': signal_paths,
        }
    }
    return payload if record else metrics


def exp3_eval_factory(method, seed):
    def evaluate(params):
        return simulate_exp3(method, params, episodes=96, steps=50, assets=12, seed=seed, record=False)['mean_utility']
    return evaluate


def run_experiment_3(seed=37):
    specs = {
        'full_ndu_joint': 19,
        'fixed_pref_joint_rl': 12,
        'oracle_factor_joint_rl': 6,
        'signal_only_joint_rl': 6,
    }
    rows = []
    raw_rows = []
    traces = {}
    frontier = {}
    for i, (method, dim) in enumerate(specs.items()):
        seed_values = experiment_seed_values(seed + 30 * i)
        method_records = []
        method_histories = []
        for method_seed in seed_values:
            opt = CEMOptimizer(dim, exp3_eval_factory(method, method_seed), seed=method_seed)
            iterations, population = search_budget(method, dim, base_iterations=9, base_population=24)
            best, _, hist = opt.run(iterations=iterations, population=population, elite_frac=0.25)
            record = simulate_exp3(method, best, episodes=256, steps=50, assets=12, seed=method_seed + 500000, record=True)
            method_records.append(record)
            method_histories.append(hist)
        rows.append(summarize_metric_records(method, method_records))
        raw_rows.extend(per_seed_metric_rows(method, seed_values, method_records))
        traces[method] = concat_path_records(method_records)
        frontier[method] = average_histories(method_histories)
    df = pd.DataFrame(rows).sort_values('cew', ascending=False).reset_index(drop=True)
    df.to_csv(ROOT / 'exp3_metrics.csv', index=False)
    pd.DataFrame(raw_rows).to_csv(ROOT / 'exp3_seed_metrics.csv', index=False)
    # shared frontier grid with dimension-scaled budgets
    frontier_frames = []
    for method, hist in frontier.items():
        frontier_frames.append(pd.DataFrame({'evaluations': hist.evaluations, method: hist.best_scores}))
    frontier_df = frontier_frames[0]
    for frame in frontier_frames[1:]:
        frontier_df = frontier_df.merge(frame, on='evaluations', how='outer')
    frontier_df = frontier_df.sort_values('evaluations').ffill()
    frontier_df.to_csv(ROOT / 'exp3_training_frontier.csv', index=False)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6.6))
    axes[0].plot(traces['full_ndu_joint']['factor'].mean(axis=0), label='latent factor', c='k', ls='--')
    axes[0].plot(traces['full_ndu_joint']['theta'].mean(axis=0), label='full_ndu_joint theta')
    axes[0].set_title('Latent factor vs theta', pad=14)
    axes[1].plot(traces['full_ndu_joint']['signal'].mean(axis=0), label='signal')
    axes[1].plot(traces['full_ndu_joint']['wealth'].mean(axis=0), label='wealth')
    axes[1].set_title('Observed signal and wealth', pad=14)
    for ax in axes:
        ax.legend(fontsize=13)
        ax.grid(alpha=0.25)
    save_figure(fig, 'fig_exp3_theta')

    fig, ax = plt.subplots(figsize=(9.4, 6.8))
    for method, hist in frontier.items():
        ax.plot(hist.evaluations, hist.best_scores, label=method)
    ax.set_title('Best utility frontier by evaluations', pad=14)
    ax.set_xlabel('policy evaluations')
    ax.set_ylabel('best score so far')
    ax.legend(fontsize=13)
    ax.grid(alpha=0.25)
    save_figure(fig, 'fig_exp3_cew')
    return df, frontier_df


def write_manifest(exp1_df, exp2_df, exp3_df, exp3_frontier):
    payload = {
        'generated_at_unix': time.time(),
        'algorithm_variant': ALGO_VARIANT,
        'experiment_seed_count': EXPERIMENT_SEED_COUNT,
        'experiment_seed_stride': EXPERIMENT_SEED_STRIDE,
        'optimizer': {
            'name': 'CEM',
            'budget_policy': 'dimension_scaled_plus_full_ndu_bonus',
            'stabilization': {
                'mean_mix': 0.85,
                'std_mix': 0.70,
                'min_std': 0.05,
            },
        },
        'experiments': {
            'exp1_methods': exp1_df['method'].tolist(),
            'exp2_methods': exp2_df['method'].tolist(),
            'exp3_methods': exp3_df['method'].tolist(),
        },
        'files': {
            'metrics': [
                'exp1_metrics.csv', 'exp2_metrics.csv', 'exp3_metrics.csv',
                'exp1_seed_metrics.csv', 'exp2_seed_metrics.csv', 'exp3_seed_metrics.csv',
                'exp3_training_frontier.csv'
            ],
            'figures': [
                'fig_exp1_habit_paths.png', 'fig_exp1_habit_control.png', 'fig_app_exp1_mechanism.png',
                'fig_exp2_regime.png', 'fig_exp2_control.png', 'fig_app_exp2_mechanism.png',
                'fig_exp3_theta.png', 'fig_exp3_cew.png'
            ]
        }
    }
    with open(ROOT / 'ndu_experiment_manifest.json', 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)


def run_all_experiments():
    exp1 = run_experiment_1()
    exp2 = run_experiment_2()
    exp3, frontier = run_experiment_3()
    write_manifest(exp1, exp2, exp3, frontier)
    return exp1, exp2, exp3, frontier


def main():
    parser = argparse.ArgumentParser(description='Generate current NDU experiment figures/metrics into a target folder.')
    parser.add_argument('--outdir', default='.', help='Output directory for figures, CSVs, and manifest (default: current directory).')
    args = parser.parse_args()
    global ROOT
    ROOT = Path(args.outdir).resolve()
    ROOT.mkdir(parents=True, exist_ok=True)
    run_all_experiments()
    print(f'[generate_ndu_experiments] wrote outputs to {ROOT}')


if __name__ == '__main__':
    main()
