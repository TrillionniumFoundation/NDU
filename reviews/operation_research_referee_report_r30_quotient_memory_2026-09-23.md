# Confidential Referee Report for Operations Research

**Manuscript:** *Accepted Service Adaptation: Finite Continuation Prices and the Value of Memory*  
**Revision reviewed:** `revision/ndu-operations-research-r30-quotient-memory-20260923`  
**Prior scientific revision:** `revision/ndu-operations-research-r29-price-state-20260923`  
**Review branch:** `review/operation-research-r30-quotient-memory-harsh-20260923`  
**Recommendation:** **Reject / return as not substantively revised**

---

## Executive assessment

I was asked to evaluate the latest revision as an external referee for *Operations Research*. My first task was therefore a version audit. That audit is decisive.

The branch labeled

`revision/ndu-operations-research-r30-quotient-memory-20260923`

does **not** contain a scientific revision of the manuscript relative to

`revision/ndu-operations-research-r29-price-state-20260923`.

The Git comparison shows the r30 branch is exactly one commit ahead of r29-price-state, and the only added file is the previous referee report:

`reviews/operation_research_referee_report_r29_price_state_2026-09-23.md`.

No manuscript, electronic-companion, computational-supplement, bibliography, README, or submission-checklist file changed. The core blob hashes are identical across the two branches:

| File | r29-price-state SHA | r30 SHA | Scientific delta |
|---|---|---|---|
| `main.tex` | `9a8613aa55a3f2021da823ba97e5eaf330e10f6a` | same | none |
| `electronic_companion.tex` | `5a308fec2522e3ef845de2945a97ecb9a58a64e0` | same | none |
| `computational_supplement.tex` | `e269f8769770b82c6fbcd693cc6b91085c1eed33` | same | none |
| `main.bib` | `0009488fd0f4aec753c36e1a0408ed8d8c3a91cb` | same | none |
| `README.md` | `5ac614c3f33475eabc042fcda1dabf7b78ed63d0` | same | none |
| `NDU_OR_submission_checklist.md` | `6f6f00e85e9c8b218c40b5c01c5c711b81cb1373` | same | none |

Accordingly, there is no basis for treating r30 as a response to the prior report. The branch name suggests a revision centered on “quotient memory,” but no such revision is present in the scientific files.

My recommendation is therefore straightforward: **Reject / return as not substantively revised.** The previous r29-price-state referee report remains applicable in full.

This is not a cosmetic objection. In a top-journal revision process, a new revision branch must contain a traceable response to the substantive objections that motivated the prior decision. Adding the prior referee report to a new branch does not constitute a manuscript revision.

---

# 1. Version audit

Relative to r29-price-state, the r30 branch has:

- one additional commit;
- one additional file;
- zero modified scientific files;
- zero modified computational files;
- zero modified bibliography files;
- zero modified editorial-positioning files.

The only new file is the previous referee report.

Thus:

[
	ext{scientific delta}(r30,r29	ext{-price-state})=0.
]

I therefore do not re-score the unchanged theorems as though the authors had responded to the previous report. Instead, I record which rejection-level issues remain unresolved and what would be required before another substantive review would be meaningful.

---

# 2. The central novelty problem remains completely unresolved

The previous report identified the main publication obstacle: the manuscript's central finite-price construction is not yet positioned convincingly against the closest classical Operations Research literature on separable concave/convex allocation with tree or laminar constraints.

That remains unchanged.

The manuscript still needs a serious theorem-by-theorem comparison with, at minimum:

1. K. M. Mjelde (1983), “Resource Allocation with Tree Constraints,” *Operations Research* 31(5):881–890.
2. C. S. Tang (1990), “Reducing Separable Convex Programs with Tree Constraints,” *Management Science* 36(11):1407–1412.
3. Subsequent laminar/tree-constrained separable resource-allocation work relevant to the exact quadratic structure.
4. The nested resource-allocation literature already cited.
5. Policy-graph decomposition / SDDP only after the classical deterministic laminar connection is settled.

The essential question is not whether scalar marginal prices exist. In the full-history expansion, the no-switching subclass has a separable objective and subtree-sum constraints, which is visibly a tree/laminar resource-allocation structure.

The potentially publishable residual contribution is much narrower and more interesting:

> repeated subtree structure in a compact recombining public DAG can be quotient-compressed into a finite family of conditional response functions, with a globally controlled breakpoint universe and a finite endogenous price-memory implementation, without unfolding the exponentially larger history tree.

That is the claim the paper should prove and position.

The current manuscript still does not demonstrate that this compact-DAG quotient is not an immediate memoized form of the classical tree-reduction machinery.

Until this is resolved, the priority claim is incomplete.

---

# 3. A formal compact-DAG quotient theorem is still missing

The previous report asked for an explicit occurrence-to-vertex invariance theorem. That request remains unaddressed.

The manuscript should formally distinguish:

- a compact public DAG vertex (v);
- an occurrence (h) of (v) in the unfolded history tree;
- the incoming accumulated continuation price (eta_h);
- the conditional subtree optimization below that occurrence.

Then prove:

> for every occurrence (h) of public vertex (v), conditional on the same incoming scalar price (eta), the optimal continuation value, payment response, and action rule depend only on ((v,eta)), not on the ancestor path that generated the occurrence.

That is the mathematical quotient statement. It is the exact step that converts an algorithm on the unfolded laminar tree into an algorithm on the compact recombining graph.

The current proof uses the graph-level recursion but does not isolate this quotient property as the principal theorem.

For an *Operations Research* contribution whose computational advantage depends on recombination, leaving the quotient step implicit is not acceptable.

---

# 4. The complexity claim still stops at arithmetic operations

The manuscript carefully distinguishes its arithmetic-operation count from bit complexity, but the issue remains unresolved.

The exact algorithm repeatedly:

- sums rational slopes and intercepts;
- forms probability-weighted rational coefficients;
- solves affine breakpoint equations;
- merges exact rational piecewise-affine curves;
- propagates exact prices across the graph.

A bound such as

[
O((N+M)Nlog(N+1))
]

in a real-RAM or arithmetic-operation model does not establish polynomial-time complexity under ordinary rational encoding.

The paper still needs one of two clean positions.

### Option A: prove a bit-complexity result

State an input encoding model and bound:

- numerator growth;
- denominator growth;
- breakpoint encoding length;
- arithmetic cost under exact rational computation.

### Option B: stay explicitly in the arithmetic model

Then remove any prose that could be read as a conventional polynomial-time claim and report exact coefficient bit-length growth empirically.

The current computational timing evidence cannot substitute for this distinction.

---

# 5. The memory theorem remains interesting but too narrow for the surrounding narrative

The lower-bound and finite-memory-frontier construction is one of the more interesting parts of the paper. It establishes that exact implementation can require a number of endogenous labels growing linearly with graph size in a deliberately recombining family.

However, the manuscript still needs to sharpen exactly what is being minimized.

The controller model should specify which information is available without counting as writable memory:

- date;
- current public state;
- inherited physical tier;
- remaining promise;
- root price;
- read-only threshold table;
- graph primitives.

The current accounting excludes the read-only threshold table and its numerical precision. That is a legitimate systems convention, but it is not an invariant notion of information complexity.

The manuscript should also address:

1. whether the lower bound extends from deterministic to randomized controllers;
2. whether continuation-price cells are minimal in a formal automata/state-equivalence sense;
3. whether ordered cells remain optimal beyond the specially constructed three-date family;
4. whether a broader theorem can characterize when continuation-price order induces contiguous optimal memory cells.

Without such a strengthening, the paper should describe the result as a worst-case exact-memory lower bound and an exact frontier for one structured family, not as a general theory of information architecture.

---

# 6. The computational section still validates correctness rather than comparative importance

The exact rational verification suite is a real strength. The package checks:

- response-curve identities;
- local KKT conditions;
- state-flow identities;
- primal-dual equality;
- small unfolded-tree instances;
- exact memory-frontier enumeration;
- supporting-cut validity.

These checks answer the question:

> Did the implementation faithfully realize the stated mathematics?

They do **not** answer:

> Is the proposed algorithm competitive or structurally advantageous relative to the closest OR methods?

The paper still needs serious baselines.

At minimum:

1. **Tree/laminar resource allocation.** Implement or reproduce a relevant classical exact method on the unfolded problem for the range where unfolding is feasible.
2. **Generic convex/QP solve.** Compare against a high-quality generic solver on the same exact or high-precision formulation.
3. **Promise-state dynamic programming.** Compare with the recursion already discussed in the manuscript on instances where promise discretization or finite attainability is controlled.
4. **Policy-graph / decomposition baseline.** Include a modern decomposition method on the recombining stochastic graph.
5. **Scaling experiment.** Vary compact graph size and horizon separately, rather than relying on a single statement that the naive history tree would have exponentially many paths.

A 190-vertex / 64-date example is a useful proof of concept. It is not, by itself, evidence that the method dominates relevant alternatives, because modern decomposition methods also avoid literal enumeration of (3^{64}) histories.

---

# 7. The service-contract interpretation remains secondary to the optimization structure

The central finite-price theorem relies on a narrow but mathematically clean subclass:

- one positive additive payment commitment;
- exogenous public Markov transitions;
- separable strictly concave quadratic local rewards;
- scalar or separable local controls;
- no switching cost in the main finite-price result;
- no coupled vector commitments in the central theorem;
- no private information;
- public-state-sufficient continuation caps.

Under these assumptions, the problem is close to a structured resource-allocation model.

That is not a defect if the paper is positioned as a methodological OR contribution. But then the optimization novelty must be unmistakable.

If the service-contract application is intended to carry part of the publication case, the paper needs a genuinely service-design-specific theorem or empirical result, for example:

- a theorem linking outside-option heterogeneity to the number of required continuation-price labels;
- comparative statics for memory value as renewal rights vary;
- conditions under which contractual renewal makes the physical Markov state insufficient;
- a calibrated service example in which the compact price state changes a nontrivial design recommendation.

At present, the application remains illustrative rather than independently contribution-bearing.

---

# 8. The shared-table results still need disciplined scope

The zero-release shared-table formulation is useful because it correctly preserves a single shared table across successor states rather than reoptimizing it independently in each child.

The fixed-table positive-release oracle is also useful: it supplies an exact value and a supporting cut using the finite-price engine.

But the paper must maintain the distinction between:

- an exact compact oracle for a fixed table query; and
- a globally optimized shared-table design algorithm with a finite complexity guarantee.

The latter is not established.

The Benders-style outer design problem still has no finite exact cut bound. The manuscript should not let the exactness of the inner oracle blur the unresolved complexity of the outer master problem.

The normal-cone treatment of physical-bound / corridor-bound ties also still deserves a complete formal proof in the companion.

---

# 9. Several technical points from the previous report remain open verbatim

Because the manuscript files did not change, the following points remain unresolved.

## 9.1 Separate capped and pre-cap response notation

The proof of the finite-price theorem should distinguish the response before imposing the current continuation cap from the already capped response. The current notation makes the reflection argument harder to audit than necessary.

## 9.2 Root equality and root cap

The manuscript should state explicitly whether the root itself is subject to a cap and impose the appropriate compatibility between the exact root promise interval and that cap.

## 9.3 Plateau convention

If a threshold equation has a price plateau, the paper should prove that the chosen leftmost-threshold convention and the update

[
s_v=max{eta,alpha_v}
]

produce the unique primal policy even when the dual multiplier is not unique.

## 9.4 Global knot count versus total stored response size

The global set of distinct knots may be (O(N)), but storing separate response functions at all vertices can still require (O(N^2)) segment storage. This distinction should remain explicit wherever compactness is discussed.

## 9.5 Multi-coordinate extension

If local action dimension increases the global knot universe but not the number of realized endogenous barrier labels, the paper should explain this distinction conceptually, not only symbolically.

---

# 10. Manuscript architecture remains too broad

The manuscript still carries a large amount of inherited material:

- release-path analysis;
- continuation-rent sensitivity;
- friction paths;
- information hierarchies;
- promise-state recursion;
- multiple cache bounds;
- robust outer comparators;
- correlated certificates;
- governance machinery;
- adaptive statistical certificates;
- the newer finite-price and memory results.

Many individual components are correct and useful. That is not the question.

The question is whether they belong in one *Operations Research* article centered on the compact-DAG finite-price theorem.

The answer, in the current form, is no.

The paper would be substantially stronger if rebuilt around:

1. the compact-DAG quotient theorem;
2. its exact relation to classical tree/laminar allocation;
3. the finite endogenous price-state result;
4. the matching memory lower bound/frontier;
5. the minimum shared-table machinery needed for the economic benchmark;
6. computational comparisons directly targeted at those claims.

Historical derivations can remain in the repository. They do not all need to remain in the journal article.

---

# 11. Revision-governance problem

There is an additional editorial issue specific to this r30 branch.

A branch named

`revision/ndu-operations-research-r30-quotient-memory-20260923`

signals that the authors have produced a revision addressing the previous report, presumably with a new quotient/memory focus.

But the scientific files are byte-for-byte unchanged.

This creates avoidable ambiguity for referees, editors, and future authors auditing the repository. A revision branch should not be advanced merely by copying in the previous referee report while leaving the manuscript unchanged.

For future rounds I strongly recommend:

1. base the new revision branch on the exact reviewed branch;
2. modify the manuscript and companion files on that revision branch;
3. include a response-to-referees or change log;
4. include a machine-readable or human-readable list of modified scientific files;
5. ensure the review branch is created from the exact revision commit being reviewed.

This is especially important in a repository with many rapid r-number iterations.

---

# 12. What a genuine r30 revision would need to contain

I would consider another substantive review only after a branch contains an actual scientific response. At minimum:

## A. Priority and literature

Add the missing tree/laminar literature and state precisely which parts of the finite-price theorem are old, which are adaptations, and which are new.

## B. Formal quotient theorem

Prove occurrence-to-vertex invariance and state the compact-DAG quotient as a theorem in its own right.

## C. Complexity

Give either bit complexity or a disciplined real-RAM/arithmetic-model statement plus coefficient-growth evidence.

## D. Memory theory

Clarify the controller observation model, randomness, read-only table accounting, and attempt a broader minimal-memory characterization.

## E. Comparative computation

Add relevant classical tree-allocation, generic QP, state-recursion, and policy-graph/decomposition baselines.

## F. Operational content

Supply a service-design implication that is not simply a relabeled resource-allocation observation.

## G. Focus

Move noncentral cache/governance/sensitivity material to a companion or separate paper unless needed directly for the main theorem.

## H. Transparent revision response

Include a point-by-point response showing where each prior major concern has been addressed.

---

# 13. Recommendation to the editor

The manuscript I am being asked to review in r30 is scientifically identical to the r29-price-state manuscript for which I already recommended rejection.

The r29 manuscript had improved substantially and contained an interesting new finite-price construction. My rejection was not based on the absence of mathematical substance. It was based on unresolved novelty relative to the closest tree/laminar allocation literature, the lack of a formal compact-DAG quotient theorem, insufficient comparative computation, and insufficiently sharp complexity and memory claims.

None of those issues has been addressed in r30 because no scientific file has changed.

I therefore recommend that the editor **not treat this branch as a revised manuscript**.

**Decision recommendation: Reject / return as not substantively revised. A future submission should be evaluated only after the authors commit a genuine scientific revision centered on the compact-DAG quotient theorem, its exact relationship to classical tree-constrained allocation, and its minimal-memory consequences.**
