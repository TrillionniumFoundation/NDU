# Historical preservation and claim map

The snapshot `archive/pre-r4/` has the exact tree SHA `a34671dee3769cbc43d70ed6ba3c70badb8f3348` of reviewed commit `a91b707883b2408de58d9392e4fc546e08a00881`. Git tree reuse preserves every file and directory; it does not select or summarize the original contents. The current R4 source is at the repository root.

| Historical thread | Current treatment | New anchor |
|---|---|---|
| Fixed-preference embedding | Exact frozen-policy restriction; explicit expanded-action equality | Proposition 2.1 |
| Support Bellman non-collapse | Correctly restricted to one affine primitive with distinct exposed slopes | Section 2.1; EC.1 |
| Entropic risk exclusion | Replaced by exact Gibbs variational overlap | Equation (Gibbs); EC.1 |
| Inventory pressure monotonicity | Penalty-only counterexample retained; new external-contract primitive and full dynamic proof | Assumption 3.1; Theorem 3.2 |
| Inner concavity/projection | Retained with verified strong-concavity and normal-cone hypotheses; not assumed globally | EC.1.2 |
| Computability | Exact stock elimination, rational threshold envelope, and stronger quadratic grid bound | Theorems 3.3–3.4 |
| Neural value representation | New constructed smooth critic with analytic uniform and policy bounds | Corollary 3.5; EC.4.4 |
| Physical-cost matching | Retained as restricted newsvendor mismatch, not attributed to an inserted optimizer | EC.2 |
| Actual endogenous-policy physical cost | New exact accounting and oracle-gap budget, executed mixed metrics | Theorem 4.1; Tables 1–2 |
| FBSDE, adjoint, regularization | Retained with shared-noise, value-gradient, boundary-normal, and convergence qualifications | Section 5.1; EC.3 |
| HJB solver certificate | Boundary-complete stopped Dirichlet problem; separate defects and both value comparisons | Theorem 5.2 |
| Cover refinement | New scheme-specific state–time–action calculation; old fixed-state audit retained as such | Proposition 5.3; Table 6; EC.5 |
| Large neural/SKU/solver experiments | Original files retained unchanged; diagnostics are not uniform certificates or new R4 runs | EC.5; archive/pre-r4/reproducibility/ and supplemental/ |
| Hashes, manifests, release/replay guards | Retained as engineering provenance outside theorem stack | EC.5.3; archive/pre-r4/ |
| Prior reports and recorded protocols | Preserved at original paths and in immutable snapshot | reviews/; revisions/; archive/pre-r4/ |

The preserved old root source blob is `2569eee2eb7f80f0a5b31ed07be75d5da9e6a0d3`. The preserved old root PDF blob is `3ed6d3446ad5eafe4f99e8279c28d37ae3a91068`. They are archival, not the active R4 submission.
