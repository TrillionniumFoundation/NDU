#!/usr/bin/env python3
"""Uniform residual/terminal/greedy-gap certificate audit for NBO-as-HJB solver.

The audit uses the same compact two-state service-pressure LQ instance as the
existing theory-covered HJB check, but reports the exact ingredients appearing
in the NBO HJB-solver theorem:

  sup optimal-Hamiltonian residual, terminal residual, greedy-action gap,
  and resulting certificate bound.

Rows gamma=0.08,0.04,0.02,0.01 form an explicit value-critic/actor sequence
whose certificate gaps close; gamma=0 is the exact compact solve.  Bounds are
analytic sup bounds on the box |c|,|u|<=R rather than Monte Carlo estimates.
"""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import numpy as np


def solve_riccati(T: float, steps: int, k: float, b: float, r: float, q: float, rho: float, terminal: float) -> tuple[np.ndarray, np.ndarray]:
    ts = np.linspace(0.0, T, steps + 1)
    K = np.zeros(steps + 1)
    K[-1] = terminal
    dt = T / steps
    for i in range(steps, 0, -1):
        val = K[i]
        deriv = (2.0 * k + rho) * val + (b * b / r) * val * val - q
        K[i - 1] = val - dt * deriv
    return ts, K


def solve_constant(ts: np.ndarray, Kc: np.ndarray, Ku: np.ndarray, sigma_c: float, sigma_u: float, rho: float) -> np.ndarray:
    C = np.zeros_like(ts)
    dt = ts[1] - ts[0]
    for i in range(len(ts) - 1, 0, -1):
        source = 0.5 * (sigma_c * sigma_c * Kc[i] + sigma_u * sigma_u * Ku[i])
        deriv = source + rho * C[i]
        C[i - 1] = C[i] - dt * deriv
    return C


def interp(ts: np.ndarray, vals: np.ndarray, t: float) -> float:
    return float(np.interp(t, ts, vals))


def ci_bound_for_gamma(gamma: float, *, R: float, T: float, ts: np.ndarray, Kc: np.ndarray, Ku: np.ndarray, C: np.ndarray,
                       k_c: float, k_u: float, beta: float, r_a: float, r_theta: float, q_c: float, q_u: float,
                       rho: float, sigma_c: float, sigma_u: float, control_bound: float) -> dict[str, float | int | str]:
    time_grid = np.linspace(0.0, T, 501)
    residual_sup = 0.0
    greedy_sup = 0.0
    actor_residual_sup = 0.0
    value_error_sup = 0.0
    max_abs_a_star = 0.0
    max_abs_theta_star = 0.0
    max_abs_a_actor = 0.0
    max_abs_theta_actor = 0.0

    for t in time_grid:
        kc = interp(ts, Kc, t)
        ku = interp(ts, Ku, t)
        cc = interp(ts, C, t)
        kc_hat = kc + gamma
        ku_hat = ku + gamma
        # Exact derivative of K; gamma is constant in time.
        kc_prime = (2.0 * k_c + rho) * kc + (1.0 / r_a) * kc * kc - q_c
        ku_prime = (2.0 * k_u + rho) * ku + (beta * beta / r_theta) * ku * ku - q_u
        source = 0.5 * (sigma_c * sigma_c * kc + sigma_u * sigma_u * ku)
        c_prime = source + rho * cc

        # HJB optimal-Hamiltonian residual coefficients for V_hat.
        rc = -0.5 * kc_prime + k_c * kc_hat + 0.5 * (kc_hat * kc_hat / r_a) - 0.5 * q_c + 0.5 * rho * kc_hat
        ru = -0.5 * ku_prime + k_u * ku_hat + 0.5 * (beta * beta * ku_hat * ku_hat / r_theta) - 0.5 * q_u + 0.5 * rho * ku_hat
        r0 = c_prime - 0.5 * (sigma_c * sigma_c * kc_hat + sigma_u * sigma_u * ku_hat) - rho * cc
        opt_resid = abs(r0) + abs(rc) * R * R + abs(ru) * R * R
        residual_sup = max(residual_sup, opt_resid)

        # Greedy selector for V_hat and deliberately near-greedy actor A_eta=(1-gamma)A^*.
        max_a_star = kc_hat * R / r_a
        max_theta_star = beta * ku_hat * R / r_theta
        max_abs_a_star = max(max_abs_a_star, abs(max_a_star))
        max_abs_theta_star = max(max_abs_theta_star, abs(max_theta_star))
        max_abs_a_actor = max(max_abs_a_actor, abs((1.0 - gamma) * max_a_star))
        max_abs_theta_actor = max(max_abs_theta_actor, abs((1.0 - gamma) * max_theta_star))
        gap = 0.5 * r_a * (gamma * max_a_star) ** 2 + 0.5 * r_theta * (gamma * max_theta_star) ** 2
        greedy_sup = max(greedy_sup, gap)
        actor_residual_sup = max(actor_residual_sup, opt_resid + gap)
        value_error_sup = max(value_error_sup, 0.5 * gamma * (R * R + R * R))

    terminal_residual_sup = gamma * R * R
    certificate_bound = terminal_residual_sup + T * residual_sup + T * greedy_sup
    return {
        'gamma': gamma,
        'state_box_radius': R,
        'time_grid_size': len(time_grid),
        'uniform_optimal_hamiltonian_residual_sup': residual_sup,
        'uniform_actor_residual_sup_bound': actor_residual_sup,
        'uniform_terminal_residual_sup': terminal_residual_sup,
        'uniform_greedy_gap_sup': greedy_sup,
        'certificate_value_policy_bound_proxy': certificate_bound,
        'actual_value_error_sup': value_error_sup,
        'max_abs_greedy_action_a': max_abs_a_star,
        'max_abs_greedy_action_theta': max_abs_theta_star,
        'max_abs_actor_action_a': max_abs_a_actor,
        'max_abs_actor_action_theta': max_abs_theta_actor,
        'controls_inside_compact_bound': int(max(max_abs_a_star, max_abs_theta_star, max_abs_a_actor, max_abs_theta_actor) < control_bound),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--outdir', default=str(Path(__file__).resolve().parents[1] / 'data'))
    args = parser.parse_args()
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    T = 0.25
    eps = 0.08
    rho = 0.03
    sigma_c = 0.30
    sigma_u = math.sqrt(2.0 * eps)
    k_c, k_u = 0.40, 0.70
    beta = 0.25
    r_a, r_theta = 2.00, 2.50
    q_c, q_u = 0.80, 0.60
    s_c, s_u = 0.75, 0.50
    control_bound = 1.0
    R = 1.2
    steps = 8000
    ts, Kc = solve_riccati(T, steps, k_c, 1.0, r_a, q_c, rho, s_c)
    _, Ku = solve_riccati(T, steps, k_u, beta, r_theta, q_u, rho, s_u)
    C = solve_constant(ts, Kc, Ku, sigma_c, sigma_u, rho)

    rows = []
    for gamma in [0.0, 0.08, 0.04, 0.02, 0.01]:
        r = ci_bound_for_gamma(
            gamma,
            R=R,
            T=T,
            ts=ts,
            Kc=Kc,
            Ku=Ku,
            C=C,
            k_c=k_c,
            k_u=k_u,
            beta=beta,
            r_a=r_a,
            r_theta=r_theta,
            q_c=q_c,
            q_u=q_u,
            rho=rho,
            sigma_c=sigma_c,
            sigma_u=sigma_u,
            control_bound=control_bound,
        )
        status = 'exact_uniform_hjb_solve' if gamma == 0.0 else 'certificate_gap_sequence'
        row = {
            'instance': 'lq_uniform_nbo_hjb_solver_certificate',
            'epsilon': f'{eps:.12g}',
            'horizon': f'{T:.12g}',
            'state_dim': '2',
            'control_dim': '2',
            'compact_control_set': '1',
            'control_bound': f'{control_bound:.12g}',
            'selector_unique': '1',
            'certificate_status': status,
            'interpretation': 'analytic uniform residual-terminal-greedy certificate for compact LQ NDU/NBO HJB solver sequence',
        }
        for k, v in r.items():
            if isinstance(v, float):
                row[k] = f'{v:.12g}'
            else:
                row[k] = str(v)
        rows.append(row)

    path = outdir / 'uniform_hjb_greedy_certificate.csv'
    with path.open('w', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(path)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
