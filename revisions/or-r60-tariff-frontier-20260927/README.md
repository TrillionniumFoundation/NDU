# NDU — Operations Research R60

**Finite-Catalog Resource Allocation: A Tariff-Sensitive Complexity Frontier**

Current readers: `main.pdf`, `electronic_companion.pdf`. New revision: `revisions/or-r60-tariff-frontier-20260927`.
Based on latest report `reviews/operation_research_referee_report_r59_independent_harsh_2026-09-27.md` at review commit `cc7ac349969adc9186e9a75f8d01f76ad485c3ba`. Author branch: `revision/ndu-operations-research-r60-tariff-frontier-20260927`.

## New substantive results

Theorem 6.2 gives exact allocation with a standard opening fee and d exceptional commands in O(k N^2 + 2^d m N^2) rational operations, and 2^d poly(L) bit time, for common linear rewards and free preliminary service. Arbitrary expected caps, realization ceilings, probabilities and rational denominators remain allowed. Uniform fees give a polynomial algorithm without a resource grid. This is a positive counterpart to the retained original-model W[1]-hardness in menu allowance plus cap count. The manuscript also adds same-book price-support and gap results, bounded-path recognition with witnesses, and a corridor-rehabilitation mapping. Scope and all earlier proofs remain explicit.

## Review entry points

- `revisions/or-r60-tariff-frontier-20260927/RESPONSE_TO_REFEREES.pdf`: complete point-by-point R59 response.
- `revisions/or-r60-tariff-frontier-20260927/CURRENT_SUBMISSION.zip`: standalone readers and a flat, independently verifiable code/data package.
- `revisions/or-r60-tariff-frontier-20260927/PRESERVATION.json`: hashes, source origins and retained mathematical labels.
- `revisions/or-r60-tariff-frontier-20260927/retained_r59/`: byte-identical reviewed root readers and entry points.
- `revisions/or-r60-tariff-frontier-20260927/results/ALL_RUNS.csv`: every new method request, including failures and deadlines.
- `revisions/or-r60-tariff-frontier-20260927/results/STUDY_FREEZE.json` and `SOURCE_FREEZE_COMMIT.txt`: sources and inputs committed before timing.
- `revisions/or-r60-tariff-frontier-20260927/results/SUMMARY.json`: actual family/budget/method success and tail costs.
- `revisions/or-r60-tariff-frontier-20260927/results/R59_REANALYSIS.json`: separately labeled reanalysis of unchanged historical records.
- `revisions/or-r60-tariff-frontier-20260927/BUILD_VALIDATION.json` and `RELEASE_MANIFEST.json`: reader and payload closure.

The prospective study has 90 distinct models, 270 budget-tagged cases and 1260 requests. Thirty seeds per family recur across interventions and three budgets; these requests are not independent observations. Rationally certified global intervals and SCIP numerical-bound results are reported separately. SCIP's selected book is reoptimized exactly for its lower policy; its global upper bound remains numerical. No field validation or unexecuted hybrid advantage is claimed.

## Build and verify

Python 3.13.5 and pinned dependencies: `revisions/or-r60-tariff-frontier-20260927/requirements.txt`. TeX Live needs newtx, xr-hyper and xurl. Ordinary scientific sources are committed before compilation.

```sh
python revisions/or-r60-tariff-frontier-20260927/code/tests60.py --output /tmp/STRUCTURAL60.json
python revisions/or-r60-tariff-frontier-20260927/code/study60.py verify
python revisions/or-r60-tariff-frontier-20260927/code/package60.py tails
python revisions/or-r60-tariff-frontier-20260927/code/build60.py
python revisions/or-r60-tariff-frontier-20260927/code/package60.py finish
python revisions/or-r60-tariff-frontier-20260927/code/package60.py verify
```

The standalone ZIP requires no historical directory tree: run `python code/flat_verify60.py`, then `python rebuild_readers.py` to compile. `python rerun_study.py --output /absolute/new/directory` reproduces the design in a fresh directory without overwriting recorded evidence. New timings are new executions, not replacements for the published receipts.

## Publication validation

Abstract: 169 words. Main: 30 PDF pages, 28 excluding references. Companion: 28 pages. Category: Regular manuscript. Anonymous 11-point type, 1.5 spacing and one-inch margins; equation-free introduction; author-year alphabetical references; tables after references. Build diagnostics: PASS. Exact final-checkout verification is separately bound to the published commit by CI, not conflated with the execution freeze. The review branch and all earlier revision directories remain unchanged.
