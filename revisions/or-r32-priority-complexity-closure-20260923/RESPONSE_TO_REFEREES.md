# Response to the independent R30 referee report — R32 closure revision

**Manuscript:** *Accepted Service Adaptation: Tight Parametric Quotients and Minimal Additional Writable Memory*  
**Revision:** R32  
**Branch:** `revision/ndu-operations-research-r32-priority-complexity-closure-20260923`  
**Report answered:** `reviews/operation_research_referee_report_r30_independent_2026-09-23.md`  
**Scientific predecessor:** R31 `revision/ndu-operations-research-r31-tightness-minimal-machine-20260923`

R31 supplied the substantive mathematical response to the independent R30 report. R32 keeps every R31 theorem and proof intact and adds a main-text audit layer so that the residual novelty, tightness, and memory-accounting claims can be verified without reconstructing them from the response letter and companion.

## 1. Parametric optimization and residual priority

We retain the R31 comparisons to Klimm–Warode (2021) and Harks–Klimm–Peis (2018) and continue to treat generic parametric solution paths, scalar marginal allocation, and normalized memoization as predecessor principles. R32 adds Table 1 in the main manuscript, which explicitly separates those inherited principles from the compact public-DAG statements actually claimed here.

The residual claim is unchanged: the supplied public DAG admits a complete normalized response with at most (3N) global knots, (O(N^2+M)) stored response scalars, a matching-order rational lower-bound family, and a compiler-specific polynomial bit bound.

## 2. Matching lower bounds

R31 already added the requested analytic chain family with exactly (2N) global knots and (N^2+2N) stored affine segments. R32 does not substitute experiments for this theorem. The new scope/tightness table places the upper and lower bounds side by side and marks both knot count and response storage as tight in order.

The renewal lower-bound family remains the matching linear example for the additional writable alphabet.

## 3. Classical machine/model minimization

We continue to treat deterministic behavioral minimization as classical and retain the citations to Bean–Birge–Smith, Givan–Dean–Greig, and Peyrière. R32 adds a concise main-text statement that the new content is the contract-generated finite reached price transducer, price-order contiguity, and the exact resource accounting after minimization—not the partition-refinement principle itself.

## 4. Meaning of “minimal additional writable memory”

R32 further hardens the architecture boundary. The new Proposition “Three-layer representation accounting” reports, in one place:

1. read-only compiler representation and its bit complexity;
2. combined reached public-state/class count (C_*=sum_v c_v);
3. minimum additional writable alphabet (K_*=max_v c_v);
4. repeated root-query inversion cost.

It states explicitly that these quantities are not interchangeable. This removes the remaining route by which (K_*) could be read as total controller complexity.

## 5. Randomization convention

The R31 theorem and institutional explanation are unchanged. The exact-optimum lower bound applies when retained private randomness is charged to writable state and continuation feasibility is evaluated in conditional expectation before the private coin is realized. If feasibility is imposed pathwise with respect to the controller coin, the admissible randomized class is smaller and the deterministic lower bound cannot weaken.

No claim is made that randomization is useless for every approximate restricted-memory frontier.

## 6. Dynamic-contract finite policy graphs

Zhang (2012) remains in the main literature discussion. R32's new scope table records “finite policy graphs” as a predecessor representation principle and states the narrower claim: the present public-information scalar subclass yields an exact fixed-query reached policy graph with sharp representation and writable-state accounting.

## 7. Outside-option comparative static

The statement remains exactly calibrated to ordered mean-preserving radial spreads. R32 preserves the explicit sentence that no arbitrary convex-order, majorization, or variance monotonicity theorem is claimed.

## 8. Bit complexity

The coefficient-event bit theorem remains the R31 sharpened theorem. R32's audit table labels it “compiler-specific” so the binary complexity claim cannot be mistaken for a generic theorem about all parametric solvers.

## 9. Computational baselines

The computational section remains unchanged. The unmemoized occurrence tree is an independent exact cross-check, not the basis of the novelty claim. The public-graph promise method remains the more relevant compact-state comparator. R32 adds this boundary to the companion concordance.

## 10. Top-journal significance and scope

We have not enlarged the finite-price theorem by assertion. The assumptions remain: one scalar additive commitment, positive payment coefficients, separable strictly concave quadratics, interval controls, exogenous acyclic public transitions, public-state-sufficient caps, and no switching/coupled vector commitments in the exact compiler.

The significance case remains the sharp theorem package that survives the classical reductions:
- exact occurrence-to-public-vertex quotient;
- worst-case-tight linear knot and quadratic response-storage complexity;
- polynomial exact rational coefficient-event preprocessing;
- finite reached price transducer with standard minimization separated from contract-specific structure;
- worst-case-tight linear additional writable alphabet;
- exact heterogeneous deterministic memory-value frontier and radial comparative static.

## 11. What R32 changes relative to R31

R32 is intentionally additive rather than cosmetic:
- a new main-text referee-facing priority/scope/tightness table;
- a new main-text proposition collecting the three representation layers and their non-equivalence;
- a companion concordance mapping each independent-R30 objection to a theorem/section anchor;
- revised README/checklist and revision labels.

No R31 proof, negative result, historical derivation, or computational evidence is deleted or weakened.

## 12. Preservation and reviewability

The new branch is based on R31, whose ancestry already contains the independent R30 review branch. The referee report, R30 scientific baseline, R31 theorem modules, and all earlier retained theory remain available unchanged. R32 therefore makes the response easier to audit while preserving the full scientific record.
