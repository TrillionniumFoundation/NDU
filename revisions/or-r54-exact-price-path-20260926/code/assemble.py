"""Assemble current readers; preserve all root predecessors byte-for-byte."""
from pathlib import Path
import subprocess,json,hashlib
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];P=str(R.relative_to(ROOT))
PARENT='fcd7b7ab1719f00e547cd29e94cbb421fab59b0a';TITLE='Exact Path Representations for Finite-Catalog Renewal Design'
OLD=ROOT/'revisions/or-r52-resource-path-20260925';R53=ROOT/'revisions/or-r53-catalog-safe-certificates-20260926'
def old_bytes(name):
    if (ROOT/'.git').exists():return subprocess.check_output(['git','show',PARENT+':'+name],cwd=ROOT)
    if (R/'predecessor'/name).exists():return (R/'predecessor'/name).read_bytes()
    if (ROOT/'NDU/NDU'/name).exists():return (ROOT/'NDU/NDU'/name).read_bytes()
    if name.endswith('.tex') and (R53/name).exists():return (R53/name).read_bytes()
    if (ROOT/name).exists():return (ROOT/name).read_bytes()
    raise RuntimeError('Missing exact predecessor '+name)
def run():
    saved=R/'predecessor';saved.mkdir(exist_ok=True)
    for name in ['main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md']:
        (saved/name).write_bytes(old_bytes(name))
    pre=(OLD/'RESPONSE_TO_REFEREES.tex').read_text().split('\\externaldocument')[0]
    pre=pre.replace('Selected-Boundary Resource Paths','Exact Renewal Path Representations')
    metrics='\\input{revisions/or-r52-resource-path-20260925/generated/metrics.tex}\n'+f'\\input{{{P}/generated/metrics.tex}}\n'
    abstract=(R/'ABSTRACT.txt').read_text().strip()
    main=pre+metrics+'\\externaldocument{.build/r54/electronic_companion}[electronic_companion.pdf]\n'
    main+='\\hypersetup{pdftitle={'+TITLE+'},pdfauthor={Anonymous}}\n\\begin{document}\\hypersetup{pageanchor=false}\n'
    main+='\\begin{titlepage}\\centering{\\Large\\bfseries '+TITLE+'\\par}\n\\vspace{0.25in}Anonymous manuscript for Operations Research\\par\\vspace{0.2in}\n'
    main+='\\begin{minipage}{\\textwidth}\\textbf{Abstract.} '+abstract+'\n\\par\\vspace{0.15in}\\textbf{Keywords:} renewal contracts; dynamic programming; global optimization.\n'
    main+='\\par\\vspace{0.1in}\\textbf{Subject classifications:} Dynamic programming: finite command design; Programming: global optimization.\n\\par\\vspace{0.1in}\\textbf{Area of review:} Optimization.\\end{minipage}\\vfill September 26, 2026\\end{titlepage}\n\\hypersetup{pageanchor=true}\n'
    for name in ['introduction','model','constructive']:
        main+=f'\\input{{{P}/{name}.tex}}\n'
    main+='\\input{revisions/or-r53-catalog-safe-certificates-20260926/capacity_potential.tex}\n'
    for name in ['exact_caps','hardness','price_duality','packing','branching','uniform_summary','study','conclusion']:
        main+=f'\\input{{{P}/{name}.tex}}\n'
    main+='\\clearpage\\phantomsection\\label{refs-start}\n'+f'\\input{{{P}/references.tex}}\n'+'\\label{refs-end}\\clearpage\n'+f'\\input{{{P}/generated/main_tables.tex}}\n\\end{{document}}\n'
    mathematical=(OLD/'companion_body.tex').read_text().split('\\section{Protocol, Models, and Timing Scope}')[0]
    (R/'retained_certificate_math.tex').write_text(mathematical)
    ec=pre+metrics+'\\externaldocument{.build/r54/main}[main.pdf]\n\\renewcommand{\\thesection}{EC.\\arabic{section}}\n\\renewcommand{\\thetable}{EC.\\arabic{table}}\n\\begin{document}\n'
    ec+='\\begin{center}{\\Large\\bfseries Electronic Companion}\\par '+TITLE+'\\par Anonymous\\end{center}\n'
    ec+='This companion distinguishes current diagnostics from retained antecedent proofs. The full historical sources and readers remain unchanged. Counts in the retained resource-checker discussion describe its antecedent validation, not the current 130-model test.\\par\n'
    ec+=f'\\input{{{P}/diagnostics.tex}}\n'
    for path in ['revisions/or-r52-resource-path-20260925/algorithm.tex','revisions/or-r52-resource-path-20260925/common_and_robustness.tex','revisions/or-r53-catalog-safe-certificates-20260926/safe_catalog.tex',f'{P}/retained_certificate_math.tex','revisions/or-r52-resource-path-20260925/production.tex']:
        ec+=f'\\input{{{path}}}\n'
    ec+='\\clearpage'+f'\\input{{{P}/references.tex}}\n\\clearpage\\input{{{P}/generated/ec_tables.tex}}\n\\end{{document}}\n'
    response=pre+metrics+'\\externaldocument{.build/r54/main}[../../main.pdf]\n\\externaldocument{.build/r54/electronic_companion}[../../electronic_companion.pdf]\n\\begin{document}\n'+f'\\input{{{P}/response_body.tex}}\n\\end{{document}}\n'
    for name,text in [('main.tex',main),('electronic_companion.tex',ec)]:
        (R/name).write_text(text);(ROOT/name).write_text(text)
    (R/'RESPONSE_TO_REFEREES.tex').write_text(response)
    if (R/'README.md').exists():(ROOT/'README.md').write_bytes((R/'README.md').read_bytes())
    if (R/'NDU_OR_submission_checklist.md').exists():(ROOT/'NDU_OR_submission_checklist.md').write_bytes((R/'NDU_OR_submission_checklist.md').read_bytes())
    mapping=dict(parent=PARENT,current=dict(main_sections=['model','constructive','exact_caps','hardness','price_duality','packing','branching','uniform_summary','study'],companion_retained=['R52 algorithm: full proof','R52 common eligibility and catalog robustness: full proof','R53 safe-catalog screening: full proof','R52 class-box, dyadic and grid-checker proofs','R52 production guarantee']),
                 historical_computations='Original R52/R53 study sources, generated tables, data, PDFs and predecessor readers remain at their exact paths; they are not current timings.',
                 root_predecessors={n:hashlib.sha256((saved/n).read_bytes()).hexdigest() for n in ['main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md']},
                 model_regularization='Cost continuity on the compact domain is made explicit for attained general convex extrema; every quadratic model and every executed input is unchanged.')
    (R/'CONTENT_MAP.json').write_text(json.dumps(mapping,indent=2)+'\n')
if __name__=='__main__':run()
