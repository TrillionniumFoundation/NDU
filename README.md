# NDU — Operations Research revision R33

**Accepted Service Adaptation: Exact Parametric Quotients and Minimal Additional Writable Memory**

Isolated revision branch: `revision/ndu-operations-research-r33-piecewise-randomized-20260923`.
Scientific base: `238bfdb24d93439a545551d275a0c9189dbc017b` (R32).
Review answered: independent R30 report at `a017f474619e86be533547acac87a3c8354f64cf`.

## Reader entry points

- `main.tex` and rebuilt `main.pdf`: complete revised article.
- `electronic_companion.tex` and rebuilt `electronic_companion.pdf`: retained companion plus new verification and accounting concordance.
- `revisions/or-r33-piecewise-randomized-20260923/RESPONSE_TO_REFEREES.md`: point-by-point response with inherited/new distinctions.
- `revisions/or-r33-piecewise-randomized-20260923/DERIVATION_PROVENANCE.md`: exact source commits and proof dependencies.
- `revisions/or-r33-piecewise-randomized-20260923/BUILD_VALIDATION.json`: source identity, reader-PDF hashes, page counts, and build checks once successfully generated. A stale predecessor PDF is not a validated R33 reader file.

## New scientific content

The `extensions.tex` module proves exact closure for continuous strictly concave piecewise-quadratic rewards, including marginal jumps, with a local-piece event budget, polynomial rational coefficient-event complexity, and the same cap-only carried-price bound. It supplies a nondifferentiable-safe conjugate certificate, an explicit convex-cost-flow bridge, and a shared-circuit persistent-storage/query tradeoff. Quadratic explicit-table tightness is preserved and is not misrepresented as a lower bound on every shared representation.

The `randomized_memory.tex` module gives an adjacent-lottery characterization for fixed terminal codebooks. It globally solves a three-branch instance: two deterministic symbols lose `1/8`, while two randomized symbols under expected participation lose `1/96`. Exact optimality still requires three symbols. Private-draw pathwise participation is expressly distinguished.

## Reproduce the new exact checks

```sh
python revisions/or-r33-piecewise-randomized-20260923/verify.py
```

This regenerates `verification.json` and `representation.csv`. The local run passed 24 piecewise recombining inputs, 4,170 independent local checks, 834 whole-graph circuit comparisons, 834 circuit inversions, 836 primal–dual certificates, four complete exact active-set paths, and seven chain sizes. The records identify the actual run and environment-dependent timing.

The parametric reference is our own exhaustive small-instance KKT enumerator. It is not a published specialized-solver implementation or a competitive speed benchmark. Instances are synthetic; no service calibration is claimed.

## Preservation and build

All R31/R32 modules, previous theory volumes, and earlier favorable and unfavorable evidence remain in the branch. Exact predecessor wrappers are archived in the R33 `predecessor/` directory. The root wrappers, new R33 modules, and response constitute the revision. `main` and all prior branches are left unchanged.

The isolated R33 workflow verifies the payload, commits the scientific sources, runs exact checks, compiles both reader PDFs with filtered cross-document labels, checks citations/references and layout, and publishes validation artifacts on this branch only. Read the final scientific commit and build record rather than inferring completion from a branch name.
