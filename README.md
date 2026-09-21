# Neural Differential Utility — Operations Research revision R7

Current scientific revision: `revision/ndu-operations-research-r7-20260921`.

This revision responds to the [R7 referee report](reviews/operation_research_referee_report_r7_2026-09-21.md) at `31c8d31b8041f19b89dcac8193d0e0dcccbdcbe8`. It builds on scientific revision R6 at `1004079f29ce65e9a8e3157c63d654b28d42f1f6`. The main branch and earlier revision/review branches are not modified.

## Current review sources

[Manuscript source](main.tex), [electronic companion source](electronic_companion.tex), [point-by-point response](revisions/or-r7-20260921/RESPONSE_TO_REFEREE.md), and [preservation map](revisions/or-r7-20260921/PRESERVATION.md) identify the current package. This is a **source-first branch**: compile the sources to obtain the current PDFs. No link here assumes that a root PDF has been committed. Legacy `main.bib` and `main.bbl` are preserved historical files; the current manuscript uses the reference section under the R7 directory.

## Principal new results

The continuous accepted optimum is deterministic and gains **0.6366652716114345** over the optimized continuous static contract, with exactly unchanged customer utility, filled demand, and physical cost. Accepted increments are **0.0008168767827264** for time, **0.616558016063448** for the current regime, and **0.0192903787652605** for the inherited tier. These are rationally verified values, not the older provider-relaxation decomposition.

Allowing the customer to exit at all **3,280** review-history nodes retains a feasible gain of **0.4530787632236716**, with a rational upper gap below **6.95e-7**. A new accepted policy-loss identity and a rational residual certificate support coupled learned deployments with **1,024** tier coordinates. All **288** evaluated decisions pass exact acceptance and certificate replay. The largest learned value–gradient bound is **8.0436e-7 per service**. The comparison includes equal raw-oracle value-only fitting, ten paired seeds, analytic filtering, conjugate gradients, and direct solvers; stronger classical accuracy and inconclusive seed intervals remain visible.

The accepted robustness design has 31 cases, including two infeasible commitments and a zero-gain case. Fine menus, deterministic incumbents, complete multi-tier inaction regions, the original coarse exact certificate, and the full historical evidence are retained with separate scopes.

## Build and reproduce

The build first runs `prepare_sources.py`, which checks the Git blob IDs of the preserved R6 inputs and deterministically assembles their annotated R7 copies. All newly proved R7 sections are tracked as ordinary TeX. With Python 3 and a LaTeX installation containing `newtx`, `natbib`, `xr-hyper`, and the standard AMS packages:

```sh
bash revisions/or-r7-20260921/build.sh
```

The audited local build produces 31-page `main.pdf` and 31-page `electronic_companion.pdf`, with no unresolved references or overfull text boxes. On minimal TeX Live installations, `binhex.tex` is supplied by the plain/generic packages; install them rather than replacing the manuscript's math fonts.

To rerun the R7 experiments and exact certificate checks:

```sh
python -m pip install -r revisions/or-r7-20260921/requirements.txt
bash revisions/or-r7-20260921/reproduce.sh
```

The source checkout includes tracked tables, compact recorded metrics, and hashes for the reviewed run. Full generated policies and diagnostic arrays are written to `revisions/or-r7-20260921/results/` by reproduction. The delivered reproducibility bundle additionally contains those complete generated records and the compiled PDFs. Reproduction writes separate replay tables under `results/replay_tables/` and does not overwrite the tracked paper tables; numerical iterates and wall times can vary by environment. Exact proofs and exact acceptance checks do not use a solver status as a substitute for a certificate.

## Preservation and evidence scope

R6 and earlier scientific directories remain unchanged. The reviewed root manuscript, companion, README, and checklist are copied to `archive/pre-r7/`. The current main paper and companion retain all prior substantive theorem families and reported adverse outcomes; the response explains their placement.

The portfolio experiment is a coupled accepted review/terminal Bellman update, not an arbitrary 1,024-dimensional multistage solution. Its critic is a trained quadratic graph-filter readout, not a new generic architecture. The continuous-rate HJB model remains a separate extension. Rational certificates, floating-point LP diagnostics, sampled historical neural results, and editorial judgments are not interchangeable.
