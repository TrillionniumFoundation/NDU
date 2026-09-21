# NDU — Operations Research revision R4

**Active manuscript:** `main.tex` / `main.pdf`  
**Electronic companion:** `electronic_companion.tex` / `electronic_companion.pdf`  
**Referee response:** `revisions/or-r4-20260920/RESPONSE_TO_REFEREE.md`

This branch contains a new scientific manuscript, executed experiments, and proofs responding to `reviews/operation_research_referee_report_r4_2026-09-20.md` at commit `a91b707883b2408de58d9392e4fc546e08a00881`. It is not a protocol-only revision. The root paper is now **Neural Differential Utility: Endogenous Service Contracts and Certified Dynamic Optimization**.

The externally priced inventory-contract model is canonical. Its premium, liability, maintenance, adjustment, demand, and transition parameters are the unchanged R2 protocol. New results include a dynamic monotonicity theorem, exact envelope reduction, an O(n^-2) contract-discretization bound without global concavity, constructive C2 neural critics with uniform error bounds, and a boundary-complete stopped-diffusion certificate. Expanded-action control represents the joint problem exactly. Net reward, physical cost, and fill are reported separately.

## Reproduce

Python 3.11 or newer, NumPy and SciPy, and a LaTeX installation with the packages listed in the source are required. The recorded execution used Python 3.13.5, NumPy 2.3.5, and SciPy 1.17.0. No external dataset or network is needed once dependencies are installed.

```sh
python -m pip install -r revisions/or-r4-20260920/requirements.txt
python revisions/or-r4-20260920/execute.py
python revisions/or-r4-20260920/make_tables.py
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error electronic_companion.tex
pdflatex -interaction=nonstopmode -halt-on-error electronic_companion.tex
```

The executor checks the frozen protocol's exact SHA-256, performs integer-scaled DP and independent Fraction-based recomputation for all five methods, tests policy ties and monotonicity, and writes the complete deterministic and seeded numerical results. `results/sha256.json` records output integrity, not a scientific tolerance. Runtime fields and floating-point least-squares last bits can vary by environment; rational results must agree exactly.

`LOCAL_EXECUTION.json` and `local-execution-sha256.json` retain the first executed record and its output fingerprints. `CI_REPLAY.json` records the independent runner replay when published. That replay requires seven exact-result files to match the local record byte-for-byte and requires the generated manuscript tables to remain unchanged. The workflows only write this isolated revision branch.

## Principal executed results

Joint and expanded-action DP agree exactly at every state. Joint minus frozen net reward is 0.944747060878850; frozen minus joint physical cost is 0.213203951173630. Fill falls from 0.925925926 to 0.882108861. The physical oracle remains better on physical cost. All five methods, all 64 simulation batches, and all conditioning batches are retained.

The 160-interval grid gives a continuous-contract value enclosure of approximately [-4.99278573, -4.99260152]. This is for the same stock set, not a stock-discretization or diffusion-limit guarantee. Constructively compiled smooth critics give an additional uniform grid-policy-loss bound down to 1.18419e-6; their exact primary-grid policies happen to remain optimal. The identical-data least-squares study finds direct-P / inferred-P parity, not an invented learning advantage.

## Historical preservation

`archive/pre-r4/` is the complete Git tree of the reviewed commit, tree SHA `a34671dee3769cbc43d70ed6ba3c70badb8f3348`. It preserves every historical manuscript, proof, PDF, bibliography, figure, result, script, manifest, review, and release file byte-for-byte. The old root `main.tex` blob is `2569eee2eb7f80f0a5b31ed07be75d5da9e6a0d3`; its PDF blob is `3ed6d3446ad5eafe4f99e8279c28d37ae3a91068`.

The archive is not the current submission. EC.5 and the referee response map old claims to corrected proofs and retained diagnostics. Historical large-neural results have not been rerun or reclassified as uniform HJB certificates. No new large-neural training, field experiment, or external acceptance decision is claimed.
