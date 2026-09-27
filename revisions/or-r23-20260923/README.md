# Reproducing the complete R23 revision

The root main manuscript and electronic companion are the review objects. This directory contains additive R23 derivations and executed evidence; earlier results remain in their original directories.

## Execution

Use Python 3.13, NumPy 2.3.5, SciPy 1.17.0, CasADi 3.7.2 (its bundled OSQP library), and PyMuPDF 1.26.7. A C compiler builds the inherited OSQP bridge. Limit BLAS/OpenMP to one thread. A TeX Live installation with newtx, natbib, endfloat and amsthm builds the paper.

```sh
python revisions/or-r23-20260923/robust_study.py
python -S revisions/or-r23-20260923/replay.py
python revisions/or-r23-20260923/analyze.py
python revisions/or-r23-20260923/materialize_revision.py
bash revisions/or-r23-20260923/build.sh
python revisions/or-r23-20260923/package_metadata.py
python revisions/or-r23-20260923/check_package.py
python revisions/or-r23-20260923/package_metadata.py --manifest
python revisions/or-r23-20260923/check_package.py --verify-manifest
```

For a nonmutating verification of published evidence:

```sh
python -S revisions/or-r23-20260923/replay.py --check
python -S revisions/or-r22-20260923/replay.py --check
python -S revisions/or-r22-20260923/complete_dual_checks.py --check
python -S revisions/or-r19-20260923/replay.py --check
python revisions/or-r23-20260923/check_package.py --verify-manifest
```

The raw `certificates.jsonl.gz` records retain the rational implemented decisions, all eight valid outer-class dual certificates and all nominal nondeployment diagnostics. `robust_exact.py` has no numerical-library dependency; `python -S` prevents it from loading site packages. The comparator geometry is reconstructed analytically before replay. `DESIGN.json` declares the context seed, counts, uncertainty law, failure policy and the excluded engineering pilot. No pilot record enters the final results. Reexecution may change wall-clock timing or last digits of numerical proposals across hosts; exact authorization is repeated on the resulting records.

## Interpretation

The new records certify per-context robust feasibility and gain against the actual model-specific optimized restricted contract, conditional on the true coefficients belonging to the specified uncertainty set. New averages are descriptive, not lower confidence bounds. R22's nominal-model population bounds remain separately identified. The eight comparator solves are real additional work; this study does not claim acceleration. The `predecessor/` snapshot and manifest preserve the full R22 sources and PDFs.
