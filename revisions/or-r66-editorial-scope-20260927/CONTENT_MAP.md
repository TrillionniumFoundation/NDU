# R63 → R64 preservation and referee-response map

All 6,848 files of the reviewed R63 flat package are preserved byte-for-byte. R63 root files, code, sections and results are copied to `archive/r63/`; other inherited files remain unchanged at their original relative paths. `verify64.py` resolves each original manifest entry against this map and checks its hash. The earlier R60→R63 preservation map remains in `archive/r63/CONTENT_MAP.md`.

| Reviewed contribution | R64 disposition |
|---|---|
| Exact selected-boundary representation and original-policy reconstruction | Main, unchanged mathematical statements and proofs |
| Original-model W[1] reduction and group-sum argument | Main, unchanged |
| Exact tariff-exception algorithm and uniform-fee frontier | Main, unchanged theorem/proof; independently checked modal parameterization and conditional-exactness explanation added |
| Fee-transfer theorem, norm bounds and strict-margin condition | Main, unchanged statement/proof; high-level exactness distinction and theoretical-only margin qualification added |
| Sparse-exception projection | Main, full argument retained; allowance notation, deterministic ties, zero tolerance, nearest antecedents and precise preprocessing scope clarified |
| Conservation, deficit approximation, convolution, repair and bit complexity | Main and companion, unchanged mathematics |
| Same-book support and positive-gap example | Main, unchanged mathematics; empirical caption specifies one active original book |
| Heterogeneous rewards, prototypes, cap counts and all additional retained results | Companion and original archives, unchanged |
| Historical experiments, 16 no-certificate requests and 45 later-successful original failures | Unchanged frozen records; current replay adds evidence, not reclassification |
| R63 reader, response, code and source freeze | Preserved in archive/r63; shared historical evidence remains at original paths |
| Independent certificate semantics | Companion EC.11.2; check_projection64.py plus strengthened check_tariff60.py/check_robust61.py |
| Required projection-quality table | Main Table 5; all 12 requests, original timings, exact/bounded regret, paired proof sizes; exact machine-readable provenance |
| Required literature and wording corrections | Abstract, introduction, related work, projection subsection, conclusion and response |
| R63 original-timing vs later integrity-audit distinction | Every primary computational table caption/note and current reproduction instructions |

Of 78 inherited mathematical environments, 76 are byte-identical in the current readers. The two projection environments only clarify notation, the descriptive heading, and inclusion of zero tolerance. No inherited mathematical environment is removed. All principal proofs remain in the current article or companion, not merely in an archive.


## R65 request/transfer correction — no removal of scientific content

The current main paper keeps the full R64 theorem/proof sequence and tables; its abstract specifies the sparse-exception class and its robustness section states the external request/transfer contract. The companion retains every mathematical environment and adds the request schema, trust boundary, exact equal-gross lower formula, legacy migration, and the two witnessed regressions. All 6,992 files in the reviewed R64 payload resolve through `archive/r64/<path>` when present and the unchanged `<path>` otherwise. The preservation verifier checks original hashes and separately compares all 36 main and 42 companion mathematical environments byte-for-byte. Earlier maps remain above as provenance, not contradictory current build instructions.

Current operational entry points are `revise65.py`, `qualify65.py`, `compile65.py`, `publish65.py`, and `verify65.py`. Request-level checking is `code/binding65.py`; old low-level utilities retain their explicitly narrower mathematical meaning. The projection-quality table and all previous timing, failure and regret-bound records are unchanged.


## R66 editorial clarification — accepted science and checker unchanged

All 7,080 R65 manifest entries are preserved under the `archive/r65/<path>`-first resolution rule. The current article and companion retain all 36 and 42 accepted mathematical environments, respectively, every display and bibliography, and all empirical tables. No inherited `code/`, `evidence/`, `generated/`, `sections/` or `results/` file is replaced. The complete editorial diff and all twelve comment dispositions are provided in `EDITORIAL_DIFF66.patch` and `EDITORIAL_SCOPE66.md`. Current build, qualification, sealing and read-only verification entry points end in `66.py`; the request API and schema remain the accepted R65 versions.
