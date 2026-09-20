#!/usr/bin/env python3
"""Tabulate scale-aware residual diagnostics for the full HBO/NBO run."""
from __future__ import annotations

import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
FULL_SPECS = [
    ('exp1_habit_portfolio', 'nbo_full_ndu'),
    ('exp2_hidden_regime', 'nbo_full_ndu'),
    ('exp3_high_dimensional_allocation', 'nbo_full_ndu'),
    ('inventory_service_level', 'nbo_full_ndu_inventory'),
]


def main() -> int:
    rows = list(csv.DictReader((DATA / 'source_nbo_training_diagnostics.csv').open()))
    out = []
    for experiment, method in FULL_SPECS:
        final = max(
            (r for r in rows if r['experiment'] == experiment and r['method'] == method),
            key=lambda r: int(r['iteration']),
        )
        hjb = float(final['hjb_loss'])
        rmse = math.sqrt(hjb)
        mean_h = abs(float(final['mean_hamiltonian']))
        norm = rmse / (1.0 + mean_h)
        out.append({
            'experiment': experiment,
            'method': method,
            'iteration': final['iteration'],
            'native_hjb_loss': f'{hjb:.12g}',
            'residual_rmse': f'{rmse:.12g}',
            'mean_abs_residual': final['residual_mean_abs'],
            'mean_hamiltonian_abs': f'{mean_h:.12g}',
            'normalized_residual_rmse_over_one_plus_abs_mean_hamiltonian': f'{norm:.12g}',
            'terminal_boundary_loss': final['terminal_loss'],
            'interpretation': 'residual_certificate_gap_reported',
        })
    path = DATA / 'hbo_residual_diagnostics.csv'
    with path.open('w', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        writer.writeheader()
        writer.writerows(out)
    print(f'wrote {path} ({len(out)} rows)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
