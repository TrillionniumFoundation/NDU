# R31 residual literature audit

This audit records the literatures that become closest after R30 concedes classical laminar allocation and normalized memoization.

| Reference | What is inherited / related | What R31 claims instead |
|---|---|---|
| Klimm & Warode (2021), *Mathematics of Operations Research* 47(1):812–846, DOI 10.1287/moor.2021.1151 | Parametric algorithms for separable continuous piecewise-quadratic strictly convex minimum-cost flow; output complexity is tied to breakpoints. | No claim that parametric paths or output-sensitive algorithms are new. R31 proves a public-DAG-specific (O(N)) global knot bound, a matching (Omega(N)) family, matching (Omega(N^2)) total response storage, and compact-input rational bit bounds for its coefficient-event compiler. |
| Harks, Klimm & Peis (2018), *SIAM J. Optim.* 28(3):2222–2245, DOI 10.1137/16M1107450 | Sensitivity analysis for separable optimization over integral polymatroids. | R31 treats polymatroid sensitivity as predecessor geometry/sensitivity literature; its exact theorem is continuous quadratic and concerns the complete dual-price response after public-DAG quotienting. |
| Bean, Birge & Smith (1987), *Operations Research* 35(2):215–220, DOI 10.1287/opre.35.2.215 | Dynamic-program state aggregation. | Aggregation/minimization is not claimed as new; R31 isolates the contract-generated finite transducer and its ordered/tight memory structure. |
| Givan, Dean & Greig (2003), *Artificial Intelligence* 147(1–2):163–223, DOI 10.1016/S0004-3702(02)00376-4 | Equivalence, bisimulation and model minimization for MDPs. | R31 uses standard behavioral minimization terminology and claims only model-specific finite reachability, price-order contiguity, exact optimal-contract coupling and complexity. |
| Peyrière (2023), *Theoretical Computer Science* 951:113774, DOI 10.1016/j.tcs.2023.113774 | Minimum-state equivalent Moore-machine viewpoint. | Backward output/successor refinement is explicitly classical. |
| Zhang (2012), *Operations Research* 60(4):850–864, DOI 10.1287/opre.1120.1056 | Finite policy graphs for an infinite-horizon adverse-selection model and continuation-contract representation. | R31's finite graph is exact for a finite-horizon public-information scalar-contract subclass; it does not claim finite policy graphs themselves as new. |

## Priority boundary used in the manuscript

R31 does **not** claim priority for:
- tree/laminar separable allocation;
- marginal-price reductions;
- normalized memoization;
- generic piecewise-affine parametric solution maps;
- deterministic machine minimization or state aggregation;
- policy graphs as a representation device;
- Benders/supporting-cut principles.

R31 claims the combination of structural statements proved for the accepted-service subclass:
- occurrence-to-public-vertex quotient of the complete normalized response;
- graph-input (O(N)) knot bound with matching (Omega(N)) construction;
- (O(N^2+M)) response storage with matching (Omega(N^2)) construction;
- exact rational coefficient-event complexity;
- a finite reached price transducer whose minimized behavior classes are ordered;
- architecture-conditional minimal *additional writable* alphabet with matching linear lower bound;
- the heterogeneous renewal memory-value frontier and ordered mean-preserving radial comparative static.
