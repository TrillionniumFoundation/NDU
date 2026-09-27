#!/usr/bin/env python3
"""Selected Exp III PyTorch-AD HBO/NBO parity-closing audit.

This script reruns the two selected non-oracle, same-architecture/same-budget
Exp III configurations used in the manuscript audit: 1500 and 1800 train steps
with the packaged PyTorch-AD HBO/NBO actor--critic runner.  It intentionally
trains only Full NDU and the fixed-preference joint comparator; privileged
oracle-factor rows are not used for model selection or ranking.
"""
from __future__ import annotations

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


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def mean_se_ci(vals: list[float]) -> tuple[float, float, float]:
    mean = float(np.mean(vals))
    se = float(stats.stdev(vals) / math.sqrt(len(vals))) if len(vals) > 1 else 0.0
    return mean, se, 1.96 * se


def train_pair(train_steps: int, base_seed: int = 20260512) -> dict[str, hbo.HBOPolicy]:
    policies: dict[str, hbo.HBOPolicy] = {}
    for spec in [base.exp3_spec("nbo_full_ndu"), base.exp3_spec("nbo_fixed_pref_joint")]:
        policies[spec.method] = hbo.train_hbo(
            spec,
            seed=base_seed + 20_000,
            width=56,
            depth=2,
            train_steps=train_steps,
            batch=96,
            omega=1.0,
            actor_lr=5e-6,
            critic_lr=1.2e-3,
            terminal_weight=2.0,
            actor_hjb_weight=0.05,
            grad_clip=10.0,
            init_mode="safe",
        )
    return policies


def run_config(label: str, train_steps: int, eval_base_seeds: list[int], heldout_per_block: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    policies = train_pair(train_steps)
    seed_rows: list[dict[str, Any]] = []
    diag_rows: list[dict[str, Any]] = []
    for method, policy in policies.items():
        for r in policy.diagnostics:
            rr = {"config": label, "train_steps": train_steps, **r}
            diag_rows.append(rr)
        for base_seed in eval_base_seeds:
            for j in range(heldout_per_block):
                seed = base_seed + 30_000 + j
                metrics = hbo.eval_policy(policy, seed)
                seed_rows.append({"config": label, "train_steps": train_steps, "method": method, "seed": seed, **metrics})

    out: list[dict[str, Any]] = []
    for method in ["nbo_full_ndu", "nbo_fixed_pref_joint"]:
        mrows = [r for r in seed_rows if r["method"] == method]
        mean, se, ci = mean_se_ci([float(r["mean_utility"]) for r in mrows])
        out.append({
            "config": label,
            "method": method,
            "train_steps": train_steps,
            "seed_count": len(mrows),
            "mean_utility": f"{mean:.12g}",
            "mean_utility_se": f"{se:.12g}",
            "mean_utility_ci95": f"{ci:.12g}",
            "cew": f"{float(np.mean([float(r['cew']) for r in mrows])):.12g}",
            "turnover": f"{float(np.mean([float(r['turnover']) for r in mrows])):.12g}",
            "theta_stability": f"{float(np.mean([float(r['theta_stability']) for r in mrows])):.12g}",
            "wealth_terminal": f"{float(np.mean([float(r['wealth_terminal']) for r in mrows])):.12g}",
            "sharpe": f"{float(np.mean([float(r['sharpe']) for r in mrows])):.12g}",
        })
    full = {r["seed"]: float(r["mean_utility"]) for r in seed_rows if r["method"] == "nbo_full_ndu"}
    fixed = {r["seed"]: float(r["mean_utility"]) for r in seed_rows if r["method"] == "nbo_fixed_pref_joint"}
    paired = [full[s] - fixed[s] for s in sorted(set(full) & set(fixed))]
    mean, se, ci = mean_se_ci(paired)
    final = {(r["method"], int(r["iteration"])): r for r in diag_rows}
    fdiag = final[("nbo_full_ndu", train_steps)]
    cdiag = final[("nbo_fixed_pref_joint", train_steps)]
    out.append({
        "config": label,
        "method": "paired_gap_full_minus_fixed",
        "train_steps": train_steps,
        "seed_count": len(paired),
        "mean_utility": f"{mean:.12g}",
        "mean_utility_se": f"{se:.12g}",
        "mean_utility_ci95": f"{ci:.12g}",
        "ci95_lo": f"{mean-ci:.12g}",
        "ci95_hi": f"{mean+ci:.12g}",
        "full_final_hjb": f"{float(fdiag['hjb_loss']):.12g}",
        "fixed_final_hjb": f"{float(cdiag['hjb_loss']):.12g}",
        "full_final_terminal_loss": f"{float(fdiag['terminal_loss']):.12g}",
        "fixed_final_terminal_loss": f"{float(cdiag['terminal_loss']):.12g}",
        "full_final_mean_action": fdiag["mean_action"],
        "fixed_final_mean_action": cdiag["mean_action"],
        "claim_status": "non_oracle_same_budget_full_beats_fixed" if mean - ci > 0 else "not_significant",
    })
    return seed_rows, out, diag_rows


def main() -> int:
    torch.set_num_threads(2)
    eval_blocks = [20260512, 20270512]
    seed_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    diag_rows: list[dict[str, Any]] = []
    for label, steps in [("recommended_1500", 1500), ("robustness_1800", 1800)]:
        seeds, summary, diag = run_config(label, steps, eval_blocks, 30)
        seed_rows.extend(seeds)
        summary_rows.extend(summary)
        diag_rows.extend(diag)
        write_csv(DATA / "hbo_exp3_parity_closing_seed_metrics.csv", seed_rows)
        write_csv(DATA / "hbo_exp3_parity_closing_audit.csv", summary_rows)
        write_csv(DATA / "hbo_exp3_parity_closing_training_diagnostics.csv", diag_rows)
    print(DATA / "hbo_exp3_parity_closing_audit.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
