# R13 scientific revision and reproducibility

Read the root `main.pdf`, `electronic_companion.pdf`, and this folder's `RESPONSE_TO_REFEREE.md`. `PRESERVATION.md` maps all prior scientific content. The new proofs are in `sections/constructive_flow.tex` and `sections/certified_cells.tex`; no optimizer flag substitutes for those proofs.

## Replay the recorded package

From the repository root with Python 3.13 and the pinned requirements:

```sh
python -m pip install -r revisions/or-r13-20260922/requirements.txt
python revisions/or-r13-20260922/verify.py
bash revisions/or-r13-20260922/build.sh
```

`verify.py` itself needs only the Python standard library. It independently reconstructs accepted tiers, every subtree commitment, profit, arbitrary-tension leakage, all reported policy bounds, corner ranges, exact confirmation sums, and lower/upper critical-friction witnesses. LaTeX building additionally needs pdfLaTeX, newtx fonts, the packages in the preamble, and Poppler's `pdfinfo`.

## Reproduce, rather than replay, the experiments

```sh
bash revisions/or-r13-20260922/reproduce.sh
bash revisions/or-r13-20260922/build.sh
python revisions/or-r13-20260922/manifest.py
```

Reproduction fits a fresh deterministic-seed model before either validation stage. It overwrites this branch's R13 generated results only. It does not rewrite older experiments. The train/validate/confirm stages are separate; confirmation freezes its model-derived range before drawing its fresh cohort. Hardware-dependent timings and model-file hashes may differ between reruns because measured offline times are serialized in the frozen model. The numerical primitives, random seeds, policies, and hash linkage within each run are recorded.

The source payload publication step, where used by the GitHub workflow, materializes ordinary tracked source files before running these commands. It is not a dependency of the finished manuscript: the final branch includes those ordinary sources, PDFs, and outputs directly.

## Result interpretation

`confirmation.json` reports simultaneous expected-gain lower bounds and expected-regret upper bounds for three frozen static-gated policies. Positive gain is relative to static in the specified synthetic distribution. The wider regret ceiling is not a high-accuracy guarantee. `matched_records.json.gz` separately records actual refinements to a common certified tolerance. `scaling.json.gz` retains first-order brackets that miss their iteration-limited target. The stronger sequential-cell classical comparator and all prior negative transfer evidence are retained.

The package contains synthetic data only. Publishing this branch neither submits a paper to a journal nor asserts an editorial outcome.
