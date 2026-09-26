# R57 claim, response, and preservation map

Scientific parent: `eee0d39e08eaedc3a26cad792b71c9c5b5a8abd9`.
Latest reviewed branch tip: `1bf0400f3540605d2ac68d2a40e8bcfb377d5446`.
The full response is `RESPONSE_TO_REFEREES.tex` / `.pdf`; exact theorem numbers are generated in `BUILD_VALIDATION.json`.

| Reviewer issue | Scientific source | Implementation/evidence |
|---|---|---|
| R56 absent revision, misidentified reader | Current root readers, R57 response introduction | Actual recorder input graph, source/PDF hashes, publication and preservation audits |
| Small-menu structure | `small_menus.tex`: cap-count, strict `2q` construction, joint cap/reward-type theorem | `compression.py`, `tests56.py`, `JOINT_TYPE_REGRESSION.json` |
| Encoding-sensitive weak hardness | Retained `hardness.tex`; exact zero-service theorem in `lattice.tex` | `deficit.py` lattice mode, 18 lattice comparisons and three encoding stress requests |
| Severe separate-anchor resource complexity | `deficit_paths.tex`: source-independent coordinate, centering, exact-promise repair, arbitrary support holes | `deficit.py`, `check_deficit.py`, exact reference regressions and heterogeneous timed runs |
| Bit, cache, memory and checking costs | `deficit_paths.tex` and `lattice.tex`, current companion | Large-integer full-certificate test, pre-allocation state rejection, recorded bit/byte/checking metrics |
| Search mechanics and exact-target comparisons | Current computational section and companion | `SEARCH_MECHANICS.csv`, exact-target records, `MECHANICS_REPLAY.json`, complete trajectories |
| Screening plus downstream total time | Current screening table | `SCREENING_END_TO_END.csv`, original-instance transferred certificates, independent `check_screen.py` |
| Independent verification | Current companion, separate verification modules | `CHECKER_DEPENDENCIES.json`, certificate bytes/hashes, mutation tests, original and extended verification records |
| Operational importance | Structural results plus `operations_interface.tex` and retained production example | Payoff-calibration transfer with fixed feasibility; no claim of field-calibrated inputs |
| Preserve antecedent science | Current main and complete EC inputs; all prior revision directories unchanged | Full Git-blob manifest and exact copies of six replaced root entry points |

## Distinct provenance objects

1. R54 is the scientific parent actually published and reviewed; all its evidence remains unchanged.
2. R55/R56 review branches record the missing-publication problem; they are not silently merged or relabeled as scientific work.
3. The recovered local R56 development package has an explicitly recorded SHA-256. It is a development input, not evidence of earlier remote publication, and its timings are not pooled with R57.
4. R57 supplies a new scientific delta and freshly executes the disclosed 225-run design. Separate labels distinguish primary, extension, untimed mechanics and extended verification. Earlier post-inspection protocol text is retained under `development/recovered_protocols/` for provenance; it is not an R57 preregistration claim.
5. The different absent R55 local 269-run archive is not fabricated or counted as current evidence.

The initial R57 checker refactor is semantic-preserving: enumeration and screening proof functions are moved to verifier-only modules. The import-graph regression verifies their separation from the optimization modules. The new joint-type constructor is a scientific implementation addition, not a renamed common-reward check.
