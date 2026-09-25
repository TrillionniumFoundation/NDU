"""Assemble R48 readers. Every inherited scientific input stays byte-preserved."""
from pathlib import Path
import re,json,shutil
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];P=str(R.relative_to(ROOT));R47=R.parent/'or-r47-joint-certificates-20260925'
TITLE='Limited-Memory Renewal Contracts: Harmonic Coarsening and Certified Joint Design'
ABSTRACT='''A renewal provider must select a limited command alphabet and allocate an accepted obligation across heterogeneous histories. We develop contract-preserving joint optimization for a finite catalog with opening charges, participation caps, and realization ceilings. An eligibility-aware two-sided price-path oracle supplies globally valid bounds on target boxes. Guarded aggregation reduces the history dimension, and weighted harmonic service curvatures tighten the reduced model without adding target coordinates. We prove dominance over minimum-curvature aggregation and construct an optimal within-group lift satisfying every original constraint. A square-root curvature partition gives a second-order cost-dispersion bound and improves the accuracy-dependent dimension of the variable-history additive scheme. For bounded eligibility complexity and primitive scales, fixed-accuracy complexity is polynomial in the history count and catalog size; accuracy dependence remains potentially large. Independent checkers verify reduced upper bounds and original policy feasibility. A paired 24-case cost-heterogeneity study includes up to 256 histories, exact joint references, numerical mixed-integer comparisons, and retained unresolved cases. Canonical contractual allocation, continuous quadratic design, Monge acceleration, and budgeted compression remain under their original assumptions. The method strengthens joint-design certificates without expanding the installed command budget.'''

def run():
    (R/'generated').mkdir(exist_ok=True)
    main=(R/'predecessor/main.tex').read_text();ec=(R/'predecessor/electronic_companion.tex').read_text()
    old='Limited-Memory Renewal Contracts: Joint Design with Certified Response Coarsening'
    for a,b in [(old,TITLE),('Joint Design with Certified Response Coarsening','Harmonic Coarsening and Certified Joint Design'),('r47-ec-labels','r48-ec-labels'),('r47-main-labels','r48-main-labels')]:
        main=main.replace(a,b);ec=ec.replace(a,b)
    main=re.sub(r'(?<=\\textbf\{Abstract\.\} ).*?(?=\n\\par\\vspace)',lambda m:ABSTRACT,main,flags=re.S)
    for name in ('introduction','study','conclusion'):
        main=main.replace(f'revisions/or-r47-joint-certificates-20260925/{name}.tex',f'{P}/{name}.tex')
    main=main.replace('\\input{revisions/or-r45-budgeted-compression-20260924/certificates.tex}',f'\\input{{{P}/harmonic.tex}}')
    resources='revisions/or-r45-budgeted-compression-20260924/derived/revisions__or-r39-robust-quantizer-20260924__resources.tex'
    main=main.replace('\\input{'+resources+'}\n','')
    ec=ec.replace('\\input{revisions/or-r46-box-decomposition-20260925/study.tex}\n','').replace('\\input{revisions/or-r46-box-decomposition-20260925/protocol.tex}\n','')
    ec=ec.replace('\\clearpage\n\\input{revisions/or-r47-joint-certificates-20260925/generated/references.tex}',
        '\\input{revisions/or-r45-budgeted-compression-20260924/certificates.tex}\n\\input{'+resources+'}\n\\clearpage\n\\input{revisions/or-r47-joint-certificates-20260925/generated/references.tex}')
    for x in ('main','ec'):
        s=locals()[x].replace('revisions/or-r47-joint-certificates-20260925/generated/references.tex',P+'/generated/references.tex')
        s=s.replace('\\begin{document}',f'\\externaldocument{{r48-cs-labels}}[{P}/COMPUTATIONAL_RECORD.pdf]\n\\begin{{document}}',1)
        if x=='main':main=s
        else:ec=s
    main=main.replace('revisions/or-r47-joint-certificates-20260925/generated/antecedent_main_tables.tex',P+'/generated/antecedent_main_tables.tex')
    main=main.replace('\\end{document}',f'\\input{{{P}/generated/main_table.tex}}\n\\end{{document}}')
    ec=ec.replace('This companion retains the preceding mathematical chain, the two-sided decomposition study, and supplemental certificates. It also supplies the distinct-history stress and independent mixed-integer comparisons.', 'This companion retains the preceding mathematical chain, the comparison certificates, resource accounting, and computational tables. Complete study narratives and implementation protocols appear in the separately identified Computational Reproduction Record.')
    # Reader copy, not changes to the preceding source table.
    tab=(R47/'generated/antecedent_main_tables.tex').read_text().replace('New, Theorem','R47, Theorem').replace('New refinement, Proposition','R47 refinement, Proposition')
    tab=tab.replace('\\bottomrule',r'Harmonic pooling and square-root bins & Dominating upper model; optimal original lift; smaller accuracy-dependent dimension & R48, Theorems~\ref{thm:r48-harmonic}--\ref{thm:r48-scheme} \\'+'\n'+r'\bottomrule',1)
    (R/'generated/antecedent_main_tables.tex').write_text(tab)
    refs=(R47/'generated/references.tex').read_text()
    # The new proof is elementary; cite a primary study to distinguish classical mean inequalities from model-specific contributions.
    entry='\\bibitem[Liao and Wu(2015)]{LiaoWu2015} Liao W, Wu J (2015) Matrix inequalities for the difference between arithmetic mean and harmonic mean. \\emph{arXiv:1501.04823}.\n'
    # Alphabetical insertion immediately before Li, or before final bibliography marker if absent.
    pos=refs.find('\\bibitem[Nielsen')
    if pos<0:pos=refs.find('\\bibitem[Liu')
    if pos<0:pos=refs.index('\\end{thebibliography}')
    refs=refs[:pos]+entry+refs[pos:];(R/'generated/references.tex').write_text(refs)
    # A reproducibility record carries intact older computational narratives, not relocated mathematical proofs.
    pre=ec.split('\\begin{document}')[0]
    pre=pre.replace('\\externaldocument{r48-cs-labels}['+P+'/COMPUTATIONAL_RECORD.pdf]','')
    pre=pre.replace('[main.pdf]','[../../main.pdf]')
    pre=pre.replace('{EC.','{CR.')
    pre+='\\externaldocument{r48-ec-labels}[../../electronic_companion.pdf]\n'
    cs=pre+'\\begin{document}\n\\begin{center}{\\Large\\bfseries Computational Reproduction Record}\\end{center}\n'
    cs+='This repository record preserves the complete R46 and R47 computational narratives and implementation protocols, and supplies all R48 per-instance metrics. Mathematical statements and proofs remain in the current article and electronic companion. Antecedent measurements are not relabeled as new runs.\n'
    for f in ['revisions/or-r46-box-decomposition-20260925/study.tex','revisions/or-r46-box-decomposition-20260925/protocol.tex','revisions/or-r47-joint-certificates-20260925/study.tex']:
        cs+='\\input{'+f+'}\n'
    cs+='\\clearpage\\input{'+P+'/generated/references.tex}\n\\clearpage\\input{'+P+'/generated/detailed_tables.tex}\n\\end{document}\n'
    (R/'COMPUTATIONAL_RECORD.tex').write_text(cs)
    ROOT.joinpath('main.tex').write_text(main);ROOT.joinpath('electronic_companion.tex').write_text(ec)
    (R/'CONTENT_MAP.json').write_text(json.dumps(dict(base='df1e192fd0846315ff0938e57d797efcd04109aa',
        intact_math_moves_to_ec=['R45 certificates.tex',resources],
        intact_computational_moves_to_record=['R46 study.tex','R46 protocol.tex','R47 study.tex'],
        all_mathematical_statements_and_proofs='retained in current main and electronic companion',
        original_entry_points_and_readers='predecessor/',unchanged_antecedent_sources=True),indent=2)+'\n')
    print('Abstract words',len(ABSTRACT.split()))
if __name__=='__main__':run()
