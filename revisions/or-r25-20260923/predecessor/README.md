# Accepted Service Adaptation — Operations Research R24

**Accepted Service Adaptation: Continuation Prices, Transfer Coordinates, and Certified Gains**

Revision: September 23, 2026. Branch: `revision/ndu-operations-research-r24-20260923`.

[Main manuscript](main.pdf) · [complete main source](main.tex) · [formal electronic companion](electronic_companion.pdf) · [companion source](electronic_companion.tex) · [computational record](computational_supplement.pdf).

[Point-by-point response](revisions/or-r24-20260923/RESPONSE_TO_REFEREE.md) · [preservation map](revisions/or-r24-20260923/PRESERVATION_MAP.md) · [claim/evidence ledger](revisions/or-r24-20260923/CLAIM_EVIDENCE.md) · [literature boundary](revisions/or-r24-20260923/LITERATURE_MAP.md) · [reproduction guide](revisions/or-r24-20260923/README.md).

## Review target and substantive revision

R24 responds to the latest completed R23 referee report at `685fdc4d4f1823c6930bd6ccdfbc66822043bf9e`, reviewing the paper at `b4165155612fea340a8832bbe7a8b13fe2b9259b`. The new branch inherits the report and all historical derivations. No other manuscript branch is changed.

The new benchmark-relative continuation-transfer theorem permits nonconstant and boundary restricted contracts with unused participation slack. It parametrizes the entire stated positive-payment accepted class, represents restricted equalities exactly, and gives the exact quadratic expansion formula or a comparator-error-charged lower certificate. The worked optimized time-only example has restricted value **5/24**, full accepted value **21/64**, and exact expansion **23/192**. Its negative relative flow demonstrates why cap-matching nonnegative coordinates cannot simply be applied around a slack benchmark. The proof is supported by 64 exact rational tree tests.

The paper's organizing contribution is accepted-control structure and implemented economic gain certification. All neural, direct-price, face, scalar and full-polyhedron results remain. The robust implication is explicitly a certification lemma, not a claim to invent generic robustness or duality.

## New executed evidence

The interior diagnostic contains **768 models and 1,536 independently certified comparator brackets**. Each model separately reoptimizes the true accepted time-only class and the common outer class. At radius 0.25, mean total certificate slack is **0.096102**, comprising **0.075207** outer-set relaxation and **0.020896** interpolation. The maximum comparator interval width is **3.839e-08**; failed solves: **0**. These are designed-model diagnostics, not field-calibrated coverage.

The repeated-query study executes **1728 pipelines**, with 64 paid optimizer labels for each of three configurations, 32 held-out contexts, three repetitions, both accuracy targets and all three methods. It records individual fit/setup/storage costs, prediction, solve, audit, polishing, and every fallback phase. Failed pipelines: **0**. Finite observed break-even cases against lifted continuation: **0** in this study; this is an observed result, not a universal impossibility statement. Paired resampling intervals are descriptive for fixed fits, with serial-dependence sensitivity and no retraining-level guarantee.

A separate fresh-host robust accounting study audits **96 complete pointwise certificates and 256 comparator certificates**, including ensemble prediction and all eight comparator solves per independently certified method. It does not splice prediction timings from a new host into archived R23 timings. Candidates can achieve different robust gains, so these costs do not imply matched-quality speed superiority. All **800** original R22 scaling rows and **1152** original R23 robust rows remain and receive explicitly dated retrospective cost/variability analyses.

## Preservation, format, and verification

All **72** predecessor mathematical statement/proof blocks remain in the main-plus-companion pair, with only the documented robust theorem-to-lemma relabeling. Original empirical tables and adverse results are retained. Exact reviewed roots are archived in `predecessor/`; prior revisions and the historical supplement are unchanged.

The formal journal package is the main paper and **one** electronic companion. The computational PDF is a readable code/data-archive record, not an additional formal companion. The manuscript uses anonymous 11-point, one-and-a-half-spaced, one-inch-margin Lengthy formatting, an equation-free introduction, a text-only abstract below 200 words, author-year citations, and tables after references.

[Actual package checks](revisions/or-r24-20260923/results/package_check.json) · [independent rational replay](revisions/or-r24-20260923/results/replay.json) · [manifest](revisions/or-r24-20260923/MANIFEST.json) · [provenance](revisions/or-r24-20260923/PROVENANCE.json).

The publication workflow attaches `ndu-or-r24/final-sha` only after a fresh checkout independently verifies the actual published files. Numerical audits do not establish scientific priority or journal acceptance. Author submission declarations remain for the authors; no submission has been made by this workflow.
