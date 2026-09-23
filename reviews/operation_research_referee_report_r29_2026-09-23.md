# Confidential Referee Report for Operations Research

**Manuscript:** *Accepted Service Adaptation: Shared Policy Tables, Continuation Prices, and Certified Design*  
**Branch reviewed:** `revision/ndu-operations-research-r29-20260923`  
**Nominal revision:** R29, September 23, 2026  
**Scientific manuscript actually reviewed:** R28 content carried unchanged into R29  
**Review type:** Independent harsh review against the *Operations Research* bar  
**Area claimed by manuscript:** Stochastic Models  
**Recommendation:** **Reject. I do not recommend another ordinary revision round.**

## Executive assessment

I reviewed the tip of the branch identified above, the journal-facing manuscript, the electronic companion, the R28 shared-table bridge and governance material, the computational evidence, and the immediately preceding referee report.

My first finding is procedural but scientifically important: **R29 is not a scientific manuscript revision.** Relative to `revision/ndu-operations-research-r28-20260923`, the R29 branch adds only the file

`reviews/operation_research_referee_report_r28_2026-09-23.md`.

The manuscript source, electronic companion, computational supplement, R28 bridge, R28 governance section, evidence, bibliography, README content, and delivery checklist are not revised. The README still calls the package “Operations Research R28,” the title page still says “Revision R28,” and the checklist is still the R28 checklist. There is no R29 response-to-referees directory and no R29 scientific delta.

That fact alone means there is no new author revision to evaluate against the previous report. More importantly, an independent re-reading does not change the scientific conclusion. The current paper is technically careful and unusually transparent about its limitations, but the central result remains a **representation of a specialized multistage stochastic program by recursively reorganized extensive-form dual information**, not a new stochastic decomposition theorem with a new constructive algorithm, convergence guarantee, complexity result, or structural consequence of comparable depth.

The paper’s strongest theorem, the “shared-table, continuation-price bridge,” is exact in an ex post sense: one starts from an optimal joint full-tree primal-dual solution, normalizes the tree multipliers by reach probabilities, and reconstructs a recursively tight affine plane. That is a useful identity. It does not establish that the exact plane can be discovered without the full-tree solution, that only polynomially many planes are needed, that a finite cut-generation algorithm converges without tree enumeration, or that the proposed representation has better complexity than a standard multistage stochastic-programming formulation with a here-and-now linking variable and nested Benders/SDDP-style cuts.

The root table LP is, in substance, a Benders-style master for a global design variable. The promise recursion is a resource-state dynamic program. The recursively propagated affine planes are stochastic dual cuts. The exactness proof is recovered from full-tree strong duality and stationarity. The table stationarity condition is the nonanticipativity/linking-variable condition specialized to the paper’s information restriction. The nested continuation-price recursion is interpretable and contract-specific, but the manuscript does not derive from it a new algorithmic or structural conclusion that separates the paper from established multistage decomposition theory.

The computational evidence also fails to carry the paper. The R28 scaling experiment is a direct sum of independent two-period blocks, not a difficult shared-table multistage instance. Under the declared strict tolerance, **83 of 84 queries refresh**, and the cached pipeline is not faster. That is scientifically honest adverse evidence, but it means the cache layer is not demonstrated as a computational contribution.

I did not find a simple fatal algebraic contradiction in the bridge proof, the release-frontier theorem, the cache-governance inequality, or the adaptive Bernstein certificate. My recommendation is negative for a more basic reason: **the paper has not established a sufficiently new OR theorem, algorithm, or operational insight to justify the size and complexity of the manuscript.**

---

# 1. Version audit: the “R29 revision” contains no manuscript revision

This point should be stated explicitly in the editorial record.

The branch comparison R28 (ightarrow) R29 contains one added file and no scientific manuscript changes:

- added: `reviews/operation_research_referee_report_r28_2026-09-23.md`;
- no change to `main.tex`;
- no change to `electronic_companion.tex`;
- no change to `computational_supplement.tex`;
- no change to the R28 shared-table bridge;
- no change to the R28 governance theorem;
- no change to the R28 scaling evidence;
- no change to the R28 bibliography.

The current README begins “Accepted Service Adaptation — Operations Research R28.” The title page in `main.tex` says “Revision R28, September 23, 2026.” The delivery checklist is titled “R28 Operations Research format and delivery checklist.”

Therefore, if R29 is intended as a response to the preceding R28 referee report, it has not yet occurred. The branch number advanced; the paper did not.

I would not ask an editor to treat this as a substantive new round. The most recent scientific object is still R28.

---

# 2. The central theorem is an extensive-form-dual representation, not a new decomposition result

The paper’s identity now rests on Theorem “Shared-table, continuation-price bridge.” I agree that it fixes a real modeling mistake: a time-only or finite-memory table must be shared across all histories assigned to the same information cell. Allowing each child problem to reselect its own table changes the feasible policy class.

But enforcing one global table is the correct nonanticipative/linking-variable formulation of the stochastic program. The theorem must therefore do more than show that the global variable remains global.

The proof has the following structure:

1. fix a shared table;
2. solve a Markov/promise-state recursion;
3. upper-bound child value functions by affine planes;
4. propagate dual prices backward;
5. optimize the common table in a root linear master;
6. prove exactness by starting from an optimal full-tree primal-dual pair and reconstructing a tight recursive plane.

This is recognizably the architecture of nested decomposition.

The manuscript itself partly acknowledges this by saying that Benders decomposition, policy aggregation, and stochastic dual cuts are not claimed as new. The unresolved question is then: **what mathematical conclusion remains after those established components are removed?**

I see the following residual statement:

> for a particular additive scalar continuation-contract institution, the extensive-form dual multipliers can be normalized so that continuation prices obey a path recursion and table-corridor prices aggregate into a global stationarity condition.

That is a clean representation theorem. I do not see why it is a top-journal stochastic-optimization result by itself.

---

# 3. “Dual completeness” is nonconstructive in exactly the place where computational novelty would matter

The phrase “dual-complete” sounds stronger than what is proved.

The EC proof explicitly says:

> Take an optimum of the joint ((x,u)) problem.

It then obtains the relevant tree multipliers, normalizes them, and constructs the recursive planes backward.

Thus exactness is established **after the full extensive-form optimum and its dual information are available**.

This proves an existence identity. It does not prove a new method for obtaining that identity cheaply.

The missing results are precisely the ones that would turn the representation into a new stochastic-programming theorem:

- no bound on the number of planes required for exactness;
- no bound on the number of distinct planes per Markov state;
- no finite-convergence theorem for a cut-generation procedure;
- no proof that exact cuts can be discovered without full-tree work;
- no polynomial storage theorem;
- no polynomial-time result;
- no scenario-tree-independent separation oracle;
- no proof that degeneracy can be handled with a state-local price function;
- no lower-dimensional exact dual state that replaces history-indexed dual choices.

The companion correctly disclaims these claims. That honesty is a strength of the exposition, but it also identifies the scientific limitation.

I would strongly prefer a term such as **extensive-form-dual representability** to “dual completeness” unless the authors prove a constructive discovery theorem.

---

# 4. The root LP is a Benders-style master and should be positioned as such

The root optimization
[
max_{u,v}{v: vle H_{0,a}(q_0,b_0;u,delta) orall a}
]
is a master problem over a global design variable constrained by affine cuts.

That is a Benders-style master.

Calling it merely a “root table-design linear program” avoids the closest established terminology and makes the construction look more distinct than it is.

The important research question is not whether such a master can be written. It is whether the continuation-contract structure gives:

- stronger cuts than generic stochastic decomposition;
- fewer cuts;
- a special separation procedure;
- a finite exact cut set of controlled size;
- monotonicity or ordering that can be exploited;
- a new convergence guarantee;
- or a computational advantage on a nontrivial stochastic instance.

The current paper proves none of those.

---

# 5. The modern multistage stochastic-programming comparison is still inadequate

The bibliography continues to cite the classical origins—Benders (1962), Rockafellar and Wets (1991), Pereira and Pinto (1991)—but omits important modern work that is directly relevant to the current paper’s claimed contribution.

At minimum, the manuscript should confront:

- Girardeau, Leclere, and Philpott, “On the Convergence of Decomposition Methods for Multistage Stochastic Convex Programs,” *Mathematics of Operations Research* 40(1):130–145;
- Dowson, “The Policy Graph Decomposition of Multistage Stochastic Programming Problems,” *Networks* 76(1):3–23;
- Füllner and Rebennack, “Stochastic Dual Dynamic Programming and Its Variants: A Review,” *SIAM Review* 67(3):415–539.

This is not a request for cosmetic citations.

The paper now claims a stochastic decomposition representation, exact recursive prices, stored affine planes, finite-memory public states, continuous resource states, and a global linking design variable. Those claims sit directly inside the modern nested-Benders/SDDP/policy-graph literature.

A top-journal novelty argument cannot stop at the 1962 and 1991 references.

The authors need a theorem-by-theorem comparison explaining why the shared-table/continuation-price construction is not already an instance of a multistage stochastic convex program with state augmentation and linking variables.

The current novelty table asserts a residual contribution but does not prove that the residual lies outside the established framework.

---

# 6. The theorem does not establish computational state compression in the strong sense suggested by the narrative

The manuscript repeatedly and carefully says that it avoids a “query history vector.” That statement is formally true once a certified collection of state planes and witnesses has already been constructed.

But the exact plane proving completeness may encode information obtained from a full history-tree dual solution.

Therefore there are two very different claims:

1. **representation claim:** an exact extensive-form dual solution can be reorganized into a recursive certificate;
2. **computational claim:** an exact certificate can be generated and maintained with complexity controlled by the stochastic state rather than the history tree.

R28 proves the first, not the second.

The difference is fundamental.

If the number of planes can grow with the number of histories, and if discovering the exact plane can require solving the extensive form, then the representation can be history-free at evaluation time while still being history-scale in construction.

The paper acknowledges this in the companion, but the abstract and main narrative continue to benefit rhetorically from the word “state.”

For Operations Research, I would want one of the following:

- a bound on plane growth;
- a finite convergence theorem;
- a complexity theorem;
- a structural single-cut result;
- or a computational experiment showing a genuine reduction on a difficult multistage problem.

None is present.

---

# 7. The shared-table dimension can itself erase the claimed compression

The table (uin[0,1]^K) is global.

For a fixed finite-memory architecture, (K) may be manageable. But the paper does not characterize how (K) scales as the allowed memory class becomes richer.

For a (d)-step history memory, the number of table cells can grow with the number of admissible public-memory states. If memory is enlarged toward full history, (K) can itself inherit combinatorial growth.

This matters because the root master has (K+1) variables, every stored plane carries a (K)-dimensional coefficient, and the companion’s own storage formula is
[
O(TS_0M_0P_0(K+1)).
]

Thus the paper has not proved that the global table is a low-dimensional design object over the model classes that generate the largest value of information.

The representation can move combinatorial complexity from history-indexed decisions into table dimension and plane count.

That may still be useful. It is not a generic compression theorem.

---

# 8. The theorem that is supposed to unify the paper applies to a narrower model than the inherited framework

Earlier sections allow a broad finite-dimensional convex program with:

- vector decisions;
- signed payment coefficients;
- arbitrary retained accepted inequalities and equalities;
- general pooling matrices.

The shared-table bridge then specializes to:

- scalar tiers;
- positive payment coefficients;
- additive payment promises;
- public Markov transitions;
- Markov continuation caps;
- one particular quadratic-plus-switching stage reward;
- finite-memory pooling through a common table.

The paper correctly says the scalar bridge does not automatically extend to signed or nonadditive accepted constraints.

This creates a scientific identity problem.

The broad framework motivates many inherited results, but the theorem that is supposed to connect the paper’s parts is valid only on a narrower institution.

Either the bridge should be generalized substantially—e.g. to vector additive commitments and a broader class of shared design restrictions—or the manuscript should be narrowed to the scalar institution and remove a large amount of inherited machinery.

At present the paper wants the breadth of the general convex framework and the structural interpretation of the specialized scalar bridge simultaneously.

---

# 9. The architecture-design section is mathematically correct but too elementary to supply operational novelty

The “endogenous” architecture problem is
[
max_{j,delta}{V_{M_j}(delta)-C_j(delta)},
]
with a declared cost schedule such as
[
C_j(delta)=f_j+c_jT|M_j|+a_jdelta+b_jdelta^2/2.
]

This is a valid decision model.

But the information-technology or organizational cost function is an input. The paper does not derive it from an acquisition technology, staffing model, sensor design, storage architecture, audit workload, learning process, or empirical cost calibration.

Consequently the structural result reduces to:

- compute a value frontier;
- subtract a supplied cost;
- compare designs;
- equate marginal value and marginal cost on a smooth segment.

That is not a new information-acquisition theorem.

The exact (delta=1/15) example is a useful illustration, not a paper-level contribution.

---

# 10. Cache governance is correct weak duality, and the paper’s own evidence is adverse

The governance result
[
0le U-K_	hetale U-W_	heta(z^w)
]
is immediate once (W_	heta(z^w)le K_	hetale U).

It is a sensible operational rule, but it is not a substantial theorem.

The face-retention test is also standard convex/KKT active-set verification.

The empirical result is more important:

**83 of 84 strict-tolerance queries refresh.**

The cache pipeline is not faster under the reported protocol.

This is not a minor caveat. It is the central deployment result of the R28 cache experiment.

The manuscript should therefore not present caching as a positive computational contribution unless a meaningful operating regime is found in which:

- refresh frequency is substantially below one;
- certificate width remains useful;
- and total cost is lower than the fresh benchmark at matched quality.

Otherwise the cache material belongs in a robustness appendix as a negative or boundary result.

---

# 11. The scaling study does not stress the shared-table stochastic recursion

The R28 scaling family is a direct sum of independent two-period blocks.

This design is good for exact rational accounting. It is weak evidence for the theorem that defines the paper.

It does not stress:

- long horizons;
- recombining public state;
- deep continuation-price propagation;
- multiple promise-state dimensions;
- shared tables coupling many descendants;
- plane proliferation at the same public state;
- recursive cut generation;
- large root-master dimension;
- branching-dependent child allocation;
- or exact-versus-approximate state compression.

The fresh comparator is specialized and exact because the direct-sum structure is deliberately simple.

Therefore the experiment mainly verifies the implementation of the certificate accounting. It does not demonstrate that the proposed bridge is computationally useful on the stochastic problem class for which it is advertised.

A convincing experiment would compare against a competent extensive-form/nested-Benders/SDDP baseline on a genuinely multistage instance where the shared table materially couples many scenarios.

---

# 12. The continuous-state approximation result exposes a curse of dimensionality rather than resolving it

The companion’s conditional rate is explicit:

- (O((L/arepsilon)^{d_s})) under Lipschitz regularity;
- (O((M/arepsilon)^{d_s/2})) under smoothness.

This is mathematically honest.

It also means that the continuous promise/tier state can face the standard curse of dimensionality.

Additional additive commitments add state dimensions. The shared table adds design dimensions. Nonsmooth active-set changes remove the smooth rate.

Therefore the manuscript should not imply that the bridge makes continuous-state stochastic control tractable in a broad sense. It provides certified approximation machinery under regularity assumptions, with dimension-dependent covering costs.

That is useful methodology but not a complexity breakthrough.

---

# 13. The adaptive Bernstein certificate is technically reasonable but scientifically orthogonal

The adaptive-policy proposition addresses a real issue: if both coefficients and a policy vary affinely with a parameter, vertex feasibility does not imply interior feasibility because correlated products become quadratic.

The Bernstein cross-coefficient test is a legitimate sufficient condition.

But this result is not conceptually necessary for the shared-table bridge.

It is a separate robust-certification result.

The manuscript has accumulated too many theorem families:

1. release-frontier sensitivity;
2. continuation-rent comparative statics;
3. friction paths;
4. promise-state recursion;
5. continuous-state envelopes;
6. shared-table dual representation;
7. architecture costs;
8. reward-only cache envelopes;
9. correlated cache bounds;
10. cache governance;
11. adaptive Bernstein certification;
12. multiple generations of synthetic evidence.

The result is an omnibus paper rather than a single sharp contribution.

The R28 bridge should have enabled major consolidation. Instead, nearly every inherited result remains.

---

# 14. The service-contract application still does not independently carry the paper

The application is coherent, but it remains synthetic.

There is no:

- field dataset;
- calibrated service system;
- empirically estimated continuation outside option;
- calibrated switching cost;
- calibrated information/memory cost;
- managerial study of actual architecture choice;
- or case in which the proposed representation changes a real operational decision relative to a standard stochastic-programming model.

A theoretical *Operations Research* paper does not need field data if its theorem is sufficiently strong.

Here that absence matters because the main stochastic theorem is, in my assessment, too close to established decomposition machinery.

The paper therefore lacks a second independent reason for publication.

---

# 15. Technical observations

I record these to distinguish “I disagree with the novelty claim” from “the mathematics is obviously wrong.”

## 15.1 Shared-table quantifier order

The paper is correct that
[
max_u sum_j p_j V_j(u)
]
cannot generally be replaced by
[
sum_jp_jmax_{u^j}V_j(u^j).
]

The latter changes the policy class. This is an important modeling warning, but it is fundamentally a nonanticipativity/linking-variable issue.

## 15.2 Corridor elimination

For one scalar table entry in a memory cell, the common-intersection condition produces pairwise spread bounds with the factor (2deltaomega_c). The R28 example appears internally consistent on this point.

## 15.3 Root-master upper bound

If every stored root plane is valid for every admissible table, then maximizing the pointwise minimum over the common table yields a valid upper bound. I do not object to this weak-duality step.

My objection is that exactness of the plane class is proved by importing the extensive-form optimum.

## 15.4 Continuation-price normalization

The relation
[
eta_j-chi_j=eta_n
]
is a clear contract-specific normalization of nested cap prices. This is probably the most interesting structural identity in the paper.

The missing step is a consequence theorem showing that this identity yields something unavailable to a generic multistage convex-program formulation.

## 15.5 Release-frontier theorem

The global concavity/piecewise-quadratic argument is plausible under the stated strongly concave objective and polyhedral parametric feasible set. The local regular-cell formula is also presented with the appropriate active-set qualifications.

This theorem is useful but belongs to standard multiparametric convex/QP sensitivity once the operational restriction is fixed.

## 15.6 Cache-governance inequality

The inequality is correct but essentially weak duality plus feasibility.

## 15.7 Adaptive Bernstein feasibility

The off-diagonal Bernstein coefficient is the right object for a quadratic slack generated by affine coefficient and affine policy interpolation. It is sufficient, not necessary, and can be conservative. The paper does not characterize this conservatism or its scaling with parameter dimension.

---

# 16. Presentation and positioning issues

These are not the reason for rejection, but they matter.

### 16.1 The abstract still overweights “exact representation”

The exactness is existential and per finite extensive-form instance. The abstract should make explicit that exact tight planes can require full-tree dual information and that no constructive polynomial discovery result is proved.

### 16.2 “Dual-complete” is too strong a name

The term invites an algorithmic reading. “Extensive-form-dual representable” would be more accurate unless a constructive theorem is added.

### 16.3 The root LP should be called a Benders-style master

Using established terminology would make the novelty boundary more transparent.

### 16.4 The negative cache result should be visible earlier

If 83/84 queries refresh and the cached pipeline is not faster, that should appear prominently wherever the cache is advertised.

### 16.5 The paper remains conceptually overlong

The formal page count is not my main concern. The scientific message is.

There are too many partially independent theorem families for one general-journal paper.

---

# 17. What would change my assessment in a fundamentally new submission

I do not recommend another additive R30 that preserves the current architecture and adds more certificates.

A substantially different submission could become interesting if it delivered one of the following.

## A. A genuinely new stochastic-decomposition theorem

For example:

- a bounded number of exact planes per public state under a meaningful continuation-contract structure;
- finite exact cut generation without materializing the history tree;
- a polynomial bound for a nontrivial subclass;
- a state-local exact dual recursion whose price state is sufficient;
- a provable reduction in scenario-tree complexity relative to standard nested decomposition.

## B. A strong structural information-design theorem

For example:

- characterize optimal memory depth from primitives;
- prove a monotonicity or threshold theorem for when public information should be retained or pooled;
- derive an endogenous information architecture rather than supplying its cost schedule;
- show how continuation participation qualitatively changes an optimal sensing or memory design.

## C. A compelling real operational application

A calibrated service system could justify a synthesis of known optimization machinery if the synthesis produces a new managerial conclusion of independent importance.

## D. A much narrower methodological paper

The authors could separate:

- the shared-table stochastic representation;
- the release/sensitivity theory;
- and the correlated/adaptive certificate machinery.

Each could then be compared with the correct specialist literature and developed to a sharper result.

---

# 18. Recommendation to the editor

The current branch should not be treated as a substantive new revision because it contains no new scientific manuscript content relative to R28.

On the merits of the unchanged paper, I recommend **Reject**.

The reasons are not package quality or mathematical sloppiness. The package is unusually auditable, and the manuscript is commendably explicit about adverse computational evidence and theorem limitations.

The problem is the publication-level scientific contribution.

The central bridge is an elegant specialization and reorganization of known multistage stochastic-programming ideas: a shared linking variable, promise/resource-state recursion, dual cuts, a Benders-style master, and full-tree strong duality. The exactness proof begins from the very extensive-form primal-dual solution whose history-scale computation the narrative would like to avoid. No new constructive exact algorithm, finite-convergence result, plane-complexity theorem, or strong operational structure theorem is proved. The cache contribution is empirically adverse under strict tolerances, the scaling experiment does not stress the central multistage problem, and the application remains synthetic.

I therefore do not see a plausible ordinary-revision path from this manuscript to the *Operations Research* bar. A publishable successor would need a different theorem-level center of gravity, not another layer of certification around the same representation.

**Decision recommendation: Reject.**

