# Derivation provenance and reading map

## Baseline

The R30 local branch is based on the exact R29 scientific commit `51552e4198f09b82c764956b92d7b1ee2ad57aff`, tree `2354d7cfc9211ddea586ba69d5e45b4e20e9e56b`. It answers the separate price-state review commit `d1f7f977132e46ac9ca582a1d78f5219365509c8`. The complete source archive was obtained from GitHub Actions artifact 10738995323; rebuilding its Git tree matched the upstream tree exactly. No unrelated repository or manuscript branch was used as a write target.

## Historical mathematics actually used

| Source, retained unchanged | Use in R30 | Current location |
|---|---|---|
| `revisions/or-r29-price-state-20260923/price_main.tex`, `price_solver.py`, `verify.py` | Finite scalar payment response, cap reflection, old exact examples and independent whole-curve verifier | Theorem 3.1; new coefficient-event implementation in `quotient.py`; 35 exact regression instances |
| `revisions/or-r29-price-state-20260923/memory_main.tex`, `memory_frontier.py` | Original three-date necessary-memory family and equal-weight quadratic loss | Theorems 4.1–4.2 generalize behavior and heterogeneous frontier; the old eight-branch values are exactly retained |
| `revisions/or-r29-price-state-20260923/shared_main.tex`, `table_comparator.py`, `oracle_check.py` | One globally optimized shared table and the fixed-release oracle | Propositions 5.1–5.2; tied-bound proof and tests in `corridor_oracle.py` |
| `revisions/or-r29-price-state-20260923/research.py`, `results/evidence.json` | Rational Markov graph generator and inherited test/certificate corpus | New markov/bounded scale cases and complete 35-instance regression |
| `revisions/or-r29-price-state-20260923/inherited_mathematics.tex` | Full general accepted-service, release, sensitivity, promise-state and certificate mathematics | Preserved R29 main PDF/source in `predecessor/`, plus unchanged source file |
| `revisions/or-r29-price-state-20260923/predecessor/main.tex` and companion | Prior general switching and acceptance proofs | Retained R28 originals and all their included sources |
| R26 continuous-state and R28 shared-table bridge sources | Distinction between sufficient states, approximation envelopes and optimized information restrictions | Preserved supplementary theory; not assumed as an unproved premise for scalar finite-price closure |
| R24–R29 deployment/governance result directories and R29 `retained_evidence.pdf` | Auditable cache/certificate results, including adverse strict-tolerance refresh evidence | Retained without new positive performance attribution; 83/84 strict queries refreshed remains explicit |

## New derivation dependencies

Proposition 2.1 is a direct change of variables. EC.1 identifies the lower-shifted laminar rank and exact-total truncation. Theorem 3.1 proves the occurrence quotient before invoking graph recursion. Theorem 3.3 uses direct coefficient sources and acyclic path denominators, not numerical measurements. Theorem 4.1 uses future-action equivalence and strict concavity, not the special renewal example. Theorem 4.2 derives cell loss for heterogeneous rewards/costs and proves ordered reassignment; Proposition 4.3 differentiates that loss along a fixed-mean cap-dispersion path. Proposition 5.2 splits original endpoint normals and applies weak duality to arbitrary new feasible policies.

## No-deletion rule

All 1,540 inherited files are checked against `INHERITED_SHA256.json`. Six root reader entry points may change: main source/PDF, companion source/PDF, README, and submission checklist. Each original has a byte-identical copy in `predecessor/`. Every other inherited path must remain byte-identical. `validate_final.py` fails on an unexpected change, deletion, or missing original. Moving emphasis out of the main journal article therefore does not erase a theorem, proof, result file, or earlier manuscript.
