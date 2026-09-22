# Neural Differential Utility — Operations Research revision R12

**Current branch:** `revision/ndu-operations-research-r12-20260922`  
**Title:** Neural Differential Utility: Accepted Adaptive Service Control and Certified Value-Gradient Learning.  
**Date:** September 22, 2026.

This is the complete new revision responding to the R10 report on `review/operation-research-r10-harsh-20260921` (`b3abde1e805f36292f03c7ee65df7ef9298020b0`). It preserves the complete R10 scientific manuscript and the incomplete R11 transport history; main and previous branches are unchanged.

## Read the revision

[Main manuscript](main.pdf) · [Main source](main.tex) · [Current electronic companion](electronic_companion.pdf) · [Historical scientific archive](historical_supplement.pdf)

[Point-by-point referee response](revisions/or-r12-20260922/RESPONSE_TO_REFEREE.md) · [Preservation map](revisions/or-r12-20260922/PRESERVATION.md) · [Typesetting/source checks](revisions/or-r12-20260922/results/package_checks.json) · [Independent numerical verification](revisions/or-r12-20260922/results/verification.json) · [Source/data/PDF manifest](revisions/or-r12-20260922/results/manifest.json)

The historical archive preserves earlier material but is not part of the current journal EC. All essential new proofs are in the main manuscript. The build uses ordinary committed TeX inputs and does not require the old R7 source-preparation step.

## Substantive additions

The full-tree capacitated continuation-balance theorem covers arbitrary feasible outside protocols, boundary and vector tiers, multiple commitments, information equalities, signed coefficients, and absolute switching. On scalar trees, eliminating edge tensions gives cumulative subtree cuts and an exact isotonic critical-friction program. Nonconstant outside protocols can have a bounded optimal-friction interval, rather than necessarily an upper ray. A sharp price–capacity margin gives quantitative accepted-gain bounds and an exact optimum on its stated quadratic subclass.

The same continuation/boundary prices and switching faces connect the structural theorem to full-horizon policy certification and an approximation-to-decision theorem for compatible value-gradient critics. The acceptance-face hypothesis is essential and is not assumed to be known by the implemented actor. Independent validation gives a separate finite-sample certificate for choosing among frozen, complete learning pipelines under stated sampling and range conditions.

The new study contains 48 noncentered graph/tree instances and 432 deployments, with reoptimized service-specific outside tiers and fifteen boundary-inclusive comparators. It measures radial repair, weighted projection, a continuation-feasible tree-flow actor, and actual generation–certification–refinement at matched tolerances. All new deployments satisfy their exact final tolerance and do not underperform the static outside protocol. All forty originally failed 992-coordinate weighted-block actors receive an actually executed classical fallback. The raw failures remain visible.

These runs do not demonstrate a learning speed advantage or a statistically resolved advantage of derivative weighting. The new learning theorems are not described as arbitrary distribution-shift guarantees. All experiments remain synthetic; no field calibration is claimed.

## Reproduce and build

Use Python 3.13 and a TeX Live installation with `newtx`, `natbib`, `xr-hyper`, `endfloat`, AMS packages, and Poppler utilities. Numerical dependencies are pinned.

```sh
python -m pip install -r revisions/or-r12-20260922/requirements.txt
bash revisions/or-r12-20260922/reproduce.sh
bash revisions/or-r12-20260922/build.sh
python revisions/or-r12-20260922/manifest.py
```

Independent replay of committed policies and structural examples:

```sh
python revisions/or-r12-20260922/verify.py
python revisions/or-r12-20260922/structural_checks.py
python revisions/or-r10-20260921/verify.py
```

`verify.py` uses Python fractions and imports neither the optimizer nor NumPy/SciPy. It reconstructs all tested rewards, continuation constraints, boundary prices, and full-horizon residual certificates, including retimed decisions and finite-difference oracle witnesses. Structural LP cross-checks are numerical tests, not substitutes for the analytic proofs. Exact rational examples are recorded separately.

The R12 workflow reproduces, independently checks, compiles, and publishes actual ordinary sources, full result records, and PDFs on this branch only. Hardware-dependent timing observations are identified by the recorded environment; a replay generates new timings rather than claiming to recover the original machine. The source/result manifest binds the published package.
