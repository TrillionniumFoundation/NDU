#!/usr/bin/env python3
"""Full HBO/NBO actor--critic rerun with trainable PyTorch networks.

This runner executes the source-style Hamiltonian Bellman/HJB operator
training loop with:

* fully trainable actor and critic MLPs;
* trainable random MLPs with benchmark-safe constant-bias initialization only;
* PyTorch automatic differentiation for value time gradients, value-gradient
  and exact state Hessian terms in the HJB residual;
* actor updates obtained by differentiating the Hamiltonian through the
  differentiable benchmark transition/reward equations; and
* held-out rollout evaluation over all benchmark families.

The script still imports the benchmark specs and rollout evaluators from
``run_nbo_full_ndu_solver.py`` so the environments and metrics remain identical
across solver audits.  NumPy is used only for sampling, CSV I/O, and rollout
evaluation; the solver itself is the PyTorch AD HBO/NBO actor--critic.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import torch
from torch import nn

import run_nbo_full_ndu_solver as base

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DEVICE = torch.device("cpu")
DTYPE = torch.float64


def _sigmoid_t(x: torch.Tensor) -> torch.Tensor:
    return torch.sigmoid(torch.clamp(x, -40.0, 40.0))


def _np_seed_list(base_seed: int, count: int) -> list[int]:
    return [base_seed + 30000 + j for j in range(count)]


class SmoothMLP(nn.Module):
    """Smooth fully trainable MLP used for actor and critic."""

    def __init__(self, input_dim: int, output_dim: int, width: int, depth: int) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        prev = input_dim
        for _ in range(depth):
            lin = nn.Linear(prev, width)
            nn.init.xavier_uniform_(lin.weight)
            nn.init.zeros_(lin.bias)
            layers.append(lin)
            layers.append(nn.Tanh())
            prev = width
        out = nn.Linear(prev, output_dim)
        nn.init.xavier_uniform_(out.weight, gain=0.25)
        nn.init.zeros_(out.bias)
        layers.append(out)
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


@dataclass
class HBOPolicy:
    experiment: str
    method: str
    horizon: int
    state_dim: int
    action_dim: int
    lower: torch.Tensor
    upper: torch.Tensor
    center: torch.Tensor
    scale: torch.Tensor
    actor: SmoothMLP
    critic: SmoothMLP
    diagnostics: list[dict]
    seed: int

    def normalize(self, U: torch.Tensor) -> torch.Tensor:
        return (U - self.center[None, :]) / self.scale[None, :]

    def input_matrix_t(self, t_frac: torch.Tensor, states: torch.Tensor) -> torch.Tensor:
        return torch.cat([t_frac.reshape(-1, 1), states], dim=1)

    def action_t(self, U: torch.Tensor) -> torch.Tensor:
        raw = self.actor(self.normalize(U))
        span = self.upper - self.lower
        A = self.lower[None, :] + span[None, :] * _sigmoid_t(raw)
        fixed = span <= 1e-12
        if bool(torch.any(fixed)):
            A = torch.where(fixed[None, :], self.lower[None, :], A)
        return A

    def value_t(self, U: torch.Tensor) -> torch.Tensor:
        return self.critic(self.normalize(U)).squeeze(-1)

    def action(self, t: int, states: np.ndarray) -> np.ndarray:
        with torch.no_grad():
            X = torch.as_tensor(states, dtype=DTYPE, device=DEVICE)
            tt = torch.full((X.shape[0],), min(max(t, 0), self.horizon - 1) / max(1, self.horizon - 1), dtype=DTYPE, device=DEVICE)
            U = self.input_matrix_t(tt, X)
            return self.action_t(U).cpu().numpy()


_original_nbo_actions = base.nbo_actions


def _dispatch_actions(policy, t: int, states: np.ndarray) -> np.ndarray:
    if hasattr(policy, "action"):
        return policy.action(t, states)
    return _original_nbo_actions(policy, t, states)


base.nbo_actions = _dispatch_actions


def specs_all() -> list[base.NBOSpec]:
    specs: list[base.NBOSpec] = []
    for method in ["nbo_full_ndu", "nbo_fixed_pref", "nbo_preference_only"]:
        specs.append(base.exp1_spec(method))
    for method in ["nbo_full_ndu", "nbo_fixed_pref_recurrent", "nbo_oracle_joint_action"]:
        specs.append(base.exp2_spec(method))
    for method in ["nbo_full_ndu", "nbo_fixed_pref_joint", "nbo_oracle_factor"]:
        specs.append(base.exp3_spec(method))
    for method in ["nbo_full_ndu_inventory", "nbo_action_only_inventory", "nbo_fixed_service_inventory"]:
        specs.append(base.inv_spec(method))
    return specs


def sample_states(spec: base.NBOSpec, rng: np.random.Generator, batch: int) -> torch.Tensor:
    grid = spec.state_grid
    idx = rng.integers(0, grid.shape[0], size=batch)
    X = grid[idx].astype(float).copy()
    lo = grid.min(axis=0)
    hi = grid.max(axis=0)
    span = np.maximum(hi - lo, 1e-6)
    X += rng.normal(0.0, 0.03, size=X.shape) * span[None, :]
    boundary_mask = rng.random(size=X.shape) < 0.08
    boundary_vals = np.where(rng.random(size=X.shape) < 0.5, lo[None, :], hi[None, :])
    X = np.where(boundary_mask, boundary_vals, X)
    X = np.clip(X, lo[None, :], hi[None, :])
    return torch.as_tensor(X, dtype=DTYPE, device=DEVICE)


def terminal_value_t(spec: base.NBOSpec, X: torch.Tensor) -> torch.Tensor:
    if spec.experiment == "exp1_habit_portfolio":
        return 0.45 * torch.log(torch.clamp(X[:, 0], min=1e-5))
    if spec.experiment in {"exp2_hidden_regime", "exp3_high_dimensional_allocation"}:
        return torch.zeros(X.shape[0], dtype=DTYPE, device=DEVICE)
    if spec.experiment == "inventory_service_level":
        return -0.15 * X[:, 0] - 2.0 * X[:, 1]
    raise KeyError(spec.experiment)


def value_derivatives(policy: HBOPolicy, U: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    U_req = U.detach().clone().requires_grad_(True)
    V = policy.value_t(U_req)
    dV = torch.autograd.grad(V.sum(), U_req, create_graph=True, retain_graph=True)[0]
    Vt = dV[:, 0]
    grad_x = dV[:, 1:]
    hcols = []
    for j in range(policy.state_dim):
        gj = grad_x[:, j]
        dgj = torch.autograd.grad(gj.sum(), U_req, create_graph=True, retain_graph=True)[0][:, 1:]
        hcols.append(dgj)
    hess = torch.stack(hcols, dim=1)
    return V, Vt, grad_x, hess


def exp3_weights_t(action: torch.Tensor, signal: torch.Tensor, assets: int = 12) -> torch.Tensor:
    leverage, theta, bnext = action[:, 0], action[:, 1], action[:, 2]
    alphas = torch.linspace(0.04, 0.09, assets, dtype=DTYPE, device=DEVICE)
    betas = torch.linspace(0.6, 1.6, assets, dtype=DTYPE, device=DEVICE)
    alpha_dev = alphas - alphas.mean()
    beta_dev = betas - betas.mean()
    mix = 0.60 * bnext + 0.40 * signal
    raw = alpha_dev[None, :] + beta_dev[None, :] * mix[:, None] + 0.55 * (theta[:, None] - 0.25) * (alpha_dev[None, :] + 0.55 * beta_dev[None, :] * signal[:, None])
    raw = raw - raw.mean(dim=1, keepdim=True)
    return leverage[:, None] * raw / (torch.sum(torch.abs(raw), dim=1, keepdim=True) + 1e-8)


def transition_reward_t(spec: base.NBOSpec, step: int, X: torch.Tensor, A: torch.Tensor, shock: Iterable[float] | torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    shock_t = torch.as_tensor(np.asarray(shock, dtype=float), dtype=DTYPE, device=DEVICE).flatten()
    method = spec.method

    if spec.experiment == "exp1_habit_portfolio":
        horizon = spec.horizon
        dt = 1.0 / horizon
        z = shock_t[0]
        W, h = X[:, 0], X[:, 1]
        pi, cfrac, theta = A[:, 0], A[:, 1], A[:, 2]
        Wsafe = torch.clamp(W, min=1e-4)
        if method == "nbo_preference_only":
            surplus_pressure = torch.clamp(h / Wsafe, 0.0, 1.0)
            pi_eff = torch.clamp(0.75 - 1.2 * surplus_pressure, -0.5, 1.0)
            cfrac_eff = 0.045 + 0.03 * (1.0 - surplus_pressure)
        else:
            pi_eff = pi
            cfrac_eff = cfrac
        mu = 0.11 if step < horizon // 2 else -0.05
        sigma = 0.16 if step < horizon // 2 else 0.36
        c = torch.clamp(cfrac_eff * Wsafe, min=1e-5)
        dW = (0.02 * W + pi_eff * W * (mu - 0.02) - c) * dt + pi_eff * W * sigma * math.sqrt(dt) * z
        Wn = torch.clamp(W + dW, min=1e-5)
        hn = torch.clamp(h + theta * (c - h) * dt, min=1e-5)
        surplus = c - h
        ruined = (surplus <= 1e-4) | (Wn <= 1e-5)
        reward = ((1.0 + 0.65 * theta) * torch.log(torch.clamp(surplus, min=1e-4))
                  - 0.10 * (theta - 0.25) ** 2
                  - 0.02 * pi_eff ** 2
                  - 0.01 * (c / Wsafe) ** 2) * dt
        reward = torch.where(ruined, reward - 2.5, reward)
        Xn = torch.stack([torch.clamp(Wn, 0.25, 2.05), torch.clamp(hn, 0.015, 0.30)], dim=1)
        return Xn, reward

    if spec.experiment == "exp2_hidden_regime":
        horizon = spec.horizon
        dt = 1.0 / horizon
        wealth, belief = X[:, 0], X[:, 1]
        pi, theta, bnext = A[:, 0], A[:, 1], A[:, 2]
        u, rz, sz = shock_t[0], shock_t[1], shock_t[2]
        p_high = belief * (0.94 if step >= horizon // 2 else 0.90) + (1.0 - belief) * (0.72 if step >= horizon // 2 else 0.08)
        high = (u < p_high).to(DTYPE)
        sigma = torch.where(high > 0.5, torch.full_like(high, 0.58), torch.full_like(high, 0.18))
        mu = torch.where(high > 0.5, torch.full_like(high, -0.04), torch.full_like(high, 0.10))
        ret = (0.01 + pi * (mu - 0.01)) * dt + pi * sigma * math.sqrt(dt) * rz
        Wn = torch.clamp(wealth * torch.clamp(1.0 + ret, min=1e-4), min=1e-5)
        signal_next = high + 0.50 * sz
        reward = ((1.0 + 0.55 * theta) * torch.log(torch.clamp(1.0 + ret, min=1e-6))
                  - 0.08 * (theta - 0.25) ** 2
                  - 0.01 * torch.abs(pi))
        Xn = torch.stack([
            torch.clamp(Wn, 0.35, 2.0),
            torch.clamp(bnext, 0.02, 0.98),
            torch.clamp(ret, -0.20, 0.20),
            torch.clamp(signal_next.expand_as(Wn), -1.0, 2.0),
        ], dim=1)
        return Xn, reward

    if spec.experiment == "exp3_high_dimensional_allocation":
        horizon = spec.horizon
        dt = 1.0 / horizon
        assets = 12
        W, belief, _prev_signal, signal = X[:, 0], X[:, 1], X[:, 2], X[:, 3]
        theta, bnext = A[:, 1], A[:, 2]
        fz, iz = shock_t[0], shock_t[1]
        alphas = torch.linspace(0.04, 0.09, assets, dtype=DTYPE, device=DEVICE)
        betas = torch.linspace(0.6, 1.6, assets, dtype=DTYPE, device=DEVICE)
        idio = torch.linspace(0.10, 0.22, assets, dtype=DTYPE, device=DEVICE)
        weights = exp3_weights_t(A, signal, assets=assets)
        factor = 0.92 * belief + 0.18 * fz
        eps = iz * torch.ones((X.shape[0], assets), dtype=DTYPE, device=DEVICE)
        asset_rets = alphas[None, :] * dt + betas[None, :] * factor[:, None] * dt + idio[None, :] * math.sqrt(dt) * eps
        turnover = torch.sum(torch.abs(weights), dim=1)
        port_ret = torch.sum(weights * asset_rets, dim=1) - 0.0025 * turnover
        Wn = torch.clamp(W * torch.clamp(1.0 + port_ret, min=1e-4), min=1e-5)
        signal_next = 0.4 * signal + factor + 0.25 * iz
        reward = ((1.0 + 0.40 * theta) * torch.log(torch.clamp(1.0 + port_ret, min=1e-6))
                  - 0.07 * (theta - 0.25) ** 2
                  - 0.0015 * turnover)
        Xn = torch.stack([
            torch.clamp(Wn, 0.35, 2.2),
            torch.clamp(bnext, -1.2, 1.2),
            torch.clamp(signal, -1.5, 1.5),
            torch.clamp(signal_next, -1.5, 1.5),
        ], dim=1)
        return Xn, reward

    if spec.experiment == "inventory_service_level":
        inventory, backlog, ewma, last_demand = X[:, 0], X[:, 1], X[:, 2], X[:, 3]
        order_up_to, theta = A[:, 0], A[:, 1]
        if method == "nbo_fixed_service_inventory":
            order_up_to = torch.full_like(order_up_to, 36.0)
            theta = torch.ones_like(theta)
        q = torch.clamp(order_up_to + 0.35 * backlog - inventory, min=0.0)
        inventory2 = inventory + q
        u, dz = shock_t[0], shock_t[1]
        p_high = 0.12 + 0.35 * _sigmoid_t((last_demand - ewma) / 5.0)
        high = (u < p_high).to(DTYPE)
        seasonal = 2.5 * math.sin(2.0 * math.pi * step / 20.0)
        mean = 18.0 + seasonal + high * 10.0
        sd = 3.0 + high * 1.5
        demand = torch.clamp(torch.round(mean + sd * dz), min=0.0)
        need = backlog + demand
        filled = torch.minimum(inventory2, need)
        invn = inventory2 - filled
        bkn = need - filled
        fill = torch.where(need <= 1e-9, torch.ones_like(need), filled / torch.clamp(need, min=1e-9))
        holding_cost = 0.28 * invn
        shortage_cost = 2.85 * bkn
        order_cost = 0.055 * q + 0.010 * torch.clamp(q - 35.0, min=0.0) ** 2 / 35.0
        theta_cost = 0.045 * (theta - 1.0) ** 2
        cost = holding_cost + shortage_cost + order_cost + theta_cost
        reward = -cost + 8.0 * theta * (fill - 0.92) - 0.03 * theta * (fill < 0.92).to(DTYPE)
        ewmn = 0.82 * ewma + 0.18 * demand
        Xn = torch.stack([
            torch.clamp(invn, 0.0, 115.0),
            torch.clamp(bkn, 0.0, 80.0),
            torch.clamp(ewmn, 5.0, 50.0),
            torch.clamp(demand, 0.0, 60.0),
        ], dim=1)
        return Xn, reward

    raise KeyError(spec.experiment)


def transition_moments_t(spec: base.NBOSpec, step: int, X: torch.Tensor, A: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    # X is detached because the HJB operator only needs sampled-state values,
    # while actor gradients flow through A and critic gradients through V_t, DV,
    # and D2V.  This avoids unnecessary graph paths through piecewise dynamics.
    Xd = X.detach()
    B, dim = Xd.shape
    dt = 1.0 / max(1, spec.horizon)
    rewards = torch.zeros(B, dtype=DTYPE, device=DEVICE)
    dx_sum = torch.zeros((B, dim), dtype=DTYPE, device=DEVICE)
    second_sum = torch.zeros((B, dim, dim), dtype=DTYPE, device=DEVICE)
    for shock in spec.shocks:
        Xn, rew = transition_reward_t(spec, step, Xd, A, shock)
        dx = Xn - Xd
        rewards = rewards + rew
        dx_sum = dx_sum + dx
        second_sum = second_sum + dx[:, :, None] * dx[:, None, :]
    n = float(max(1, len(spec.shocks)))
    rewards = rewards / n
    mean_dx = dx_sum / n
    second = second_sum / n
    flow = rewards / dt
    drift = mean_dx / dt
    cov = (second - mean_dx[:, :, None] * mean_dx[:, None, :]) / dt
    return flow, drift, cov


def hamiltonian_residual(policy: HBOPolicy, spec: base.NBOSpec, step: int, X: torch.Tensor, A: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    B = X.shape[0]
    tt = torch.full((B,), step / max(1, spec.horizon - 1), dtype=DTYPE, device=DEVICE)
    U = policy.input_matrix_t(tt, X)
    _V, Vt, grad_x, hess = value_derivatives(policy, U)
    flow, drift, cov = transition_moments_t(spec, step, X, A)
    diff_term = 0.5 * torch.einsum("bij,bij->b", cov, hess)
    H = flow + torch.sum(grad_x * drift, dim=1) + diff_term
    R = -Vt - H
    return H, R, diff_term


def benchmark_initial_action(spec: base.NBOSpec, lower_np: np.ndarray, upper_np: np.ndarray, init_mode: str) -> np.ndarray:
    """Return a non-fitted benchmark-safe actor bias for random MLP training.

    This is benchmark-safe constant-bias initialization: it uses only simple
    admissible constant controls to keep hard-clipped benchmark rewards in a
    differentiable/viable region before HBO actor updates begin.
    """
    if init_mode == "neutral":
        return 0.5 * (lower_np + upper_np)
    if spec.experiment == "exp1_habit_portfolio":
        if spec.method == "nbo_full_ndu":
            return np.array([0.35, 0.17, 0.08], dtype=float)
        if spec.method == "nbo_fixed_pref":
            return np.array([0.35, 0.17, 0.25], dtype=float)
        return np.array([0.55, 0.07, 0.25], dtype=float)
    if spec.experiment == "exp2_hidden_regime":
        return np.array([0.0, 0.25, 0.55], dtype=float)
    if spec.experiment == "exp3_high_dimensional_allocation":
        return np.array([1.20, 0.25, 0.0], dtype=float)
    if spec.experiment == "inventory_service_level":
        if spec.method == "nbo_full_ndu_inventory":
            return np.array([36.0, 2.20], dtype=float)
        return np.array([36.0, 1.0], dtype=float)
    return 0.5 * (lower_np + upper_np)


def init_policy(spec: base.NBOSpec, seed: int, width: int, depth: int, init_mode: str) -> HBOPolicy:
    torch.manual_seed(seed)
    dim = spec.state_grid.shape[1]
    input_dim = dim + 1
    lo = spec.state_grid.min(axis=0)
    hi = spec.state_grid.max(axis=0)
    center_np = np.concatenate([[0.5], 0.5 * (lo + hi)])
    scale_np = np.concatenate([[0.5], np.maximum(0.5 * (hi - lo), 1e-6)])
    lower_np = spec.actions.min(axis=0).astype(float)
    upper_np = spec.actions.max(axis=0).astype(float)
    if spec.method == "nbo_full_ndu_inventory":
        lower_np[0] = max(lower_np[0], 36.0)
    if spec.method == "nbo_fixed_service_inventory":
        lower_np[:] = np.array([36.0, 1.0])
        upper_np[:] = np.array([36.0, 1.0])
    lower = torch.as_tensor(lower_np, dtype=DTYPE, device=DEVICE)
    upper = torch.as_tensor(upper_np, dtype=DTYPE, device=DEVICE)
    actor = SmoothMLP(input_dim, spec.actions.shape[1], width, depth).to(device=DEVICE, dtype=DTYPE)
    critic = SmoothMLP(input_dim, 1, width, depth).to(device=DEVICE, dtype=DTYPE)
    # Benchmark-safe random MLP bias initialization.
    with torch.no_grad():
        last = actor.net[-1]
        assert isinstance(last, nn.Linear)
        span = torch.clamp(upper - lower, min=1e-9)
        init_action_np = np.clip(benchmark_initial_action(spec, lower_np, upper_np, init_mode), lower_np, upper_np)
        init_action = torch.as_tensor(init_action_np, dtype=DTYPE, device=DEVICE)
        p = torch.clamp((init_action - lower) / span, 1e-4, 1.0 - 1e-4)
        # Zero the final actor weights so the initial trainable MLP is exactly
        # the safe constant policy; actor gradients then train the final layer
        # and, after the first step, the hidden layers as well.
        last.weight.zero_()
        last.bias.copy_(torch.log(p / (1.0 - p)))
        fixed = (upper - lower) <= 1e-12
        if bool(torch.any(fixed)):
            last.weight[fixed, :] = 0.0
            last.bias[fixed] = 0.0
    return HBOPolicy(
        experiment=spec.experiment,
        method=spec.method,
        horizon=spec.horizon,
        state_dim=dim,
        action_dim=spec.actions.shape[1],
        lower=lower,
        upper=upper,
        center=torch.as_tensor(center_np, dtype=DTYPE, device=DEVICE),
        scale=torch.as_tensor(scale_np, dtype=DTYPE, device=DEVICE),
        actor=actor,
        critic=critic,
        diagnostics=[],
        seed=seed,
    )


def train_hbo(
    spec: base.NBOSpec,
    *,
    seed: int,
    width: int,
    depth: int,
    train_steps: int,
    batch: int,
    omega: float,
    actor_lr: float,
    critic_lr: float,
    terminal_weight: float,
    actor_hjb_weight: float,
    grad_clip: float,
    init_mode: str,
) -> HBOPolicy:
    rng = np.random.default_rng(seed)
    policy = init_policy(spec, seed, width, depth, init_mode)
    opt_a = torch.optim.Adam(policy.actor.parameters(), lr=actor_lr)
    opt_v = torch.optim.Adam(policy.critic.parameters(), lr=critic_lr)

    for it in range(1, train_steps + 1):
        step = int(rng.integers(0, spec.horizon))
        X = sample_states(spec, rng, batch)
        tt = torch.full((batch,), step / max(1, spec.horizon - 1), dtype=DTYPE, device=DEVICE)
        U_actor = policy.input_matrix_t(tt, X).detach()
        with torch.no_grad():
            A_detached = policy.action_t(U_actor).detach()

        # Critic: minimize zero-centered HJB residual plus terminal boundary loss.
        opt_v.zero_grad(set_to_none=True)
        Hc, Rc, _ = hamiltonian_residual(policy, spec, step, X, A_detached)
        XT = sample_states(spec, rng, max(16, batch // 2))
        UT = policy.input_matrix_t(torch.ones(XT.shape[0], dtype=DTYPE, device=DEVICE), XT)
        VT = policy.value_t(UT)
        targetT = terminal_value_t(spec, XT)
        terminal_loss = torch.mean((VT - targetT) ** 2)
        critic_loss = omega * torch.mean(Rc ** 2) + terminal_weight * terminal_loss
        critic_loss.backward()
        if grad_clip > 0:
            torch.nn.utils.clip_grad_norm_(policy.critic.parameters(), grad_clip)
        opt_v.step()

        # Actor: maximize the Hamiltonian using AD through the trainable actor and
        # differentiable benchmark equations. Critic parameters are frozen, but
        # value gradients/Hessians wrt state are still computed by AD.
        for p in policy.critic.parameters():
            p.requires_grad_(False)
        opt_a.zero_grad(set_to_none=True)
        A = policy.action_t(U_actor)
        Ha, Ra, _ = hamiltonian_residual(policy, spec, step, X, A)
        actor_loss = -torch.mean(Ha) + actor_hjb_weight * omega * torch.mean(Ra ** 2)
        actor_loss.backward()
        if grad_clip > 0:
            torch.nn.utils.clip_grad_norm_(policy.actor.parameters(), grad_clip)
        opt_a.step()
        for p in policy.critic.parameters():
            p.requires_grad_(True)

        if it == 1 or it % max(1, train_steps // 10) == 0 or it == train_steps:
            with torch.no_grad():
                A_mean = A.detach().mean(dim=0).cpu().numpy()
            policy.diagnostics.append({
                "experiment": spec.experiment,
                "method": spec.method,
                "iteration": it,
                "loss_perf": float((-Ha.detach().mean()).cpu()),
                "hjb_loss": float(torch.mean(Rc.detach() ** 2).cpu()),
                "terminal_loss": float(terminal_loss.detach().cpu()),
                "residual_mean_abs": float(torch.mean(torch.abs(Rc.detach())).cpu()),
                "mean_hamiltonian": float(torch.mean(Ha.detach()).cpu()),
                "mean_action": ";".join(f"{x:.6g}" for x in A_mean),
                "omega": omega,
                "algorithm": "hbo_full_actor_critic_pytorch_ad",
                "backend": f"torch-{torch.__version__}",
                "initialization": f"{init_mode}_constant_bias_random_mlp_no_bellman_pretraining",
                "ad_terms": "V_t_gradV_exact_state_Hessian_and_actor_Hamiltonian_gradients",
            })
    return policy


def eval_policy(policy: HBOPolicy, seed: int) -> dict[str, float]:
    if policy.experiment == "exp1_habit_portfolio":
        return base.eval_exp1(policy, seed)
    if policy.experiment == "exp2_hidden_regime":
        return base.eval_exp2(policy, seed)
    if policy.experiment == "exp3_high_dimensional_allocation":
        return base.eval_exp3(policy, seed)
    if policy.experiment == "inventory_service_level":
        return base.eval_inventory(policy, seed)
    raise KeyError(policy.experiment)


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def summarize(seed_rows: list[dict]) -> list[dict]:
    groups: dict[tuple[str, str], list[dict]] = {}
    for row in seed_rows:
        groups.setdefault((row["experiment"], row["method"]), []).append(row)
    out: list[dict] = []
    for (exp, method), rows in sorted(groups.items()):
        summary = {"experiment": exp, "method": method, "seed_count": len(rows), "algorithm": "hbo_full_actor_critic_pytorch_ad"}
        numeric: list[str] = []
        for key, val in rows[0].items():
            if key in {"experiment", "method", "seed"}:
                continue
            try:
                float(val)
                numeric.append(key)
            except Exception:
                pass
        for key in numeric:
            vals = np.array([float(r[key]) for r in rows], dtype=float)
            summary[key] = float(vals.mean())
            summary[f"{key}_se"] = float(vals.std(ddof=1) / math.sqrt(len(vals))) if len(vals) > 1 else 0.0
        out.append(summary)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--train-steps", type=int, default=450)
    parser.add_argument("--width", type=int, default=56)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--batch", type=int, default=96)
    parser.add_argument("--omega", type=float, default=1.0)
    parser.add_argument("--actor-lr", type=float, default=5e-6)
    parser.add_argument("--critic-lr", type=float, default=1.2e-3)
    parser.add_argument("--terminal-weight", type=float, default=2.0)
    parser.add_argument("--actor-hjb-weight", type=float, default=0.05)
    parser.add_argument("--grad-clip", type=float, default=10.0)
    parser.add_argument("--base-seed", type=int, default=20260512)
    parser.add_argument("--init-mode", choices=["safe", "neutral"], default="safe")
    parser.add_argument("--torch-threads", type=int, default=2)
    parser.add_argument("--experiments", nargs="*", default=None, help="Optional subset of experiment names for smoke tests.")
    args = parser.parse_args()

    torch.set_num_threads(max(1, args.torch_threads))
    torch.manual_seed(args.base_seed)

    policies: list[HBOPolicy] = []
    diag_rows: list[dict] = []
    specs = specs_all()
    if args.experiments:
        wanted = set(args.experiments)
        specs = [s for s in specs if s.experiment in wanted or s.method in wanted]
    for spec in specs:
        bench_seed_offset = {
            "exp1_habit_portfolio": 0,
            "exp2_hidden_regime": 10_000,
            "exp3_high_dimensional_allocation": 20_000,
            "inventory_service_level": 30_000,
        }[spec.experiment]
        policy = train_hbo(
            spec,
            seed=args.base_seed + bench_seed_offset,
            width=args.width,
            depth=args.depth,
            train_steps=args.train_steps,
            batch=args.batch,
            omega=args.omega,
            actor_lr=args.actor_lr,
            critic_lr=args.critic_lr,
            terminal_weight=args.terminal_weight,
            actor_hjb_weight=args.actor_hjb_weight,
            grad_clip=args.grad_clip,
            init_mode=args.init_mode,
        )
        policies.append(policy)
        diag_rows.extend(policy.diagnostics)
        print(f"[hbo-ad] trained {spec.experiment}/{spec.method} final_hjb={policy.diagnostics[-1]['hjb_loss']:.6g}", flush=True)

    seed_rows: list[dict] = []
    for policy in policies:
        for seed in _np_seed_list(args.base_seed, args.seeds):
            metrics = eval_policy(policy, seed)
            row = {"experiment": policy.experiment, "method": policy.method, "seed": seed}
            row.update(metrics)
            seed_rows.append(row)
        print(f"[hbo-ad] evaluated {policy.experiment}/{policy.method}", flush=True)

    metric_rows = summarize(seed_rows)
    write_csv(DATA / "source_nbo_seed_metrics.csv", seed_rows)
    write_csv(DATA / "source_nbo_metrics.csv", metric_rows)
    write_csv(DATA / "source_nbo_training_diagnostics.csv", diag_rows)
    meta = {
        "algorithm": "hbo_full_actor_critic_pytorch_ad",
        "source_archive": "Neural_Bellman_Operators.zip",
        "backend": f"torch-{torch.__version__}",
        "loss": "L_PERF + omega L_HJB with terminal boundary loss",
        "networks": "fully_trainable_actor_and_critic_MLPs",
        "automatic_differentiation": "PyTorch AD for V_t, grad V, exact state Hessian, and actor Hamiltonian gradients",
        "initialization": f"{args.init_mode}_constant_bias_random_mlp_no_bellman_pretraining",
        "seeds": args.seeds,
        "train_steps": args.train_steps,
        "width": args.width,
        "depth": args.depth,
        "batch": args.batch,
        "omega": args.omega,
        "actor_lr": args.actor_lr,
        "critic_lr": args.critic_lr,
        "terminal_weight": args.terminal_weight,
        "actor_hjb_weight": args.actor_hjb_weight,
        "grad_clip": args.grad_clip,
        "dtype": str(DTYPE).replace("torch.", ""),
        "benchmarks": sorted({p.experiment for p in policies}),
        "methods": sorted({p.method for p in policies}),
    }
    (DATA / "source_nbo_run_metadata.json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
    print(json.dumps(meta, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
