# Neural Differential Utility — Operations Research R22

**Accepted Service Adaptation with Neural Differential Utility: Continuation Prices and Certified Gains**

Revision: September 23, 2026. Branch: `revision/ndu-operations-research-r22-20260923`.

## Current reviewer entry points

[Main manuscript](main.pdf) · [ordinary complete main source](main.tex) · [electronic companion](electronic_companion.pdf) · [ordinary complete companion source](electronic_companion.tex).

[Point-by-point referee response](revisions/or-r22-20260923/RESPONSE_TO_REFEREE.md) · [preservation map](revisions/or-r22-20260923/PRESERVATION_MAP.md) · [literature/novelty map](revisions/or-r22-20260923/LITERATURE_MAP.md) · [claim/evidence ledger](revisions/or-r22-20260923/CLAIM_EVIDENCE.md) · [reproduction guide](revisions/or-r22-20260923/README.md).

This is the complete R22 review package, not the earlier R20 plan. It responds to the [September 23 R20 report](reviews/operation_research_referee_report_r20_2026-09-23.md), review commit `18381729edf8d15a536ebef16abf6660ee0db48f`. The reviewed plan-only R20 tip was `45553b28f40c92a14895b8b82d8739e608f6d4b1`; its complete manuscript was R19 at `cb4f8644652ebe92f0aac5294baaff898d97f5cf`. Exact original root files are preserved under [revisions/or-r22-20260923/predecessor/](revisions/or-r22-20260923/predecessor/). Earlier revision directories, reviews, historical supplement and other branches are not overwritten.

## Scientific revision

The common target is the certified gain from expanding an already optimized accepted policy class. The full continuation, friction, transfer, resource-price and inexact-response theory is retained. New proofs separate certificate error into box, resource, switching and participation terms, identify a price-repair floor, establish monotone resource/equality-price repair, prove complete dual attainment and a convergent full-price repair without strict feasibility, certify context transport, charge regularization bias, and connect implemented decisions with a reoptimized restricted contract. A theorem-level literature map distinguishes accepted-control consequences from established sensitivity, duality, decision-focused learning, dual prediction and learned warm starts.

The original neural and non-neural results, including adverse comparisons, remain in a dated companion section. New experiments include a structure-aware lifted primal--dual classical continuation baseline, full-polyhedron scaling, frozen deterministic neural and direct-price ensembles, an optimized time-only-amendment comparator, and independent in-distribution/shifted validation with fresh numerical workspaces. Positive gain against an optimized restricted class is not equated with neural acceleration or field validity. All operational primitives are synthetic and known.

## Executed and independently checked evidence

[5,120 matched-cost pipelines](revisions/or-r22-20260923/results/matched_rows.json) include prediction, response, repair, audit, price polishing and actual fallback under identical final tolerances. [Final deterministic validation](revisions/or-r22-20260923/results/validation_summary.json) contains 2,048 IID and 512 shifted contexts for each of two frozen ensembles, with four simultaneous conditional expected-gain bounds against the true optimized restricted value. [Full-class scaling](revisions/or-r22-20260923/results/scaling_summary.json) contains ten geometries, 640 audited training labels and 800 deployment attempts; failures are retained. [Independent rational replay](revisions/or-r22-20260923/results/replay.json) checks 32,416 new policy records, 320 component identities and four rejected invalid controls. [Complete dual-repair checks](revisions/or-r22-20260923/results/complete_dual_checks.json) additionally verify 225 exact optima, 3,600 projected-gradient steps and 450 context transports. The inherited R19 standard-library replay is also rerun without modifying historical inputs.

The lower confidence bounds in the final recorded study are:

| Population | Frozen deterministic rule | Conditional expected-gain lower bound |
|---|---|---:|
| iid | ensemble-tanh-gradient | 1.158492 |
| iid | ensemble-rbf-direct | 1.160880 |
| shift | ensemble-tanh-gradient | 1.386231 |
| shift | ensemble-rbf-direct | 1.401297 |

These are four simultaneous 95% one-sided bounds conditional on the frozen rules, for their respective declared synthetic context laws. The comparator gate itself requires optimization and is not evidence of a speed advantage. The stateful developmental pilot is excluded; [the correction record](revisions/or-r22-20260923/audit_notes/STATE_ISOLATION_CORRECTION.json) identifies the fresh final protocol.

## Format, provenance and verification

The main PDF has 41 pages (38 excluding references); the companion has 37 pages. The 182-word abstract, 11-point text, one-and-a-half spacing, one-inch margins, anonymous title pages, mathematical-notation-free introduction, author-year references and tables after references are checked against the journal's **Lengthy** manuscript format. All current references resolve. Verbatim preservation checks cover 58 original mathematical statements/proofs.

[Package checks](revisions/or-r22-20260923/results/package_check.json) · [manifest](revisions/or-r22-20260923/MANIFEST.json) · [provenance](revisions/or-r22-20260923/PROVENANCE.json) · [submission checklist](NDU_OR_submission_checklist.md).

The workflow attaches `ndu-or-r22/final-sha` to the actual final published commit after independent final-checkout replay, PDF and hash verification. A successful source checkpoint alone is not called a completed revision. Author approval of authorship, conflicts and submission declarations is still required. This branch is a referee-ready research package, not journal acceptance.
