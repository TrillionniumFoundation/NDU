# Confidential Referee Report for *Operations Research*

**Manuscript:** *Finite-Catalog Resource Allocation: A Tariff-Sensitive Complexity Frontier*  
**Revision reviewed:** `revision/ndu-operations-research-r64-certificate-closure-20260927`  
**Audited revision tip:** `5704e3b4572da9726cab8bdcc8d74d0194f77d9e`  
**Audited source tree:** `e6d96192b83e764b1c78d437d7861f6f70d4c802`  
**Governing prior report:** `review/operation-research-r63-independent-harsh-20260927`, report commit `ddeb5f75febffd585eaf2d2c6e99a99b5c86cbdb`  
**Review branch:** `review/operation-research-r64-independent-harsh-20260927`  
**Date:** September 27, 2026  
**Recommendation:** **Minor Revision, with a presumption of acceptance once the two remaining certificate-semantic gaps are closed.**

---

## Executive assessment

R64 is a serious and largely successful response to the R63 report. The authors have correctly closed the two certificate gaps explicitly identified in that report: the tariff checker now recomputes the smallest rational modal fee, and the robust checker now independently recomputes the trimmed absolute-deviation projection, deterministic median/window ties, and the minimum exception allowance meeting the submitted distortion tolerance. The manuscript also now distinguishes exact sparse-exception tractability from additive policy transfer to near-standard original fees, gives appropriate antecedent credit, and supplies the requested projection-quality table from immutable records.

I continue to find the central scientific contribution sound and potentially publishable:

1. a constructive exact reduction from the original history-level allocation problem to selected-boundary resource paths;
2. W[1]-hardness in command allowance plus distinct-cap count under common linear reward and free preliminary service;
3. exact fixed-parameter tractability in the number of commands whose fee differs from a standard tariff, under the same physical primitives;
4. an exact uniform-fee polynomial regime and installation-cardinality frontier;
5. an original-feasible additive transfer certificate for sparse-exception surrogates of near-standard tariffs;
6. and complementary resource-deficit and same-book price certificates for broader regimes.

I find no fatal mathematical error in the exact representation, lower bound, tariff dynamic program, fee-perturbation theorem, trimmed projection proposition, length-aware conservation construction, or same-book support theorem. R64 also passes an unusually strong reproducibility audit. I independently validated the package manifest and source closure, reran the semantic regression suite, and replayed all 405 frozen requests in parallel chunks through the current external-input binding and independent proof checkers. The totals exactly match the submitted receipt: 342 rational two-sided proofs, 47 numerical-solver lower policies, 16 no-certificate requests, and 16 exactly equivalent but byte-different input serializations, with no replay errors.

However, the revision's claim of complete certificate-semantic closure is still slightly too strong. I found two additional, reproducible gaps:

- the tolerance that determines the claimed minimum projection allowance is self-declared by the certificate and is not bound to the external request;
- the robust checker requires only that the original-fee policy use the same book as the surrogate policy, not that it be the same physical policy or attain the theorem's stated transfer lower bound.

Both gaps leave the submitted mathematical upper and lower intervals valid. They do not overturn any theorem or recorded numerical conclusion. They do, however, permit a certificate to pass while making a false claim about either the requested projection tolerance or the exact policy-transfer formula. Because auditability is an explicit contribution of this paper, these points should be corrected before acceptance.

No new central theorem and no new large computational campaign are required.

---

## Referee scorecard

| Dimension | Assessment | Comment |
|---|---:|---|
| Technical correctness | 4.7/5 | No fatal mathematical flaw found; two proof-schema claims remain under-bound. |
| Originality | 3.5/5 | The model-specific representation and tariff-sensitive parameterized frontier are genuine; the projection and coefficient-sensitivity components are correctly presented as antecedent machinery. |
| Significance for OR | 3.7/5 | A credible optimization-theory contribution with implementable recovery and a meaningful tariff frontier. |
| Algorithmic contribution | 4.2/5 | Exact FPT regime, uniform-fee polynomial algorithm, reconstructed original policy, fee frontiers, and independent global certificates. |
| Computational evidence | 4.2/5 | Well aligned with the theorem and exceptionally transparent, though constructed rather than field calibrated. |
| Exposition | 4.2/5 | The dominant scientific argument is now clear; secondary machinery remains extensive but no longer obscures the core. |
| Reproducibility | 4.7/5 | Excellent exact-head, freeze, replay, failure-preservation, and semantic testing; the two remaining bindings prevent a full score. |
| Overall | Minor Revision | Scientifically acceptable after a bounded checker/schema correction. |

---

# 1. Version, provenance, build, and independent audit

## 1.1 Exact reviewed object

The reviewed R64 branch tip is `5704e3b4572da9726cab8bdcc8d74d0194f77d9e`, with source tree `e6d96192b83e764b1c78d437d7861f6f70d4c802`. It is seven commits ahead of the exact R63 reviewed tip and descends directly from that author commit. The R63 referee report is pinned by immutable commit and blob rather than merged as a scientific parent.

The exact tip carries the successful status `ndu/r64-exact-head`. Its receipt binds the published commit, source-trigger commit, scientific parent, governing review, package manifest, reader hashes, build diagnostics, semantic tests, 48 exact root-support cases, and 389 frozen certificates.

The current build reports:

- 31 article PDF pages, 28 excluding references;
- 30 companion pages;
- a four-page response;
- a 173-word text-only abstract;
- no unresolved references;
- and no overfull boxes.

## 1.2 Independent execution

I downloaded and unpacked the 13.7 MB `ndu-or-r64-referee-package-and-exact-head-receipt` artifact and audited the flat submission.

I independently ran `verify64.py`; it passed the complete package inventory, R63 preservation map, current source freeze, 48 root-support cases, replay receipts, semantic test counts, structural test receipts, projection table provenance, and build limits.

I independently reran `code/tests64.py`. It accepted 577 valid robust certificates, compared 288 projections against exhaustive retained-subset enumeration, reproduced ten complete certificates with false semantic metadata that the archived checker accepts, and confirmed that the current checker rejects all ten.

I also independently replayed every one of the 405 frozen records in six parallel chunks using the current `binding63.verify_bound` path. The aggregate result was:

- 342 `PASS` rational two-sided proofs;
- 47 `PASS_LOWER_ONLY` numerical-solver policies;
- 16 requests with no certificate;
- 16 fieldwise-equal but byte-different input serializations;
- zero checker exceptions or hash failures.

This replay was an integrity audit only. It does not change the original timing, deadline, or target-attainment classifications.

---

# 2. What R64 successfully closes

## 2.1 Canonical standard-fee semantics

The revised tariff checker independently counts exact rational fees, chooses the smallest rational value among the most frequent modes, and requires the certificate's declared standard to equal that value. It then recomputes the relative exception inventory, all `2^d` exception subsets, every capacity state, every branch bound, and the original feasible policy.

This correctly separates two facts:

- the dynamic program is exact for any declared standard if all relative exceptions are enumerated;
- choosing a mode minimizes the exception parameter, while the smallest-mode rule fixes deterministic ties.

The new adversaries for a nonmodal standard and an incorrect tied mode are appropriate and pass/fail exactly as claimed.

## 2.2 Optimal sparse projection and minimum allowance

The new `check_projection64.py` is independent of the prefix-sum optimizer. For a submitted allowance it sorts the original fees, directly evaluates every consecutive retained window at its lower median, applies deterministic ties, checks the complete projected vector and exception inventory, binds the inner tariff proof to that vector, and verifies failure of the preceding allowance.

The mathematical reasoning is correct. In one dimension, an optimal retained set for a fixed center can be chosen contiguous after sorting, and a median minimizes the retained absolute deviation. Monotonicity of the optimal distortion in the allowed number of exceptions makes the `d-1` failure check sufficient for minimum allowance.

The paper now also distinguishes:

- the allowed projection budget `d_allow`;
- the actual projected exception count `d_proj`;
- and the inner solver's modal exception count `d_tariff`.

That distinction is necessary and correctly stated.

## 2.3 Exact versus approximate tariff claims

The abstract, introduction, robustness section, and conclusion now say that the exact sparse-exception surrogate is transferred to the original near-standard tariff through an additive original-policy certificate. They no longer imply an exact FPT algorithm for arbitrary near-standard original fees.

The retained perturbation theorem is correct. Only objective coefficients change, so the surrogate policy remains physically feasible. The sums of the largest positive and negative fee differences give valid one-sided bounds over every book of at most `m` commands.

## 2.4 Antecedent positioning

The manuscript now credits least trimmed absolute deviation, consecutive-window/median preprocessing, and objective-coefficient sensitivity. It does not present the median or the elementary coefficient comparison as new general algorithms. The model-specific contribution is correctly located in their integration with an exact original-model tariff solver and a reconstructed original-feasible policy interval.

## 2.5 Projection-quality evidence

Table 5 is useful and appropriately conservative. It includes all twelve adversarial robust requests, including mathematical inapplicability and an engineering guard; distinguishes exact zero regret from bounded regret; reports the three exception counts separately; and pairs original optimization/checking time with raw and compressed proof size. It does not relabel post-study comparator checks as original target attainment.

---

# 3. Remaining required revision 1: bind the certificate to the requested tolerance

## 3.1 The current gap

The physical model input is externally bound, but the robust request tolerance is not.

`binding63.verify_bound(cert, expected)` compares the certificate's model specification with the external specification. The specification contains probabilities, caps, ceilings, reward and service coefficients, catalog, fees, promise, and command allowance. It does not contain the requested additive tolerance.

`check_projection64.verify_projection` instead reads `cert['epsilon']` from the certificate itself. Consequently, the checker certifies that the selected exception allowance is minimal for the certificate's self-declared distortion tolerance, not necessarily for the tolerance requested by the external case.

The historical replay later checks interval width against the case tolerance only for records originally marked as target attainment. That protects the numerical target claim. It does not bind the certificate's “minimum allowance” metadata to the external request.

## 3.2 Reproducible witness

Consider two equally likely histories with caps and ceilings one, common reward `f(x)=x`, free service, catalog `(0,1/2,1)`, promise `B=1/4`, command allowance three, and fees `(0,1/100,2/100)`.

- With requested tolerance `1/10`, the minimum projection allowance is zero.
- A certificate generated for the stricter self-declared tolerance `1/200` uses allowance two and closes the value interval exactly.
- Passing that stricter certificate together with the same external physical specification to `binding63.verify_bound` returns `PASS`.

The interval is valid and is more accurate than requested. The false claim is that allowance two is the minimum allowance for the external `1/10` request.

## 3.3 Required correction

Create and bind a request object, not only a model object. At minimum it should include:

- the exact physical specification;
- requested tolerance;
- method or certificate class;
- and, when reported as certified execution metadata, the configured exception guard.

The independent checker should receive the external request or an immutable digest of it and require equality with the certificate's request fields. Add a coordinated mutation test in which the physical input remains unchanged but the certificate tolerance is changed.

For the existing frozen panel, the submitted robust certificates' epsilon values agree with their case files. Therefore this correction should require only checker/schema work and a new integrity replay, not a new optimization study or reclassification of original timing outcomes.

---

# 4. Remaining required revision 2: certify the theorem's actual transferred lower bound

## 4.1 The current gap

Theorem 6 states that the same surrogate-optimal physical policy, evaluated under the original fees, has lower value

`L = V_tilde - sum_{i in c_tilde}(rho_i - rho_tilde_i)`.

The current robust checker validates the inner exact tariff proof and checks an outer original-fee policy. It requires only that the inner and outer policies select the same book. It does not require:

- equality of the physical policies;
- equality of their gross values;
- or equality of the lower bound to the displayed transfer formula.

It therefore accepts a different, deliberately degraded feasible allocation on the same book, provided the resulting wider interval still fits the certificate's tolerance.

## 4.2 Reproducible witness

Use the same two-history instance above. The uniform surrogate selects book `(0,1/2)`. The surrogate-optimal physical allocation, evaluated under the original fees, gives the theorem's lower value `6/25`.

I changed only the outer policy:

- retained the same book `(0,1/2)`;
- shifted `1/50` of the first history's terminal obligation to free preliminary service;
- adjusted its lottery to preserve the exact target and every cap/ceiling;
- set the original gross value to `6/25` and net lower value to `23/100`;
- retained upper value `6/25` and tolerance `1/10`.

The current `check_robust61.verify` returns `PASS`. The resulting interval `[23/100,6/25]` is mathematically valid, but the certificate no longer establishes the theorem's stated same-policy transfer or its displayed lower formula.

## 4.3 Required correction

The robust checker should require one of the following equivalent contracts:

1. the outer physical policy fields are identical to the inner policy fields, with only the fee-dependent value recomputed; or
2. if alternative fixed-book tie solutions are allowed, the outer book is identical, its gross payoff equals the inner gross payoff, and

   `lower = inner_exact_value - sum_{i in book}(rho_i-rho_tilde_i)`.

The second option is more robust to harmless tie-breaking differences. Add a mutation test that preserves the book and feasibility while degrading terminal reward through preliminary service.

Again, the current producers already construct the intended canonical transferred policy. Existing legitimate certificates should pass the strengthened check without rerunning optimization.

---

# 5. Certificate metadata hygiene

I also confirmed that changing `configured_guard` and the textual `modal_tie_rule` field in a tariff certificate does not affect acceptance. The modal fee itself is recomputed, so a false tie-rule string has no mathematical effect. The guard is execution metadata rather than part of the exact optimization proof.

The authors should choose one clean convention:

- remove unverified execution metadata from the mathematical certificate;
- label it explicitly as untrusted informational metadata;
- or bind and verify it through the external request object proposed above.

This point alone would not block acceptance, but resolving it together with the tolerance binding would make the certificate scope unambiguous.

---

# 6. Mathematical assessment

## 6.1 Selected-boundary representation

The model-specific reconstruction remains convincing. The path capacities telescope while ceiling eligibility changes payoffs rather than hidden resource state. The rearrangement and packing arguments produce original lotteries and preliminary service satisfying the accepted aggregate equality, individual expected caps, realization ceilings, and command budget.

## 6.2 Complexity frontier

The W[1] lower bound and tariff-exception upper bound address different structural parameters in the same linear/free-service physical subclass. This is now a coherent frontier rather than a juxtaposition of unrelated special cases. The manuscript correctly avoids claiming W[1]-membership, a strong-hardness result, a kernel lower bound, or a complete classification for curved rewards.

## 6.3 Tariff dynamic program

Conditional on the chosen exceptional subset and book cardinality, the charge is constant. Gross value is nondecreasing in terminal capacity. Retaining one maximum-capacity state for each subset/cardinality/endpoint is therefore exact. The `2^d` factor multiplies a polynomial whose exponent is independent of `d`, and predecessor recovery gives an original feasible policy.

I did not find a counterexample in the proof or in exhaustive small-instance checks.

## 6.4 Robust transfer and projection

The fee-transfer bounds are elementary but correct, and the paper now positions them properly. The sparse projection proposition is also correct under its precise surrogate class. The manuscript appropriately says that minimum total fee distortion need not minimize final interval width, realized regret, or running time.

## 6.5 Broader results

The length-aware conservation lifting, same-path repair, and same-book price-support theorem remain sound within their stated assumptions. They are complementary results rather than the primary novelty, which is now reflected in the exposition.

---

# 7. Computational and reproducibility assessment

The expanded evidence remains well designed for a theory paper:

- exception count is varied through `0,1,2,4,6,8,10,12`;
- physical sizes reach `(N,k,m)=(129,48,32)`;
- optimization, checking, memory, raw proof size, and compressed proof size are separated;
- the adversarial generator is distinct from the earlier seeded panel and the hardness construction;
- the hybrid is actually executed and its mixed performance is reported;
- root support is classified through an independent exhaustive 48-case diagnostic;
- numerical SCIP upper bounds remain separate from rational global certificates;
- unfavorable deficit and screening results remain visible;
- and later replay never promotes an original deadline failure.

The lack of field calibration remains a limitation, but the manuscript says so clearly. I do not regard field data as necessary for acceptance of the present optimization-theory contribution.

---

# 8. Required revision checklist

Before acceptance, I require the authors to:

1. bind the requested tolerance to the certificate or external request digest;
2. bind any claimed configured guard if it remains scientific certificate metadata;
3. strengthen the robust checker to verify the exact transfer lower formula or equal gross payoff, not only the selected book;
4. add the two coordinated adversaries described in Sections 3 and 4;
5. replay all existing robust certificates with the strengthened checker while preserving original timing classifications;
6. document the request-level certificate schema in the companion;
7. either validate or remove redundant textual metadata such as `modal_tie_rule`;
8. update the response and exact-head receipt to state precisely which claims are certified.

No new theorem, solver design, or large experiment is required.

---

# 9. Minor editorial comments

1. In the abstract, “minimum-distortion fee projection” is accurate only for the declared trimmed-L1 surrogate class; retaining “within the stated sparse-exception class” once in the main text would prevent overreading.
2. The projection checker complexity is asymptotically stated correctly, although the implementation sorts separately for `d` and `d-1`; the text need not claim one shared sort unless implemented.
3. The projection-quality table's `Regret` column is handled carefully. Keep the bracket notation and avoid shortening it to “regret” without “bound” in surrounding prose.
4. The service-credit interpretation remains stylized. Continue to avoid adoption or field-performance language.
5. The main article is now 28 nonreference pages and the companion 30 pages. Further certificate implementation detail should remain in the companion rather than expanding the main narrative.
6. Preserve the distinction between exact optimality of the surrogate, exact feasibility of the returned original policy, and additive optimality for the original tariff.

---

# 10. Recommendation to the editor

R64 has completed the scientific revision requested in R63. The principal theory is coherent, the main proofs appear correct, the evidence is unusually transparent, and the manuscript now has a publishable contribution hierarchy.

The two remaining issues are not mathematical counterexamples. They are proof-contract mismatches exposed by coordinated certificates that retain valid bounds while falsifying a stronger semantic claim. In an ordinary paper I might treat them as software errata. In this manuscript, independent certification is part of the contribution, so they should be closed before acceptance.

**Recommendation: Minor Revision, with acceptance expected after the request-tolerance and transferred-policy bindings are repaired and independently replayed.**
