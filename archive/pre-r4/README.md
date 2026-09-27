# NDU: A Generalization of Fixed-Preference Reinforcement Learning

Public research repository for the NDU Operations Research manuscript and its computational reproducibility bundle.

## Contents

- `main.pdf`: the anonymous manuscript PDF.
- `main.tex`, `main.bib`, `main.bbl`, `informs3.cls`, and `ormsv080.bst`: source files needed to rebuild the manuscript.
- `reproducibility/`: packaged data, audit scripts, manifests, and the lightweight checker.
- `artifact/`: release-package validation scripts and their packaged results.
- `supplemental/`: convenience copies of root-level figures and compact summary tables from the source folder.
- `release/NDU_RL_OR.zip`: the exact self-contained submission bundle used as the canonical release artifact, with its SHA256 file.

## Lightweight validation

From the repository root:

```bash
python3 reproducibility/check_ndu_reproducibility.py
```

The packaged release currently passes 2,988 checks with zero failures. The checker validates the supplied files and derived evidence; it does not retrain the full models or rerun the expensive optimizers.

The full and partial regeneration commands, dependency notes, and interpretation boundaries are documented in [`reproducibility/README.md`](reproducibility/README.md).

## Release scope

The repository is curated from the source directory's self-contained submission package. Local virtual environments, Python caches, historical draft extractions, build intermediates, backups, and working-memory notes are intentionally omitted from the public repository.

