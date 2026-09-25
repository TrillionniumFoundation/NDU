"""Assemble the R49 readers from immutable R48 inputs, retaining every proof."""
from pathlib import Path
import json,re,hashlib
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
P=R/'predecessor';PREFIX=str(R.relative_to(ROOT));OLD='revisions/or-r48-harmonic-coarsening-20260925'
TITLE='Limited-Memory Renewal Contracts: Exact Eligibility Pooling and Certified Joint Design'
ABSTRACT='''A renewal provider must choose a limited command alphabet and allocate an accepted obligation across heterogeneous histories. We develop exact joint optimization for a finite catalog with opening charges, individual participation caps, and realization ceilings. A terminal-first allocation theorem pools histories that admit the same catalog symbols while retaining their different caps and service costs. The resulting correction depends only on the last eligible selected symbol and enters an ordered path recurrence. With common eligibility and quadratic primitives, one polynomial-time call solves the original joint problem, even at interior promises and with arbitrarily many distinct histories. With several eligibility classes, an exact two-sided price oracle provides globally valid bounds over their means. Certified subdivision and an additive approximation scheme depend exponentially on the number of classes rather than on the history count or cost-dispersion bins. Independent primal-dual and coverage checks validate original-space policies and bounds. A declared synthetic study includes 1,024-history exact solutions, paired comparisons, numerical mixed-integer brackets, and all unresolved multi-class cases. The method retains the original command budget and all individual contractual constraints; earlier continuous-design and harmonic-coarsening results remain available under their original assumptions.'''
MOVED_MATH=[
'revisions/or-r46-box-decomposition-20260925/types.tex',
'revisions/or-r47-joint-certificates-20260925/coarsening.tex',
'revisions/or-r48-harmonic-coarsening-20260925/harmonic.tex']

def run():
    main=(P/'main.tex').read_text();ec=(P/'electronic_companion.tex').read_text()
    oldtitle='Limited-Memory Renewal Contracts: Harmonic Coarsening and Certified Joint Design'
    main=main.replace('Harmonic Coarsening and Certified Joint Design','Exact Eligibility Pooling and Certified Joint Design').replace('{r48-','{r49-')
    main=main.replace(OLD+'/COMPUTATIONAL_RECORD.pdf',PREFIX+'/COMPUTATIONAL_RECORD.pdf')
    main=re.sub(r'(?<=\\textbf\{Abstract\.\} ).*?(?=\n\\par\\vspace\{\.15in\})',lambda _:ABSTRACT,main,flags=re.S)
    for name in ['introduction','study','conclusion']:
        main=main.replace(OLD+'/'+name+'.tex',PREFIX+'/'+name+'.tex')
    for name in MOVED_MATH: main=main.replace('\\input{'+name+'}\n','')
    key='\\input{revisions/or-r45-budgeted-compression-20260924/compression.tex}\n'
    main=main.replace(key,key+'\\input{'+PREFIX+'/pooling.tex}\n')
    key='\\input{revisions/or-r46-box-decomposition-20260925/adaptive.tex}\n'
    main=main.replace(key,key+'\\input{'+PREFIX+'/group_boxes.tex}\n')
    main=main.replace(OLD+'/generated/references.tex',PREFIX+'/generated/references.tex')
    before,after=main.split('\\label{refs-end}',1)
    oldmain_tables=re.findall(r'\\input\{([^}]+)\}',after)
    main=before+'\\label{refs-end}\n\\clearpage\n\\input{'+PREFIX+'/generated/main_tables.tex}\n\\end{document}\n'
    # All antecedent mathematics remains in the article or companion.
    ec=ec.replace('{r48-','{r49-').replace(oldtitle,TITLE)
    ec=ec.replace(OLD+'/COMPUTATIONAL_RECORD.pdf',PREFIX+'/COMPUTATIONAL_RECORD.pdf')
    start=ec.index('This companion retains');end=ec.index('\\input{',start)
    ec=ec[:start]+('This companion retains the preceding mathematical chain, including exact response-type reduction, guarded aggregation, harmonic coarsening, and continuous-design results. All original statements and proofs remain under their stated assumptions. Complete historical and new computational records, rather than additional mathematical proofs, are supplied in the separately identified Computational Reproduction Record.\n')+ec[end:]
    # Put the exact type comparison first, and approximations after the other retained theory.
    start=ec.index('\\input{')
    ec=ec[:start]+'\\input{'+MOVED_MATH[0]+'}\n'+ec[start:]
    key='\\clearpage\n\\input{'+OLD+'/generated/references.tex}'
    ec=ec.replace(key,'\n'.join('\\input{'+x+'}' for x in MOVED_MATH[1:])+'\n'+key)
    before,after=ec.split('\\input{'+OLD+'/generated/references.tex}',1)
    oldec_tables=re.findall(r'\\input\{([^}]+)\}',after)
    ec=before+'\\input{'+PREFIX+'/generated/references.tex}\n\\end{document}\n'
    # Keep the complexity map near the new theorem and the antecedent net in print.
    tline='\\input{'+MOVED_MATH[0]+'}\n'
    ec=ec.replace(tline,'')
    marker='\\input{'+PREFIX+'/pooling.tex}\n'
    main=main.replace(marker,marker+tline)
    net='revisions/or-r45-budgeted-compression-20260924/target_net.tex'
    ec=ec.replace('\\input{'+net+'}\n','')
    main=main.replace('\\appendix\n','\\appendix\n\\input{'+net+'}\n')
    ROOT.joinpath('main.tex').write_text(main);ROOT.joinpath('electronic_companion.tex').write_text(ec)
    # Preserve all old computational narratives and table bodies verbatim as inputs.
    cr=ROOT.joinpath(OLD,'COMPUTATIONAL_RECORD.tex').read_text().replace('{r48-','{r49-').replace(oldtitle,TITLE)
    start=cr.index('This repository record');end=cr.index('\\input{',start)
    cr=cr[:start]+('This repository reproduction record contains the complete preceding computational narratives and tables, identified by their original revision, followed by every new exact-pooling and numerical mixed-integer case. It is code-and-experiment documentation, not an additional proof appendix. The current article and electronic companion retain all mathematical statements and proofs. Historical measurements are not relabeled as fresh executions.\n')+cr[end:]
    key='\\clearpage\\input{'+OLD+'/generated/references.tex}'
    cr=cr.replace(key,'\\input{'+OLD+'/study.tex}\n'+key.replace(OLD,PREFIX))
    cr=cr.replace('\\end{document}', '\n'.join('\\clearpage\\input{'+x+'}' for x in oldmain_tables+oldec_tables)+'\n\\clearpage\\input{'+PREFIX+'/generated/detailed_tables.tex}\n\\end{document}')
    R.joinpath('COMPUTATIONAL_RECORD.tex').write_text(cr)
    refs=ROOT.joinpath(OLD,'generated/references.tex').read_text()
    insert=r'''\bibitem[Patriksson and Str{\"o}mberg(2015)]{PatrikssonStromberg2015}
Patriksson M, Str{\"o}mberg C (2015) Algorithms for the continuous nonlinear resource allocation problem---new implementations and numerical studies. Author manuscript, arXiv:1501.07035.

\bibitem[Schoot Uiterkamp et al.(2022)Schoot Uiterkamp, Gerards, and Hurink]{SchootUiterkamp2022}
Schoot Uiterkamp MHH, Gerards MET, Hurink JL (2022) Quadratic nonseparable resource allocation problems with generalized bound constraints. \emph{INFORMS Journal on Optimization} 4(2):215--247. doi:10.1287/ijoo.2021.0065.

'''
    refs=refs.replace('\\bibitem[Spear',insert+'\\bibitem[Spear')
    R.joinpath('generated/references.tex').write_text(refs)
    mapping=dict(scientific_parent='939cce84881a1d1eabf93aa3a2d3f4f4417ce53f',
        antecedent_math_moved_intact_to_companion=MOVED_MATH[1:],antecedent_net_moved_intact_to_print_appendix=net,antecedent_tables_moved_intact_to_computational_record=oldmain_tables+oldec_tables,
        antecedent_study_added_intact_to_record=OLD+'/study.tex',new_main_sections=[PREFIX+'/'+x+'.tex' for x in ['pooling','group_boxes','introduction','study','conclusion']],
        preserved_reader_copies=[str((P/x).relative_to(ROOT)) for x in ['main.tex','electronic_companion.tex','main.pdf','electronic_companion.pdf','README.md']],
        relocated_input_sha256={p:hashlib.sha256(ROOT.joinpath(p).read_bytes()).hexdigest() for p in MOVED_MATH+oldmain_tables+oldec_tables+[OLD+'/study.tex']})
    R.joinpath('CONTENT_MAP.json').write_text(json.dumps(mapping,indent=2)+'\n')

if __name__=='__main__':run()
