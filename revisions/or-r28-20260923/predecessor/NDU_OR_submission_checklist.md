# Operations Research R27 — author/referee package checklist

## Review object

Current revision branch: `revision/ndu-operations-research-r27-20260923`. Scientific predecessor: R26 `38f99a5b46d8cfe4f1197fc869735d5f798c499a`. Both the ordinary and later independent R24 reports are addressed in `revisions/or-r27-20260923/RESPONSE_TO_REFEREES.md`; neither report file is edited.

## Journal-facing documents

- Title retained: *Accepted Service Adaptation: Continuation Prices, Transfer Coordinates, and Certified Gains*.
- `main.tex` / `main.pdf` and `electronic_companion.tex` / `electronic_companion.pdf` are the current R27 documents.
- Anonymous 11-point text, letter paper, one-inch margins, and one-and-a-half spacing.
- Text-only single-paragraph abstract: 181 words; equation-free introduction.
- Author–year references, tables after references without vertical rules, and no footnotes.
- Regular-paper length: main PDF at most 30 pages even counting title/references/tables; companion no longer than the main PDF. Actual page counts are recorded by `check_package.py` after compilation.
- Cross-document references are generated in four paired LaTeX passes and checked for undefined or multiply defined references and horizontal overflow.
- Area remains Stochastic Models, supported by the sufficient-state and continuous accepted-policy results, with optimizer-level restriction/rent theorems and comparator certification.

The format was checked against the publisher's Operations Research submission guidelines on September 23, 2026. The official INFORMS class is not required when the stated formatting rules are met. No journal submission is made by this workflow.

## Scientific revision checks

- Retain all R26 mathematical statements/proofs, including the continuous-state source inputs, and all earlier research files.
- Integrate Theorem 7.3 and Corollary 7.4 in the existing certification section, with full supporting derivations and exact counterexamples in EC.11.
- Distinguish globally valid reuse from the conditional exact-anchor quadratic bound.
- Preserve coefficient correlations and the correct cell/anchor/vertex ordering for uniform uncertainty.
- Distinguish 72 new numerical proposals and 24 new off-ray queries from new bound evaluations of inherited records.
- Independently reconstruct 232 optimization certificates, 240 cached-price evaluations, the exact gap identities, positive uniform example, and 14 negative controls.
- Preserve the corrected amortization equation, strict-target 100% learned fallbacks, and null observed break-even results.
- Separate offline optimizer work, query arithmetic, policy acceptance, and any possible refresh cost. Do not infer unmatched wall-clock superiority or field calibration.

## Publication and preservation checks

Thirteen R26 root files are preserved under the new predecessor directory. The inherited inventory pins every predecessor file; only six current root documents can differ. The package manifest includes the actual root PDFs, source inputs, new records, exact replay results, response, and preservation inventories. The workflow must push only the R27 branch, then validate a clean checkout of the **actual final scientific SHA** and attach `ndu-or-r27/final-sha` status to that SHA. A green generation job alone is not the final verification.

See `revisions/or-r27-20260923/BUILD_REPORT.md` and `results/package_check.json` for the executed checks. Passing them is evidence about the package and calculations, not an assertion of editorial acceptance.
