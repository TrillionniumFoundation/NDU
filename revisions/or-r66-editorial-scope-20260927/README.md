# NDU — Operations Research revision R66

**Finite-Catalog Resource Allocation: A Tariff-Sensitive Complexity Frontier**

Read `main.pdf`, `electronic_companion.pdf` and `RESPONSE_TO_REFEREES.pdf`. All three have standalone LaTeX sources. R66 responds to the September 27, 2026 R65 report, which recommends **Accept** with nonblocking editorial comments. A referee recommendation is not represented as a formal journal decision.

## What changed

The main article adds one receipt-scope sentence; the companion explains that only explicitly reported mathematical conclusions are certified and that unreported legacy extension metadata is not endorsed. Content binding is not request authentication, runtime attestation or editorial approval. `EDITORIAL_SCOPE66.md` maps all twelve comments and the optional clarification to their retained or revised locations. `EDITORIAL_DIFF66.patch` exposes the entire reader diff.

No accepted theorem, proof, mathematical display, bibliography, empirical table, optimizer, checker, request schema or historical observation changes. All scientific content remains in the current main article and companion. Existing R65 code and evidence remain byte-identical. The external request API is still `code/binding65.py`, with the exact same schema; `REQUEST_CONTRACT65.md` remains the operative request contract.

## Reproduction

Python 3.13.5 and the versions in `requirements.txt` are used by the qualification workflow. Install the declared TeX packages (including newtx) to compile the readers.

```sh
python -m pip install -r requirements.txt
python qualify66.py
python publish66.py
python verify66.py --replay-output /tmp/ndu-r66-independent-replay
```

`qualify66.py` executes new and inherited regressions, compiles the readers and replays all frozen requests. It writes only new `results/r66/` evidence and current reader PDFs; reseal afterward. `publish66.py` seals the current package. `verify66.py` is read-only; optional fresh replay output must be outside the package. Old numbered builders remain preserved history, not current reproduction entry points. The current readers are direct, complete sources, not references to an unexecuted patch.

For a tariff or robust-tariff request, the accepted interface is unchanged:

```sh
python code/produce65.py request.json certificate.json
python code/binding65.py certificate.json request.json --output receipt.json
```

Supply the external request separately from the submitted proof. `--legacy` creates a request-binding wrapper at replay time; it does not backdate that wrapper. `PASS`, `tolerance_met`, original on-time success and later replay have different meanings. `PASS_LOWER_ONLY` certifies no upper bound. Consumers must not present arbitrary unverified legacy metadata as part of the checker-produced receipt.

## Evidence

`results/r66/SCOPE_TESTS66.json` documents the six-class receipt-scope regression. `results/r66/request/` and `results/r66/semantic/` contain fresh executions of the accepted request/transfer and semantic suites. Structural tests and the independent 48-case root-support enumeration remain checked. `results/r66/replay/` records fresh request-bound replay of all 405 frozen requests: 342 two-sided rational proofs, 47 lower-only proofs, and 16 requests without a certificate. All 389 available certificates, including 42 robust transfer proofs, remain checked. The 45 later-successful checks are not reclassified as original successes.

`results/r66/QUALIFICATION66.json` records actual commands, exit codes and logs. `results/r66/BUILD66.json` records page, abstract, reference and overflow checks. A separate exact-head receipt binds the final Git commit and tree after publication; it is external to that commit to avoid a self-referential hash.

## Preservation

For each of the 7,080 R65 manifest entries, `verify66.py` resolves `archive/r65/<path>` first and otherwise its original relative path, then checks the original SHA-256. Only changed root readers, response, README, content map and manifest need archival copies; existing `code/`, `evidence/`, `generated/`, `sections/` and `results/` entries are unchanged. The mathematical environments, displays, bibliographies and empirical tables are checked directly in the current readers. All earlier derivations and evidence remain included through the inherited preservation maps.

`PROVENANCE66.json` pins the R65 author commit and the exact R65 report commit/path/blob. The revision descends from the author commit, not the review commit. Main, review and prior revision branches are not modified. The full referee report is retained for provenance without treating its recommendation as a publisher decision.
