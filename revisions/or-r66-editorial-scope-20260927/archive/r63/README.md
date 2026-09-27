# NDU — Operations Research R63

Start with `main.pdf`, `electronic_companion.pdf`, and `RESPONSE_TO_REFEREES.pdf`.
The main manuscript is 28 PDF pages (26 excluding references); the companion is
28 pages and the response is 5 pages. The text-only abstract has 172 words.

## Scientific revision

The exact selected-boundary representation, original-model W[1] reduction,
exception-parameter tariff theorem, centered resource-deficit guarantee, and
same-book price-support theorem are retained. New material proves original-policy
fee-perturbation bounds and an optimal absolute-distortion sparse-exception
projection, computes actual command-book switches, reports the expanded frozen
405-request study, and adds a 48-case exhaustive root-support diagnostic.

## Read-only verification

Python 3.13 is the declared runtime. The exact proof checkers require the standard
library; installing the pinned `requirements.txt` also enables PDF inspection,
figure reconstruction and the numerical solver. Run from this directory:

```sh
python verify63.py
python code/replay63.py evidence/r61 /tmp/ndu-r63-independent-replay
```

The second command rechecks all 389 existing historical certificates against
external frozen inputs without modifying historical timing or failure outcomes.
It checks 342 rational two-sided proofs and 47 numerical-solver lower policies.
Sixteen of 405 requests have no certificate; numerical upper bounds are not
rational certificates. Sixteen certificate inputs use equivalent rational byte
encodings. Forty-five proofs previously failed or lacked a completed check;
later replay does not reclassify these as original on-time successes.

## Rebuild or rerun in a copy

To preserve the delivered execution record, use a fresh copy for reruns:

```sh
python code/tests60.py --output results/STRUCTURAL60_REPLAY.json
python code/tests61.py --output results/STRUCTURAL61_REPLAY.json
python code/tests63.py
python code/support63.py
python build_revision.py --r60 evidence/r60 --r61 evidence/r61
python compile63.py
```

Install a TeX distribution containing pdfLaTeX, newtx, natbib, geometry,
xr-hyper and booktabs before compilation. Cross-reference-only auxiliary files
avoid importing duplicate bibliographic definitions. `compile63.py` makes three
passes and rejects unresolved references. Timings in the new root diagnostic are
machine-specific; exact inputs, hulls, policies and mathematical certificates are
rechecked separately. The diagnostic source and all current Python modules are
hashed before its execution.

## Provenance and preserved content

`PROVENANCE63.json` pins the reviewed R60 manuscript, R60 referee report, and
R61 author-only parent. `CONTENT_MAP.md` explains every relocation. `archive/r60/`
contains byte-identical reviewed readers and sources; `evidence/r60/` contains
the complete earlier flat source/data package. `evidence/r61/` contains unchanged
execution sources, input freeze, all row records, and all existing proofs.
`results/` contains this revision's independent replay, exact regressions,
root-support inputs/proofs/records, and build checks.

`PACKAGE_MANIFEST.json` hashes every delivered file except itself and disposable
build caches. The GitHub publication validates the exact generated commit and
publishes its SHA-bound receipt as a workflow artifact/commit status, avoiding a
self-referential file-to-containing-commit hash. The study is constructed, not
field-calibrated. No theorem or empirical result asserts universal method-routing
superiority, journal acceptance, or that verification is free.
