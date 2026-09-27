# Confidential Referee Report for *Operations Research*

**Manuscript:** *Finite-Catalog Resource Allocation: A Tariff-Sensitive Complexity Frontier*  
**Revision reviewed:** `revision/ndu-operations-research-r65-request-transfer-20260927`  
**Audited revision tip:** `6bc195dcdbc93d1a796b1388639c053c0a11ddd0`  
**Audited source tree:** `13f8d13ef25e3ca6c1dd99e046b245bc70f0d5a2`  
**Governing prior report:** `review/operation-research-r64-independent-harsh-20260927`, report commit `3fa2fc1db4257a15af4b3a437c54b306a4589e63`  
**Review branch:** `review/operation-research-r65-independent-harsh-20260927`  
**Date:** September 27, 2026  
**Recommendation:** **Accept. No further scientific revision is required. The remaining comments are nonblocking editorial clarifications and should not require another referee round unless the accepted manuscript changes its mathematical claims, checker contract, or empirical evidence.**

---

## Executive assessment

R65 closes the two remaining certificate-semantic gaps identified in my R64 report and preserves the scientific contribution that had already reached the acceptance threshold.

The manuscript now presents a coherent optimization-theory contribution:

1. a constructive exact representation of the original history-level allocation problem as a selected-boundary resource path, with recovery of original lotteries and preliminary service;
2. an original-model W[1]-hardness result parameterized by command allowance and distinct expected-cap count, already under common linear reward and free preliminary service;
3. an exact fixed-parameter algorithm in the number of commands whose opening fee differs from a standard tariff, under the same physical primitives;
4. an exact polynomial regime and installation-cardinality frontier under uniform fees;
5. an original-feasible additive transfer certificate from an exactly solved sparse-exception surrogate to a near-standard original tariff;
6. and complementary resource-deficit approximation and same-book price-support results for broader regimes.

I continue to find no fatal mathematical error in the selected-boundary representation, parameterized reduction, tariff dynamic program, perturbation bound, trimmed absolute-deviation projection, length-aware conservation theorem, or same-book support theorem. The main mathematical environments are byte-identical to R64; R65 changes the request/proof contract and explanatory text rather than silently altering the scientific results.

The two prior blockers are now genuinely resolved.

First, the checker no longer treats a self-declared certificate tolerance as the requested tolerance. The caller supplies an external request containing the complete physical specification, exact tolerance, proof class, configured exception guard, and schema version. The submitted envelope and digest are checked against that separate trust anchor. Coordinated changes to both the envelope and its digest do not evade the comparison.

Second, the robust checker no longer accepts an arbitrary lower-gross allocation merely because it uses the surrogate book. It independently validates the inner and outer policies, requires the same book and equal gross payoff, and checks the exact transfer formula

`lower = inner_exact_value - sum(original_fee - surrogate_fee over the selected book)`.

This permits harmless alternative fixed-book optima at ties, but rejects a feasible degraded same-book policy that does not establish the theorem's stated lower value.

I downloaded and independently audited the complete R65 referee package rather than relying only on repository `PASS` labels. The request-level regressions, package verification, independent PDF rebuild, complete proof replay, and additional randomized exhaustive checks all passed. I therefore see no remaining scientific or certificate-semantic basis for another revision cycle.

---

## Referee scorecard

| Dimension | Assessment | Comment |
|---|---:|---|
| Technical correctness | 4.8/5 | No fatal flaw found in the principal representation, lower bound, tariff algorithm, transfer theorem, projection, or recovery. |
| Originality | 3.6/5 | The model-specific representation and tariff-sensitive parameterized frontier are genuine; standard projection and sensitivity machinery are now properly credited. |
| Significance for OR | 3.9/5 | A credible and useful optimization-theory contribution with explicit implementation recovery and a meaningful fee-structure frontier. |
| Algorithmic contribution | 4.3/5 | Exact FPT regime, uniform-fee polynomial algorithm, original-policy reconstruction, fee frontiers, and independently checkable global certificates. |
| Computational evidence | 4.2/5 | Well aligned with the theorem, complete about failures and checking cost, and appropriately described as constructed rather than field calibrated. |
| Exposition | 4.3/5 | The dominant scientific argument is clear and the exact-versus-additive scopes are now consistently separated. |
| Reproducibility | 5/5 | Exact-head binding, immutable request replay, failure preservation, adversarial semantic tests, source closure, and independent certificate checking are exceptional. |
| Overall | Accept | The contribution is publishable in its current scientific form. |

---

# 1. Exact reviewed object, provenance, and build

The reviewed branch tip is `6bc195dcdbc93d1a796b1388639c053c0a11ddd0`, with tree `13f8d13ef25e3ca6c1dd99e046b245bc70f0d5a2`. It descends directly from the exact R64 author commit `5704e3b4572da9726cab8bdcc8d74d0194f77d9e`. The R64 referee report is pinned by immutable commit, path, and blob; it is not merged as a scientific parent.

The exact tip carries the successful status `ndu/r65-exact-head`. The external receipt binds:

- the final published commit and tree;
- the source-trigger commit;
- the R64 scientific parent;
- the governing R64 referee report;
- the package manifest and reader hashes;
- the request/transfer semantic tests;
- the 48 exact root-support cases;
- and the fresh replay of all available frozen proofs.

I independently rebuilt the three readers from the supplied standalone sources. The build produced:

- 31 article pages, 28 excluding references;
- a 31-page electronic companion;
- a three-page response to referees;
- a 178-word text-only abstract;
- no unresolved references;
- and no overfull boxes.

The package verifier also confirms preservation of all 6,992 R64 manifest entries and byte identity of 36 mathematical environments in the main article and 42 in the companion.

---

# 2. Independent audit performed for this report

## 2.1 Request and transfer regressions

I independently reran `code/tests65.py`. The suite passed:

- 66 valid request-level checks;
- 25 rejected request, metadata, tolerance, class, guard, or transfer adversaries;
- the two complete R64 referee witnesses, which are accepted by the archived checker and rejected by the current checker;
- equivalent rational request encodings;
- a different physical policy with the same book and equal gross payoff;
- exact tariff requests;
- robust requests at multiple tolerances;
- and an optimizer-import closure test for the request checker.

The first coordinated witness uses the same physical model but a certificate generated for projection tolerance `1/200` when the external request asks for `1/10`. The old model-only path accepts it; the R65 request-level checker rejects it because the projection tolerance differs from the external request.

The second witness keeps the same selected book and remains physically feasible, but deliberately lowers gross payoff by shifting terminal obligation to free preliminary service. Its wider objective interval remains valid. The old robust checker accepts it; the R65 checker rejects it because the transferred policy does not have the surrogate-optimal gross payoff.

The regression suite also rejects coordinated envelope/digest changes, wrong proof classes, unknown request fields, missing tolerance, floating-point tolerance, Boolean or negative guards, changed promise, changed original command allowance, false or missing modal tie metadata, and false inner or outer gross metadata.

## 2.2 Complete frozen-proof replay

I independently ran a fresh full replay of the 405 frozen requests through the current external-request binding and mathematical checkers. The replay completed successfully in approximately 49 seconds on my review environment and returned:

| Replay class | Count |
|---|---:|
| Rational two-sided proofs: `PASS` | 342 |
| Numerical-solver lower policies: `PASS_LOWER_ONLY` | 47 |
| Requests with no certificate | 16 |
| Available certificates | 389 |
| Request-bound certificates | 389 |
| Robust proofs passing request and transfer checks | 42 |
| Exactly equal but byte-different input serializations | 16 |
| Later-successful replays not retroactively reclassified | 45 |
| Replay errors or hash failures | 0 |

The external request for each replay is derived from the frozen case and immutable execution record, not from the certificate being checked. For hybrid robust proofs, the guard is taken from the frozen four-exception protocol. Historical proof bytes and original timing/failure classifications remain unchanged.

## 2.3 Additional randomized exhaustive checks

Beyond the submitted test suite, I generated 240 additional small rational linear/free-service instances with random histories, probabilities, caps, ceilings, catalogs, command allowances, fees, promises, and robust tolerances.

For each instance I:

- compared the exact tariff result with exhaustive enumeration of every feasible book;
- checked that the robust lower and upper bounds contain the exact original-fee optimum;
- checked that the robust interval width does not exceed the externally requested tolerance;
- recomputed the transferred lower formula directly from the selected book and the original/surrogate fee differences;
- changed the external tolerance while keeping the certificate fixed and confirmed rejection;
- changed the external guard while keeping the certificate fixed and confirmed rejection;
- and verified the exact tariff request through the request-bound API.

All 240 instances passed without discrepancy. These finite tests do not replace the proofs, but they provide additional independent evidence that the R65 corrections are not limited to the two hand-crafted witnesses.

---

# 3. Resolution of the R64 required revisions

## 3.1 External tolerance is now part of the trusted request

The request schema contains exactly:

- schema version;
- complete physical specification;
- exact nonnegative rational tolerance;
- mathematical certificate class;
- configured exception guard.

The envelope contains a canonical copy and digest, but the verifier compares both with a separately supplied caller request. The envelope is not its own trust anchor.

For robust proofs, the certificate's projection tolerance must equal the external tolerance. Minimum projection allowance is then checked against that external value by verifying both attainment at `d` and failure at `d-1`. This closes the precise semantic gap identified in R64.

For price, enumeration, deficit, and exact-tariff proofs, the verifier independently recomputes whether the returned interval meets the external requested objective width. A mathematically valid wider interval can still be verified, but is not reported as target attainment. Numerical lower-only proofs are never reported as two-sided tolerance certificates.

## 3.2 The transferred lower formula is now independently certified

The inner exact tariff proof is checked on the projected fees. The outer policy is checked on the original fees and original physical constraints. The checker then requires:

- identical selected books;
- identical independently derived gross payoff;
- and exact equality of the original lower value with the theorem's transfer formula.

This is the correct tie-compatible contract. Literal identity of every target and lottery field is unnecessarily restrictive when the fixed-book allocation has multiple gross-optimal solutions. Equal book and equal gross payoff are sufficient: the outer policy is then also surrogate-optimal and its original-fee value is exactly the displayed transfer lower bound.

The checker does not trust a declared gross field. It derives gross payoff from the independently checked net value and selected-book charges; any supplied gross metadata must agree.

## 3.3 Guard and modal-fee metadata are correctly scoped

The exact tariff checker independently recomputes the smallest rational modal fee, its exception inventory, and the actual exception count. It validates the canonical tie string and requires a nonnegative integer configured guard that covers the actual modal exception count.

The request-level verifier additionally requires the proof guard to equal the external request guard. The manuscript correctly states that this proves compatibility with a declared mathematical request, not that a particular runtime process actually used that guard. Runtime, deadline, and resource claims remain properties of immutable execution records.

## 3.4 Historical migration is represented honestly

Legacy proof bytes are not rewritten or backdated. Request envelopes are created at replay time and marked as such. Later successful integrity replay does not upgrade an original timeout, failed check, missing check, or missed target into an original success.

This distinction is especially important for the 45 later-successful checks that retain their historical unsuccessful or incomplete classification. R65 handles it correctly.

---

# 4. Mathematical assessment

## 4.1 Exact selected-boundary representation

The representation remains convincing and constructive. Ceiling eligibility changes which histories contribute terminal increments and service tails, but total capacity telescopes through a potential. The rearrangement and packing arguments recover original policies satisfying:

- the exact accepted aggregate promise;
- every expected cap;
- every outcome-by-outcome realization ceiling;
- the command allowance;
- and the selected opening charges.

The result is not merely a relabeling of a generic constrained-path problem. The paper proves why the original history-level restrictions collapse to the stated path capacities and edge payoffs.

## 4.2 Parameterized lower bound

The retained multicolored-clique/group-sum construction continues to support the W[1]-hardness claim. The zero command and group baselines consume actual command slots; the threshold equality excludes multiple positive options from one group; and the no-carry digits enforce vertex-edge consistency.

The reduction remains inside the original policy model with common linear reward, free service, positive uniform probabilities, caps equal to ceilings, and nonnegative rational opening charges. The manuscript appropriately avoids claiming W[1]-membership, completeness, strong NP-hardness, an ETH exponent lower bound, or a kernel lower bound.

## 4.3 Exact tariff-exception algorithm

For a fixed included set of exceptional commands and a fixed book cardinality, every admissible book pays the same charge. Under common linear reward and free service, gross value is nondecreasing in attainable terminal capacity. Therefore the dynamic program may retain one maximum-capacity label per exception subset, selected-command count, and endpoint.

The resulting `2^d` factor multiplies a polynomial whose exponent is independent of `d`, and predecessor recovery supplies an original feasible policy. Uniform fees give the stated polynomial exact regime without a capacity or promise grid.

I found no counterexample in the proof, submitted exhaustive tests, or my additional random enumeration.

## 4.4 Near-standard transfer and sparse projection

The transfer theorem is elementary but correct and now precisely scoped. Only opening-fee coefficients change; physical feasibility is unchanged. The sums of the largest positive and negative fee differences over at most `min(m,N)` commands give valid one-sided global bounds.

The sparse projection proposition is correct for its declared surrogate class. After sorting, a minimum trimmed absolute-deviation retained set can be chosen as a consecutive window, and a median minimizes its absolute deviation. The paper now gives appropriate antecedent credit and does not advertise this preprocessing as a new general clustering algorithm.

Crucially, R65 consistently describes the result as:

- exact optimization of a sparse-exception surrogate;
- exact feasibility and exact fee evaluation of the returned original policy;
- and additive optimality for the original tariff.

It does not claim exact fixed-parameter tractability for arbitrary near-standard original fees.

## 4.5 Complementary approximation and price results

The length-aware conservation lifting, same-path repair, centered deficit approximation, and same-book price-support theorem remain sound within their stated assumptions. Their prominence is now appropriately secondary to the representation and tariff-sensitive complexity frontier.

---

# 5. Computational and evidentiary assessment

The computational evidence is unusually transparent for a theory paper.

The controlled scaling study varies exception count through `0,1,2,4,6,8,10,12` and physical sizes through catalogs of 17, 65, and 129 commands. It separately reports optimization, serialization, verification, resident memory, uncompressed proof size, and compressed proof size. It preserves cases where optimization finishes but checking misses the parent deadline.

The separate adversarial panel does not reuse the earlier seeds or the clique reduction. It reports mixed method performance rather than selecting only favorable outcomes. Price succeeds on all twelve adversarial cases, while the executed hybrid succeeds on eight, robust tariff on seven, exact tariff on four, and deficit and enumeration on none. SCIP's upper bounds remain numerical; only reconstructed feasible lower policies receive exact independent checks.

The 48-case root-support diagnostic enumerates all feasible books and constructs the exact upper hull independently of the price-path recurrence. It distinguishes support by one active original book from a relaxation that mixes books.

The manuscript retains the negative screening and deficit observations, all interrupted requests, all missing certificates, and phase-dependent denominators. It correctly states that these are constructed experiments rather than customer observations, a standard external benchmark, or evidence of field adoption.

I do not require field data for acceptance of this optimization-theory contribution. The operational interpretation is stylized, but the mathematical decision structure, assumptions, and limitations are explicit.

---

# 6. Nonblocking limitations and editorial comments

The following points should be preserved during final production, but none warrants another scientific revision.

1. Keep the exact theorem's physical regime explicit: common linear terminal reward and free preliminary service. Uniform fees do not solve the general curved/costly-service model.
2. Continue to describe near-standard tariffs through an additive transfer certificate, not an exact-tractability extension.
3. Preserve “within the specified sparse-exception class” whenever describing the minimum-distortion projection.
4. Keep `d_allow`, `d_proj`, and `d_tariff` distinct. They have different meanings and need not coincide.
5. Retain the statement that a verified guard is request agreement, not runtime attestation.
6. Retain the distinction between a mathematical proof's `PASS`, original on-time target attainment, and later integrity replay.
7. Do not relabel numerical SCIP upper bounds as exact rational certificates.
8. Keep bracket notation for regret intervals when comparator evidence does not identify exact regret.
9. Preserve the disclosure that historical wrappers are constructed at replay rather than claimed to have existed during original execution.
10. Keep request authentication and trusted storage outside the mathematical checker's certified scope unless an actual authenticated transport layer is later added.
11. Avoid implying that the tested hybrid is a universally optimal routing policy; the submitted adversarial results directly contradict such a claim.
12. Certificate implementation detail should remain primarily in the companion so that the main article stays centered on the representation and complexity frontier.

One optional software-hardening improvement would be to state explicitly that only fields represented in the returned verification receipt are certified; arbitrary unknown extension metadata inside a low-level legacy certificate should not be interpreted as endorsed. The current exact request and envelope schemas already reject unknown fields, and I found no submitted result that depends on an unchecked extension field.

---

# 7. Recommendation to the editor

R65 has completed the bounded revision requested in R64. The two coordinated proof-contract witnesses are now rejected for the correct reasons, all 42 frozen robust proofs pass the strengthened request and transfer checks, all 389 available frozen proofs pass request-bound replay, and the scientific results remain unchanged.

The manuscript's principal contribution is now both mathematically coherent and accurately scoped. The exact selected-boundary representation, original-model lower bound, tariff-exception FPT upper bound, uniform-fee frontier, and original-policy transfer certificate form a credible *Operations Research* theory paper. The computational evidence is aligned with those claims and unusually honest about proof cost, failure, dependence, and numerical versus rational evidence.

I therefore recommend **Accept**. I do not request another referee round unless the final accepted version materially changes a theorem, proof, request schema, independent checker, or reported computational result.
