"""Construct ordinary complete R23 TeX from immutable R22 predecessor sources.
All earlier theorem/proof blocks remain verbatim in the main or companion.
"""
from pathlib import Path
import re,json,hashlib
R=Path(__file__).resolve().parent;ROOT=R.parent.parent
for name,h in json.loads((R/'PREDECESSOR_SHA256.json').read_text()).items():
 assert hashlib.sha256((R/'predecessor'/name).read_bytes()).hexdigest()==h,name
main=(R/'predecessor/main.tex').read_text();ec=(R/'predecessor/electronic_companion.tex').read_text()
main=main.replace('Revision R22','Revision R23');ec=ec.replace('Revision R22','Revision R23')
for n in ('main','ec'):
 t=locals()[n].replace('Continuation Prices and Certified Gains','Continuation Prices and Robust Certified Gains')
 locals()[n]=t
abstract='''Service providers can revise contractual tiers only when customers accept continuation terms and physical commitments remain intact. We develop a certified expansion framework that compares accepted adaptation with reoptimized restricted contracts. Continuation prices, switching capacities, and exact transfer coordinates characterize profitable deviations and critical friction. Under stated strong convexity and smooth resource coupling, a prescribed resource-reward value gradient yields a controlled accepted response without an optimal-face oracle. A component certificate separates decision loss from resource, switching, and participation slack; complete dual repair attains the best certificate without strict feasibility. We extend accepted gain certification to simultaneous objective and participation-coefficient uncertainty. A common outer comparator class protects the true model-specific restricted optimum, whereas separately reoptimized vertex comparators can fail. Neural value-gradient and direct-price methods are evaluated using frozen deterministic ensembles, independent validation, structured classical baselines, and full-polyhedron scaling. Joint-misspecification experiments retain positive pointwise gain certificates while unprotected nominal decisions violate uncertain participation constraints. Classical robust optimization and direct-price methods remain strong comparators. The results connect accepted-control geometry, implemented decisions, and certified economic gains without equating neural approximation with computational advantage.'''
a=main.index('\\textbf{Abstract.}')+len('\\textbf{Abstract.}');b=main.index('\\par\\vspace',a);main=main[:a]+'\n'+abstract+'\n'+main[b:]
old='These are known-model synthetic experiments, not field calibration or evidence that an unknown acceptance model has been learned correctly.'
new='The known-model studies are complemented by a new experiment in which reward, friction, participation coefficients, and capacity budgets are jointly misspecified. A robust accepted response and a common outer comparator class protect the gain relative to the truly reoptimized restricted contract. Separate vertex-specific comparators can fail when acceptance itself changes; an explicit counterexample identifies this distinction. The uncertainty set is specified rather than statistically estimated, so the experiments do not establish field calibration.'
assert old in main;main=main.replace(old,new)
main=main.replace('Here the feasible polyhedron is known; learning proposes a policy and a separate calculation certifies it.','In the nominal studies the feasible polyhedron is known; under joint coefficient uncertainty, an explicit robust counterpart is used. Learning proposes a policy and a separate calculation certifies it.')
# Preserve the complete original global-bridge proof, relocating only its display.
start=main.index('\\label{thm:r19-global}');a=main.index('\\begin{proof}',start);b=main.index('\\end{proof}',a)+len('\\end{proof}')
proof=main[a:b]
main=main[:a]+'The complete proof is in Electronic Companion Section~\\ref{ec:r23-preserved-global-proof}.\n'+main[b:]
relocated='\\section{Proof of the global resource-price bridge}\\label{ec:r23-preserved-global-proof}\nThe following is the complete proof of Theorem~\\ref{thm:r19-global}, retained verbatim from the predecessor manuscript.\n'+proof+'\n'
main=main.replace('\\section{Computational study', '\\section{Computational study') # no-op guards ordinary source approach
marker='\\section{'
# Insert the robust extension directly before the existing computational section.
idx=main.index('\\label{sec:r22-complete}')
emp=main.find('\\section{',idx)
assert emp>0, 'Empirical section not found'
# The next section after complete dual is the existing empirical section.
print('Insertion before',main[emp:emp+100])
main=main[:emp]+(R/'sections/robust_main.tex').read_text()+'\n'+main[emp:]
main=main.replace('\\section{Conclusions and operational implications}',(R/'sections/robust_findings.tex').read_text()+'\n\\section{Conclusions and operational implications}')
old='Unknown demand, misspecified commitments, field calibration, and arbitrary retraining are different empirical targets and are not inferred from the present certificates.'
new='Joint objective and commitment-coefficient error is now addressed by a robust accepted response and a union-containing outer comparator class. This protects the true model-specific economic comparison even when nominal acceptance fails. The recorded positive pointwise certificates concern the declared coefficient sets; unknown demand, field-calibrated uncertainty and arbitrary retraining remain different empirical targets.'
assert old in main;main=main.replace(old,new)
main=main.replace('All new measurements are distinguished from retrospective analyses of the R16 dataset.','R23 adds a separately predeclared 96-context joint-misspecification study and independent rational replay; its engineering pilot is excluded. All new measurements are distinguished from retrospective analyses of the R16 dataset.')
# Keep all old companion scientific material, append new detailed construction.
idx=ec.index('\\begin{thebibliography}')
ec=ec[:idx]+relocated+'\n'+(R/'sections/robust_ec.tex').read_text()+'\n'+ec[idx:]
refs=r'''\bibitem[Ben-Tal and Nemirovski(2000)]{BenTalNemirovski2000}
Ben-Tal A, Nemirovski A (2000) Robust solutions of linear programming problems contaminated with uncertain data. \emph{Mathematical Programming} 88:411--424. doi:10.1007/PL00011380.

'''
refs2=r'''\bibitem[Bertsimas and Sim(2004)]{BertsimasSim2004}
Bertsimas D, Sim M (2004) The price of robustness. \emph{Operations Research} 52(1):35--53. doi:10.1287/opre.1030.0065.

'''
for name in ('main','ec'):
 t=locals()[name]
 # Ben-Tal follows Bemporad; Bertsimas/Sim follows Bertsimas/Kallus.
 mark='\\bibitem[Bertsimas and Kallus';idx=t.index(mark);t=t[:idx]+refs+t[idx:]
 idx=t.index('\\bibitem[',t.index(mark)+len(mark));t=t[:idx]+refs2+t[idx:]
 locals()[name]=t
# Add one narrow novelty-map row without replacing any existing comparison.
idx=main.index('Hoeffding concentration; fixed policy')
row=r'''Robust uncertain-data optimization \citep{BenTalNemirovski2000,BertsimasSim2004}
& Vertex robust counterparts and uncertainty--performance tradeoffs are established.
& Theorem~\ref{thm:r23-robust} retains the true model-specific accepted comparator through a common outer class; the interior-comparator counterexample shows why separate vertex benchmarks do not suffice.\\
'''
main=main[:idx]+row+main[idx:]
(ROOT/'main.tex').write_text(main);(ROOT/'electronic_companion.tex').write_text(ec)
(ROOT/'main.bib').write_bytes((R/'predecessor/main.bib').read_bytes())
# Bibliography is inline and duplicated in companion for independent compilation.
for key,entry in [('BenTalNemirovski2000', '@article{BenTalNemirovski2000, author={Ben-Tal, Aharon and Nemirovski, Arkadi}, title={Robust solutions of linear programming problems contaminated with uncertain data}, journal={Mathematical Programming}, volume={88}, pages={411--424}, year={2000}, doi={10.1007/PL00011380}}'),('BertsimasSim2004','@article{BertsimasSim2004, author={Bertsimas, Dimitris and Sim, Melvyn}, title={The price of robustness}, journal={Operations Research}, volume={52}, number={1}, pages={35--53}, year={2004}, doi={10.1287/opre.1030.0065}}')]:
 with (ROOT/'main.bib').open('a') as f:f.write('\n'+entry+'\n')
(R/'PRESERVATION_MAP.md').write_text('''# R23 preservation map

The complete R22 publication at `fef3bad92ab9c74530b530a885bb6f437e8b1c1a` is the scientific base. Exact predecessor root documents are in `predecessor/`, with SHA-256 hashes in `PREDECESSOR_SHA256.json`.

All predecessor theorem, proposition, lemma, corollary, assumption and proof environments are preserved verbatim in the current main manuscript or electronic companion. Only the full proof of the global resource-price bridge (`thm:r19-global`) moves from the main manuscript to the companion section `ec:r23-preserved-global-proof`, with a precise cross-reference. Its theorem statement remains in the main paper. The new robust extension is additive.

The abstract, introductory synthesis and conclusion are updated to reflect executed joint-coefficient-misspecification evidence; their exact old text remains in the predecessor snapshot. No original neural, polynomial, RBF, geometry, scaling, matched-cost, or adverse empirical result is removed. R19 and R22 scientific observations are not rebranded as R23 execution. Historical supplements, earlier revision directories and reviews are unchanged.
''')
print('Wrote complete ordinary R23 sources; abstract words',len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*",abstract)))
