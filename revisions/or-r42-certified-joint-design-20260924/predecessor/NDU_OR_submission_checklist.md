# Operations Research R39 submission checklist

The PDF/build evidence in `BUILD_VALIDATION.json` is authoritative for page counts, warnings, hashes and execution status. This checklist records scope and format, not an editorial acceptance decision.

| Item | Disposition |
| --- | --- |
| Latest report | R37 independent harsh report, 2026-09-24, review tip 1cf9c8d |
| New branch | revision/ndu-operations-research-r39-robust-quantizer-20260924 |
| Main readers | Root main.tex/main.pdf and electronic_companion.tex/electronic_companion.pdf |
| Format | 11-point Times-family text/math, US Letter, one-inch margins, one-and-a-half spacing |
| Anonymity | Anonymous reader title/header; no author identities added |
| Length | Build requires at most 30 nonreference main pages; companion no longer than main |
| Abstract | Build requires at most 200 words |
| Area | Optimization |
| Literature | Direct Wu, stochastic-rounding, dual-quantization and finite-rate-control comparison |
| New analysis | All-promise exact alphabet; budget-uniform stability; strict nonsaturated interval; promise-allocation reduction |
| Joint implementation cost | Exact finite-catalog recurrence with actual additive selected-level charges |
| Risk | Pre-draw intermediate service explicitly stipulated; catalog result general in branch/catalog sizes and tolerance |
| Proof retention | Thirteen prior proof blocks in focused companion; complete preceding readers archived |
| Verification | New exact tests and unchanged R33–R37 suites executed; finite tests not substituted for proofs |
| Computation provenance | Old scale data retained as old; new catalog data separately timed and labeled |
| Bibliography and labels | Current numbering; build fails on unresolved/multiply-defined references or citations |
| Archive preservation | Full Git checkout checks all prior tracked paths against the review base |
| Referee response | RESPONSE_TO_REFEREES.md/.tex/.pdf with point-by-point coverage |
| Open scope boundary | No claimed global O(mk) algorithm for arbitrary nonsaturated or arbitrary nonadditive representation-cost problems |

Formatting source consulted: the official Operations Research submission guidelines, https://pubsonline.informs.org/page/opre/submission-guidelines (2026-09-24). Submission classification and page compliance do not ensure editorial suitability or acceptance.

- R39: arbitrary-promise stability and independently certified nonsaturated allocation; original R38 source recovered without overwriting transport.
- Final page counts, complete source dependencies, exact test results, and output hashes are validated by BUILD_VALIDATION.json.
