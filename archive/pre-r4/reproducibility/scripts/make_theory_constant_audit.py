#!/usr/bin/env python3
"""Generate explicit small-coupling constant audit for the NDU theory section.

The audit is deterministic and illustrates the sufficient fixed-epsilon
Picard contraction bound used in the manuscript. It is not fitted to any
simulation benchmark.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def row(instance: str, *, T: float, epsilon: float, beta_h: float, lam: float,
        theta_max: float, L_b_x: float, L_psi: float, L_g_x: float,
        rho: float) -> dict[str, object]:
    """Return constants for a one-dimensional active NDU toy model.

    Model: du=(-kappa u + beta_h theta)dt + sqrt(2 epsilon)dW^u,
    reward r(x)+eta u - lam theta^2/2, theta in [-theta_max, theta_max].
    The Hamiltonian selector has p-Lipschitz constant beta_h/lam and the
    conservative BSDE z-Lipschitz bound is theta_max*beta_h/sqrt(2 epsilon).
    """
    L_alpha = beta_h / lam
    Lambda_epsilon = beta_h * L_alpha / math.sqrt(2.0 * epsilon)
    L_g_z = theta_max * beta_h / math.sqrt(2.0 * epsilon)
    C_X = T * math.exp(2.0 * L_b_x * T)
    C_B = 2.0 * math.exp((1.0 + 2.0 * rho + L_g_z ** 2) * T)
    q = C_B * C_X * (L_psi ** 2 + T * L_g_x ** 2) * Lambda_epsilon ** 2
    return {
        "instance": instance,
        "T": T,
        "epsilon": epsilon,
        "beta_h": beta_h,
        "lambda": lam,
        "theta_max": theta_max,
        "L_alpha": L_alpha,
        "Lambda_epsilon": Lambda_epsilon,
        "L_b_x": L_b_x,
        "L_g_z": L_g_z,
        "L_psi": L_psi,
        "L_g_x": L_g_x,
        "rho": rho,
        "C_X": C_X,
        "C_B": C_B,
        "q_epsilon": q,
        "condition_holds": int(q < 1.0),
    }


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    rows = [
        row(
            "active_small_coupling",
            T=1.0,
            epsilon=0.5,
            beta_h=0.10,
            lam=2.0,
            theta_max=0.80,
            L_b_x=0.30,
            L_psi=0.40,
            L_g_x=0.25,
            rho=0.10,
        ),
        row(
            "strong_coupling_diagnostic",
            T=1.0,
            epsilon=0.20,
            beta_h=0.80,
            lam=0.50,
            theta_max=1.00,
            L_b_x=0.80,
            L_psi=0.60,
            L_g_x=0.40,
            rho=0.10,
        ),
    ]
    path = DATA / "theory_small_coupling_constants.csv"
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(path)


if __name__ == "__main__":
    main()
