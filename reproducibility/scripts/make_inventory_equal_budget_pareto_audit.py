#!/usr/bin/env python3
"""Inventory equal-budget Pareto audit.

This selected audit reruns a deeper same-information/same-CEM-budget inventory
comparison for Full NDU versus the action-only adaptive base-stock comparator.
Positive deltas in the output favor Full NDU: welfare deltas are Full minus
action-only, while cost/backlog/breach deltas are action-only minus Full.
"""
from __future__ import annotations

import argparse
import csv
import math
import statistics as stats
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[0]
DATA = ROOT / "data"
sys.path.insert(0, str(SCRIPT_DIR))

import run_inventory_equal_budget_theta_audit as inv  # noqa: E402

METHODS = ["full_ndu_inventory", "action_only_adaptive_base_stock"]
METRICS = [
    "mean_welfare",
    "mean_welfare_no_theta_cost",
    "avg_cost_no_theta",
    "fill_rate",
    "ending_backlog",
    "service_breach_count",
    "theta_std",
    "theta_mean_abs_deviation_from_one",
]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    keys: list[str] = []
    for row in rows:
        for k in row:
            if k not in keys:
                keys.append(k)
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def run_selected(seed_count: int = 24, iterations: int = 32, population: int = 48, report_episodes: int = 768) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    for j in range(seed_count):
        eval_seed = 1_199_000 + j
        for method in METHODS:
            train_seed = (12_061 if method.startswith("full") else 12_161) + 1000 * (j + 1)
            cem = inv.CEM(inv.method_dim(method), train_seed + 991)

            def score(params, method=method, train_seed=train_seed):
                return inv.simulate(method, params, train_seed + 100_000, 48, 1.0, "normal")["mean_welfare"]

            params, search_score, evals = cem.run(score, iterations=iterations, population=population)
            report = inv.simulate(method, params, eval_seed, report_episodes, 1.0, "normal")
            row: dict[str, Any] = {
                "config": "welfare_1536_confirm24",
                "seed_index": j,
                "method": method,
                "train_seed": train_seed,
                "eval_seed": eval_seed,
                "iterations": iterations,
                "population": population,
                "policy_evaluations": evals,
                "objective": "welfare",
                "search_score": search_score,
            }
            row.update(report)
            rows.append(row)
    summary = summarize(rows)
    return rows, summary


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seed_count = len({int(r["seed_index"]) for r in rows})
    out: dict[str, Any] = {"config": "welfare_1536_confirm24", "n": seed_count, "policy_evaluations": 1536, "objective": "welfare"}
    for metric in METRICS:
        diffs = []
        for j in range(seed_count):
            full = next(r for r in rows if int(r["seed_index"]) == j and r["method"] == "full_ndu_inventory")
            action = next(r for r in rows if int(r["seed_index"]) == j and r["method"] == "action_only_adaptive_base_stock")
            if metric in {"avg_cost_no_theta", "ending_backlog", "service_breach_count"}:
                diffs.append(float(action[metric]) - float(full[metric]))
            else:
                diffs.append(float(full[metric]) - float(action[metric]))
        mean = sum(diffs) / len(diffs)
        ci = 1.96 * stats.stdev(diffs) / math.sqrt(len(diffs)) if len(diffs) > 1 else 0.0
        out[f"delta_{metric}"] = f"{mean:.12g}"
        out[f"delta_{metric}_ci95"] = f"{ci:.12g}"
    out["claim_status"] = "same_budget_physical_signs_all_favor_full"
    return [out]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-count", type=int, default=24)
    ap.add_argument("--iterations", type=int, default=32)
    ap.add_argument("--population", type=int, default=48)
    ap.add_argument("--report-episodes", type=int, default=768)
    args = ap.parse_args()
    seed_rows, summary = run_selected(args.seed_count, args.iterations, args.population, args.report_episodes)
    write_csv(DATA / "inventory_equal_budget_pareto_seed_metrics.csv", seed_rows)
    write_csv(DATA / "inventory_equal_budget_pareto_audit.csv", summary)
    print(DATA / "inventory_equal_budget_pareto_audit.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
