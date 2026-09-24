# NDU — Operations Research R44

**Current manuscript:** Limited-Memory Renewal Contracts: Exact Quadratic Design and Resource Augmentation.

Read `main.pdf`, `electronic_companion.pdf`, and `revisions/or-r44-resource-augmentation-20260924/RESPONSE_TO_REFEREES.pdf`.

Isolated branch: `revision/ndu-operations-research-r44-resource-augmentation-20260924`.

Review: `a0d1f4e3dfc3f7639f806cab01f1faae877d5361`, report `reviews/operation_research_referee_report_r42_independent_harsh_2026-09-24.md`.

Immediate predecessor: published R43 `55313f79ad7d6b09c2edf1ceeafe254898a2bcbe`.

## New result

Two exact priced optimizers construct one fixed union alphabet with at most twice the symbol budget, exact promise and realization feasibility, and an explicit additive payoff guarantee. With zero charges the guarantee is within the requested tolerance of the original-budget catalog optimum. For nonnegative charges the actual extra installation charge is reported. Feasible mesh transport gives a continuous-design comparison with variable budget.

This is resource augmentation, not a same-budget FPTAS or a zero-duality-gap claim. An exact example has two-symbol optimum 45/64, minimum price bound 453/640, and gap 3/640; three installed levels attain 453/640. Original-budget intervals and augmented policy values are always separate.

The rational-quadratic exact continuous theorem, corrected face count, polynomial price DP, independently checked prefix partitions, sharp uniform mesh bound, saturated Monge results, and all earlier technical content remain in the reader package.

## Reproduction

From the repository root, use Python 3.12 and the standard library for the new recovery work. Inherited tests require SymPy and SciPy. Readers use pdflatex, newtx fonts, and poppler.

```bash
R=revisions/or-r44-resource-augmentation-20260924
python "$R/code/tests.py"
python "$R/code/study.py"
python "$R/code/inherited.py"
python "$R/code/tables.py"
python "$R/code/check_augmentation.py" "$R/results/certificates/strict_gap.json"
```

`code/build.py prepare` runs these steps. Commit scientific sources and executed evidence before `code/build.py build`. The branch-specific publication workflow performs that order and pushes only this revision branch. `bootstrap.py` assembles current reader wrappers from the pinned predecessor without modifying any historical source.

## Evidence and preservation

The new suite uses 144 exhaustive comparisons, 16 boundary checks, 14 semantic corruption rejections, and 5 invalid-input rejections. Twelve complete scaling/accuracy cases reach 256 branches, 65 catalog levels, and budget eight. These are synthetic models. Complete inputs, exact fractions, policies and independent certificates are in `results/`; tables derive from executed JSON.

The independent checker imports neither the recovery procedure nor the fixed-book allocator. It reconstructs price bounds via the R43 independent support checker and verifies policies and charge accounting directly. Inherited suites execute in disposable copies. Earlier SCIP comparisons remain preceding evidence, not new runs.

`BUILD_VALIDATION.json` records the committed scientific source and PDF checks. `PRESERVATION_MANIFEST.json` compares every historical path against the pinned predecessor. Existing branches and historical directories are not modified. Old root readers are snapshotted in `predecessor/`.
