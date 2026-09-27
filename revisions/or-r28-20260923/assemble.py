#!/usr/bin/env python3
"""Create the R28 reader files from byte-preserved R27 predecessors."""
from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parent; ROOT=R.parents[1]
mutable=['main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md']
if not (R/'INHERITED_SHA256.json').exists():
    base='61aff783672ce39745713f5cefbcf83d8748ebd6'
    names=subprocess.check_output(['git','ls-tree','-r','--name-only',base],cwd=ROOT,text=True).splitlines()
    delta=subprocess.check_output(['git','diff','--name-only',base,'HEAD'],cwd=ROOT,text=True).splitlines()
    assert all(n.startswith('.r28-delivery/') or n=='.github/workflows/ndu-or-r28-publication.yml' for n in delta),delta
    inv={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names}
    (R/'INHERITED_SHA256.json').write_text(json.dumps(inv,indent=2,sort_keys=True)+'\n')
inv=json.loads((R/'INHERITED_SHA256.json').read_text())
(R/'predecessor').mkdir(exist_ok=True)
for name in mutable:
    p=R/'predecessor'/name
    if not p.exists(): p.write_bytes((ROOT/name).read_bytes())
    assert hashlib.sha256(p.read_bytes()).hexdigest()==inv[name],name
# The review was committed after the scientific archive. Preserve and pin it too.
report='reviews/operation_research_referee_report_r27_2026-09-23.md'
if (ROOT/report).exists():
    raw=(ROOT/report).read_bytes()
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()=='8f3c74a0cba1bb591c1f6cde3476fca2d1b9674d'
    inv[report]=hashlib.sha256(raw).hexdigest()
    (R/'INHERITED_SHA256.json').write_text(json.dumps(inv,indent=2,sort_keys=True)+'\n')
main=(R/'predecessor/main.tex').read_text()
main=main.replace('r27-ec-labels','r28-ec-labels').replace('Revision R27,','Revision R28,')
oldtitle='Accepted Service Adaptation: Continuation Prices, Transfer Coordinates, and Certified Gains'
newtitle='Accepted Service Adaptation: Shared Policy Tables, Continuation Prices, and Certified Design'
main=main.replace(oldtitle,newtitle).replace('Accepted Service Adaptation:\\ Continuation Prices, Transfer Coordinates,\\ and Certified Gains','Accepted Service Adaptation:\\ Shared Policy Tables, Continuation Prices,\\ and Certified Design')
start=main.index('A service provider gains from adaptation only'); end=main.index('\\par\\vspace{.15in}',start)
main=main[:start]+'''A service provider must respect promised continuations when deciding how much policy flexibility to install. We connect optimized information restrictions to a sufficient stochastic state by requiring one shared policy table to survive every successor problem. A bridge theorem represents the restricted optimum through inherited service tiers, remaining payment promises, and finite public memory. Recursively accumulated participation and restriction prices certify the optimized table through a root linear program; their release coefficient recovers the marginal value of flexibility. The representation is exact for the stated additive Markov institution, while finite stored plane families provide computable bounds without a query history vector. An explicit implementation-cost model converts information-value accounting into a net design decision. Certified witness widths govern price-cache refreshes. A second certificate covers declared parameter-dependent policies under jointly changing rewards, continuation coefficients, commitments, and switching-friction scale; it checks correlated interior feasibility rather than only parameter vertices. Exact examples expose invalid childwise table selection and endpoint-only feasibility. A scaling study reports full certificate costs, including frequent refreshes under strict tolerances. Earlier structural results and unfavorable learning evidence are retained. State sufficiency is separated from the dimension-dependent cost of certified approximation.
'''+main[end:]
start=main.index('\\section{Introduction}'); end=main.index('\\section{Relation to',start)
main=main[:start]+r'''\section{Introduction}
A service provider can find a more profitable operating policy and still be unable to offer it. A customer with an exit right evaluates the promised service and transfers remaining at the current review, not only the surplus forecast when the agreement was signed. An operational improvement must respect every continuation commitment, physical capacity, and the cost of changing service tiers.

The relevant comparison is with the best implementable restricted contract. A time-only schedule, a current-regime table, and a finite-memory rule use different organizational capabilities. Those capabilities cost money to install and maintain. Comparing adaptation with an arbitrary fixed protocol mixes the value of flexibility with poor selection of the original policy. We optimize both contracts and then optimize the net value of the implementable design.

The central difficulty is that a public-information restriction couples histories that a stochastic recursion would otherwise separate. A time-only schedule must remain the same schedule in every successor. Allowing each child to choose its own table removes the restriction and overstates its optimized value. Conversely, requiring the current public regime alone to summarize a contract can omit its inherited tier and outstanding payment promise. These are distinct failures of representation.

Our main contribution is a shared-table bridge connecting these two requirements. One finite-memory table is selected before uncertainty is resolved. Conditional on that table, the remaining payment promise and inherited tier support exact stochastic implementation. Participation prices accumulate along the nested continuations, while the common table preserves the global stationarity of the information restriction. A backward price construction then bounds the optimized restricted contract through a root table-design linear program. Its release coefficient is the discounted restriction rent; when the certificate is tight it supports the optimized value frontier. Thus the frontier, sufficient-state recursion, and comparator certificate are one theorem chain rather than independent uses of generic optimization tools.

The representation has explicit boundaries. It applies to the stated additive public-Markov institution and finite-memory pooling, not automatically to arbitrary signed or nonadditive contractual constraints. The recursion avoids a query history vector, but continuous promises, table dimension, and the number of stored planes still cost computation. Exact finite-horizon dual representation is an existence result, not a polynomial storage theorem. We give conditional approximation rates and distinguish them from a posteriori certificates.

The supporting structural results retain the optimized release frontier and comparator-adjusted continuation rents. Relaxing a continuation improves both optimized values but can reduce their difference; greater switching friction can increase the adaptation premium when the restriction itself forces switching. A declared cost of memory and release turns these value comparisons into an endogenous organizational choice. A rational example selects an interior release rather than either the original table or full flexibility.

Implementation needs both a feasible policy and a valid upper bound on its optimized comparator. Audited witness widths provide a computable price-cache refresh rule, including at face changes. For a declared parameter-dependent policy, correlated constraints cannot generally be verified at parameter vertices alone. We therefore give an interior-valid polynomial cell certificate and an exact positive adaptive example. These results retain the actual query commitments and friction scale without claiming that all cost geometry may change.

The numerical evidence separates exact structural checks, synthetic scaling, and inherited results. The scaling study charges coefficient construction, candidate generation, audits, cache evaluation, witness repair, and refresh, and compares them with an exact specialized restricted solve at the same tolerance target. Frequent refreshes under strict tolerances are reported rather than hidden. The earlier unfavorable learned-versus-classical record remains intact. Neither learning superiority nor a broad empirical speed advantage is needed for the shared-table theorem.

'''+main[end:]
needle='\\section{A Service Agreement with Continuation Participation}'
pos=main.index(needle)
main=main[:pos]+r'''\input{revisions/or-r28-20260923/novelty_table.tex}
Nonanticipativity and policy aggregation already treat information bundles as constraints on scenario decisions \citep{RockafellarWets1991}. Benders decomposition already separates shared design variables from conditional subproblems \citep{Benders1962}, and stochastic dual methods already propagate value approximations \citep{PereiraPinto1991}. The added conclusion here is not a new decomposition principle: it is that a \emph{single shared table}, exact payment promises, and nested participation prices produce an exact restriction-value representation and a recursively priced optimized-comparator certificate. Without the table's global stationarity, childwise optimization certifies the wrong class. Without the additive continuation structure, the displayed price recursion is not available. EC Section~\ref{ec:novelty} compares every principal result with its closest established theorem class and states the essential assumptions.

'''+main[pos:]
main=main.replace('Successive segments describe the complete release frontier.','The finite segments describe the complete frontier structurally; degenerate events require the exhaustive refinement described in the companion.')
main=main.replace('The union of these projections is exactly the zero set. There is no general upward-ray conclusion', 'The union of these projections is exactly the zero set. This is a structural reduction, not a general complexity improvement. There is no general upward-ray conclusion')
main=main.replace('\\input{revisions/or-r26-20260923/continuous_main.tex}', '\\input{revisions/or-r26-20260923/continuous_main.tex}\n\\input{revisions/or-r28-20260923/bridge_main.tex}')
main=main.replace('\\input{revisions/or-r27-20260923/correlated_main.tex}', '\\input{revisions/or-r27-20260923/correlated_main.tex}\n\\input{revisions/or-r28-20260923/governance_main.tex}')
main=main.replace('\\section{Computational Evidence}\\label{sec:evidence}', '\\section{Computational Evidence}\\label{sec:evidence}\n\\input{revisions/or-r28-20260923/evidence_main.tex}')
main=main.replace('reports the new construction in Section', 'reports the inherited continuous-state construction in Section')
start=main.index('\\section{Conclusions}'); end=main.index('\\section*{Data and Code Accessibility}',start)
main=main[:start]+r'''\section{Conclusions}
An information restriction is a commitment shared across histories, not a collection of independent restrictions that each successor can redesign. The shared-table bridge preserves that commitment in a sufficient-state recursion and in its dual prices. Nested participation prices and globally balanced table prices certify the optimized restricted value, and the resulting release rent supports an explicit net design choice. The earlier frontier and rent results describe its finite-dimensional sensitivity; the state construction identifies when those values can be implemented and certified without a query history vector.

The same distinction governs deployment. A cached upper bound remains valid outside its favorable local face, but its quality requires an audited witness or a refreshed certificate. A parameter-dependent policy requires interior-valid correlated feasibility, not an extrapolation from individually optimized queries. These certificates do not remove the costs of continuous-state approximation, shared design variables, policy generation, or refresh. The exact examples and scaling record make those boundaries observable while retaining the full historical mathematical and computational record.

'''+main[end:]
main=main.replace('\\input{revisions/or-r26-20260923/references.tex}',r'''The R28 directory adds the shared-table theorem and full proof, endogenous design example, cache-governance and adaptive-policy certificates, exact-arithmetic scaling generator, independent verifier, complete referee response, and byte-preserved R27 reader files. Its current evidence is separate from the inherited R24--R27 observations. The formal proof and arithmetic checks are supplied for further scrutiny, not as an assertion of editorial acceptance.

\input{revisions/or-r28-20260923/references.tex}''')
(ROOT/'main.tex').write_text(main)
ec=(R/'predecessor/electronic_companion.tex').read_text().replace('r27-main-labels','r28-main-labels').replace('Revision R27,','Revision R28,').replace(oldtitle,newtitle)
ec=ec.replace('\\input{revisions/or-r25-20260923/references.tex}','')
ec=ec.replace('\\end{document}',r'''\input{revisions/or-r28-20260923/bridge_ec.tex}
\input{revisions/or-r28-20260923/governance_ec.tex}
\input{revisions/or-r28-20260923/evidence_ec.tex}
\input{revisions/or-r28-20260923/references.tex}
\end{document}''')
(ROOT/'electronic_companion.tex').write_text(ec)
refs=(ROOT/'revisions/or-r26-20260923/references.tex').read_text()
refs=refs.replace('\\bibitem[Ben-Tal',r'''\bibitem[Benders(1962)]{Benders1962}
Benders JF (1962) Partitioning procedures for solving mixed-variables programming problems. \emph{Numerische Mathematik} 4:238--252. doi:10.1007/BF01386316.

\bibitem[Ben-Tal''')
refs=refs.replace('\\bibitem[Spear',r'''\bibitem[Rockafellar and Wets(1991)]{RockafellarWets1991}
Rockafellar RT, Wets RJB (1991) Scenarios and policy aggregation in optimization under uncertainty. \emph{Mathematics of Operations Research} 16(1):119--147. doi:10.1287/moor.16.1.119.

\bibitem[Spear''')
(R/'references.tex').write_text(refs)
(ROOT/'README.md').write_text('''# Accepted Service Adaptation — Operations Research R28

**Revision branch:** `revision/ndu-operations-research-r28-20260923`  
**Review base:** `61aff783672ce39745713f5cefbcf83d8748ebd6`  
**Scientific predecessor:** R27 `85fe1a799a192758a93a423bbb6d213ab9f04cce`.

## Read the revision

- [Current paper](main.pdf) · [LaTeX](main.tex)
- [Electronic companion](electronic_companion.pdf) · [LaTeX](electronic_companion.tex)
- [Point-by-point referee response](revisions/or-r28-20260923/RESPONSE_TO_REFEREES.md)
- [Novelty and assumptions matrix](revisions/or-r28-20260923/NOVELTY_MATRIX.md)
- [Exact replay](revisions/or-r28-20260923/results/replay.json)
- [Full phase-resolved scaling evidence](revisions/or-r28-20260923/results/evidence.json)
- [Build/preservation report](revisions/or-r28-20260923/BUILD_REPORT.md)
- [Manifest](revisions/or-r28-20260923/MANIFEST.json)
- [Latest referee report, unchanged](reviews/operation_research_referee_report_r27_2026-09-23.md)

The central result is a shared-table bridge: one ex ante policy table survives the promised-payment recursion; normalized continuation and restriction prices produce an optimized-comparator certificate through a root table LP. A dual-completeness proof states explicitly that discovering an exact finite certificate need not have polynomial storage or construction cost. New results include a net implementation-cost decision, a certified refresh rule, and an interior-valid certificate for a declared adaptive policy.

The exact two-period example distinguishes the pooled value 37/50 from the unrestricted value 53/50. With unit linear release cost, the optimal release is 1/15. The adaptive continuum example certifies gain 9/1024. These are exact synthetic examples, not field estimates. The scaling design is deliberately block-separable and compares exact rational certificate accounting with a specialized exact solve; it is not a dense-QP speedup claim. Strict tolerances cause frequent cache refreshes.

## Reproduce

```bash
python -S revisions/or-r28-20260923/research.py
python -S revisions/or-r28-20260923/verify.py
python -S revisions/or-r28-20260923/make_tables.py
bash revisions/or-r28-20260923/build.sh
python revisions/or-r28-20260923/check_package.py --manifest
python -S revisions/or-r28-20260923/verify.py --check
```

The evidence generator and independent verifier require only Python's standard library. The checker does not import the generator. Linux subprocesses measure isolated configuration peak RSS; timings are platform observations, not reproducible performance constants. The inherited R24–R27 replays are unchanged. LaTeX dependencies match R27; the PDF inspection additionally uses PyMuPDF.

## Preservation and scientific status

All earlier derivations, reports, data, code, and revisions remain at their original paths. The six R27 reader files are preserved byte for byte under `revisions/or-r28-20260923/predecessor/`. Root reader files are updated; no unrelated branch is changed. Inherited-source hashes and final document hashes are verified independently. The latest review is part of the branch ancestry and remains unchanged.

This is a substantive author revision for another referee review, not a journal submission, acceptance claim, or independent proof of novelty. Its manuscript uses the Operations Research anonymous, author–year, 11-point, 1.5-spaced format; exact pagination is recorded in the build report.
''')
(ROOT/'NDU_OR_submission_checklist.md').write_text('''# R28 Operations Research format and delivery checklist

- Anonymous title page, abstract at most 200 words, subject classifications, Stochastic Models area.
- Letter paper, one-inch margins, 11-point text, one-and-a-half line spacing.
- Introduction without displayed equations; author–year citations; alphabetic references.
- Numbered tables without vertical rules, placed after references in the main paper.
- Data/code accessibility statement; all inherited mathematical material and adverse learning results retained.
- Current pagination, reference resolution, horizontal overflow, predecessor preservation, and source/PDF hashes are recorded by `revisions/or-r28-20260923/check_package.py`.
- This branch is for further review; no journal submission or acceptance is asserted.

Official format source: https://pubsonline.informs.org/page/opre/submission-guidelines (checked September 23, 2026). Regular manuscripts are limited to 30 pages excluding references; the lengthy-paper category normally permits 40 excluding references. The final build report identifies the category supported by the generated page counts, rather than assuming that a long revision is regular length.
''')
print('R28 reader sources assembled; six predecessor reader files preserved.')
