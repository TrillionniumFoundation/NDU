# NDU — Operations Research revision R34

**Accepted Service Adaptation: Exact Parametric Quotients and Minimal Additional Writable Memory**

Revision branch: `revision/ndu-operations-research-r34-global-randomized-frontier-20260923`.
Base: R33 at `38b3f264e371758054d94a9f94088ae17a816241`.
Latest independent report answered: `a017f474619e86be533547acac87a3c8354f64cf` (reviewed R30, not the later revisions).

## Reader entry points

- `main.tex` / `main.pdf`: full revised article, with the new global randomized frontier and pathwise theorem proved in the main text.
- `electronic_companion.tex` / `electronic_companion.pdf`: retained companion plus new implementation and verification concordance.
- `revisions/or-r34-global-randomized-frontier-20260923/RESPONSE_TO_REFEREES.md`: response organized against the report, separating R31–R33 inherited changes from new R34 results.
- `revisions/or-r34-global-randomized-frontier-20260923/DERIVATION_PROVENANCE.md`: immutable review/base commits and proof dependencies.
- `revisions/or-r34-global-randomized-frontier-20260923/BUILD_VALIDATION.json`: source identity, PDF hashes, page counts, source preservation, and actual tests. A predecessor PDF or a transport commit alone is not a validated R34 reader.

## New mathematical result

For the heterogeneous quadratic renewal family, an optimal randomized terminal codebook has all nonhighest levels at branch caps and at most one continuous highest level. An ordered dynamic program plus exact interval minimization computes the global frontier through budget `m` in `O(m k^2)` rational operations and `O(m k+k)` scalar storage for `m<=k`. The highest level cannot simply be restricted to caps: the new three-branch example has optimal levels `1/4,5/8` and loss `23/1280`, below the best cap-only loss `3/160`.

A separate all-budget theorem shows that private-draw pathwise participation has exactly the deterministic frontier under the stated saturated-root renewal architecture. Expected participation can admit a strictly better randomized frontier. Both institutions retain the same exact-optimum alphabet threshold when the full-information optimum is unique.

These results add to, rather than replace, the retained quotient, tightness, piecewise-quadratic, machine-minimization, circuit, comparator, and historical switching/deployment results.

## Reproduction

From the repository root, with Python 3.12 or newer and no third-party Python packages:

```sh
R=revisions/or-r34-global-randomized-frontier-20260923
python "$R/verify.py"
python "$R/reproduce_inherited.py"
python "$R/build_validate.py"
```

The last command also requires pdfLaTeX with newtx/standard LaTeX packages and Poppler utilities. It records the current Git source commit and checks both documents. The isolated GitHub Actions workflow executes the same steps and publishes validated readers only on the R34 branch.

The exact new suite passed 51 small instances, 1,932 reduced-candidate comparisons, 446 frontier equalities, 1,073 nonanchor-grid checks, 1,346 moment identities, 255 controller replays, and ten invalid-input checks. The scale family computes all budgets through eight on 16, 32, 64, and 128 branches. `verification.json`, `scaling.csv`, and `inherited_verification.json` record the actual run and environment.

The exhaustive comparator uses the proved anchor reduction but is independent of the production DP and moment arithmetic. Grids are falsification tests, not a proof over the continuum. No published specialized solver implementation is represented as having been run. Instances are synthetic, not calibrated service data.

## Preservation and presentation

All R31–R33 source modules and earlier evidence remain in the branch. Original root wrappers are archived in the R34 `predecessor/` directory. `PRESERVATION_MANIFEST.json` validates 35 inherited reader/source/evidence files and four archived wrappers. The remote tree inherits every other historical file unchanged. `main` and all previous revision/review branches are left untouched.

The full article is prepared under the Operations Research Lengthy Manuscript category, preserving 11-point text, 1.5 spacing, one-inch margins, author–year references, and tables after references. The validated build conservatively requires no more than 40 total main pages, a companion no longer than the main paper, an abstract of at most 200 words, and no unresolved references/citations or overfull boxes. It is a manuscript for further review, not a journal submission or acceptance.
