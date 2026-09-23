#!/usr/bin/env python3
"""Assemble the R29 reader documents from preserved R28 blocks and new results.
Historical scientific sources are never edited in place.
"""
from pathlib import Path
import shutil,hashlib,json,re,subprocess
R=Path(__file__).resolve().parent; ROOT=R.parent.parent
PFX='revisions/'+R.name
BASE='af01e2c33f85835e550896985b7cb83b3f4b784f'
READERS=['main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md']

def between(s,a,b):return s[s.index(a):s.index(b)]

def main():
    pre=R/'predecessor';pre.mkdir(exist_ok=True)
    for f in READERS:
        if not (pre/f).exists():shutil.copy2(ROOT/f,pre/f)
    manifest=R/'INHERITED_SHA256.json'
    if not manifest.exists():
        if (ROOT/'.git').exists():
            files=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines()
        else:
            files=[str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and R not in p.parents and '__pycache__' not in p.parts]
        manifest.write_text(json.dumps({f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in sorted(files)},indent=2)+'\n')
    old=(pre/'main.tex').read_text();ec=(pre/'electronic_companion.tex').read_text()
    title='Accepted Service Adaptation: Finite Continuation Prices and the Value of Memory'
    abstract=('A service provider with renewal participation constraints must decide how much past information to retain. '
    'We identify a class of continuous-tier contracts in which exact optimal adaptation can be constructed on a recombining public graph without enumerating histories. '
    'Positive additive payments, quadratic operating rewards, and the absence of intertemporal switching make each continuation cap introduce at most one new payment-price threshold. '
    'A finite global breakpoint set yields an explicit arithmetic complexity bound, while the optimizer retains only the largest threshold encountered along the realized history. '
    'We prove a matching linear-order lower bound on the number of necessary memory labels and derive an exact memory-value frontier for a family of renewal agreements. '
    'A graph-sized quadratic program optimizes a shared zero-release table; at positive release, the finite-price construction supplies exact fixed-table values and supporting cuts. '
    'The broader switching, release-rent, promise-state, and deployment results are retained with their proofs. '
    'Exact coupled-graph experiments extend to 64 dates and include independent tree and shared-table checks. '
    'Earlier unfavorable cache evidence remains explicit: 83 of 84 strict-tolerance queries refreshed, without a measured cache speed advantage.')
    assert len(abstract.split())<=200
    (R/'abstract.txt').write_text(abstract+'\n')
    preamble=old[:old.index('\\begin{document}')]
    preamble=preamble.replace('r28-ec-labels','r29-ec-labels')
    preamble=re.sub(r'\\hypersetup\{pdftitle=.*?pdfauthor=\{Anonymous\}\}',r'\\hypersetup{pdftitle={'+title+r'},pdfauthor={Anonymous}}',preamble)
    preamble+=r'\externaldocument{r29-retained-labels}[revisions/or-r29-price-state-20260923/retained_evidence.pdf]'+'\n'
    front=r'''\begin{document}
\begin{titlepage}\centering
{\Large\bfseries Accepted Service Adaptation:\\ Finite Continuation Prices\\ and the Value of Memory\par}
\vspace{.35in}{Anonymous manuscript for Operations Research\par}\vspace{.25in}
\begin{minipage}{\textwidth}
\textbf{Abstract.} '''+abstract+r'''
\par\vspace{.15in}\textbf{Keywords:} continuation participation; contractual memory; stochastic optimization.
\par\vspace{.1in}\textbf{Subject classifications:} Dynamic programming/optimal control: service adaptation; Programming: stochastic models; Inventory/production: service contracts.
\par\vspace{.1in}\textbf{Area of review:} Stochastic Models.
\end{minipage}\vfill{Revision R29, September 23, 2026\par}
\end{titlepage}
'''
    literature=between(old,'\\section{Relation to Dynamic Contracting','\\input{revisions/or-r28-20260923/novelty_table.tex}')
    model=between(old,'\\section{A Service Agreement','\\section{The Value Frontier')
    inherited=between(old,'\\section{The Value Frontier','\\section{Computational Evidence}')
    (R/'inherited_mathematics.tex').write_text(inherited)
    # Exact old mathematical body is retained. Only the presentation of the
    # representability statement is clarified in a copy of its included file.
    bridge=(ROOT/'revisions/or-r28-20260923/bridge_main.tex').read_text()
    bridge=bridge.replace('dual-complete','extensive-form-dual representable').replace('dual complete','extensive-form-dual representable')
    bridge=bridge.replace('root linear program','Benders-style root linear program')
    (R/'bridge_main.tex').write_text(bridge)
    active_inherited=inherited.replace('revisions/or-r28-20260923/bridge_main.tex',PFX+'/bridge_main.tex')
    conclusion=r'''\section{Conclusions}
Nested continuation participation has two distinct consequences. For general accepted adaptation it creates scarcity prices, release rents, and a need to carry outstanding promises. For the separable no-switching subclass, those prices admit a stronger construction: each public cap contributes at most one threshold, and an optimizer carries a finite running-maximum record rather than the history tree. The resulting exact graph algorithm, its memory lower bound, and the memory-value frontier give substantive content to the information architecture.

The shared table remains a commitment chosen once. Its zero-release value has a graph-sized formulation, and its positive-release subproblems have exact tree-free price oracles under the finite-price assumptions. Broader switching and correlated-certificate results remain valid under their separately stated assumptions. They are not used to infer a complexity bound that their proofs do not supply. The computational record distinguishes exact structural checks, single-run cost measurements, and the unchanged adverse historical evidence.

\section*{Data and Code Accessibility}
The code/data package contains all rational primitive graphs, compact primal--dual certificates, independent verifiers, small-tree matrix and numerical comparisons, optimized-table KKT records, memory partitions, scripts, and build checks. The complete R28 manuscript, companion, and reader files are preserved byte for byte, as are all earlier repository derivations. Its complete numerical narrative and tables are additionally typeset in the retained computational appendix. No historical mathematical statement, proof, or unfavorable result is silently discarded. No field data are used. Repository delivery is for author/referee scrutiny, not a journal submission or a representation of editorial acceptance.

\appendix
\section*{Print Appendices: General Accepted Adaptation}
The following results preserve the broader mathematical framework. The finite-price theorem does not require the deployment certificates or conditional continuous-state approximation rates. These appendices state what remains valid when the tractable no-switching specialization is not imposed; the electronic companion retains their detailed proofs and all qualifications.
'''
    new=preamble+front+f'\\input{{{PFX}/metrics.tex}}\n'+f'\\input{{{PFX}/intro.tex}}\n'+literature+f'\\input{{{PFX}/modern_literature.tex}}\n'+model
    for f in ['price_main','memory_main','shared_main','evidence_main']:new+=f'\\input{{{PFX}/{f}.tex}}\n'
    new+=conclusion+active_inherited+f'\n\\input{{{PFX}/references.tex}}\n\\end{{document}}\n'
    (ROOT/'main.tex').write_text(new)
    ec=ec.replace('r28-main-labels','r29-main-labels').replace('Revision R28','Revision R29')
    ec=ec.replace('Accepted Service Adaptation: Shared Policy Tables, Continuation Prices, and Certified Design',title)
    ec=ec.replace('\\begin{document}',r'\externaldocument{r29-retained-labels}[revisions/or-r29-price-state-20260923/retained_evidence.pdf]'+'\n'+r'\begin{document}')
    ec=ec.replace('\\section{Identified Stocks',f'\\input{{{PFX}/checks_ec.tex}}\n\\section{{Identified Stocks',1)
    ec=ec.replace('revisions/or-r28-20260923/references.tex',PFX+'/references.tex')
    (ROOT/'electronic_companion.tex').write_text(ec)
    evidence=between(old,'\\section{Computational Evidence}','\\section{Conclusions}')
    (R/'retained_evidence_body.tex').write_text(evidence)
    retained_preamble=old[:old.index('\\begin{document}')]
    retained_preamble=retained_preamble[:retained_preamble.index('\\externaldocument')]
    retained_preamble+=r'''\externaldocument{r29-retained-source-main-labels}[predecessor/main.pdf]
\externaldocument{r28-ec-labels}[predecessor/electronic_companion.pdf]
\hypersetup{pdftitle={Retained R28 Computational Evidence},pdfauthor={Anonymous}}
\begin{document}
\begin{center}{\Large\bfseries Retained Computational Appendix}\par
Unabridged R28 numerical narrative and tables\par
Preserved with Revision R29, September 23, 2026\end{center}
This document preserves the complete predecessor evidence, including its unfavorable cache and learning outcomes. Its numerical observations are historical R24--R28 records, not new measurements of the R29 finite-price algorithm. References to the earlier manuscript and companion link to their byte-preserved copies. The predecessor result-comparison table is also retained below; the new paper's research positioning is given in its current literature section.
\input{revisions/or-r28-20260923/novelty_table.tex}
'''
    retained=retained_preamble+evidence+f'\n\\input{{{PFX}/references.tex}}\n\\end{{document}}\n'
    (R/'retained_evidence.tex').write_text(retained)
    labels=(ROOT/'r28-main-labels.aux').read_text().splitlines()
    (ROOT/'r29-retained-source-main-labels.aux').write_text('\n'.join(x for x in labels if not x.startswith(r'\newlabel{tab:') and not x.startswith(r'\newlabel{sec:evidence}') and not x.startswith(r'\newlabel{eq:amortization}'))+'\n')
    preservation={'baseline_commit':BASE,'reader_predecessors':{f:hashlib.sha256((pre/f).read_bytes()).hexdigest() for f in READERS},
       'mathematics_block_sha256':hashlib.sha256(inherited.encode()).hexdigest(),
       'retained_evidence_block_sha256':hashlib.sha256(evidence.encode()).hexdigest(),
       'operations':['reordered all inherited mathematical statements/proofs into print appendices',
        'preserved unabridged old empirical narrative and tables in a compiled computational appendix',
        'clarified dual representability in a copied bridge source; original unchanged',
        'replaced introduction, synthesis and literature positioning; originals byte-preserved']}
    (R/'PRESERVATION.json').write_text(json.dumps(preservation,indent=2)+'\n')
    for source,target in [('README.template.md','README.md'),('submission_checklist.template.md','NDU_OR_submission_checklist.md')]:
        shutil.copy2(R/source,ROOT/target)
    print('Assembled R29; abstract words:',len(abstract.split()))

if __name__=='__main__':main()
