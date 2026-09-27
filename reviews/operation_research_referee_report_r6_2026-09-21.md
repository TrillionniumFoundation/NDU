# Referee Report on Nominal R5

**Journal:** Operations Research  
**Manuscript:** *Neural Differential Utility: Endogenous Service Contracts and Certified Dynamic Optimization*  
**Reviewed branch:** revision/ndu-operations-research-r5-20260920  
**Reviewed head:** 31987afe62c630819de26e19a89dbbbec81a51e8  
**Scientific manuscript actually present:** R4 scientific manuscript, unchanged from revision/ndu-operations-research-r4-20260920 at 144d61b8f32521aa2431aa21d61a2ee1641adf61  
**Review date:** 2026-09-21  
**Round:** R6 external harsh review of the nominal R5 revision

## Recommendation

**Reject. Do not invite another incremental revision of this branch.**

The decisive fact is procedural and scientific at the same time: the nominal R5 branch contains **no substantive scientific revision relative to R4**. Comparing the R4 and R5 revision branches shows only two added files:

1. the previous R5 referee report on R4; and
2. a GitHub Actions workflow that exports the already reviewed baseline.

There are no changes to the active manuscript, electronic companion, theorem sections, numerical results, bibliography, or computational evidence. The active title page still says “Revision R4, September 20, 2026.” The electronic companion still says “Revision R4.” The README still identifies the branch as “Operations Research revision R4” and points to the R4 response-to-referee file. A corresponding R5 scientific response file under revisions/or-r5-20260920 is absent.

Accordingly, the manuscript has not responded to the previous referee report. The major publication blockers identified in that report remain intact. I therefore do not view the present branch as a new scientific revision.

Even putting the revision-integrity problem aside and rereading the scientific manuscript on its own terms, I would still recommend rejection for Operations Research. The paper contains several technically competent pieces, but it does not yet establish a sufficiently novel and coherent OR contribution. It remains an overextended combination of a small dynamic service-contract MDP, a useful one-dimensional envelope reduction, a Topkis-style monotonicity theorem, deterministic neural representation, and a largely separate manufactured HJB example.

---

# 1. Revision-integrity audit: R5 is not a scientific revision

This issue must be stated first because it changes how the entire round should be interpreted.

The R4 scientific branch head is

144d61b8f32521aa2431aa21d61a2ee1641adf61.

The nominal R5 branch head is

31987afe62c630819de26e19a89dbbbec81a51e8.

The R4-to-R5 comparison contains exactly two added files:

- reviews/operation_research_referee_report_r5_2026-09-20.md;
- .github/workflows/ndu-or-r5-validation.yml.

The intermediate commit e7e04eb45b190fe1ab0c3bf86502948a6101f1b7 is explicitly titled

“review(or): add R5 harsh referee report on R4 revision.”

The head commit is explicitly titled

“build(or-r5): isolate revision and export immutable reviewed baseline.”

That is not a manuscript revision. It is preservation of the previously reviewed state.

The active manuscript itself confirms this. main.tex begins with the comment

“R4 scientific manuscript”

and its title page says

“Revision R4, September 20, 2026.”

The electronic companion also says

“Revision R4, September 20, 2026.”

The README says

“NDU — Operations Research revision R4”

and directs the reader to revisions/or-r4-20260920/RESPONSE_TO_REFEREE.md.

There is no R5 response-to-referee document at the corresponding R5 path.

This means that, as an external referee, I cannot credit any scientific response to the previous round because none has been made in the reviewed branch.

A further packaging inconsistency is that the root NDU_OR_submission_checklist.md begins with an “R89 submission checklist snapshot (2026-05-27),” months and many internal rounds removed from the active R4 scientific manuscript. That checklist documents a different local evidence-packaging pipeline and is not a clean scientific revision record for the current OR paper. The repository therefore mixes current scientific material, historical QA machinery, and prior-round artifacts in a way that is inappropriate for a supposedly final journal revision package.

For a top-journal revision cycle, this is not a cosmetic defect. The branch should make it immediately auditable what changed scientifically, why it changed, and which referee requests were addressed. R5 does none of those things.

---

# 2. The previous central novelty objection remains completely unanswered

The manuscript still has only five bibliography entries:

- Federgruen and Heching (1999);
- Han, Jentzen, and E (2018);
- Kushner and Dupuis (2001);
- Ma, Protter, and Yong (1994);
- Topkis (1978).

That is plainly insufficient for a paper centered on persistent service contracts, adjustment costs, service-level decisions, dynamic inventory control, and switching behavior.

The previous report identified directly adjacent Operations Research and operations-management literature on monotone or hysteretic service controls, service-level agreements, inventory contracts, dynamic inventory policies under contractual incentives, and contract coordination. None of that literature has been incorporated because the manuscript has not changed.

The introduction still positions the contribution primarily against generic joint pricing/replenishment and lattice optimization. That does not answer the relevant novelty question.

The real comparison class is not simply “ordinary stochastic control.” The relevant comparison class includes dynamic service-level contracts, incentive contracts, SLA design, state-dependent contractual payments, and service-control systems with switching costs.

The manuscript still does not answer, theorem by theorem:

1. what is new relative to monotone service-control models with adjustment or switching costs;
2. what is new relative to inventory SLA models with penalties and premiums;
3. what is new relative to dynamic inventory policies under service contracts;
4. what is new relative to contract-design models with an explicit principal or customer;
5. what is computationally new beyond an ordered one-dimensional action-envelope reduction.

For Operations Research, novelty must be established against the closest literature, not merely against generic MDP notation.

---

# 3. The “service contract” remains institutionally incomplete

The canonical stage reward is

\[
g(z,q,S,\theta)
=
r_z\theta
-
C_z(S)
-
\kappa \theta L_z(S)
-
m\theta^2
-
\lambda(\theta-q)^2.
\]

The paper says that the provider “receives premium” \(r_z\theta\), pays shortage liability, pays maintenance, and pays adjustment cost.

But the model still contains no contractual counterparty.

There is no customer acceptance decision. There is no participation constraint. There is no demand response to the service tier. There is no regulator. There is no principal-agent structure. There is no service-level feasibility constraint. There is no endogenous premium schedule. There is no explanation for why the provider may observe the demand regime and then unilaterally choose a higher “contract” and collect the corresponding premium.

This makes the central economic object ambiguous.

If \(\theta\) is an insurance or coverage tier purchased from an exogenous menu, then say so and model the menu explicitly.

If \(\theta\) is a posted service tier purchased by customers, model customer choice or demand response.

If \(\theta\) is an SLA negotiated with a customer, model acceptance or participation.

If \(\theta\) is a service commitment, connect it to an actual service metric or probability constraint.

At present, \(\theta\) is mathematically a persistent control variable that changes transfers and shortage liability. Calling it a service contract does not by itself make it a contract-design model.

The institutional incompleteness matters because the principal computational result allows the provider to obtain higher net reward while serving less demand. Without a customer or service feasibility mechanism, this is not surprising: the provider is choosing a transfer/liability parameter that alters its own objective.

---

# 4. The central computational comparison still uses the wrong fixed-contract benchmark

This was the most important quantitative objection in the previous round, and it is unchanged.

The computational study explicitly states:

“Frozen contract fixes the economic contract at 0.5.”

That is not the economically relevant benchmark.

If the paper wants to measure the value of dynamic contract adaptation, the correct comparison is against the **best fixed contract chosen ex ante**, not against one arbitrarily fixed value.

The previous referee audit recomputed the fixed-contract problem from the manuscript primitives and found:

\[
\theta_{\mathrm{static}}^* \approx 0.58211039,
\]

with continuous fixed-contract value approximately

\[
W_{\mathrm{static}}^* \approx -5.870110973.
\]

On the paper's 0.1 contract grid, the best fixed contract is \(\theta=0.6\), with value approximately

\[
-5.873763514.
\]

The joint dynamic value is approximately

\[
-5.002310555.
\]

Therefore:

- reported gain versus the arbitrary \(\theta=0.5\) frozen baseline:
  \[
  0.944747061;
  \]
- gain versus the best fixed grid contract:
  \[
  0.871452959;
  \]
- gain versus the best continuous fixed contract:
  \[
  0.867800418.
  \]

The adaptive gain remains positive. That is not the issue.

The issue is that the paper still reports the wrong decomposition of that gain.

A nontrivial fraction of the headline improvement comes from replacing a suboptimal fixed contract, not from dynamic adaptation.

This is a basic benchmark-design error for an OR computational study.

---

# 5. The value of adaptivity is still not decomposed

The manuscript compares five methods, but these methods do not isolate the economic value of the proposed dynamic mechanism.

The important nested policy classes are still missing:

1. best static contract chosen ex ante;
2. time-dependent but state-independent contract;
3. regime-dependent contract that ignores inherited \(q\);
4. inherited-contract-dependent contract;
5. full state-dependent dynamic contract;
6. ideally, a version with service constraints or customer response.

Without this hierarchy, the reader cannot tell which component generates value:

- simply choosing a better contract level;
- adapting to time;
- adapting to demand regime;
- reacting to the inherited contract;
- exploiting contract persistence;
- exploiting switching-cost hysteresis.

The paper currently proves that the enlarged decision set can outperform one restricted policy class. Proposition 2.1 already makes that inclusion relationship obvious.

For a top OR contribution, the computational section should quantify the **marginal value of each source of adaptivity**.

It does not.

---

# 6. The structural theorem remains too thin relative to the switching-cost literature

The main structural result proves monotonicity of the greatest optimal stock/contract pair under a premium-liability compatibility condition.

The condition is

\[
r_{z_2}-r_{z_1}
\ge
\kappa\{L_{z_2}(S)-L_{z_1}(S)\}.
\]

For the translated-demand example it reduces to the primitive inequality

\[
1.4 > 1.2.
\]

The proof is a recognizable lattice-supermodularity argument using Topkis.

This is mathematically legitimate. It is not yet a strong enough structural contribution to carry an Operations Research paper about dynamic service contracts with persistence and adjustment costs.

The manuscript still does not characterize:

- switching thresholds;
- hysteresis bands;
- width of hysteresis as a function of \(\lambda\);
- comparative statics in \(\kappa\), \(m\), \(\lambda\), \(\beta\), or regime persistence;
- what happens when premium-liability compatibility fails;
- when the optimal contract is constant despite state variation;
- when inherited-contract persistence has first-order value;
- whether monotonicity survives economically standard nonlinear SLA payments;
- multidimensional contracts or multiple service attributes.

In a model whose main distinguishing feature is a persistent contract with quadratic adjustment cost, stopping at monotonicity leaves the most interesting switching-cost structure unexplored.

---

# 7. The service interpretation remains in tension with the numerical outcome

The paper reports:

\[
\text{fill rate under frozen policy} = 0.925926,
\]

and

\[
\text{fill rate under joint policy} = 0.882109.
\]

Thus the optimized “service contract” policy serves materially less demand.

The paper is transparent about this, which is good. But transparency does not resolve the conceptual problem.

The joint policy improves provider net reward and slightly lowers the defined physical cost while sacrificing service.

That is a cost-service tradeoff, not a service improvement.

If the paper wants to make an operational service-contract contribution, it should directly study one of the following:

\[
\min_\pi C^\pi
\quad
\text{s.t. fill rate}\ge \gamma,
\]

or an SLA penalty/bonus tied to an observed service metric, or a customer participation condition, or a Pareto frontier between provider profit and service performance.

Without such a formulation, the managerial statement is essentially:

“A provider allowed to adapt a premium/liability tier may choose to stock less and accept more lost demand.”

That may be true, but it is not yet a compelling new service-contract result.

---

# 8. The exact envelope algorithm is useful, but too specialized to support the paper's breadth

The upper-envelope identity

\[
V_t(z,q)
=
-\lambda q^2
+
\max_{\theta}
\{b_t(z,\theta)+2\lambda\theta q\}
\]

is a clean observation.

The resulting ordered-slope hull algorithm is also useful.

The contract-grid bound of order \(O(n^{-2})\) is one of the stronger technical pieces in the manuscript because it does not rely on global concavity.

However, this machinery exploits a very specific scalar quadratic adjustment structure.

The manuscript does not show:

- whether the method survives nonquadratic switching costs;
- whether it survives multidimensional contract states;
- whether it helps with continuous physical state variables;
- whether it materially improves solution time on a realistically scaled OR instance;
- whether it yields a new algorithmic complexity result beyond standard convex-hull maintenance;
- whether the threshold structure leads to implementable managerial rules.

At present, it is a good lemma/algorithm for the chosen model, not a broad computational contribution.

---

# 9. The “neural” contribution remains mostly branding rather than learning

The paper's constructive neural result takes an exactly computed piecewise-affine envelope and smooths its hinges with cubic-ReLU units.

That is a deterministic representation theorem.

It is not a trained neural algorithm.

The paper itself correctly says:

“This is constructive approximation and validation, not a newly trained neural solver.”

That sentence is scientifically responsible.

It also exposes the branding problem.

If the main finite-model neural result is a deterministic compilation of an exact value function into a small smooth network, then the word “Neural” in “Neural Differential Utility” is doing more conceptual work than the method justifies.

The large historical neural diagnostics are explicitly excluded from the current uniform-certificate claims.

The continuous-time least-squares comparison finds parity between direct-gradient and inferred-gradient parameterizations.

The manufactured HJB example does not require neural learning.

Therefore the manuscript has not shown that a neural method is necessary, superior, or even central to the main OR contribution.

---

# 10. The continuous-time HJB section remains scientifically disconnected from the main inventory-contract study

The stopped-domain verification theorem is reasonable.

The need to include lateral boundary defects is correct.

The policy-loss bound correctly charges value residual, action gap, and boundary defects.

But the theorem is a generic verification/certification result.

The numerical continuous-time example is manufactured:

\[
V^*(c,u)=\frac{c^2+u^2}{2}
\]

is known analytically, and the controls are chosen so that the HJB identity closes by construction.

The state-time-action refinement result is also tailored to this manufactured quadratic solution; central differences are exact and there is no temporal truncation term.

The manuscript itself admits this.

The problem is not correctness. The problem is relevance.

The continuous model is not a diffusion limit of the service-contract inventory problem. It is not calibrated to the same economic primitives. It does not demonstrate the envelope algorithm. It does not show a difficult high-dimensional service-contract control problem. It does not show neural training. It does not show a realistic application where the HJB certificate changes a decision.

Thus the continuous section remains an almost separate methods note attached to the inventory paper.

Operations Research papers can be broad, but the components need to reinforce one central scientific question.

Here they do not.

---

# 11. The direct-gradient conditioning story does not currently produce a method advantage

The paper motivates direct value gradients by noting that recovering an internal shadow price through

\[
Z_u^\varepsilon=\sqrt{2\varepsilon}P_u
\]

requires division by \(\sqrt{2\varepsilon}\), which can amplify a fixed additive error.

That algebra is correct.

But the paper's own identical-data least-squares experiment produces parameterization parity.

The text explicitly reports that the recovered gradients agree to floating-point precision and that naturally induced volatility error can shrink with the noise level.

Therefore the current experiment does not establish an empirical advantage for the direct-gradient parameterization.

This is another example where the manuscript has repaired an earlier overclaim by becoming scientifically honest, but the repaired claim is now too weak to support the larger narrative.

---

# 12. “NDU” still lacks a mathematically distinctive identity

The manuscript now states, correctly, that the full model is exactly an ordinary MDP on the product action space \((S,\theta)\).

That is the right mathematical statement.

But then the question becomes:

What exactly is Neural Differential Utility as a new object?

It is not a new admissible-control class.

It is not a new Bellman operator class.

It is not a non-MDP decision problem.

It is not a new stochastic calculus.

It is not a new neural training algorithm.

It is not a new risk-sensitive or robust-control operator.

It is not required for the HJB residual certificate.

The current paper says the term denotes “joint control of physical activity and a costly internal or contractual state.”

That is a modeling pattern, not yet a new theory.

There is nothing wrong with introducing a useful modeling pattern, but the title and repeated branding should be proportional to what has actually been established.

A much more credible title would focus on the concrete contribution: dynamic service contracts with adjustment costs, monotone policies, envelope algorithms, and value-of-adaptivity analysis.

---

# 13. The evidence architecture is still far more elaborate than the scientific contribution requires

The repository contains a very large amount of reproducibility, hash-ledger, package-parity, branch-isolation, and historical-preservation machinery.

Reproducibility is welcome.

But the current R5 branch illustrates the danger of allowing the evidence pipeline to become the project.

The branch has an R5 validation workflow but no R5 scientific revision.

The root checklist refers to R89 historical packaging.

The manuscript is R4.

The companion is R4.

The README is R4.

The previous referee report is committed onto the nominal R5 revision branch.

This is precisely the kind of process-heavy structure that can obscure rather than clarify the scientific state.

For journal review, the priority should be:

1. a scientifically new manuscript;
2. a point-by-point response;
3. an exact list of changed sections;
4. reproducible code for the actual claims;
5. a clean branch containing only the relevant current submission material.

The current repository has more machinery than scientific revision.

---

# 14. Specific technical comments that remain unresolved

These are secondary to the major contribution problems, but they should still be addressed in any future reconstruction.

## 14.1 Topkis theorem usage

The monotonicity proof should identify precisely which lattice maximization and monotone-selection theorem is being invoked, including compactness/continuity conditions and the order convention for stochastic monotonicity.

The current proof is plausible, but top-journal exposition should not leave the key comparative-statics step at the level of “this is the lattice optimization argument.”

## 14.2 Interior maximizer argument in the \(O(n^{-2})\) bound

The subgradient argument for

\[
f(x)=G(x)-Ax^2+\ell x
\]

is interesting but compact.

Because \(G\) is convex while the full objective need not be concave, the statement that the supporting-subgradient linear coefficient must vanish at an interior global maximizer deserves a standalone lemma with endpoint and nonsmooth cases spelled out carefully.

## 14.3 Neural network size accounting

The statement “at most 27 cubic-ReLU units” should define the architecture accounting convention.

Does the count exclude the quadratic skip connection, affine terms, or shared structure across states?

Without a standard size definition, the number is not comparable to conventional approximation results.

## 14.4 Continuous certificate positioning

The stopped HJB result should be presented as a verification theorem under explicit probabilistic and regularity assumptions.

It should not be allowed to drift rhetorically toward a general neural HJB convergence theorem.

The current text is much better on this point than older versions, but the overall title still invites that broader reading.

## 14.5 Manufactured-solution refinement

The displayed grid-rate proposition benefits strongly from the fact that the exact solution is quadratic and time independent.

A general OR computational claim would require a nonmanufactured problem in which the discretization has genuinely nonzero spatial and temporal truncation terms.

---

# 15. What a scientifically new submission would need

I would not recommend another nominal revision that merely adds checks, package metadata, or archival machinery.

A scientifically new submission would need at least the following.

1. **Define a real contracting institution.**  
   Specify who chooses the contract, who pays, what is observable, what service measure is promised, and why the premium schedule is available.

2. **Engage the closest SLA and dynamic-contract literature.**  
   The paper must explain its incremental contribution relative to service-level agreements, switching-cost service control, and dynamic inventory contracting.

3. **Optimize the fixed-contract comparator.**  
   The \(\theta=0.5\) baseline should not remain the headline comparator.

4. **Decompose adaptivity.**  
   Static, time-only, regime-only, inherited-state, and fully adaptive contract classes should be compared.

5. **Develop switching/hysteresis structure.**  
   The adjustment-cost state should generate more than monotonicity.

6. **Provide meaningful comparative statics.**  
   Especially in \(\lambda\), \(\kappa\), contract-premium slopes, regime persistence, and failure of the compatibility condition.

7. **Tie service directly to the model.**  
   Add a service constraint, customer response, or profit-service frontier.

8. **Choose one paper identity.**  
   Either develop a strong OR service-contract paper or develop a real continuous neural/HJB computational paper. The current manuscript tries to do both and fully achieves neither.

9. **If “neural” stays in the title, solve a real learning problem.**  
   Deterministic smoothing of an exactly known envelope is not enough.

10. **If continuous-time material stays, connect it to the operational model.**  
    The main computational example should not be an unrelated manufactured quadratic PDE.

11. **Use a clean revision branch.**  
    A new revision should contain a new manuscript, a new companion if needed, and a point-by-point response. The revision identifier in the manuscript, README, companion, and branch should agree.

12. **Retire stale submission machinery from the active root.**  
    Historical R89 packaging artifacts should be archived or clearly separated from the current OR submission.

---

# 16. Positive elements worth preserving

The recommendation is negative, but there are still components worth keeping in a reconstructed paper.

- The correction that the joint problem is exactly an expanded-action MDP is important and honest.
- The premium-liability monotonicity condition is interpretable.
- The inherited-contract envelope representation is clean.
- The ordered upper-hull algorithm is useful.
- The \(O(n^{-2})\) contract-grid value bound is a real analytic result.
- The manuscript carefully distinguishes net reward, physical cost, and fill rate.
- The authors do not hide the lower fill rate.
- The physical-cost oracle is retained rather than suppressed.
- The continuous certificate correctly accounts for lateral boundary error.
- The paper no longer upgrades sampled neural diagnostics into uniform guarantees.
- The least-squares conditioning experiment reports parity rather than manufacturing a favorable result.

These are meaningful scientific repairs from earlier versions.

They do not overcome the lack of a new R5 revision, the unresolved benchmark problem, the incomplete contract institution, the novelty gap, or the lack of a coherent central OR contribution.

---

# 17. Recommendation to the editor

**Reject.**

The nominal R5 branch should not be treated as a substantive revision. It is the R4 scientific manuscript plus the previous referee report and a workflow that exports the reviewed baseline.

Consequently the previous round's major objections have not been answered.

On the merits of the unchanged manuscript, the paper still has four central publication-level weaknesses:

1. the service-contract mechanism is economically underdefined;
2. novelty is not established against the relevant service-contract, SLA, and switching-cost literature;
3. the main dynamic gain is still measured against a nonoptimized frozen contract;
4. the manuscript combines a small finite inventory-contract model with a largely disconnected continuous HJB/neural methods component.

The cleanest path forward would be a genuine new paper centered on dynamic service-contract control: explicit contracting institution, optimized static benchmark, value-of-adaptivity decomposition, hysteresis/threshold structure, sensitivity analysis, and a service-constrained or customer-linked application.

I would not recommend another round based on repository hardening, validation gates, or relabeling of the existing R4 manuscript as R5. The next review should occur only after there is an actual scientific revision.
