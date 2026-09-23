# R30 revision package

This directory contains the Operations Research R30 revision addressing the latest R29 price-state referee report.

## Contents
- theorem/source modules used by the root `main.tex` and `electronic_companion.tex`;
- `RESPONSE_TO_REFEREES.md/.tex/.pdf`;
- exact Python implementation and independent audit scripts;
- literature, derivation, novelty, preservation, and validation notes;
- aggregate computational results under `results/`;
- `r30_text_source.tar.gz` and `r30_aggregate_results.tar.gz` as compact transport copies of the core review materials;
- `predecessor/` copies of the R29 manuscript entry points.

The revised PDFs, LaTeX modules, response, and implementation files are byte-identical to local revision commit `55baedb835bc5573593e1234c6ea8477b3d7827c`. Large per-instance certificate traces are reproducible from `experiments.py` and are inventoried in `OMITTED_REGENERABLE_CERTIFICATES.md`; they are omitted from this remote connector publication only to avoid transferring roughly 180 MB of redundant generated evidence through the GitHub contents interface.

No claim is made here that a remote CI run has executed.
