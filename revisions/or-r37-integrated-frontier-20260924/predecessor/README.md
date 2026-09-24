# NDU — Operations Research revision R36

**Accepted Service Adaptation: Exact Parametric Quotients and Minimal Additional Writable Memory**

New branch: `revision/ndu-operations-research-r36-linear-frontier-20260924`.
Baseline reader: R35 at `7e49851cd04f0f7e015c2561b43a4e7591574e67`.
Independent report addressed: `a017f474619e86be533547acac87a3c8354f64cf`, which reviewed R30, not R31–R36.

## Readers and audit entry points

- `main.tex` / `main.pdf`: the complete article, including the new linear-work theorem and proof and all inherited R31–R35 theorem modules.
- `electronic_companion.tex` / `electronic_companion.pdf`: retained technical material plus the full symbolic-completion argument, search invariants, complexity accounting, and evidence details.
- `revisions/or-r36-linear-frontier-20260924/RESPONSE_TO_REFEREES.md` / `.pdf`: point-by-point cumulative response with inherited/new results distinguished.
- `revisions/or-r36-linear-frontier-20260924/DERIVATION_PROVENANCE.md`: immutable identities and proof/evidence dependencies.
- `revisions/or-r36-linear-frontier-20260924/BUILD_VALIDATION.json`: actual source commit, reader hashes, page counts, tests, and preservation checks.

## New scientific and implementation result

Both exact renewal memory frontiers through budget `m` on `k` ordered branches can be computed in `O(m k)` rational operations and comparisons, with `O(m k+k)` storage for `m<=k`, including an optimal codebook for every budget. The conditional-expectation frontier retains its continuously optimized, possibly off-cap highest level. The deterministic frontier remains the private-draw pathwise randomized optimum in the established renewal architecture.

The new step is a proved symbolic completion of the contractual Monge staircases, including selected submatrices whose rows contain no feasible entry. Uniform infinite padding with ordinary left ties does not satisfy the needed condition. The implementation applies **classical SMAWK**, explicitly attributed, to this interface. Generic matrix search is not claimed as new. The earlier R35 divide-and-conquer implementation and R34 quadratic algorithm remain unchanged.

## Exact verification and same-input evidence

The new exact suite passes 100 instances, 4,232 objective equalities against both earlier algorithms, 2,116 controller replays, 156 independent reduced-candidate frontier equalities, 43,431 submatrix argmin checks, 2,595 nonvacuous total-monotonicity implications, 255 direct interval checks, 402 finite Monge checks, 176 nonanchor-grid falsification checks, two padding regressions, 16,273 work checks, and 17 invalid-input rejections.

The study computes all budgets one through eight on 16–2,048 branches. Both frontiers agree exactly with R35 throughout; the quadratic randomized R34 comparison runs through 256 branches. Larger R34 entries are `NOT_RUN`, not estimates or timeouts. Full codebooks, exact losses, counts, actual times, environment, and source hashes are recorded in `benchmark.json` and `scaling.csv`.

The asymptotic improvement does **not** mean uniform speed. At 16 branches the expected frontier uses 534 economic queries versus R35's 289; at 2,048 it uses 128,966 versus 135,597. The deterministic count at 2,048 remains larger, 163,838 versus 153,180. These unfavorable constants are retained. Inputs are synthetic; there is no claim of an external published-flow-solver benchmark or empirical service calibration.

## Reproduction

From the repository root, with Python 3.12 or newer:

```sh
R=revisions/or-r36-linear-frontier-20260924
python "$R/verify.py"
python "$R/benchmark.py"
python "$R/reproduce_inherited.py"
python "$R/build_validate.py"
```

The first three commands use only the Python standard library. The last needs pdfLaTeX, newtx and standard packages, and Poppler. The inherited R33–R35 suites run unchanged in temporary directories so their prior evidence is not overwritten. R34/R35 comparators share economic primitives and moments; the reduced-candidate and submatrix checks supply separate direct validation.

A local build outside a Git checkout can use `NDU_LOCAL_VALIDATION=1`; it records content hashes, not a fabricated source commit. The remote build commits scientific sources/evidence before compiling, so PDF hashes are tied to an actual source identity.

## Preservation and further review

The original four root wrappers are archived under the new revision's `predecessor/`. Every inherited theorem source and evidence file is preserved, and the full remote tree audit checks that no unrelated base path changes or disappears. Main and previous review/revision branches are untouched. This is a new manuscript for further referee review, not a journal submission or an editorial acceptance claim. The Operations Research lengthy-manuscript format is checked by the build record.
