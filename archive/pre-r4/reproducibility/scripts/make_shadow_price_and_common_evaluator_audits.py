#!/usr/bin/env python3
"""Lightweight bridge audits for shadow-price observability and common external metrics.

The shadow-price audit is a small analytic shadow-price sanity check for the
preference-coordinate observability issue: a value-gradient oracle is known on a
one-dimensional preference grid, and recovering the same gradient by inverting
Z_u = sqrt(2 eps) P_u amplifies a fixed volatility-estimation perturbation by
1/sqrt(eps).  It is not a new high-dimensional solver benchmark; it is a direct
numerical diagnostic for the stability mechanism discussed in the theory.

The common-evaluator audit repackages existing held-out benchmark metrics that
do not use each method's endogenous theta as the score: terminal wealth,
portfolio Sharpe/drawdown/turnover, latent-regime Sharpe/drawdown/detection metrics, and inventory cost/service metrics.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def read_rows(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="") as fh:
        return list(csv.DictReader(fh))


def method_row(name: str, method: str) -> dict[str, str]:
    for row in read_rows(name):
        if row["method"] == method:
            return row
    raise KeyError((name, method))


def write_shadow_price_observability() -> None:
    u = np.linspace(-1.0, 1.0, 401)
    k_value = 0.8
    theta_cost = 2.0
    theta_bound = 0.5
    p_oracle = -k_value * u
    theta_oracle = np.clip(p_oracle / theta_cost, -theta_bound, theta_bound)
    deterministic_noise = np.sin(7.0 * u + 0.3)
    z_noise_std = 0.01
    p_noise_std = 0.01
    rows = []
    for eps in [1.0, 0.1, 0.01, 0.001, 0.0001]:
        z_pref = math.sqrt(2.0 * eps) * p_oracle
        z_noisy = z_pref + z_noise_std * deterministic_noise
        p_from_z = z_noisy / math.sqrt(2.0 * eps)
        p_direct = p_oracle + p_noise_std * deterministic_noise
        theta_from_z = np.clip(p_from_z / theta_cost, -theta_bound, theta_bound)
        theta_from_p = np.clip(p_direct / theta_cost, -theta_bound, theta_bound)
        p_analytic_rmse = 0.0
        p_z_rmse = float(np.sqrt(np.mean((p_from_z - p_oracle) ** 2)))
        p_direct_rmse = float(np.sqrt(np.mean((p_direct - p_oracle) ** 2)))
        theta_z_rmse = float(np.sqrt(np.mean((theta_from_z - theta_oracle) ** 2)))
        theta_direct_rmse = float(np.sqrt(np.mean((theta_from_p - theta_oracle) ** 2)))
        rows.append({
            "epsilon": f"{eps:.8g}",
            "preference_z_rms": f"{float(np.sqrt(np.mean(z_pref**2))):.12g}",
            "analytic_p_rmse": f"{p_analytic_rmse:.12g}",
            "z_inversion_p_rmse": f"{p_z_rmse:.12g}",
            "direct_p_rmse": f"{p_direct_rmse:.12g}",
            "z_inversion_theta_rmse": f"{theta_z_rmse:.12g}",
            "direct_p_theta_rmse": f"{theta_direct_rmse:.12g}",
            "z_over_direct_theta_rmse_ratio": f"{theta_z_rmse / max(theta_direct_rmse, 1e-12):.12g}",
        })
    with (DATA / "shadow_price_observability_audit.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def best_non_ndu(rows: list[dict[str, str]], metric: str, lower_is_better: bool, exclude: set[str]) -> tuple[str, float]:
    candidates = [(r["method"], float(r[metric])) for r in rows if r["method"] not in exclude]
    return min(candidates, key=lambda x: x[1]) if lower_is_better else max(candidates, key=lambda x: x[1])


def write_common_external_evaluator() -> None:
    exp1_rows = read_rows("exp1_metrics.csv")
    exp2_rows = read_rows("exp2_metrics.csv")
    exp3_rows = read_rows("exp3_metrics.csv")
    inv_rows = read_rows("inventory_service_level_metrics.csv")
    items = []

    def add(benchmark: str, metric: str, full_method: str, best_method: str, full_value: float, best_value: float, lower: bool, note: str) -> None:
        gap = (best_value - full_value) if lower else (full_value - best_value)
        items.append({
            "benchmark": benchmark,
            "metric": metric,
            "full_ndu_value": f"{full_value:.12g}",
            "best_non_ndu_method": best_method,
            "best_non_ndu_value": f"{best_value:.12g}",
            "full_minus_best_non_ndu_if_higher_better_else_best_minus_full": f"{gap:.12g}",
            "lower_is_better": str(lower).lower(),
            "note": note,
        })

    full_exp1 = method_row("exp1_metrics.csv", "full_ndu_joint")
    method, val = best_non_ndu(exp1_rows, "wealth_terminal", False, {"full_ndu_joint"})
    add("exp1", "wealth_terminal", "full_ndu_joint", method, float(full_exp1["wealth_terminal"]), val, False, "external terminal-wealth metric")

    full_exp2 = method_row("exp2_metrics.csv", "full_ndu_joint")
    for metric, lower, note in [
        ("sharpe", False, "latent-regime realized Sharpe; theta not used directly in evaluator"),
        ("max_drawdown", False, "drawdown closer to zero is better; theta not used directly in evaluator"),
        ("regime_detection_acc", False, "diagnostic filtering accuracy; oracle row is privileged"),
    ]:
        method, val = best_non_ndu(exp2_rows, metric, lower, {"full_ndu_joint", "oracle_joint_action_rl"})
        add("exp2", metric, "full_ndu_joint", method, float(full_exp2[metric]), val, lower, note)

    full_exp3 = method_row("exp3_metrics.csv", "full_ndu_joint")
    for metric, lower, note in [
        ("sharpe", False, "realized return Sharpe; theta not used in evaluator"),
        ("max_drawdown", False, "drawdown closer to zero is better; theta not used in evaluator"),
        ("turnover", True, "portfolio trading turnover; theta not used in evaluator"),
    ]:
        method, val = best_non_ndu(exp3_rows, metric, lower, {"full_ndu_joint"})
        add("exp3", metric, "full_ndu_joint", method, float(full_exp3[metric]), val, lower, note)

    full_inv = method_row("inventory_service_level_metrics.csv", "full_ndu_inventory")
    for metric, lower, note in [
        ("avg_cost", True, "inventory operating cost"),
        ("ending_backlog", True, "inventory ending backlog"),
        ("service_breach_count", True, "periods below service-level target"),
    ]:
        method, val = best_non_ndu(inv_rows, metric, lower, {"full_ndu_inventory"})
        add("inventory", metric, "full_ndu_inventory", method, float(full_inv[metric]), val, lower, note)

    with (DATA / "common_external_evaluator_audit.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(items[0].keys()))
        writer.writeheader()
        writer.writerows(items)


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    write_shadow_price_observability()
    write_common_external_evaluator()
    print(DATA / "shadow_price_observability_audit.csv")
    print(DATA / "common_external_evaluator_audit.csv")


if __name__ == "__main__":
    main()
