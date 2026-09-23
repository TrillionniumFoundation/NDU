# Accepted Service Adaptation — Operations Research R26

**Current manuscript:** *Accepted Service Adaptation: Continuation Prices, Transfer Coordinates, and Certified Gains*.

R26 responds to both September 23 R24 reports, including the independent report absent from the R25 tree. It builds on the complete R25 scientific tip `7f3f12c9d412b45a570725dc9b61203d64da5e41` and is delivered only on `revision/ndu-operations-research-r26-20260923`. Main and review branches, R25, and previous revision branches are not changed.

## Referee reading order

Read `main.pdf`, then `electronic_companion.pdf`. The response is `revisions/or-r26-20260923/RESPONSE_TO_REFEREES.md`. The optimized restriction-release and comparator-rent results remain Theorem 4.1, Theorem 5.1, and Proposition 5.2. New **Theorem 6.2** gives continuous promised-payment policies and global error bounds; **Proposition 6.3** certifies the value of omitted state. Main Table 1 and EC.10 specify the new continuous-state evidence. All retained R25 hierarchy, radius, cache, and historical timing tables follow it.

The exact examples separate the promise from the inherited tier. The continuous-state study verifies 4,414 feasible anchors and 1,123 recursive price planes across six synthetic models. Its uniform guarantees cover all feasible promises and inherited tiers, not only sampled states. The study makes no learned speedup or matched-time comparison.

## Preservation

R26 `predecessor/` preserves 12 R25 source/PDF/reference/guide files byte for byte. Every R25 mathematical statement/proof environment is retained in the current formal documents. All earlier revision paths and both R24 reports remain available. The R24 predecessor inside R25 and the root computational/historical supplements are unchanged. `ARCHIVE_GUIDE.md`, `PREDECESSOR_SHA256.json`, and `SOURCE_REVIEWS.json` identify lineage and evidence boundaries.

## Replay and regeneration

Independent verification uses only Python's standard library:

```bash
python -S revisions/or-r26-20260923/replay.py --check
python -S revisions/or-r25-20260923/replay.py --check
python -S revisions/or-r24-20260923/replay.py --check
```

Regenerate only the new study and build the current PDFs:

```bash
R=revisions/or-r26-20260923
python -m pip install -r "$R/requirements.txt"
bash "$R/regenerate.sh"
bash "$R/build.sh"
python "$R/check_package.py"
```

`envelope.py` uses numerical LP proposals; `replay.py` checks exact rational continuation feasibility, prices, supports, and whole-domain bounds. No solver status is accepted as a certificate. `MANIFEST.json` pins the complete published source/PDF/evidence package. The publication workflow creates the final scientific commit, checks it out again, and attaches `ndu-or-r26/final-sha` only after independent verification.

The current PDFs follow the Operations Research anonymous, 11-point, one-inch-margin, 1.5-spaced format, with an equation-free introduction and author–year references. This is repository delivery for further review, not submission to the journal or a guarantee of acceptance. The unfavorable historical learned-amortization results remain unchanged.
