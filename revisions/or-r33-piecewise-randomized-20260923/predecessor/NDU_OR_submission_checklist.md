# Operations Research submission preparation — R32

## Scientific closure on this branch

- Latest effective independent R30 referee report remains identified and preserved in branch ancestry.
- R31 theorem-level corrections are retained unchanged: parametric-optimization positioning, machine/model minimization boundary, tight response-size lower bounds, writable-memory tightness, explicit memory accounting, randomized-feasibility convention, and radial-spread scope.
- New main-text priority/scope/tightness table separates classical predecessor principles from the claims specific to this paper.
- New Proposition “Three-layer representation accounting” jointly reports read-only compiler size, fixed-query reached states, additional writable alphabet, and repeated root-query inversion cost.
- Companion concordance maps every major independent-R30 objection to a theorem/section anchor and an explicit non-claim boundary.
- No theorem is weakened, no negative result is removed, and no earlier derivation/evidence directory is deleted.

## Review package

- `main.tex` and `electronic_companion.tex` carry the R32 revision label.
- R32 overlay files are under `revisions/or-r32-priority-complexity-closure-20260923/`.
- R31 scientific source remains under `revisions/or-r31-tightness-minimal-machine-20260923/` and is intentionally reused byte-for-byte where unchanged.

## Validation targets

A fresh build should check:
- main and companion LaTeX compilation;
- cross-document references after the R32 prefix update;
- undefined references/citations;
- table width/overfull boxes for the new closure tables;
- preservation of the R31 theorem labels used by the new synthesis proposition;
- exact tightness checker and the existing R31 computational audits.

## Not inferred

Author identities/affiliations, ORCIDs, coauthor approval, funding/conflicts, permissions, editorial category approval, or journal-system submission status are not fabricated or marked complete.