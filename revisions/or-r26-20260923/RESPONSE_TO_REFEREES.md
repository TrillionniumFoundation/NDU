# Response to the two R24 Operations Research reports — R26

**Manuscript:** *Accepted Service Adaptation: Continuation Prices, Transfer Coordinates, and Certified Gains*  
**Scientific predecessor:** R25, `7f3f12c9d412b45a570725dc9b61203d64da5e41`.  
**Reports answered:** ordinary R24 report at `9080e29443191f9bb415ab0a213af446d4ce3be3`; independent R24 report at `ded3e34349631cd6dc7a4aa35d58a9d248c77d47`. Both reports examine the R24 scientific manuscript at `63bbb843e1bbe7cac2170dc7d317d4cf18bb2bb8`.  
**New delivery branch:** `revision/ndu-operations-research-r26-20260923`.

We thank both referees for distinguishing algebraic correctness, economic content, implementability, and computational evidence. We have not treated the independent report's recommendation as a reason to abandon the accepted-control question. We have used its specific requirements to strengthen the optimizer-level argument and the continuous-state implementation theorem. This response distinguishes improvements already present in R25 from the new R26 work; it does not claim that the independent report reviewed R25 or that an unchanged R25 result was newly derived here.

The main theorem chain now answers two questions. First, what gain follows from releasing restrictions on an already optimized contract, and which continuation bottleneck stops that gain? Second, when the public stochastic model admits an augmented Markov state, can an actual continuous-tier policy and its error certificate be represented without enumerating public histories? R25 established the optimized restriction-release frontier, comparator-adjusted rents, and exact state sufficiency. R26 adds a promise-preserving continuous-state envelope theorem, a certified information-omission bound, and examples that separately demonstrate why the promise and inherited tier belong in the state. No predecessor theorem, proof, empirical table, or unfavorable implementation result has been removed from the repository.

## 1. Review object and retained improvements

**Independent Sections 1–2; ordinary Sections 1–2.**

The new root `main.tex`/`main.pdf` and `electronic_companion.tex`/`.pdf` are the review objects. The source/PDF pairs, bibliography, reading guide, and checklist of R25 are preserved byte for byte under `predecessor/`, with their SHA-256 manifest. The complete R24 package remains in the R25 predecessor archive and at its existing revision paths. Both reports are retained in `reviews/`, including the independent report that was absent from the R25 tree.

We retain the revised title, optimized comparison, slack-aware transfer example, adverse timing evidence, and designed-versus-calibrated uncertainty distinction that the reports credit. The scientific argument does not use preservation counts as evidence of novelty.

## 2. From a coordinate identity to optimized contract value

**Independent Sections 3, 16, and 17.1; ordinary Sections 3–4 and requirement 1.**

The transfer representation remains a lemma in the theorem chain, not its endpoint. Main Theorem 4.1 (`thm:release`), already established in R25 and retained with its proof, gives the optimized restriction-release frontier. The exact first regular segment is determined by restricted-class prices, reduced curvature, and the first primal, price, or switching event. The subtree continuation-slack ratio determines a genuine policy-path breakpoint. The three-node example has two nontrivial policy segments and reaches the expanded optimum at release 3/8; it is not an objective identity obtained by relabeling a feasible vector.

Main Theorem 5.1 and Proposition 5.2 retain the comparator-adjusted capacity and friction results. They reoptimize the restricted contract, instead of transporting a constant-comparator critical-friction claim to a different benchmark. Their exact examples show that the premium can decrease as a continuation cap relaxes, and can increase with switching friction when the restriction forces switching. These results answer the ordinary report's request for optimizer-level consequences.

R26 goes beyond the previous formal promise-state induction. Main Theorem 6.2 (`thm:r26-envelopes`) gives an executable continuous-state lower policy, a globally valid recursively generated upper bound, and an explicit uniform error certificate. Its price plane has a closed-form scalar quadratic conjugate and capped-child-payment support terms. These quantities can be checked without a tree optimizer or an assumption that numerical dual labels are exact. The main proof includes feasibility, concavity, implementation, weak duality, and the full-domain certificate; EC.10 gives construction details and residual propagation.

This is the strengthened substantive answer to the independent report's central question: an optimized expansion need not remain an abstract history-tree value or an unverified promise-grid policy. Under the stated public Markov and convex-tier assumptions, it has a deterministic accepted implementation and a computable error bracket on the entire continuous promised-payment domain.

## 3. Optimized restrictions and the economic source of value

**Independent Sections 4 and 17.2; ordinary Section 5 and requirement 2.**

The five-class common-instance hierarchy introduced in R25 is retained: fixed, time-only, date–regime, two-period-memory, and full-history contracts. Every class is optimized on the same accepted set. The legacy amendment family is kept distinct from the actual-tier Markov family. Time-only is an operationally specified decision technology, not a universal incumbent chosen because it generates a convenient positive gain. The hierarchy is not a unique causal or Shapley decomposition.

New Proposition 6.3 (`prop:r26-dispersion`) supplies a quantitative test. The full-versus-pooled premium is at least half the squared curvature-weighted distance of the full optimizer from the pooling subspace. With an inexact feasible full decision, a certified full-class upper bound supplies the explicit square-root error correction. Thus variation in an inaccurate optimizer is not automatically declared valuable information.

The new exact promise example is deliberately constructed so that, under the unique full optimizer, two terminal histories have **both the same public regime and the same inherited tier**, but different remaining promises. Their values are −25/32 in the full class and −27/32 in the optimized date–regime class. The gain is 1/16 and the curvature lower bound is 1/32. This avoids confounding the promise distinction with an inherited-tier distinction. Conversely, a second pair of continuation problems has the same public regime and remaining promise but different inherited tiers; its omission cost is also exactly 1/16. EC.10.3 derives both optimizers and all values.

These examples are not advertised as a general exact formula for every information premium. They demonstrate why a regime-only Markov rule is not the augmented-state policy guaranteed by Theorem 6.1 and identify observable, contractual sources of the lost value.

## 4. One primary participation institution

**Independent Sections 5, 13, and 17.3; ordinary Sections 6 and 14.**

The primary model in main Section 3 is customer exit **before implementation at every review**. It derives each continuation row directly from stage customer utility and the outside continuation. Fixed root payment is a separate commitment; it is not inferred from a participation inequality. Ex ante participation is the special case retaining only the root row.

We retain the historical master-agreement derivation in the archive rather than alter its institution retroactively. The current formal companion begins with the continued-participation reduction. R26 adds explicit operational examples—verifiable service-level agreements and maintenance subscriptions with periodic cancellation rights—and states that termination is not an optimized action in the modeled retention contract. The public tariff is fixed; no hidden effort or private report is assumed away inside a theorem that actually requires it.

## 5. Stochastic-model content and horizon complexity

**Independent Sections 6, 12, 17.4, and 17.8; ordinary Section 13.**

The current Stochastic Models positioning rests on the augmented-state theorem and its continuous-state implementation, alongside the optimized contractual value results. We do not equate linear work on a finite tree with linear work in primitive horizon.

Theorem 6.1 identifies sufficient state `(date, public regime, inherited tier, exact remaining payment)` under Markov outside caps, rewards, and feasible actions. Theorem 6.2 then computes the exact feasible promise interval recursively, mixes deterministic actions and child promises without rounding those promises to a grid point, and propagates dual upper planes. Every positive-probability child retains its participation cap. Boundary promises require neither Slater slack nor a differentiable value function.

For bounded numbers of retained anchors and planes, the witness representation is indexed by date and regime, not all histories. We explicitly charge dense child-mixture storage, the policy query's mixture linear program, numerical proposal solves, and rational arithmetic. We do not claim a general polynomial accuracy–horizon bound, a uniform grid convergence rate, or applicability to hidden nonadditive resources. Indivisible service tiers are an explicit counterexample to deterministic interpolation.

The new six-case continuous-state study checks 4,414 lower-anchor witnesses and 1,123 price planes. The four-period whole-domain bound decreases from 0.113253 to 0.019567 when mesh subdivisions increase from 4 to 16. The sixteen-period design uses 800 anchors with a 0.193576 bound; its hypothetical full binary tree has 65,535 nodes and is not materialized. These are certified approximation and representation results, not a timing superiority claim. The older finite-action enumeration remains unchanged and is not repurposed as a continuous-state proof.

## 6. Learned implementations and amortization

**Independent Sections 7–8, 17.5, and 18.1/18.7/18.10; ordinary Sections 8–9.**

The historical strict-target table and complete R24 phase-resolved records remain unchanged. At 63, 127, and 255 nodes, both learned routes fall back in every strict-target case and are slower than lifted continuation. The coarse target likewise supplies no finite observed learned amortization case. The new state-envelope study does not refit a neural architecture or relabel these outcomes as favorable.

R25 corrected the actual sign error, and R26 preserves that equation (`eq:amortization`): candidate-minus-lifted cost is `C_off + Q(t_C−t_L) = C_off−Q delta`; a positive-cost candidate crosses only if `t_C<t_L`. The original erroneous prose remains identifiable in the archived R24 source, while its already-correct analysis code and all original measurements are preserved. An archive copy is not the current formula.

The earlier frozen-policy validation remains a result for fixed policies under a known synthetic model, not an inferred general learning theorem. No economic class-expansion result is made contingent on an unobserved learned speed advantage.

## 7. Robust comparator geometry and quality–cost accounting

**Independent Sections 9–11, 17.6–17.7, and 18.8; ordinary Sections 10–12.**

R25's local outer-comparator bound and fine-radius experiment are retained as main Proposition 7.2 and Section 8.3. Their conclusion is an explicit linear-in-radius upper bound under a uniform strict anchor, not a claim that four old radii proved a discontinuity. The finer sweep fixes contexts and coefficient directions while reducing the radius. Designed uncertainty is not called calibrated field uncertainty.

The unmatched robust timing comparison is not a speed claim. Its complete gain–cost coordinates remain in the predecessor computational record; the stronger classical robust certificate and weaker learned certificates are not compared as equal quality. We do not invent a new common-target frontier that has not been measured. The new Markov envelope experiment concerns a different, explicitly stated problem and cannot retroactively improve those historical timings.

For economic certification, main Proposition 7.1 retains the reusable restricted-value envelope when geometry is fixed and only reward queries vary. It includes anchor optimization error, charges initial anchors, and identifies offline validation separately from online query arithmetic. Geometry changes require a new valid bound. Accepted-policy implementation is not said to require a new optimized-comparator solve at every decision. These changes directly target the comparator bottleneck the reports identified rather than shave uncharged prediction time.

## 8. Dynamic-contract literature and continuation prices

**Independent Section 14 and 18.4; ordinary Section 7.**

R25 had already added Chen, Sun, and Xiao (2020) and Liang, Sun, Tang, and Zhang (2023). R26 adds the independent report's three specific journal-local comparisons: Tian, Sun, and Duenyas (2021), Liu, Lewis, Song, and Kuribko (2019), and He (2023). The discussion contrasts public versus private information, fixed tariff versus designed transfers, termination versus continued participation, and operating switching costs versus incentive provision. Publication years, volumes, pages, and DOIs were verified against the publishers' records. He's full title includes “Technical Note.”

A continuation **price** is a dual multiplier on an accepted continuation constraint. A remaining-payment **promise** is a primal state. Both are defined near their first relevant use; the new recursive plane makes their distinct roles explicit.

We also cite Pereira and Pinto (1991) when discussing supporting cuts and piecewise-linear continuation approximations. We do not claim concave interpolation, weak duality, strong-concavity distance bounds, or stochastic dual approximation as newly invented general mathematics. The contribution is the contract-specific theorem chain: optimized restriction release and rents, exact continued participation in the public stochastic state, and a feasible continuous-policy error certificate.

## 9. Formal architecture, preservation, and presentation

**Independent Sections 15, 17, 18, and 19; ordinary Sections 15–18.**

The title is unchanged. The current main paper remains within the Regular manuscript length limit even counting its title page, references, and end tables; the formal companion is shorter than the main paper. The main proof of the continuous-state theorem is in the manuscript, with implementation, residual, and experimental details in the EC. The abstract is text-only and below 200 words. The introduction is equation-free. Anonymous 11-point text, one-inch margins, one-and-a-half spacing, author–year citations, and tables after references are retained and checked against the journal's current guidelines.

The new theorem is integrated into the existing recursion section instead of creating another independent neural, robustness, or timing paper inside the submission. The full R25 mathematical statement/proof blocks remain verbatim; R24 and older results remain at their existing archive paths. Preservation therefore supports author review without forcing the journal-facing paper to reproduce every earlier implementation stage.

Exact rational witnesses and numerical optimizer proposals are consistently distinguished. The independent verifier recomputes the scalar conjugates and interval supports, which proves the claimed finite-model continuum brackets by the stated induction. Its pass counts are reproducibility information, not a substitute for theorem novelty or an assertion of journal acceptance.

## 10. Action crosswalk for the independent report's Section 17

| Request | Current response location |
|---|---|
| 17.1 Deeper optimized-comparator theorem | Main 4–5; retained release/rent results; new Theorem 6.2 and Proposition 6.3 |
| 17.2 Institution-based comparator hierarchy | Main 3 and 5.3; retained common-instance hierarchy; new omitted-state examples |
| 17.3 Unify participation | Main 3.1 and EC.1; ex ante-only model explicitly distinguished |
| 17.4 Address horizon complexity | Main 6, especially 6.1; EC.10.1–2; new continuous-state certificates |
| 17.5 Learning as evidence, not identity | Main historical timing subsection and unchanged computational archive |
| 17.6 Explain/fix robust comparator | Retained Proposition 7.2, fine-radius evidence, explicit assumptions |
| 17.7 Online versus offline certification | Retained Proposition 7.1; explicit cache costs and query boundary |
| 17.8 Literature and area | Main 2; new journal-local references; stochastic state and certification results |

The response is intended for another substantive referee examination. The scientific argument is stronger than a transfer-coordinate identity and now has a continuous accepted implementation with explicit error control. The scope conditions and retained negative results are part of that argument, not reasons to stop the investigation. Editorial judgments about significance remain for the referees and editor.
