# NDU — Operations Research revision R6

**Revision R6, September 21, 2026.** New scientific response to the R6 report at review commit `a16435cca2c973331e60908b4c45f505de71e698`.

## Current referee package

- [Manuscript](main.pdf) — [LaTeX source](main.tex): *Neural Differential Utility: Accepted Dynamic Service Contracts and Certified Value-Gradient Learning*.
- [Electronic companion](electronic_companion.pdf) — [source](electronic_companion.tex).
- [Point-by-point response](revisions/or-r6-20260921/RESPONSE_TO_REFEREE.md), [review report](reviews/operation_research_referee_report_r6_2026-09-21.md), and [revision checklist](NDU_OR_submission_checklist.md).
- [Scientific programs and generated evidence](revisions/or-r6-20260921/), including the [exact customer-preserving certificate](revisions/or-r6-20260921/results/exact_service_certificate.json).

The best continuous fixed tier is **0.582110391776**, with reward **-5.870110973047**. An implementable dynamic protocol preserves exactly the customer's utility, discounted fill, and physical cost and increases provider reward by **0.625140311972**. Its independent exact rational Bellman-dual gap is below **8.21e-16**. New material also includes optimized information restrictions, switching/hysteresis rules, comparative statics, nonquadratic envelopes, and actual scalar-critic training on a nonmanufactured operational continuous-review model. Finite-chain learning budgets and continuum verification assumptions are kept distinct.

## Reproduce

From the repository root, install `revisions/or-r6-20260921/requirements.txt` in an isolated environment. For the exact scientific checks on recorded results and both PDF builds:

```sh
bash revisions/or-r6-20260921/build.sh
```

To recompute the experiments (numerical timings can differ across machines):

```sh
python revisions/or-r6-20260921/compute.py all
python revisions/or-r6-20260921/exact_certificate.py
python revisions/or-r6-20260921/envelopes.py
python revisions/or-r6-20260921/continuous_learning.py
python revisions/or-r6-20260921/make_tables.py
bash revisions/or-r6-20260921/build.sh
```

The original recorded results and trained weights are committed. Numerical re-execution is not silently substituted for their provenance. `verify.py` distinguishes exact arithmetic properties from numerical optimization/learning diagnostics.

## Preserved history

The R4 scientific text also appeared unchanged in nominal R5. Its exact root manuscript, companion, README, and old R89 checklist are retained at [archive/pre-r6](archive/pre-r6/). Earlier [pre-R4 history](archive/pre-r4/), [revisions](revisions/), [reviews](reviews/), and historical computational records are preserved. The active companion retains the valid earlier derivations and outcomes, including unfavorable comparators and identical-data conditioning parity. Historical checks are not evidence of an unperformed R6 scientific revision.

This branch is `revision/ndu-operations-research-r6-20260921`; main and the review branches are not overwritten or merged.
