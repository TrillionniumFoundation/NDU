# NDU — Operations Research revision R64

**Finite-Catalog Resource Allocation: A Tariff-Sensitive Complexity Frontier**

This is the complete R64 response to the independent R63 report. The main reader is `main.pdf`, the current electronic companion is `electronic_companion.pdf`, and the point-by-point letter is `RESPONSE_TO_REFEREES.pdf`. The LaTeX sources are standalone. The current entry points are the `*64.py` scripts below; `*63.py` publication scripts are retained historical material, not current build instructions.

## Changes and certified scope

The independent tariff checker now verifies the smallest rational modal standard fee. The robust checker independently verifies optimal trimmed absolute-deviation projection, all projected fields, and the smallest allowance meeting the **total absolute fee-distortion** tolerance. The inner solver's actual modal exception count, the projection's actual exception count, and its allowed budget are separately reported. No optimizer is imported by the production checker closure.

The article retains its exact representation, original-model lower bound, tariff-sensitive exact algorithm, transfer theorem, fee frontier, approximation and price-support results. High-level near-standard wording now explicitly describes an original-policy additive transfer certificate, not unproved exact tractability. Related work credits trimmed absolute deviations and objective-coefficient sensitivity. Table 5 contains all twelve frozen adversarial robust-tariff requests with quality and paired raw/compressed proof costs. No new optimization run contributes to that table.

## Reproduce the revision

Use Python 3.13.5 and `python -m pip install -r requirements.txt`. PDF compilation requires `pdflatex`, the newtx fonts/packages, and standard LaTeX packages used in the sources. The workflow uses the recorded Ubuntu 22.04 TeX package installation.

```sh
# Full executed qualification; writes only current R64 results and readers.
python qualify64.py

# Seal the delivered package after execution.
python publish64.py

# Read-only validation plus a fresh replay of all 389 available proofs.
# The fresh receipt must be outside the sealed package.
python verify64.py --replay-output /tmp/ndu-r64-fresh-replay
```

For targeted work, `python code/tests64.py` produces the semantic regression evidence; `python code/projection_table64.py` rebuilds the table from frozen records; `python revise64.py` deterministically reconstructs the manuscript from the unchanged R63 reader and R64 source fragments; `python compile64.py` compiles all three readers and checks page limits, abstract length, references and overfull boxes. Rerunning these commands modifies generated R64 artifacts, so re-seal afterward. It does not replace any historical timed observation.

## Evidence and interpretation

`results/r64/SEMANTIC_TESTS64.json` records 577 valid certificates, 288 exhaustive projection comparisons, and ten complete false-metadata certificates accepted by the archived checker but rejected by the current checker. `SEMANTIC_ADVERSARIES64.json` retains those certificates. The inherited structural suites and the 48-case exact root diagnostic remain checked. These tests validate implementations, not novelty or editorial acceptance.

`results/r64/replay/` records 405 frozen requests: 342 rational two-sided certificates, 47 numerical-solver lower policies, and 16 no-certificate requests. The 45 later-successful replays retain their original failed/incomplete checking outcomes. Original on-time target attainment is never inferred from a later integrity replay. SCIP upper bounds remain numerical. Mathematical inapplicability, implementation guards, optimization deadlines and parent timeouts remain distinct.

`results/r64/PROJECTION_QUALITY64.json` contains exact rational quantities and comparator provenance; its CSV is a flattened view. Five regrets are identified as zero; two remain intervals. Original optimizer/checker times and proof bytes are not new measurements. `SOURCE_FREEZE64.json`, `QUALIFICATION64.json`, and `PACKAGE_MANIFEST.json` bind current sources, executed commands, and every delivered file. The external exact-head receipt binds the eventual published commit without a self-referential in-tree commit hash.

## Preservation and ancestry

`PROVENANCE64.json` pins the reviewed author commit and the governing report's immutable commit and blob. `archive/r63/` preserves the R63 root readers, source/code, and results. Files not duplicated there remain byte-identical at their inherited locations, including `evidence/r60/`, `evidence/r61/`, and older archives; `verify64.py` resolves and verifies **all 6,848 files** listed in the R63 package manifest. The R63 snapshot is not mislabeled as a standalone second timing study. `CONTENT_MAP.md` records the current disposition of each contribution. No review branch or previous scientific branch is changed.
