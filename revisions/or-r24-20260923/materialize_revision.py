"""Build ordinary standalone R24 manuscripts from the pinned R23 sources.
Scientific statements/proofs and empirical tables are relocated, never silently
omitted. The one robust-result environment is relabeled as a lemma explicitly.
"""
from pathlib import Path
import re
R=Path(__file__).resolve().parent;REPO=R.parent.parent
TITLE='Accepted Service Adaptation: Continuation Prices, Transfer Coordinates, and Certified Gains'

def subtext(text,start,end):
    a=text.index(start);b=text.index(end,a);return text[a:b]

def main():
    original=(R/'predecessor/main.tex').read_text(); oldec=(R/'predecessor/electronic_companion.tex').read_text()
    m=original;e=oldec
    canonical=subtext(m,r'\section{An externally priced inventory contract}',r'\section{Identification and a unified accepted-control problem}')
    m=m.replace(canonical,'')
    intro=subtext(m,r'\section{Introduction}',r'\subsection{Related literature and the incremental contribution}')
    m=m.replace(intro,(R/'sections/introduction.tex').read_text())
    oldtitle='Accepted Service Adaptation with Neural Differential Utility: Continuation Prices and Robust Certified Gains'
    m=m.replace(oldtitle,TITLE)
    m=m.replace(r'Accepted Service Adaptation with\\ Neural Differential Utility:\\ Continuation Prices and Robust Certified Gains',r'Accepted Service Adaptation:\\ Continuation Prices, Transfer Coordinates,\\ and Certified Gains')
    m=m.replace('Revision R23,','Revision R24,')
    abstract='''Contractual service adaptation creates value only when customers accept every continuation and physical commitments remain feasible. We characterize accepted expansion relative to an optimized restricted contract on finite history trees. Cumulative continuation prices and switching capacities identify profitable deviations and critical friction. With positive scalar payment coefficients, benchmark-relative transfer coordinates parametrize the entire accepted class, including nonconstant contracts and unused participation slack, and yield an exact quadratic expansion formula. Constructive tension repair supplies gain witnesses and threshold bounds. Independent primal--dual certificates connect these geometric results to implemented decisions and economically meaningful comparators. Under explicit strong convexity and smooth resource coupling, a resource-reward value gradient provides one implementation statistic; neural, direct-price, and classical methods remain alternatives. Component and complete-dual repair identify attainable certification accuracy without strict feasibility. Synthetic studies retain the full accepted polyhedron, optimized time-only comparators, and frozen-policy validation. New repeated-query measurements charge labels, fitting, auditing, and fallback against lifted continuation. Direct interior-model optimization quantifies the conservatism of robust comparator certificates under designed joint coefficient uncertainty. The results separate the value of accepted expansion from the approximation and computational costs of recovering it.'''
    a=m.index('Service providers can revise contractual tiers');b=m.index(r'\par\vspace{.16in}',a)
    m=m[:a]+abstract+'\n'+m[b:]
    m=m.replace('accepted service control; resource prices; value-gradient decisions.','accepted service adaptation; continuation participation; certified optimization.')
    m=m.replace('The canonical sections below derive','The canonical sections in the electronic companion derive')
    m=m.replace(r'\section{Identification and a unified accepted-control problem}',(R/'sections/service_summary.tex').read_text()+'\n'+r'\section{Identification and a unified accepted-control problem}')
    m=m.replace(r'\section{A value-gradient implementation on general accepted polyhedra}',(R/'sections/benchmark_transfers.tex').read_text()+'\n'+r'\section{A value-gradient implementation on general accepted polyhedra}')
    # Compact main focus; all retained mathematical and numerical content is accessible.
    m=m.replace('Cumulative continuation prices, accepted transfer coordinates, subtree cuts and constructive service deviations: accepted-control structure.','Cumulative continuation prices, subtree cuts and constructive service deviations; Theorem~\\ref{thm:r24-transfers} gives exact coordinates around a reoptimized contract with slack: accepted-control structure.')
    m=m.replace('The main manuscript follows this chain from the accepted-service problem to implemented expansion gains. The companion retains the full R19 empirical section and all earlier scalar and verified-cell material, alongside the new exact repair and reproduction details. No historical theorem or adverse result is removed.',
      'The main manuscript develops the accepted-control structure and its implemented economic certificates. The electronic companion retains the canonical inventory model and all remaining formal derivations. The Computational Supplement retains every relocated empirical table and execution detail, including adverse comparisons; it also reports the new complete diagnostic distributions.')
    # Relocate nonessential empirical machinery out of the formal companion.
    moved=[]
    first=subtext(e,r'\subsection{Recorded objects and independent verification}',r'\section{Repeated learning, difficult geometry, and complete deployment cost}')
    e=e.replace(first,'');moved.append(r'\section{R22 recorded objects and independent verification}'+first.replace(r'\subsection{Recorded objects and independent verification}','',1))
    study=subtext(e,r'\section{Repeated learning, difficult geometry, and complete deployment cost}',r'\section{Current study: primitives, audits, and reproducibility}')
    fleet=subtext(study,r'\begin{proposition}[Conditional frozen-fleet guarantee]',r'For $K=8$')
    moved.append(study.replace(fleet,'The conditional frozen-fleet proposition and its full proof remain in Electronic Companion Section~\\ref{ec:r24-fleet}.\n'))
    e=e.replace(study,r'\section{The preserved conditional frozen-fleet guarantee}\label{ec:r24-fleet}'+'\nThe following result concerns the historical randomized frozen fleet, not the current deterministic ensemble target. The observations and interpretation remain in Computational Supplement Section~\\ref{sec:r19-experiment}.\n'+fleet+'\n')
    primitive=subtext(e,r'\section{Current study: primitives, audits, and reproducibility}',r'\section{Primitive structure under continuation participation}')
    e=e.replace(primitive,'');moved.append(primitive)
    experiments=subtext(e,r'\section{Nonsmooth service decisions and frozen learning pipelines}',r'\section{Implementation details for verified continuation cells}')
    e=e.replace(experiments,'');moved.append(experiments)
    implementation=subtext(e,r'\section{Implementation details for verified continuation cells}',r'\section{Proof of the global resource-price bridge}')
    # Keep the analytical sparse Lipschitz construction in the formal companion.
    analytic=subtext(implementation,r'\subsection{Sparse Lipschitz bounds without fill-in}',r'\subsection{Cell recovery and rejection}')
    e=e.replace(implementation,r'\section{Sparse bounds for verified continuation cells}\label{ec:r24-sparse}'+'\n'+analytic)
    moved.append(implementation.replace(analytic,'The analytical sparse bound remains in Electronic Companion Section~\\ref{ec:r24-sparse}.\n'))
    # Add the complete canonical institutional development, preserving its blocks.
    ecbody=e.index(r'\section{R22 design, exact restricted repair, and replay}')
    e=e[:ecbody]+canonical+'\n'+e[ecbody:]
    e=e.replace(oldtitle,TITLE).replace('Revision R23,','Revision R24,')
    oldintro=subtext(e,'This electronic companion contains',r'\section{An externally priced inventory contract}')
    e=e.replace(oldintro,'This companion contains the complete canonical service institution and all formal derivations relocated from the main paper. Every predecessor mathematical statement and proof remains in the current main or companion. Numerical experiments and execution details moved to the Computational Supplement retain their original sources, dates, and adverse results. The R19 randomized-fleet result remains distinct from the R22 deterministic frozen-policy validation.\n\n')
    e=e.replace('R22 starts from the complete R19 manuscript, not from an unexecuted result attributed to the R20 plan. The newest referee report is dated September 23, 2026. Its reviewed tip contains only that plan beyond the R19 publication. The current sources, manuscripts, response, raw results, and final-checkout tests form one completed object.',
                'This subsection records the preserved R22 design and its numerical-state correction. The historical R20 review pointer concerns an earlier plan-only tip; R24 responds instead to the completed R23 manuscript and its September 23 report. The R22 observations remain a separate completed study.')
    # Same statement/proof, explicit theorem-to-lemma relabeling requested by R23.
    for textname in ('m','e'):
        text=locals()[textname]
        text=text.replace(r'Theorem~\ref{thm:r23-robust}',r'Lemma~\ref{thm:r23-robust}')
        pat=r'\\begin\{theorem\}\[Robust accepted expansion against a model-specific comparator\](.*?)\\end\{theorem\}'
        text=re.sub(pat,lambda z:r'\begin{lemma}[Robust accepted expansion against a model-specific comparator]'+z.group(1)+r'\end{lemma}',text,flags=re.S)
        if textname=='m':m=text
        else:e=text
    # Update document destinations without altering the relocated statements.
    cslabels=['sec:r19-experiment','ec:r19-details','sec:r13-experiment','sec:r14-experiment','ec:r13-implementation','ec:r14-details']
    for lab in cslabels:
        for prefix in ['EC Section~','Electronic Companion Section~']:
            m=m.replace(prefix+r'\ref{'+lab+'}',r'Computational Supplement Section~\ref{'+lab+'}')
            e=e.replace(prefix+r'\ref{'+lab+'}',r'Computational Supplement Section~\ref{'+lab+'}')
    m=m.replace(r'\section{Conclusions}',(R/'sections/diagnostics.tex').read_text()+'\n'+r'\section{Conclusions}')
    conclusion_start=m.index(r'\section{Conclusions and operational implications}')
    conclusion_end=m.index(r'\section*{Data, software, and computation accessibility}',conclusion_start)
    m=m[:conclusion_start]+(R/'sections/conclusions.tex').read_text()+'\n'+m[conclusion_end:]
    # The actual header is singular in some predecessors.
    if r'\label{sec:r24-diagnostics}' not in m:
        marker=next(x for x in re.findall(r'\\section\{[^}]*\}',m) if 'Conclusion' in x)
        m=m.replace(marker,(R/'sections/diagnostics.tex').read_text()+'\n'+marker)
    m=m.replace('The current README identifies a single main manuscript and electronic companion.',
                'The current README identifies the main manuscript, formal electronic companion, and separate computational supplement. R24 adds benchmark-relative transfer coordinates, independently checked interior-comparator diagnostics, repeated-query cost components, and an explicit comparison of online and offline certification protocols.')
    m=m.replace(r'\fancyhead[L]{\small NDU: Accepted Service Adaptation}',r'\fancyhead[L]{\small Accepted Service Adaptation}')
    e=e.replace(r'\fancyhead[L]{\small NDU: Electronic Companion}',r'\fancyhead[L]{\small Accepted Service Adaptation: Companion}')
    # Cross-document references are resolved by the multi-pass build.
    m=m.replace(r'\externaldocument{ec-labels}[electronic_companion.pdf]',r'\externaldocument{ec-labels}[electronic_companion.pdf]'+'\n'+r'\externaldocument{cs-labels}[computational_supplement.pdf]')
    e=e.replace(r'\externaldocument{main-labels}[main.pdf]',r'\externaldocument{main-labels}[main.pdf]'+'\n'+r'\externaldocument{cs-labels}[computational_supplement.pdf]')
    macros=(R/'tables/metrics.tex').read_text() if (R/'tables/metrics.tex').exists() else ''
    m=m.replace(r'\begin{document}',macros+'\n'+r'\begin{document}',1)
    newtables=(R/'tables/main_tables.tex').read_text() if (R/'tables/main_tables.tex').exists() else ''
    conclusion=next(x for x in re.findall(r'\\section\{[^}]*\}',m) if 'Conclusion' in x)
    m=m.replace(conclusion,newtables+'\n'+conclusion)
    preamble=oldec[:oldec.index(r'\begin{document}')]
    preamble=preamble.replace(oldtitle,TITLE+' -- Computational Supplement')
    preamble=preamble.replace(r'\fancyhead[L]{\small NDU: Electronic Companion}',r'\fancyhead[L]{\small Accepted Service Adaptation: Computation}')
    preamble=preamble.replace(r'\externaldocument{main-labels}[main.pdf]',r'\externaldocument{main-labels}[main.pdf]'+'\n'+r'\externaldocument{ec-labels}[electronic_companion.pdf]')
    preamble=preamble.replace('EC.','CS.')
    bibliography=subtext(oldec,r'\begin{thebibliography}',r'\end{thebibliography}')+r'\end{thebibliography}'
    cs=preamble+macros+'\n'+r'\begin{document}'+'\n'+r'\begin{center}{\Large\bfseries Computational Supplement\par}\medskip'+ '\n{\\large '+TITLE+r'\par}\medskip'+'\nRevision R24, September 23, 2026\n'+r'\end{center}'+'\n'
    cs+=(R/'sections/computational_intro.tex').read_text()+'\n'
    if (R/'tables/computational_tables.tex').exists():cs+=(R/'tables/computational_tables.tex').read_text()+'\n'
    cs+='\n'.join(moved)+'\n'+bibliography+'\n'+r'\end{document}'+'\n'
    for name,text in [('main.tex',m),('electronic_companion.tex',e),('computational_supplement.tex',cs)]:
        (REPO/name).write_text(text)
    (R/'results/relocations.json').write_text(__import__('json').dumps({'canonical_main_to_ec':len(canonical.encode()),
      'ec_to_computational_bytes':sum(len(t.encode()) for t in moved),
      'formal_fleet_statement_and_proof_retained_in_ec':True,
      'robust_result_environment_change':'theorem to lemma; statement/proof content unchanged'},indent=2)+'\n')
if __name__=='__main__':main()
