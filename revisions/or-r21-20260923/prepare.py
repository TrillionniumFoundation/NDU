"""Produce complete ordinary root manuscripts from preserved R19 sources."""
from pathlib import Path
import re,json,hashlib
R=Path(__file__).resolve().parent;ROOT=R.parents[1];P=R/'predecessor'
TITLE='Accepted Service Adaptation with Neural Differential Utility: Continuation Prices and Certified Gains'
OLDTITLE='Neural Differential Utility: Accepted Multistage Service Control and Certified Value-Gradient Decisions'
ADDITIONS=r'''
\bibitem[Amos and Kolter(2017)]{AmosKolter2017}
Amos B, Kolter JZ (2017) OptNet: Differentiable optimization as a layer in neural networks. \emph{Proceedings of Machine Learning Research} 70:136--145.
\bibitem[Bertsimas and Kallus(2020)]{BertsimasKallus2020}
Bertsimas D, Kallus N (2020) From predictive to prescriptive analytics. \emph{Management Science} 66(3):1025--1044. doi:10.1287/mnsc.2018.3253.
\bibitem[Elmachtoub and Grigas(2022)]{ElmachtoubGrigas2022}
Elmachtoub AN, Grigas P (2022) Smart ``predict, then optimize.'' \emph{Management Science} 68(1):9--26. doi:10.1287/mnsc.2020.3922.
\bibitem[Kraul et al.(2023)Kraul, Seizinger, and Brunner]{KraulSeizingerBrunner2023}
Kraul S, Seizinger M, Brunner JO (2023) Machine learning--supported prediction of dual variables for the cutting stock problem with an application in stabilized column generation. \emph{INFORMS Journal on Computing} 35(3):692--709. doi:10.1287/ijoc.2023.1277.
\bibitem[Sambharya et al.(2024)Sambharya, Hall, Amos, and Stellato]{Sambharya2024}
Sambharya R, Hall G, Amos B, Stellato B (2024) Learning to warm-start fixed-point optimization algorithms. \emph{Journal of Machine Learning Research} 25(166):1--46.
\bibitem[Stellato et al.(2020)Stellato, Banjac, Goulart, Bemporad, and Boyd]{Stellato2020}
Stellato B, Banjac G, Goulart P, Bemporad A, Boyd S (2020) OSQP: An operator splitting solver for quadratic programs. \emph{Mathematical Programming Computation} 12(4):637--672. doi:10.1007/s12532-020-00179-2.
'''
ABSTRACT='''Service providers can revise contractual tiers only when customers accept continuation terms and physical commitments remain intact. We develop a certified expansion framework that compares accepted adaptation with reoptimized restricted contracts. Continuation prices, switching capacities, and exact transfer coordinates characterize profitable deviations and critical friction. Under stated strong convexity and smooth resource coupling, a prescribed resource-reward value gradient yields a globally controlled accepted response without an optimal-face oracle. A four-component certificate separates decision loss from resource, switching, and participation slack, and supports monotone low-dimensional price repair. An implemented benchmark gate and independent one-sided validation certify gains relative to the optimized restricted value. Neural value-gradient and direct-price methods are evaluated using frozen deterministic ensembles, fresh in-distribution and shifted contexts, and full-polyhedron scaling. Both ensembles achieve positive conditional expected-gain bounds in the recorded synthetic study; direct-price methods are more accurate, and structured classical optimization remains an essential computational comparator. Complete timing includes repair, certification, and actual fallback. The results establish an auditable path from accepted-control geometry to realized economic gains without equating neural approximation with computational advantage.'''
CONTRIBUTIONS=r'''The organizing quantity is the gain from expanding an already optimized accepted policy class, not improvement over a weak announced incumbent. Continuation-price balance, cumulative subtree cuts, and exact transfer coordinates identify profitable accepted directions and critical-friction bounds. Those accepted-service consequences use classical convex and total-variation tools; they are not presented as new general principles of duality. The canonical information hierarchy and the general tree theory remain intact.

A resource statistic then connects this geometric value to an implemented decision. Differentiating an optimized scalar value in deliberately specified resource-reward coordinates yields the optimal resource vector. With stated strong curvature and smooth resource coupling, price-response stability gives a global regret bound across switching and capacity transitions. Every participation row remains in the response. The theorem concerns broad accepted geometry under these objective assumptions; it does not cover arbitrary objectives by silently adding regularization.

The certificate supplies the operational connection. A new component identity separates resource-price error from box optimality, switching tension and participation slack, and identifies when price-only repair cannot meet a requested accuracy. A small-dimensional monotone repair improves the upper bound without changing the decision. The benchmark-gate theorem then compares the selected feasible output with a reoptimized restricted contract, charging approximation and comparator error explicitly. This is the same accepted expansion problem from geometry through deployment, rather than a separate theorem for each predictor.

The empirical work tests that connection with both neural value gradients and directly learned prices. Original neural, polynomial and RBF results remain available, including adverse comparisons. New independent validation evaluates two fixed deterministic ensembles against optimized time-only amendments, with full numerical-state isolation and a separate shifted context population. The timing comparison includes a structure-aware lifted primal--dual continuation method, identical final certificate targets, and actual fallback. Scaling varies the full accepted polyhedron rather than relying on the old scalar star. These are known-model synthetic experiments, not field calibration or evidence that an unknown acceptance model has been learned correctly.
'''
CONCLUSION=r'''\section{Conclusions and operational implications}
Accepted adaptation can create value beyond an optimized restricted service contract without relaxing customer commitments. Continuation prices and switching capacities identify this expansion value; the resource statistic connects it to a concrete response; and the final certificate and benchmark gate connect that response to realized gain. This is the paper's common theorem chain, not a requirement that every implementation be neural.

The new certificate distinguishes a price problem from a decision problem. Resource and equality prices can be repaired in a low-dimensional space, but fixed switching and participation slack provide an irreducible floor. A better upper bound does not change primal regret. General convex objectives retain Fenchel certification; the global quadratic derivative-error rate requires its stated curvature, and any added regularization must carry the explicit original-objective bias budget.

Independent final validation now targets frozen deterministic rules and reoptimized time-only amendments, with complete solver-state isolation and fresh contexts. Its positive conditional gains support economically meaningful accepted adaptation in the declared synthetic model. Direct-price methods remain strong competitors, and measured classical structure can outweigh surrogate prediction savings. Complete scaling, offline accounting, and retained failures delimit these computational claims. Unknown demand, misspecified commitments, field calibration, and arbitrary retraining are different empirical targets and are not inferred from the present certificates.
'''

def inline(s):
    def f(m):
        path=ROOT/m.group(1)
        if not path.suffix:path=path.with_suffix('.tex')
        return '\n% BEGIN R21 source: '+str(path.relative_to(ROOT))+'\n'+inline(path.read_text())+'\n% END R21 source\n'
    return re.sub(r'\\input\{([^}]+)\}',f,s)
def bibliography(s):
    pat=r'(\\begin\{thebibliography\}\{99\})(.*?)(\\end\{thebibliography\})'
    def f(m):
        block=m.group(2).strip()+'\n'+ADDITIONS
        entries=re.findall(r'\\bibitem.*?(?=\\bibitem|\Z)',block,re.S)
        def key(x):
            body=x.split('\n',1)[1];return re.sub('[^a-z]','',body.split('(')[0].lower())
        return m.group(1)+'\n'+'\n'.join(sorted(entries,key=key))+'\n'+m.group(3)
    return re.sub(pat,f,s,flags=re.S)
def run():
    old=(P/'main.tex').read_text();ec=(P/'electronic_companion.tex').read_text();main=old
    start=main.index('% BEGIN preserved/input source: revisions/or-r19-20260923/sections/experiment.tex')
    marker='% END input source: revisions/or-r19-20260923/sections/experiment.tex';end=main.index(marker,start)+len(marker)
    preserved=main[start:end];main=main[:start]+''.join((R/'sections'/n).read_text()+'\n' for n in ['certification.tex','benchmark.tex','empirical.tex'])+main[end:]
    aa=main.index('Our first contribution');bb=main.index('\\subsection{Related literature',aa)
    main=main[:aa]+CONTRIBUTIONS+main[bb:]
    before='The main paper contains the institution,';aa=main.index(before);bb=main.index('% BEGIN preserved/input source: revisions/or-r14-20260922/sections/model.tex',aa)
    main=main[:aa]+(R/'sections/literature.tex').read_text()+'\nThe main manuscript follows this chain from the accepted-service problem to implemented expansion gains. The companion retains the full R19 empirical section and all earlier scalar and verified-cell material, alongside the new exact repair and reproduction details. No historical theorem or adverse result is removed.\n\n'+(R/'sections/early.tex').read_text()+'\n'+main[bb:]
    main=main.replace("We benchmark SciPy's sequential quadratic programming implementation alongside the preserved sparse Newton methods", "The preserved historical studies benchmark SciPy's sequential quadratic programming implementation alongside sparse Newton methods")
    aa=main.index('\\section{Conclusions and operational implications}');bb=main.index('\\section*{Data, software, and computation accessibility}',aa)
    main=main[:aa]+CONCLUSION+main[bb:]
    main=main.replace('New follow-up measurements are distinguished from retrospective analyses of the R16 dataset.','R21 final validation uses fresh seeds after a documented numerical-state audit; no pilot confidence bound is used as a final result. All new measurements are distinguished from retrospective analyses of the R16 dataset.')
    a=main.index('\\textbf{Abstract.}');b=main.index('\\par\\vspace',a)
    abstract=ABSTRACT
    if json.loads((R/'results/analysis.json').read_text())['minimum_expected_gain_lower']<=0:
        abstract=abstract.replace('Both ensembles achieve positive conditional expected-gain bounds in the recorded synthetic study;','Conditional expected-gain bounds are reported for both ensembles in the recorded synthetic study;')
    main=main[:a]+'\\textbf{Abstract.}\n'+abstract+'\n'+main[b:]
    main=re.sub(r'\{\\Large\\bfseries.*?\\par\}',lambda m:r'{\Large\bfseries Accepted Service Adaptation with\\ Neural Differential Utility:\\ Continuation Prices and Certified Gains\par}',main,count=1,flags=re.S)
    # Current EC material precedes the dated, complete archival sections.
    aa=ec.index('This companion retains');bb=ec.index('% BEGIN preserved/input source:',aa)
    intro=('This electronic companion contains the new R21 protocol and the complete preserved R19 empirical section, followed by all earlier scalar, verified-cell, and implementation developments. Historical wording is dated explicitly and is not pooled as new evidence. The R21 predecessor directory preserves the complete R19 root manuscripts byte for byte; older revision directories and the historical supplement are unchanged. The R19 fleet calculation is retained under its stated fixed-policy assumptions; the current empirical confidence claims use only the freshly reset final validation described below.\n\n')
    ec=ec[:aa]+intro+(R/'sections/companion.tex').read_text()+'\n'+preserved+'\n'+ec[bb:]
    ec=ec.replace('\\input{revisions/or-r21-20260923/tables/geometry.tex}', '\\input{revisions/or-r21-20260923/tables/geometry.tex}\n\\input{revisions/or-r21-20260923/tables/setup.tex}')
    for name,s in [('main',main),('electronic_companion',ec)]:
        s=s.replace(OLDTITLE,TITLE).replace('Revision R19, September 23, 2026','Revision R21, September 23, 2026')
        s=s.replace('NDU: Accepted Multistage Service Control','NDU: Accepted Service Adaptation')
        s=s.replace('\\onehalfspacing','\\renewcommand{\\efloatseparator}{\\par\\bigskip}\n\\onehalfspacing',1)
        s=bibliography(inline(s))
        (ROOT/(name+'.tex')).write_text(s)
    # The archival experimental block is preserved literally, including every number.
    assert preserved in (ROOT/'electronic_companion.tex').read_text()
    (R/'PRESERVATION_MAP.md').write_text('# R21 content preservation\n\nComplete R19 root sources and PDFs are snapshotted in `predecessor/`; their hashes are pinned by `PREDECESSOR_SHA256.json`. The complete R19 main experimental section, including all seven predictors, fleet inference, geometry checks, matched cost and adverse outcomes, is moved verbatim into the current electronic companion. Its SHA-256 is `'+hashlib.sha256(preserved.encode()).hexdigest()+'`.\n\nEvery pre-existing theorem, proposition, lemma and corollary statement in both R19 manuscripts remains verbatim in the combined current main/companion source. The current main retains all accepted-control, continuation, friction, transfer, global resource-price and inexact-response proofs. New sections add certificate components, price repair, a charged regularization bound, a benchmark gate, deterministic validation and full-class scaling. The introduction, abstract and conclusions are rewritten to organize this chain; their complete prior versions remain in the immutable predecessor sources.\n\nAll directories through R19, all review files, and `historical_supplement.pdf` are unchanged. Main and companion references resolve to their actual current or immutable predecessor PDFs. Tables remain after references but may share pages; no font or margin reduction is used to delete content or disguise manuscript length.\n')
    # Keep BibTeX source alongside the compiled inline author-year bibliography.
    bib=(P/'main.bib').read_text()+'\n% R21 additions; the manuscript contains the matching inline author-year entries.\n'
    data=[('AmosKolter2017','Amos, Brandon and Kolter, J. Zico','OptNet: Differentiable Optimization as a Layer in Neural Networks','Proceedings of Machine Learning Research','2017','70','136--145',''),('BertsimasKallus2020','Bertsimas, Dimitris and Kallus, Nathan','From Predictive to Prescriptive Analytics','Management Science','2020','66','1025--1044','10.1287/mnsc.2018.3253'),('ElmachtoubGrigas2022','Elmachtoub, Adam N. and Grigas, Paul','Smart Predict, then Optimize','Management Science','2022','68','9--26','10.1287/mnsc.2020.3922'),('KraulSeizingerBrunner2023','Kraul, Sebastian and Seizinger, Markus and Brunner, Jens O.','Machine Learning-Supported Prediction of Dual Variables for the Cutting Stock Problem with an Application in Stabilized Column Generation','INFORMS Journal on Computing','2023','35','692--709','10.1287/ijoc.2023.1277'),('Sambharya2024','Sambharya, Rajiv and Hall, Georgina and Amos, Brandon and Stellato, Bartolomeo','Learning to Warm-Start Fixed-Point Optimization Algorithms','Journal of Machine Learning Research','2024','25','1--46',''),('Stellato2020','Stellato, Bartolomeo and Banjac, Goran and Goulart, Paul and Bemporad, Alberto and Boyd, Stephen','OSQP: An Operator Splitting Solver for Quadratic Programs','Mathematical Programming Computation','2020','12','637--672','10.1007/s12532-020-00179-2')]
    for key,author,title,journal,year,volume,pages,doi in data:
        bib+='@article{'+key+',\n'+',\n'.join('  '+k+'={'+v+'}' for k,v in [('author',author),('title',title),('journal',journal),('year',year),('volume',volume),('pages',pages),('doi',doi)] if v)+'\n}\n'
    (ROOT/'main.bib').write_text(bib)
    print('Complete R21 main and companion sources assembled.')
if __name__=='__main__':run()
