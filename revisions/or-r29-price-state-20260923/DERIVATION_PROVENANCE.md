# Derivation provenance and no-deletion map

## Frozen baselines

The revision descends from review commit `af01e2c33f85835e550896985b7cb83b3f4b784f`, whose report assesses scientific R28 commit `b53d644be66e9d27bb58cd0f8529aba0c91ec14c`. The review itself is unchanged. Every tracked predecessor file is hashed in `INHERITED_SHA256.json`. The only overwritten baseline paths are the six reader entry points listed in `PRESERVATION.json`; all six have byte-identical copies in `predecessor/`.

## Historical derivations used

- Root R28 `main.tex`, retained verbatim in `predecessor/main.tex`: finite-tree continuation inequalities, accepted balance, subtree transfers, optimized release frontier, comparator-adjusted continuation rents, friction paths, and promised-payment recursion. The entire mathematical block from the value-frontier section through certification is copied into `inherited_mathematics.tex` and placed in the current print appendices.
- Root R28 `electronic_companion.tex`, retained verbatim in `predecessor/electronic_companion.tex`: original detailed proofs remain in the active companion. A new initial methods/proofs section is inserted; original proofs are not replaced by a summary.
- `revisions/or-r26-20260923/continuous_main.tex` and the accompanying continuous-state derivations: retained conditional interpolation/envelope rates distinguish sufficient state from approximation cost. Those rates are not used to prove the new exact finite-price bound.
- `revisions/or-r28-20260923/bridge_main.tex` and `bridge_ec.tex`: the globally shared table, conditional-price normalization, and extensive-form-dual reconstruction supply the starting distinction. The new theorem turns the scalar price relation into an independently constructed threshold. A copy of `bridge_main.tex` clarifies the old representation's name and Benders master; the original is unchanged.
- R24–R27 result/replay directories and the R28 `research.py`, `verify.py`, `governance_main.tex`, `governance_ec.tex`, and their included companion sources: preserved deployment, cache, continuum, and counterexample evidence. They do not supply an unproved performance premise for the new graph algorithm.

## New proof dependency

1. Local strictly concave quadratic reward gives a clipped affine payment response.
2. A scalar additive continuation cap is imposed by raising the inherited price to one crossing threshold; continuity, monotonicity, constant tails, and exact root inversion handle boundary cases.
3. Sums merge existing knots; a cap adds at most one. This gives the global compact-graph response bound without a precomputed tree optimum.
4. Price reflection implies a running maximum, hence finitely many realized memory labels.
5. A binding-cap recombination family forces different service at the same terminal public state. Deriving its cell loss gives the necessary-memory bound and exact optimal grouping frontier.
6. A globally shared zero-release table has public-graph recursion for its payments and a graph-sized objective. A fixed positive-release table changes local intervals and therefore admits the same exact price engine; standard dual sensitivity then supplies a supporting cut.

## Where every predecessor component can be read

| Predecessor component | Current readable location | Unchanged source location |
|---|---|---|
| Model, physical identification, accepted balance/transfers | Main Sections 2–3 and EC | `predecessor/main.tex`, `predecessor/electronic_companion.tex` |
| Release frontier and complete three-node path | Main print Appendix A, original detailed EC proofs | All original revision sources, plus `inherited_mathematics.tex` |
| Comparator-adjusted capacity rents, friction paths and information hierarchy | Main print Appendix B, original EC | Same |
| General promise recursion, continuous envelopes, shared-table bridge and cost design | Main print Appendix C, original EC | Original R26/R28 sources unchanged |
| Reward/correlated comparator certificates, cache governance, adaptive Bernstein certificate | Main print Appendix D and original EC | Original R24–R28 sources unchanged |
| Complete computational narrative, every displayed predecessor table and adverse result | `retained_evidence.pdf` (compiled separately) | `retained_evidence_body.tex` is byte-identical to the full R28 empirical block; all input tables/data unchanged |
| Old introduction, novelty positioning and conclusion | `predecessor/main.pdf` and `.tex` | Byte-identical backup, not misrepresented as current contribution claims |
| Earlier long-form technical/historical supplements | Original root and archive paths | Byte-for-byte unchanged |

`check_package.py` verifies inherited hashes, reader backup hashes, the two unabridged extracted blocks, and source inclusion. Reorganization does not erase the record; old claims that were merely representational are not silently rewritten into the new complexity result.

## Latest-review reconciliation before scientific publication

The R29 report at `1647d416e7a2806d36b1c9972aff0c0b54779912` appeared during this work and was read in full before publication. It evaluates unchanged R28 content on the separate nominal R29 branch. Its original file is preserved at `reviews/operation_research_referee_report_r29_2026-09-23.md`, Git blob `ce85546dfcb30764376e9187d558ce8f1db607a2`. `LATEST_REVIEW.json` and the package checker verify this additional report. The response now answers Sections 1–18 and preserves the full preceding R28 response. The new source receipt is explicitly not treated as the scientific revision; only the final committed manuscripts/evidence and its fresh-checkout status are delivery evidence.

The final source overlay also makes output-directory initialization safe on a clean checkout and clarifies that stored coefficients are rational for rational primitives. It does not change the exact algorithm, the input suite, or any original theorem's hypotheses.
