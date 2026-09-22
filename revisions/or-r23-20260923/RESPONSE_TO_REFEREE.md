# Response to the September 23 Operations Research referee report

**Revision R23 — September 23, 2026**  
**Branch:** `revision/ndu-operations-research-r23-20260923`  
**Paper:** *Accepted Service Adaptation with Neural Differential Utility: Continuation Prices and Robust Certified Gains*

The report addressed is `reviews/operation_research_referee_report_r20_2026-09-23.md`, review commit `18381729edf8d15a536ebef16abf6660ee0db48f`. It reviewed the plan-only R20 tip `45553b28f40c92a14895b8b82d8739e608f6d4b1`, whose complete manuscript was R19. R23 builds on the complete R22 publication `fef3bad92ab9c74530b530a885bb6f437e8b1c1a`, not on the old plan. There is no claim that a new referee has already reviewed R22 or R23.

We thank the referee for distinguishing the validity of the mathematical bridge from the need for a sharper operational contribution and stronger evidence. The revised paper follows one decision problem: **certify the economic gain from expanding an already optimized accepted service-policy class**. Continuation geometry, resource-statistic learning, implementation, and verification remain parts of this same problem. Neural Differential Utility, the global bridge, continuous-time and friction derivations, direct-price alternatives, and unfavorable numerical results are all retained.

R22 supplied the complete dual-repair theorem, full-polyhedron scaling, a lifted classical continuation baseline, optimized time-only comparators and independent deterministic validation. R23 adds a substantive further step: **joint objective and acceptance-model misspecification**. It does not rename reward-context shift as model robustness. The new theorem certifies feasibility and gain against the *true model-specific reoptimized restricted optimum*, using a common outer comparator class. An explicit counterexample shows why independently optimized vertex comparators can fail when the acceptance set changes. A new exact repair, a fully specified 96-context experiment, a strong classical robust-maximin comparator and independent rational replay accompany this theorem.

## 1. Review object, completeness and provenance

The original version diagnosis is correct: a branch name and a revision plan are not a revised paper. The R23 review objects are the ordinary complete root `main.tex`, `main.pdf`, `electronic_companion.tex` and `electronic_companion.pdf`. The new branch preserves exact R22 root artifacts in `revisions/or-r23-20260923/predecessor/`, with SHA-256 hashes. Source generation, executed raw records, generated tables, this response and a preservation map are included. The publication workflow checks the actual final commit independently and attaches `ndu-or-r23/final-sha` only to that commit.

## 2. Results already credited in R19

All credited scope is retained: the full accepted polyhedron, vector tiers, several coupled resources, heterogeneous outside protocol, root equalities, hard capacities and endogenous switching signs. The global bridge and inexact-response theorem are unchanged. The older friction, transfer, inventory, continuous-time, scalar and verified-cell derivations remain. All predecessor theorem/proof environments are checked verbatim across the current main and companion. Only the full global-bridge proof is relocated, intact, to companion `ec:r23-preserved-global-proof`; its statement and precise cross-reference remain in the main.

## 3. Neural framing and the non-neural winning methods

We retain the neural construction while making the operational target explicit. A scalar neural critic is not asserted to be necessary, and RBF interpolation is not described as neural. The original and new tables preserve stronger direct-price and classical results. The R23 experiment uses the *same frozen neural prices* to propose decisions under a robust acceptance layer, establishing a concrete protected implementation without claiming neural superiority. The classical robust-maximin program is stronger in the recorded comparisons, and is prominently reported.

Locations: title and abstract; Introduction; `thm:r19-global`; new `thm:r23-robust`; Tables `tab:r22-cost` and `tab:r23-robust`; R23 `results/summary.json`.

## 4. Derivative supervision and what is actually trained

The models remain fixed-random-feature tanh models with a ridge readout, not fully trained deep networks. The paired derivative-supervision evidence remains a supervised representation comparison using optimizer-generated labels. Direct-price learners receive the same underlying information. Original label-generation and fitting costs and eight training/deployment pairs remain, including the unfavorable comparisons. R23 performs no retraining or selection on its new contexts.

## 5. Novelty boundary of the global bridge

The main literature table continues to identify envelope sensitivity, strong-convexity stability and conjugate/Bregman algebra as established ingredients. The accepted-control consequence is a response retaining every continuation, equality, capacity and nonsmooth-switching restriction across face changes. We retain the complete proof rather than replacing it with a claim of novelty.

The later certificate results answer a different implementation question: which part of the observed gap can be removed without changing the decision? The four-component identity, the fixed-block floor and complete dual attainment identify that separation explicitly. R23 then handles a limitation of nominal transport: a changed acceptance matrix invalidates an automatic feasibility claim. The new common-outer-class theorem protects the actual economic comparator under that change. Its vertex and weak-duality ingredients are classical; the model-specific comparison and the interior-comparator counterexample are stated exactly, not advertised as a new general principle of robust optimization.

## 6. Directly relevant literature

The paper retains explicit engagement with Elmachtoub and Grigas (2022), Bertsimas and Kallus (2020), Amos and Kolter (2017), Kraul, Seizinger and Brunner (2023), and learned/classical warm starts. The theorem-level comparison table distinguishes their assumptions and implications from the present accepted-control consequences. R23 adds Ben-Tal and Nemirovski (2000) and Bertsimas and Sim (2004), with verified journal metadata and a narrow comparison to robust uncertain-data optimization. `LITERATURE_MAP.md` identifies the incremental claims; none depends on describing generic dual prediction or robust counterparts as unprecedented.

## 7. Deliberately selected value-gradient coordinates

The main statement retains the specified resource-reward perturbation. Its value derivative reveals the resource vector because that coordinate was chosen, not because an arbitrary scalar value reveals every operational price. Direct-price and value-gradient prediction remain alternative constructions. The robust experiment uses their frozen predicted nominal resource prices as proposals, and relies on the robust response and separate certificate for its guarantee; it does not assign the nominal gradient the role of a hidden true-model gradient.

## 8. Structure-aware classical alternatives

The complete R22 lifted `(x,t,u)` primal-dual continuation baseline remains, with equality `u=Ux`, diagonal quadratic structure, cached matrices and explicit adaptive-factorization caveats. Its 5,120 matched-cost pipelines include prediction, response, repair, audits, price polishing and actual fallback at identical final tolerances. R23 additionally solves an ordinary robust-maximin convex QP over the same robust accepted class and the same vertex comparator bounds. Eight outer-comparator solves are recorded as shared certification work, not hidden as free labels. R23 is not presented as a matched-runtime acceleration experiment.

## 9. Scaling of the general class

The ten R22 full-polyhedron configurations, 640 training labels and 800 deployment attempts remain, including the 1,023-node/two-service case. Service dimension, resource rank, capacities and curvature vary; the old scalar star is not substituted for this study. Setup and label costs, full fallback work and failures remain recorded. The new joint-misspecification study is on the full 63-node model and is clearly distinguished from the scaling evidence; we do not claim that four uncertainty radii constitute a new scalability result.

## 10. Economically meaningful optimized comparator

Nominal validation continues to use a reoptimized accepted time-only amendment, not an arbitrary outside protocol. Under misspecification the appropriate comparator changes with the hidden model. The new theorem explicitly targets `K_zeta = max_{x in Y_zeta} F_zeta(x)` and requires a common outer class containing the union of all these restricted classes. In the experiment, the outer class keeps the time-only and root equalities and analytically relaxes the uncertain continuation/capacity inequalities. This proves an upper bound on every true restricted optimum, not only a value from a chosen numerical incumbent or from the robust intersection of classes.

The necessity of this distinction is demonstrated exactly: two vertex acceptance sets can equal `{0}` while the interior set is `[0,1]`. Separate vertex comparator values then miss an interior optimum of one. The theorem's common outer class yields the correct uniform certificate.

## 11. Deterministic deployment and independent validation

R22's two deterministic eight-model ensembles, 2,048 IID and 512 shifted contexts per ensemble, and four simultaneous conditional expected-gain bounds remain unchanged. Their fresh-workspace correction and excluded pilot remain documented. R23 uses the same frozen models, separate seed 2302301, and 96 new contexts. Every numerical response uses a fresh workspace; no warm-start or adaptive-penalty history leaks into the declared policy mapping. The R23 results are pointwise robust certificates and descriptive paired summaries, **not** a new positive population confidence bound. A companion extension states the additional boundedness and sampling assumptions needed for such a population claim.

## 12. Joint model misspecification, not merely covariate shift

This is R23's main additional response. Reward, switching friction, continuation coefficients and capacity budgets change jointly in a declared three-dimensional uncertainty cube. The implementation observes the nominal context but not the hidden realization. Robust response and exact rational repair protect all vertex inequalities, hence every affine interior model. Upper certificates on the common outer comparator class then protect gain relative to the actual model-specific restricted optimum.

The four declared radii are 0, 6.25%, 12.5% and 25%. The 96-context study records 1,152 protected implemented policies, 3,072 vertex comparator certificates and 768 nondeployed nominal diagnostics. All are retained, with all failures and negative certificates required by the protocol to remain in the output. Every protected policy is exactly robust-feasible; every reported robust gain certificate is positive in this sample. At each positive radius, both unprotected nominal learned rules violate at least one uncertain restriction in every recorded context. Violation magnitudes are reported, not just a binary flag. Classical maximin is strongest in the new comparison.

These results extend the scientific claim to *specified coefficient misspecification*. They do not estimate the uncertainty set, learn an unknown transition law, or establish field validity. Truth-in-set is an explicit theorem assumption. This is a mathematical and executed operational extension, not an attempt to infer arbitrary-model robustness from a nominal certificate.

Locations: `sec:r23-robust`, `thm:r23-robust`, `eq:r23-gain`; companion `ec:r23-robust`; `DESIGN.json`, `robust_study.py`, `robust_exact.py`, `replay.py`, `results/summary.json`, `results/violation_magnitudes.json`.

## 13. Feasible-geometry versus objective generality

The original global quadratic price-error rate retains its strong-convexity and smooth-coupling assumptions. The existing regularization-bias charge remains explicit. The new robust implication requires continuous concave objectives affine in the uncertainty and valid vertex upper bounds; it does not require strong convexity or a strictly feasible accepted point. Its particular rational ray-repair implementation does use a strict anchor, clearly separated from the theorem. No unconstrained generality or rate is silently inherited by changing the objective class.

## 14. One coherent paper, with preserved content

The single target remains accepted expansion relative to an optimized restricted contract. The robust extension asks whether the same implementation and economic comparison survive specified coefficient error. It is therefore an extension of the same theorem chain, not a new unrelated benchmark. Every previous mathematical block and adverse observation remains. The only proof relocation is the full global bridge proof to the electronic companion. The main uses 11-point text, one-and-a-half spacing, one-inch margins, an anonymous title page, a text-only abstract below 200 words, a notation-free introduction, author-year references and tables after references. The package is prepared as a Lengthy manuscript; exact final page counts are checked automatically.

## 15. Specific technical and presentation comments

**15.1 — Two-Bregman identity.** It remains identified as conjugate/Bregman algebra with an explicit accepted-control consequence. The complete proof is retained.

**15.2 — Value versus direct-price learning.** Both routes remain. No general preference for the scalar critic is asserted, and stronger RBF/direct-price evidence is preserved.

**15.3 — Solver details.** The main retains OSQP, lifted structure, cached and warm-started timing states, factorization caveats and complete work accounting. R23's statistical mapping deliberately uses fresh workspaces for every solve. Its robust-maximin QP is written explicitly in the companion.

**15.4 — Theorem tests versus predictive robustness.** Historical geometry/quartic checks remain theorem checks. R22 evaluates frozen models under covariate shift. R23 evaluates the actual frozen predictors with simultaneous objective/constraint coefficient error and gives explicit truth-in-set guarantees. These three experiments are not conflated.

**15.5 — All-binding star cases.** Their interpretation as response/repair tests rather than predictor comparisons remains unchanged.

**15.6 — Fleet sampling target.** The older randomized-fleet theorem is preserved for its stated mixture estimand. Current nominal population claims concern frozen deterministic rules. R23's descriptive robust study is not pooled into those confidence bounds or represented as a training-randomness guarantee.

**15.7 — Break-even accounting.** Historical break-even estimates remain host/protocol-specific. New robust certification has explicit additional comparator work; it does not inherit the old speedup or break-even number.

**15.8 — Executed polishing.** R22's complete recorded price-polishing execution and replay are retained and rerun for integrity. Fixed-primal polishing, exact complete-dual convergence and R23 robust acceptance repair are distinct operations with distinct guarantees.

## 16. Scientific grounds for reconsideration

The current package supplies the requested close literature comparison, a coherent accepted-control theorem chain, strong classical alternatives, full-class scaling, optimized economic comparators and independent deterministic validation. R23 further removes a substantive limitation of nominal certification by addressing simultaneous objective/acceptance misspecification, exposing a comparator pitfall and proving a correct remedy. This positive contribution is supported by complete proofs and executed exact certificates. It does not depend on suppressing the non-neural winner or discarding the original theory.

## 17. Closing response

The new branch contains a completed revision rather than a recommendation-dependent research plan. The contribution is accepted service adaptation with implementable, auditable and now robust economic-gain guarantees under explicit assumptions. The records distinguish mathematical validity, pointwise deployment evidence, conditional statistical evidence and computational performance. We respectfully submit the complete revision and response for renewed scientific evaluation, without treating reproducibility checks as a substitute for the referee's judgment.
