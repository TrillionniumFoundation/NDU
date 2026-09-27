# Response to the R6 referee report

**Manuscript:** Neural Differential Utility: Accepted Dynamic Service Contracts and Certified Value-Gradient Learning  
**Revision:** R6, September 21, 2026  
**Target journal:** Operations Research  
**Reviewed report:** `reviews/operation_research_referee_report_r6_2026-09-21.md`, review commit `a16435cca2c973331e60908b4c45f505de71e698`  
**New branch:** `revision/ndu-operations-research-r6-20260921`  
**Scientific comparison:** R4 manuscript at `144d61b8f32521aa2431aa21d61a2ee1641adf61`, also present without scientific changes in nominal R5 at `31987afe62c630819de26e19a89dbbbec81a51e8`.

We thank the referee for separating the useful mathematical results from the institutional and computational deficiencies. This is a scientific revision of the manuscript and companion, not a relabeling or an export of R4. It adds an accepted contracting institution, exact optimized comparators, a constrained Pareto-improvement certificate, information-restricted optimization, switching structure, nonquadratic extensions, and an actually trained value-gradient method on a nonmanufactured operational model. Earlier correct results, unfavorable comparators, and historical diagnostics remain available. The report itself is unchanged.

The central new result is explicit. The best continuous fixed tier is 0.5821103917760961, with incremental provider reward -5.87011097304676. An implementable dynamic protocol attains -5.244970661074607 while preserving **exactly** the static customer's utility, discounted fill, and physical cost. Its gain is 0.6251403119721533. An independent rational Bellman-dual upper bound is less than 8.21e-16 above that feasible reward. This establishes that the improvement is not purchased with worse service or a lower customer reservation payoff. It is an instance-specific result, not a universal dominance assertion.

## 1. Revision integrity (report Sections 1 and 13)

**Concern.** Nominal R5 contains no scientific revision; active files remain R4 and the root checklist describes a historical R89 packaging process.

**Response and changes.** We agree with the factual branch comparison. The active `main.tex`, `electronic_companion.tex`, scientific section files, numerical programs, tables, and this response are newly written or substantively revised. All active identifiers are R6. The root README now points directly to the manuscript, companion, response, computations, and results. The earlier root checklist and the exact reviewed manuscript/companion are preserved under `archive/pre-r6/`; the current root checklist identifies only this revision. Earlier review and revision directories are retained rather than rewritten.

**Audit.** Compare this branch with the reviewed commit, inspect the source hashes in `manifest.json`, and run `verify.py`. The checks require substantive source changes and exact scientific certificate properties, rather than treating a successful export workflow as a scientific response.

## 2. Closest literature and incremental novelty (report Section 2)

**Concern.** Five references do not position a service-contract paper against the relevant SLA, switching-cost, or dynamic-contract literature.

**Response and changes.** The introduction now contains a dedicated, substantive literature comparison and 14 references. It discusses Liang and Atkins (2013), Sieke et al. (2012), Katok et al. (2008), Hosseinifard et al. (2022), Caggiano et al. (2007), Abbasi et al. (2022), Plambeck and Zenios (2003), and Hipp and Holzbaur (1988), as well as the previously cited works and Sobolev training. It distinguishes adaptive stocking under a fixed SLA from adaptation of a persistent installed tier; coordination/menu design from operating an already accepted contingent menu; and hidden-action contracting from contractible public-state protocols.

The contribution is not described as the first SLA, first hysteresis policy, new general convex-hull algorithm, or control class beyond MDPs. It is the combination of accepted-contract and optimized-static comparisons, exact customer-preserving improvement, information-restricted optimization, inherited-tier envelope structure, and a connected gradient-based operational deployment. The manuscript identifies which theorem and computation provides each increment, rather than relying on an enlarged action-space inclusion as the substantive finding.

**Locations.** Introduction, related literature; `sections/references.tex`; Sections 2--6.

## 3. A real contractual counterparty (report Section 3)

**Concern.** The provider cannot unilaterally choose a higher tier after observing demand and collect a premium without a contracting institution.

**Response and changes.** Before operations start, a customer accepts an enforceable state-contingent master protocol, an externally available premium/indemnity menu, and observable stock and revision decisions. The protocol can use publicly observed demand regimes and public randomization. Its terms are committed ex ante; the provider does not ex post invent a premium. We define customer surplus as service value plus indemnity less premium, impose a reservation utility, and impose an expected discounted fill commitment. A common initial retainer of 6 is paid under both static and adaptive contracts. It leaves all incremental rewards and comparisons unchanged, and makes provider profit nonnegative for the accepted static and adaptive protocols in the principal example.

These are explicit institutional assumptions: observable and enforceable actions, risk-neutral expected utility, and commitment over the horizon. We do not claim to solve private information, renegotiation, or a moral-hazard problem by relabeling a persistent control. Stock remains a genuine operational decision, and all stock actions are retained when commitments are imposed.

**Locations.** Section 2, customer institution; Section 5, accepted occupation program.

## 4. Optimized fixed-contract benchmark (report Section 4)

**Concern.** The frozen tier 0.5 is not the best static comparator.

**Response and changes.** The main comparator is now the best continuous static tier, optimized exactly by enumerating stock-envelope breakpoints and quadratic stationary candidates. Every class pays the same initial installation cost. We independently reproduce the referee's value and tier. The best grid tier is 0.6, with reward -5.873763513923846; the original 0.5 comparator is retained only as a historical comparison.

The full grid dynamic reward -5.002310554584505 exceeds the continuous static optimum by 0.8678004184622514, not the previously emphasized 0.944747060879 versus 0.5. The difference between those two comparisons is explicitly attributed to better static tier selection.

**Evidence.** `compute.py` (`static_exact`), `results/static_exact.json`, `results/exact_replay.json`, Table 1. Static enumeration has 27 candidate values and uses rational arithmetic.

## 5. Marginal value of adaptivity (report Section 5)

**Concern.** The five previous methods did not isolate the source of adaptation gains.

**Response and changes.** We define the nested deterministic classes static, time-only, time--regime, and full time--regime--inherited tier. Inherited-only feedback from deterministic initial tier is proved value-equivalent to a time schedule; it is not incorrectly treated as a new information increment. Stock is regime responsive in every class, including static contracts.

Time-only and inherited-only policies achieve -5.873763513923846 on this instance. A mixed-integer occupation program with tier selectors shared across inherited states optimizes the time--regime restriction and gives -5.052903963837447. Its gain over the best fixed grid tier is 0.820859550086; adding inherited-tier information contributes 0.050593409253. The MIP solver reports a zero relative gap and matching primal/dual objectives to floating precision. This is labeled a numerical optimization certificate, separately from the rational certificates for the principal outcomes.

**Locations/evidence.** Proposition on information classes; `restricted` in `compute.py`; `restriction_regime.json`, `restriction_inherited.json`, Table 1.

## 6. Switching structure and comparative statics (report Section 6)

**Concern.** Monotonicity alone does not characterize the persistent adjustment decision.

**Response and changes.** We derive exact switch points between adjacent surviving hull tiers. For two tiers separated by d, upward switching requires continuation-adjusted advantage at least lambda*d^2, and downward switching requires advantage strictly below -lambda*d^2 under greatest-tier tie breaking. Thus the inherited tier is preserved on a precisely stated hysteresis interval of width 2*lambda*d^2. We distinguish discrete-menu hysteresis from smooth continuous-menu adjustments and do not silently hold a lambda-dependent continuation value fixed in parameter comparisons.

A revealed-preference proposition proves monotone aggregate exposures in adjustment, maintenance, and liability coefficients for a fixed feasible class. A common intrinsic maximizer gives a sufficient condition for a constant contract at every horizon. An explicit positive-premium counterexample shows failure of regime monotonicity without compatibility. The new sensitivity study varies adjustment, liability, maintenance, premium slope, discounting, and regime persistence, and recomputes each fixed-tier comparator. The conditional scope of comparisons whose participation set changes is explicit.

**Locations/evidence.** `sections/extensions.tex`; `comparative_statics.csv`; Table 3; hull threshold JSON files.

## 7. Service degradation and customer participation (report Section 7)

**Concern.** The original joint policy improved provider reward by sacrificing fill.

**Response and changes.** We preserve that outcome rather than suppress it, but it is no longer the accepted-contract headline. The new finite occupation program imposes service and customer constraints before optimization, with an optional physical-resource cap. It shows a service/participation frontier and a strictly positive provider gain with exactly unchanged fill, customer utility, and physical cost relative to the best continuous static tier.

A feasible rational feedback protocol stocks S=z+2 on every positive-occupancy state. It randomizes at just one state, (t,z,q)=(1,2,0.5), between tiers 0.7 and 0.8, with upper-tier probability 0.21191056706761804. The full feedback map is recorded. Fraction arithmetic verifies all three equalities and a positive exact gain. A separate rational Lagrangian Bellman recursion supplies the matching upper bound. The gap is approximately 8.20e-16 in exact rational arithmetic, not a floating equality tolerance.

The 0.95 fill point is more expensive and fails a zero provider outside option with the common retainer. It is explicitly labeled an operating frontier point, not an accepted contract recommendation. The model therefore exposes genuine service costs rather than declaring all service commitments costless.

**Evidence.** Section 5.3, Table 2; `exact_certificate.py`, `exact_service_certificate.json`, `service_frontier.csv`, `service_policies.json`, `lp_certificates.json`.

## 8. Envelope generality and scaling (report Section 8)

**Concern.** The scalar quadratic algorithm is too specialized for broad computational claims.

**Response and changes.** We extend the envelope to adjustment costs generated by a strictly convex potential. The scalar hull acts on the dual coordinate phi'(q); the original quadratic case and phi(q)=q^2+0.2q^4 are both computed. The theorem also provides the vector affine-envelope identity and permits an additional physical state when inherited q enters only through adjustment. It explains the remaining intercept/integration work and does not equate a vector identity with a linear-time multidimensional hull algorithm.

At 2,048 intervals, the canonical eight-period computation reduces 100,761,624 pairwise tier comparisons to 49,176 inserted lines, excluding preprocessing. Both implementations give identical selected policies and value differences at floating roundoff. Measured speedups are approximately 22 and 13 on this CPU; vectorized enumeration wins on small grids. The operation-count theorem, measured timings, and limitations are separated.

**Evidence.** Dual-coordinate theorem; `envelopes.py`, `envelope_scaling.csv`. Nonlinear matched premium/liability transforms are covered for monotonicity, while the quadratic grid-error argument is not automatically asserted for arbitrary transforms.

## 9. Actual neural learning (report Section 9)

**Concern.** Deterministic smoothing of a known hull is not training.

**Response and changes.** The constructive approximation theorem remains as such. In addition, we train four randomly initialized scalar value networks on a nonmanufactured inventory-contract model. The architecture has 1,281 trainable parameters. Two paired seeds compare value-only supervision with value-and-derivative supervision on the same 2,048 sampled inputs, initial weights, and minibatch schedules, for 6,000 Adam steps each. The learned derivative implements a contractual revision velocity.

All four trained parameter sets and full finite-chain policy evaluations are retained. Gradient supervision reduces initial policy loss for both pairs (0.029062 to 0.014750; 0.020323 to 0.006948). It supplies extra target information and takes more training work. We do not call this an identical-target parameterization advantage or a universal result from two seeds. Worst-case residual budgets, which are much larger than the realized losses, are reported in full.

**Evidence.** Section 6; Table 4; `continuous_learning.py`, four critic weight records, `learned_critics.csv`. A separately named 1,800-step pilot remains historical and is not pooled with the final runs.

## 10. Continuous model connected to operations (report Section 10)

**Concern.** A manufactured quadratic HJB is unrelated to the service-contract example.

**Response and changes.** The new continuous-review model uses the same demand regimes, shortage loss, stock menu, premiums, indemnity and maintenance costs. The inherited tier has bounded inward velocity; the unknown value solves a regime-switching control problem. A scaling proposition derives its local generator from short reviews with flow reward and movement cost scaled as lambda*(theta-q)^2/Delta. This explicitly differs from taking an unscaled limit of the original eight-period jump-adjustment problem.

We solve successively refined nonmanufactured chains (20,40,80,160 tier intervals) with genuinely changing time steps and report the values. The learned-control experiment uses this operational model, not an analytically prescribed value function. The earlier manufactured example and the general stopped-diffusion verification theorem are preserved in the companion as distinct supporting material.

**Locations.** Continuous-review embedding, confined jump verification, upwind chain construction, learning study; EC retained diffusion and manufactured study.

## 11. Conditioning and identical-data parity (report Section 11)

**Concern.** Algebraic division by small volatility does not establish practical superiority, and the earlier least-squares experiment found parity.

**Response and changes.** We retain that parity result and the conditional amplification identity without converting either into a superiority claim. The new learning comparison is different: it changes supervision to include derivative targets relevant to the actual control. Its benefit, cost, additional information, and finite-chain evaluation are stated explicitly. No favorable outcome has been manufactured by hiding the former parity result.

## 12. Identity of Neural Differential Utility (report Section 12)

**Concern.** NDU is not a new admissible control class or a non-MDP operator.

**Response and changes.** The exact expanded-action MDP equality is preserved. The paper now specifies a concrete system: external contractual commitments, joint stock and persistent-tier control, compatible scalar value gradients for continuous reconfiguration, and independent error/accounting checks. The title keeps NDU but identifies accepted dynamic contracts and value-gradient learning rather than implying a separation from ordinary control. Substantive novelty is attached to theorems, the accepted comparison, and implemented learning evidence, not to nomenclature alone.

## 13. Evidence architecture (report Section 13)

**Response.** Active entry points are limited to the manuscript, companion, this response, four scientific experiment/check programs, generated tables, and a compact revision checklist. Earlier hash-ledger and packaging materials remain as historical records and are not used as substitutes for scientific validation. The build verifies source changes, exact certificate properties, cross-references, and PDF production. History is preserved; active navigation no longer directs the referee to an R89 checklist or R4 response.

## 14. Specific technical points (report Section 14)

**14.1 Lattice selection.** The assumptions identify compact ordered action lattices, continuity, greatest maximizer selection, and tail-sum stochastic ordering. The proof spells out the supermodular meet/join argument and how increasing differences order the greatest selections, rather than using an unqualified reference to a “lattice argument.”

**14.2 Interior nonsmooth maximizer.** A standalone supporting-subgradient lemma shows that at an interior local maximizer of convex G(x)-A*x^2+ell*x, both one-sided derivative inequalities force differentiability and the common coefficient to vanish. Endpoints are on the grid; the lower supporting bound then proves the second-order loss even without global concavity. The original rounding theorem is retained.

**14.3 Neural size.** The 27 cubic-ReLU units are counted per fixed time--regime critic and exclude the declared affine/quadratic skip. Twenty-four independent critics use at most 648 such units. This count is not conflated with the new trained network's 1,281 trainable parameters.

**14.4 Verification scope.** The continuum result explicitly assumes admissibility, well-posed confined trajectories, candidate regularity, and uniform residual/boundary control. The new confined jump model has inward velocities and no exit or reflection; the old stopped-domain diffusion theorem continues to charge lateral defects. Finite-chain residual maxima are not promoted into a continuum uniform certificate.

**14.5 Nonmanufactured refinement.** The added operational example has an unknown value, changing mesh and time step, and a true numerical teacher. Refinement differences are reported as numerical evidence, not a general unproved convergence rate.

## 15. Requested reconstruction and preservation (report Sections 15--17)

All twelve reconstruction requests now have concrete destinations in the manuscript or evidence above. In particular, this branch contains a new scientific text, an explicit counterparty, closest-literature comparison, optimized static baseline, value-of-information hierarchy, switching structure, parameter studies, service/participation constraints, an operational continuous model, actual training, and a new point-by-point response.

The positive elements identified by the referee remain: expanded-action equality; compatibility; ordered hull; O(n^-2) grid bound; separate provider, physical and service ledgers; unfavorable fill and physical-oracle comparisons; lateral-boundary verification; and conditioning parity. Their source history is preserved byte-for-byte where archived, and valid technical content remains accessible in the active companion. We ask that the next review assess the newly supplied scientific claims and their evidence rather than the unchanged nominal R5 package.

### What the new results do and do not establish

The rational service-preserving improvement is exact for the specified finite stock/tier instance and the explicitly optimized continuous static comparator. The regime-only optimization and numerical scaling are solver/implementation evidence. The learning experiment is a reproducible synthetic operational study with two paired seeds and complete finite-chain evaluation; it is not a continuum interval certificate, field validation, high-dimensional performance guarantee, or hidden-action mechanism-design theorem. Those distinctions do not remove the positive mathematical and computational results now supplied.
