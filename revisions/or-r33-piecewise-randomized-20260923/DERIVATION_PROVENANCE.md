# R33 derivation and version provenance

## Pinned sources

- Latest independent report: `a017f474619e86be533547acac87a3c8354f64cf`, path `reviews/operation_research_referee_report_r30_independent_2026-09-23.md`.
- Reviewed manuscript: `fdc1ed47d46dc9d3344b8bce47c1670f11dcd475`.
- R33 base: `238bfdb24d93439a545551d275a0c9189dbc017b`, branch `revision/ndu-operations-research-r32-priority-complexity-closure-20260923`.
- New branch: `revision/ndu-operations-research-r33-piecewise-randomized-20260923`.
- Predecessor `main.tex` blob: `58334602f005117266355d19f9355fe092263002`.
- Predecessor `electronic_companion.tex` blob: `d26e9f007c77234125050b44bbc0a1165e010378`.

## Dependence on retained derivations

| New result | Retained input | New mathematical step |
|---|---|---|
| Piecewise quotient | R31 suffix bijection, cap reflection, coefficient events | Inverse-marginal kink plateaus; primitive-piece event budget; same cap-only carried prices |
| Shared circuit | R31 graph recursion and explicit chain count | Post-compilation sharing, exact circuit inversion, explicit output versus shared representation distinction |
| Piecewise certificate | R31 occupation-flow dual equality | Bounded local conjugate rather than a derivative at a join |
| Flow bridge | R31 invertible occurrence allocation map | Tree-flow conservation and transformed local convex costs, primal/dual parameter relation |
| Randomized codebook | R31 heterogeneous renewal frontier and expected-feasibility architecture | Adjacent-chord envelope and optimum branch mean |
| Strict lottery benefit | R31 quadratic cell loss | Exact global two-codeword solution with loss 1/96 versus deterministic 1/8 |

The R31 modules are reused unchanged; R32's accounting discussion is moved into the electronic companion by a derived text/table split without altering the retained source. The old entry-point wrappers and README are archived verbatim on the new branch. Root entry points and README change intentionally; historical theories and adverse results are not deleted.

## External primary sources checked

- Operations Research submission guidelines: https://pubsonline.informs.org/page/opre/submission-guidelines (accessed September 23, 2026). Abstract at most 200 words, text only; equation-free introduction; 11-point minimum, 1.5 spacing, one-inch margins; tables after references. Page counts are reported by the build rather than assumed.
- Klimm and Warode, *Parametric Computation of Minimum-Cost Flows with Piecewise Quadratic Costs*, DOI 10.1287/moor.2021.1151. Publisher online date 2021; volume 47(1), pages 812–846. Source used to distinguish demand-parameter flow paths from dual-price response and avoid claiming a published algorithm was implemented.
- Zhang, *Solving an Infinite Horizon Adverse Selection Model Through Finite Policy Graphs*, Operations Research 60(4), 850–864, DOI 10.1287/opre.1120.1056. Retained as the directly relevant policy-graph contract predecessor.
- Peyrière, *Moore machines duality*, author manuscript arXiv:2106.13124, and the retained published reference. Used only to identify classical machine minimization, not as support for the contract-specific order theorem.

The inherited bibliography contains the additional polymatroid-sensitivity, aggregation, MDP minimization, and dynamic contracting references. This record does not assert an exhaustive literature-priority certification.

## Reproduction boundary

New verification is standard-library exact rational computation. Old large-scale timings remain inherited records, not newly measured runs. Four full-parametric checks use our own exhaustive KKT reference, not published specialized solver software. All instances are synthetic. Runtime measurements are descriptive. Mathematical universal claims rely on the displayed proofs, not finite tests.

## Reader layout preservation

`main_table_layout.tex` is the exact R31 table text with forced inter-table page breaks removed and float placement changed to collected table pages. Every datum and note is retained. The R33 local-response definition is displayed to avoid an overfull theorem-heading line. Full theorem proofs stay in the main article. The predecessor root submission checklist is also archived verbatim. `prepare_reader.py` makes only these idempotent publication changes and fixes decoding of TeX log bytes; mathematical statements are unchanged.
