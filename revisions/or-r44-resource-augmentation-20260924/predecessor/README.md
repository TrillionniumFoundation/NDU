# NDU — Operations Research R43

**Current manuscript:** Limited-Memory Renewal Contracts: Exact Quadratic Design and Prefix Decomposition.

**Reader entry points:** `main.pdf`, `electronic_companion.pdf`, and `revisions/or-r43-prefix-decomposition-20260924/RESPONSE_TO_REFEREES.pdf`.

**Isolated branch:** `revision/ndu-operations-research-r43-prefix-decomposition-20260924`.

**Immutable review baseline:** `a0d1f4e3dfc3f7639f806cab01f1faae877d5361`; report `reviews/operation_research_referee_report_r42_independent_harsh_2026-09-24.md`.

## New mathematical and algorithmic results

R43 adds the eligibility-prefix price decomposition, taking O((k+m)N^2) arithmetic work on a catalog with variable branch count k and alphabet budget m. Exact prefix-completion bounds yield finite catalog search and a globally checkable interval at interruption. A uniform-mesh lower bound is sharp on one fixed uncharged input. A monotone-charge theorem identifies the boundary of the one-branch randomization example. The exact rational-quadratic continuous theorem is retained, with the corrected s+1+4k inequality count and a rank-limited active-set bound.

The price problem is not asserted to have zero outer duality gap. Full prefix search still has exponential worst-case size. General concave structure and scalar-oracle decomposition are distinguished from exact unrestricted rational-quadratic continuous optimization. A numerical SCIP cross-check is not a rational proof certificate.

## Reproduction

From this branch's repository root, use Python 3.12, the standard library, SymPy, SciPy, PySCIPOpt, pypdf, pdflatex with newtx fonts, and poppler tools. Exact versions and instrumented timings are recorded by the run.

```bash
R=revisions/or-r43-prefix-decomposition-20260924
python "$R/code/tests.py"
python "$R/code/study.py"
python "$R/code/inherited.py"
python "$R/code/tables.py"
python "$R/code/checker.py" "$R/results/certificates/case_07.json"
```

`code/build.py prepare` performs the experiment and reader preparation steps. Scientific sources must be committed before `code/build.py build`, which checks page limits, references, provenance, and preservation. The branch-only publication workflow performs this ordering and requires all six independent nonlinear comparisons.

## Evidence

`results/verification.json` records seeded exact comparisons against independent exhaustive enumeration and rejection of modified bounds. `results/certificates/` stores complete global prefix partitions and feasible lotteries, which `checker.py` validates without importing the solver or face generator. `results/scaling.json` records exact catalog and continuous intervals, evaluated books, prefixes, bit lengths, memory, and separate checker times. `results/continuous_frontier.json` includes every completed or budget-limited continuous run and the separate original-policy nonlinear program. `results/inherited.json` records isolated replay of R42 and the inherited R39/R33–R37 suites.

`BUILD_VALIDATION.json` reports the actual committed scientific source, page counts, test identities, and output hashes. `PRESERVATION_MANIFEST.json` verifies every baseline path outside the allowed current reader replacements. These provenance files do not substitute for mathematical or global-search verification.

## Preservation and reader organization

No prior revision directory or review report is modified. The old main and companion readers, README, and checklist are copied byte for byte into the R43 `predecessor/` directory. The R42 joint-design study and all its tables are retained in the current companion, clearly identified as preceding evidence. Original sources remain available in their original locations and all historical branches remain unchanged.

All experiments are synthetic. The ordered-interface theorem is reusable without the renewal interpretation; no deployed contract or empirically calibrated application is asserted. This branch is ready for further mathematical and editorial review, not a claim of journal acceptance.
