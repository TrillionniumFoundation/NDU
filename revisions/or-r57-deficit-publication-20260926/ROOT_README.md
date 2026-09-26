# NDU — Operations Research R57

## Current scientific review object

**Finite-Catalog Renewal Design: Small Menus and Resource-Deficit Paths**

Current branch: `revision/ndu-operations-research-r57-deficit-publication-20260926`.
Scientific parent: `eee0d39e08eaedc3a26cad792b71c9c5b5a8abd9` (the actual R54 scientific tip).
Governing report: `review/operation-research-r56-independent-harsh-20260926`, commit `1bf0400f3540605d2ac68d2a40e8bcfb377d5446`, file `reviews/operation_research_referee_report_r56_independent_harsh_2026-09-26.md`.
The intervening R55/R56 branch names did not contain a scientific revision. Their referee reports are not merged into this author-revision delta. Existing branches remain unchanged.

Read **`main.pdf`**, **`electronic_companion.pdf`**, and **`revisions/or-r57-deficit-publication-20260926/RESPONSE_TO_REFEREES.pdf`**.
The measured `BUILD_VALIDATION.json`, `PRESERVATION_MANIFEST.json`, `SOURCE_FREEZE.json`, `results/PUBLICATION_AUDIT.json` and `PUBLICATION_STATUS.json` identify what was actually assembled, executed, checked and published. A protocol, transport payload, empty branch, local PDF, or build alone is not a completed scientific revision.

## Scientific changes

The paper retains the original paid finite catalog, promise equality, expected caps, realization ceilings, pre-draw service, nonnegative opening charges and command budget. The selected-boundary construction, heterogeneous component packing, exact price-path oracle, weak hardness, common-cap tractability, safe screening, robustness and historical evidence are retained.

The additions are a constructive tight `2q` cap-count bound; a joint cap/reward-type extension allowing heterogeneous rewards; the source-independent resource-deficit representation; a centered heterogeneous additive algorithm with a catalog-quadratic rather than catalog-cubic path term; and an exact zero-service lattice algorithm for arbitrary command budgets. The paper separately states arithmetic, memory, certificate-checking and binary-encoding costs. Exact book enumeration is XP in the stated menu/type parameters. No unproved FPT classification, strong NP-hardness, or universal solver superiority is claimed.

## Evidence and reproducibility

A complete unpublished local R56 package was recovered as development input. Its content hash is in the R57 protocol. It was not in the tree audited by the latest referee. The R57 tables do **not** relabel its old timings: all 186 primary and 39 extension method runs are freshly executed from the current source snapshot. The design was already inspected during development; it is not an unseen confirmatory sample. All limits, failures and original checking statuses are retained. Nine deterministic mechanical replays and extended checks of unchanged certificate bytes are separate records, not replacement benchmark timings.

The recovered source corrections retain completed enumeration incumbents under outer interruption and handle very large rational integers without decimal conversion. R57 also places enumeration and screening verification in separate checker modules. The complete checker import graph is tested: no public checker imports an optimizer.

```bash
python -m pip install scipy==1.17.0 sympy==1.14.0 PyMuPDF==1.26.7 matplotlib==3.10.8
R=revisions/or-r57-deficit-publication-20260926
python "$R/code/tests56.py"
python "$R/code/revision57.py" joint_type_tests checker_import_test
python "$R/code/publication56.py"
python "$R/code/extension56.py"
python "$R/code/verify_replay56.py"
python "$R/code/mechanics56.py"
python "$R/code/tables56.py"
python "$R/code/plot56.py"
python "$R/code/finalize_generated56.py"
python "$R/code/revision57.py" outcomes
python "$R/code/build56.py"
python "$R/code/revision57.py" preservation package
```

The `56` suffixes of inherited script filenames document source continuity; their current directory, source hashes, reader graph and R57 protocol determine the revision. Execute the complete timed sequence only in a separate working copy: move its existing `results/` to an explicitly named archive before a fresh rerun, and do not overwrite published evidence in place. Primary execution can resume unchanged inputs only with matching source hashes. Full preservation requires the Git parent; an unpacked source subset is not a substitute for that audit.

Independent single-certificate verification:

```bash
python "$R/code/check_certificate56.py" path/to/certificate.json.gz --expected-sha256 EXPECTED_ORIGINAL_MODEL_HASH
```

Supply the expected hash from the input record, not from trusting the certificate's own declaration. Price, deficit, enumeration and screening schemas dispatch to independent verification modules. Optimizer regressions use assertions and require ordinary Python without `-O`. Linux signal and address-space limits are part of the timed protocol; other operating systems require a documented adaptation.

## Preservation and journal-facing package

All scientific-parent Git blobs are retained unchanged except the six current root entry points; those six have exact predecessor copies. Earlier complete readers remain in the repository. Complete retained proofs and tables are assembled in the current main/companion or remain in explicitly identified historical sources. `CONTENT_MAP.md` maps the scientific claims, response, implementations and evidence.

`CODE_AND_DATA.zip` contains retained runnable source/data dependencies and the current readers, inputs, certificates and records. The source transfer is only a publication mechanism. The final branch contains ordinary readable scientific files and requires no transport decoding to read the paper.

The journal format uses eleven-point type, one-and-one-half spacing, one-inch margins, an anonymous title page, a text-only abstract of at most 200 words, and an equation-free introduction. The actual nonreference page count selects the regular or lengthy category; it is not guessed. Synthetic data support implementation and method comparisons, not field calibration or journal acceptance.

The ZIP deliberately omits its own hash and final publication-state manifests. Those are supplied in the Git tree and bind the completed archive without a circular self-hash. The ZIP retains its source-freeze, execution, build and preservation audits.
