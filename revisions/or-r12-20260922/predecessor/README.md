# Neural Differential Utility — Operations Research revision R10

Current scientific branch: `revision/ndu-operations-research-r10-20260921`.

**Title:** Neural Differential Utility: Accepted Adaptive Service Control and Certified Value-Gradient Learning.

This is an integrated revision responding to the R9 report at `c4cf05f40feb0eb690f4f0c65a0d6176b3d32b28`, on the R9 predecessor `584296b1a22de455a482c6809f00eda1387b6dab`. Main and previous review/revision branches are unchanged.

## Read the current manuscript

[Main manuscript](main.pdf) ([source](main.tex)), [electronic companion](electronic_companion.pdf) ([source](electronic_companion.tex)), and [historical scientific supplement](historical_supplement.pdf) ([source](historical_supplement.tex)) are the complete reading package. The historical supplement preserves all earlier continuous-time, diffusion, and computational material without presenting it as validation of the new model.

[Point-by-point response](revisions/or-r10-20260921/RESPONSE_TO_REFEREE.md), [preservation map](revisions/or-r10-20260921/PRESERVATION.md), and [build audit](revisions/or-r10-20260921/results/package_validation.json) make the new theorem chain, remaining empirical limitations, and integration explicit.

## Scientific revision

The general formulation now has vector node tiers, joint graph resource costs, explicit information equalities, and all continuation-participation rows. Stock identification handles exogenous occupation weights, constrained quantiles, one-sided derivatives, and a specified vector extension. Standard convex and Bregman tools are credited as standard.

A new complete scalar tree-edge criterion identifies whether a payment-neutral static protocol is globally optimal using primitive marginal reward ratios. A violated edge constructs a continuation-compatible improvement. Curvature bounds quantify its value; absolute switching admits an exact two-review friction threshold. A remaining-payment Bellman state and an exact zero-friction counterexample separate contractual memory from extra demand information.

The exact R7 accepted hierarchy and customer-exit gain are retained and replayed. A new graph-coupled **quartic multistage** task trains compatible nonlinear scalar potentials, uses 720 certified scalar teacher records, and audits 176 complete contingent-plan proposals with 2,640 exact continuation checks. Test instances reach 992 tier coordinates and change graph family, weights, curvature, and horizon. Cached-preconditioned nonlinear solvers, setup cost, repeated end-to-end timings, and paired training-seed uncertainty are disclosed.

All repaired proposals are feasible, but not all learned proposals improve the static comparator. Severe weighted-block shift produces adverse raw results; the static gate prevents negative incremental deployment reward. The paired seed interval includes zero: a reproducible superiority of gradient supervision is **not** claimed. The study is synthetic, not a calibrated field application. These findings are visible in the manuscript and raw records, not deleted or labeled successful transfer.

## Build and replay

With Python 3.11+ and a TeX Live installation containing `newtx`, `endfloat`, `natbib`, `xr-hyper`, and the ordinary AMS packages:

```sh
python -m pip install -r revisions/or-r10-20260921/requirements.txt
bash revisions/or-r10-20260921/reproduce.sh
bash revisions/or-r10-20260921/build.sh
```

Independent verification of the recorded R10 rational results (without running or importing the learner):

```sh
python revisions/or-r10-20260921/verify.py
python revisions/or-r10-20260921/structural_checks.py
python revisions/or-r10-20260921/check_package.py --pdf
```

The R10 `results/` directory and `replayed_r7/` archive contain full rational policies, multipliers, all oracle endpoint records, problem primitives, raw timing observations, and summary files. The R10 workflow builds all three documents, runs both the R7 and R10 scientific checks, and publishes actual ordinary source files and complete records on this branch. Its artifact is a convenience, not the sole archival location. Reproduction updates recorded timings and generated tables for its environment; the commit and manifest identify which run accompanies each PDF. It does not retroactively recover the original R7 timing run.

## Scope and preservation

[Preservation map](revisions/or-r10-20260921/PRESERVATION.md) lists every predecessor input and its new location. No earlier scientific directory is overwritten to replace a theorem or suppress an adverse result. The predecessor root sources are preserved verbatim. Bibliographic entries are retained and a verified convex-optimization reference is added. Private information, endogenous tariff design, and a real-world service calibration remain outside the demonstrated model.
