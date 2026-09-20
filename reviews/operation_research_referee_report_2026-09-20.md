# Referee Report for *Operations Research*

**Manuscript:** *NDU: A Generalization of Fixed-Preference Reinforcement Learning*  
**Repository:** `TrillionniumFoundation/NDU`  
**Version reviewed:** commit `036c3b9914789ef5717a807598d04eacdbf0e1d9` on `main`  
**Review branch:** `review/operation-research-harsh-2026-09-20`  
**Review type:** external, deliberately stringent technical review  
**Recommendation:** **Reject in the present form. A publishable successor would require a fundamental reconstruction rather than an incremental revision.**

## 1. Executive assessment

The manuscript has an ambitious idea: make a valuation/service-pressure coordinate an endogenous costly control, connect that control to stochastic control/FBSDE language, and motivate a direct value-gradient (“direct-(P)”) numerical route when the preference-state diffusion becomes nearly degenerate. The repository is unusually extensive and contains substantial reproducibility engineering.

Unfortunately, the central scientific claims do not survive close scrutiny in their present form. The principal Operations Research structure theorem has a sign problem that produces the opposite comparative static in the simplest admissible special case. A central “non-equivalence” result for entropic risk-sensitive control is mathematically false as stated because the entropic Bellman term has a standard variational representation as a supremum of affine continuation-value functionals penalized by relative entropy. The core inventory experiments do not instantiate the inventory valuation model stated in the theory: in the main simulator, (	heta) acts primarily as an extra policy gate entering the order-up-to formula, while the shortage cost remains fixed. The headline inventory advantage also benefits from a larger optimization budget; the equal-budget rerun reverses the welfare and cost ordering, and the later positive 1536-evaluation result follows configuration screening and therefore is not an independent confirmation.

The HJB “certificate” layer is also overstated. The bounded-domain theorem omits nonterminal spatial boundary conditions from its statement even though its proof later acknowledges that a boundary residual is necessary unless a state-constraint/reflected problem is specified. The cover-refinement result asserts a generic finite-error rate from monotonicity/stability/consistency without a sufficiently specified numerical scheme or a rate theorem. The large neural inventory row, meanwhile, has normalized HJB residual above one and very large terminal/greedy gaps; calling a surrounding collection of self-defined audit guards “pass” does not convert those diagnostics into a PDE certificate.

In short, there are interesting ingredients here, but the current manuscript conflates four distinct claims:

1. a modeling proposal in which valuation parameters are controlled;
2. a trivial policy-class enlargement from (a) to ((a,	heta));
3. structural OR results for an inventory/service-pressure model; and
4. a neural HJB/FBSDE solver claim.

At present, (2) is true but not deep, (3) contains a core incorrect theorem, and (4) is not established by the reported neural evidence. I therefore cannot recommend publication in *Operations Research*.

## 2. What is genuinely positive

I want to separate the scientific objections from the engineering work. The repository is better organized and more auditable than most research submissions. It contains seed-level outputs, exact finite-state checks, multiple comparator tables, scripts, manifests, and explicit acknowledgments of several negative or mixed results. The manuscript also does something commendable by reporting cases in which physical metrics do **not** favor Full NDU rather than hiding them.

Those strengths make the substantive problems easier to diagnose. They do not, however, repair incorrect theorems or a mismatch between the theoretical control variable and the variable implemented in the main benchmark.

---

# Major comments

## 3. Fatal issue: the main inventory monotonicity theorem has the wrong sign

Theorem `thm:inventory_service_pressure_structure` is presented as the main OR structural result. The representative one-period objective in `main.tex` (around the subsection “Endogenous Service-Pressure Structure in Inventory”) contains the term

[
-p(	heta),mathbb E[(B+D_z-S)^+]
-lambda(	heta-	heta^-)^2,
qquad p'(	heta)>0,
]

inside a **maximization** problem.

The theorem then claims that the optimal valuation/service-pressure selector (	heta_t^*) is nondecreasing in backlog (B) and demand stress (z). The proof states that increasing differences hold because (p(	heta)) multiplies unmet demand. This is backwards: the manuscript has **minus** (p(	heta)) times unmet demand.

A one-period counterexample is immediate. Set continuation value to zero, let (p(	heta)=	heta), and for the moment hold (S) fixed. Write

[
H(B,z,S)=mathbb E[(B+D_z-S)^+]>0.
]

The (	heta)-dependent objective is

[
-	heta H(B,z,S)-lambda(	heta-	heta^-)^2.
]

When the interior solution is feasible,

[
	heta^*=	heta^- - rac{H(B,z,S)}{2lambda}.
]

Hence (	heta^*) is **decreasing**, not increasing, in expected shortage and therefore generically decreasing in backlog/stress. The same sign problem remains relevant when (S) is jointly optimized; the stated assumptions do not provide a continuation-value cross-effect strong enough to reverse it.

This is not a cosmetic proof gap. It exposes a conceptual problem: if (	heta) is literally an internally chosen penalty on shortage, a decision maker maximizing its own objective can improve that objective by lowering the penalty when shortage becomes painful. That is preference manipulation/reward hacking, not an operational service-pressure response.

### Required correction

The authors need to decide what (	heta) **physically is**.

- If (	heta) is an external service commitment, contractual penalty, inspection intensity, safety margin, or resource-backed target that changes the feasible system or creates an external transfer, model that mechanism explicitly.
- If (	heta) is merely an internal weight in the decision maker’s own objective, then the direction of optimal adjustment must be derived honestly, and the interpretation as “higher stress increases service pressure” cannot be asserted without additional structure.
- The lattice/Topkis proof must be rewritten with correct supermodularity/submodularity signs and an internally consistent cost-versus-reward convention.

Until this theorem is corrected, the principal OR contribution is not valid.

## 4. The claimed non-equivalence to entropic risk-sensitive control is false as stated

Corollary `thm:non_equivalence_models` claims, under the switching condition, non-equivalence to a risk-sensitive model with fixed entropic parameter except in an affine degeneracy. The proof argues that an entropic continuation operator is smooth/curved whereas a valuation-control support function is piecewise affine and generally nonsmooth.

There are two basic problems.

First, (Theta) in the manuscript is generally a compact **continuum**. A supremum over a continuum of affine functionals need not be piecewise affine or nonsmooth.

Second, and more decisively, the standard Gibbs/Donsker–Varadhan variational identity gives, for a finite nominal transition distribution (p) and (ho>0),

[
rac{1}{ho}logsum_i p_i e^{ho V_i}
=
sup_{qinDelta}
left{
sum_i q_i V_i
-rac{1}{ho}D_{mathrm{KL}}(q|p)
ight}.
]

The right-hand side is exactly a supremum of affine continuation-value functionals with a (	heta=q)-dependent intercept/penalty. In other words, an entropic risk-sensitive operator has precisely the kind of variational support representation the manuscript says cannot coincide with NDU except when affine.

This is standard in the risk-sensitive/robust-control literature; the manuscript itself cites Hansen–Sargent-style robust control, where relative-entropy perturbations and risk sensitivity are closely connected.

### Required correction

Delete the current broad non-equivalence claim. At most, prove a narrowly defined non-equivalence for a **specific restricted parameterization** of (g_	heta) and (P_	heta) that excludes the variational representations used by risk-sensitive/robust control. The paper must distinguish “our chosen parameterization differs from class X” from “class X cannot represent our Bellman operator.”

## 5. The “generalization of reinforcement learning” result is mostly an action-space enlargement

The manuscript correctly admits that, once ((c,u)) is treated as the state and ((a,	heta)) as the control, NDU is an augmented-state stochastic-control problem. That admission is important, but it also weakens the title-level theorem substantially.

The frozen-face embedding is essentially

[
A hookrightarrow A	imesTheta
]

by fixing (	heta=ar	heta). A larger action set weakly improves the optimum; a strictly useful extra action can strictly improve it. This is not a new expressivity theorem about dynamic programming or reinforcement learning.

The operator-level theorem does establish a small mathematical fact: after optimizing (	heta) out, the resulting action-conditioned term need not be one fixed affine functional of continuation value. But an ordinary MDP/control problem with the expanded action ((a,	heta)) represents the model exactly. Therefore the “non-collapse” result is largely a consequence of insisting that the comparator retain the old physical action set (A) while NDU receives (A	imesTheta).

For *Operations Research*, the important contribution would have to be **why (	heta) is an economically/operationally legitimate scarce control** and what new policy structure or performance consequences follow from that fact—not the observation that adding a control coordinate enlarges a policy class.

### Required correction

Reposition the contribution as an endogenous service-standard/valuation-control model, not a generalization of RL in an expressivity sense. State explicitly that standard augmented-state RL/control can solve the model when (	heta) is included as an action. Then identify the genuinely new OR object (e.g., commitment cost, service-level adjustment friction, endogenous risk budget) and derive nontrivial structure from that object.

## 6. The main inventory code does not implement the inventory model used in the theorem

This is a major theory–experiment disconnect.

In `reproducibility/scripts/run_inventory_service_level_benchmark.py`:

- Full NDU computes
  `theta = 0.55 + 1.65 * sigmoid(...)`;
- that `theta` enters the **policy formula** for `order_up_to`;
- the shortage cost is fixed as
  `shortage_cost = 2.85 * backlog`;
- the only direct objective term involving (	heta) is
  `theta_cost = 0.045 * (theta - 1.0) ** 2`.

Thus the main experimental (	heta) is primarily an additional nonlinear policy gate/action parameter. It is **not** the theoretical (p(	heta)) shortage-penalty coefficient in equation `eq:inventory_service_pressure_objective`.

The exact finite-cover/policy-class scripts use yet another construction: (	heta) enters a service/fill reward multiplier such as
`8.0 * theta * (fill_rate - 0.92)`, again not the theoretical (-p(	heta)	imes) shortage term. The SKU exact MDP uses still another calibrated valuation benefit/service penalty.

Therefore the manuscript currently has several different “theta” models connected mainly by terminology.

This also confounds the empirical comparison. The canonical main benchmark gives Full NDU a 12-dimensional policy parameterization and the action-only comparator 7 parameters. A richer multiplicative policy gate can improve action mapping even if there is no meaningful endogenous valuation mechanism.

### Required correction

There should be **one canonical inventory model**. Its Bellman equation, theorem, exact DP, finite-cover discretization, and simulation must all use the same primitives and the same meaning of (	heta). If a policy network internally uses extra latent gates, those are architecture features and must not be identified with the economic (	heta) unless the objective/dynamics make them the same object.

A strong baseline should also match the action policy’s representational capacity while disabling only the economically meaningful valuation-control channel.

## 7. The physical-cost “improvement theorem” is an oracle newsvendor comparison, not a theorem about NDU optimization

Theorem `thm:stable_physical_cost_improvement` assumes state/regime-specific physical shortage costs (p_z), then lets the NDU service-pressure rule choose (	heta_z) satisfying (p(	heta_z)=p_z). This produces the regime-specific newsvendor critical fractile (S_z^*). The comparator is forced to use one fixed (ar p).

Under the density lower bound, strict convexity of the newsvendor cost immediately yields the displayed quadratic loss from using the wrong fractile. That calculation is correct, but the interpretation is much weaker than the manuscript suggests.

The theorem does **not** show that the NDU objective learns or optimizes toward (p(	heta_z)=p_z). It simply gives NDU the correct regime-specific physical penalty by assumption. A same-information action-only policy that directly optimizes the theta-free physical cost can also choose the regime-specific (S_z^*) without introducing a preference-control variable at all.

The manuscript explicitly excludes that comparator, but that exclusion is exactly why this theorem cannot establish an operational performance advantage of NDU.

### Required correction

Either derive (	heta_z=p_z) (or an approximation to it) from the actual endogenous-(	heta) optimization problem, or present this result honestly as a calibration lemma showing the cost of a misspecified fixed service-pressure parameter. It should not be one of the main proofs of NDU’s practical value.

## 8. The compact-domain HJB certificate theorem is incomplete at the spatial boundary

Theorem `thm:nbo_hjb_solver_certificate` works on a compact parabolic domain (D=[0,T]	imes K) and states a sup-norm value bound using an interior HJB residual and terminal residual. The theorem statement does not specify data on the nonterminal spatial boundary ([0,T)	imespartial K), nor does it define a state-constraint/reflected boundary problem.

The proof later concedes the issue: if the compact certificate is not a state-constraint/reflected problem, the nonterminal boundary residual must be included. That requirement belongs in the theorem, not in a retrospective qualification in the proof.

Without a boundary condition, interior PDE residual plus terminal data do not uniquely characterize a bounded-domain parabolic solution.

The asserted constant (C_D) is also too generic. A rigorous result needs the exact properness/comparison setting, boundary condition, operator structure, and the barrier argument from which the quantitative estimate follows.

### Required correction

State the PDE problem completely, including boundary conditions. Define the residual on every relevant part of the parabolic boundary. Then prove the quantitative perturbation estimate for that specific problem.

## 9. The cover-refinement result invokes convergence theory but asserts an unproved generic error rate

Corollary `cor:cover_refinement_hjb_certificate` says that monotone, stable, consistent state-time covers plus interpolation error (eta_h) and action fill distance (ho) give a policy bound of the form

[
C_D{delta_T+T(delta_B+delta_A+eta_h+L_Aho)}.
]

The proof consists essentially of saying that interpolation transfers the discrete Bellman operator to the continuous operator with error (eta_h), then applying comparison.

This is not enough. The classical Barles–Souganidis framework establishes convergence of monotone, stable, consistent schemes under comparison; it does not, by itself, supply the generic linear finite-error rate displayed here. Quantitative error rates require additional regularity and scheme-specific approximation estimates.

Moreover, the manuscript does not specify a single numerical discretization with enough precision for a theorem of this strength. An “exact finite-cover solve” certifies the finite discrete dynamic program. It does not automatically certify the continuous HJB.

### Required correction

Either:
1. restrict the result to convergence (no generic rate) under a precisely defined monotone/stable/consistent scheme; or
2. provide a scheme-specific quantitative error theorem with the regularity assumptions needed for its rate.

Barles and Souganidis (1991) should be treated as a convergence theorem, not as a generic finite-sample error bound.

## 10. The reported neural NBO/HBO inventory solver is far from its own HJB certificate

The large neural rows are described carefully in some paragraphs as “certificate-gap evidence,” which is appropriate. But the manuscript repeatedly surrounds these rows with “solver,” “closure,” “pass,” and multi-guard language that overstates what the numbers show.

For the inventory headline NBO row, the paper reports approximately:

- native HJB loss (6.26	imes 10^4);
- normalized residual RMSE (1.84);
- terminal loss (2.06	imes 10^3).

The sampled greedy-gap audit is also very poor:

- actor residual (L^2/sup approx 204.6/805.6);
- grid-optimal residual (L^2/sup approx 417.0/1315.9);
- greedy gap p95/sup (approx 1257.7/1556.6);
- terminal sup (approx 75.1).

The actor-gap-focused inventory run reduces the greedy-gap sup to about (120), but terminal error remains about (75). The residual-focused run drives other terms down while the greedy-gap sup grows to roughly (1652). The selected normalized-residual Pareto run still has normalized RMSE (approx 1.805), i.e. the residual remains of the same order as or larger than the Hamiltonian scale under the manuscript’s own interpretation.

These are useful diagnostics of a difficult numerical problem. They are not evidence that the neural solver is close to satisfying the uniform HJB certificate.

### Required correction

Downgrade the neural claim to “heuristic actor–critic solver with residual diagnostics” unless and until a boundary-complete, near-zero sup-norm residual/terminal/greedy certificate is actually obtained on the same economically relevant instance.

The many downstream guard scripts should not be described as closing the HJB theorem when the primitive residual and greedy quantities remain large.

## 11. The headline inventory comparison is not optimization-budget matched, and the fair-budget rerun reverses the result

The canonical script `run_inventory_service_level_benchmark.py` allocates different CEM budgets:

- Full NDU: (11	imes26=286) policy evaluations;
- action-only adaptive base-stock: (9	imes22=198);
- fixed service: (8	imes18=144).

The headline 30-seed table then reports a small Full advantage.

The dedicated equal-budget rerun uses 192 evaluations for each method and reports:

- action-only welfare about (-3.7162);
- Full NDU welfare about (-3.7303);
- action-only theta-free cost about (4.3114);
- Full theta-free cost about (4.3207).

Thus the fair-budget result goes in the opposite direction.

The manuscript then reports a deeper 1536-evaluation positive result. But the corresponding audit file records several **screening** configurations (`welfare_1152`, `physical_guarded_1152`, `service_guarded_1152`, `welfare_1536`) before a selected `welfare_1536_confirm24` row. The script itself calls the routine `run_selected`, and the manuscript says the positive retest was selected after screening.

The reported confirmation interval therefore does not account for configuration selection/multiplicity. It should not be presented as independent confirmatory evidence.

### Required correction

Predeclare one common optimization protocol, match policy-evaluation budget and expressive capacity, and evaluate once on a fresh untouched test seed set. If configurations are tuned using physical signs, use nested tuning/test splits or adjust inference for selection.

## 12. The primary “theta-free cost” ledger appears to mislabel a cost that includes theta adjustment

This is a concrete reporting inconsistency that should be fixed before any further review.

In the canonical inventory simulator, `total_cost` includes

[
0.045(	heta-1)^2.
]

The stored `avg_cost` is computed from that total. The paired audit reports the headline Full-minus-action-only cost difference (-0.017328...) using the `avg_cost` column.

The primary OR ledger in `main.tex` places the same (-0.01733) number under the heading **“Theta-free cost.”**

That number is not theta-free according to the canonical simulator. The later equal-budget script correctly creates a separate `avg_cost_no_theta`, which makes the mismatch especially clear.

### Required correction

Regenerate the headline physical evaluator with a true theta-free cost, propagate it through every table/audit/claim, and state exactly which terms are included in each metric.

## 13. Strong OR comparators frequently match or beat Full NDU on the actual physical metrics

Several tables already reveal the central empirical issue:

- On the public SKU panel, Approximate DP has lower external cost ((approx0.3537) vs (0.3558)), higher fill, and lower backlog than Full NDU; Full wins only on its valuation-adjusted welfare.
- In the exact policy-class DP, Full has higher valuation welfare but worse average cost ((approx3.3912) vs (3.1948) for action-only).
- In the exact valuation-state MDP, Full improves valuation welfare but has the same theta-free cost/fill as action-only.
- In the PyTorch inventory row, Full improves the internal service-pressure welfare but has worse reported cost than action-only ((approx5.0211) vs (4.9314)).

These are not necessarily failures if the paper is explicitly about a different objective. But they severely weaken the claim that endogenous valuation control provides an OR performance benefit rather than simply optimizing a different score.

The manuscript should not let a (	heta)-dependent welfare improvement stand in for operational superiority.

## 14. The direct-(P) “observability paradox” is mostly an imposed scaling experiment

The algebraic lemma is correct under its assumptions:

[
Z_u=sqrt{2arepsilon}P_u
]

and additive (Z)-target noise of variance independent of (arepsilon) produces (P)-error amplified by (1/(2arepsilon)).

But the strength of the conclusion depends on the **equal absolute noise-scale assumption**. It is not a general statistical lower bound for every (Z)-based Deep BSDE method, nor do all such methods literally observe a noisy (Z) target and then invert it.

The empirical direct-(P)/(Z) experiments largely build in the same equal-scale perturbation, so they are primarily demonstrations of the algebra. In the same-architecture neural ablation, learned-(Z) even has better welfare at (arepsilon=10^{-1}) and (10^{-2}), becoming worse only in the near-singular (10^{-3}) regime.

The useful contribution here is a conditioning warning in a specific near-degenerate representation, not a general superiority theorem for direct-(P) learning.

### Required correction

Use a realistic end-to-end learning model in which noise/approximation error arises from the training procedure, report how error scales with (arepsilon), and narrow the wording from “paradox”/solver superiority to a conditioning result.

## 15. Too many “theorems” are actually artifact checks

The manuscript contains roughly fifty theorem-like environments, including propositions/corollaries with names such as referee-objection support, six-pillar claim support, bounded-architecture audit, cross-artifact consistency guard, leave-one-guard-out robustness, and stress-frontier guard.

Many of these statements have the form “if a packaged script checks these rows, then the audit passes,” and the corresponding proof says, in effect, that the script recomputes the table.

That is reproducibility documentation, not mathematical theory. Elevating it into theorem/proposition environments makes the paper look less rigorous, not more rigorous, because it obscures the distinction between:

- mathematical implication,
- numerical evidence,
- software consistency,
- and manuscript bookkeeping.

For a top OR journal, the paper should become much shorter and conceptually cleaner. Keep the reproducibility bundle; move almost all audit-gate material out of the theoretical narrative.

## 16. The “real-demand” evidence is not convincing external validation

The AirPassengers replay scales airline passenger counts into inventory demand units. This may be a useful nonstationary time-series stress test, but it is not real inventory operations evidence and should not be called a “real-demand calibration bridge” in a way that suggests business validation.

The SKU panel is more relevant, but the effective train/test history is short and bootstrap seeds do not create independent operational datasets. The physical comparison there also favors Approximate DP on cost/fill/backlog.

If empirical external validity is meant to be a central *Operations Research* contribution, the paper needs a substantially more credible operations dataset or a deliberately theory-first positioning with correspondingly modest empirical claims.

---

# 17. Additional technical and presentation comments

1. **Continuous-time versus discrete-time identity.** The manuscript begins as a continuous-time FBSDE/HJB theory paper but the primary OR contribution is a periodic-review inventory model with several bespoke discrete objectives. The bridge is not mathematically tight. The authors should choose a primary mathematical setting and make all other settings explicit specializations/approximations.

2. **“Neural” in NDU.** The paper itself says the neural parameterization is optional and not the core theory. The name therefore risks overstating the role of neural differential equations. If the novelty is endogenous valuation control, name and frame the object around that.

3. **Value/cost sign conventions.** The inventory structural proof mixes convex-cost reasoning with a reward-maximization value function. This should be cleaned up globally; it is likely related to the monotonicity sign error.

4. **Comparator semantics.** “Fixed preference,” “action-only,” “preference backbone,” and “augmented fixed-(	heta)” should be defined once, with matched information, parameter count, policy architecture, and optimization budget.

5. **State/action semantics.** If (	heta) changes the policy map directly, it is an action/control coordinate. If it changes a utility/penalty, it is a preference/evaluator coordinate. If it changes a service contract, it is an operational state/control with external consequences. The paper currently moves among all three meanings.

6. **Exact DP evidence.** Exact solution of a finite model is valuable, but the finite model must be the discretization/special case of the same theoretical model for it to validate the theory.

7. **Statistical uncertainty.** Inference should distinguish rollout Monte Carlo error, training-seed variability, hyperparameter/configuration selection, and model/data uncertainty. A very narrow paired-seed interval is not a substitute for the latter categories.

8. **Scope tables.** The manuscript contains multiple scope/certificate/support matrices that repeat claims. One concise claim-to-evidence table would be enough.

---

# 18. Minimum reconstruction needed before this could become an OR paper

A credible new version would need, at minimum, the following sequence.

### A. Rebuild the economic model

Give (	heta) a single operational meaning with external consequences or a defensible commitment/resource interpretation. Do not let the decision maker simply choose the coefficient that grades its own shortage.

### B. Re-prove the structural result from the corrected primitives

State the dynamic program in cost or reward form consistently. Prove the required increasing/decreasing differences with correct signs. Give a counterexample section showing why the result fails without the key assumptions.

### C. Narrow the model-class comparison claims

Acknowledge explicitly that standard augmented-state/action stochastic control represents NDU. Remove the false entropic risk-sensitive non-equivalence result. If a restricted non-equivalence is useful, define the restricted comparator class precisely.

### D. Make theory and experiments literally the same model

The exact DP, finite-cover problem, simulator, and theorem must use the same (p(	heta)), adjustment cost, transition law, and state variables. Any neural policy architecture should be an approximation layer on top of that model, not a new definition of (	heta).

### E. Run one predeclared, genuinely fair empirical comparison

Match information, policy capacity, and optimization budget. Tune on training/validation data and report once on untouched test seeds/data. Include a strong action-only policy that can observe the same state and has comparable representational capacity.

### F. Decide whether the paper is a modeling paper or a solver paper

If it is a modeling/OR-structure paper, remove most neural solver claims and audit machinery. If it is also a numerical PDE solver paper, provide a complete boundary-value problem, a precise scheme, a valid convergence/error theorem, and a genuinely small residual/terminal/greedy certificate on the economically relevant instance.

### G. Move software audits out of theorem environments

Keep them in the repository as reproducibility checks. They are useful engineering artifacts, but they should not be presented as mathematical propositions.

---

# 19. Confidential recommendation to the editor

**Recommendation: Reject.**

My recommendation is driven by substantive correctness, not taste or insufficient polishing.

The primary OR structure theorem has a direct sign counterexample under the manuscript’s own objective. The risk-sensitive non-equivalence corollary is contradicted by the standard entropy-penalized variational representation of the entropic operator. The main inventory experiment uses a (	heta) mechanism different from the one in the theory, and the main positive inventory comparison is not search-budget matched; the equal-budget comparison reverses the result. The neural HJB diagnostics remain far from the stated certificate conditions, while many artifact-level “pass” guards risk obscuring rather than resolving that gap.

The reproducibility engineering is a real strength and suggests that a substantially rebuilt paper could be evaluated efficiently. But the required changes go to the model definition, main theorem, novelty claim, benchmark implementation, and numerical theorem. That is beyond the scope of a normal revision cycle.

---

## References relevant to this report

- Barles, G., and P. E. Souganidis (1991), “Convergence of approximation schemes for fully nonlinear second order equations,” *Asymptotic Analysis* 4, 271–283. The classic result gives convergence of monotone, stable, consistent schemes under comparison; it is not by itself a generic finite-error-rate theorem.
- Gibbs/Donsker–Varadhan variational identity for log moment-generating functions / relative entropy. This provides the explicit entropic-risk counterexample discussed above.
- Hansen–Sargent robust-control/risk-sensitive formulations, already adjacent to the manuscript’s cited literature, provide additional reason to treat entropy-penalized transition distortions as a nearby representational class rather than as generically excluded.

