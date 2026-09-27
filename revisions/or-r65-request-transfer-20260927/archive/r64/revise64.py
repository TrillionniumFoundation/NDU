"""Deterministically revise the immutable R63 reader; preserve its central proofs."""
from pathlib import Path
import json,re,hashlib
R=Path(__file__).resolve().parent
A=R/'archive/r63'

def once(text,old,new):
    assert text.count(old)==1,('Expected exactly one source anchor',old[:100],text.count(old))
    return text.replace(old,new,1)

def read(name):return (R/'sections/r64'/name).read_text().strip()
def revise():
    main=(A/'main.tex').read_text();ec=(A/'electronic_companion.tex').read_text()
    main=main.replace('.build/r63/','.build/r64/').replace('Operations Research --- R63','Operations Research --- R64')
    ec=ec.replace('.build/r63/','.build/r64/').replace('R63','R64',1)
    main=once(main,'We extend this result to near-standard tariffs through an explicit original-policy perturbation certificate and a minimum-distortion sparse-exception projection.',
        'We transfer the exact sparse-exception solution to near-standard tariffs through an original-policy additive certificate, using a minimum-distortion fee projection.')
    main=once(main,'Near-standard fees are not treated as exact uniform fees: we bound the value lost by simplifying the tariff and evaluate the returned policy under its original charges.',
        'For near-standard fees, an exact sparse-exception surrogate supplies an original-policy additive interval, not an exact-tractability claim for the original fees. We evaluate the returned policy under its original charges.')
    main=once(main,'\\subsection{Relationship to prior work}\n','\\subsection{Relationship to prior work}\n'+read('related_work.tex')+'\n\n')
    main=once(main,'For $J\\subseteq E$, require exactly those exceptional commands',
        'The recurrence is exact for any declared standard when all its relative exceptions are enumerated; the choice affects the parameter and computational cost, not the exact optimal value. The independent checker verifies the modal fee and the tie rule from the original fees before checking the optimization proof. For $J\\subseteq E$, require exactly those exceptional commands')
    main=once(main,'It creates a certified approximation neighborhood of the exact theorem, with an explicit price for simplifying the tariff.',
        'It creates a certified approximation neighborhood of the exact theorem, with an explicit price for simplifying the tariff. The strict-margin condition is a theoretical book-stability diagnostic: the implementation does not compute a second-best-book margin or claim a stability certificate.')
    # Retain the projection argument; distinguish allowance from realized counts.
    start=main.index('\\subsection{Selecting a sparse-exception surrogate}')
    stop=main.index('\\subsection{Exact fees, installed commands, and policy changes}',start)
    projection=main[start:stop]
    projection=projection.replace('$0\\leq d<N$','$0\\leq d_{\\rm allow}<N$').replace('$n_0=N-d$','$n_0=N-d_{\\rm allow}$')
    projection=projection.replace('$d$','$d_{\\rm allow}$').replace('$d=N-1$','$d_{\\rm allow}=N-1$')
    projection=projection.replace('$d\\in\\{','$d_{\\rm allow}\\in\\{').replace('$\\varepsilon>0$','$\\varepsilon\\geq0$')
    projection=projection.replace('[Minimum absolute tariff distortion]','[Sparse-tariff preprocessing by trimmed absolute deviation]')
    old='Sorted prefix sums evaluate all window deviations in linear time after sorting.'
    new=('This is the one-dimensional trimmed absolute-deviation construction discussed in the related work, specialized to tariff preprocessing. Among windows with equal minimum distortion, choose the smallest lower median and then the earliest sorted window. Write $d_{\\rm proj}$ for the actual number of projected fees different from this median and $d_{\\rm tariff}$ for the inner tariff solver\'s exception count after it chooses its own modal fee. Then $d_{\\rm tariff}\\leq d_{\\rm proj}\\leq d_{\\rm allow}$; the two standards need not coincide.\n\n'+old)
    projection=once(projection,old,new)
    projection=projection.replace('$2^d\\operatorname{poly}(L)$','$2^{d_{\\rm tariff}}\\operatorname{poly}(L)$')
    projection=projection.replace('A declared computational guard may still stop a large-$d$ request.',
        'The tolerance constrains total absolute fee distortion, not the final width directly. A declared computational guard may still stop a request with large $d_{\\rm tariff}$. Independent checking certifies both the projection and failure of the preceding allowance; it does not trust the binary-search trace.')
    # d was rewritten above, so also replace the old guard wording after substitution.
    projection=projection.replace('A declared computational guard may still stop a large-$d_{\\rm allow}$ request.',
        'The tolerance constrains total absolute fee distortion, not the final width directly. A declared computational guard may still stop a request with large $d_{\\rm tariff}$. Independent checking certifies both the projection and failure of the preceding allowance; it does not trust the binary-search trace.')
    main=main[:start]+projection+main[stop:]
    main=once(main,'Proof files in the entire expanded panel reach 5,572,345 uncompressed bytes.',
        'Across the expanded panel, the maxima are 5,572,345 uncompressed bytes and 214,897 gzip-compressed bytes. At the fixed 17-command scale, the zero- and twelve-exception proofs compress to 922 and 115,597 bytes, respectively; their paired uncompressed sizes are 4,143 and 3,964,865 bytes. These proof and checking costs are not negligible.')
    main=once(main,'\\section{Conclusion}\\label{sec:conclusion63}',
        '\\subsection{Projection quality under the original fees}\\label{sec:projection-study64}\n'
        'Table~\\ref{tab:projection64} reports every adversarial robust-tariff request, including four mathematically inapplicable cases and one engineering guard. All seven available intervals are checked against the original fees. Five returned policies have exactly zero regret, established by closed rational comparator intervals. For the two diffuse near-standard tariffs, uniform surrogates give widths $8\\times10^{-5}$ and $19\\times10^{-5}$ at tolerance $1/500$; their regrets remain bounded rather than identified. The distinction among projection allowance, actual projected exceptions, and the inner modal count is reported explicitly. Original optimizer and checker times and paired raw/compressed proof sizes accompany the quality measures. The table is generated from frozen records without a new optimization run. Later comparator checks inform regret, not original target attainment.\n\n'
        '\\section{Conclusion}\\label{sec:conclusion63}')
    main=once(main,'the perturbation certificate extends that algorithm to near-standard tariffs with a bound on the value lost by an original-feasible policy.',
        'the additive transfer certificate evaluates an exact sparse-exception surrogate\'s original-feasible policy under near-standard original fees. This transfer gives an original-fee interval, not exact tractability of arbitrary near-standard instances.')
    # Original-timing versus later integrity audit must be visible in each caption/note.
    main=once(main,'Controlled scaling: target attainment within the original total allowance',
        'Controlled scaling: original on-time target attainment, not later binding replay')
    main=once(main,'A later successful replay does not change these original timing outcomes.',
        'Success requires the original end-to-end deadline and the original checker outcome. R63 external-input binding and R64 semantic replay are later integrity audits and do not promote originally late or failed requests.')
    main=once(main,'The exception loop and independent certification at fixed physical size',
        'The exception loop and original timed certification at fixed physical size')
    main=once(main,'The raw records contain all components and budgets.',
        'The raw records contain all components and budgets. These are original timed checking measurements; later R63 external-input binding and R64 semantic audits neither replace these times nor reclassify late or failed requests.')
    main=once(main,'Local diagnostic times are descriptive and are not pooled with the earlier frozen execution environment.',
        'This is the separate post-study root diagnostic, not a reclassification of original timed requests. Local diagnostic times are descriptive and are not pooled with the earlier frozen execution environment; later binding or semantic replay does not alter any original checker outcome. Root support requires one active original book, not merely a convex mixture of books.')
    main=once(main,'\\end{document}',(R/'generated/projection_quality64.tex').read_text().replace('sec:robust-fees','sec:robust63')+'\n\\end{document}')
    # New detail belongs in the companion rather than replacing existing technical material.
    ec=once(ec,'\\subsection{Source closure and reproduction}',read('checker_semantics.tex')+'\n\n\\subsection{Source closure and reproduction}')
    ec=once(ec,'The root panel has its own input and source freeze before its execution;',
        'The R63 root panel\'s original source freeze is verified against the unchanged archived R63 code, while current checkers are separately hashed and execute the proof replay. The root panel has its own input and source freeze before its execution;')
    ec=once(ec,'Reviewer files are not introduced as a scientific parent.',
        'Reviewer files are not introduced as a scientific parent. R64 preserves the R63 readers, code, and result snapshot; their unchanged R60/R61 evidence remains shared at its original paths. The archival manifest is interpreted with this preservation map rather than as an independently copied second timing study. Exact-head receipts establish artifact integrity and executed checks, not novelty or editorial acceptance.')
    # Bibliography is alphabetical and identical between the two scientific readers.
    for key,bib in [('Virtanen2020',r'''\bibitem[Tableman(1994)]{Tableman1994}
Tableman M (1994) The asymptotics of the least trimmed absolute deviations (LTAD) estimator. \emph{Statistics \& Probability Letters} 19(5):387--398. doi:10.1016/0167-7152(94)90007-8.
'''),('Yang2025',r'''\bibitem[Xu and Burer(2017)]{XuBurer2017}
Xu G, Burer S (2017) Robust sensitivity analysis of the optimal value of linear programming. \emph{Optimization Methods and Software} 32(6):1187--1205. doi:10.1080/10556788.2016.1256400.
''')]:
        for name in ('main','ec'):
            s=main if name=='main' else ec
            anchor=re.search(r'\\bibitem[^\n]*\{'+key+r'\}',s).group(0)
            s=once(s,anchor,bib+anchor)
            if name=='main':main=s
            else:ec=s
    bib=r'''\bibitem[Zioutas et al.(2015)Zioutas, Chatzinakos, Nguyen, and Pitsoulis]{Zioutas2015}
Zioutas G, Chatzinakos C, Nguyen TD, Pitsoulis L (2015) Optimization techniques for multivariate least trimmed absolute deviation estimation. arXiv:1511.04220.
'''
    main=once(main,'\\end{thebibliography}',bib+'\\end{thebibliography}')
    ec=once(ec,'\\end{thebibliography}',bib+'\\end{thebibliography}')
    (R/'main.tex').write_text(main);(R/'electronic_companion.tex').write_text(ec)
    prefix=(A/'RESPONSE_TO_REFEREES.tex').read_text().split('\\begin{document}')[0].replace('.build/r63/','.build/r64/')
    (R/'RESPONSE_TO_REFEREES.tex').write_text(prefix+'\\begin{document}\n'+read('response_body.tex')+'\n\\end{document}\n')
    # Source fragments mirror the reader, not stale R63 wording.
    (R/'sections/robustness.tex').write_text(main[main.index('\\section{Near-Standard'):main.index('\\section{Merged-Origin')])
    (R/'sections/study.tex').write_text(main[main.index('\\section{Computational Evidence'):main.index('\\section{Conclusion}')])
    (R/'sections/implementation.tex').write_text(ec[ec.index('\\section{Implementation Boundaries'):ec.index('\\clearpage\\phantomsection\\label{ec-refs-start}')])
    (R/'sections/response_body.tex').write_text(read('response_body.tex')+'\n')
    # No central mathematical environment is removed. Projection notation and
    # its descriptive heading are the sole edits inside an inherited statement/proof.
    pattern=r'\\begin\{(theorem|proposition|lemma|corollary|proof)\}.*?\\end\{\1\}'
    preservation={}
    for name in ('main','electronic_companion'):
        old=(A/(name+'.tex')).read_text();new=(R/(name+'.tex')).read_text()
        blocks=[m.group(0) for m in re.finditer(pattern,old,re.S)]
        unchanged=sum(b in new for b in blocks)
        permitted=[b for b in blocks if b not in new]
        assert not permitted or (name=='main' and len(permitted)==2 and
            'prop:projection63' in permitted[0] and 'fixed standard' in permitted[1])
        preservation[name]={'inherited_mathematical_environments':len(blocks),'byte_identical':unchanged,
            'projection_notation_and_zero_tolerance_clarifications':len(permitted),'removed_environments':0}
    (R/'results/r64/PRESERVATION64.json').write_text(json.dumps(preservation,indent=2)+'\n')
    print(preservation)
if __name__=='__main__':revise()
