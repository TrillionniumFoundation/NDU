# Neural Differential Utility — Operations Research R23

**Accepted Service Adaptation with Neural Differential Utility: Continuation Prices and Robust Certified Gains**

Revision: September 23, 2026. Branch: `revision/ndu-operations-research-r23-20260923`.

## Current review package

[Main manuscript](main.pdf) · [complete main source](main.tex) · [electronic companion](electronic_companion.pdf) · [complete companion source](electronic_companion.tex).

[Point-by-point referee response](revisions/or-r23-20260923/RESPONSE_TO_REFEREE.md) · [preservation map](revisions/or-r23-20260923/PRESERVATION_MAP.md) · [literature map](revisions/or-r23-20260923/LITERATURE_MAP.md) · [claim/evidence ledger](revisions/or-r23-20260923/CLAIM_EVIDENCE.md) · [reproduction guide](revisions/or-r23-20260923/README.md).

R23 addresses the September 23 R20 review report at `18381729edf8d15a536ebef16abf6660ee0db48f`. Its scientific base is the complete R22 publication `fef3bad92ab9c74530b530a885bb6f437e8b1c1a`. The reviewed R20 tip was a plan on R19; R23 does not claim that a newer referee has already reviewed R22. Exact R22 root documents are preserved in `revisions/or-r23-20260923/predecessor/`; all earlier revision directories, reviews and historical supplements remain unchanged.

## Scientific addition

The current paper retains the accepted-control, friction, transfer, value-gradient, inexact-response, component-certificate and complete-dual-repair results. It now proves robust accepted gains under **joint objective and participation/capacity coefficient uncertainty**. The gain is measured against the true model-specific reoptimized restricted contract. A common outer comparator class contains the union of those restricted classes; a scalar counterexample shows why separately optimized vertex comparators can miss a stronger interior comparator. The new exact repair preserves root equalities and every uncertain inequality, and explicitly charges its value effect.

The generic robust-counterpart and weak-duality ingredients are identified as classical. The accepted-service consequence, hidden-model comparator distinction and implemented rational certificate are explicit. The uncertainty set is specified rather than field-estimated.

## Newly executed R23 evidence

The predeclared study uses 96 fresh contexts, four uncertainty radii, the same frozen eight-model neural and RBF ensembles, and a classical robust-maximin QP. It records **1,152 protected implementations**, **3,072 vertex comparator upper certificates** and **768 nondeployed nominal diagnostics**. All protected decisions are exactly robust-feasible and all their gain lower certificates are positive in this sample. The independent Python-standard-library replay also checks 2,304 interior certificate mixtures, the scalar counterexample at 1,001 rational parameters, and six rejected invalid controls. Numerical solve failures: **0**; failure and negative-certificate retention is part of the protocol.

At uncertainty radius 0.25:

| Implemented rule | Mean robust gain lower certificate | Minimum certificate |
|---|---:|---:|
| Protected tanh-gradient | 0.808414 | 0.225658 |
| Protected RBF-direct | 0.815943 | 0.278173 |
| Classical robust maximin | 0.848251 | 0.378572 |

These are averages/minima of pointwise, uniformly valid certificates, **not** new population confidence bounds. Both nominal learned rules violate some uncertain restriction in every recorded positive-radius context; their violation magnitudes are retained. None of these unsafe diagnostics is deployed. The classical robust rule remains strongest; no neural speed or accuracy superiority is asserted.

## Preserved evidence and verification

All original unfavorable neural/direct-price comparisons, the complete R22 5,120-pipeline matched-cost study, deterministic IID/shift validation, full-polyhedron scaling and prior exact checks remain. Their original provenance and statistical targets are unchanged. Every predecessor mathematical statement/proof block is preserved verbatim across the current main and companion; only the full global-bridge proof is moved intact to the companion.

The current main and companion use the journal's anonymous 11-point, one-and-a-half-spaced, one-inch-margin Lengthy format, a text-only abstract below 200 words, a notation-free introduction, author-year references and tables after references. Actual page counts, reference resolution and preservation are in [package checks](revisions/or-r23-20260923/results/package_check.json). [Manifest](revisions/or-r23-20260923/MANIFEST.json) · [provenance](revisions/or-r23-20260923/PROVENANCE.json) · [exact replay](revisions/or-r23-20260923/results/replay.json).

The publication workflow attaches `ndu-or-r23/final-sha` only after independent verification of the actual final commit. Author approval of submission declarations is still required; this package is a research revision, not journal acceptance.
