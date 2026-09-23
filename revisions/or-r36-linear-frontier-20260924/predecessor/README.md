# NDU — Operations Research revision R35

**Accepted Service Adaptation: Exact Parametric Quotients and Minimal Additional Writable Memory**

Branch: `revision/ndu-operations-research-r35-monge-frontier-20260923`.
Scientific baseline: R34 at `fbfdf24b370201c810425f633f5fc06048282b5c`.
Independent report answered: `a017f474619e86be533547acac87a3c8354f64cf`, which reviewed R30, not R31–R34.

## Review entry points

- `main.tex` / `main.pdf`: complete revised article, including the new Monge-frontier theorem and proof.
- `electronic_companion.tex` / `electronic_companion.pdf`: retained technical companion plus exact search, boundary, and verification details.
- `revisions/or-r35-monge-frontier-20260923/RESPONSE_TO_REFEREES.md` / `.pdf`: point-by-point response, separating inherited repairs from new R35 results.
- `revisions/or-r35-monge-frontier-20260923/DERIVATION_PROVENANCE.md`: immutable report/base identities and proof/evidence dependencies.
- `revisions/or-r35-monge-frontier-20260923/BUILD_VALIDATION.json`: authoritative source identity, reader hashes, page counts, tests, and preservation checks.

## New result

The heterogeneous quadratic renewal model has Monge interpolation costs and deterministic cell costs. Crucially, the terminal cost array remains Monge **after the continuous highest codeword is optimized in each interval**. Leftmost monotone search computes both the global expected-participation randomized frontier and the deterministic/pathwise frontier through budget `m` in `O(m k log(k+1))` exact rational operations and comparisons, with `O(m k+k)` storage for `m<=k`. The earlier global algorithm required `O(m k^2)` work. Both solve the same problem, including off-cap terminal levels. Generic Monge search is attributed to the classical literature; the new result proves its contractual-cost hypotheses.

## Reproduction

From the repository root, with Python 3.12 or newer:

```sh
R=revisions/or-r35-monge-frontier-20260923
python "$R/verify.py"
python "$R/benchmark.py"
python "$R/reproduce_inherited.py"
python "$R/build_validate.py"
```

The first three commands use only the Python standard library. The final command requires pdfLaTeX with newtx and standard packages, plus Poppler. It compiles the main article, companion, and response; checks references, layout, source preservation, and test status; and binds their hashes to the exact scientific source commit. Run `NDU_LOCAL_VALIDATION=1` only outside a Git checkout; that mode records content hashes and does not invent a Git commit.

The new exact suite passes 98 cases, 1,712 frontier equalities, 1,712 controller replays, 8,030 Monge inequalities, 1,401 direct terminal checks, 384 leftmost-argmin checks, and 14 invalid-input rejections. Independent exhaustive and nonanchor-grid checks are recorded separately. Both unchanged R33 and R34 suites are rerun in temporary directories.

The scale study computes every budget through eight on 16–1,024 branches. Exact comparisons with the unchanged R34 randomized solver are run through 256 branches. At that size, combined terminal/prefix evaluations decline from 192,546 to 12,177. Larger baseline entries are NOT_RUN, not estimated or timeout results. `benchmark.json` and `scaling.csv` preserve exact losses, work counts, actual timings, source hashes, and environment metadata. The instances are synthetic; no published specialized flow-solver benchmark is claimed.

## Preservation and review status

All inherited R31–R34 theorem modules, earlier records, and historical theory volumes remain in the branch. The four original root wrappers are archived in the new revision's `predecessor/` directory. The preservation manifest verifies the inherited reader/source/evidence snapshot; a remote tree audit verifies that every other base path remains unchanged. `main` and all earlier review/revision branches are untouched.

This is a new manuscript for further referee review, not a journal submission or an editorial decision. The Operations Research lengthy-manuscript format preserves the complete theory rather than deleting results to fit a shorter reader.
