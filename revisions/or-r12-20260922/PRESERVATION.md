# R12 scientific preservation and version map

## Ancestry

The latest reviewed scientific manuscript is R10 at `3f5bc42f0fa053453ca82f8ab3d66b5b46d88372`. The latest report is in review commit `b3abde1e805f36292f03c7ee65df7ef9298020b0`. The new R12 branch starts at `69e1dcf5c4fc6400827463702abb64332c60fc99`, preserving the report and both incomplete R11 transport fragments. Neither fragment is represented as a completed R11 manuscript.

No predecessor scientific directory, old review, or earlier branch is replaced. The active root manuscript/companion/archive and README are revised only on the new branch. Full predecessor root TeX and README are retained under `predecessor/`; the publication workflow also preserves the three inherited R10 PDFs there before building the new PDFs.

## Reading and preservation map

| Predecessor material | Current destination |
|---|---|
| R10 complete root manuscript, companion, archive, and README | Verbatim `predecessor/` copies; old branch remains unchanged. |
| Physical institution, stock and tier accounting | Active R12 `sections/model.tex`; complete predecessor model in `retained/model_structure.tex`. |
| R7 expanded-action and support-envelope discussion | Current EC `retained/representation.tex`; original full generated source also retained. |
| R7 provider-relaxation monotonicity and exact envelopes | Current EC `retained/provider_structure.tex`, with relaxation scope unchanged. |
| R10 general stock identification and standard convex structure | Active R12 `sections/general_theory.tex`; original R10 source unchanged. |
| R10 scalar edge criterion, two-review threshold, memory proposition and counterexample | Entire original `or-r10-20260921/sections/tree_structure.tex` included in the main appendix. |
| R7 accepted continuous information hierarchy and interim-participation comparison | Entire original `or-r7-20260921/sections/accepted_continuous.tex` remains in the main paper. |
| R7 old quadratic accepted-learning section | Entire original `or-r7-20260921/sections/accepted_learning.tex` in the current EC. |
| R10 cached quadratic correction and exact/raw tables | Current EC; original R10 records remain unchanged. |
| R10 nonlinear multistage learned-control section, including adverse weighted-block outcomes | Entire original `or-r10-20260921/sections/certified_multistage.tex` in the current EC. |
| Accepted occupation/accounting material, multi-tier inaction, customer-exit certificate | Current EC, with all proof material retained. |
| R7 constructive smooth critics, extensions, and older computational diagnostics | Historical scientific archive, as complete retained sections. |
| Previous historical supplement | Entire predecessor content remains in the expanded historical archive; original TeX and PDF also retained separately. |
| All previous rational policies, scripts, scalar observations, fitted coefficients, and reviews | Original paths and commits unchanged. R12 re-audits are new records, not substituted historical data. |

The historical scientific archive is **not** the current journal electronic companion. It supplies preservation and provenance; reading it is not required to understand the main R12 theorems. The current EC is the separately built `electronic_companion.pdf` and satisfies the checked relative length rule.

## Active-source closure

R7 once generated several TeX inputs from pinned R6 sources. R12 stores ordinary copies under `retained/` and does not run that generator when building. The main, EC, and historical archive recursively resolve only ordinary committed inputs. `results/package_checks.json` lists their hashes. `results/manifest.json` additionally hashes new code, proofs, data, and PDFs.

Relocation is not deletion: the root narrative is restructured, full predecessor roots are preserved, old theorem statements and evidence remain readable, and the new paper states which statements concern a provider relaxation, an accepted optimum, or an empirical approximation experiment.
