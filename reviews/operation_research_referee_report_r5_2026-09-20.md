# Referee Report on R4

**Journal:** Operations Research  
**Manuscript:** *Neural Differential Utility: Endogenous Service Contracts and Certified Dynamic Optimization*  
**Reviewed branch:** `revision/ndu-operations-research-r4-20260920`  
**Reviewed head:** `144d61b8f32521aa2431aa21d61a2ee1641adf61`  
**Review date:** 2026-09-20  
**Round:** R5 external harsh review of the R4 scientific revision

## Recommendation

**Reject in the present form.** If journal policy permits, I would be willing to look at a substantially reconstructed new submission, but I would not recommend another incremental revision of the current manuscript.

This recommendation is no longer driven by the fatal defects identified in the previous round. R4 is a genuine scientific revision: the root manuscript has been replaced, the old internal-penalty monotonicity claim has been removed from the active theorem stack, the entropic-control overclaim has been corrected, the expanded-action representation is stated honestly, the compact-domain HJB theorem now includes lateral boundary data, and the earlier fixed-state action-refinement audit is no longer presented as continuous state-time convergence. The authors also retain negative results rather than deleting them.

The problem is now more fundamental. Once the incorrect claims are repaired, the paper that remains does not yet establish a sufficiently novel, unified, and operationally convincing contribution for *Operations Research*. The manuscript currently combines:

1. a finite-horizon Markov decision problem with an endogenous service/contract action and quadratic switching cost;
2. a one-dimensional upper-envelope computation and contract-grid approximation bound;
3. a deterministic spline-to-cubic-ReLU construction;
4. a generic residual verification theorem for a stopped HJB problem;
5. a manufactured two-dimensional diffusion example; and
6. an algebraic conditioning observation whose accompanying least-squares experiment is exactly a reparameterization.

Several of these pieces are correct and useful. I do not see a convincing argument that their combination is a new OR theory, a new computational method of meaningful scale, or a sufficiently developed service-contract model.

---

# 1. R4 has fixed the previous round's correctness crisis

I want to state this explicitly because the present report should not recycle objections that R4 actually resolved.

The following issues are materially improved:

- the root paper is now the external premium/liability contract model rather than the old penalty-only model;
- the service-pressure sign error is preserved as a counterexample instead of defended;
- Proposition 2.1 correctly says that the joint problem is exactly an ordinary MDP on the product action space;
- the broad entropic non-equivalence claim is replaced by the Gibbs variational identity;
- the monotonicity theorem is now tied to a cash-flow condition that gives the required increasing differences;
- the physical-cost claim is reduced to an accounting identity plus an oracle comparison;
- the continuous HJB certificate has terminal and lateral boundary defects;
- the numerical refinement proposition is scheme-specific;
- the large historical neural diagnostics are no longer upgraded into uniform certificates;
- repository QA has largely been removed from the active theorem stack.

These are substantial repairs.

They also expose the central question more sharply: **what is the publishable OR contribution after these repairs?** I do not think the manuscript currently answers that question.

---

# 2. The manuscript has not established novelty against the directly relevant service-contract literature

The bibliography of the active paper contains only five references:

- Federgruen and Heching (1999);
- Han, Jentzen, and E (2018);
- Kushner and Dupuis (2001);
- Ma, Protter, and Yong (1994);
- Topkis (1978).

That is not an adequate literature position for a paper whose central story is a persistent service contract with penalties, premiums, dynamic stocking, and switching/adjustment costs.

A limited referee search immediately finds directly adjacent work that is absent from the manuscript, including:

- Hipp and Holzbaur (1988), “Decision Processes with Monotone Hysteretic Policies,” *Operations Research* 36(4):585–588. This paper explicitly studies dynamic service levels with switching costs and establishes monotone/hysteretic policy structure.
- Plambeck and Zenios (2003), “Incentive Efficient Control of a Make-to-Stock Production System,” *Operations Research* 51(3):371–386. This is a dynamic inventory/control contracting paper with state-dependent incentive payments.
- Caggiano, Jackson, Muckstadt, and Rappold (2007), “Optimizing Service Parts Inventory in a Multiechelon, Multi-Item Supply Chain with Time-Based Customer Service-Level Agreements,” *Operations Research* 55(2):303–318.
- Katok, Thomas, and Davis (2008), “Inventory Service-Level Agreements as Coordination Mechanisms: The Effect of Review Periods,” *Manufacturing & Service Operations Management* 10(4):609–624.
- Sieke, Seifert, and Thonemann (2012), “Designing Service Level Contracts for Supply Chain Coordination,” *Production and Operations Management* 21(4):698–714.
- Liang and Atkins (2013), “Designing Service Level Agreements for Inventory Management,” *Production and Operations Management* 22(5):1103–1117.
- Hosseinifard, Shao, and Talluri (2022), “Service-Level Agreement with Dynamic Inventory Policy: The Effect of the Performance Review Period and the Incentive Structure,” *Decision Sciences* 53:802–826.
- Abbasi, Bruzda, and Gavirneni (2022), “Optimal Operational Service Levels in Vendor Managed Inventory Contracts—An Exact Approach,” *Operations Research Letters* 50(5):610–617.

This list is not claimed to be exhaustive. That is precisely the point: even a shallow search reveals a mature adjacent literature.

The current paper therefore cannot simply say that joint pricing/replenishment is known, cite Federgruen–Heching, and then present its own contract state as though the surrounding service-contract literature were empty. The closest comparison is not generic joint pricing. It is dynamic service-level agreements, service-contract incentives, and monotone/hysteretic service controls with adjustment costs.

### Required correction

The authors must conduct a real literature review and answer, theorem by theorem:

1. What is new relative to monotone/hysteretic service-control MDPs with switching costs?
2. What is new relative to inventory SLAs with penalty/bonus contracts?
3. What is new relative to dynamic inventory policies under SLAs?
4. What is new relative to contract-design models in which one party chooses contract terms and another party responds?
5. What is new computationally beyond a one-dimensional upper hull for ordered actions?

Until those comparisons are made, the novelty claim is not auditable.

---

# 3. The “contract” mechanism is not yet economically complete

The new external-contract model is much better than allowing the controller to lower its own internal shortage penalty. But it still has a serious institutional ambiguity.

The provider chooses (	heta) and immediately receives premium (r_z	heta). It also pays incremental shortage liability, maintenance, and adjustment costs. There is no customer, principal, regulator, or contracting counterparty in the model. There is no acceptance decision, participation constraint, promised service constraint, demand response, or mechanism explaining why the provider may unilaterally choose a larger contract and collect the corresponding premium.

This raises a basic question:

**What exactly is (	heta)?**

If it is a contract negotiated with a customer, the model is missing the customer side.

If it is a posted service tier, the model is missing acceptance/demand for the tier.

If it is an internally selected insurance/coverage level under an exogenous tariff, that can be coherent, but it should be described that way rather than as a generic endogenous service contract.

If it is a service-level commitment, the mapping from (	heta) to actual service is too weak: (	heta) changes a premium and a shortage-liability coefficient, but it does not impose a service constraint.

The numerical result makes the ambiguity visible. The optimized joint policy has **lower fill rate** than the frozen policy:

[
0.882109 < 0.925926.
]

Thus the paper's endogenous “service contract” can improve provider net reward while serving less demand. That may be a perfectly valid profit-maximizing outcome. It is not naturally interpreted as a stronger service commitment without a more explicit contract mechanism.

### Required correction

The authors need to specify the institutional interpretation:

- Who offers the contract?
- Who accepts it?
- Who pays the premium?
- What observable performance triggers liability?
- Can (	heta) be changed after observing (z)?
- Why is the premium schedule (r_z	heta) available after the demand regime is observed?
- Is (	heta) a contractual service target, a penalty intensity, an insurance tier, or an operating mode?
- If it is a service target, why is there no direct service-level feasibility or performance condition?

At present the mathematics is clearer than the economics.

---

# 4. The main numerical comparison uses the wrong fixed-contract benchmark

This is the most important new quantitative objection in this round.

The headline comparison is between:

- the joint dynamic contract policy, and
- a frozen contract fixed at (	heta=0.5).

But (	heta=0.5) is not optimized within the class of fixed contracts.

Therefore the reported gain of approximately

[
0.944747
]

is not the value of dynamic contract adaptation relative to the best fixed contract. It is the value of dynamic adaptation **plus** the value of moving away from an arbitrarily fixed (	heta=0.5).

This matters because Proposition 2.1 already proves that the joint policy cannot be worse than any particular frozen policy. The economically meaningful comparator is the **best policy in the fixed-contract class**, not one prespecified value.

## 4.1 Independent referee audit

I recomputed the fixed-contract problem directly from the primitives displayed in the manuscript. The calculation reproduces the manuscript's (	heta=0.5) value to machine precision, so this is not a different model.

For the relevant fixed-contract optimum, the state-aware stock choices remain

[
S_0=2,qquad S_1=3,qquad S_2=4.
]

Under the initial state (z=1,q=0.5), the fixed-contract objective in the neighborhood of the optimum is

[
W_{mathrm{static}}(	heta)
=
-9.58737773159547
+
(14.4171093708203-1.73005312449843)	heta
-
1.5(7.20855468541013)	heta^2
-
0.6(	heta-0.5)^2.
]

Its continuous maximizer is approximately

[
	heta_{mathrm{static}}^*=0.58211039,
]

with value approximately

[
W_{mathrm{static}}^*=-5.870110973.
]

On the paper's (0.1)-spaced contract grid, the best fixed contract is (	heta=0.6), with value approximately

[
-5.873763514.
]

The joint dynamic value is

[
-5.002310555.
]

Hence:

- headline gain versus the reported (	heta=0.5) baseline: (0.944747061);
- gain versus the best fixed grid contract: (0.871452959);
- gain versus the best continuous fixed contract: (0.867800418).

So the central adaptive gain remains positive, but the current headline overstates it. About 8.1% of the reported gain disappears when the fixed comparator is optimized.

More importantly, the paper is currently answering the wrong economic question.

### Required correction

The computational section should at minimum report:

1. best frozen contract chosen ex ante;
2. best time-dependent but state-independent contract;
3. best regime-dependent contract that ignores inherited (q);
4. full regime-and-(q)-adaptive contract;
5. the value added by inherited-contract persistence itself;
6. sensitivity to (lambda), so the value of flexibility versus switching cost is visible.

Without this decomposition, the numerical experiment does not isolate the value of the proposed dynamic mechanism.

---

# 5. The structural theorem is plausible, but its OR content is thinner than the manuscript suggests

Theorem 3.2 is a substantial improvement over the previous false monotonicity claim. I do not see the earlier sign error in the new proof.

However, the theorem now says roughly:

- demand becomes stochastically larger with (z);
- the transition is stochastically monotone;
- premium growth is at least as large as the increase in contractual shortage exposure;
- quadratic adjustment creates complementarity between current and inherited contract;
- therefore a greatest optimal stock/contract pair is nondecreasing in (z) and (q).

This is a recognizable Topkis-style result.

The key condition

[
r_{z_2}-r_{z_1}
ge
kappa{L_{z_2}(S)-L_{z_1}(S)}
]

is also almost exactly the sign condition needed to make the ((	heta,z)) cross difference nonnegative. In the translated-demand example it is reduced to (1.4>1.2).

That is mathematically fine. It is not yet a deep economic characterization.

The paper does not show:

- whether the condition is close to necessary;
- what happens when it fails;
- whether there are threshold or hysteresis regions;
- how switching-cost magnitude changes those regions;
- how contract persistence changes stock sensitivity;
- comparative statics in (m,lambda,kappa,eta), or regime persistence;
- whether the result survives a more standard SLA payment structure;
- whether the result extends beyond a scalar ordered contract.

The omission is particularly important because monotone and hysteretic service controls with switching costs have long been studied in OR.

### Required correction

The authors should either strengthen the structural contribution substantially or narrow the novelty claim.

A stronger version would characterize switching thresholds/hysteresis bands and comparative statics in the adjustment cost, rather than stopping at monotonicity of the greatest optimizer.

---

# 6. The “service contract” is not tied tightly enough to service

The paper carefully reports that fill decreases. That transparency is good.

But the result creates a conceptual tension that is not fully confronted.

The joint policy reduces physical cost from about (9.5874) to (9.3742), yet fill falls by roughly 4.38 percentage points. In the current model, one way to save physical cost is simply to carry less stock and lose more demand. That is exactly what occurs in part of the state space.

This means the physical-cost comparison is not an operational-efficiency result in the usual sense. It is a cost/service trade-off.

The paper says this in words, but the title and service-contract interpretation still invite a stronger reading.

A serious OR treatment should therefore present a Pareto frontier or constrained formulation, for example:

[
min C^pi
quad
	ext{s.t. fill rate}ge gamma,
]

or a customer-side service requirement tied to (	heta).

Otherwise the managerial implication is mainly: “if the provider is allowed to change the premium/liability tier, it may rationally serve less demand in some states.”

That is not obviously a new service-contract insight.

---

# 7. The exact envelope algorithm is useful but currently too narrow to carry the paper

The envelope representation is one of the cleaner parts of R4.

For fixed (z,t), after eliminating stock, the inherited-contract value is a maximum of affine functions in (q) minus a quadratic term. Ordered slopes allow an upper-hull construction. That is computationally useful.

However, the claimed computational contribution needs to be put in perspective.

The result relies heavily on:

- a scalar ordered contract;
- quadratic adjustment (-lambda(	heta-q)^2);
- an action-independent next inherited state (q'=	heta);
- separability that lets stock be eliminated first;
- a small finite regime set.

The paper states an (O(N_	heta)) hull construction after other terms are computed, but it does not give a full end-to-end complexity theorem in (T,|mathcal Z|,N_S,N_	heta,N_q), including continuation expectations and stock-stage calculations.

The numerical instance itself is tiny: 8 periods, 3 regimes, 13 stock actions, and 11 contract actions in the primary grid. Exhaustive joint DP requires only 37,752 Bellman candidates.

That is an excellent correctness test. It is not evidence of a difficult computational problem.

### Required correction

Either:

- demonstrate a genuinely large instance in which the hull materially changes tractability; or
- reposition the hull as a structural lemma rather than a major computational contribution.

The paper should also discuss whether the method extends to multidimensional contract states. A scalar convex hull is not a general “NDU” solver.

---

# 8. The (O(n^{-2})) contract discretization bound is neat but should be scoped more modestly

Theorem 3.4 appears internally coherent and is stronger than simply comparing two numerical grids.

But its significance is narrower than the paper's framing suggests.

The bound is for contract discretization while retaining the same stock action set. It exploits a very specific “convex term minus quadratic” structure. It does not provide:

- stock discretization error;
- a continuous-inventory approximation theorem;
- a diffusion limit;
- multidimensional contract discretization;
- a generic approximation theorem for the broader NDU framework.

In this particular experiment the demand support is discrete and the stock grid contains the important knots, so this limitation may not hurt the example. But it does limit the generality of the theoretical claim.

The paper should say more explicitly that this is a one-dimensional semiconvex grid bound for this contract structure, not a general approximation theory for endogenous utility/control states.

---

# 9. The “constructive neural critics” are a deterministic spline compilation, not a neural optimization result

Corollary 3.5 is mathematically legitimate. It is also being asked to carry more conceptual weight than it deserves.

The exact finite-grid value is already known. The authors write its one-dimensional convex piecewise-affine part as hinges and smooth each hinge with a cubic finite-difference formula. This yields a small cubic-ReLU representation.

No network is trained.

No high-dimensional approximation problem is solved.

No optimization difficulty is overcome.

A separate network is effectively indexed by each discrete ((t,z)) pair.

The maximum network size is 27 cubic-ReLU units.

The resulting policy equality on the grid is unsurprising because the network was constructed directly from the exact value envelope and the smoothing error is made small.

This is better described as a smooth spline/network representation theorem than as evidence for a “neural” dynamic-optimization method.

### Required correction

If the authors keep this result, I recommend moving it to the electronic companion unless they can show a computational or theoretical consequence that is not already obtained from the exact envelope.

The paper should not use this construction to justify the broader “Neural Differential Utility” branding.

---

# 10. The continuous-time HJB section is still a different paper

The authors now clearly state that the stopped diffusion is **not** a diffusion limit of the perishable inventory model. That fixes an earlier overreach.

It also leaves a major integration problem.

The continuous-time section uses:

- a different state space;
- a different reward;
- a different control problem;
- a generic residual theorem;
- a manufactured quadratic solution;
- a separate finite-difference scheme.

No result transfers quantitatively from the finite inventory-contract model to the diffusion example.

No contract-policy result from Sections 2–4 is needed for the manufactured HJB example.

No HJB certificate is used to solve a continuous counterpart of the inventory contract.

This reads as a second methods note appended to the service-contract paper.

Theorem 5.2 itself is essentially a stopped Itô verification/residual argument under assumed DPP/comparison/selectors. The repaired boundary accounting is correct and useful, but the paper does not establish that this generic bound is a new OR contribution.

Proposition 5.3 is even more special: the exact solution is quadratic and time-independent, central differences are exact on the second derivative, and there is no temporal truncation term for this manufactured solution. It is a clean regression test, not a difficult numerical demonstration.

### Required correction

Choose one of two directions.

**Direction A: service-contract paper.** Remove most of the continuous HJB material from the main paper and focus on the finite operational model, structure, adaptivity value, and contract economics.

**Direction B: continuous computational paper.** Derive and solve a genuine continuous-state counterpart of the contract model and show that the residual/gradient machinery matters there.

The current hybrid is too diffuse.

---

# 11. The direct-(P) conditioning experiment is algebraically predetermined

Lemma 5.1 is a narrow linear-algebra observation:

[
Z_u=sqrt{2arepsilon}P_u.
]

If a fixed additive error is imposed on (Z_u), inversion amplifies it by (1/sqrt{2arepsilon}), hence squared error by (1/(2arepsilon)).

That statement is correct.

The accompanying experiment, however, is not evidence of an algorithmic advantage. The paper itself shows that the two least-squares design matrices are related by deterministic column scaling and span exactly the same fitted function class. Therefore the recovered shadow-price functions must coincide in exact arithmetic.

In other words, the reported parity is not an empirical discovery; it is an identity.

The condition-number table is also parameterization-dependent. Simple column normalization can change a design-matrix condition number without changing the fitted function.

### Required correction

Either provide an actual learning/optimization setting in which direct gradient parameterization changes statistical or numerical behavior under a fair normalization, or reduce this section to a short conditioning remark.

At present this material does not support the paper's main operational claims.

---

# 12. The computational study is too synthetic and too narrow for the managerial conclusions

The exact rational implementation is excellent for verification. It is not external validation.

The entire main economic experiment uses one synthetic instance:

- 3 demand regimes;
- a four-point translated demand distribution;
- horizon 8;
- one transition matrix;
- one premium slope;
- one liability coefficient;
- one maintenance coefficient;
- one adjustment coefficient;
- one initial contract.

The R2 protocol being recorded before the R4 execution is useful for process integrity, but it does not make the parameter values economically representative.

There is no calibration source for:

- (r_z);
- (kappa);
- (m);
- (lambda);
- the regime transition;
- the chosen horizon;
- the contract range.

The key structural condition is then satisfied by design because premium slope 1.4 exceeds liability coefficient 1.2 in the translated-demand bound.

### Required correction

A publishable computational section should show at least:

- sensitivity to premium slope and liability;
- sensitivity across the boundary where Assumption 3.1 fails;
- sensitivity to adjustment cost (lambda);
- sensitivity to regime persistence;
- value of dynamic adaptation relative to the best static contract;
- service/profit trade-offs;
- threshold/hysteresis patterns;
- larger action/state grids;
- one calibrated or realistically scaled example if managerial claims are retained.

One exact toy model can validate code. It cannot establish broad operational relevance.

---

# 13. The robustness inequality is generic and does not establish robustness of the optimized conclusion

Equation (4.3) bounds the performance difference of the **same two fixed policies** when an exogenous one-step law is perturbed in total variation.

That coupling bound is fine.

But it does not prove stability of:

- the optimizer;
- the monotonicity region;
- the optimal contract;
- the sign of the reoptimized joint-versus-static advantage;
- the service trade-off after reselection.

The manuscript acknowledges this limitation.

Given that limitation, I do not see why this generic inequality deserves main-text space. It does not materially validate the economic result.

---

# 14. “Net reward” should not be called welfare

The paper defines

[
W^pi=K^pi-C^pi
]

where (K^pi) includes premium receipts.

That is a provider objective or provider net payoff under the stated accounting convention.

If the premium is paid by a customer, it is a transfer between parties. It is not social welfare unless the customer's utility/payment side is modeled.

The computational section contains the sentence “Improved welfare is not a synonym for higher service.” Under the current model, “welfare” is not the right term.

### Required correction

Use “provider net reward,” “provider profit,” or another precise term unless a social objective is explicitly modeled.

---

# 15. The NDU label remains underdefined as a scientific object

The paper now says that Neural Differential Utility denotes joint control of physical activity and a costly internal or contractual state.

But once Proposition 2.1 is accepted, that is an ordinary controlled Markov process with an enlarged action and state space.

The paper is admirably candid about this.

That candor creates a branding problem: what mathematically distinctive object does “NDU” denote?

It is not a new control class.

It is not a new Bellman operator class.

It is not a new neural training algorithm in the finite model.

It is not required for the HJB residual theorem.

It is not required for the convex-envelope theorem except as a name for the contract variable.

If “NDU” is merely a modeling pattern—physical action plus persistent endogenous contract/internal state—then that should be said explicitly and modestly. The title should probably be about dynamic service contracts with adjustment costs, not a new named theory.

---

# 16. Technical comments on the repaired theorem stack

These are secondary to the contribution concerns above.

## 16.1 Theorem 3.2

The proof should cite the exact lattice theorem used for:

- preservation of supermodularity under maximization;
- sublattice structure of the argmax;
- monotonicity of the greatest selection.

The current proof sketch is plausible, but a top OR paper should make the compact-chain/continuity assumptions and the Topkis correspondence theorem fully explicit.

The stochastic-monotonicity step should also state the order convention on (mathcal Z) and the exact definition of stochastic monotonicity being used.

## 16.2 Theorem 3.4

The subgradient argument is clever but terse.

At an interior maximizer of

[
G(x)-Ax^2+ell x
]

with (G) convex, the paper says that the linear coefficient from a supporting subgradient must vanish. This is correct under the intended argument, but it should be presented more carefully because the objective is not assumed concave.

I recommend a standalone lemma with all endpoint/interior cases.

## 16.3 Corollary 3.5

Clarify whether “network size” counts the quadratic skip connection, affine term, and all cubic-ReLU units in a conventional architecture measure. At present “27 units” is not fully comparable to standard network-size statements.

## 16.4 Theorem 5.2

The theorem assumes enough regularity for stopped Itô's formula and comparison. That is acceptable, but the result should be positioned as a verification/residual bound under these assumptions rather than as a general HJB convergence theorem.

## 16.5 Proposition 5.3

The special manufactured solution eliminates the temporal truncation term and makes the central second differences exact. The proposition should not be used rhetorically as evidence that the same rate or tightness will hold for a nontrivial operational HJB.

---

# 17. Presentation and paper architecture

R4 is much cleaner than the archived manuscript, but the article still contains too many identities.

A reader is asked to accept all of the following as one paper:

- service contracts;
- inventory monotonicity;
- exact MDP equivalence;
- entropic variational geometry;
- convex envelopes;
- grid discretization;
- cubic-ReLU smoothing;
- physical-cost accounting;
- total-variation robustness;
- FBSDE notation;
- singular volatility inversion;
- stopped HJB verification;
- manufactured PDEs;
- Markov-chain approximation;
- reproducibility execution.

The result is intellectually overpacked and scientifically undercentered.

My preferred OR paper here would be much simpler:

1. economically explicit dynamic service-contract model;
2. literature-grounded structural theorem;
3. threshold/hysteresis characterization;
4. value-of-adaptivity decomposition versus best static and simpler dynamic contract classes;
5. exact/envelope algorithm;
6. broad computational sensitivity and one realistic application.

The FBSDE/PDE/neural material could be a separate paper if it develops into an actual continuous computational method.

---

# 18. What I would require before a new scientific review

I would not recommend another round based only on polishing the current R4 manuscript. A meaningful resubmission should make the following changes.

1. **Define the contracting institution.**  
   Explain who chooses (	heta), who pays the premium, why the premium schedule is available, and how contract performance is measured.

2. **Engage the SLA/service-contract literature.**  
   The literature section must include the directly adjacent work and state the incremental theorem contribution precisely.

3. **Replace the (	heta=0.5) frozen baseline with an optimized fixed-contract comparator.**  
   Report the best grid and continuous fixed contracts.

4. **Decompose the value of adaptivity.**  
   Separate static, time-only, regime-only, inherited-state, and fully dynamic contract policies.

5. **Develop actual threshold/hysteresis results.**  
   Monotonicity alone is not enough given the prior switching-cost literature.

6. **Show economically meaningful sensitivity.**  
   Especially in (lambda,kappa,r_z), regime persistence, and the failure of the premium-liability compatibility condition.

7. **Treat service explicitly.**  
   Either impose a service requirement or present a provider-profit/service frontier.

8. **Choose a central paper identity.**  
   Either a dynamic service-contract OR paper or a continuous HJB/neural-method paper.

9. **Reduce the neural claim unless a real learning problem is solved.**  
   Deterministic cubic-ReLU compilation from an exact one-dimensional value function is not enough.

10. **If continuous-time material remains, connect it to the operational model.**  
    Do not rely on an unrelated manufactured quadratic PDE as the main evidence.

11. **Stop using “welfare” for provider net reward.**

12. **Expand the bibliography substantially.**

---

# 19. Positive elements worth preserving

Despite the recommendation, several parts are worth retaining.

1. **R4's revision integrity is strong.**  
   It actually replaces the manuscript and executes the new model.

2. **The external premium/liability interpretation is much better than the old internal-penalty control.**

3. **The exact expanded-action equality is the correct baseline and should remain.**

4. **The upper-envelope reduction is clean and useful.**

5. **The contract-grid bound is a real analytic bound rather than an observed-grid heuristic.**

6. **The paper now distinguishes exact finite-model results, manufactured PDE results, and historical neural diagnostics.**

7. **The authors report the lower fill rate and the stronger physical oracle rather than suppressing inconvenient outcomes.**

These are meaningful improvements. They are not yet enough for publication in *Operations Research*.

---

# 20. Recommendation to the editor

**Reject.**

R4 has converted the project from a manuscript with serious correctness problems into a largely coherent collection of correct or plausible results. That is real progress.

However, the corrected paper still has four publication-level problems:

1. the service-contract mechanism is economically underdefined;
2. the novelty case is not made against the directly relevant SLA, dynamic-contract, and switching-cost literature;
3. the central numerical comparison uses a nonoptimized frozen-contract baseline;
4. the manuscript combines a finite inventory-contract paper with a largely disconnected continuous HJB/neural methods paper.

The strongest route forward is not another layer of certificates or repository QA. It is a narrower and more economically serious OR paper centered on dynamic service-contract design/control, best-static versus adaptive value, hysteresis/threshold structure, and meaningful computational sensitivity.

The present R4 branch is substantially better than the manuscript I reviewed previously. It is still not at the level I would recommend for publication in *Operations Research*.
