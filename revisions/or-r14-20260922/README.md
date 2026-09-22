# R14 review and reproduction package

This is an additive revision of the completed R13 manuscript, responding to the latest R12 Operations Research report. The current branch is `revision/ndu-operations-research-r14-20260922`; its scientific parent is `808b8f0353051581134d3b8b5a7424422d4e48a8`.

Read `../../main.pdf`, `../../electronic_companion.pdf`, `RESPONSE_TO_REFEREE.md`, and `PRESERVATION.md`. Main Section 7 contains the explicit accepted-star threshold, single-price algorithm, and global nonoracular scalar-gradient regret theorem. Section 9 contains the direct neural-critic experiment and independent gain confirmation. Previous full-tree scope, verified cells, all earlier experiments, and their adverse outcomes remain available.

## Reproduce

From the repository root, with Python 3.13 and a TeX distribution providing `newtx`, `natbib`, `endfloat`, `xr-hyper`, and `fancyhdr`:

```sh
python -m pip install -r revisions/or-r14-20260922/requirements.txt
bash revisions/or-r14-20260922/reproduce.sh
bash revisions/or-r14-20260922/build.sh
python revisions/or-r14-20260922/check_package.py
python revisions/or-r14-20260922/manifest.py
```

No network request or external dataset is needed by the numerical scripts. `OPENBLAS_NUM_THREADS=1` and `OMP_NUM_THREADS=1` are set by the reproduction entry point. The dependency versions are pinned. Training and validation plans are fixed in `EXPERIMENT_PLAN.json` and `validation.py`; this is an internal prospective plan, not external preregistration. Timing numbers depend on hardware and load and are regenerated into tables, not hardcoded in the manuscript.

`star.py` proposes numerical policies and rational certificates. `structural_tests.py` compares independent algorithms and the full tension LP, tests global inequalities through binding capacities, and records branching-scale timings. `study.py` trains eight paired scalar critics and reports raw quality separately from complete matched-accuracy timing. `validation.py` evaluates two frozen critics on a new independent cohort with exact corner ranges. `verify.py` imports only the standard library and independently reconstructs the rational feasibility, switching, profit, and conjugate bounds. `tables.py` generates every new table and displayed experimental macro from actual records; certificate ranges are rounded outward in prose.

## Evidence files

`results/verification.json` and `results/package_checks.json` are the independent policy and preservation/layout checks. `results/summary.json` records eight-seed outcomes, paired intervals, full timing components, and training costs. `results/validation.json` records the exact range, confidence statement, model hash, and selection result. `results/structural_checks.json` summarizes solver and inequality checks. Every raw policy, timing record, corner, training sample, label, and fitted coefficient is retained alongside them. `results/manifest.json` hashes the source and evidence files.

The proposed neural policies are accurate in this declared two-review distribution, but complete audited latency remains slower than the structure-aware classical methods. The paired derivative-training difference is statistically unresolved. Neither outcome is removed. The expected-gain confirmation uses no full-objective refinement and does not claim arbitrary distribution-shift performance.
