# R28 closest-results and assumptions matrix

The primary claim is the shared-table continuation-price representation. The classifications below are not claims of priority over an exhaustive literature search.

| Result | Closest established theorem class | Precise conclusion retained or added | Character of contribution | Essential assumptions and boundary |
|---|---|---|---|---|
| Accepted balance / transfer coordinates | Convex subgradients, polyhedral normal cones, tree incidence | Benchmark-relative accepted transfers and restriction versus participation prices | Foundation and operational interpretation | Positive scalar coefficients for the transfer bijection; generic balance allows the broader polyhedral model |
| Optimized release frontier | Strongly concave multiparametric QP; Bemporad et al. (2002) | Exact release rent, curvature and first continuation bottleneck on regular segments | Operational specialization, not a new parametric-QP principle | Polyhedral restrictions and positive curvature; degeneracy needs finite pattern/refinement checks |
| Comparator-adjusted rents / friction | Envelope and convex sensitivity theorems | Difference of separately reoptimized rents, with counterexamples to naive monotonicity | Operational comparative statics | Same accepted class on both sides; directional prices selected from optimal dual sets at degeneracy |
| Unrestricted promise recursion | Recursive contracts, constrained MDP resource states | Exact remaining-payment implementation in the public exit-at-review institution | Institution-specific representation | Additive payments and sufficient public/physical state; not arbitrary nonadditive constraints |
| **Shared-table bridge** | Policy aggregation/nonanticipativity (Rockafellar–Wets 1991), Benders (1962), Bellman resource states | **One globally optimized finite-memory table survives every child recursion; normalized nested participation prices and global table stationarity yield a state-plane certificate for the optimized restricted comparator and its release rent** | **Central mathematical representation and operational design link** | **The same table is chosen ex ante, positive additive conditional payments and Markov caps. Exact finite-horizon dual completeness does not imply polynomial plane discovery or storage.** |
| Continuous lower/upper envelopes | Concave interpolation and stochastic dual cuts; Pereira–Pinto (1991) | Executable deterministic mixtures preserve exact promises and all continuations, with a global a posteriori gap | Contract-specific implementation/certification | Convex feasible policy graphs; indivisible tiers need a different institution; conditional rates require stated regularity |
| Correlated cached comparator | Lagrangian weak duality, separable conjugates and parametric dual sensitivity | Actual correlated query coefficients retained; four nonnegative losses separated | Specialized certificate representation | Fixed box, H, R, D, h and kappa; only declared coefficients and friction scale vary; quadratic loss requires exact anchor and retained priced face |
| Cache governance | Primal–dual brackets and active-set KKT verification | An auditable retain/refresh/uncertified decision, plus a sufficient priced-face test | Computable deployment consequence | Restricted witness must first be feasible; a failed sufficient test proves neither infeasibility nor bad true value; full query costs charged |
| Adaptive continuum certificate | Bernstein polynomial positivity and convex chord bounds | Interior-valid feasibility and gain for a declared cellwise affine policy under correlated coefficient changes | Deployment extension with explicit correlation terms | Fixed quadratic/switching geometry; refine switching cells; test accepted E rows, not comparator-only F rows; nonempty restricted class throughout |
| Net architecture/release design | Finite design choice and concave optimization | Optimize net implementability value, with a certified epsilon-optimal decision | Operational decision model | Implementation costs are specified inputs, not calibrated or causal estimates |

## Primary closest-result sources

Benders JF (1962), *Partitioning procedures for solving mixed-variables programming problems*, Numerische Mathematik 4:238–252, doi:10.1007/BF01386316.

Rockafellar RT, Wets RJB (1991), *Scenarios and policy aggregation in optimization under uncertainty*, Mathematics of Operations Research 16(1):119–147, doi:10.1287/moor.16.1.119.

Pereira MVF, Pinto LMVG (1991), *Multi-stage stochastic optimization applied to energy planning*, Mathematical Programming 52:359–375, doi:10.1007/BF01582895.

The main bibliography retains the existing parametric-QP, convex optimization, recursive contracting, generalized-lasso, and robust-optimization sources. The response and main table explain the residue after those principles are credited, rather than merely saying that they are not claimed as new.
