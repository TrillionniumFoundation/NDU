# Second-Round Referee Report for *Operations Research*

**Manuscript:** *NDU: A Generalization of Fixed-Preference Reinforcement Learning*  
**Repository:** `TrillionniumFoundation/NDU`  
**Revision branch reviewed:** `revision/ndu-or-r2-20260920`  
**Revision tip:** `fd37a524c491db0228b357285b0a7b2acb8be4fb`  
**Manuscript blob reviewed:** `main.tex` = `2569eee2eb7f80f0a5b31ed07be75d5da9e6a0d3`  
**PDF blob reviewed:** `main.pdf` = `3ed6d3446ad5eafe4f99e8279c28d37ae3a91068`  
**Prior referee report in repository:** `reviews/operation_research_referee_report_2026-09-20.md`  
**New review branch:** `review/operation-research-r2-harsh-20260920`  
**Review type:** external second-round technical review, deliberately stringent  
**Recommendation:** **Reject. The branch labeled R2 is not yet a revised manuscript, and the central mathematical objections remain present verbatim in the submitted paper.**

---

## 1. Executive assessment

I read the current manuscript, the prior referee report, the current R2 protocol, and the surrounding revision branches. The most important fact is procedural but scientifically decisive: **the paper itself has not changed.** The `main.tex`, `main.pdf`, and submission-checklist blobs are byte-identical on `main`, `revision/ndu-mathematical-reconstruction-2026-09-20`, `revision/ndu-operations-research-r1-20260920`, and `revision/ndu-or-r2-20260920`. The R2 branch adds a predeclared `revisions/or-r2-20260920/protocol.json`; it does not contain a revised manuscript implementing that protocol.

This matters because the previous report identified defects in the paper's main theorem, model-class comparison, physical-performance interpretation, and HJB certification. Those defects are still present in the same theorem statements and proofs. A protocol promising to run a corrected model is useful research planning, but it is not a revision and cannot be evaluated as if the promised results existed.

The R2 protocol is substantially better conceived than the current manuscript in several respects. It predeclares an external contract/premium interpretation for the service-pressure variable, exact rational dynamic programming, an explicit expanded-action MDP comparator, a physical-cost oracle, fair action/evaluation accounting, naturally generated conditioning noise, a boundary-complete manufactured PDE problem, and regression tests for several known counterexamples. Those are constructive responses to the prior report.

However, the protocol also clarifies why the manuscript requires a conceptual rewrite rather than another layer of audits. In the protocol, the joint contract control and an ordinary expanded-action MDP enumerate the same ((S,	heta)) pairs and are expected to coincide exactly. That is the correct representation. It means the defensible contribution is a structured **endogenous-contract / endogenous-valuation stochastic-control model relative to a frozen-(	heta) action-only face**, not a new control formalism beyond standard MDP/stochastic-control representation.

At present, I do not regard R2 as reviewable as a scientific revision. It is a pre-registration of work that still needs to be performed and then written into the paper.

---

## 2. Revision-integrity audit: there is no revised paper in R2

The R2 branch tip `fd37a524...` adds only:

- `revisions/or-r2-20260920/protocol.json`.

The manuscript artifacts on R2 are unchanged from the previously reviewed version:

- `main.tex`: blob `2569eee2...`;
- `main.pdf`: blob `3ed6d344...`;
- `NDU_OR_submission_checklist.md`: blob `432c303c...`.

The same manuscript/PDF/checklist blobs appear on every current revision branch.

This should be stated plainly to the editor: **the authors have submitted a revision plan, not a revision.** The manuscript cannot receive credit for results that are only predeclared in a protocol.

The correct second-round standard is therefore not “does the new protocol sound promising?” It is “were the mathematical and empirical defects in the reviewed paper corrected?” The answer is no.

---

# Major comments

## 3. Fatal: the inventory service-pressure monotonicity theorem still has the wrong sign

The manuscript still states, in Eq. `inventory_service_pressure_objective`, a one-period reward containing

[
-p(	heta),mathbb E[(B+D_z-S)^+]-lambda(	heta-	heta^-)^2,
qquad p'(	heta)>0,
]

and Theorem `thm:inventory_service_pressure_structure` still claims that the maximizing selector (	heta_t^*) is nondecreasing in backlog and demand stress.

The proof still says:

> the one-step objective has increasing differences between (	heta) and the shortage/backlog stress variables because (p(	heta)) multiplies expected unmet demand.

That is the wrong sign. It is **minus** (p(	heta)) times expected unmet demand.

Let

[
H(B,z,S)=mathbb E[(B+D_z-S)^+]>0
]

and take the admissible specialization (p(	heta)=	heta) with continuation value independent of (	heta). Then the (	heta)-dependent objective is

[
-	heta H(B,z,S)-lambda(	heta-	heta^-)^2.
]

For an interior optimum,

[
	heta^*
=
	heta^- - rac{H(B,z,S)}{2lambda}.
]

As shortage stress rises, (	heta^*) falls. Equivalently, the cross effect between (	heta) and the shortage quantity is negative, not positive.

This is not a missing technical condition. It reverses the central comparative static in the simplest specialization of the stated model. The theorem and its proof remain false as written.

### What R2 changes, and why that is not yet a fix

The R2 protocol changes the economics. It introduces an external premium and an external contract liability:

[
q_z	heta
-
1.2,	heta H
-
1.5	heta^2
-
0.6(	heta-	heta^-)^2,
qquad q_z=0.6+1.4z.
]

For fixed (S), an interior selector satisfies

[
	heta^*
=
rac{q_z-1.2H+1.2	heta^-}{4.2}.
]

This is economically more defensible because (	heta) now has an external transfer/contract interpretation rather than merely allowing the decision maker to choose the coefficient that grades its own shortage.

But even in this corrected protocol, monotonicity in stress is **not automatic**. The premium increase (q_z) must dominate the increase in expected shortage liability, including the endogenous response of (S). A general theorem requires explicit increasing-differences conditions for the **new contract objective**, not the old internal-penalty objective.

The R2 protocol says it will verify all-state monotonicity numerically. That would be a useful finite-model fact, but it would not repair the theorem currently printed in the manuscript.

---

## 4. The entropic risk-sensitive “non-equivalence” proof remains invalid

Corollary `thm:non_equivalence_models` still claims non-equivalence to fixed-parameter entropic risk-sensitive control. Its proof still argues that the entropic continuation operator is smooth/strictly curved whereas a valuation-control support function is piecewise affine and nonsmooth.

There are two problems.

First, for (ho>0),

[
rac1holog mathbb E_P[e^{ho V}]
=
sup_{Qll P}
left{
mathbb E_Q[V]
-rac1ho D_{mathrm{KL}}(Q|P)
ight}.
]

Thus the entropic operator itself has a standard variational representation as a supremum of affine functionals of (V), with a convex penalty on the distorted kernel. The manuscript's “smooth curved versus supremum-of-affine” argument does not establish a structural separation.

Second, the paper does not assume that the NDU valuation set is finite in this corollary. A supremum over a compact **continuous** family of affine functionals need not be piecewise affine; it can be smooth. The proof's geometric contrast is therefore not valid for the model class actually stated.

A restricted non-equivalence statement may still be possible, for example under a precisely fixed evaluator, physical action set, transition family, and forbidden kernel distortion. But the present proof does not establish the claim.

The R2 protocol explicitly lists a “Gibbs variational identity” regression. That is encouraging because it acknowledges exactly the missing comparison. But again, the manuscript has not been rewritten.

---

## 5. R2 itself confirms that NDU is representable as an ordinary expanded-action MDP

The R2 protocol defines both:

- `joint_contract`: enumerate every ((S,	heta));
- `expanded_action_mdp`: ordinary MDP with action ((S,	heta)), same primitives.

The intended check is exact coincidence.

That is the right benchmark, and it should materially change the paper's framing.

The substantive distinction is:

- fixed-preference/action-only control restricts (	heta) to a face of the joint action set;
- NDU allows (	heta) to be controlled jointly with the physical action.

That can be a meaningful modeling contribution. But it is not a representational generalization beyond standard Markov decision processes or stochastic control. It is an **enlarged structured control class**.

The current title and several “non-collapse” passages invite a stronger reading than the protocol can support. The paper should say explicitly, near the beginning and without qualification buried later, that NDU is representable as standard stochastic control on an enlarged state/action space. The novelty, if any, must lie in:

1. the economics/operations interpretation of the added control;
2. structural results generated by that interpretation;
3. computational consequences of the structure;
4. empirically relevant performance relative to strong restricted-policy comparators.

The fact that an expanded-action MDP exactly reproduces the model is not a nuisance to be hidden; it is the correct mathematical baseline.

---

## 6. The “stable theta-free physical-cost improvement” theorem is a calibration lemma, not a theorem about endogenous NDU optimality

Theorem `thm:stable_physical_cost_improvement` assumes regime-specific physical shortage costs (p_z), then allows the NDU service-pressure rule to choose (	heta_z) satisfying

[
p(	heta_z)=p_z.
]

Once that equality is imposed, the NDU row is given the regime-correct newsvendor critical fractile, while the fixed-pressure comparator is forced to use one common (ar p). Strong convexity of the newsvendor objective then gives a quadratic loss for the misspecified fixed parameter.

The inequality is mathematically reasonable under its stated density conditions. The issue is interpretation.

The theorem does **not** derive (p(	heta_z)=p_z) from the NDU optimization problem. It selects the (	heta_z) that reproduces the regime-specific physical coefficient. A same-information physical-cost oracle can simply choose the regime-specific (S_z^*) directly, without introducing any endogenous valuation variable.

The manuscript now admits that it does not claim dominance over such an oracle. That qualification is appropriate, but it also removes much of the theorem's force as evidence that endogenous valuation control improves operations.

The R2 protocol wisely adds a `physical_oracle`. That comparator should be central. On theta-free physical cost, the physical oracle is the relevant upper benchmark: NDU cannot beat the minimum of the same physical objective under the same information and feasible physical actions. Any positive NDU physical-cost result therefore needs to be interpreted as an advantage over a **restricted fixed-pressure policy class**, not as an inherent operational advantage of endogenous valuation control.

I would relabel this theorem as a calibration/misspecification result unless the revised paper actually derives the correct (	heta_z) from the joint contract objective.

---

## 7. The new contract semantics are more credible, but they define a materially different model

The current manuscript repeatedly interprets (	heta) as an internal valuation/service-pressure parameter. The R2 protocol instead gives (	heta) external contractual consequences:

- external premium;
- incremental shortage liability;
- maintenance cost;
- adjustment cost.

That change is not cosmetic. It repairs the reward-hacking interpretation by making (	heta) an economically real contract/control variable. But once this is done, the paper is no longer proving properties of the same model currently written in Section `Endogenous Service-Pressure Structure in Inventory`.

The revised manuscript must choose one semantics and use it consistently across:

- theorem statements;
- dynamic program;
- exact DP;
- simulator;
- comparator definitions;
- physical-cost decomposition;
- interpretation of (	heta);
- HJB/FBSDE formulation.

If the authors adopt the contract model, I would regard that as the correct direction. But they must rederive the structural results from that model rather than retain the old theorem and append a new experiment.

---

## 8. The HJB certificate theorem still does not state a complete boundary-value problem

Theorem `thm:nbo_hjb_solver_certificate` works on a compact parabolic domain (D=[0,T]	imes K) and specifies:

- an interior HJB residual;
- a terminal residual on ({T}	imes K);
- a greedy-action gap.

It does not state boundary data on ([0,T)	imespartial K), nor does it specify that the problem is a state-constraint or reflected problem.

The proof later says that if the compact problem is not state-constrained/reflected, then a nonterminal boundary residual must be included “as part of (delta_H).” But (delta_H) was defined in the theorem as the interior optimal-Hamiltonian residual. A boundary mismatch is not the same mathematical object as an interior PDE residual.

This is still an under-specified theorem. “Suppose comparison holds” does not eliminate the need to say **for what boundary-value problem** comparison holds and what residuals are being controlled.

The R2 protocol's boundary-complete manufactured diffusion is a good test instance. It should be used to rewrite the theorem with an explicit parabolic boundary term, e.g. a separate (delta_{partial D}), and with the exact state-constraint/reflection/Dirichlet semantics stated.

---

## 9. The cover-refinement corollary still asserts a quantitative rate without a scheme-specific error theorem

Corollary `cor:cover_refinement_hjb_certificate` states a bound of the form

[
V^*-V^{A_{h,ho}}
le
C_D{delta_T+T(delta_B+delta_A+eta_h+L_Aho)}.
]

The proof says monotone/stable/consistent interpolation transfers the discrete Bellman operator to the continuous HJB with error (eta_h), then invokes comparison.

This remains too generic for the displayed finite-error estimate. An exact finite-cover Bellman solve certifies the finite discrete problem. Lifting it to a continuous HJB with a quantitative error requires a precisely defined scheme, an actual consistency/truncation estimate, interpolation control, and enough regularity to justify the claimed rate.

Monotonicity, stability, and consistency are convergence ingredients. They do not by themselves generate the specific linear error bound written here.

The R2 protocol proposes continuous-contract action-quantization bounds on nested grids. That is exactly the kind of **scheme-specific** argument the paper needs. But the current generic corollary should not survive unchanged.

---

## 10. The manufactured PDE certificate will not certify the economically relevant inventory solver

The R2 protocol proposes a boundary-complete manufactured controlled diffusion with known quadratic value function and perturbed critics. This is a useful unit test of the certificate machinery.

It is not, however:

- the inventory model;
- a trained neural result;
- evidence that the neural inventory critic satisfies the theorem;
- evidence that the direct-(P) solver closes the HJB gaps on the economically relevant instance.

The protocol appropriately says so. The manuscript should preserve that separation.

A manufactured-solution test can establish that the residual/certificate code behaves correctly on a controlled example. It cannot convert the large sampled neural inventory rows into proof-certified HJB solves.

---

## 11. The direct-(P) result should be narrowed to a conditioning statement

The algebra

[
Z_u=sqrt{2arepsilon},P_u
]

implies that inverting (Z_u) to recover (P_u) amplifies an **equal absolute (Z)-error** by (1/sqrt{2arepsilon}), and squared error by (1/(2arepsilon)). That is a valid conditioning observation.

It is not a general lower bound against all (Z)-based algorithms.

The R2 conditioning protocol is actually more scientifically useful than the current strong rhetoric. It proposes to fit equivalent quadratic value parameterizations to the **same stochastic-return samples**, with no injected independent (Z)-target noise. Under exact least squares and exact reparameterization, one should expect the two parameterizations to agree up to numerical conditioning/finite precision unless regularization or optimization breaks the invariance.

That experiment can falsify an overbroad “direct-(P) is intrinsically superior” claim. Good. The revised paper should embrace the falsifiable interpretation:

- direct-(P) avoids an ill-conditioned inversion map near degenerate diffusion;
- whether that matters statistically or computationally depends on how approximation/training error enters the learned representation.

That is a useful result. Calling it a general solver superiority theorem would not be justified.

---

## 12. The empirical comparison still has not been rerun under the predeclared fair protocol

The current manuscript contains a large and complicated evidence stack, including mixed physical results, selected configurations, exact DPs for related models, sampled neural residual audits, and numerous guard tables.

The R2 protocol proposes something much cleaner:

- exact rational finite-horizon DP;
- same state information;
- unrestricted stock tables;
- explicit distinction between unique economic actions and Bellman evaluations;
- frozen-contract comparator;
- capacity-matched dummy gate;
- expanded-action MDP equivalence check;
- physical-cost oracle;
- full ledger decomposition;
- all predeclared methods reported.

That is the correct direction.

But those R2 results do not yet exist on the R2 branch. Until they are executed and written into the manuscript, the old empirical objections remain unresolved.

In particular, the revised paper needs one canonical table that reports, for every comparator under the same model:

1. exact value under the contractual objective;
2. theta-free physical cost;
3. premium;
4. contract liability;
5. maintenance/adjustment;
6. fill/lost demand;
7. action-space size;
8. actual Bellman evaluations;
9. whether the method is an exact optimizer or a heuristic.

The paper should not ask a referee to reconstruct the main comparison from dozens of audit CSVs.

---

## 13. “Pass” guards and artifact propositions still overwhelm the scientific argument

The manuscript still contains a large number of theorem/proposition/corollary environments whose content is essentially:

- a script checks rows;
- a threshold is satisfied;
- an audit is therefore labeled “pass.”

Examples include objection-closure, six-pillar support, bounded-architecture budget, stress-margin, cross-artifact consistency, concordance, leave-one-out guard, and synthesis propositions.

These may be useful repository QA. They are not mathematical theory.

For *Operations Research*, the paper should sharply separate:

- mathematical theorems;
- numerical error certificates;
- empirical results;
- software reproducibility checks;
- manuscript bookkeeping.

The current document is still far too long and self-referential. A referee should not have to read a theorem that says an internal “referee objection closure” table passes. That language is especially inappropriate in a blind journal manuscript because it makes the paper read like a response dossier rather than a scientific article.

Keep the audit machinery in the repository. Remove most of it from theorem environments and compress it into a reproducibility appendix/table.

---

## 14. The OR contribution is still obscured by three papers being combined into one

The current manuscript is simultaneously trying to be:

1. a general stochastic-control/FBSDE theory paper;
2. an inventory/service-contract structural paper;
3. a neural HJB solver/certification paper.

The result is more than 2,500 lines of TeX, an extremely long PDF, a large number of theorem-like environments, several model semantics for (	heta), multiple benchmark families, and a large internal certificate vocabulary.

The strongest plausible *Operations Research* paper is much narrower:

- define one operational meaning of (	heta), preferably the external contract interpretation in R2;
- formulate one canonical stochastic/dynamic inventory model;
- derive one or two correct structural theorems;
- show the exact expanded-action representation and frozen-face relationship;
- prove one scheme-specific approximation result if needed;
- run one predeclared exact/fair comparison and one credible data illustration;
- relegate generic neural solver material to a secondary section or separate paper unless it is essential to solving the model.

The current manuscript's breadth is not a substitute for a clean primary contribution.

---

# 15. Status of the previous major objections

| Prior objection | Current manuscript | R2 protocol | Second-round status |
|---|---|---|---|
| Inventory monotonicity sign error | Same theorem and same incorrect proof remain | Changes to external contract economics; plans all-state monotonicity check | **Open / fatal** |
| Entropic risk-sensitive non-equivalence | Same corollary/proof remain | Gibbs variational identity listed as regression | **Open / fatal to current taxonomy claim** |
| Theory/experiment (	heta)-semantics mismatch | Current paper still mixes internal valuation, policy gate, service pressure, contract language | Gives one explicit external contract model | **Promising plan, not implemented** |
| Fair comparator / search budget | Current evidence stack unchanged | Exact DP and fair accounting predeclared | **Open until executed** |
| Theta-free cost accounting | Existing paper unchanged | Full ledger decomposition predeclared | **Open until new results replace old tables** |
| HJB nonterminal boundary | Theorem statement still omits explicit spatial-boundary residual/data | Boundary-complete manufactured PDE planned | **Open** |
| Generic cover-refinement error rate | Same corollary remains | Nested quantization study planned | **Open** |
| Neural solver certificate gap | Same sampled guard architecture remains | Manufactured PDE explicitly separate from neural/inventory | **Open; should be downscoped** |
| Excessive audit propositions | Unchanged | No manuscript cleanup yet | **Open** |
| Standard expanded-action representation | Paper still frames strong non-collapse claims | R2 explicitly includes equivalent expanded-action MDP | **Requires reframing of novelty/title** |

---

## 16. What would constitute an actual reviewable R3

I would not recommend another referee round until the repository contains a genuinely new manuscript blob. At minimum, an R3 should satisfy all of the following.

### A. Replace the old inventory model, theorem, and proof

If the external contract model is the intended model, write it into the paper and remove the old internal-penalty theorem. Derive monotonicity from the new objective with correct sufficient conditions. Include explicit counterexamples showing failure when the premium/liability comparative-statics condition is violated.

### B. Rewrite the novelty claim around the expanded-action baseline

State plainly that the model is an ordinary stochastic-control/MDP problem with joint action ((a,	heta)). Define “generalization of fixed-preference RL” only as nesting of a frozen-(	heta) face. Remove language implying that standard expanded-action MDP representation is impossible.

### C. Delete or repair the entropic non-equivalence corollary

Any remaining comparison to risk-sensitive control must account for the variational representation of the entropic operator and must specify exactly what transformations/evaluators/kernel controls are forbidden.

### D. Execute the R2 protocol without post hoc changes

Commit:

- exact DP outputs;
- source code;
- all comparator rows;
- seed/batch outputs;
- complete ledger;
- monotonicity checks;
- action quantization sequence;
- conditioning study;
- manufactured PDE certificate.

If parameters are changed after seeing results, version the protocol and treat the new run as exploratory rather than confirmatory.

### E. Make the physical oracle central

Report NDU versus:

- frozen-contract optimal stock policy;
- expanded-action MDP;
- physical-cost oracle.

Do not use “physical improvement” language without naming the restricted comparator.

### F. State a complete HJB boundary-value theorem

Specify the parabolic boundary conditions and include boundary residuals explicitly. Replace the generic cover-refinement rate by a scheme-specific theorem or weaken it to a convergence statement.

### G. Separate theorem, evidence, and software QA

Theorems should contain mathematics. Numerical certificates should contain error bounds. Empirical tables should contain outcomes. Repository scripts should test reproducibility. Remove “referee closure” and most software-audit propositions from the scientific theorem stack.

### H. Cut the paper aggressively

A clean OR article should be readable without navigating a certificate ontology. The current 90-plus-page architecture is a serious editorial risk even if every technical issue were eventually repaired.

---

## 17. Positive aspects of the R2 protocol

Although my recommendation is negative, I want to record that the R2 protocol moves in several correct directions:

- it predeclares the model before execution;
- it gives (	heta) external contract semantics rather than letting the decision maker freely manipulate its own penalty coefficient;
- it includes exact dynamic programming rather than relying on optimizer heuristics;
- it explicitly includes an expanded-action MDP equivalence benchmark;
- it includes a physical oracle;
- it distinguishes unique actions from duplicate evaluation slots;
- it avoids injecting artificial (Z)-target noise in the conditioning experiment;
- it proposes boundary-complete PDE verification;
- it records negative/counterexample regressions rather than only positive claims.

If these design choices are actually executed and used to rebuild the manuscript, they could produce a much more credible paper. They are not, however, results yet.

---

# 18. Confidential recommendation to the editor

**Recommendation: Reject.**

The reason is not merely that I disagree with the framing. The branch submitted as R2 does not contain a revised manuscript. The `main.tex` and `main.pdf` are unchanged from the previously reviewed version, and the main mathematical defects therefore remain verbatim.

Most importantly:

1. the core inventory monotonicity theorem still has a direct sign counterexample;
2. the entropic risk-sensitive non-equivalence proof is still invalid;
3. the HJB compact-domain theorem still omits a complete boundary specification from its statement;
4. the cover-refinement result still asserts a quantitative bound without a sufficiently specified scheme/error theorem;
5. the physical-cost theorem still calibrates (	heta) to the desired regime coefficient rather than deriving it from endogenous optimization;
6. the paper's strongest novelty language is undermined by the R2 protocol's correct admission that an ordinary expanded-action MDP exactly represents the joint ((S,	heta)) control;
7. the promised fair exact comparisons and corrected model are predeclared but not executed.

The authors have a potentially useful direction: an externally meaningful adaptive service contract, embedded in standard stochastic control, with structural inventory results and exact dynamic programming. That paper does not yet exist in the submitted manuscript.

A future submission should be reviewed as a substantially reconstructed new manuscript, not as an incremental response layered onto the current 90-plus-page certificate/audit architecture.
