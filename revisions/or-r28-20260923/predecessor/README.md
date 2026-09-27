# Accepted Service Adaptation — Operations Research R27

**Current revision branch:** `revision/ndu-operations-research-r27-20260923`  
**Scientific base:** R26 `38f99a5b46d8cfe4f1197fc869735d5f798c499a`  
**Purpose:** a new author/referee revision responding to both latest R24 reports. This repository delivery is not a journal submission or an assertion of acceptance.

## Read the revision

| Document | Location |
|---|---|
| Current manuscript | [main.pdf](main.pdf) · [LaTeX](main.tex) |
| Current electronic companion | [electronic_companion.pdf](electronic_companion.pdf) · [LaTeX](electronic_companion.tex) |
| Response to both latest reports | [R27 response](revisions/or-r27-20260923/RESPONSE_TO_REFEREES.md) |
| Exact build and preservation results | [Build report](revisions/or-r27-20260923/BUILD_REPORT.md) |
| Final source/PDF/evidence hashes | [Manifest](revisions/or-r27-20260923/MANIFEST.json) |
| New rational verification | [Replay results](revisions/or-r27-20260923/results/replay.json) |
| Current submission-format checklist | [Checklist](NDU_OR_submission_checklist.md) |

The theorem chain is: optimized restriction release and continuation/friction rents (Sections 4–5); sufficient promised state and certified continuous implementation (Section 6); implemented gains and optimized-comparator certification (Section 7). The R24 coordinates are retained as a lemma, not the sole scientific conclusion.

## New in R27

**Theorem 7.3** retains jointly changing rewards, continuation matrices and budgets, payment/information equalities, and switching friction in a normalized-price cache. It gives a globally valid comparator upper bound, an exact four-term gap decomposition, and a quadratic reuse loss under an exact-anchor, retained-priced-face condition. A degenerate exact example demonstrates why the local condition cannot be discarded.

**Corollary 7.4** gives a uniform economic-gain certificate over an affine parameter polytope. Correctly ordered cell/anchor/vertex extrema preserve coefficient correlations; subdivision and additional cached prices improve the certificate monotonically. An exact positive-gain example and an invalid-minimax counterexample are independently checked.

**New evidence** consists of 24 off-ray parameter queries and 72 newly generated optimization proposals, separately checked with rational arithmetic. The same frozen historical anchor prices produce tighter upper bounds than the historical outer comparator on all 24 new queries, with positive implemented-gain certificates in all 24. A separate 56-query panel evaluates inherited radius records; it is not relabeled as newly generated optimization data. All initial work, offline quality checks, and the absence of any measured end-to-end speedup claim are explicit.

New proofs and the complete experimental specification are in [EC.11 source](revisions/or-r27-20260923/correlated_ec.tex). The main statement is [here](revisions/or-r27-20260923/correlated_main.tex).

## Reproduce or evaluate a query

The independent checker needs only Python's standard library:

```bash
python -S revisions/or-r27-20260923/replay.py --check
python -S revisions/or-r27-20260923/make_tables.py --check
python -S revisions/or-r26-20260923/replay.py --check
python -S revisions/or-r25-20260923/replay.py --check
python -S revisions/or-r24-20260923/replay.py --check
```

A query uses cached prices, not a new optimizer or a query optimizer label:

```bash
python -S revisions/or-r27-20260923/query_cache.py \
  --context-id 0 --rho 1/8 --theta -3 4 5
```

The three integer direction arguments are divided by eight. This interface evaluates the explicitly designed family; a comparator upper bound alone is not a positive economic-gain certificate.

To regenerate the new numerical proposals and their exact audit, install the pinned dependencies in `revisions/or-r27-20260923/requirements.txt`, use a C compiler, and run:

```bash
python revisions/or-r27-20260923/propose.py
python -S revisions/or-r27-20260923/replay.py
python -S revisions/or-r27-20260923/make_tables.py
```

Numerical proposals and timings can change with the execution platform; the independent rational checks, not an optimizer success label, determine acceptance. The publication workflow records its actual execution provenance.

For the PDFs, install LaTeX with `newtx`, `endfloat`, and the packages declared by the sources. Then run `bash revisions/or-r27-20260923/build.sh`. After inherited replays are recorded in the R27 results directory, run `check_package.py`, `check_package.py --manifest`, and `check_package.py --verify-manifest`. The final-SHA workflow checks a fresh checkout of the published scientific commit.

## Reports and preservation

Both latest reports are retained unchanged:

- [Ordinary R24 report](reviews/operation_research_referee_report_r24_2026-09-23.md), review SHA `9080e29443191f9bb415ab0a213af446d4ce3be3`.
- [Independent R24 report](reviews/operation_research_referee_report_r24_independent_2026-09-23.md), review SHA `ded3e34349631cd6dc7a4aa35d58a9d248c77d47`.

The complete R26 current-root source/PDF/navigation files are copied byte for byte into [the R27 predecessor directory](revisions/or-r27-20260923/predecessor/). Every inherited repository file is pinned in `INHERITED_SHA256.json`; only six current root documents are revised. All expanded R26 mathematical statements and proofs remain in the current formal documents. R25/R24 and older derivations, raw data, code, learned-method failures, and both computational/historical root supplements retain their original contents and paths.

The scientific ancestors are R24 `63bbb843e1bbe7cac2170dc7d317d4cf18bb2bb8`, R25 `7f3f12c9d412b45a570725dc9b61203d64da5e41`, and R26 `38f99a5b46d8cfe4f1197fc869735d5f798c499a`. Inherited continuous-state results and unfavorable learning timings are not presented as fresh R27 experiments. No calibrated field uncertainty, hidden-information mechanism, unconditional quadratic cache rate, or unmeasured learning speed advantage is claimed.
