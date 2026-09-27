# Response to the latest R29 referee report and the preceding R28 report

**Actual revised manuscript:** *Accepted Service Adaptation: Finite Continuation Prices and the Value of Memory*  
**Scientific revision branch:** `revision/ndu-operations-research-r29-price-state-20260923`  
**Latest report read in full:** `reviews/operation_research_referee_report_r29_2026-09-23.md`, commit `1647d416e7a2806d36b1c9972aff0c0b54779912`.  
**Earlier report and scientific baseline:** R28 report at `af01e2c33f85835e550896985b7cb83b3f4b784f`; scientific R28 at `b53d644be66e9d27bb58cd0f8529aba0c91ec14c`.

## Version reconciliation

The latest report became visible during final remote reconciliation of this work. It reviews `revision/ndu-operations-research-r29-20260923`, not this new `r29-price-state` branch. Its version audit is correct: the nominal R29 branch contained the R28 manuscript unchanged and did not constitute a scientific revision. We do not count that branch, the creation of our new branch, or our compressed-source receipt as a revised manuscript.

This delivery changes the mathematical content, manuscript, companion, bibliography, README, and checklist, and commits all new sources, evidence, three compiled readers, six byte-identical predecessor readers, and the response below. The final scientific commit is checked separately in a fresh checkout. The latest report is copied verbatim into this branch and independently hash-checked against its reviewed commit. The scientific predecessor remains R28: no intervening revised theorem is silently substituted or omitted.

## Responses to the latest report, Sections 1–18

### 1. No scientific delta on the nominal R29 branch

We agree with the factual audit and correct the delivery, rather than contesting the branch label. Main Sections 4–6 are new: constructive finite continuation prices; a necessary-memory theorem and exact retention frontier; and optimized shared-table condensation and exact fixed-table supporting cuts. Section 7 supplies new coupled-graph evidence. The title page and reader entry points now identify the price-state R29 revision. The manifest, Git diff, exact evidence, compiled readers, and final-SHA status distinguish this scientific revision from an upload receipt or an empty renamed branch.

### 2. Representation versus a new consequence theorem

The old bridge is not relabeled as a new algorithm. It is retained in Appendix C as extensive-form-dual representability. Theorem 4.1 proves a different claim: in the stated positive-scalar-payment, separable-quadratic, no-switching institution, a cap truncates a monotone response and creates at most one threshold. The union of all response breakpoints is bounded by 3N on the compact public graph. This produces both an exact construction and a finite realized memory state. The theorem-specific conclusion, rather than generic duality or the existence of a linking variable, carries the revision.

### 3. Constructive discovery, storage and degeneracy

Theorem 4.1 starts with graph primitives, not an extensive-form optimum. A backward piecewise-affine merge constructs every payment response; one scalar inversion gives the root equality price; forward propagation uses the running maximum of state barriers. The proof supplies O((N+M)N log(N+1)) arithmetic operations/comparisons, O(N^2+M) coefficient/graph storage, at most N+1 price labels, and at most N(N+1) public/incoming-price pairs. Rational primitives produce rational coefficients. No rational bit-complexity bound is asserted. Plateau and tail prices, tied barriers, fixed intervals, binding minimum caps, and infeasible promises are addressed explicitly. Independent code verifies these cases. The bound concerns complete payment responses, not an unproved bound on generic Benders value cuts.

### 4. Benders-style master and a genuinely constructive oracle

The root shared-design master is expressly called Benders-style. Proposition 6.2 constructs an exact fixed-table, positive-release value and supporting cut with the finite-price engine, without full-tree dual input. The table is globally fixed during that oracle call. Optimizing a continuously varying positive-release table is not assigned an unproved finite-cut bound. Proposition 6.1 separately condenses the optimized zero-release table to a graph-sized convex program. The standard master and standard QP are not themselves claimed as new optimization algorithms.

### 5. Modern comparison

Section 2 and the closest-results matrix directly compare Girardeau–Leclere–Philpott, Dowson, Füllner–Rebennack, and Lan, as well as the nested resource-allocation work of Vidal–Jaillet–Maculan, Schoot Uiterkamp–Hurink–Gerards, and Wu–Nip–He. Publication/version metadata and primary sources are recorded in the audit. Water filling, policy graphs, linking variables, convex duality, dynamic programming and Benders/SDDP are treated as established. The exact union bound on a recombining contract graph and the derived necessary-memory/retention frontier are the residual claims submitted for scrutiny. This comparison is not presented as exhaustive proof of priority.

### 6. Construction-scale rather than evaluation-only compression

The production algorithm takes a compact graph and a promise. It neither materializes a history tree nor accepts tree multipliers. The induction bounds response storage before the root query is solved. The compact primal-dual certificate is generated after that construction, not imported from an extensive-form solve. The separate full-tree checker is used only for small-instance independent comparison; it is not called by the graph solver. Thus the new claim concerns construction and storage, not only cheap evaluation after an unspecified expensive offline procedure.

### 7. Table dimension and information accounting

We keep K explicit in the zero-release formulation: K+N variables and O(N+M+K) nonzero occurrences. No arbitrary full-history table is claimed to have small K. The public graph may itself be large if externally augmented with a growing history. Theorem 4.1 instead derives its own at-most-N+1-label record on the supplied graph. Theorem 5.1 quantifies both its worst-case necessity and the value attainable with a limited number of labels. The writable-bit statement counts a changing record index, not the read-only table or the numerical precision of its prices. These distinctions prevent table storage, price precision or exogenous graph growth from being hidden in a memory claim.

### 8. Scope of the new theorem versus the retained general framework

The principal narrative is organized around the constructive institution; the broad signed/general-constraint framework remains in print appendices and companion proofs with its original assumptions. Corollary 4.2 extends the construction to several separable service coordinates under one scalar additive commitment, replacing 3N by 2D+N. Independent separable commitments can be treated coordinatewise. Coupled vector promises, arbitrary signed/nonadditive constraints and intertemporal switching are not silently assigned the ordered-scalar result. For those cases the retained general formulation remains a different statement. We pursue the report's requested deeper structural result, rather than deleting valid mathematics or claiming an unsupported generalization.

### 9. Information design from primitives

Theorem 5.1 derives a concrete retention technology: at most m distinguishable symbols at a common future public state. Binding continuation caps make each branch's required accepted payment distinct. Exact implementation needs at least k symbols for a k-branch family. With fewer symbols, the theorem proves that optimal cells are contiguous in sorted caps, derives their exact welfare loss, and computes the optimal frontier in O(mk^2) arithmetic operations. This is not a supplied acquisition-cost function followed by a first-order condition. A cost can subsequently be compared against the derived value, but no cost calibration or optimal-memory-depth theorem for arbitrary institutions is claimed.

### 10. Adverse cache evidence

The abstract and main computational discussion explicitly retain the 83/84 refresh result and the absence of measured cache speed improvement. The full old computational section is reproduced in the retained appendix, not discarded. Weak-duality governance and active-face checks remain useful boundary material; they do not carry a positive speed claim or the new theorem's novelty. No favorable deployment regime is fabricated.

### 11. Genuinely multistage evidence and meaningful comparators

The new exact suite includes 35 instances, nonstationary recombining graphs through 64 dates and 190 public vertices, heterogeneous coefficients, binding continuation caps, a root equality commitment, and positive-release corridors. Fourteen small instances are independently unfolded and checked using exact full-tree constraint matrices and a numerical convex solve. Eleven shared-table comparators are optimized and independently KKT-certified. Fifty-four feasible table/release perturbations test the supporting-cut inequality. The memory study exhausts all set partitions through six regimes and reports larger frontiers through 32 regimes. This evidence is not independent replication of two-period blocks. It is also not advertised as a broad timing victory over tuned SDDP; the claimed computational result is the proved graph-input construction with exact system-level certificates.

### 12. Conditional covering rates and dimension

The inherited dimension-dependent envelope rates are preserved with their conditional regularity assumptions, but are not used to prove Theorem 4.1. The finite-price construction has no promise grid or epsilon-net and does not turn a d-dimensional covering rate into a dimension-free assertion. Multiple coupled commitments and other excluded features retain their original state/approximation burden. The separation of these results is explicit in the main theorem and comparison matrix.

### 13. Focus without deletion

The main narrative follows one chain: finite prices, necessary memory, optimized restrictions, exact coupled-graph evidence. Release sensitivity, rents, switching paths, the broad promise recursion, correlated caches, governance and the adaptive Bernstein test remain in numbered print appendices and companion proofs. The old empirical section and closest-results table are separately compiled without abridgment. The preservation checker verifies every original mathematical block and all original manuscript labels, rather than relying on a statement that material was merely moved.

### 14. Application status

No field data, estimated outside options, switching or memory costs, managerial deployment, or calibrated service system is invented. The manuscript is a theory submission. The operational conclusion is a primitive-driven retention/value frontier, not an empirical adoption claim. The report's alternative theoretical route is addressed by Theorems 4.1 and 5.1.

### 15. Technical observations

The correct shared-table quantifier and factor-two corridor geometry remain. Global cuts remain valid for every feasible table; exact fixed-table cuts now come from the constructive price oracle. The normalization highlighted in Section 15.4 leads to the reflected-price/running-maximum consequence, the finite label bound and the memory lower bound. Release sensitivity and cache governance retain their original qualifications and are not counted as new general optimization results. The adaptive Bernstein condition remains expressly sufficient, not necessary; neither completeness nor a dimension-independent conservatism bound is asserted for it.

### 16. Presentation and positioning

The abstract now leads with the constructive result and necessary memory, not existential extensive-form reconstruction. The retained representation and master have the requested conventional names. Adverse cache evidence is visible immediately. The main argument is consolidated while all older content remains accessible. We use the official Lengthy Manuscript category rather than falsely claim the regular 30-page category. Actual PDF and conservative nonreference counts, anonymous formatting, references and companion length are checked after compilation.

### 17. Requested fundamental advance

We pursue routes A and B: a graph-input finite exact construction in a stated nontrivial subclass, a sufficient finite dual record, a necessary-memory family, and an exact optimal retention frontier. This is a change of the theorem-level center, not another certificate surrounding the unchanged R28 bridge. We do not claim the alternative field-study route C, or delete and split the user's retained material under route D. The proofs, actual scientific diff and independent checks are the objects to be assessed.

### 18. Editorial recommendation

We acknowledge that the latest report rejected the unchanged nominal R29. That recommendation is not evidence about the new price-state theorem before it is read. Conversely, our new derivations and passing software checks are not evidence of editorial acceptance. The package supplies the stronger scientific response and complete preserved record for a further independent assessment of correctness, priority and significance. No journal-system submission or referee approval is claimed.

---

# Detailed response to the preceding R28 report (preserved)

# Response to the Operations Research referee report on R28

**Revised paper:** *Accepted Service Adaptation: Finite Continuation Prices and the Value of Memory*  
**Revision:** R29, September 23, 2026  
**Branch:** `revision/ndu-operations-research-r29-price-state-20260923`  
**Report:** `reviews/operation_research_referee_report_r28_2026-09-23.md` at `af01e2c33f85835e550896985b7cb83b3f4b784f`  
**Scientific predecessor:** R28, `b53d644be66e9d27bb58cd0f8529aba0c91ec14c`.

## Principal response

We address the report's principal scientific objection by changing the mathematical center of the paper, not by renaming the R28 representation theorem. The new Theorem 4.1 constructs the optimum directly from a compact acyclic public graph for continuous tiers, positive additive payments, quadratic rewards, and no intertemporal switching. A continuation cap truncates a nonincreasing payment response and adds at most one price threshold. Consequently the union of all exact response breakpoints has cardinality at most 3N, all responses can be constructed with a stated polynomial arithmetic bound in the public graph, and the optimal policy carries a running maximum from at most N+1 price labels. No full-tree primal or dual optimum is an input to this construction.

Theorem 5.1 establishes that this finite memory is not merely a convenient implementation: a family of recombining agreements requires linearly many distinguishable terminal memory labels. It also derives an exact memory-value frontier, with an ordered-cell characterization and a finite dynamic program. This is a characterization of information retention from continuation-cap primitives, not a first-order condition for an externally assigned implementation cost.

The main narrative now develops this construction, its memory consequence, and its relation to a genuinely optimized shared-table comparator. All previous mathematical statements and proofs remain in print appendices, the electronic companion, and their unchanged historical source paths. The old computational narrative and tables are reproduced without abridgment in a separate compiled retained computational appendix. None of the unfavorable cache or learning evidence is discarded.

These are author-supplied theorems and reproducible checks for independent scrutiny. Exact arithmetic checks are not a substitute for mathematical peer review, and the revision makes no claim of editorial acceptance or exhaustive proof of priority.

## 1. Improvements already acknowledged in the report

We retain the global shared-table quantifier, the factor-two pooling geometry, promise normalization, optimized-comparator master, implementation-cost example, governance rule, and interior-valid adaptive certificate. The six predecessor reader files are copied byte for byte into `predecessor/`. The underlying earlier revision directories and review reports are unchanged. `PRESERVATION.json`, `INHERITED_SHA256.json`, and the package checker make these statements auditable.

## 2. Distinguishing the central result from nested Benders/SDDP

### 2.1 A shared table is a linking design variable

Agreed. The revised literature section identifies nonanticipativity and policy aggregation as established. We do not count the instruction that a table must remain shared as a new theorem. Proposition 6.1 gives its exact graph-sized, zero-release formulation, optimizing the table rather than fixing an arbitrary one. Its quadratic-program solution is conventional. The new contribution is the contract-specific finite-price construction and its consequences, not the existence of a shared variable.

### 2.2 Affine planes and the root master

The retained R28 result is explicitly described as a Benders-style shared-design master and extensive-form-dual representability. In contrast, the production implementation of Theorem 4.1 constructs complete piecewise-affine payment responses from primitives, merging their breakpoints and inserting at most one crossing per cap. It does not discover an unspecified family of value planes.

For a fixed positive-release table, Proposition 6.2 applies this exact algorithm to the intersected corridor intervals. The resulting corridor multipliers provide valid supporting cuts in the shared design. The outer master remains a standard decomposition device; we do not assert an unproved bound on the number of cuts needed to optimize a continuously varying table.

### 2.3 Exactness no longer starts from an optimal full tree

Theorem 4.1 proves the identity R_v(eta)=min(B_v,d_v(eta)) by scalar Lagrangian truncation and backward induction. It then derives the finite breakpoint union, root-price inversion, and the realized price-state policy. `price_solver.py` takes only graph primitives and the root promise. It neither accepts nor solves an unfolded history tree. The independent `tree_check.py` is an external small-instance cross-check, not part of this solver.

### 2.4 A structural consequence of normalized continuation prices

The relation between parent and child prices becomes a constructive reflection: the effective price is the maximum of the incoming price and one state-local barrier. It is therefore a running maximum along the history. This yields (i) at most N+1 memory labels, (ii) at most N(N+1) reached public/price pairs, (iii) a compact exact primal-dual certificate, and (iv) the memory lower bound and frontier of Theorem 5.1. These conclusions were absent from R28.

## 3. Modern decomposition and nested allocation literature

Section 2 now directly compares Girardeau, Leclere, and Philpott (2015), Dowson (2020), Fullner and Rebennack (2025), and Lan's revised working paper (2023). It also compares the closest nested resource-allocation algorithms of Vidal, Jaillet, and Maculan (2016), Schoot Uiterkamp, Hurink, and Gerards (2021), and Wu, Nip, and He (2021). We do not claim that water filling, scalar resource prices, dynamic programming, policy graphs, or convex decomposition are new.

`NOVELTY_MATRIX.md` states the residual result and its scope. `LITERATURE_AUDIT.md` records publication/version metadata and primary-source identifiers. The relevant difference is the exact response-union bound and finite realized memory on a compact recombining contract graph, accompanied by a necessary-memory example and an exact operational retention frontier. Priority and journal-level significance remain questions for independent referees; the bibliography is not presented as an exhaustive novelty proof.

## 4. Exact computational compression

Theorem 4.1 gives a constructive algorithm with O((N+M)N log(N+1)) arithmetic operations/comparisons and O(N^2+M) coefficient/graph storage. N and M refer to the compact public graph, not its exponentially large history unfolding. The statement explicitly distinguishes arithmetic complexity from rational bit complexity. Constant response tails, equality promises at interval endpoints, redundant caps, and infeasible promises are handled in the proof and implementation.

This is a bound for a meaningful specialization, not a claim that arbitrary switching, dense coupling, vector promises, or generic nested stochastic programs admit the same compression. The original general promise recursion and conditional approximation results remain, with their original qualifications. We no longer use their existence statements to support an exact polynomial construction claim.

## 5. Breadth of the stochastic result

The revision takes the report's suggested route of a deeper scalar structural conclusion. It additionally extends the construction to multiple separable service coordinates under one scalar additive commitment (Corollary 4.2), with a 2D+N breakpoint bound. Nonstationary transitions, heterogeneous payments and curvature, binding continuation caps, continuous tiers, and discounting remain allowed.

The model boundaries are explicit: independent separable commitments can be solved separately; coupled vector promises or switching costs do not inherit the ordered scalar reflection. The general retained framework covers those cases under its own assumptions. This is not an unsupported extension of a scalar theorem to a vector order.

## 6. Information design from primitives, rather than only declared costs

Theorem 5.1 derives the information requirement from a family of continuation caps on a three-date recombining graph. All caps bind at the declared root payment. Distinct intermediate caps induce distinct optimal service at an identical terminal public state, requiring at least k terminal symbols for exact implementation.

For at most m symbols, the theorem identifies contiguous groups in sorted caps, derives their exact welfare loss, and computes the optimal grouping in O(mk^2) arithmetic operations. B writable bits implement at most 2^B symbols, giving a finite memory-value frontier without fitting an acquisition-cost curve. This counts the mutable state index, not the precision or read-only storage of the precomputed tables. The original cost-schedule optimization and exact 1/15 release example remain in the retained general framework; they are not promoted to an information-production theorem.

## 7. Cache governance and adverse reuse evidence

The abstract explicitly retains the result that 83 of 84 strict-tolerance queries refreshed without a measured speed advantage. The new theory and experiments do not depend on cache superiority. The original weak-duality governance rule and active-face audit remain valid deployment tools, but are not presented as the central stochastic contribution. Their full original numerical record remains in `retained_evidence.pdf`, and all original data/code paths are unchanged. We do not claim a new refresh-frequency guarantee.

## 8. Experiments on the central coupled stochastic problem

The new 35-instance exact suite includes long-horizon recombining graphs, binding continuation caps, heterogeneous scalar coefficients, corridor-restricted instances, and a root exact commitment coupling successors. Horizons extend to 64 dates; the largest public graph has 190 vertices. Production responses and policies are generated without history enumeration.

The independent verifier checks 147,157 groups of exact response, domain, compact-flow, primal, dual, and equality assertions in the current deterministic suite. Fourteen small cases are also checked against independently built full-tree constraint matrices and a separately solved numerical convex program. Eleven time-only shared tables are optimized and certified by exact KKT records. Fifty-four feasible perturbed table/release queries verify the supporting-cut inequality. The memory experiment exhausts every set partition through six regimes (277 partitions over the tested sizes), not only ordered partitions, and additionally reports frontiers through 32 regimes.

The objective certificate is exact at the system level. There is no tolerance proportional to replicated blocks. Reported solve/audit times are single-run observations with the environment recorded, not evidence of a general speed advantage. The manuscript tables and numerical-error macro are generated from the actual run, not transcribed from a previous machine.

## 9. Scientific focus and preservation of the adaptive certificate

The principal narrative now has one chain: finite continuation prices, necessary retained memory, optimized shared-table comparisons, and coupled-graph evidence. Release-rent paths, friction paths, broad promise-state recursion, correlated certificates, and the adaptive Bernstein result are retained as print appendices and companion proofs. The complete previous empirical section is separately compiled. This is reorganization with a verifiable preservation map, not selective deletion or suppression of adverse results.

## 10. Application and evidence status

The paper remains theoretical. No field observations, estimated outside options, calibrated memory costs, or managerial deployments are invented. The operational result is an exact retention/value tradeoff derived from contract primitives, illustrated synthetically. A calibrated application would be distinct additional evidence; none is claimed here.

## 11. Specific presentation comments

- **11.1:** R28 dual completeness is identified as extensive-form-dual representability. Theorem 4.1 is a different constructive result with a proved finite representation bound.
- **11.2:** The root design master is expressly identified as Benders-style.
- **11.3:** The new merged-state example separates public state from necessary contractual memory. The scalable suite increases horizon and genuine recombination, rather than copying independent two-period blocks.
- **11.4:** Conditional Lipschitz/Lipschitz-gradient approximation rates remain in the general appendices and are not invoked in the finite-price complexity proof.
- **11.5:** The inherited cost comparison is explicitly an optimization over a declared schedule. The new memory frontier instead derives feasible retention classes and their losses from primitives.
- **11.6:** The adverse 83/84 refresh result appears in the abstract and experimental discussion and is fully retained.
- **11.7:** Seven directly relevant modern decomposition/nested-allocation sources are added; all original cited sources are preserved.
- **11.8:** The main narrative is focused, with the complete general mathematics in print appendices. Preservation requires the official Lengthy Manuscript format rather than asserting compliance with the regular 30-page category. The build report records actual pages and the separate companion-size check.

## 12. Requested paper-level advances

The revision pursues alternatives A and B in the report. Theorem 4.1 supplies finite, graph-input exact construction in a stated contract class rather than an existence proof based on full-tree multipliers. Theorem 5.1 supplies necessary memory and an exact primitive-driven retention frontier. Proposition 6.1 shows an optimized shared restriction that actually condenses to public-graph scale; Proposition 6.2 connects fixed positive-release queries to the exact price engine. The central theorem is therefore not unchanged from R28.

## 13. Editorial recommendation

We have not treated the negative recommendation as an instruction to withdraw the result or replace a theorem by a weaker claim. We have addressed its scientific basis with a stronger construction and a new structural consequence, while preserving every earlier derivation and adverse result. The package is submitted for another independent author/referee assessment. The correctness, novelty, and significance of the new theorem chain should be judged on the actual statements, proofs, implementation, and comparison record rather than on a claimed administrative closure of the review.

## Reproducibility entry points

See root `README.md` for exact commands; `BUILD_REPORT.md` and `results/package_check.json` for package checks; `results/verification.json` and `results/extensions_verification.json` for independent exact checks; `DERIVATION_PROVENANCE.md` for the full preservation and derivation map. The final scientific commit has a separate fresh-checkout validation status; a source-upload receipt alone is not that validation.
