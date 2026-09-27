# Third-Round Referee Report for *Operations Research*

**Manuscript:** *NDU: A Generalization of Fixed-Preference Reinforcement Learning*  
**Repository:** TrillionniumFoundation/NDU  
**Revision branch presented as latest:** revision/ndu-or-r2-20260920  
**Revision tip audited:** fd37a524c491db0228b357285b0a7b2acb8be4fb  
**Current manuscript blob:** main.tex = 2569eee2eb7f80f0a5b31ed07be75d5da9e6a0d3  
**Current PDF blob:** main.pdf = 3ed6d3446ad5eafe4f99e8279c28d37ae3a91068  
**Current R2 protocol blob:** revisions/or-r2-20260920/protocol.json = 055cec67f297166cca69b60d92be3faeb0cb86f4  
**Previous second-round review:** commit 5580a1052c8f2625a4ca84fa6df8c09086e5cf4a on review/operation-research-r2-harsh-20260920  
**New review branch:** review/operation-research-r3-harsh-20260920  
**Review type:** external third-round technical review, deliberately stringent  
**Recommendation:** **Reject / return without further scientific revision credit. There is no new manuscript revision after the second-round report, and the central mathematical objections remain in the submitted paper.**

---

## 1. Executive assessment

I audited the branch that is currently the newest revision branch, the current manuscript and PDF blobs, the predeclared R2 protocol, the previous two referee reports, and the branch ancestry.

The decisive repository fact is that there is still **no revised paper after the second-round review**. The current R2 revision tip is the direct ancestor of the existing R2 review branch. Its main.tex and main.pdf are the same blobs already reviewed in round two. Relative to the prior revision line, the R2 branch adds a protocol file but no manuscript delta, no replacement theorem text, no replacement proof, and no executed R2 result bundle.

Therefore this is not a third scientific revision in the ordinary journal sense. It is the same manuscript plus an unexecuted reconstruction protocol.

That procedural point would be sufficient to return the paper. I nevertheless re-checked the major mathematical and Operations Research claims. The main defects are still present verbatim:

1. the inventory service-pressure monotonicity theorem has the wrong sign under the stated maximization objective;
2. the claimed risk-sensitive non-equivalence is not proved and is false at the claimed level of generality;
3. ordinary expanded-action stochastic control represents the joint (a, theta) decision exactly, a point the new R2 protocol itself now acknowledges;
4. the physical-cost theorem compares against an artificially restricted fixed-pressure class and does not establish that NDU optimality causes the physical improvement;
5. the new contract protocol is a materially different economic model, but that model has not replaced the model in the paper;
6. the predeclared fair exact-DP experiment has not been executed and incorporated into the manuscript;
7. the HJB certificate theorem still does not state a complete bounded-domain boundary-value problem;
8. the cover-refinement corollary still asserts a quantitative finite-error form without a scheme-specific rate theorem;
9. the economically relevant neural inventory solver remains far from its own uniform residual/terminal/greedy-gap certificate; and
10. a very large amount of software QA remains promoted to proposition/corollary status, obscuring rather than strengthening the core theory.

There are useful ingredients here: the endogenous contract/valuation idea can be made operationally meaningful, the exact-DP direction is appropriate, the reproducibility engineering is strong, and the authors have become more explicit about mixed physical results. But *Operations Research* requires a coherent scientific paper, not a repository in which the correct future model exists only as a protocol while the submitted manuscript still contains the old false theorem and old incompatible evidence.

---

# 2. Revision-integrity audit: no new paper exists after round two

The current latest revision branch is revision/ndu-or-r2-20260920. Its tip is fd37a524c491db0228b357285b0a7b2acb8be4fb, whose commit message is a predeclaration of the OR R2 contract model and verification protocol.

The existing second-round referee report was then committed one step later on review/operation-research-r2-harsh-20260920 at 5580a1052c8f2625a4ca84fa6df8c09086e5cf4a.

The branch comparison is therefore unambiguous:

- review/operation-research-r2-harsh-20260920 is one commit ahead of the R2 revision branch;
- the R2 revision branch has no commit after that review;
- main.tex is still blob 2569eee2eb7f80f0a5b31ed07be75d5da9e6a0d3;
- main.pdf is still blob 3ed6d3446ad5eafe4f99e8279c28d37ae3a91068;
- the only substantive R2 addition relative to the earlier R1 line is revisions/or-r2-20260920/protocol.json.

Thus there is no response to the second-round report in the paper itself.

A journal revision must change the object being reviewed. A protocol for a future reconstruction is not a revised manuscript.

---

# Major comments

## 3. Fatal: the inventory monotonicity theorem still has the wrong sign

Theorem thm:inventory_service_pressure_structure remains unchanged.

The stated one-period maximization objective contains

\[
-p(\theta)\,\mathbb E[(B+D_z-S)^+]
-\lambda(\theta-\theta^-)^2,
\]

with \(p'(\theta)>0\).

Let

\[
L(B,z,S)=\mathbb E[(B+D_z-S)^+].
\]

Ignoring continuation terms for the moment, the stage contribution depending on \(\theta\) is

\[
-p(\theta)L-\lambda(\theta-\theta^-)^2.
\]

The cross effect of \(\theta\) and shortage stress \(L\) is

\[
\frac{\partial^2}{\partial \theta\,\partial L}
[-p(\theta)L]
=
-p'(\theta)
<0.
\]

That is **decreasing differences**, not increasing differences.

The proof nevertheless says:

> Because \(p(\theta)\) multiplies expected unmet demand, the one-step objective has increasing differences between \(\theta\) and shortage/backlog stress variables.

The missing minus sign is not cosmetic. Under the stated reward maximization problem, higher shortage exposure makes a higher penalty coefficient more costly to the controller. All else equal, the controller wants to reduce \(\theta\), not increase it.

A one-period admissible special case with zero continuation value already contradicts the theorem's claim that \(\theta_t^*\) is nondecreasing in backlog and demand stress.

The assumptions do not repair this. The theorem imposes no condition that the continuation value has a sufficiently strong positive cross effect in \((\theta,B)\) or \((\theta,z)\) to overcome the negative stage cross-partial.

The asserted mean-reversion comparative static is also stated too loosely. A quadratic adjustment term pulls toward \(\theta^-\), but "mean-reverting toward \(\theta^-\) with strength increasing in \(\lambda\)" requires a precise parameterized argmax statement. It does not follow as written from the listed assumptions.

### Required correction

The old internal-penalty formulation should be removed rather than patched. If the intended \(\theta\) is an externally priced service contract, insurance level, capacity commitment, or compensation term, state that model directly and prove its lattice/monotonicity result from the correct economic primitives.

The new R2 protocol points in exactly that direction, but the manuscript has not adopted it.

---

## 4. The entropic risk-sensitive non-equivalence result is still invalid

Corollary thm:non_equivalence_models continues to assert non-equivalence to fixed-parameter entropic risk-sensitive control, and the proof argues that an entropic continuation operator is smooth/strictly curved whereas a valuation-control support function is piecewise affine/nonsmooth.

This does not establish the claimed conclusion.

First, the manuscript's valuation set \(\Theta\) is not restricted to a finite set. A supremum over a continuum of affine functionals can be smooth and strictly convex. For example, quadratic penalties on a continuous control produce smooth convex conjugates.

Second, entropic continuation operators possess the standard entropy-penalized variational representation

\[
\frac{1}{\rho}\log \mathbb E[e^{\rho V}]
=
\sup_Q
\left\{
\mathbb E_Q[V]
-
\frac{1}{\rho}D_{\mathrm{KL}}(Q\|P)
\right\},
\]

under the usual absolute-continuity/integrability conditions.

That is itself a supremum of affine continuation-value functionals plus a penalty. Once the valuation-control family is rich enough to parameterize the relevant distorted kernels, the geometry invoked in the proof no longer separates the classes.

Third, the current proof silently changes the comparator from "all fixed-parameter risk-sensitive models" to a much narrower representation class with a particular primitive form.

### Required correction

Either delete item (iii) from the non-equivalence corollary, or state a narrowly defined comparator class and prove non-equivalence relative to that exact class.

The broad taxonomic claim is not supportable from the present argument.

---

## 5. The new R2 protocol itself confirms ordinary expanded-action representability

The R2 protocol explicitly lists an expanded_action_mdp comparator.

That is the correct baseline.

If the decision at a state is the pair \((a,\theta)\), then an ordinary controlled Markov model with action space

\[
A' = A\times\Theta
\]

represents the joint decision directly. This is not a loophole; it is the standard representation of a controlled variable.

The paper's operator-level theorem proves only that after optimizing out \(\theta\), the resulting reduced support operator need not be representable by **one fixed affine action-conditioned primitive while refusing to enlarge the action set**.

That statement is mathematically fine but much narrower than the title and rhetoric suggest. It is a theorem about a restricted evaluator-preserving/action-preserving collapse, not a theorem that NDU lies outside standard stochastic control or RL.

The manuscript actually admits this in places, but repeatedly surrounds the restricted theorem with "generalization", "non-collapse", and model-taxonomy language that can easily be read more broadly.

### Required correction

Make the expanded-action MDP equivalence explicit in the main theorem section, not only in the protocol.

The novelty claim should be framed around the economic semantics, structural consequences, and computational treatment of a costly endogenous valuation/contract coordinate—not around nonrepresentability by ordinary control.

---

## 6. The stable theta-free physical-cost theorem is a capacity/calibration lemma, not an NDU optimality theorem

Theorem thm:stable_physical_cost_improvement defines regime-specific physical costs

\[
C_z(S)=h\mathbb E[(S-D_z)^+]+p_z\mathbb E[(D_z-S)^+],
\]

then assumes NDU may choose \(\theta_z\) so that \(p(\theta_z)=p_z\), thereby reproducing the regime-specific newsvendor quantile.

This proves a simple fact: a regime-dependent parameter can fit multiple regime-specific critical fractiles that one fixed parameter cannot fit.

It does **not** prove that the endogenous NDU objective optimally selects those \(\theta_z\).

Indeed, the theorem effectively inserts the physical shortage coefficient \(p_z\) into the valuation parameter by construction.

More importantly, if \(z\) is observed and the physical order-up-to action \(S\) may itself depend on \(z\), then a same-information action-only controller can choose

\[
S_z=F_z^{-1}\!\left(\frac{p_z}{h+p_z}\right)
\]

directly, without any valuation coordinate at all.

The theorem excludes that stronger comparator by definition and compares only with a single fixed-pressure rule. This makes the result a restricted policy-class separation, not a general operational benefit of endogenous valuation.

The paper now partly acknowledges this, but the theorem remains positioned as a major physical OR contribution.

### Required correction

Either:

1. prove a result under information, implementation, commitment, or contracting constraints that make \(\theta\) operationally necessary; or
2. downgrade this result to a representation/capacity lemma and make the same-information physical oracle the primary comparator.

The R2 protocol correctly includes a physical_oracle comparator. That comparator should be central in the actual paper.

---

## 7. The R2 contract protocol is economically more credible, but it is a different model that has not replaced the manuscript

The strongest improvement in the repository is conceptual, not yet scientific evidence.

The R2 protocol gives \(\theta\) explicit external consequences:

- a regime-dependent external premium;
- incremental contract liability proportional to shortage;
- maintenance cost;
- adjustment cost;
- persistence through the previous-contract state.

This is much more defensible than allowing an agent to choose the coefficient by which its own shortage is internally scored.

But the current manuscript still describes \(\theta\) mainly as an endogenous service-pressure / shortage-penalty multiplier and proves the old theorem under that formulation.

The main CEM inventory benchmark also uses a different mechanism again: \(\theta\) enters an order-up-to policy map, an adjustment term, and a service-pressure welfare calculation. The SKU benchmark uses yet another mapping from \(\theta\) to target fill.

The R2 contract model is therefore not a small calibration change. It changes the economic meaning of the decision variable.

### Required correction

Choose one canonical operational model and use it throughout:

- theory;
- exact DP;
- physical evaluator;
- comparator definitions;
- numerical experiments;
- economic interpretation.

Do not keep the old internal-penalty theorem while using a new externally priced contract only in a protocol.

---

## 8. The predeclared R2 fair experiment has not been executed

The R2 protocol is unusually concrete and, in several respects, well designed. It predeclares:

- an exact finite-horizon rational DP;
- the joint contract controller;
- expanded-action MDP;
- frozen contract;
- capacity-matched gate;
- physical oracle;
- exhaustive action enumeration;
- actual Bellman evaluation counts;
- ledger decomposition;
- fresh simulation seeds;
- direct-P / learned-Z conditioning diagnostics;
- a boundary-complete manufactured PDE example.

Those are exactly the kinds of controls the paper needs.

But the branch contains the protocol only.

There is no new result table, no generated ledger, no exact-DP output, no fresh seed report, no protocol checksum-to-result chain, and no manuscript section incorporating an R2 execution.

A preregistration cannot be cited as empirical evidence for the paper.

### Required correction

Execute the frozen protocol without post hoc parameter changes. Commit:

1. exact DP outputs for every predeclared comparator;
2. full objective decomposition;
3. theta-free physical metrics;
4. fresh simulation uncertainty summaries;
5. the physical-oracle gap;
6. expanded-action equivalence diagnostics;
7. conditioning experiment outputs;
8. a machine-readable manifest binding outputs to the protocol commit.

Then rewrite the manuscript around those results.

---

## 9. The HJB certificate theorem still does not state a complete bounded-domain problem

Theorem thm:nbo_hjb_solver_certificate fixes a compact parabolic domain

\[
D=[0,T]\times K
\]

and states sup-norm value and policy bounds from an interior HJB residual and terminal residual.

The theorem statement does not specify what happens on the nonterminal spatial boundary \([0,T)\times\partial K\).

The proof later says that if the compact problem is not state constrained or reflected, then the certificate must include the nonterminal boundary residual.

That caveat belongs in the theorem statement.

A bounded-domain parabolic PDE is not uniquely characterized by an interior equation plus terminal data without an appropriate spatial boundary condition or a precisely defined state-constraint problem.

"Suppose comparison holds in the relevant bounded viscosity class" is not enough to make an unspecified boundary problem mathematically complete.

The constant \(C_D\) is also too abstract for the claimed quantitative estimate unless the exact properness/comparison/barrier setting is given.

### Required correction

State one concrete PDE problem:

- Dirichlet;
- Neumann/reflected;
- state constraint;
- periodic; or
- another precisely defined boundary condition.

Define the residual on the full parabolic boundary required by that problem and prove the quantitative stability estimate for that setting.

The new R2 manufactured PDE protocol is explicitly boundary-complete. That is good, but again it is not yet the theorem in the paper.

---

## 10. The cover-refinement corollary still overclaims a quantitative rate

Corollary cor:cover_refinement_hjb_certificate states a bound of the form

\[
C_D\{\delta_T+T(\delta_B+\delta_A+\eta_h+L_A\rho)\}.
\]

Monotonicity, stability, consistency, and comparison are enough for convergence in the classical viscosity-scheme framework, but they do not automatically give this generic linear finite-error rate.

A quantitative rate requires additional regularity and a scheme-specific consistency/error estimate.

The current manuscript still does not define a single numerical discretization in enough detail for such a theorem.

### Required correction

Either:

- state only convergence under a precisely defined monotone/stable/consistent scheme; or
- provide a scheme-specific rate theorem with the regularity assumptions and constants needed for the displayed finite bound.

An exact solve of a finite cover certifies the finite discrete problem. It does not automatically certify a continuous HJB at the claimed rate.

---

## 11. The neural inventory solver is still far from the paper's own certificate

The manuscript is now more candid that the large neural rows are "certificate-gap evidence", which is an improvement.

But the actual inventory diagnostics remain poor relative to the theorem:

- headline normalized HJB RMSE about 1.84;
- headline native HJB loss about \(6.26\times 10^4\);
- terminal loss about \(2.06\times10^3\);
- sampled greedy-gap sup about 1556.6;
- sampled terminal sup about 75.1.

The targeted actor-gap run lowers the greedy-gap sup materially, but terminal error remains large. The residual-oriented run improves some residual measures while the greedy gap again becomes very large.

These are useful diagnostics of an unstable or difficult solver. They are not evidence that the economically relevant neural inventory instance is close to satisfying the uniform HJB theorem.

The manufactured compact example can certify the manufactured example. It does not transfer a certificate to the inventory neural solver.

### Required correction

For the main OR paper, one of two choices is needed:

1. **Modeling paper:** treat the neural actor-critic as a heuristic numerical method with diagnostics and remove HJB-solver language from the central contribution.
2. **Solver paper:** obtain a boundary-complete, quantitatively small residual/terminal/greedy certificate on the same economically relevant instance, or provide a rigorous discretization-to-solver argument that actually applies there.

At present the manuscript tries to claim both.

---

## 12. The direct-P result is a valid conditioning identity but not a general solver-superiority theorem

The lemma

\[
Z_u=\sqrt{2\varepsilon}P_u
\]

implies that if an additive \(Z\)-target error has an \(\varepsilon\)-independent absolute scale, then inversion divides the squared error by \(2\varepsilon\).

That is correct.

But the result is conditional on the error model. It is not a lower bound for every learned-Z architecture or every Deep BSDE solver.

Many learning procedures do not observe a noisy fixed-scale \(Z\) target and then perform literal post hoc inversion.

The manuscript itself now includes some same-architecture ablations where learned-Z can be competitive away from the nearly degenerate regime.

### Required correction

Call this what it is: a representation-conditioning result near a degenerate diffusion block.

Do not use it to imply generic superiority of direct-P learning without an end-to-end statistical or optimization theorem.

---

## 13. The empirical OR story remains mixed, not a demonstrated operational advantage

The paper now reports several negative/mixed physical results, which is scientifically preferable to hiding them.

However, the aggregate evidence does not support a broad operational-superiority story:

- the compact equal-budget inventory rerun favors action-only slightly on welfare and theta-free cost;
- the public SKU approximate-DP comparator has lower external cost, higher fill, and lower backlog than Full NDU;
- the exact policy-class DP gives Full better internal valuation welfare but worse average physical cost than action-only;
- the exact valuation-state MDP gives a valuation-welfare gain with the same theta-free cost and fill;
- the PyTorch inventory row reports worse cost for Full despite a better internal objective.

The selected larger positive retest is explicitly post-screening and should remain descriptive.

This pattern is perfectly acceptable for a paper whose contribution is a new operational contract objective with explicit tradeoffs. It is not strong evidence for a general claim that endogenous valuation improves physical operations.

### Required correction

The new exact R2 contract experiment should become the main evidence.

Report:

- the contract objective;
- the physical-only objective;
- the joint-controller optimum;
- the expanded-action MDP optimum;
- the frozen-contract optimum;
- the physical oracle;
- all objective components.

Then let the reader see exactly what is gained and what is traded off.

---

## 14. Too many theorem environments are still software/audit bookkeeping

The manuscript contains a long sequence of corollaries and propositions for:

- validation-cover guards;
- empirical-envelope guards;
- interval-domain guards;
- bounded-architecture audits;
- cross-artifact consistency;
- refinement/stress guards;
- bootstrap guards;
- concordance guards;
- leave-one-out robustness;
- stress-frontier checks;
- referee-objection support;
- six-pillar claim support;
- synthesis/closure maps.

Most of these are not mathematical contributions. They are reproducibility or manuscript-consistency checks.

A top OR paper becomes harder to trust when software assertions are dressed in theorem syntax next to actual stochastic-control results. The distinction between proof, numerical evidence, code validation, and editorial bookkeeping must be sharp.

### Required correction

Move nearly all of these to a reproducibility appendix or repository audit document.

The main paper should keep only genuine mathematical results and a small number of evidence tables.

---

## 15. The manuscript still combines three insufficiently integrated papers

The current document remains an unstable combination of:

1. an endogenous-valuation stochastic-control modeling paper;
2. a stochastic HJB/FBSDE numerical-method paper; and
3. an inventory/service-system OR application paper.

The continuous-time FBSDE framework, the discrete periodic-review inventory problem, the contract-like R2 protocol, the direct-P conditioning argument, and the actor-critic certificate machinery are not yet a single mathematical object.

For *Operations Research*, breadth is valuable only when the paper remains scientifically coherent and broadly interpretable.

The strongest version of this project is likely a **theory-first OR model with an exact discrete application**, with the neural/HJB material substantially reduced or separated unless the numerical theory is independently completed.

---

# 16. What would constitute an actual reviewable next revision

A next revision should not be another protocol-only branch. At minimum it should contain all of the following.

### A. Replace the old inventory primitives

Adopt one economically defensible interpretation for \(\theta\), preferably the external contract/commitment interpretation already predeclared in R2.

The submitted theorem, Bellman recursion, simulator, and exact DP must use the same primitives.

### B. Re-prove the structure theorem

Derive the correct increasing/decreasing-differences conditions from the new economic model.

Include a counterexample showing why the monotonicity result fails without the key condition.

### C. Rewrite the novelty statement

State explicitly that the full joint problem is an ordinary MDP/stochastic-control problem on the expanded action space.

Then explain what is new about the operational semantics, structural policy, or computational reduction.

### D. Repair or delete the risk-sensitive taxonomy claim

Do not claim generic entropic non-equivalence from smooth-versus-piecewise-affine geometry.

### E. Execute the frozen R2 experiment exactly as preregistered

Do not tune model parameters after observing result signs.

The expanded-action MDP and physical oracle must be first-class comparator rows.

### F. Make the physical oracle central

If the joint contract controller improves its own net contract objective but not pure physical cost, say so.

That can still be an important OR result if the contract has real external economics.

### G. State a complete HJB theorem

Specify the spatial boundary problem and prove the residual-to-value estimate for that exact setting.

### H. Remove artifact checks from theorem status

Keep the reproducibility engineering, but move it to a technical artifact appendix.

### I. Cut the paper materially

The current manuscript is overgrown because it attempts to preserve every audit, repair, and stress test in the main narrative.

A publishable version should have a small number of central theorems and a small number of decisive experiments.

---

## 17. Positive aspects worth preserving

The repository has several genuine strengths:

- unusually transparent negative/mixed-result reporting;
- strong artifact organization;
- explicit matched-budget concerns;
- exact-DP instincts rather than relying only on neural training;
- willingness to include stronger physical comparators;
- the new R2 contract semantics, which give \(\theta\) an external operational interpretation;
- preregistration of a fairer experiment before execution;
- separation of theta-dependent objective terms from theta-free physical metrics.

These are valuable. They are also why the next step should be a true scientific reconstruction rather than another layer of audit machinery.

---

# 18. Confidential recommendation to the editor

**Recommendation: Reject / return without revision credit.**

This recommendation is not based on style or insufficient polish.

The current branch presented as the latest revision does not contain a revised manuscript after the existing second-round review. The main.tex and main.pdf are unchanged, and the only new R2 scientific object is a protocol for a future model and experiment.

On the unchanged manuscript, the central inventory monotonicity theorem is still wrong under its stated objective; the entropic non-equivalence argument remains invalid; the physical-cost theorem does not establish NDU optimality relative to a same-information action-only controller; the HJB theorem remains boundary-incomplete; the cover-refinement rate is not justified; and the neural inventory solver remains far from its own stated certificate.

The R2 protocol is a promising blueprint for a materially different and potentially much stronger paper. But a blueprint is not a revision.

I would be willing to review a future manuscript that actually implements that reconstruction. The next submission should be judged as a new scientific version, not as a minor continuation of the present text.
