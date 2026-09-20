#!/usr/bin/env python3
"""Targeted HBO/NBO residual-weight and terminal-boundary audit.

The headline HBO/NBO run is performance-oriented.  This script reruns only the
two high-residual families (Exp I and inventory) under residual-focused settings
and reports the residual/performance tradeoff rather than replacing the headline
ranking.
"""
from __future__ import annotations

import csv
import math
import statistics as stats
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import run_hbo_full_experiments as hbo  # noqa: E402
import run_nbo_full_ndu_solver as base  # noqa: E402

SEED_COUNT = 30
EVAL_BASE_SEED = 20260512


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
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


def eval_many(policy: hbo.HBOPolicy, metric: str) -> tuple[float, float]:
    vals = []
    for j in range(SEED_COUNT):
        seed = EVAL_BASE_SEED + 30000 + j + 1
        vals.append(float(hbo.eval_policy(policy, seed)[metric]))
    ci = 1.96 * stats.stdev(vals) / math.sqrt(len(vals)) if len(vals) > 1 else 0.0
    return float(np.mean(vals)), float(ci)


def baseline_rows() -> list[dict[str, Any]]:
    residual = {r["experiment"]: r for r in read_csv(DATA / "hbo_residual_diagnostics.csv")}
    metrics = {(r["experiment"], r["method"]): r for r in read_csv(DATA / "source_nbo_metrics.csv")}
    out: list[dict[str, Any]] = []
    for experiment, method, primary_metric in [
        ("exp1_habit_portfolio", "nbo_full_ndu", "mean_utility"),
        ("inventory_service_level", "nbo_full_ndu_inventory", "mean_welfare"),
    ]:
        r = residual[experiment]
        m = metrics[(experiment, method)]
        out.append({
            "experiment": experiment,
            "method": method,
            "audit_config": "headline_performance_run",
            "train_steps": r["iteration"],
            "width": 56,
            "batch": 96,
            "omega": 1.0,
            "terminal_weight": 2.0,
            "actor_hjb_weight": 0.05,
            "actor_lr": 5e-6,
            "critic_lr": 0.0012,
            "native_hjb_loss": r["native_hjb_loss"],
            "residual_rmse": r["residual_rmse"],
            "normalized_residual_rmse": r["normalized_residual_rmse_over_one_plus_abs_mean_hamiltonian"],
            "terminal_boundary_loss": r["terminal_boundary_loss"],
            "primary_metric": primary_metric,
            "heldout_value": m[primary_metric],
            "heldout_ci95": 1.96 * float(m[f"{primary_metric}_se"]),
            "interpretation": "headline actor-critic run; performance row, not a convergence certificate",
        })
    return out


def run_config(label: str, spec: base.NBOSpec, seed: int, primary_metric: str, **kwargs: Any) -> dict[str, Any]:
    policy = hbo.train_hbo(spec, seed=seed, init_mode="safe", grad_clip=10.0, **kwargs)
    diag = policy.diagnostics[-1]
    val, ci = eval_many(policy, primary_metric)
    return {
        "experiment": spec.experiment,
        "method": spec.method,
        "audit_config": label,
        "train_steps": kwargs["train_steps"],
        "width": kwargs["width"],
        "batch": kwargs["batch"],
        "omega": kwargs["omega"],
        "terminal_weight": kwargs["terminal_weight"],
        "actor_hjb_weight": kwargs["actor_hjb_weight"],
        "actor_lr": kwargs["actor_lr"],
        "critic_lr": kwargs["critic_lr"],
        "native_hjb_loss": f"{float(diag['hjb_loss']):.12g}",
        "residual_rmse": f"{math.sqrt(float(diag['hjb_loss'])):.12g}",
        "normalized_residual_rmse": f"{math.sqrt(float(diag['hjb_loss'])) / (1.0 + abs(float(diag['mean_hamiltonian']))):.12g}",
        "terminal_boundary_loss": f"{float(diag['terminal_loss']):.12g}",
        "primary_metric": primary_metric,
        "heldout_value": f"{val:.12g}",
        "heldout_ci95": f"{ci:.12g}",
        "mean_action": diag["mean_action"],
        "interpretation": "residual-focused rerun; diagnostic tradeoff, not headline replacement",
    }


def main() -> int:
    rows = baseline_rows()
    rows.append(run_config(
        "exp1_residual_only_critic_no_terminal_guardrail",
        base.exp1_spec("nbo_full_ndu"),
        20260512 + 987,
        "mean_utility",
        width=56,
        depth=2,
        train_steps=900,
        batch=128,
        omega=1.0,
        actor_lr=0.0,
        critic_lr=0.0012,
        terminal_weight=0.0,
        actor_hjb_weight=0.0,
    ))
    rows.append(run_config(
        "inventory_residual_balanced_long",
        base.inv_spec("nbo_full_ndu_inventory"),
        20260512 + 30000 + 123,
        "mean_welfare",
        width=64,
        depth=2,
        train_steps=900,
        batch=128,
        omega=8.0,
        actor_lr=2e-6,
        critic_lr=0.0012,
        terminal_weight=15.0,
        actor_hjb_weight=0.05,
    ))
    base_by_exp = {r["experiment"]: r for r in rows if r["audit_config"] == "headline_performance_run"}
    for row in rows:
        base_row = base_by_exp[row["experiment"]]
        base_hjb = float(base_row["native_hjb_loss"])
        base_terminal = float(base_row["terminal_boundary_loss"])
        row["hjb_loss_ratio_vs_headline"] = f"{float(row['native_hjb_loss']) / base_hjb:.12g}"
        row["terminal_loss_ratio_vs_headline"] = f"{float(row['terminal_boundary_loss']) / base_terminal:.12g}"
        if row["audit_config"] == "headline_performance_run":
            row["claim_status"] = "baseline_high_residual_visible"
        elif row["experiment"] == "exp1_habit_portfolio":
            row["claim_status"] = "residual_reduced_but_terminal_boundary_worse"
        else:
            row["claim_status"] = "residual_reduced_with_similar_inventory_welfare"
    write_csv(DATA / "hbo_residual_weight_audit.csv", rows)
    print(DATA / "hbo_residual_weight_audit.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
