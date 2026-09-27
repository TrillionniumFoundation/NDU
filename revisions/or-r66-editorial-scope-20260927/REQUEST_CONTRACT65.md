# R65 external-request and policy-transfer contract

The caller supplies a trusted request separately from the proof. A self-declared digest provides neither authenticity nor the requested tolerance. The independent checker accepts only equality to the supplied request; authentication of that caller or storage system is outside this mathematical checker.

## Schema

The request contains exactly `schema`, `spec`, `epsilon`, `certificate_class`, and `configured_guard`. `schema` is `NDU-R65-request-v1`. The physical `spec` is the full model, ordered catalog, charges, promise, and original integer command allowance used by the independent physical validator. Canonicalization compares every rational value exactly, including equivalent ordinary/hexadecimal fraction encodings. It does not truncate the external allowance to the effective algorithmic one.

`epsilon` is an exact nonnegative rational encoded as a string or integer, never a binary floating-point number or Boolean. For robust proofs it is the requested **total absolute fee-distortion** tolerance and must equal the proof's epsilon. For other classes it is the external requested objective width: the result recomputes `tolerance_met` against it, independent of any historical producer's internal stopping field. Acceptance of a mathematically valid wider interval is not reported as tolerance attainment. Numerical lower-only proofs never establish two-sided tolerance attainment.

`certificate_class` is one of the recognized mathematical proof schema identifiers: price, enumeration, deficit, exact tariff, robust tariff, or numerical lower-only. This is the class of the mathematical proof, not a claim about which high-level hybrid algorithm executed. `configured_guard` is a nonnegative integer for tariff and robust-tariff classes and null otherwise. For robust proofs the guard applies to the **inner modal exception count**, not the allowed projection budget. The checker validates its equality to the external request and actual exception count within the guard. The canonical modal tie string is `smallest rational fee`.

The envelope contains exactly `schema`, `request`, `request_sha256`, and `certificate`; its schema is `NDU-R65-request-bound-certificate-v1`. The SHA-256 digest is computed by `rational.digest` on the canonical request. Canonical JSON uses sorted keys and compact separators; exact rationals use the shared hexadecimal numerator/denominator representation. Raw external-request and physical-input digests are recorded separately. Changing both envelope request and its hash does not change the external anchor.

## Transfer check

The inner exact tariff proof is independently verified on the optimal projected charges. The outer policy is independently verified against original fees and original constraints. Their book is equal. The checker derives inner gross payoff as `inner_exact_value + sum(surrogate_selected_fees)` and outer gross payoff as `outer_checked_value + sum(original_selected_fees)`, requires equality, and explicitly verifies

```
lower = inner_exact_value - sum(original_fee - surrogate_fee for each selected command)
```

Any declared gross field must agree with its independently derived value. Alternative feasible policies with equal gross payoff on the same book are intentionally admissible. The contract certifies the exact transfer lower value, **not identity of physical-policy fields**. A different lower-gross allocation remains a feasible policy but fails this stronger transfer contract.

## Frozen-proof migration and scope

`bind_legacy` is packaging, not verification. `verify_request` always requires the separately supplied external request. `replay65.py` derives the spec and tolerance from the frozen case, certificate class from its immutable execution record, and guard from the case or frozen hybrid protocol (four). Old proof bytes are never modified. Envelopes are created at replay, never backdated. Original deadlines, failures, and timed success flags remain in the row receipt unchanged.

A verified guard is configuration agreement, not proof of actual runtime behavior. Mathematical feasibility, value bounds, request agreement, execution records, and editorial acceptance remain separate. The current public request-level API is `binding65.verify_request`; archived model-only `binding63` and low-level checkers must not be treated as request-level acceptance APIs.
