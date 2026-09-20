# Fourth-Round Referee Report for *Operations Research*

**Manuscript:** *NDU: A Generalization of Fixed-Preference Reinforcement Learning*  
**Repository:** TrillionniumFoundation/NDU  
**Latest revision branch audited:** revision/ndu-operations-research-r3-20260920  
**Revision tip audited:** 0473a2e4cf0d2162e93d6826e810c1f6d487b879  
**Current manuscript blob:** main.tex = 2569eee2eb7f80f0a5b31ed07be75d5da9e6a0d3  
**Previous referee branch:** review/operation-research-r3-harsh-20260920  
**Previous referee commit:** ef7cfa8325638bbe575492443ff305d2c4ab04cd  
**New referee branch:** review/operation-research-r4-harsh-20260920  
**Review type:** external fourth-round technical review, deliberately stringent  
**Recommendation:** **Reject / return without further revision credit in the current round. The branch does not contain a new paper revision or executed R3 result package after the previous referee report, and a central structural theorem remains false under the manuscript's own objective.**

---

## 1. Executive assessment

I audited the newest revision branch, its ancestry relative to the prior referee branch, the current root manuscript, the newly added R3 execution conventions and workflow, and the mathematical claims that remain central to the paper.

The first issue is procedural but decisive. The branch presented as the latest revision is two commits ahead of the previous R3 referee report, yet those two commits change only:

1. .github/workflows/ndu-or-r3-validation.yml; and
2. revisions/or-r3-20260920/EXECUTION_CONVENTIONS.md.

There is **no new main.tex**, no replacement PDF, no executed R3 result bundle, no new proof text, and no response that changes the scientific object previously reviewed. The root manuscript remains blob 2569eee2eb7f80f0a5b31ed07be75d5da9e6a0d3, exactly the manuscript already reviewed.

The newly committed execution-convention note confirms this status rather than resolving it. It is explicitly titled “Execution conventions fixed before R3 results,” and its final item says that the final R3 root entry point and PDF “will” refer to the new manuscript. In other words, the branch itself states that the scientific R3 manuscript and results are still future work.

That alone means there is no fourth scientific revision to credit.

I nevertheless re-audited the paper rather than stopping at the branch-integrity issue. The core defects remain material:

- the inventory service-pressure monotonicity theorem has the wrong sign under the stated maximization objective;
- the broad non-equivalence claim for fixed-parameter entropic risk-sensitive control is false at the stated level of generality;
- the operator “non-collapse” result distinguishes NDU only after the comparator is forbidden from using the valuation control as an ordinary action, while the authors' own exact-DP protocol correctly recognizes the exact expanded-action MDP;
- the physical-cost improvement theorem manually selects a state-dependent service parameter that reproduces the physical critical fractile, but does not prove that the NDU optimum selects that rule;
- the advertised compact-domain HJB certificate still does not specify a complete lateral boundary-value problem;
- the cover-refinement result states a quantitative continuous-HJB error bound without a scheme-specific rate argument, while the released inventory “refinement” keeps the state-time cover fixed and refines only the action cover;
- the large neural inventory row remains far from a genuine HJB certificate in absolute terms, while the reporting pipeline assigns “gap_closure_pass” as a literal status string and uses permissive relative-to-headline thresholds;
- extensive repository QA is still promoted into theorem/proposition/corollary rhetoric in the paper, obscuring the scientific core rather than strengthening it.

There are salvageable ideas. The exact expanded-action DP is the right equivalence check; the external-contract interpretation is more coherent than treating an internal shortage penalty as a control; and the direct-P versus Z-inversion calculation is a legitimate conditioning observation. But these pieces have not yet been assembled into a mathematically correct, economically coherent *Operations Research* paper.

---

# 2. Revision-integrity audit: the “R3 revision” is still a pre-execution shell

The repository comparison is unambiguous.

The previous referee branch review/operation-research-r3-harsh-20260920 ends at commit

ef7cfa8325638bbe575492443ff305d2c4ab04cd.

The current revision branch revision/ndu-operations-research-r3-20260920 is exactly two commits ahead. The only changed files are:

- .github/workflows/ndu-or-r3-validation.yml;
- revisions/or-r3-20260920/EXECUTION_CONVENTIONS.md.

The current root main.tex is still

2569eee2eb7f80f0a5b31ed07be75d5da9e6a0d3.

Thus the mathematical statements discussed in the previous report are still present verbatim.

The workflow also does not itself constitute an execution. Its validation step runs revisions/or-r3-20260920/validate.py only “when present.” The present revision delta does not add that validator or an executed result package.

The execution-convention note further states:

- the R2 protocol is to be executed byte-for-byte;
- no economic parameter or method is changed;
- the preserved historical root manuscript and PDF are archival evidence;
- the final R3 root entry point and PDF will refer to the new manuscript.

This is a useful preregistration-style step, but it is not a revised paper.

### Referee consequence

A journal referee cannot award revision credit for a plan to execute a revision later. The next scientific review should begin only after a new root manuscript, new result package, and theorem/proof changes are actually committed.

---

# Major comments

## 3. Fatal: the inventory service-pressure monotonicity theorem still has the wrong sign

The current manuscript defines the one-period inventory objective as

\[
R_t(x,S,\theta)
=
-c(S-I)^+
-h\,\mathbb E[(S-D_z)^+]
-p(\theta)\,\mathbb E[(B+D_z-S)^+]
-\lambda(\theta-\theta^-)^2
+\mathbb E[V_{t+1}(I',B',z',\theta)],
\]

with \(p'(\theta)>0\).

The theorem then states that the optimal valuation selector \(\theta_t^*\) is nondecreasing in backlog and demand stress. The proof says that the objective has increasing differences between \(\theta\) and shortage/backlog stress “because \(p(\theta)\) multiplies expected unmet demand.”

That proof drops the minus sign.

Let

\[
L(B,z,S)=\mathbb E[(B+D_z-S)^+].
\]

The stage term involving service pressure is

\[
-p(\theta)L-\lambda(\theta-\theta^-)^2.
\]

Its cross effect is

\[
\frac{\partial^2}{\partial\theta\,\partial L}
[-p(\theta)L]
=
-p'(\theta)
<0.
\]

This is **decreasing differences**, not increasing differences.

A one-period counterexample is immediate and lies inside the stated model class. Set the continuation value to zero, take \(p(\theta)=\theta\), \(\Theta=[0,1]\), and \(\theta^-=1/2\). For a fixed physical action the \(\theta\)-problem is

\[
\max_{\theta\in[0,1]}
\left\{
-\theta L-\lambda(\theta-1/2)^2
\right\}.
\]

Whenever the interior solution applies,

\[
\theta^*(L)=\frac12-\frac{L}{2\lambda}.
\]

After projection to \([0,1]\), \(\theta^*(L)\) is still nonincreasing in shortage exposure \(L\). Hence as backlog or demand stress increases shortage exposure, the optimal \(\theta\) moves **down**, not up.

The zero continuation value is convex and satisfies the manuscript's increasing-differences condition trivially. Therefore the claimed theorem is not saved by the continuation-value assumptions as written.

This is not a minor proof omission. It reverses the economic comparative static that the paper repeatedly advertises as an OR structural contribution.

### Required correction

Do not patch the current proof with another sentence. Replace the economic primitive.

If \(\theta\) is intended to be an externally priced service contract, insurance level, capacity commitment, or compensation schedule, then write that objective directly. The R2/R3 protocol already points toward a more coherent structure with an external premium, incremental liability, maintenance cost, and adjustment cost.

Then prove the desired lattice comparative statics from the actual cross-partials of that contract model. The theorem must state the conditions that produce increasing differences in \((\theta,B)\) and \((\theta,z)\); they cannot be inferred from an internal penalty term with the wrong sign.

The current theorem should not remain in any resubmission.

---

## 4. Fatal as stated: the entropic risk-sensitive non-equivalence corollary is false

The manuscript claims that active NDU valuation control is not equivalent to fixed-parameter entropic risk-sensitive control except in degenerate affine cases.

The proof argues that an entropic continuation operator is smooth/strictly curved, whereas “a finite valuation-control support function is piecewise affine and generally nonsmooth.”

This argument fails for two independent reasons.

### 4.1 The theorem does not assume a finite valuation set

The general NDU formulation uses compact valuation sets and elsewhere explicitly works with compact intervals. A supremum over a continuum of affine functionals need not be piecewise affine or nonsmooth. It can be smooth and strictly convex.

Therefore the sentence about a “finite valuation-control support function” introduces a restriction that is not in the corollary.

### 4.2 Entropic control has an exact variational support representation

For an action-conditioned reference kernel \(P\), the Gibbs/Donsker-Varadhan identity gives, under the standard absolute-continuity and integrability conditions,

\[
\frac{1}{\rho}
\log
\mathbb E_P
\left[
e^{\rho\beta V}
\right]
=
\sup_{Q\ll P}
\left\{
\beta\,\mathbb E_Q[V]
-
\frac{1}{\rho}D_{\mathrm{KL}}(Q\|P)
\right\}.
\]

This is precisely a supremum of affine functionals of the continuation value plus a penalty. If the NDU valuation-control coordinate is rich enough to parameterize the distorted kernels \(Q\), set

\[
P_\theta=Q,
\qquad
g_\theta=-\rho^{-1}D_{\mathrm{KL}}(Q\|P),
\]

and the entropic continuation operator is represented exactly by the same support-envelope geometry that the proof claims is impossible.

The fact that the risk parameter \(\rho\) is fixed does not remove this variational representation.

### Required correction

Delete the broad entropic non-equivalence claim, or replace it with a narrowly defined comparator class whose admissible transition/payoff family explicitly excludes the variational representation above.

The paper may legitimately prove non-equivalence to a specific fixed affine primitive. It cannot promote that result into a general non-equivalence theorem for entropic risk-sensitive control.

---

## 5. The core “non-collapse” result is mathematically narrow and does not separate NDU from ordinary stochastic control

The operator-level theorem says that if optimizing over \(\theta\) creates multiple exposed affine faces, then the resulting support envelope cannot be represented by **one fixed affine reward/transition primitive after the physical action is fixed**.

As a convex-analysis statement, this is reasonable.

But it is not a separation from ordinary dynamic programming or stochastic control.

If the actual decision is the pair

\[
(a,\theta),
\]

then ordinary stochastic control simply uses the expanded action space

\[
A' = A\times\Theta.
\]

The authors' own R2 protocol now recognizes exactly this point through the comparator named expanded_action_mdp and specifies that it enumerates every \((S,\theta)\) pair.

Thus the strongest valid reading is:

> a model with an extra controlled valuation coordinate cannot in general be reduced to a model in which that controlled coordinate is forbidden from the action space while the evaluator is held fixed.

That is essentially a policy-class inclusion fact.

It may still be useful modeling, but it is not a new dynamic-programming principle.

### OR consequence

The paper should stop using the non-collapse theorem as evidence that NDU is outside or fundamentally beyond standard stochastic-control representations. The scientifically interesting questions are instead:

- when is the extra controlled coordinate economically meaningful rather than a reward reparameterization?
- what structure does it produce in an operations model?
- can the joint problem be solved more efficiently than generic expanded-action control?
- what observability/conditioning problem is genuinely introduced by the continuous-time formulation?
- is there a policy or computational gain after comparing against an unrestricted state-aware ordinary controller?

Those are good questions. The current theorem does not answer them.

---

## 6. The physical-cost improvement theorem does not prove that NDU optimality causes the improvement

The theorem on “stable theta-free physical-cost improvement” is, at its core, a newsvendor mismatch bound.

For each regime \(z\), define the physical cost

\[
C_z(S)
=
h\,\mathbb E[(S-D_z)^+]
+
p_z\,\mathbb E[(D_z-S)^+],
\]

with optimal critical fractile

\[
S_z^*
=
F_z^{-1}
\left(
\frac{p_z}{h+p_z}
\right).
\]

A fixed service pressure chooses one common \(\bar p=p(\bar\theta)\), hence a regime-specific quantile at the wrong common critical-fractile level. The theorem then says an NDU rule “may choose” \(\theta_z\) such that

\[
p(\theta_z)=p_z.
\]

From there, strong convexity gives the cost gap. That derivation is fine as a conditional approximation/mismatch result.

But the theorem does **not** show that the optimizer of the NDU operating objective chooses this \(\theta_z\).

The rule \(p(\theta_z)=p_z\) is inserted by hand.

This is especially important because the manuscript's actual NDU objective includes valuation effects and adjustment costs. Once those terms are present, the optimizer need not choose the physical-cost-matching \(\theta_z\).

A conventional state-aware inventory controller that observes \(z\) can also choose \(S_z^*\) directly. It does not need an endogenous service-pressure variable to compute the critical fractile.

The manuscript itself partially concedes this by stating that the theorem does not imply dominance over an action-only oracle that directly optimizes the same physical cost.

### Required correction

Choose one of two paths.

**Path A: prove an NDU theorem.**  
Start from the actual endogenous-contract objective and prove that its optimal \(\theta^*(z,\theta^-)\), together with the optimal stock action, produces the claimed physical-cost bound under explicit conditions.

**Path B: relabel the theorem.**  
Present it as a restricted-comparator newsvendor mismatch result: allowing state-dependent service parameters can reduce physical cost relative to a single fixed service parameter. Do not attribute the improvement to NDU optimality.

At present the theorem is rhetorically stronger than its mathematics.

---

## 7. The R2/R3 contract protocol is more coherent, but it is still only a protocol

The predeclared model used by the R2/R3 protocol is materially different from the old root manuscript's “internal shortage penalty as a control.”

The protocol introduces:

- physical stock cost;
- an external regime-dependent contract premium;
- incremental contract liability;
- maintenance cost;
- adjustment cost;
- a persistent previous-contract state;
- exact rational finite-horizon dynamic programming;
- an exact expanded-action MDP comparator;
- a frozen-contract comparator;
- a physical-cost oracle.

This is a better OR model because \(\theta\) has an actual contractual cash-flow interpretation.

However, that model has not replaced the root paper. Nor has the current R3 branch executed and incorporated the preregistered experiment.

A protocol cannot repair a theorem in a manuscript that still uses the old primitives.

### Required correction

The next paper version should have one canonical economic model. The theorem statements, exact DP, figures, tables, and empirical interpretation must all refer to that same model.

Do not preserve the old internal-penalty theorem as the main OR story while relegating the coherent contract model to a protocol directory.

---

## 8. The HJB certificate theorem still does not state a complete compact-domain boundary-value problem

The NBO HJB-solver theorem fixes a compact parabolic domain

\[
D=[0,T]\times K
\]

and supplies a terminal mismatch bound on \(\{T\}\times K\). It then claims a sup-norm value bound from the interior HJB residual plus terminal residual.

But if \(K\) has a spatial boundary, a compact-domain parabolic HJB problem is not determined by a terminal condition alone.

One must specify, for example:

- Dirichlet boundary data;
- a Neumann/oblique derivative condition;
- a reflected controlled diffusion;
- a state-constraint viscosity boundary condition; or
- a stopped process with explicit boundary payoff.

These choices lead to different value functions and different comparison principles.

The proof acknowledges the problem after the fact. It says the result applies to state constraints or reflected/numerical boundary faces, and otherwise “the certificate must include the boundary residual on the nonterminal faces as part of \(\delta_H\).”

That is not a complete theorem statement.

A boundary residual is not automatically the same object as an interior HJB residual. A Dirichlet mismatch, Neumann defect, and state-constraint viscosity condition require different boundary operators.

### Required correction

State the boundary-value problem explicitly:

\[
\mathcal F[V]=0 \quad \text{in the interior},
\]

\[
\mathcal B[V]=0 \quad \text{on the lateral boundary},
\]

\[
V(T,\cdot)=G.
\]

Then include a separate certified boundary defect \(\delta_{\partial}\) in the stability inequality, with the comparison theorem appropriate to the stated boundary condition.

Until then, the advertised compact-domain certificate is incomplete.

---

## 9. The cover-refinement corollary asserts a rate-like bound that is not justified by the stated scheme hypotheses

The cover-refinement corollary assumes monotonicity, stability, consistency, an interpolation consistency error \(\eta_h\), and an action fill distance \(\rho\). It then states the quantitative bound

\[
0\le
V^*-V^{A_{h,\rho}}
\le
C_D
\left\{
\delta_T+
T(\delta_B+\delta_A+\eta_h+L_A\rho)
\right\}.
\]

The proof is one paragraph: discrete residuals are transferred through monotone/stable/consistent interpolation and then a continuous comparison estimate is invoked.

This is not enough for the displayed error bound.

Monotone + stable + consistent schemes are the basis of qualitative viscosity convergence arguments. They do not, by themselves, provide an additive first-order error estimate of the form displayed above. Quantitative rates require additional regularity and a scheme-specific consistency/stability analysis.

In particular, \(\eta_h\) is not a substitute for proving how interpolation and local truncation error propagate through the nonlinear HJB operator and the lateral boundary.

### Empirical mismatch

The released inventory_cover_refinement_certificate.csv does not even refine the state-time cover:

- state_count remains 122 at every reported level;
- Bellman state-time nodes remain 1220 at every level;
- only the action grid increases from 5 to 10 to 13 to 16;
- the reported action fill-distance proxy shrinks from about 1.206 to 0.546.

That is useful evidence of **finite action-cover refinement on one fixed discrete state-time problem**.

It is not an empirical realization of a sequence with \(h\to0\) for the continuous HJB domain.

### Required correction

Either:

1. prove a scheme-specific continuous-HJB error theorem with state-time mesh refinement, action refinement, boundary consistency, and the regularity needed for the stated rate; or
2. weaken the result to qualitative convergence and call the current artifact what it is: an exact finite-state/action-refinement audit.

---

## 10. The large neural inventory “certificate closure” remains a diagnostic, not a certificate

The manuscript is more cautious than earlier versions in some places, but the evidence hierarchy still overstates what the large neural inventory row establishes.

The integrated ladder reports for the inventory row approximately:

- native HJB ratio: 0.192341;
- normalized residual RMSE ratio: 0.979301;
- terminal-loss ratio: 0.929462;
- greedy-gap p95: 29.326960;
- greedy-gap sup: 120.040491;
- held-out delta: 0.0001994.

A normalized residual ratio of 0.979 is only a roughly two-percent improvement relative to the selected headline baseline. A terminal-loss ratio of 0.929 is not terminal convergence. Greedy gaps of 29.3 at p95 and 120 at the supremum are not small in any theorem-level sense absent a natural-scale normalization that turns them into a meaningful policy-loss bound.

Most importantly, Theorem nbo_hjb_solver_certificate requires certified absolute sup-norm residual, terminal, and greedy gaps that quantitatively control value/policy error, and an HJB solver sequence requires these quantities to tend to zero.

Ratios against a poor baseline do not establish that.

### 10.1 The ladder “pass” label is literally hard-coded

The generator reproducibility/scripts/make_hjb_solver_certificate_ladder.py constructs the inventory row and sets

status = "sampled_inventory_gap_closure_pass"

as a literal string. There is no numeric theorem predicate at that assignment.

A separate manifest contains threshold checks, but those thresholds are themselves relative-to-headline guards. For the inventory row they are approximately:

- native HJB ratio < 0.20, observed 0.19234;
- normalized RMSE ratio < 1.00, observed 0.97930;
- terminal-loss ratio < 0.94, observed 0.92946;
- greedy p95 < 30, observed 29.32696.

These are software acceptance guards. They do not derive from the HJB stability theorem, and several are close to the observed values.

I am not alleging misconduct or data manipulation. I am making a narrower methodological point: a repository status field named “pass” or “closure” is not independent scientific evidence unless its threshold is linked to a mathematically meaningful error target and the provenance of that target is clear.

### Required correction

For the neural experiments:

- report absolute residual, boundary/terminal defect, and greedy-gap scales;
- translate them into an actual value/policy-loss bound when the theorem's hypotheses are certified;
- demonstrate convergence across a prespecified sequence of training/discretization/validation refinements;
- separate pure QA thresholds from scientific tolerances;
- avoid words such as “certificate closure” for rows that are only sampled diagnostics.

---

## 11. The paper repeatedly turns repository QA into mathematical propositions

The manuscript contains a long stack of items with names such as:

- referee-objection closure;
- state/reward equivalence exclusion;
- strong-form claim closure;
- full-support referee synthesis;
- interval-domain certificate guard;
- bounded-architecture budget audit;
- cross-artifact consistency guard;
- refinement/stress guard.

Many of these are useful reproducibility checks. But they are not mathematical contributions at the same level as an OR structural theorem or an HJB convergence theorem.

Promoting them into propositions and corollaries has three costs.

First, it inflates the apparent theorem count without increasing the scientific content.

Second, it makes internal package labels look like external validation.

Third, it makes the main argument nearly impossible to audit because the reader has to distinguish genuine mathematical implications from deterministic spreadsheet/script checks.

### Required correction

Move software QA, hash checks, manifest consistency, replay status, and artifact stress tests into an online supplement or reproducibility appendix.

The main paper should contain only:

- the canonical OR model;
- the structural theorem(s);
- the exact equivalence/non-equivalence statement with correctly defined comparator classes;
- the computational theorem;
- the empirical/DP evidence directly tied to those claims.

An *Operations Research* paper should not need an internal “referee objection closure” proposition to tell the reader that the proof is correct.

---

## 12. The direct-P conditioning observation is one of the cleaner surviving results, but its scope must remain narrow

The algebraic conditioning statement

\[
Z_u^\varepsilon
=
\sqrt{2\varepsilon}\,P_u
\]

and therefore

\[
\widehat P_u^Z-P_u
=
\frac{\eta_Z}{\sqrt{2\varepsilon}}
\]

is correct under the stated additive-error model. Equal-scale \(Z\)-target error is amplified by \(1/(2\varepsilon)\) in mean-square shadow-price error after inversion.

The paper also correctly notes that directly regressing \(P\) is not automatically sufficient: \(P\) must still be a value gradient/adjoint, which motivates the value-gradient construction \(P_\beta=\nabla V_\beta\).

This is a useful numerical-conditioning point.

But it does not by itself validate the full NBO solver, and the empirical learned-Z/direct-P comparison should not be used to upgrade sampled residual diagnostics into a convergence certificate.

I would retain this result in a reconstructed paper, but present it as a conditioning/representation lemma rather than as evidence that the whole NDU framework has been solved.

---

## 13. OR contribution and positioning remain unresolved

The paper currently combines four different messages:

1. NDU is a strict generalization of fixed-preference RL;
2. NDU cannot collapse to several other control classes;
3. endogenous service pressure gives new inventory structure;
4. NBO solves the resulting continuous-time HJB more stably through direct shadow prices.

The first is largely action-space enlargement once \(\theta\) is recognized as an ordinary control.

The second is overclaimed and, for entropic risk, false as stated.

The third currently relies on a false monotonicity theorem under the root manuscript's objective.

The fourth contains a valid conditioning observation but an incomplete global solver certification story.

This leaves no single central theorem/contribution that currently meets the bar of *Operations Research*.

The R2/R3 external-contract model is the best route to a coherent OR paper because it can give \(\theta\) a genuine operational meaning. But that route needs to become the paper rather than remain a preregistered repository plan.

---

# 14. What I would require before any further scientific review

A further round would be worthwhile only after a genuinely new manuscript is committed. At minimum:

1. **Replace the root manuscript and PDF.**  
   A new revision must change the paper, not just add protocol/workflow files.

2. **Delete or fully replace the false service-pressure monotonicity theorem.**  
   Use an economically coherent external-contract primitive and prove the cross-partial/increasing-differences conditions correctly.

3. **Remove the broad entropic risk-sensitive non-equivalence claim.**  
   Either acknowledge the Gibbs variational representation or define a much narrower comparator class.

4. **Reposition the operator non-collapse theorem.**  
   State clearly that expanded-action stochastic control with \(A\times\Theta\) represents the joint problem exactly.

5. **Execute the preregistered R2/R3 contract protocol.**  
   Commit immutable outputs, exact-DP tables, independent recomputation checks, and all negative results.

6. **Use expanded_action_mdp as an exact equality sanity check.**  
   Any mismatch with the joint-contract DP is an implementation failure.

7. **Separate objective value from physical diagnostics.**  
   Do not infer physical-cost superiority from a valuation-welfare objective unless a theorem connects the two.

8. **Repair the HJB boundary-value statement.**  
   Define the lateral boundary operator/data and include the corresponding defect in the certificate.

9. **Either prove a real scheme-specific refinement theorem or weaken the cover-refinement claim.**  
   A fixed state grid plus denser actions is not continuous state-time HJB refinement.

10. **Replace relative “gap closure” labels with theorem-scale quantitative bounds.**  
    QA thresholds should be visibly separate from mathematical tolerances.

11. **Move reproducibility governance out of the theorem stack.**  
    Hashes, manifests, replay checks, and “referee closure” tables belong in the supplement.

12. **Condense the paper around one OR story.**  
    A state-dependent service/contract-control model with rigorous structure, exact expanded-action equivalence, computational reduction, and carefully scoped shadow-price conditioning would be far stronger than the current collection of generalized-RL taxonomies and audit layers.

---

# 15. Minor and presentation comments

Even after the mathematical issues are fixed, the presentation needs substantial simplification.

### 15.1 The theorem-scope table is too large and mixes unlike objects

Core theorems, numerical diagnostics, artifact audits, and internal evidence maps should not occupy equal rows in one “formal claim” table.

### 15.2 “Certificate” is used too broadly

Reserve “certificate” for an object that actually gives a mathematically valid bound under verified assumptions. Use “diagnostic,” “audit,” “replay check,” or “sampled guard” for the rest.

### 15.3 The title overstates the current contribution

“NDU: A Generalization of Fixed-Preference Reinforcement Learning” invites the reader to expect a substantive new RL/control class. If the final model is an endogenous service/contract control problem representable by an expanded action space, the title should emphasize the operational/economic mechanism and computational issue rather than generic RL generalization.

### 15.4 The old and new economics should not coexist

The internal shortage-penalty-as-control model and the external premium/liability contract model encode different economics. One should be canonical.

### 15.5 The empirical hierarchy should be made explicit

Separate:

- exact finite-model results;
- manufactured analytic PDE examples;
- sampled neural diagnostics;
- historical benchmark replays;
- any real-data/SKU evidence.

The current manuscript often places these in a single ladder, which risks suggesting they validate one another more strongly than they do.

---

# 16. Positive elements worth preserving

A harsh report should still identify what is worth keeping.

1. **Exact expanded-action DP.**  
   This is the correct representational baseline and should become a central sanity check.

2. **The external-contract interpretation.**  
   Premium/liability/maintenance/adjustment primitives are substantially more defensible than allowing the controller to lower its own internal shortage penalty.

3. **Direct-P conditioning.**  
   The \(1/\varepsilon\) inversion amplification is a clean numerical observation when scoped to the stated error model.

4. **Reproducibility engineering.**  
   The repository contains much more traceability than a typical theoretical paper. The problem is not the existence of these checks; it is their promotion into scientific theorem language.

5. **Willingness to retain negative/mixed physical results.**  
   This is the right evidence practice and should continue in the reconstructed version.

These strengths make a new paper plausible. They do not make the current manuscript publishable.

---

# 17. Recommendation to the editor

**Recommendation: Reject / return without further revision credit.**

My recommendation is driven first by revision integrity: the latest branch contains no new manuscript or executed R3 scientific result package after the previous referee report.

Independently of that procedural point, the current paper still contains a false central monotonicity theorem and an invalidly broad entropic risk-sensitive non-equivalence claim. The HJB and cover-refinement claims also require substantial formal repair, while the neural “certificate closure” language is not supported by theorem-scale absolute error control.

I would not recommend another ordinary incremental revision of this exact manuscript. If journal policy permits a substantially new resubmission, the authors should reconstruct the paper around the external-contract model, exact expanded-action equivalence, a correct OR structural theorem, a boundary-complete computational theorem, and a much cleaner separation between mathematical evidence and repository QA.

That reconstructed paper could be worth reviewing. The present branch is not yet that paper.
