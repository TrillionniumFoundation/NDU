from pathlib import Path
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];O=R.parent/'or-r45-budgeted-compression-20260924'
TITLE='Limited-Memory Renewal Contracts: Two-Sided Decomposition and Certified Joint Design'
ABSTRACT='''A renewal provider must jointly choose a limited command alphabet and allocate an accepted service obligation under participation caps, realization ceilings, and command-opening charges. We derive an exact price oracle on arbitrary target boxes. Concavity orders the command scores into an increasing prefix and a decreasing suffix: upper-target crossings determine the first side, lower-target crossings determine the second, and a shared peak joins them without exceeding the original budget. The resulting polynomial node oracle yields an adaptive global interval and finite termination at any positive additive tolerance. An exact response-type reduction replaces the number of histories by the number of distinct catalog responses in the search dimension. A separate checker verifies path inequalities, the complete target cover, and the original contract. The worst-case accuracy dependence remains exponential in the number of distinct types; it is not an asserted hardness barrier. Thirty-two synthetic joint-design cases and independent mixed-integer comparisons expose both completed certificates and unresolved gaps. Inherited price-prefix search is stronger on several cases. Canonical contractual allocation, continuous quadratic design, Monge acceleration, budgeted compression, and their proofs remain available under their original assumptions.'''

def inp(path):return '\\input{'+str(path.relative_to(ROOT))+'}\n'
def run():
    pre=(R/'predecessor/main.tex').read_text().split('\\begin{document}')[0].replace('r45-ec-labels','r46-ec-labels').replace('Budgeted Compression and Certified Joint Design','Two-Sided Decomposition and Certified Joint Design')
    main=pre+r'\begin{document}\hypersetup{pageanchor=false}'+'\n'+r'''\begin{titlepage}\centering
{\Large\bfseries Limited-Memory Renewal Contracts:\newline Two-Sided Decomposition and Certified Joint Design\par}
\vspace{.3in}Anonymous manuscript for Operations Research\par\vspace{.2in}
\begin{minipage}{\textwidth}\textbf{Abstract.} '''+ABSTRACT+r'''
\par\vspace{.15in}\textbf{Keywords:} renewal contracts; dynamic programming; global optimization.
\par\vspace{.1in}\textbf{Subject classifications:} Dynamic programming: service design; Programming: global optimization.
\par\vspace{.1in}\textbf{Area of review:} Optimization.
\par\vspace{.1in}\textbf{Submission category:} Lengthy manuscript.
\end{minipage}\vfill September 25, 2026\end{titlepage}
\hypersetup{pageanchor=true}
'''
    for p in [R/'introduction.tex',O/'model.tex',O/'compression.tex',R/'types.tex',R/'two_sided.tex',R/'adaptive.tex',O/'certificates.tex',R/'study.tex',R/'conclusion.tex']:main+=inp(p)
    main+='\\appendix\n'
    for p in [O/'derived/revisions__or-r43-prefix-decomposition-20260924__decomposition.tex',O/'derived/revisions__or-r39-robust-quantizer-20260924__resources.tex',O/'continuous_appendix.tex',O/'derived/revisions__or-r39-robust-quantizer-20260924__derived__global.tex',ROOT/'revisions/or-r39-robust-quantizer-20260924/figure.tex',O/'derived/revisions__or-r39-robust-quantizer-20260924__derived__monge.tex',O/'derived/revisions__or-r43-prefix-decomposition-20260924__grid_certificate.tex']:main+=inp(p)
    main+='\\clearpage\\phantomsection\\label{refs-start}\n'+inp(R/'generated/references.tex')+'\\label{refs-end}\n\\clearpage\n'+inp(R/'generated/main_tables.tex')+inp(R/'generated/historical_main_tables.tex')+'\\end{document}\n'
    (ROOT/'main.tex').write_text(main)
    ecpre=pre.replace('r46-ec-labels','r46-main-labels').replace('[electronic_companion.pdf]','[main.pdf]')
    ec=ecpre+r'''\renewcommand{\thesection}{EC.\arabic{section}}
\renewcommand{\theequation}{EC.\arabic{equation}}
\renewcommand{\thetable}{EC.\arabic{table}}
\begin{document}
\begin{center}{\Large\bfseries Electronic Companion}\par
Limited-Memory Renewal Contracts: Two-Sided Decomposition and Certified Joint Design\end{center}
This companion retains the complete preceding mathematical chain and supplies numerical and implementation details for joint target-box design. Historical numerical records and full predecessor readers remain separately preserved; they are not represented as new executions.
'''
    for p in [O/'derived/revisions__or-r42-certified-joint-design-20260924__institution.tex',O/'derived/revisions__or-r39-robust-quantizer-20260924__derived__deterministic.tex',O/'derived/revisions__or-r39-robust-quantizer-20260924__derived__lotteries.tex',O/'derived/revisions__or-r42-certified-joint-design-20260924__promise_robustness.tex',O/'derived/revisions__or-r39-robust-quantizer-20260924__derived__core_proofs.tex',O/'derived/revisions__or-r39-robust-quantizer-20260924__derived__mechanism.tex',O/'derived/revisions__or-r37-integrated-frontier-20260924__bounded_overrun.tex',O/'derived/revisions__or-r39-robust-quantizer-20260924__allocation_companion.tex',O/'derived/revisions__or-r43-prefix-decomposition-20260924__monotone_charge.tex',O/'derived/revisions__or-r42-certified-joint-design-20260924__catalog_design.tex',O/'derived/revisions__or-r44-resource-augmentation-20260924__augmentation.tex',O/'derived/revisions__or-r44-resource-augmentation-20260924__augmentation_companion.tex',O/'target_net.tex',O/'support.tex',R/'protocol.tex']:ec+=inp(p)
    ec+='\\clearpage\n'+inp(R/'generated/references.tex')+'\\clearpage\n'+inp(R/'generated/companion_tables.tex')+inp(ROOT/'revisions/or-r39-robust-quantizer-20260924/derived/accounting_table.tex')+'\\end{document}\n'
    (ROOT/'electronic_companion.tex').write_text(ec)
    print('Assembled; abstract words',len(ABSTRACT.split()))
if __name__=='__main__':run()
