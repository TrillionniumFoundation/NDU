# NDU — Operations Research R59

Current article: **Finite-Catalog Resource Allocation: Exact Path Representations and Menu Complexity**.

The current root `main.pdf` and `electronic_companion.pdf` are the R59 readers. The revision directory holds the complete response to the September 26 R58 referee report, ordinary LaTeX sources, exact structural tests, the frozen matched-resource study and publication validation. All earlier scientific paths remain unchanged; predecessor root files are copied under `retained_r58/` before replacement.

The primary additions are original-model W[1]-hardness jointly in menu budget and cap count, recognition/approximation for conservative resource paths, optimized common-curvature prototype grouping, and an exact mixed-integer convex comparator. Numerical SCIP bounds and rational certificates are deliberately distinguished. No editorial acceptance or field calibration is claimed.

## Entry points

- `main.pdf`: current article, central new proofs included.
- `electronic_companion.pdf`: full secondary structural/price/lattice results and direct formulation.
- `revisions/or-r59-parameterized-deficit-20260927/RESPONSE_TO_REFEREES.pdf`: point-by-point response to the latest R58 report.
- `revisions/or-r59-parameterized-deficit-20260927/CONTENT_MAP.md`: current and retained scientific reading map.
- `revisions/or-r59-parameterized-deficit-20260927/results/ALL_RUNS.csv`: every new timed request, including failures and limits.
- `revisions/or-r59-parameterized-deficit-20260927/results/STUDY_FREEZE.json`: input and execution-source freeze.
- `revisions/or-r59-parameterized-deficit-20260927/BUILD_VALIDATION.json`: actual compiled reader graph and diagnostics.
- `revisions/or-r59-parameterized-deficit-20260927/CODE_AND_DATA.zip`: flat self-contained current code/data and reader package.

## Reproduction from this root

Use Python 3.13.5; pinned dependencies are in `revisions/or-r59-parameterized-deficit-20260927/requirements.txt`. PDF compilation needs TeX Live with `newtx`, `xr-hyper` and `xurl`.

```sh
python revisions/or-r59-parameterized-deficit-20260927/code/structural59.py
python revisions/or-r59-parameterized-deficit-20260927/code/feasibility59.py
python revisions/or-r59-parameterized-deficit-20260927/code/build59.py
python revisions/or-r59-parameterized-deficit-20260927/code/release59.py verify
```

The committed study is immutable evidence. To repeat timing, copy the extracted archive to a separate directory and remove only the **new R59** `results/records`, `results/inputs`, `results/certificates`, `results/STUDY_FREEZE.json` and `results/SUMMARY.json` in that copy; then run `python revisions/or-r59-parameterized-deficit-20260927/code/study59.py freeze run`. Never relabel new timings as the preserved execution. The panel uses 72 inputs × four methods, sequential three-second total allowances, and a 1.8-second internal optimization cutoff. It is a deterministic synthetic engineering panel, not an independently sampled field study.

SCIP's quadratic formulation has zero envelope error, but floating-point global bounds are not exact rational proofs. Its reconstructed lower policy is checked independently. Process high-water RSS during checking includes retained optimizer allocations. Read-only verification records the exact checkout SHA externally; it does not modify the paper commit or claim administrative branch-protection settings.
