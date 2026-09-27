# Response to the Operations Research R4 referee report

**Report:** `reviews/operation_research_referee_report_r4_2026-09-20.md`  
**Reviewed commit:** `a91b707883b2408de58d9392e4fc546e08a00881`  
**Revision branch:** `revision/ndu-operations-research-r4-20260920`  
**New title:** Neural Differential Utility: Endogenous Service Contracts and Certified Dynamic Optimization

We thank the referee for distinguishing a recorded plan from an executed scientific revision. This response accompanies an actual replacement manuscript, an electronic companion, complete executable calculations, and their outputs. The principal changes are proofs and results, not changes to acceptance labels. The entire reviewed source tree is preserved unchanged at `archive/pre-r4/`; the active root paper is the new revision.

## 1. Revision integrity and the unchanged R3 manuscript (report Sections 1–2 and 14)

R4 replaces the root manuscript, rather than adding another protocol or workflow around the old paper. The new main text is organized around one operating model and contains the full central proofs. The electronic companion retains supporting derivations, counterexamples, implementation details, and a historical evidence map. The original manuscript, PDF, figures, bibliography, experiments, and QA material are retained through the exact reviewed Git tree. They are not deleted or passed off as new results.

The new executor actually runs the unchanged R2 model and R3 interpretation conventions. It verifies the original protocol's SHA-256 `ef3b61559baa1b015a23ee06ade6e3fa4097273e09ca314559f68047f7809b5b`. Outputs include all five methods, exact policy/value records, full accounting, batch-level simulations, conditioning fits, and numerical refinements. The validation record does not treat CI scheduling or a manifest's label as proof of execution.

## 2. Service-pressure sign and a correct dynamic structural theorem (report Section 3)

The referee's penalty-only sign calculation is correct. The old assertion is not retained as an active theorem. Main equation (penalty counterexample) and EC.2–EC.3 preserve the counterargument rather than concealing it.

The canonical primitive is now an externally priced contract: premium minus physical cost, incremental liability, maintenance, and adjustment. Assumption 3.1 requires premium growth to cover the increase in marginal contractual shortage exposure. Theorem 3.2 proves increasing differences in the action pair and in both observed state coordinates, including propagation through the regime transition and continuation value. The proof handles demand atoms through integrated stock marginals and uses a greatest optimal pair. It does not assert a backlog comparative static in a model with no carried backlog.

For the recorded translated demand, premium slope 1.4 exceeds liability coefficient 1.2, giving a direct primitive check. Exact calculations verify 416 adjacent policy comparisons and value cross differences at all relevant states; the smallest adjacent value cross difference is 9/250. These finite checks supplement, rather than replace, the theorem.

## 3. Expanded-action equivalence and the scope of non-collapse (report Sections 5 and 13)

Proposition 2.1 states exact ordinary-MDP representation on the product action set. The expanded-action implementation is an equality check, not an opponent the joint method is expected to outperform. The independently enumerated solutions agree at every state, including rational values and selected actions.

The exposed-face result survives in its precise form: two distinct uniquely exposed transition slopes cannot be represented by a single fixed affine reward/kernel primitive. EC.1 proves it and explains why this does not exclude expanded actions or a continuum of affine controls. Frozen contracts are an explicitly restricted policy class. Dummy labels have no economic capacity advantage. The paper no longer describes ordinary product-action enlargement as a new general control class.

## 4. Entropic risk and Gibbs representation (report Section 4)

The main paper and EC.1 derive the Gibbs variational identity, including the entropy remainder and the full-support, positive-risk-parameter convention. A sufficiently rich kernel-control family represents entropic continuation exactly. The previous broad entropic non-equivalence claim is replaced by this exact intersection, not defended through terminology. Comparisons with exogenous preference or multiplier families require their actual admissible primitives to be specified.

## 5. Physical improvement must concern the actual optimizer (report Section 6)

The old critical-fractile matching argument is retained in EC.2 as a restricted-comparator result, with its density-based quadratic cost bound. It is not used to claim that the endogenous optimizer selects an externally inserted matching parameter.

Theorem 4.1 instead applies to the actual optimized policies. It gives the exact ledger identity and a physical-oracle gap budget. In the executed model, joint minus frozen net reward is 0.944747060878850, while frozen minus joint physical cost is 0.213203951173630. Joint physical cost is 9.374173780421842, above the oracle's 8.506094528783953. Fill decreases from 0.925925926 to 0.882108861. These mixed results are all retained. The oracle's contract-one cash flow is explicitly a tie convention; its physical lower bound does not depend on that convention.

## 6. One canonical model and complete recorded execution (report Section 7)

The external-contract model now appears in the root paper's equations, structural proof, exact DP, tables, and interpretation. No internal penalty-only theorem supplies the main operating conclusion. The continuous stopped diffusion is explicitly a separate computational test, not an asserted diffusion limit of the perishable experiment.

The integer implementation and an independently written Fraction implementation agree over 1,320 method/state-time combinations. Every policy is evaluated with its actual next-contract state. The primary joint and expanded methods each enumerate 143 distinct economic actions; frozen and dummy-gate methods have 13. The latter still enumerates its 11 duplicate labels so actual evaluation counts are transparent. All 64 × 4,096-episode simulation batches use common random paths and paired batch intervals. No parameter or method is changed based on an outcome sign.

## 7. Complete boundary problem and policy constant (report Section 8)

Theorem 5.2 defines a stopped Dirichlet problem with a specified lateral payoff, terminal payoff, corner compatibility, stopped dynamics, admissible Hamiltonian selectors, and comparison. The certificate separately records terminal and lateral sup defects. It proves the value bound and then both comparisons needed for policy loss: twice the boundary allowance, twice the optimal-residual allowance, and the actor gap. A direct actor-residual version is proved separately.

EC.3 retains an explicit heat-equation counterexample with zero terminal and interior defects but nonzero lateral values. It also gives an exact one-step example in which terminal critic error one produces policy loss 1.9 despite zero Bellman and greedy residuals. This checks the necessity of both comparisons. Reflected, Neumann, and state-constrained problems are not silently substituted for Dirichlet data.

## 8. A genuine quantitative refinement result (report Section 9)

Theorem 3.4 proves an O(n^-2) continuous-contract value and grid-policy bound from the convex envelope minus a quadratic. It does not assume global concavity. At 160 contract intervals the proved loss allowance is 0.000184209938, giving the exact rational enclosure exported in `contract_grid_refinement.csv`.

For the manufactured stopped diffusion, Proposition 5.3 proves a bound for the displayed explicit upwind/central scheme, with a nonnegative stencil, exact boundary values, analytic local defects, and backward nonexpansive propagation. The executed study actually refines spatial nodes (25 to 1,089), time steps (4 to 94), and actions per coordinate (9 to 65). It reports node-value errors, not an unproved continuous-actor bound. The archived 122-state action-cover study remains a fixed-state action-refinement audit.

## 9. Neural evidence, absolute tolerances, and positive constructive results (report Section 10)

The archived large-neural inventory ratios and percentile gaps remain sampled diagnostics. Missing absolute interior or lateral-boundary enclosures are not filled with zero, and the old literal “pass” field is not used as a theorem predicate. No new large-neural training run is claimed.

There is, however, new positive neural evidence tied to the canonical finite model. Corollary 3.5 constructs C2 cubic-ReLU critics from the exact rational envelope. A triangular smoothing identity gives a global, one-sided critic error bound and a uniform policy-loss budget. The networks use at most 27 cubic-ReLU units per state-time critic. Five smoothing levels are evaluated exactly over all 264 nonterminal states each. Every induced primary-grid policy is unchanged from the exact optimizer, while the analytic uniform policy budget decreases to 1.18419e-6. This is an explicit construction with certified weights and compatible gradients, not a post hoc training claim.

The separate manufactured PDE sequence has exact terminal and lateral data and analytically greedy controls. Its absolute policy bound decreases to 4.38690e-6. These results do not certify the unrelated historical large-network row.

## 10. QA and scientific statements (report Section 11)

Hash checks, manifests, replay guards, package consistency, and prior “referee closure” tables are preserved in the historical snapshot and indexed in EC.5. They are not part of the main theorem stack. The current validation files distinguish exact identities, analytic error budgets, floating-point observations, and execution metadata. Software success is not interpreted as a scientific tolerance or editorial validation.

## 11. Direct-P conditioning and the natural-data check (report Section 12)

Lemma 5.1 retains the exact 1/(2 epsilon) mean-square amplification under additive volatility error and makes gradient compatibility explicit. EC.3 preserves the shared-noise, adjoint, and vanishing-viscosity distinctions, including the fact that Dirichlet boundary values do not determine the full normal gradient.

The recorded identical-data least-squares study is executed without injected error, regularization, tuning, or early stopping. Direct and inferred gradients agree to numerical precision, as their identical fitted spaces imply. Their naturally induced volatility errors shrink with epsilon. The paper reports this parity rather than using the conditional amplification lemma to manufacture an empirical superiority claim.

## 12. OR positioning, presentation, and retained content (report Sections 13–17)

The title, abstract, introduction, theorem order, and computational study now emphasize externally priced service contracts, monotone operating decisions, envelope algorithms, and certified approximation. The current OR review format uses 11-point type, 1.5 spacing, one-inch margins, an anonymous title page, a text-only abstract, author-year references, and numbered tables after the reference list. The electronic companion is shorter than the main manuscript.

EC.5 and `PRESERVATION_AND_CLAIM_MAP.md` explain the destination and current role of every major historical contribution family. The old manuscript and all its supporting files remain byte-for-byte available in the exact reviewed snapshot. This is not an arbitrary content deletion. Incorrect claims have explicit counterexamples or replacement proofs; valid supporting derivations and historical empirical records are retained without presenting them as new evidence.

The revised scientific conclusions are the displayed theorems and executed comparisons. The package does not claim an external acceptance decision or uniform certification of historical neural experiments whose required bounds remain unavailable. It supplies the new manuscript and evidence needed for an independent subsequent review.
