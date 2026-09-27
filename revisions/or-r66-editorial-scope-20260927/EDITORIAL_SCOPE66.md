# R66 editorial scope and response map

The governing R65 report recommends **Accept** and requests no further scientific revision. This is a response to a referee recommendation, not a claim of an editor's or journal's formal acceptance.

R66 makes the optional receipt-scope clarification and preserves all twelve nonblocking qualifications. No theorem, proof, mathematical display, bibliography, empirical table, solver, checker, request schema, frozen input, historical timing, failure classification, or original certificate is changed. The request API deliberately remains `binding65.verify_request` and its schema remains `NDU-R65-request-v1`.

## Comment-by-comment disposition

| R65 item | Subject | Current location | Disposition |
|---|---|---|---|
| 1 | Physical regime of exact tractability | Main, Sections 1 and 5; Theorem 5.1 | The common linear terminal reward and free preliminary service assumptions remain explicit. Uniform fees are not asserted to solve the curved-reward or costly-service model. |
| 2 | Near-standard tariffs | Main, Abstract and Section 6 | The surrogate is solved exactly; the recovered original policy is feasible and evaluated exactly, but its original-fee optimality guarantee remains additive. |
| 3 | Projection class | Main, Abstract, Section 6.2 and Proposition 6.2 | Minimum distortion is claimed only within the specified sparse-exception class. The trimmed absolute-deviation antecedents and proof are retained. |
| 4 | Three exception counts | Main, Section 6 and Table 5; companion, EC.11.2 | d_allow is the projection allowance, d_proj the actual exceptions around its projection standard, and d_tariff the inner modal count. Their distinct definitions and inequality are unchanged. |
| 5 | Guard interpretation | Companion, EC.11.1 and verification-receipt paragraph | A verified guard means agreement with the external mathematical request, not an attestation that a runtime process used that guard. |
| 6 | Proof, target and execution outcomes | Main, Section 9 and table notes; companion, EC.11.1 | Mathematical PASS, requested-width attainment, original on-time success and later integrity replay remain separate. No original failure is upgraded. |
| 7 | Numerical upper bounds | Main, Section 9 and Table 2; companion, EC.11.1 | SCIP upper bounds remain numerical. Independently reconstructed feasible policies establish lower bounds only, with PASS_LOWER_ONLY and no certified upper bound. |
| 8 | Regret intervals | Main, Section 9.5 and Table 5 | Bracket notation is unchanged when exact regret is not identified. The five identified zero regrets and two bounded regrets retain their original comparator evidence. |
| 9 | Historical wrappers | Companion, EC.11.1; REQUEST_CONTRACT65.md | Legacy bytes remain unchanged. Wrappers are constructed at replay and are not represented as having existed at original execution. |
| 10 | Request authentication | Companion, verification-receipt paragraph; REQUEST_CONTRACT65.md | Authentication and trusted storage remain outside the mathematical checker. A digest does not authenticate the request source. |
| 11 | Hybrid routing | Main, Section 9.4 | The hybrid is the tested routing policy, not a universally optimal router. The adversarial outcomes and their complete denominators are unchanged. |
| 12 | Placement of implementation detail | Main, code-and-data paragraph; companion, EC.11 | The main article remains centered on the representation and complexity frontier. The receipt clarification is explained primarily in the companion. |
| optional | Unknown legacy extension metadata | Companion, verification-receipt paragraph; tests66.py | Only explicitly returned mathematical conclusions are certified. Unreported extension metadata is not endorsed. Exact request/envelope schemas and all existing checkers remain unchanged; new tests document their existing behavior. |

## Interpretation of a returned receipt

Read `status`, the reported objective bound(s), `tolerance_met`, and the reported binding/transfer fields according to their documented proof class. `PASS` alone is not a statement of target attainment, original on-time completion, authenticated provenance, runtime configuration, or editorial acceptance. `PASS_LOWER_ONLY` has no certified upper bound. Content hashes identify content, not the identity or authority of its supplier. Runtime and original target outcomes still require the frozen execution record; new replay does not backdate that record.

The exact request and envelope schemas reject unknown fields. Low-level legacy certificate bodies are not uniformly closed schemas. An unknown extension field inside such a body is not certified merely because the recognized mathematical proof passes. Consumers must use the checker-produced receipt, not merge unverified extension claims into it and present the combination as checker output. This is an interpretation of the existing interface, not a new authentication protocol or schema version.

## New regression evidence

`tests66.py` selects the smallest archived proof of each of the six supported classes, validates each baseline, and inserts nonmathematical extension claims into low-level certificate bodies. It checks that all mathematical receipt fields are unchanged and do not contain those claims. The comparison excludes only the checker's per-execution `seconds` diagnostic, which is not a mathematical conclusion. The same extension keys are rejected in the exact request, embedded request and envelope. The test also preserves numerical lower-only semantics and checks unknown nested tariff metadata. These are documentation-regression checks, not new optimization observations or a universal fuzzing guarantee.

## Preservation

Every entry of the 7,080-file R65 manifest resolves to `archive/r65/<path>` if that file was changed and to its original relative path otherwise. Original root readers, response and manifest are retained. The current main article and companion contain all accepted mathematical environments and tables, not merely archival copies. All existing `code/`, `evidence/`, `generated/`, `sections/` and `results/` files retain their R65 bytes; new execution evidence is confined to `results/r66/`. The current package verifier checks both preservation and complete delivered-file coverage.
