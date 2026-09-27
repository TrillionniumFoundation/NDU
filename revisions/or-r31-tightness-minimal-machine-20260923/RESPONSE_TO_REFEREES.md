# Response to the independent R30 referee report

**Manuscript:** *Accepted Service Adaptation: Tight Parametric Quotients and Minimal Additional Writable Memory*  
**Revision:** R31  
**Revision branch:** `revision/ndu-operations-research-r31-tightness-minimal-machine-20260923`  
**Report answered:** `reviews/operation_research_referee_report_r30_independent_2026-09-23.md`  
**Report branch:** `review/operation-research-r30-independent-harsh-20260923`

We thank the referee for the careful independent audit of R30 and, in particular, for separating the already closed correctness questions from the residual priority and significance questions. R31 addresses that changed burden directly. We do not restore claims that R30 correctly identified as classical. Instead, we make the residual claim sharper and prove the missing complexity statements.

## 1. Residual priority audit: parametric optimization

The referee asked us to compare the complete response representation with modern parametric quadratic optimization and polymatroid sensitivity.

R31 now cites and discusses Klimm and Warode (2021) on parametric piecewise-quadratic minimum-cost flow and Harks, Klimm, and Peis (2018) on sensitivity for separable optimization over integral polymatroids. The manuscript explicitly states that generic piecewise-affine parametric solution paths, output-sensitive parametric algorithms, scalar marginal allocation, and normalized memoization are not claimed as new.

The residual theorem is now stated at the level at which it differs: on the supplied compact public DAG, all response changes arise from local clipping events and at most one contractual reflection barrier per public vertex. This gives a graph-input bound of at most (3N) distinct response knots, exact coefficient-event preprocessing with rational bit bounds, and a complete response representation whose size can be characterized sharply.

## 2. Matching lower bounds for the representation

The referee correctly identified that R30's dense computation was evidence, not a lower-bound theorem.

R31 adds Theorem 3.2, a fully analytic family. For an (n)-vertex deterministic chain with
[
a_i=q_i=1,quad [l_i,h_i]=[0,1],quad r_i=2i,
]
and redundant caps, the response at vertex (i) is
[
R_i(eta)=sum_{j=i}^{n}[2j-eta]_{[0,1]}.
]
The (2n) local clipping points (2j-1,2j) are all distinct and none cancels. Hence the global knot universe has exactly (2n) elements and the total number of affine response segments is exactly
[
sum_{i=1}^{n}{2(n-i+1)+1}=n^2+2n.
]
The family has polynomial-size rational input. Thus the paper's (O(N)) global-knot and (O(N^2+M)) response-storage orders are both worst-case tight up to constants. The experimental dense family is retained only as an implementation illustration.

The pre-existing renewal construction is also promoted into the same tightness story: with (N=k+2) public vertices it needs (K_*=k=N-2) additional writable symbols. The manuscript therefore gives matching linear worst-case order for the writable alphabet as well.

## 3. The memory theorem is now a standard minimization step plus contract-specific structure

The referee observed that R30's backward signature recursion has the form of Moore/Mealy minimization, Myhill--Nerode behavioral equivalence, and state aggregation.

We agree. R31 no longer presents backward partition refinement itself as a new minimization principle. The paper first defines the reached price system as a deterministic output transducer:
- state: a reached pair ((v,eta));
- output: the unique optimal local action;
- input: the realized public transition;
- successor: the child public vertex with the reflected incoming price.

It then explicitly invokes classical behavioral minimization, citing Bean, Birge, and Smith (1987), Givan, Dean, and Greig (2003), and Peyrière (2023).

The model-specific content is isolated and proved separately: a continuous-control contract compiles to a finite reached transducer; behavior classes are contiguous in incoming-price order; numerical price states can collapse strictly; the minimum additional writable alphabet is (K_*=max_v c_v); and the renewal family makes this linear order tight.

## 4. “Minimal memory” is now architecture-conditional by construction

The referee asked us to distinguish writable memory from total controller complexity.

R31 does so in the theorem statement and throughout the title, abstract, and discussion. Three quantities are reported separately:

1. **Additional writable alphabet:** (K_*=max_v c_v), requiring (lceillog_2 K_*ceil) changing bits under the stated public-observation architecture.
2. **Combined reached behavior states:** (C_*=sum_v c_v).
3. **Read-only representation:** the public graph, response coefficients, transition/output tables, and rational precision; the complete response representation is (O(N^2+M)) scalars and (O((N^2+M)S)) bits under the coefficient-height bound.

The theorem is expressly for a fixed root query and a decoder that receives the current public vertex without charging it to the writable register. If a different interface makes inherited physical variables freely observable, the equivalence relation must be recomputed under that enlarged observation. The manuscript no longer uses an unqualified “minimal memory” to mean total controller-state complexity.

## 5. Randomization and the contractual institution

R31 adds the institutional interpretation requested by the referee. The randomized lower bound assumes that participation is evaluated in conditional expectation before a private controller coin is realized and that retained private randomness is charged as writable state.

If instead every private-randomization realization must satisfy continuation feasibility pathwise, the admissible randomized controller class is smaller. The deterministic optimum remains feasible, and the lower bound cannot become weaker. We make no claim that randomization is useless for every *restricted-alphabet approximate* frontier.

## 6. Dynamic-contract finite policy graphs

R31 now discusses Zhang (2012), *Operations Research*, “Solving an Infinite Horizon Adverse Selection Model Through Finite Policy Graphs.”

The comparison is explicit. Zhang's policy graph is an approximation representation for an infinite-horizon adverse-selection model with Markov information. The present paper has public information, a finite horizon, no private reports, and an exact compiler-generated reached transducer for a fixed root promise. We therefore do not claim that finite contract policy graphs are new. The new statement is an exact policy-graph compression and minimization result for this scalar public-information subclass, with explicit response and writable-state complexity.

## 7. Outside-option comparative statics

The referee correctly noted that R30 proved a one-parameter radial result rather than an arbitrary convex-order theorem.

R31 calibrates the claim exactly instead of leaving “dispersion” unqualified. Proposition 4.3 is now titled **Mean-preserving radial spreads increase the value of contractual memory**. It holds for arbitrary positive branch probabilities and every strictly ordered weighted-zero-mean direction (d), over the full admissible range of the scale parameter. The text states expressly that this is not a theorem for arbitrary convex-order, majorization, or variance comparisons between unrelated cap vectors.

This is a precise strengthening of scope, not a retreat from the proved comparative static.

## 8. Bit complexity

The coefficient-event bit theorem is sharpened in five ways requested by the referee.

- Stored rational coefficients and events are reduced after exact arithmetic updates.
- The large common denominator in the proof is identified explicitly as a conceptual height bound, not an implementation object.
- Sorting, event merging, exact comparison, coefficient arithmetic, cap-crossing calculation, and root inversion are all included in the Turing-model bound.
- Exact order tests are cross-product comparisons and rational normalization/gcd work is explicitly charged.
- Response-coefficient height is separated from the potentially larger aggregate execution/certificate height.

The theorem is now named specifically for the coefficient-event compiler. It does not claim a generic bit bound for every implementation of the quotient recursion.

## 9. Computational comparisons after normalized memoization is granted

R31 changes what the computational section is used to establish.

The un-memoized occurrence tree is retained as an independently implemented exact cross-check, not as evidence of algorithmic novelty or superiority over an equivalent normalized memoized reduction. The public-graph promise method is foregrounded because it already exploits recombination and isolates exact continuous closure from graph compression.

The response-density experiments are interpreted against the new analytic tightness theorem rather than used as a surrogate lower bound. Repeated root inversions are tied to a new corollary: after the complete path is compiled, a feasible root promise is inverted with logarithmically many exact comparisons in the stored knot set and a constant number of rational operations. This is the use case for compiling the entire parameterized response.

We do not stage a software timing race against Klimm--Warode or other algorithms defined for a different parametric input. The comparison is theorem-level: parameterization, feasible-set representation, output-size guarantee, and input-size convention are stated explicitly.

## 10. Scope and significance

R31 keeps the exact theorem's assumptions visible: scalar additive commitment, positive payment coefficients, separable strictly concave quadratics, interval controls, exogenous acyclic public transitions, and public-state-sufficient caps. We do not assign the same finite-price theorem to switching, coupled vector commitments, or a continuous outer shared-table design.

The significance case is instead concentrated on the sharp statements that survive the classical reductions:
- a compact occurrence-to-vertex quotient for the whole parametric response;
- worst-case-tight linear knot and quadratic response-storage complexity;
- polynomial exact rational preprocessing for that representation;
- an exact finite reached transducer with classical minimization separated from contract-specific structure;
- worst-case-tight linear additional writable memory;
- an exact heterogeneous memory-value frontier and a precisely scoped radial comparative static.

The broader switching, sensitivity, continuous-state, cache, and deployment results remain preserved in the repository and are not deleted to make the focused paper appear cleaner.

## 11. Preservation and reviewability

R31 branches directly from the independent R30 review branch, so the answered report is in the branch ancestry. R30 scientific files remain untouched. Unchanged shared-comparator, table, and companion modules are copied byte-for-byte into the R31 review directory so that the new revision can be read as one package. The historical R29/R30 derivations remain available and are cited in the provenance file.

The response therefore changes the paper where the referee identified a real gap, while retaining previously established mathematics and negative evidence rather than replacing or suppressing them.
