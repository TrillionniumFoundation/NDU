# R37 final reader inspection

Status: **PASS — rendering and layout inspection completed**.

Scientific source commit: `0afd833f6d0f16195579399334426aebd3ea1b20`.

Reader publication commit: `4aa8b68a6a6375ad2b7e05ddba51b57206464e54`.

Successful publication workflow: `35947782872`; successful numerical-validation workflow: `35946201871`.

This inspection is an add-only review record. It does not change the compiled readers, numerical evidence, or scientific source commit recorded in `BUILD_VALIDATION.json`.

## Verified reader identities

| Reader | Physical pages | SHA-256 |
| --- | ---: | --- |
| Root `main.pdf` | 32 | `791a68b140e9d4be92feeee4255aad05d5b1805c47a4aeca4ac0f66cd5f22b8f` |
| Root `electronic_companion.pdf` | 27 | `c71406201a6c2a7a1c19ba4bd343c61dc082337617adc5eded4c13cb3304b8bf` |
| R37 `RESPONSE_TO_REFEREES.pdf` | 6 | `65fbad78434de8c71197f00da4ee66f2be8cb5fba9afc8e805450f634f11be0a` |

The main reader has 30 pages excluding its two reference pages, counting its title page, article appendices, and all six tables. The companion has 27 pages including its references. The abstract has 182 words. The source uses 11-point type, 1.5 spacing, one-inch margins, anonymous reader metadata, an equation-free introduction, author-year references, and tables after the main references. The proposed area is Optimization.

## Inspection performed

The exact successful-workflow artifact was downloaded and its three reader hashes were matched against the remotely committed build manifest. All 65 pages were rasterized. Page contact sheets were visually inspected, with full-page checks of representative dense mathematics, the timing table, and the revised response text. The final raster pages were also compared with the locally preflighted readers; unchanged response pages were byte-identical as raster images.

The inspected pages show legible text and equations, intact margins, consistent section and appendix numbering, complete table rows and captions, and no visible clipping, overlap, missing glyphs, or stray blank pages. A separate text-coordinate check found no outlying spans beyond the checked page envelope. The final LaTeX logs report zero undefined references, zero undefined citations, zero multiply defined labels, and zero overfull boxes for all three readers.

The initial build was not published as a validated reader because its companion was longer than the main paper. The final allocation moves the new bounded-overrun proofs and computational methods intact into the article appendices, and all current measurement tables after the article references. The broader inherited theory remains in the companion. No content was removed to satisfy the length check.

## Preservation and interpretation

The build audits the 1,758-file base tree at `f26f4da71207a7613735b0504bc34dbe231813c1`. It finds no removed or renamed base files and no changed legacy theorem, code, or evidence files. Exact R36 predecessor readers and their hashes are retained, with a content-preservation map. Only the new R37 branch is targeted by the write workflows.

Rendering inspection and passing computational checks are not editorial acceptance or a substitute for mathematical referee review. No journal submission has been performed. These readers, the point-by-point response, exact evidence, and preservation records are ready for the next review round.
