#!/usr/bin/env python3
"""Derive the Experiment III equal-evaluation frontier audit from the packaged frontier CSV.

The audit uses last-observation-carried-forward best-so-far utility at selected
evaluation budgets. It is intentionally stdlib-only so it can run in a clean
submission checkout without pandas/numpy.
"""
from __future__ import annotations

import csv
from pathlib import Path

METHODS = [
    'full_ndu_joint',
    'fixed_pref_joint_rl',
    'oracle_factor_joint_rl',
    'signal_only_joint_rl',
]
BUDGETS = [216, 442, 1242]


def last_at_or_before(rows: list[dict[str, str]], method: str, budget: int) -> float | None:
    value: float | None = None
    for row in rows:
        if int(float(row['evaluations'])) <= budget and row.get(method):
            value = float(row[method])
    return value


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data = root / 'data'
    with (data / 'exp3_training_frontier.csv').open(newline='') as fh:
        rows = list(csv.DictReader(fh))
    out_rows = []
    for budget in BUDGETS:
        values = {m: last_at_or_before(rows, m, budget) for m in METHODS}
        if any(v is None for v in values.values()):
            raise RuntimeError(f'missing frontier value at budget {budget}: {values}')
        non_ndu_best = max(v for m, v in values.items() if m != 'full_ndu_joint')
        leader = max(values, key=lambda m: values[m])
        sorted_vals = sorted(values.values(), reverse=True)
        out_rows.append({
            'evaluation_budget': budget,
            **{m: f'{values[m]:.17g}' for m in METHODS},
            'leader': leader,
            'second_best': f'{sorted_vals[1]:.17g}',
            'full_minus_best_non_ndu': f'{values["full_ndu_joint"] - non_ndu_best:.17g}',
        })
    with (data / 'exp3_equal_evaluation_audit.csv').open('w', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)
    print(data / 'exp3_equal_evaluation_audit.csv')


if __name__ == '__main__':
    main()
