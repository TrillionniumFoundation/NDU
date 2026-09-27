"""Idempotent R33 publication preparation; preserve every scientific statement."""
from pathlib import Path
import subprocess
R=Path('revisions/or-r33-piecewise-randomized-20260923')
BASE='238bfdb24d93439a545551d275a0c9189dbc017b'
p=R/'extensions.tex';s=p.read_text()
s=s.replace(r'Write $\phi_{vi}(\eta)=\argmax_{[l_{vi},h_{vi}]}\{g_{vi}(x)-a_{vi}\eta x\}$. The occurrence quotient, payment recursion, and cap reflection remain exact, with', 'The local price response is\n\\[\n \\phi_{vi}(\\eta)=\\argmax_{[l_{vi},h_{vi}]}\\{g_{vi}(x)-a_{vi}\\eta x\\}.\n\\]\nThe occurrence quotient, payment recursion, and cap reflection remain exact, with')
assert 'The local price response is' in s
p.write_text(s)
old='revisions/or-r31-tightness-minimal-machine-20260923/tables.tex'
s=Path(old).read_text().replace('\\clearpage\n','').replace(r'\begin{table}[htbp]',r'\begin{table}[p]')
(R/'main_table_layout.tex').write_text(s)
p=Path('main.tex');s=p.read_text().replace(old,str(R/'main_table_layout.tex'));p.write_text(s)
p=R/'build_validate.py';s=p.read_text().replace('text=True,stdout=',"text=True,encoding='utf-8',errors='replace',stdout=")
if "assert records['main']['pages']<=30" not in s:
 s=s.replace("text=(B/'main.txt').read_text()", "assert records['main']['pages']<=30\nassert records['electronic_companion']['pages']<=records['main']['pages']\ntext=(B/'main.txt').read_text()")
 s=s.replace("'tables_after_references':True,", "'tables_after_references':True,'main_all_pages_at_most_30':True,'companion_not_longer_than_main':True,")
p.write_text(s)
p=R/'predecessor/NDU_OR_submission_checklist.md'
if not p.exists():p.write_bytes(subprocess.check_output(['git','show',BASE+':NDU_OR_submission_checklist.md']))
Path('NDU_OR_submission_checklist.md').write_text('''# Operations Research review package — R33

## Version and reader files

New branch: `revision/ndu-operations-research-r33-piecewise-randomized-20260923`.
Scientific base: `238bfdb24d93439a545551d275a0c9189dbc017b`.
Effective report: independent R30 review at `a017f474619e86be533547acac87a3c8354f64cf`.
Entry points: `main.tex`, `electronic_companion.tex`, and the corresponding rebuilt PDFs.

## Scientific changes

R31/R32 results and adverse evidence are preserved. R33 adds the piecewise-quadratic event theorem, shared-circuit storage/query theorem, kink-safe conjugate certificate, explicit flow reduction, adjacent-lottery characterization, and globally solved strict two-symbol advantage. See `revisions/or-r33-piecewise-randomized-20260923/RESPONSE_TO_REFEREES.md` for every referee item and the inherited/new distinction.

## Style and reproducibility

The abstract has 183 words and no mathematical notation. The introduction contains no equations or mathematical notation. Main text uses 11-point type, one-and-a-half spacing, and one-inch margins. Author-year references are alphabetized. All tables remain after references. Only forced page breaks in a derived copy of the old tables are removed; every number and note is retained. The complete new theorem proofs remain in the article.

The build rejects undefined citations/references, multiply defined labels, and overfull boxes. It requires at most 30 total main-PDF pages, including title, references, and tables, and an EC no longer than the article. The authoritative page counts, source commit, PDF hashes, and exact-test results are in `revisions/or-r33-piecewise-randomized-20260923/BUILD_VALIDATION.json` after a successful build. Absence of that record means reader publication is not yet validated.

New exact tests and the retained tightness checker are rerun. Historical large-scale timings are retained records, not represented as new runs. No published specialized flow solver or real service dataset is claimed.

## Author-only declarations not supplied

Author identities, affiliations, ORCIDs, coauthor approval, funding/conflicts, permissions, overlapping-submission disclosures, and journal-system submission are not fabricated or certified. This is a repository referee package, not a ScholarOne submission or acceptance decision.
''')
p=Path('README.md');s=p.read_text();old='The isolated R33 workflow verifies the payload, commits the scientific sources, runs exact checks, compiles both reader PDFs with filtered cross-document labels, checks citations/references and layout, and publishes validation artifacts on this branch only.'
new='The initial transport was SHA-256 verified before scientific sources were committed. The current isolated R33 workflow builds the tracked revision, applies idempotent layout preparation, runs exact checks, compiles both reader PDFs with filtered cross-document labels, and publishes only validated PDFs on this branch. It checks citations/references, overfull boxes, the 30-total-page main limit, and the companion length.'
s=s.replace(old,new);p.write_text(s)
p=R/'DERIVATION_PROVENANCE.md';s=p.read_text()
if '## Reader layout preservation' not in s:
 s+='\n## Reader layout preservation\n\n`main_table_layout.tex` is the exact R31 table text with forced inter-table page breaks removed and float placement changed to collected table pages. Every datum and note is retained. The R33 local-response definition is displayed to avoid an overfull theorem-heading line. Full theorem proofs stay in the main article. The predecessor root submission checklist is also archived verbatim. `prepare_reader.py` makes only these idempotent publication changes and fixes decoding of TeX log bytes; mathematical statements are unchanged.\n'
p.write_text(s)
