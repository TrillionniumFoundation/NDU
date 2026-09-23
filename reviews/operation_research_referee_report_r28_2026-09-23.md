# Confidential Referee Report for Operations Research

**Manuscript:** *Accepted Service Adaptation: Shared Policy Tables, Continuation Prices, and Certified Design*  
**Revision reviewed:** R28, September 23, 2026  
**Reviewed branch:** revision/ndu-operations-research-r28-20260923  
**Reviewed scientific tip:** b53d644be66e9d27bb58cd0f8529aba0c91ec14c  
**Review type:** Independent harsh review of the current revision tip  
**Area claimed by the manuscript:** Stochastic Models  
**Recommendation:** **Reject. I do not recommend another ordinary revision round at Operations Research.**

## Executive assessment

R28 is a serious and technically competent response to the previous report. The authors did what that report explicitly asked them to do: they built a theorem-level bridge between a precommitted information restriction and the promised-payment recursion; they introduced a shared table that must survive every successor problem; they propagated continuation and corridor prices recursively; they added a root table master problem; they supplied a dual-completeness argument; they added an implementation-cost decision, a cache-governance rule, an adaptive-policy certificate, and a scaling experiment that charges refreshes instead of hiding them. They also retained the unfavorable learning evidence and the degenerate cache counterexample. The package remains unusually reproducible.

I therefore do **not** repeat the earlier criticism that the paper consists of disconnected pieces. R28 has connected them.

My recommendation is nevertheless negative because the new bridge does not, in my view, cross the Operations Research novelty threshold. Once translated into the language of multistage stochastic programming, the core construction is a here-and-now shared design variable coupled to recourse decisions by nonanticipativity/policy aggregation; a Bellman/resource-state recursion for additive commitments; recursively propagated affine value bounds of Benders/SDDP type; and an exact supporting cut recovered from an optimal extensive-form primal-dual solution by strong duality and stationarity. The manuscript now proves this synthesis carefully, but it does not establish that the synthesis itself is a new theorem class rather than a specialized re-expression of established decomposition machinery.

That distinction is decisive. The R27 report said that if the paper could not produce a mathematically or operationally nontrivial bridge, novelty would become the rejection issue. R28 does produce a bridge, but the bridge is not sufficiently differentiated from nested Benders/SDDP plus nonanticipativity and standard duality. The manuscript's own proof makes this visible: exact dual completeness is obtained by **starting from an optimal full-tree primal-dual pair**, normalizing its multipliers, and constructing the recursive plane backward. That is an elegant representation theorem, but it is not a new compression algorithm, a new finite-convergence theorem, a new complexity theorem, or a new duality principle.

The auxiliary additions do not rescue the top-journal case. The implementation-cost problem is an exogenous cost subtraction with a first-order condition on regular segments. The cache-governance proposition is a direct weak-duality width bound, and the optional face test is a standard active-set KKT verification. The adaptive continuum result is a useful Bernstein-coefficient sufficient certificate, but it is a separate certification lemma rather than the paper-defining stochastic insight. Most importantly, the new scaling study refreshes on **83 of 84 queries** and reports that the cached pipeline is not faster. That negative evidence is scientifically honest, but it removes the strongest possible computational justification for the cache layer.

I found no clear fatal algebraic contradiction in the new R28 bridge, governance, or adaptive certificate. My rejection is therefore primarily about **novelty, scientific identity, and breadth of consequence**, not about package integrity.

---

# 1. What R28 genuinely fixes

R28 deserves credit for resolving several concrete deficiencies in R27.

1. **The full-vector and state-recursion engines are now connected.**  
   The shared-table variable is global rather than reselected child by child. This is the correct quantifier order for a precommitted information restriction.

2. **The zero-release pooling restriction is represented correctly.**  
   Eliminating a shared scalar table within a cell yields pairwise tier differences bounded by twice the corridor radius. The factor-two issue is handled explicitly rather than buried.

3. **Continuation participation enters the recursive dual object.**  
   The normalized relation between parent and child payment prices makes the role of nested continuation caps visible rather than treating every accepted row as an arbitrary matrix inequality.

4. **The optimized restricted comparator is certified through a table master.**  
   The upper bound is not merely a fixed-table bound. The root maximizes the minimum of stored affine planes over the same globally shared table.

5. **The authors are explicit about what is and is not compressed.**  
   R28 states that exact state sufficiency does not imply polynomial plane discovery, polynomial storage, or dimension-free accuracy.

6. **The information hierarchy is turned into a declared design problem.**  
   Installation, memory, and release costs are introduced as inputs and the net design is optimized.

7. **Cache reuse now has a governance rule.**  
   A feasible witness produces an auditable upper bound on cache error; failed tests trigger refresh or an uncertified outcome rather than being interpreted optimistically.

8. **Uniform certification now covers a declared adaptive policy.**  
   The new Bernstein cross terms correctly address the fact that vertex feasibility alone does not certify products of affine coefficients and affine policies.

9. **The scaling study reports adverse outcomes.**  
   Refreshes, cache memory, witness costs, audit costs, and the lack of a speed advantage are visible.

These are all improvements. The problem is that they mainly make the paper a cleaner and more complete synthesis of known machinery. They do not yet show a new OR result of comparable depth to the amount of apparatus required.

---

# 2. The central shared-table theorem still looks like nested Benders/SDDP with a here-and-now design variable

This is the main scientific objection.

Theorem “Shared-table, continuation-price bridge” has four ingredients:

- a global table chosen before uncertainty resolves;
- state recursion for inherited tier and remaining additive payment;
- affine upper planes propagated backward;
- a root master over the shared table.

Those are precisely the ingredients one expects when a multistage stochastic program contains a here-and-now linking variable together with dynamic recourse.

The manuscript cites Benders (1962), Rockafellar and Wets (1991), and Pereira and Pinto (1991), but it does not yet demonstrate that the displayed bridge is more than their familiar architecture specialized to this contract.

## 2.1 Shared table = a nonanticipative/linking design variable

A time-only or finite-memory table is a collection of first-stage design coordinates whose values must be used consistently by all scenario descendants assigned to the same information bundle. The statement that childwise reoptimization gives the wrong value is correct, but that is exactly what nonanticipativity and policy aggregation are designed to prevent.

The paper currently treats “the same table survives every child recursion” as a central novelty statement. I see it instead as the correct formulation of the optimization model.

That distinction matters. A top-journal theorem should do more than prove that the correctly formulated shared variable must remain shared.

## 2.2 The affine planes are Benders/SDDP cuts in different notation

The recursive inequality

H_t(q,b;u,delta) = A_t q + B_t b + gamma_t^T u + k_t delta + C_t

is an affine value-function upper bound generated by dual prices. The root problem maximizes a variable v subject to v being below every stored plane. With the sign convention induced by maximizing a concave reward, this is the natural mirror image of a Benders/SDDP cutting-plane master.

The proof itself confirms that interpretation. Child planes are inserted, linking equalities and inequalities are priced, scalar variables are maximized out, and the resulting coefficients are propagated backward. This is nested decomposition.

The manuscript needs a theorem that says what is **mathematically unavailable** in generic multistage stochastic convex programming and becomes available only because of the continuation-contract structure. At present I do not see such a conclusion.

## 2.3 “Dual completeness” is recovered from the full extensive-form dual

The strongest-sounding new claim is finite-horizon dual completeness. But the proof begins with an optimal joint tree primal-dual pair, normalizes those prices by reach probabilities, and then reconstructs a tight root plane.

That establishes a useful representation identity. It does **not** establish:

- that an exact plane can be found without solving or implicitly resolving the extensive form;
- that only polynomially many planes are needed;
- that a finite algorithm discovers the exact plane in polynomial time;
- that the number of distinct state planes is bounded independently of history count;
- that the representation is stronger than extensive-form strong duality plus recursive elimination.

Indeed, the companion explicitly disclaims all such statements.

So the exactness theorem proves that if the full-tree optimum and dual multipliers are known, then their dual information can be rearranged into a tight recursive certificate. I do not regard that as sufficient novelty for Operations Research unless the authors can identify a nonstandard dual object or a nontrivial consequence that generic nested decomposition does not already provide.

## 2.4 The normalized continuation-price recursion is structurally interpretable, but not yet shown to be new

The relation

eta_child - chi_child = eta_parent

is a nice expression of how nested participation prices accumulate. It depends on the subtree incidence structure and conditional-probability normalization. That is the most contract-specific part of the proof.

But the paper does not show that this relation yields a new algorithm, a new monotonicity theorem, a new closed-form structural property, a new dimensional reduction, or a new comparative-static conclusion unavailable from the generic extensive-form dual.

At present it reads as an interpretable normalization of the dual multipliers generated by nested linear constraints.

That is valuable exposition. It is not yet a paper-defining theorem.

---

# 3. The modern stochastic-programming comparison is still materially incomplete

The closest-results table is an improvement, but it is too narrow for a paper whose central claim is now a stochastic decomposition representation.

The bibliography jumps from Pereira and Pinto (1991) directly to the current construction. That leaves out a large modern literature on nested Benders, SDDP, convex multistage decomposition, state augmentation for dependent processes, policy graphs, exact/dual bounds, and cut management.

At minimum, the paper should confront the following classes of results directly:

- Girardeau, Leclere, and Philpott (2015), *On the Convergence of Decomposition Methods for Multistage Stochastic Convex Programs*, Mathematics of Operations Research 40(1):130–145;
- Dowson (2020), *The Policy Graph Decomposition of Multistage Stochastic Programming Problems*, Networks 76(1):3–23;
- Füllner and Rebennack (2025), *Stochastic Dual Dynamic Programming and Its Variants: A Review*, SIAM Review 67(3):415–539;
- the nested-Benders/SDDP literature surveyed there, including variants for Markov or stagewise-dependent processes, nonlinear convex stage problems, exact bounds, and state augmentation.

This is not a bibliography-style request. It is central to judging novelty.

The paper repeatedly says that Benders, policy aggregation, and stochastic dual cuts are not claimed as new. That is good. But once those components are removed, the manuscript must identify a residual theorem that survives comparison with **modern** decomposition theory, not only with the 1962/1991 originals.

I am not convinced that the current “one shared table + promise state + nested prices” residual is outside the expected scope of a multistage stochastic convex program with linking variables and resource states.

---

# 4. The theorem does not deliver exact state compression in the computational sense suggested by the narrative

The manuscript is careful, but the title, abstract, and introduction still create a stronger impression of compression than the theorem earns.

The exact recursive certificate exists because the authors can construct state planes from full-tree dual multipliers. However:

- multiple planes may be needed at one public state;
- the number of such planes has no polynomial bound;
- exact discovery can require full-tree work;
- the table dimension K is additional;
- the continuous promise and inherited-tier state still requires approximation unless actions/promises are finite;
- child-allocation combinations can grow rapidly;
- a certificate DAG may still carry history-scale information in the number of distinct planes.

Therefore “no query history vector” is true only after an appropriate family of planes/witnesses already exists. It is not an exact theorem saying that the full optimization can be solved with state-space complexity independent of the scenario tree.

This distinction should be central to the editorial assessment because it determines whether the bridge is merely representational or algorithmic.

A genuinely stronger paper would prove one of the following:

1. a bound on the number of state planes needed for exactness under a meaningful structural condition;
2. finite convergence of a plane-generation algorithm that never materializes the history tree;
3. a complexity bound in horizon/state dimension for a nontrivial model class;
4. a state-local dual recursion whose optimal prices are functions of the sufficient state and do not require history-indexed selection;
5. a theorem showing that the shared-table restriction reduces, rather than merely rearranges, the computational burden.

R28 proves none of these. It explicitly says so.

That honesty is commendable, but it also reveals that the central result is a representation theorem whose computational consequence remains conditional.

---

# 5. The Stochastic Models case is still narrow

The revised theorem finally uses stochastic structure in its proof, so I no longer object that the Stochastic Models label is purely cosmetic.

I still question whether the contribution is broad enough for the area.

The bridge uses a highly specific institution:

- finite horizon;
- exogenous public Markov state;
- positive scalar payment coefficients;
- additive payment promises;
- Markov continuation caps;
- scalar continuous tiers;
- a quadratic stage reward;
- fixed switching geometry;
- a finite-memory table;
- corridor release around that table.

The manuscript itself correctly says that signed, nonadditive, or more general accepted constraints do not inherit the scalar bridge automatically.

That is a severe boundary. The full-vector model in earlier sections is much more general, but the new unifying theorem does not cover that generality. In other words, the theorem that is supposed to unify the paper works only on a narrower subclass than much of the paper's inherited machinery.

For a Stochastic Models paper, I would want either:

- a more general stochastic theorem that handles vector additive commitments and a broader class of shared design restrictions in a principled way; or
- a much deeper structural conclusion inside the scalar institution.

The current result is exact but narrow.

---

# 6. The “endogenous information/design” addition is too thin to carry operational novelty

R28 responds to the previous concern by assigning an architecture j a cost such as

C_j(delta) = f_j + c_j T |M_j| + a_j delta + b_j delta^2 / 2

and maximizing V_j(delta) - C_j(delta).

This is mathematically fine.

But operationally, it does not yet model how information or organizational flexibility is produced. The cost is simply declared as an input. There is no technology connecting sensors, memory, staffing, software, review frequency, data retention, or contractual complexity to the feasible policy class. No uncertainty in implementation cost is modeled. No fixed-cost combinatorics or technology substitution is analyzed. No empirical magnitude is supplied.

As a result, the “endogenous design” theorem reduces to:

- subtract a user-specified cost from the already-computed value frontier;
- compare discrete alternatives;
- on a smooth segment, equate marginal value and marginal cost.

That is correct but elementary.

The exact example in which unit linear release cost selects delta = 1/15 is useful pedagogically. It does not by itself transform feasible-set accounting into a substantive OR design problem.

I would not count this section as an independent top-journal contribution.

---

# 7. The cache-governance result is correct but essentially weak duality, and the new evidence is strongly adverse

The governance proposition states that if U is an upper bound on the optimized restricted value K and z^w is a feasible witness, then

0 <= U - K <= U - W(z^w).

That is immediate from W(z^w) <= K <= U.

It is a sensible deployment rule, and I support including it if the cache remains in the paper. But it is not a substantial new theorem.

The optional retained-face test is also standard active-set logic:

- solve the equality-constrained KKT system for a proposed active set;
- verify all primal inequalities;
- verify multiplier signs and switching subgradient bounds;
- check complementarity and stationarity.

Again, useful and correct-looking, but standard.

The scaling evidence then delivers the most important empirical fact:

**83 of 84 queries refresh under the declared strict tolerance, and the cached pipeline is not faster.**

This should materially change how the paper is framed.

At this point the cache is not a demonstrated computational contribution. It is a valid certificate that often fails to remain useful under the tested perturbations.

That leaves three defensible options:

1. demote the cache to a robustness/certification appendix;
2. identify and prove a meaningful parameter regime in which refresh frequency is controlled;
3. provide a different application in which cache reuse is operationally important.

The current manuscript instead retains a large cache section even though its own best new experiment says the mechanism almost always refreshes.

That makes the paper more diffuse without strengthening its publication case.

---

# 8. The scaling study does not stress the central shared-table stochastic problem

The new study is carefully specified, but its scaling axis is not the one the paper most needs.

Each configuration is a direct sum of independent two-period blocks. The dimension n grows by replication. Each block has its own exact payment commitment. The fresh comparator is available in closed form because the blocks are separable.

This is appropriate for exact accounting of cache overhead. It is not a stress test of the shared-table recursion.

In particular, it does not test:

- long horizon;
- nontrivial Markov recombination;
- a shared table coupling many stochastic successors;
- multiple promise states;
- plane proliferation at a common public state;
- master-LP growth with K;
- recursive cut generation;
- dense cross-service coupling;
- branching-dependent child allocation;
- exact versus approximate state compression.

Thus the numerical section validates the implementation of the new certificate machinery but does not validate the paper's central stochastic claim at scale.

There is also a quality-normalization issue. The refresh tolerance is CS/1000, so aggregate absolute tolerance grows with the number of replicated blocks. Reporting error per block is reasonable for an extensive replicated objective, but it means the experiment is a fixed **per-block** quality study, not a fixed system-level error study. That should be explicit whenever scaling is discussed.

I would not use this experiment as evidence that the bridge scales.

---

# 9. The adaptive-policy certificate is useful but further fragments the paper

The Bernstein cross-coefficient test is a legitimate fix to the R27 fixed-policy limitation.

I checked the central algebraic structure:

- affine parameter dependence composed with an affine policy produces quadratic constraint residuals;
- nonnegative degree-two Bernstein coefficients are sufficient for interior feasibility;
- accepted equalities can be certified by zero coefficients;
- switching-sign refinement makes the implemented objective quadratic on each cell;
- convexity of the cached upper bound justifies a vertex chord;
- a Bernstein minimum yields a valid cellwise lower gain certificate.

I do not see an immediate contradiction there.

But this result is not needed to understand the shared-table bridge. It is a different problem: certification of a declared parameter-dependent policy under correlated coefficient changes.

The manuscript has now accumulated:

1. release-frontier sensitivity;
2. continuation-rent sensitivity;
3. friction paths;
4. promise-state recursion;
5. continuous-state envelopes;
6. shared-table dual representation;
7. endogenous architecture cost;
8. reward-only comparator reuse;
9. correlated comparator reuse;
10. cache governance;
11. adaptive Bernstein certification;
12. multiple generations of computational evidence.

The authors claim consolidation, but the paper remains scientifically overpopulated.

A top-journal paper should make clear which results would be lost if the central theorem were removed. Several of the sections above would survive almost unchanged.

I recommend substantial pruning or splitting, not another additive revision.

---

# 10. The service-contract application still does not carry the paper independently of the mathematics

The operational story is coherent: a provider adapts service tiers while respecting continuation participation and a precommitted information architecture.

However, the journal-facing evidence remains almost entirely synthetic.

There is:

- no field data;
- no calibrated service system;
- no empirical estimate of outside options;
- no calibrated implementation/memory costs;
- no managerial experiment showing that the optimal architecture changes in a realistic regime;
- no case in which the shared-table bridge changes an actual operational conclusion relative to a standard stochastic-programming formulation.

The paper is allowed to be theoretical. But then the mathematical contribution must carry the full publication burden.

Because I find the new bridge too close to established decomposition theory, the lack of a stronger application becomes consequential.

---

# 11. Specific technical and presentation comments

These comments are secondary to the novelty recommendation.

## 11.1 Be precise about what “dual complete” means

The current phrase may be read as saying that a finite, discoverable state-plane representation exactly solves the finite-horizon problem.

What is proved is weaker and should be named accordingly:

- for a fixed finite extensive-form problem and query, an optimal full-tree primal-dual solution induces a tight recursive plane;
- exact construction may use history-indexed dual information;
- the number of distinct planes required across states/queries can be large;
- no polynomial discovery or storage theorem is provided.

I suggest wording such as “extensive-form-dual representability” unless a stronger constructive result is proved.

## 11.2 The root master is standard enough that the paper should say “Benders master” explicitly

Calling it only a “root linear program” understates the closest established object. The scientific comparison would be clearer if the paper stated that the master is a Benders-style shared-design master and then identified the precise extra structure supplied by continuation prices.

## 11.3 The bridge example is too small to distinguish competing theories

The two-period, three-tier exact example is excellent for catching childwise reoptimization and factor-two mistakes. It is not capable of demonstrating an advantage over generic extensive-form duality or nested decomposition. Every object is explicitly enumerable.

A stronger example should exhibit a phenomenon that is genuinely easier or structurally clearer in the proposed state-price representation than in the generic stochastic program.

## 11.4 The accuracy proposition remains conditional on regularity not generated by the model

The Lipschitz and Lipschitz-gradient accuracy rates are explicitly conditional. That is correct. But they should not be advertised as a complexity consequence of the bridge because the required regularity and anchor/support quality are external assumptions.

## 11.5 The cost comparison is not an information-acquisition theorem

The architecture cost subsection should avoid language suggesting that the paper derives the cost of information. It optimizes over a declared cost schedule for implementability.

## 11.6 The cache section should foreground the 83/84 refresh result

This is not a footnote. It is the main empirical finding of the new cache experiment. The abstract currently says that certified witness widths govern price-cache refreshes; I would add that strict tolerances caused almost universal refresh in the reported study, or substantially reduce the cache emphasis.

## 11.7 The bibliography is too small for the claimed synthesis

Nineteen references are not automatically too few, but for a paper positioning itself at the intersection of dynamic contracting, multistage stochastic programming, Benders/SDDP, policy aggregation, parametric QP, robust certification, and adaptive deployment, the closest-result coverage is not credible enough.

The missing modern multistage decomposition literature is the most important gap.

## 11.8 The manuscript is at the format limit but still conceptually too long

The package checker reports 31 PDF pages and a conservative 30 nonreference pages. Formal compliance is not my objection.

The issue is conceptual density. A reader must retain too many theorem families to identify the central message. The new bridge should have enabled aggressive simplification. Instead, almost all inherited theorem layers remain in the main narrative.

---

# 12. What would be required for a fundamentally new submission

Because I recommend rejection rather than another routine revision, I would not ask the authors to patch R28 point by point.

A substantially new submission would need at least one of the following paper-level advances.

## A. A genuinely new stochastic decomposition theorem

For example, prove that under a meaningful continuation-contract structure:

- exact state-price certificates require only a bounded number of planes per Markov state;
- or a finite cut-generation procedure converges without history-tree enumeration;
- or the nested continuation structure yields a complexity bound unavailable for a generic multistage stochastic program;
- or the shared restriction admits a lower-dimensional dual recursion with a provably sufficient state of prices.

This would distinguish the work from standard nested Benders/SDDP.

## B. A new structural theorem with real operational content

For example, derive a nontrivial characterization of the optimal information architecture, memory depth, or continuation flexibility from primitives rather than from an externally declared cost schedule.

The result should say something surprising about when a provider should retain or discard information, how continuation participation changes the architecture, or how optimal flexibility scales with contract parameters.

## C. A compelling application in which the synthesis matters

A calibrated or data-based service system could make the combination of known tools publishable if the model produces a substantial operational insight that is not visible from generic stochastic programming alone.

## D. A focused optimization paper instead of the current omnibus manuscript

The correlated comparator certificate, adaptive Bernstein certificate, or release-path analysis could perhaps be developed into a narrower methodological paper with the appropriate literature and stronger results.

What I do **not** recommend is R29 that adds another certificate, another exact example, and another synthetic scaling table while preserving the same central theorem.

---

# 13. Recommendation to the editor

R28 is the strongest version of this project I have seen in the repository. The authors have responded conscientiously to difficult reports. The paper is reproducible, self-critical, and much clearer about limitations than many submissions. I found the negative computational evidence particularly credible because the authors did not suppress it.

Nevertheless, my editorial judgment is that the manuscript still falls short of the Operations Research bar.

The new shared-table bridge is a correct-looking and useful synthesis, but its core mathematical content remains too close to established nonanticipativity/policy aggregation, Bellman resource-state recursion, nested Benders/SDDP cuts, and extensive-form duality. Its exactness argument reorganizes a known full-tree primal-dual optimum rather than proving a new computational compression result. The implementation-cost and cache-governance additions are too elementary to carry independent novelty, the adaptive certificate is auxiliary, and the scaling study is both highly separable and computationally adverse to the reuse story.

The paper therefore has a stronger theorem chain than R27, but not, in my view, a sufficiently new theorem chain for a top general OR journal.

**Decision recommendation: Reject.**

I would encourage the authors to preserve the R28 archive and, if they continue the project, choose one of two paths: either derive a genuinely stronger stochastic-decomposition result that cannot be obtained by generic nested Benders/SDDP duality, or rebuild the work around a substantive operational application in which the shared information architecture produces a new decision insight. Another additive revision of the present omnibus manuscript is unlikely to change my recommendation.
