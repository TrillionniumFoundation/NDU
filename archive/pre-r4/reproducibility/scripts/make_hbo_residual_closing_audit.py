#!/usr/bin/env python3
"""Stronger targeted HBO/NBO residual-closing audit for Exp I and inventory.

This script runs longer, residual/terminal-weighted PyTorch-AD HBO/NBO configs for
the two high-gap benchmark families. It does not replace the headline HBO/NBO
suite automatically; it records whether the sampled residual gaps can be
closed while preserving held-out valuation performance.
"""
from __future__ import annotations

import argparse
import csv
import math
import statistics as stats
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch

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
            "seed": "packaged_headline",
            "train_steps": r["iteration"],
            "width": 56,
            "depth": 2,
            "batch": 96,
            "omega": 1.0,
            "terminal_weight": 2.0,
            "actor_hjb_weight": 0.05,
            "actor_lr": 5e-6,
            "critic_lr": 0.0012,
            "native_hjb_loss": r["native_hjb_loss"],
            "residual_rmse": r["residual_rmse"],
            "mean_abs_residual": r["mean_abs_residual"],
            "mean_hamiltonian_abs": r["mean_hamiltonian_abs"],
            "normalized_residual_rmse": r["normalized_residual_rmse_over_one_plus_abs_mean_hamiltonian"],
            "terminal_boundary_loss": r["terminal_boundary_loss"],
            "primary_metric": primary_metric,
            "heldout_value": m[primary_metric],
            "heldout_ci95": 1.96 * float(m[f"{primary_metric}_se"]),
            "certificate_gap_read": "headline_certificate_gap",
            "claim_status": "baseline_high_residual_certificate_gap_visible",
        })
    return out


def run_config(cfg: dict[str, Any]) -> dict[str, Any]:
    spec = cfg["spec"]
    primary_metric = cfg["primary_metric"]
    train_kwargs = {k: cfg[k] for k in [
        "width", "depth", "train_steps", "batch", "omega", "actor_lr", "critic_lr", "terminal_weight", "actor_hjb_weight", "grad_clip", "init_mode"
    ]}
    policy = hbo.train_hbo(spec, seed=cfg["seed"], **train_kwargs)
    diag = policy.diagnostics[-1]
    heldout, ci = eval_many(policy, primary_metric)
    residual_rmse = math.sqrt(float(diag["hjb_loss"]))
    normalized = residual_rmse / (1.0 + abs(float(diag["mean_hamiltonian"])))
    return {
        "experiment": spec.experiment,
        "method": spec.method,
        "audit_config": cfg["label"],
        "seed": cfg["seed"],
        "train_steps": cfg["train_steps"],
        "width": cfg["width"],
        "depth": cfg["depth"],
        "batch": cfg["batch"],
        "omega": cfg["omega"],
        "terminal_weight": cfg["terminal_weight"],
        "actor_hjb_weight": cfg["actor_hjb_weight"],
        "actor_lr": cfg["actor_lr"],
        "critic_lr": cfg["critic_lr"],
        "native_hjb_loss": f"{float(diag['hjb_loss']):.12g}",
        "residual_rmse": f"{residual_rmse:.12g}",
        "mean_abs_residual": f"{float(diag['residual_mean_abs']):.12g}",
        "mean_hamiltonian_abs": f"{abs(float(diag['mean_hamiltonian'])):.12g}",
        "normalized_residual_rmse": f"{normalized:.12g}",
        "terminal_boundary_loss": f"{float(diag['terminal_loss']):.12g}",
        "primary_metric": primary_metric,
        "heldout_value": f"{heldout:.12g}",
        "heldout_ci95": f"{ci:.12g}",
        "mean_action": diag["mean_action"],
        "certificate_gap_read": "stronger_residual_closing_run",
    }


def default_configs() -> list[dict[str, Any]]:
    return [
        {
            "label": "exp1_residual_terminal_balanced_2400",
            "spec": base.exp1_spec("nbo_full_ndu"),
            "primary_metric": "mean_utility",
            "seed": EVAL_BASE_SEED + 41001,
            "width": 72,
            "depth": 2,
            "train_steps": 2400,
            "batch": 192,
            "omega": 6.0,
            "terminal_weight": 12.0,
            "actor_hjb_weight": 0.08,
            "actor_lr": 1e-6,
            "critic_lr": 8e-4,
            "grad_clip": 10.0,
            "init_mode": "safe",
        },
        {
            "label": "exp1_residual_terminal_critic_2400",
            "spec": base.exp1_spec("nbo_full_ndu"),
            "primary_metric": "mean_utility",
            "seed": EVAL_BASE_SEED + 41002,
            "width": 72,
            "depth": 2,
            "train_steps": 2400,
            "batch": 192,
            "omega": 10.0,
            "terminal_weight": 18.0,
            "actor_hjb_weight": 0.0,
            "actor_lr": 0.0,
            "critic_lr": 9e-4,
            "grad_clip": 10.0,
            "init_mode": "safe",
        },
        {
            "label": "inventory_residual_certificate_balanced_2400",
            "spec": base.inv_spec("nbo_full_ndu_inventory"),
            "primary_metric": "mean_welfare",
            "seed": EVAL_BASE_SEED + 42001,
            "width": 80,
            "depth": 2,
            "train_steps": 2400,
            "batch": 192,
            "omega": 16.0,
            "terminal_weight": 32.0,
            "actor_hjb_weight": 0.10,
            "actor_lr": 1e-6,
            "critic_lr": 8e-4,
            "grad_clip": 10.0,
            "init_mode": "safe",
        },
        {
            "label": "inventory_residual_certificate_critic_2400",
            "spec": base.inv_spec("nbo_full_ndu_inventory"),
            "primary_metric": "mean_welfare",
            "seed": EVAL_BASE_SEED + 42002,
            "width": 80,
            "depth": 2,
            "train_steps": 2400,
            "batch": 192,
            "omega": 24.0,
            "terminal_weight": 48.0,
            "actor_hjb_weight": 0.0,
            "actor_lr": 0.0,
            "critic_lr": 8e-4,
            "grad_clip": 10.0,
            "init_mode": "safe",
        },
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--torch-threads", type=int, default=2)
    parser.add_argument("--out", default=str(DATA / "hbo_residual_closing_audit.csv"))
    parser.add_argument("--quick", action="store_true", help="Use tiny train steps for smoke tests only.")
    args = parser.parse_args()
    torch.set_num_threads(max(1, args.torch_threads))
    rows = baseline_rows()
    for cfg in default_configs():
        if args.quick:
            cfg = dict(cfg)
            cfg["train_steps"] = 20
            cfg["batch"] = 32
        print(f"[residual-closing] running {cfg['label']}", flush=True)
        row = run_config(cfg)
        rows.append(row)
        # Update ratios/status after each run and checkpoint to disk.
        by_exp = {r["experiment"]: r for r in rows if r["audit_config"] == "headline_performance_run"}
        for rr in rows:
            base_row = by_exp[rr["experiment"]]
            base_hjb = float(base_row["native_hjb_loss"])
            base_term = float(base_row["terminal_boundary_loss"])
            base_val = float(base_row["heldout_value"])
            rr["hjb_loss_ratio_vs_headline"] = f"{float(rr['native_hjb_loss']) / base_hjb:.12g}"
            rr["terminal_loss_ratio_vs_headline"] = f"{float(rr['terminal_boundary_loss']) / base_term:.12g}"
            rr["heldout_delta_vs_headline"] = f"{float(rr['heldout_value']) - base_val:.12g}"
            if rr["audit_config"] == "headline_performance_run":
                rr["claim_status"] = "baseline_high_residual_certificate_gap_visible"
            elif float(rr["native_hjb_loss"]) < base_hjb and float(rr["terminal_boundary_loss"]) <= 1.25 * base_term:
                rr["claim_status"] = "residual_closed_with_terminal_guardrail"
            elif float(rr["native_hjb_loss"]) < base_hjb:
                rr["claim_status"] = "residual_reduced_with_terminal_tradeoff"
            else:
                rr["claim_status"] = "no_residual_improvement"
        write_csv(Path(args.out), rows)
        print(f"[residual-closing] wrote {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
