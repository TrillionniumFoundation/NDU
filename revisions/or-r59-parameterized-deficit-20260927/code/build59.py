"""Assemble the R59 readers, preserve R58 roots, and validate the exact input graph."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
import fitz
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];OLD=ROOT/'revisions/or-r58-structural-referee-20260926';REL=R.relative_to(ROOT).as_posix();OUT=ROOT/'.build/r59'
TITLE='Finite-Catalog Resource Allocation: Exact Path Representations and Menu Complexity'
def inp(path):return '\\input{'+str(path)+'}\n'
def own(name):return inp(f'{REL}/{name}.tex')
def old(name):return inp(f'{OLD.relative_to(ROOT)}/{name}.tex')
def preserve():
    dest=R/'retained_r58';dest.mkdir(exist_ok=True)
    for name in ['main.tex','electronic_companion.tex','main.pdf','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md']:
        src=ROOT/name;p=dest/name
        if not p.exists() and src.exists():shutil.copyfile(src,p)
    if not (dest/'main.tex').exists():raise RuntimeError('Missing predecessor source')
    text=(dest/'main.tex').read_text()
    if 'structural-referee-20260926' not in text:raise RuntimeError('Wrong predecessor capture')
    paths=list(OLD.rglob('*'))+[ROOT/p for p in ['revisions/or-r52-resource-path-20260925','revisions/or-r53-catalog-safe-certificates-20260926','revisions/or-r54-exact-price-path-20260926']]
    # The complete inherited directory tree remains untouched; root replacements are copied.
    manifest={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.glob('*') if p.is_file()}
    (R/'PRESERVATION.json').write_text(json.dumps({'author_base_commit':'1edd6d929e20f50a14ec6ef9beab4a37fa44fe39','review_commit':'fe068d2a978a44548688b6052d4f210473394417','changed_root_predecessors':manifest,'prior_scientific_paths':'All paths under prior revisions remain unchanged; verify with git diff against author base.'},indent=2)+'\n')

def assemble():
    preserve()
    pre=(R/'retained_r58/main.tex').read_text().split('\\externaldocument')[0]
    pre=re.sub(r'\\hypersetup\{pdftitle=\{[^}]+\},pdfauthor=\{Anonymous\}\}',lambda m:r'\hypersetup{pdftitle={'+TITLE+r'},pdfauthor={Anonymous}}',pre)
    pre=pre.replace('Renewal Design: Menus and Deficit Paths','Finite-Catalog Resource Allocation')
    ext=lambda name:'\\externaldocument{.build/r59/'+name+'}['+name+'.pdf]\n'
    main=pre+ext('electronic_companion')+r'''\begin{document}\hypersetup{pageanchor=false}
\begin{titlepage}\centering{\Large\bfseries '''+TITLE+r'''\par}
\vspace{0.25in}Anonymous manuscript for Operations Research --- R59\par\vspace{0.2in}
\begin{minipage}{\textwidth}\textbf{Abstract.} '''+(R/'ABSTRACT.txt').read_text().strip()+r'''
\par\vspace{0.15in}\textbf{Keywords:} resource allocation; dynamic programming; parameterized complexity.
\par\vspace{0.1in}\textbf{Subject classifications:} Programming: resource allocation; Dynamic programming: finite-catalog design.
\par\vspace{0.1in}\textbf{Area of review:} Optimization.\end{minipage}\vfill September 27, 2026\end{titlepage}
\hypersetup{pageanchor=true}
'''
    main+=own('introduction')+old('model')+own('feasibility')
    main+=r'''\paragraph{Units and loss.} Obligations and caps use one normalized resource unit. Rewards, service costs and installation charges share a net-value unit. An additive tolerance is stated in that value unit; rescaling every payoff and the tolerance by the same positive factor preserves its decision meaning. The present theory makes no empirical currency calibration.
'''
    main+=old('constructive')+inp('revisions/or-r53-catalog-safe-certificates-20260926/capacity_potential.tex')+own('packing')+own('conservative_paths')+own('parameterized')+old('deficit_paths')+own('grouping')+own('study')+own('conclusion')
    main+=r'\clearpage\phantomsection\label{refs-start}'+'\n'+own('references')+r'\label{refs-end}\clearpage'+'\n'+own('generated/antecedents_table')+own('generated/study_tables')+'\\end{document}\n'
    ec=pre+ext('main')+r'''\renewcommand{\thesection}{EC.\arabic{section}}
\renewcommand{\thetable}{EC.\arabic{table}}\renewcommand{\thefigure}{EC.\arabic{figure}}
\begin{document}\begin{center}{\Large\bfseries Electronic Companion}\par '''+TITLE+r'''\par Anonymous --- R59\end{center}
This companion retains the full secondary structural results, price-search arguments and present formulation details. Historical empirical tables, operational architecture and antecedent diagnostics remain in the complete unmodified R58 article and companion in the accompanying retained-reader directory. They are historical evidence, not relabeled current executions.
'''
    ec+=r'\section{Exact Structural Regimes and Support Bounds}'+'\n'
    for name in ['exact_caps','hardness','small_menus','robust_types']:ec+=old(name)
    for name in ['price_duality','branching','uniform_summary','saturation','lattice']:ec+=old(name)
    ec+=own('formulation')
    ec+=r'\section{Retained Resource Approximation Details}'+'\n'+inp('revisions/or-r52-resource-path-20260925/algorithm.tex')
    ec+=r'''\paragraph{Preserved antecedent diagnostics.} The full R58 readers retain the original correctness checks, operational units discussion, screening panel, equal-book-count diagnostic and complete earlier numerical outputs. These are not repeated as new results. The preservation map identifies their unchanged source paths and byte-identical predecessor copies.
'''
    ec+=r'\clearpage'+'\n'+own('references')+'\\end{document}\n'
    response=pre+ext('main')+ext('electronic_companion')+r'\begin{document}\begin{center}{\Large\bfseries Response to the R58 Referee Report}\par '+TITLE+r'\par R59 --- September 27, 2026\end{center}'+'\n'+own('response_body')+'\\end{document}\n'
    for name,text in [('main',main),('electronic_companion',ec),('RESPONSE_TO_REFEREES',response)]:
        (R/f'{name}.tex').write_text(text)
        if name!='RESPONSE_TO_REFEREES':(ROOT/f'{name}.tex').write_text(text)

def build():
    assemble();OUT.mkdir(parents=True,exist_ok=True)
    srcs=['main.tex','electronic_companion.tex',f'{REL}/RESPONSE_TO_REFEREES.tex']
    for cycle in range(4):
        for src in srcs:
            name=Path(src).stem
            cmd=['pdflatex','-interaction=nonstopmode','-halt-on-error','-recorder',f'-output-directory={OUT}',src]
            p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,errors='replace');(OUT/f'{name}.console.txt').write_text(p.stdout+p.stderr)
            if p.returncode:raise RuntimeError(p.stdout[-7000:])
    logs='\n'.join((OUT/f'{Path(s).stem}.log').read_text(errors='replace') for s in srcs)
    diagnostics={key:len(re.findall(pattern,logs)) for key,pattern in dict(undefined_references=r'Reference .* undefined',undefined_citations=r'Citation .* undefined',duplicate_labels=r'Label .* multiply defined',overfull_boxes=r'Overfull \\[hv]box',undefined_control_sequences=r'Undefined control sequence').items()}
    pages={Path(s).stem:len(fitz.open(OUT/f'{Path(s).stem}.pdf')) for s in srcs}
    aux=(OUT/'main.aux').read_text();rp=[]
    for label in ['refs-start','refs-end']:rp.append(int(re.search(r'\\newlabel\{'+label+r'\}\{\{[^}]*\}\{(\d+)\}',aux).group(1)))
    nonref=pages['main']-(rp[1]-rp[0]+1)
    abstract=(R/'ABSTRACT.txt').read_text();intro=(R/'introduction.tex').read_text();inputs={}
    for src in srcs:
        name=Path(src).stem;seen=set()
        for line in (OUT/f'{name}.fls').read_text().splitlines():
            if not line.startswith('INPUT '):continue
            p=Path(line[6:]);p=p if p.is_absolute() else ROOT/p
            try:rel=p.resolve().relative_to(ROOT)
            except ValueError:continue
            if not str(rel).startswith('.build') and p.is_file():seen.add(str(rel))
        inputs[name]=sorted(seen)
    allaux=aux+(OUT/'electronic_companion.aux').read_text()
    labels={k:v for k,v in re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]+)\}',allaux)}
    essential=['thm:wone59','lem:groupsum59','thm:recognition59','thm:abstractapprox59','thm:grouping59','thm:packing54','thm:deficit56','thm:approx56','prop:micp59']
    blank={name:[i+1 for i,p in enumerate(fitz.open(OUT/f'{name}.pdf')) if not p.get_text().strip()] for name in pages}
    report=dict(status='PASS',pages=pages,main_nonreference_pages=nonref,reference_page_range=rp,abstract_words=len(abstract.split()),text_only_abstract=not any(t in abstract for t in ('$','\\[','\\(')),equation_free_introduction=not any(t in intro for t in ('$','\\[','\\(')),submission_category='Regular manuscript' if nonref<=30 else 'Lengthy manuscript',missing_essential_labels=[x for x in essential if x not in labels],blank_pages=blank,**diagnostics,reader_inputs=inputs,source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(set().union(*map(set,inputs.values())))},pdf_sha256={name:hashlib.sha256((OUT/f'{name}.pdf').read_bytes()).hexdigest() for name in pages},theorem_number_map={x:labels.get(x) for x in essential})
    if any(diagnostics.values()) or report['missing_essential_labels'] or any(blank.values()) or len(abstract.split())>200 or not report['text_only_abstract'] or not report['equation_free_introduction'] or nonref>40 or pages['electronic_companion']>pages['main']:report['status']='FAIL'
    (R/'BUILD_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('reader_inputs','source_sha256','pdf_sha256')},indent=2))
    if report['status']!='PASS':raise RuntimeError('R59 build diagnostics failed')
    for name in pages:
        shutil.copyfile(OUT/f'{name}.pdf',R/f'{name}.pdf')
        if name!='RESPONSE_TO_REFEREES':shutil.copyfile(OUT/f'{name}.pdf',ROOT/f'{name}.pdf')
    return report
if __name__=='__main__':build()
