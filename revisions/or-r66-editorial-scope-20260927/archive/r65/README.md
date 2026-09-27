# NDU — Operations Research revision R65

**Finite-Catalog Resource Allocation: A Tariff-Sensitive Complexity Frontier**

This complete revision responds to the R64 independent referee report. Read `main.pdf`, `electronic_companion.pdf`, and `RESPONSE_TO_REFEREES.pdf`. Their standalone LaTeX sources are included. Current revision entry points end in `65.py`; older publication scripts are preserved historical material, not current instructions.

## Request-level certificate contract

`code/binding65.py` requires an externally supplied request with the physical specification, exact tolerance, mathematical certificate class, configured exception guard, and schema version. The envelope and its digest do not replace this external trust anchor. Robust proofs must use that tolerance for minimum-allowance projection; tariff guards must match the request and cover the actual modal exception count. The modal tie-rule string is validated.

The robust checker independently validates both policies, requires the same book and equal gross payoff, and checks the exact transferred lower formula. Equally good alternative fixed-book policies remain admissible. A feasible but deliberately degraded same-book policy is rejected. `REQUEST_CONTRACT65.md` documents the precise schema and trust boundary. `REVIEW_RESPONSE_MAP65.json` maps every required referee item to its correction and evidence.

`binding63.verify_bound` and low-level mathematical checkers retain their model-only meaning. Their `PASS` is **not** a request-level certificate. Current request acceptance requires `binding65.verify_request(envelope, external_request)`. The request-bound producer supports the tariff and robust-tariff classes; the request verifier also accepts the retained price, enumeration, deficit, and numerical-lower-only classes. Numerical upper bounds are never promoted to rational proofs.

## Reproduce

The remote qualification uses Python 3.13.5 and the pinned packages in `requirements.txt`. PDF compilation uses `pdflatex`, newtx, and the packages declared in the readers. The workflow records the actual TeX and Python installation.

```sh
python -m pip install -r requirements.txt
python qualify65.py
python publish65.py
python verify65.py --replay-output /tmp/ndu-r65-fresh-replay
```

`qualify65.py` reconstructs readers from archived R64 sources, freezes current sources, executes request and retained semantic/structural regressions, compiles all readers, and replays all frozen requests. These commands modify only current results and generated readers; reseal afterward. `verify65.py` checks a sealed package without writing inside it. Its optional fresh replay output must be outside the package.

For a new tariff or robust request:

```sh
python code/produce65.py request.json certificate.json
python code/binding65.py certificate.json request.json --output receipt.json
```

For an unchanged historical proof, `--legacy` creates a binding envelope **at replay time**. It does not assert that this envelope existed at original execution. The external request must still be supplied; it must never be reconstructed from the untrusted certificate under examination. `code/replay65.py` derives it from frozen cases, immutable execution records, and the frozen hybrid guard rule.

## Evidence and limits

`results/r65/REQUEST_TESTS65.json` records 66 valid request checks and 25 rejected adversaries, including the two coordinated R64 referee witnesses accepted by the archived checker. Complete witnesses and mutations are retained. The prior semantic suite again validates 577 certificates and 288 exhaustive projection comparisons, rejecting its ten original adversaries. Structural suites and the independently enumerated 48-case root diagnostic remain checked.

`results/r65/replay/` contains every one of the 405 frozen requests: 342 rational two-sided proofs, 47 numerical-solver lower policies, and 16 no-certificate requests. All 389 available proofs are request-bound, including all 42 robust proofs with the exact transfer formula. The 16 equivalent but byte-different physical serializations remain recorded. The 45 later-successful checks retain their original failed/incomplete status. Parallel integrity replay is not a replacement for the original timing study.

The projection-quality table and its exact/interval regret bounds, original times, costs, unsuccessful cases, and limitations are unchanged. This is an optimization-theory contribution with constructed computational evidence, not field adoption evidence. A verified guard certifies request agreement, not runtime attestation; an exact-head receipt certifies delivered artifacts and executed checks, not editorial acceptance.

## Preservation and publication

`archive/r64/` contains the previous root readers, mutable sources, and manifest. For every one of the **6,992** R64 manifest entries, `verify65.py` first resolves `archive/r64/<path>` and otherwise the unchanged current `<path>`, and verifies its original hash. The older archives and all historical evidence are preserved. All 36 mathematical environments in the main paper and 42 in the companion (theorems, propositions, lemmas, corollaries, and proofs) are checked byte-for-byte against R64. No scientific result is removed.

`PROVENANCE65.json` pins the reviewed author commit and governing report commit/blob. Current sources, command logs, readers, and every delivered file are bound by `SOURCE_FREEZE65.json`, `QUALIFICATION65.json`, and `PACKAGE_MANIFEST.json`. The publisher creates the complete new revision on its own branch; a separate read-only check of the actual published commit and fresh full replay produce an external exact-head receipt. Main, review, and previous revision branches remain unchanged.
