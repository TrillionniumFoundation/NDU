#!/usr/bin/env python3
"""Create an seed-level statistical audit from packaged CSVs.

The audit uses only held-out reporting seed metrics already shipped in the
reproducibility bundle. It does not rerun CEM. Method-specific seeds are offset,
so the CIs are independent two-sample normal summaries rather than common-random-
number paired tests. The file is intended as a lightweight reproducibility
artifact, not a full inferential package.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "seed_level_statistical_audit.csv"


def read_rows(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="") as fh:
        return list(csv.DictReader(fh))


def mean_var(xs: list[float]) -> tuple[float, float]:
    n = len(xs)
    mean = sum(xs) / n
    var = sum((x - mean) ** 2 for x in xs) / (n - 1) if n > 1 else 0.0
    return mean, var


def diff_audit(name: str, experiment: str, metric: str, method_a: str, method_b: str, direction: str) -> dict[str, str]:
    rows = read_rows(name)
    by_method: dict[str, list[float]] = {}
    for row in rows:
        by_method.setdefault(row["method"], []).append(float(row[metric]))
    a = by_method[method_a]
    b = by_method[method_b]
    ma, va = mean_var(a)
    mb, vb = mean_var(b)
    mean = ma - mb
    se = math.sqrt(va / len(a) + vb / len(b))
    ci = 1.96 * se
    excludes_zero = (mean - ci > 0) or (mean + ci < 0)
    return {
        "experiment": experiment,
        "metric": metric,
        "method_a": method_a,
        "method_b": method_b,
        "n_a": str(len(a)),
        "n_b": str(len(b)),
        "mean_a": f"{ma:.12g}",
        "mean_b": f"{mb:.12g}",
        "mean_diff_a_minus_b": f"{mean:.12g}",
        "ci95_halfwidth_normal_independent": f"{ci:.12g}",
        "ci95_low": f"{mean - ci:.12g}",
        "ci95_high": f"{mean + ci:.12g}",
        "ci_excludes_zero": "yes" if excludes_zero else "no",
        "direction": direction,
    }


def main() -> None:
    comparisons = [
        ("exp1_seed_metrics.csv", "I", "mean_utility", "full_ndu_joint", "augmented_state_rl", "higher is better"),
        ("exp1_seed_metrics.csv", "I", "cew", "full_ndu_joint", "augmented_state_rl", "higher is better"),
        ("exp2_seed_metrics.csv", "II", "mean_utility", "full_ndu_joint", "preference_only", "higher is better"),
        ("exp2_seed_metrics.csv", "II", "mean_utility", "full_ndu_joint", "oracle_joint_action_rl", "higher is better"),
        ("exp2_seed_metrics.csv", "II", "sharpe", "full_ndu_joint", "preference_only", "higher is better"),
        ("exp3_seed_metrics.csv", "III", "mean_utility", "full_ndu_joint", "oracle_factor_joint_rl", "higher is better"),
        ("exp3_seed_metrics.csv", "III", "cew", "full_ndu_joint", "oracle_factor_joint_rl", "higher is better"),
        ("exp3_seed_metrics.csv", "III", "turnover", "full_ndu_joint", "oracle_factor_joint_rl", "lower is better; negative favors A"),
        ("inventory_service_level_seed_metrics.csv", "inventory", "mean_welfare", "full_ndu_inventory", "action_only_adaptive_base_stock", "higher is better"),
        ("inventory_service_level_seed_metrics.csv", "inventory", "avg_cost", "full_ndu_inventory", "action_only_adaptive_base_stock", "lower is better; negative favors A"),
    ]
    rows = [diff_audit(*c) for c in comparisons]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
