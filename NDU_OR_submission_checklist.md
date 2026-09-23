# Operations Research submission preparation — R30 remote revision

## Completed on this branch
- R30 main manuscript and electronic companion sources are present and their compiled PDFs are byte-identical to the locally validated revision.
- Point-by-point referee response is present in Markdown, LaTeX, and compiled PDF.
- Core theorem modules, baseline implementations, exact-audit code, build scripts, validation report, literature audit, and aggregate computational outputs are present.
- Latest R29 price-state referee report is preserved in the branch parent commit.
- Prior R29 manuscript entry points are preserved under `revisions/or-r30-quotient-memory-20260923/predecessor/`.
- `main` and unrelated manuscript branches are untouched.

## Evidence boundary
The local full revision includes roughly 180 MB of generated per-instance certificate traces. The remote connector publication does not duplicate those large raw traces. It includes the exact generators, auditors, aggregate result files, and compact result archive; the omission is recorded in `REMOTE_PUBLICATION.md`.

## Not inferred
Author identities/affiliations, ORCIDs, coauthor approval, funding/conflicts, permissions, and journal-submission declarations are not fabricated or marked complete. No remote CI run is claimed unless separately visible in GitHub Actions.
