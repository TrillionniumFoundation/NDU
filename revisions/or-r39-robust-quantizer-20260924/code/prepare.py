"""Prepare focused anonymous readers from preserved sources, without editing history."""
from pathlib import Path
import re, json, shutil, hashlib
R=Path(__file__).resolve().parents[1]; ROOT=R.parents[1]
OLD=ROOT/'revisions/or-r37-integrated-frontier-20260924'
rel=R.relative_to(ROOT).as_posix()
D=R/'derived'; D.mkdir(exist_ok=True)
(R/'generated').mkdir(parents=True,exist_ok=True)
P=R/'predecessor'; P.mkdir(exist_ok=True)
# Never replace a preserved predecessor with a subsequently generated reader.
for name in ('main.tex','electronic_companion.tex','main.pdf','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md'):
    if (ROOT/name).exists() and not (P/name).exists(): shutil.copy2(ROOT/name,P/name)

proofs=[]; proof_map=[]
def split_proofs(text, source):
    def replace(match):
        prefix=text[:match.start()]
        owners=list(re.finditer(r'\\begin\{(theorem|lemma|proposition|corollary)\}(?:\[[^\]]*\])?\s*\\label\{([^}]+)\}',prefix))
        if not owners: raise ValueError('Unmatched proof in '+source)
        kind,label=owners[-1].groups()
        tag='ec-proof-'+label.replace(':','-')
        body=match.group(0)
        proofs.append('\\subsection{Proof of '+kind.title()+'~\\ref{'+label+'}}\\label{'+tag+'}\n'+body+'\n')
        original=(ROOT/source).read_text()
        original_body=None
        for old in re.finditer(r'\\begin\{proof\}.*?\\end\{proof\}',original,re.S):
            old_owners=list(re.finditer(r'\\begin\{(theorem|lemma|proposition|corollary)\}(?:\[[^\]]*\])?\s*\\label\{([^}]+)\}',original[:old.start()]))
            if old_owners and old_owners[-1].group(2)==label:
                original_body=old.group(0); break
        if original_body is None: raise ValueError('Missing original proof '+label)
        assert original_body.replace('Theorem~\\ref{thm:minimal}','Theorem~\\ref{thm:clipped}')==body
        proof_map.append(dict(source=source,theorem_label=label,proof_label=tag,
                              original_proof_sha256=hashlib.sha256(original_body.encode()).hexdigest(),
                              cross_reference_normalized=original_body!=body,
                              proof_sha256=hashlib.sha256(body.encode()).hexdigest()))
        return '\\noindent The proof is in Electronic Companion Section~\\ref{'+tag+'}.\n'
    return re.sub(r'\\begin\{proof\}.*?\\end\{proof\}',replace,text,flags=re.S)

sources={
'deterministic.tex':OLD/'derived/deterministic.tex',
'lotteries.tex':ROOT/'revisions/or-r33-piecewise-randomized-20260923/randomized_memory.tex',
'global.tex':ROOT/'revisions/or-r34-global-randomized-frontier-20260923/global_frontier.tex',
'monge.tex':OLD/'monge_completion.tex'}
for name,path in sources.items():
    s=path.read_text()
    s=s.replace('Theorem~\\ref{thm:minimal}','Theorem~\\ref{thm:clipped}')
    if name=='deterministic.tex':
        marker='The earlier nonsaturated two-branch example'
        if marker in s:
            s,example=s.split(marker,1)
            (D/'historical_example.tex').write_text('\\section{A Further Nonsaturated Comparison}\n'+marker+example)
        s=s.replace('Exact implementation requires $k$ symbols.',
            'Exact implementation requires $k$ symbols under strict cap ordering; repeated caps are covered by Proposition~\\ref{prop:repeated}.')
    if name=='global.tex':
        s=s.replace('An Exact Global Randomized Memory Frontier','The Global Continuous Lottery Codebook')
        s=s.replace('A genuinely continuous optimal codebook','A continuous optimal highest level')
        s=s.replace('The electronic companion gives an implementation-level concordance.',
                    'The electronic companion gives an implementation-level concordance.')
    if name=='monge.tex':
        s=s.replace('Exact complete frontiers with linear work per layer',
                    'Contractual corollary of classical matrix search')
        s=s.replace('Linear rational work does not imply',
                    '$O(k)$ exact-rational oracle/comparison work per layer does not imply')
    (D/name).write_text(split_proofs(s,str(path.relative_to(ROOT))))
(D/'core_proofs.tex').write_text('\\section{Proofs for the Saturated Continuous Frontier}\n'+''.join(proofs))
(R/'PROOF_PRESERVATION.json').write_text(json.dumps(proof_map,indent=2)+'\n')

institution=(OLD/'institution.tex').read_text()
head,mechanism=institution.split('\\subsection{An operational mechanism, not an empirical calibration}',1)
head=head.replace('the exact threshold is not claimed for repeated caps or nonunique full optima.',
                  'Proposition~\\ref{prop:repeated} handles repeated caps; uniqueness is required for the exact-action lower bound.')
head+='''\n\\subsection{Acceptance timing}
The renewal desk observes the branch and offers the intermediate tier and terminal lottery. Under expected participation, the customer accepts before the ticket draw; after acceptance only the ticket reaches the common gateway. The realized ticket may be disclosed, but no new costless exit option is supplied after the draw within this episode. Under pathwise participation, each possible realized obligation must instead satisfy the branch cap, and a draw-specific intermediate tier is allowed. A seed known before acceptance changes that conditioning information. Repeated-customer effects require an enlarged state and are not part of the three-date theorem. The full stipulated mechanism and its qualifications are given in the electronic companion; no empirical or legal claim about an actual provider is made. Section~\\ref{sec:promise} allows a nonsaturated root promise, and Section~\\ref{sec:catalog} specifies the intermediate risk protocol.\n'''
(D/'institution.tex').write_text(head)
mechanism=mechanism.replace('This is a documented stylized mechanism','This is a stipulated stylized mechanism')
(D/'mechanism.tex').write_text('\\section{Detailed Renewal Protocol}\n'+mechanism)

oracle=(OLD/'derived/oracle_concordance.tex').read_text().replace(
'The complete structural and algorithmic proofs appear in the article;',
'The complete structural and algorithmic proofs appear in this companion;')
(D/'oracle_concordance.tex').write_text(oracle)
method=(OLD/'methodology.tex').read_text()
method=method.replace('The inherited R33--R36 suites','The predecessor exact suites')
method += r'''
\subsection{Pinned independent search identity}
The independently authored search excerpt is from David Eppstein's PADS mirror, commit
\begin{quote}\ttfamily\small a6f82ff6f2d60d52a02f7b816ae7b1dfc431b5d9.\end{quote}
The original search blob is \texttt{0a94e9e685130f7f79262c52761414c33226214d}; the license blob is \texttt{af71e1c36786aef6226d34e3999787051343ee9a}. The distributed excerpt retains the MIT copyright and permission notice. It is an excerpt with an unchanged executable offline function, not a byte-identical copy of the entire upstream file. These identities distinguish the external search layer from the shared contractual oracle.
'''
(D/'methodology.tex').write_text(method)
resources=(OLD/'static_tables.tex').read_text()
resources=resources[resources.index('\\begin{table}[p]',resources.index('\\end{table}')+11):]
(D/'accounting_table.tex').write_text(resources)

# The numerical figure is defined analytically, so no image or fitted data are substituted.
(R/'figure.tex').write_text(r'''
\begin{figure}[tb]\centering
\begin{tikzpicture}
\begin{axis}[width=.8\textwidth,height=5cm,xlabel={Highest terminal level $z$},
 ylabel={Two-symbol service loss},xmin=.5,xmax=.75,ymin=.0177,ymax=.0191,
 scaled y ticks=false,yticklabel style={/pgf/number format/fixed,/pgf/number format/precision=4},
 xtick={.5,.625,.75},xticklabels={$1/2$,$5/8$,$3/4$}]
\addplot[domain=.5:.75,samples=101,thick]{x*x/20-x/16+3/80};
\addplot[only marks] coordinates {(.625,.01796875)};
\node[anchor=south] at (axis cs:.625,.01803) {$23/1280$};
\end{axis}\end{tikzpicture}
\caption{The analytically optimized highest level in the heterogeneous three-branch example. The lower level is $1/4$. The displayed function is $z^2/20-z/16+3/80$ on $[1/2,3/4]$; its interior minimum is $z=5/8$, not a branch cap.}\label{fig:top-loss}
\end{figure}
''')

# Executed results, not guessed counts, enter the reader.
verification=json.loads((R/'results/verification.json').read_text())
assert verification['status']=='PASS'
c=verification['counts']
evidence=r'''\section{Verification and Computational Evidence}\label{sec:r37-evidence}
The computational package separates exact finite checks, practical measurements, and a standard-quantizer comparison. The theorems establish the all-size and continuous claims; finite checks are regression evidence. Prices and branch populations are synthetic inputs, not empirical estimates.

\paragraph{New promise and catalog checks.}
Independent enumeration of all catalog subsets and all one/two-point branch supports agrees with every reported finite-catalog frontier, without assuming adjacent support in the comparison oracle. Tests include repeated caps, noncap catalog entries, zero intermediate curvature, nonuniform charges, and zero, intermediate, and unrestricted overrun tolerances. Clipped allocations satisfy exact weighted promises and allocation optimality conditions; direct scaling and saturation lifts verify the value inequalities on heterogeneous policies. Fixed-book responses are checked for concavity across their kinks. Invalid floating-point and malformed inputs are rejected.

'''
evidence+=f"The executed suite records {c['catalog_frontier_equalities']:,} catalog frontier equalities, {c['direct_support_book_checks']:,} direct-support book checks, {c['promise_scaling_lift_checks']:,} scaling/lift checks, {c['clipped_kkt_checks']:,} clipped-allocation checks, {c['fixed_book_concavity_checks']:,} response-concavity checks, and {c['repeated_cap_checks']:,} repeated-cap equalities. The charge-switch example and the interval in \\eqref{{eq:robust-interval}} are checked in exact fractions.\n"
evidence+=r'''
\paragraph{Comparison with an ordinary scalar quantizer.}
The baseline recursion over ordered cells is the same recursion used for scalar mean-square quantization; the cell oracle is not. For the three equal-probability caps, both optimal two-cell mean-square partitions have loss $1/96$. Their centroids are $(1/4,5/8)$ or $(3/8,3/4)$, respectively. Each merged cell includes a branch whose cap is below its centroid, so that centroid reconstruction is infeasible under the pathwise contract, even with nonnegative intermediate service. This exact comparison identifies the changed objective and constraint rather than benchmarking two algorithms that solve different problems. The expected contract instead uses the classical unbiased encoder with a contractual tail.

\paragraph{Inherited continuous-frontier evidence.}
The complete preceding exact suite, including completion ties, selected all-padded rows, controller replay, independent PADS substitution, and earlier regression suites, is rerun in isolated directories. Historical source and result files are not overwritten. The preceding process-isolated continuous-frontier timings through 16,384 branches and reduced-network HiGHS certificates are retained with their original provenance in the companion. The HiGHS comparison validates the finite reduction, not the cap-anchoring theorem or performance at the larger scale. PADS substitutes the search layer only. Neither comparison is presented as a new experiment on operational data.

\paragraph{Additional catalog landscapes.}
The executed catalog study uses uniform caps, two separated cap clusters, and a population with concentrated branch weights. Each family is evaluated at $(k,N)=(32,16)$ and $(128,32)$, eight-symbol capacity, and tolerances $0,1/8,1$, with heterogeneous curvatures and level prices. All 18 cases reconstruct and replay their selected books exactly. Times include catalog construction inside the solver, the dynamic program, reconstruction, and direct replay in one process; they are not directly compared with the predecessor's process-isolated timings. Full numerical records and the timing definition accompany the code.
'''
allocation=json.loads((R/'results/allocation_validation.json').read_text())
assert allocation['status']=='PASS'
ac=allocation['counts']
evidence+='\nThe nonsaturated extension additionally passes '+str(ac['allocation_dual_equalities'])+' exact primal/dual-event comparisons, '+str(ac['supporting_branch_maxima'])+' supporting branch maxima, '+str(ac['saturated_catalog_equalities'])+' saturated catalog/DP equalities, '+str(ac['all_promise_catalog_checks'])+' interior-promise catalog comparisons, and '+str(ac['pairwise_policy_transport_checks'])+' arbitrary-promise transport checks. The supporting-price equality certifies each fixed-book solution; finite regression is not used as proof of the general theorem.\n'
(R/'evidence.tex').write_text(evidence)
(R/'generated/allocation_evidence.tex').write_text('\\subsection{Executed allocation checks}\nThe executed exact suite reports '+str(ac['allocation_dual_equalities'])+' primal/dual-event equalities and '+str(ac['supporting_branch_maxima'])+' supporting branch maxima. It includes repeated caps, zero curvatures, singleton books, endpoint promises, and nonsaturated charged-book selection. Full rational values and checks are in the allocation validation record.\n')

# Carry forward detailed measured tables and their raw sources, clearly dated by provenance.
(D/'legacy_evidence.tex').write_text((OLD/'evidence.tex').read_text().replace(
'\\section{Verification and Computational Decision Support}\\label{sec:r37-evidence}',
'\\section{Preserved Continuous-Frontier Measurements}\\label{ec:legacy-evidence}')
.replace('The new tests','The preceding tests').replace('All current measurements','All preserved measurements'))

preamble=(P/'main.tex').read_text().split('\\begin{document}')[0]
preamble=re.sub(r'\\externaldocument[^\n]*\n','',preamble)
preamble=re.sub(r'\\hypersetup\{pdftitle=.*?\}\n','',preamble)
preamble=preamble.replace('Service Contracts with Limited Memory','Limited-Memory Renewal Contracts')
preamble=preamble.replace('\\usepackage{fancyhdr}',r'\usepackage{fancyhdr,graphicx,pgfplots}'+ '\n'+r'\pgfplotsset{compat=1.18}')
abstract='''A renewal agreement can reach one execution state with different accepted obligations while retaining only a finite service symbol. We derive the resulting quantizer design from participation and continuation promises. In the saturated quadratic model, an optimal expected-participation codebook has cap-anchored nonhighest levels and a continuously optimized highest level that can lie strictly between caps. Contractual terminal costs remain Monge after continuous minimization, making classical matrix search applicable. Pathwise participation eliminates the saturated lottery advantage. We then characterize the full-information alphabet for every root promise and prove budget-uniform bounds between every pair of promises, with exact fixed-book allocation certificates. Strict saturated institutional advantages persist on explicit nonsaturated intervals. For arbitrary finite certification catalogs, a second exact dynamic program jointly selects codewords, bounded-overrun lotteries, and additive charges for the actual chosen levels. An example shows why pricing a previously loss-minimizing codebook is insufficient. We distinguish these contractual results from classical scalar quantization, unbiased stochastic rounding, dual quantization, and finite-rate control. Exact tests, independent support enumeration and search substitution, and provenance-preserving computational evidence assess the implementations.'''
(R/'ABSTRACT.txt').write_text(abstract+'\n')
def inp(name):return '\\input{'+rel+'/'+name+'}\n'
main=preamble+'\\externaldocument{r39-ec-labels}[electronic_companion.pdf]\n'
main+='\\hypersetup{pdftitle={Limited-Memory Renewal Contracts: Participation, Quantization, and Exact Design},pdfauthor={Anonymous}}\n'
main+=r'\begin{document}\hypersetup{pageanchor=false}'+'\n'
main+=r'''\begin{titlepage}\centering
{\Large\bfseries Limited-Memory Renewal Contracts:\newline Participation, Quantization, and Exact Design\par}
\vspace{.3in}Anonymous manuscript for Operations Research\par\vspace{.2in}
\begin{minipage}{\textwidth}\textbf{Abstract.} '''+abstract+r'''
\par\vspace{.15in}\textbf{Keywords:} renewal contracts; quantization; dynamic programming.
\par\vspace{.1in}\textbf{Subject classifications:} Dynamic programming: service design; Programming: resource allocation.
\par\vspace{.1in}\textbf{Area of review:} Optimization.
\end{minipage}\vfill September 24, 2026\end{titlepage}
\hypersetup{pageanchor=true}
'''
for f in ['introduction.tex','positioning.tex','derived/institution.tex','derived/deterministic.tex',
          'derived/lotteries.tex','derived/global.tex','derived/monge.tex','promise_robustness.tex',
          'catalog_design.tex','figure.tex','resources.tex','evidence.tex','conclusion.tex']:
    main+=inp(f)
main+=inp('data_statement.tex')
main+='\\clearpage\\phantomsection\\label{refs-start}\n'+inp('generated/references.tex')+'\\label{refs-end}\n\\clearpage\n'+inp('novelty_table.tex')+'\\end{document}\n'
(ROOT/'main.tex').write_text(main)

ec=preamble+'\\externaldocument{r39-main-labels}[main.pdf]\n'
ec+=r'''\renewcommand{\thesection}{EC.\arabic{section}}
\renewcommand{\theequation}{EC.\arabic{equation}}
\renewcommand{\thetable}{EC.\arabic{table}}
\hypersetup{pdftitle={Electronic Companion: Limited-Memory Renewal Contracts},pdfauthor={Anonymous}}
\begin{document}
\begin{center}{\Large\bfseries Electronic Companion}\par
Limited-Memory Renewal Contracts: Participation, Quantization, and Exact Design\end{center}
This companion supplies the detailed proofs and implementation evidence used by the article. It is self-contained together with the article; the broader historical response-compilation program is preserved separately in the repository and is not a hidden premise of the current theorems.
'''
for f in ['derived/core_proofs.tex','derived/mechanism.tex','derived/historical_example.tex',
          'derived/oracle_concordance.tex']:
    ec+=inp(f)
ec+='\\input{revisions/or-r37-integrated-frontier-20260924/bounded_overrun.tex}\n'
ec+=inp('allocation_companion.tex')+inp('generated/allocation_evidence.tex')+inp('derived/methodology.tex')+inp('derived/legacy_evidence.tex')
ec+=inp('derived/accounting_table.tex')+'\\clearpage\n'
ec+='\\input{revisions/or-r37-integrated-frontier-20260924/generated/main_tables.tex}\n'
ec+='\\clearpage\\input{revisions/or-r37-integrated-frontier-20260924/generated/companion_tables.tex}\n'
ec+=inp('generated/catalog_table.tex')+'\\clearpage\n'+inp('generated/references.tex')+'\\end{document}\n'
(ROOT/'electronic_companion.tex').write_text(ec)

# References are selected from the union of reader inputs, retaining predecessor metadata.
alltex='\n'.join([main,ec]+[p.read_text() for p in R.glob('*.tex')]+[p.read_text() for p in D.glob('*.tex')]
                 +[(OLD/'bounded_overrun.tex').read_text(),(OLD/'methodology.tex').read_text()])
keys=set()
for hit in re.findall(r'\\cite\w*(?:\[[^\]]*\])*\{([^}]+)\}',alltex):keys.update(hit.split(','))
base=(OLD/'generated/main_references.tex').read_text()+'\n'+(OLD/'generated/companion_references.tex').read_text()+'\n'+(R/'new_references.tex').read_text()
items={}
for hit in re.finditer(r'(\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}.*?)(?=\\bibitem|\\end\{thebibliography\}|\Z)',base,re.S):
    items[hit.group(2)]=hit.group(1).strip()
missing=keys-items.keys()
if missing:raise ValueError('Unresolved bibliography keys: '+str(missing))
(R/'generated/references.tex').write_text('\\begin{thebibliography}{99}\\raggedright\n'+
    '\n\n'.join(items[k] for k in sorted(keys,key=lambda k: re.sub(r'[^A-Za-z0-9 ]','',items[k].split('\n',1)[1]).lower()))+'\n\\end{thebibliography}\n')

study=json.loads((R/'results/catalog_study.json').read_text())
rows=study['rows']
table=r'''\section{Additional Catalog Measurements}
\begin{longtable}{@{}lrrrrrr@{}}
\caption{Executed synthetic catalog designs; eight-symbol budget.}\\
\toprule Family & $k$ & $N$ & $\delta$ & Used & Total cost & Seconds\\\midrule\endfirsthead
\toprule Family & $k$ & $N$ & $\delta$ & Used & Total cost & Seconds\\\midrule\endhead
\bottomrule\endfoot
'''
for x in rows:
    fam={'uniform':'Uniform','clustered':'Clustered','concentrated_weights':'Concentrated'}[x['family']]
    from fractions import Fraction
    table+=f"{fam} & {x['k']} & {x['N']} & {x['delta']} & {x['symbols']} & {float(Fraction(x['total'])):.6f} & {x['seconds']:.4f} \\\\\n"
table+='\\end{longtable}\nTotal cost includes actual selected-level charges. Values are displayed in decimal only for readability; every stored objective and replay uses exact fractions. The included timing scope differs from the preserved continuous-frontier measurements.\n'
(R/'generated/catalog_table.tex').write_text(table)
print('Prepared main and focused companion; preserved',len(proof_map),'complete proof blocks.')
