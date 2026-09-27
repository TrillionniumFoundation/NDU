# Operations Research revision R31

This directory is the self-contained scientific text package for **Accepted Service Adaptation: Tight Parametric Quotients and Minimal Additional Writable Memory**.

R31 answers `reviews/operation_research_referee_report_r30_independent_2026-09-23.md`. It is built on top of the fully preserved R30 scientific revision and does not delete the broader switching, sensitivity, continuous-state, cache, deployment, or governance results.

## R31 scientific changes

- residual-priority audit against parametric quadratic optimization, polymatroid sensitivity, state/model minimization, and dynamic-contract policy graphs;
- matching lower bounds: a rational chain has exactly (2N) global response knots and (N^2+2N) stored affine response segments;
- coefficient-event bit theorem explicitly charges exact sorting, comparisons, rational arithmetic, and reduction;
- reached price system is stated as a deterministic output transducer before classical behavioral minimization is applied;
- memory accounting is separated into additional writable alphabet (K_*), combined reached states (C_*), and read-only representation/precision;
- historical renewal construction is promoted to an explicit (K_*=Theta(N)) tightness corollary;
- the outside-option comparative static is stated exactly for ordered mean-preserving radial spreads;
- computational claims are aligned with the residual representation theorem rather than with nonmemoized-tree timing.

## Reader files

- `main.tex` and `main.pdf` at repository root: R31 journal manuscript;
- `electronic_companion.tex` and `electronic_companion.pdf`: R31 electronic companion;
- `RESPONSE_TO_REFEREES.md`: point-by-point response;
- `DERIVATION_PROVENANCE.md`: mathematical and branch provenance;
- `LITERATURE_AUDIT.md`: residual-priority audit;
- `NOVELTY_MATRIX.md`: inherited/new boundary;
- `tightness_check.py`: independent exact checker for the new lower-bound family.

The unchanged R30 computational implementation remains the executable baseline for the quotient, machine, frontier, comparator, and certificate tests. R31 adds mathematics and editorial positioning without rewriting those validated algorithms.
