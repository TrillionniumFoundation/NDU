# Accepted Service Adaptation — Operations Research R29

**Finite Continuation Prices and the Value of Memory**

Revision branch: `revision/ndu-operations-research-r29-price-state-20260923`  
Scientific preservation base / preceding R28 report: `af01e2c33f85835e550896985b7cb83b3f4b784f`  
Latest R29 report: `1647d416e7a2806d36b1c9972aff0c0b54779912` (read and integrated during final remote reconciliation)  
Scientific predecessor: R28 `b53d644be66e9d27bb58cd0f8529aba0c91ec14c`.

## Reader entry points

- [Current manuscript](main.pdf) · [LaTeX](main.tex)
- [Electronic companion](electronic_companion.pdf) · [LaTeX](electronic_companion.tex)
- [Unabridged retained computational appendix](revisions/or-r29-price-state-20260923/retained_evidence.pdf)
- [Point-by-point response](revisions/or-r29-price-state-20260923/RESPONSE_TO_REFEREES.md)
- [Closest-results matrix](revisions/or-r29-price-state-20260923/NOVELTY_MATRIX.md) · [Primary-source audit](revisions/or-r29-price-state-20260923/LITERATURE_AUDIT.md)
- [Derivation provenance and preservation map](revisions/or-r29-price-state-20260923/DERIVATION_PROVENANCE.md)
- [Build report](revisions/or-r29-price-state-20260923/BUILD_REPORT.md) · [Manifest](revisions/or-r29-price-state-20260923/MANIFEST.json)
- [Independent exact verification](revisions/or-r29-price-state-20260923/results/verification.json) · [Extended checks](revisions/or-r29-price-state-20260923/results/extensions_verification.json)
- [Latest R29 referee report, unchanged](reviews/operation_research_referee_report_r29_2026-09-23.md) · [Preceding R28 report](reviews/operation_research_referee_report_r28_2026-09-23.md)

The latest report examined the separate nominal `revision/ndu-operations-research-r29-20260923` branch, which carried R28 unchanged. This `r29-price-state` branch is the actual scientific revision, with a new theorem chain, new experiments and compiled readers. The response covers all 18 latest-report sections as well as the preceding report.

## New results

Theorem 4.1 constructs exact continuous-tier optima from a compact recombining public graph under positive scalar additive payments, separable quadratic reward, and no intertemporal switching. Each continuation cap adds at most one price threshold. The global response knot set has at most 3N elements; a stated polynomial arithmetic bound applies in graph vertices/edges, not the exponentially large history tree. The realized policy carries the running maximum of encountered barriers from at most N+1 labels. This is distinct from reconstructing a certificate from an already solved extensive form.

Theorem 5.1 gives a linear-order necessary-memory family and an exact optimal memory-value frontier. Proposition 6.1 optimizes a globally shared zero-release table through a graph-sized convex program, including edge switching. Proposition 6.2 gives exact fixed-table positive-release oracles and supporting cuts; it does not claim an unproved finite outer master cut count. Corollary 4.2 covers several service coordinates under one scalar commitment.

The deterministic evidence suite has 35 exact graph instances, 14 independent small-tree comparisons, 11 optimized shared-table QPs, 54 feasible supporting-cut queries, and exhaustive partition checks through six regimes. Coupled recombining tests extend to 64 dates and 190 public vertices. Exact certificates are system-level, not per-replicated-block tolerances. Timings are single-run observations and are regenerated with the tables.

The broader switching/promise/release/certification theory and all historical proofs remain. The original negative evidence remains explicit: 83/84 strict-tolerance cache queries refreshed and the measured cache pipeline was not faster. No field calibration, learning superiority, general speedup, or editorial acceptance is claimed.

## Reproduce from repository root

```bash
R=revisions/or-r29-price-state-20260923
python -S "$R/research.py"
python -S "$R/memory_frontier.py"
python -S "$R/table_comparator.py"
python "$R/tree_check.py"            # NumPy and SciPy; independent full-tree checks
python -S "$R/oracle_check.py"
python -S "$R/verify.py"
python -S "$R/verify_extensions.py"
python -S "$R/make_tables.py"
python -S "$R/assemble.py"
bash "$R/build.sh"
python "$R/check_package.py" --write
```

The production solver and exact verifiers use Python's standard library and `fractions.Fraction`. The independent tree optimizer uses NumPy/SciPy; package inspection uses PyMuPDF. A LaTeX installation needs newtx, natbib, endfloat, xr-hyper, and the other packages declared in the source. `requirements-validation.txt` records the additional validation environment.

Read-only validation of published records:

```bash
R=revisions/or-r29-price-state-20260923
python -S "$R/verify.py" --check
python -S "$R/verify_extensions.py" --check
python -S "$R/make_tables.py" --check
python "$R/check_package.py" --check
```

New evidence is accompanied by an independent certificate checker that does not import the production solver. Small-tree matrices/optimization are a separate check and are not used by the production graph algorithm. The isolated publication workflow regenerates evidence and PDFs, then validates the actual final scientific commit in a fresh checkout. A source-receipt commit is not the final scientific validation.

## Format and preservation

The anonymous manuscript uses Operations Research's **Lengthy Manuscript** category: 11-point type, 1.5 spacing, one-inch margins, a text-only abstract of at most 200 words, author–year references, and tables after references. Actual page counts and the companion-length check are in the build report; regular-manuscript 30-page compliance is not asserted.

All earlier tracked files are unchanged except six designated reader entry points, whose byte-identical predecessors are under `revisions/or-r29-price-state-20260923/predecessor/`. All inherited mathematical statements/proofs remain readable in the current print appendices/companion; the unabridged predecessor empirical section has its own compiled appendix. This branch is for another author/referee review, not a submission to the journal system. No other branch is changed.
