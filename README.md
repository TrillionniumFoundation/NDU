# NDU — Operations Research revision R31

Current manuscript: **Accepted Service Adaptation: Tight Parametric Quotients and Minimal Additional Writable Memory**.

This branch is the R31 revision responding to the independent R30 referee report. It branches directly from `review/operation-research-r30-independent-harsh-20260923`, so the answered report is preserved in ancestry. `main` and unrelated manuscript branches are untouched.

## Review files

- `main.tex` / `main.pdf`: R31 Operations Research manuscript.
- `electronic_companion.tex` / `electronic_companion.pdf`: R31 electronic companion.
- `revisions/or-r31-tightness-minimal-machine-20260923/RESPONSE_TO_REFEREES.md`: point-by-point response.
- `revisions/or-r31-tightness-minimal-machine-20260923/LITERATURE_AUDIT.md`: residual priority audit.
- `revisions/or-r31-tightness-minimal-machine-20260923/DERIVATION_PROVENANCE.md`: derivation and preservation map.
- `revisions/or-r31-tightness-minimal-machine-20260923/NOVELTY_MATRIX.md`: precise inherited/new boundary.
- `revisions/or-r31-tightness-minimal-machine-20260923/tightness_check.py`: exact checker for the matching response-size lower-bound family.

R30 and all earlier derivation/evidence directories remain preserved. R31 does not use deletion or claim contraction to answer the referee; it adds the requested priority comparisons, matching complexity lower bounds, explicit machine-minimization framing, and architecture-conditional memory accounting.

A branch-specific GitHub Actions workflow rebuilds the two reader PDFs and records source/build checks on the remote branch.
