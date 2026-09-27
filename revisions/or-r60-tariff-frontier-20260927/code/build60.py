"""Assemble standalone R60 readers, preserve reviewed roots, and validate PDFs."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess
import fitz
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];OUT=ROOT/'.build/r60'
REL=R.relative_to(ROOT).as_posix();OLD=ROOT/'revisions/or-r59-parameterized-deficit-20260927'
TITLE='Finite-Catalog Resource Allocation: A Tariff-Sensitive Complexity Frontier'
REVIEW='cc7ac349969adc9186e9a75f8d01f76ad485c3ba'
ORIGINS={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def expand(text):
    def replace(m):
        name=m.group(1);p=ROOT/name
        if not p.suffix:p=p.with_suffix('.tex')
        assert p.is_file(),p
        ORIGINS[p.relative_to(ROOT).as_posix()]=sha(p)
        return '\n% BEGIN retained/current source: '+p.relative_to(ROOT).as_posix()+'\n'+expand(p.read_text())+'\n% END source\n'
    return re.sub(r'\\input\{([^}]+)\}',replace,text)
def source(path):
    p=ROOT/path;ORIGINS[p.relative_to(ROOT).as_posix()]=sha(p);return expand(p.read_text())
def old58(name):return source('revisions/or-r58-structural-referee-20260926/'+name+'.tex')
def old59(name):return source('revisions/or-r59-parameterized-deficit-20260927/'+name+'.tex')
def own(name):return source(REL+'/sections/'+name+'.tex')
def preserve():
    dest=R/'retained_r59';dest.mkdir(exist_ok=True)
    for name in ['main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md']:
        p=dest/name
        if not p.exists():
            assert (ROOT/name).is_file(),name;shutil.copyfile(ROOT/name,p)
    assert sha(dest/'main.tex')=='e3e31c7725f0921e7bc466d5419c97f40087046d3a126d3842812abe6971957d','Wrong reviewed reader'
    return {p.name:sha(p) for p in dest.iterdir() if p.is_file()}
def assemble():
    preserved=preserve();ORIGINS.clear()
    pre=(R/'retained_r59/main.tex').read_text().split('\\externaldocument')[0]
    pre=re.sub(r'\\hypersetup\{pdftitle=\{[^}]+\},pdfauthor=\{Anonymous\}\}',lambda m:r'\hypersetup{pdftitle={'+TITLE+r'},pdfauthor={Anonymous}}',pre)
    pre=expand(pre)
    ext=lambda n:r'\externaldocument{.build/r60/'+n+'}['+n+'.pdf]\n'
    main=pre+ext('electronic_companion')+r'''\begin{document}\hypersetup{pageanchor=false}
\begin{titlepage}\centering{\Large\bfseries '''+TITLE+r'''\par}
\vspace{0.25in}Anonymous manuscript for Operations Research --- R60\par\vspace{0.2in}
\begin{minipage}{\textwidth}\textbf{Abstract.} '''+(R/'ABSTRACT.txt').read_text().strip()+r'''
\par\vspace{0.15in}\textbf{Keywords:} resource allocation; dynamic programming; parameterized complexity.
\par\vspace{0.1in}\textbf{Subject classifications:} Programming: resource allocation; Dynamic programming: finite-catalog design.
\par\vspace{0.1in}\textbf{Area of review:} Optimization.\end{minipage}\vfill September 27, 2026\end{titlepage}
\hypersetup{pageanchor=true}
'''
    main+=own('introduction')+old58('model')+old59('feasibility')
    main+=r'''\paragraph{Units and loss.} Obligations and caps use one normalized resource unit. Rewards, service costs and installation charges share a net-value unit. An additive tolerance is stated in that value unit; rescaling every payoff and the tolerance by the same positive factor preserves its decision meaning. The present theory makes no empirical currency calibration.
'''
    main+=old58('constructive')+source('revisions/or-r53-catalog-safe-certificates-20260926/capacity_potential.tex')+old59('packing')+old59('conservative_paths')
    main+=r'''\paragraph{The path quantifier.} The preceding recognition theorem concerns all source-to-sink paths in the retained graph. Under an edge allowance it is sufficient, but need not be necessary. The exact bounded-path recognition, witness and oracle-cost statements are in Theorem~\ref{thm:bounded60}; its layered construction does not add a second edge-count factor to the approximation recurrence.
'''
    complexity=old59('parameterized');pos=complexity.index('\\begin{theorem}')
    main+=complexity[:pos]+own('decision')+complexity[pos:]+own('tariff')+old58('deficit_paths')+own('price_bridge')+old59('grouping')+own('study')+own('conclusion')
    main+=r'\clearpage\phantomsection\label{refs-start}'+'\n'+own('references')+r'\label{refs-end}\clearpage'+'\n'+own('frontier_table')+source(REL+'/generated/new_tables.tex')+'\\end{document}\n'
    ec=pre+ext('main')+r'''\renewcommand{\thesection}{EC.\arabic{section}}
\renewcommand{\thetable}{EC.\arabic{table}}\renewcommand{\thefigure}{EC.\arabic{figure}}
\begin{document}\begin{center}{\Large\bfseries Electronic Companion}\par '''+TITLE+r'''\par Anonymous --- R60\end{center}
This companion contains the complete retained secondary theory and proof details, the length-aware conservation extension, the nonrenewal application and reproducibility details. The reviewed R59 readers and earlier evidence remain unmodified; historical results are not relabeled as new executions.
\section{Exact Structural Regimes and Support Bounds}
'''
    for n in ['exact_caps','hardness','small_menus','robust_types','price_duality','branching','uniform_summary','saturation','lattice']:ec+=old58(n)
    ec+=old59('formulation')+r'\section{Retained Resource Approximation Details}'+'\n'+source('revisions/or-r52-resource-path-20260925/algorithm.tex')
    ec+=own('bounded_paths')+own('evidence_details')
    if (R/'generated/tail_table.tex').exists():ec+=r'\paragraph{Tail-cost panel.} Table~\ref{tab:tails60} displays the three-second request tail costs; the archive reports all budgets and phase denominators.'+'\n'
    ec+=r'\paragraph{Historical panels.} Tables~\ref{tab:antecedents59}--\ref{tab:study59} are retained from the reviewed reader and describe earlier evidence, not the new prospective study.'+'\n'
    ec+=r'\clearpage'+'\n'+own('references')+r'\clearpage'+'\n'+old59('generated/antecedents_table')+old59('generated/study_tables')
    if (R/'generated/tail_table.tex').exists():ec+=source(REL+'/generated/tail_table.tex')
    ec+='\\end{document}\n'
    response=pre+ext('main')+ext('electronic_companion')+r'\begin{document}\begin{center}{\Large\bfseries Response to the R59 Referee Report}\par '+TITLE+r'\par R60 --- September 27, 2026\end{center}'+'\n'+own('response_body')+'\\end{document}\n'
    for name,text in [('main',main),('electronic_companion',ec),('RESPONSE_TO_REFEREES',response)]:
        assert not re.search(r'\\input\{',text)
        (R/f'{name}.tex').write_text(text)
        if name!='RESPONSE_TO_REFEREES':(ROOT/f'{name}.tex').write_text(text)
    priorlabels={x for p in ORIGINS if '/or-r60-' not in p for x in re.findall(r'\\label\{([^}]+)\}',(ROOT/p).read_text())}
    combined=main+ec;missing=[x for x in priorlabels if '\\label{'+x+'}' not in combined]
    assert not missing,missing
    evidence=dict(review_commit=REVIEW,reviewed_roots=preserved,current_sources_self_contained=True,old_scientific_labels_retained=len(priorlabels),missing_old_labels=missing,source_sections=ORIGINS,prior_revision_policy='All prior revision paths remain unchanged; current readers expand their mathematical contents.')
    (R/'PRESERVATION.json').write_text(json.dumps(evidence,indent=2)+'\n')

def build():
    assemble();OUT.mkdir(parents=True,exist_ok=True)
    srcs=['main.tex','electronic_companion.tex',REL+'/RESPONSE_TO_REFEREES.tex']
    for cycle in range(4):
        for src in srcs:
            name=Path(src).stem;cmd=['pdflatex','-interaction=nonstopmode','-halt-on-error','-recorder','-output-directory='+str(OUT),src]
            p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,errors='replace');(OUT/(name+'.console.txt')).write_text(p.stdout+p.stderr)
            if p.returncode:raise RuntimeError(p.stdout[-7000:])
    logs='\n'.join((OUT/(Path(s).stem+'.log')).read_text(errors='replace') for s in srcs)
    diagnostics={k:len(re.findall(v,logs)) for k,v in dict(undefined_references=r'Reference .* undefined',undefined_citations=r'Citation .* undefined',duplicate_labels=r'Label .* multiply defined',overfull_boxes=r'Overfull \\[hv]box',undefined_control_sequences=r'Undefined control sequence').items()}
    pages={Path(s).stem:len(fitz.open(OUT/(Path(s).stem+'.pdf'))) for s in srcs}
    aux=(OUT/'main.aux').read_text();rp=[int(re.search(r'\\newlabel\{'+label+r'\}\{\{[^}]*\}\{(\d+)\}',aux).group(1)) for label in ('refs-start','refs-end')]
    nonref=pages['main']-(rp[1]-rp[0]+1);abstract=(R/'ABSTRACT.txt').read_text();intro=(R/'sections/introduction.tex').read_text()
    allaux=aux+(OUT/'electronic_companion.aux').read_text();labels={k:v for k,v in re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]+)\}',allaux)}
    essential=['thm:wone59','lem:groupsum59','thm:recognition59','thm:abstractapprox59','thm:grouping59','thm:packing54','thm:deficit56','thm:approx56','prop:micp59','thm:tariff60','lem:capacity60','cor:fee60','thm:pricebridge60','thm:bounded60']
    blank={n:[i+1 for i,p in enumerate(fitz.open(OUT/(n+'.pdf'))) if not p.get_text().strip()] for n in pages}
    report=dict(status='PASS',pages=pages,main_nonreference_pages=nonref,reference_page_range=rp,abstract_words=len(abstract.split()),text_only_abstract=not any(t in abstract for t in ('$','\\[','\\(')),equation_free_introduction=not any(t in intro for t in ('$','\\[','\\(')),submission_category='Regular manuscript' if nonref<=30 else 'Lengthy manuscript',missing_essential_labels=[x for x in essential if x not in labels],blank_pages=blank,standalone_readers=True,**diagnostics,source_sha256={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'main.tex',ROOT/'electronic_companion.tex',R/'RESPONSE_TO_REFEREES.tex']},pdf_sha256={n:sha(OUT/(n+'.pdf')) for n in pages},theorem_number_map={x:labels.get(x) for x in essential})
    if any(diagnostics.values()) or report['missing_essential_labels'] or any(blank.values()) or len(abstract.split())>200 or not report['text_only_abstract'] or not report['equation_free_introduction'] or nonref>40 or pages['electronic_companion']>pages['main']:report['status']='FAIL'
    (R/'BUILD_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    if report['status']!='PASS':raise RuntimeError('R60 build validation failed')
    for n in pages:
        shutil.copyfile(OUT/(n+'.pdf'),R/(n+'.pdf'))
        if n!='RESPONSE_TO_REFEREES':shutil.copyfile(OUT/(n+'.pdf'),ROOT/(n+'.pdf'))
    return report
if __name__=='__main__':build()
