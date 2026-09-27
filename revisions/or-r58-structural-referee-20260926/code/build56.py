"""Assemble, compile and validate the actual R58 reader graph from repo root."""
from pathlib import Path
import datetime,hashlib,json,re,shutil,subprocess,sys,platform
import fitz
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];OUT=ROOT/'.build/r58'
REL=R.relative_to(ROOT).as_posix()
TITLE='Finite-Catalog Renewal Design: Small Menus and Resource-Deficit Paths'
def inp(s):return '\\input{'+s+'}\n'
def assemble():
    old=(R/'predecessor/main.tex').read_text();pre=old.split('\\externaldocument')[0]
    pre=pre.replace('Exact Renewal Path Representations','Renewal Design: Menus and Deficit Paths')
    pre=pre.replace('amsmath,amsthm,booktabs,array,longtable','amsmath,amsthm,booktabs,array,longtable,graphicx')
    pre+=r'\hypersetup{pdftitle={'+TITLE+r'},pdfauthor={Anonymous}}'+'\n'
    ext=lambda name:'\\externaldocument{.build/r58/'+name+'}['+name+'.pdf]\n'
    main=pre+ext('electronic_companion')+r'''\begin{document}\hypersetup{pageanchor=false}
\begin{titlepage}\centering{\Large\bfseries '''+TITLE+r'''\par}
\vspace{0.25in}Anonymous manuscript for Operations Research --- R58\par\vspace{0.2in}
\begin{minipage}{\textwidth}\textbf{Abstract.} '''+(R/'ABSTRACT.txt').read_text().strip()+r'''
\par\vspace{0.15in}\textbf{Keywords:} renewal contracts; dynamic programming; global optimization.
\par\vspace{0.1in}\textbf{Subject classifications:} Dynamic programming: finite command design; Programming: global optimization.
\par\vspace{0.1in}\textbf{Area of review:} Optimization.\end{minipage}\vfill September 26, 2026\end{titlepage}
\hypersetup{pageanchor=true}
'''
    sections=['introduction','model','constructive','@revisions/or-r53-catalog-safe-certificates-20260926/capacity_potential','exact_caps','hardness','small_menus','robust_types','price_duality','packing','branching','uniform_summary','deficit_paths','saturation','lattice','study','new_study','conclusion']
    for s in sections:main+=inp(s[1:]+'.tex' if s.startswith('@') else f'{REL}/{s}.tex')
    main+=r'\clearpage\phantomsection\label{refs-start}'+'\n'+inp(f'{REL}/references.tex')+r'\label{refs-end}\clearpage'+'\n'+inp(f'{REL}/generated/main_tables.tex')+'\\end{document}\n'
    (R/'main.tex').write_text(main);(ROOT/'main.tex').write_text(main)
    ec=pre+ext('main')+r'''\renewcommand{\thesection}{EC.\arabic{section}}
\renewcommand{\thetable}{EC.\arabic{table}}
\renewcommand{\thefigure}{EC.\arabic{figure}}
\begin{document}
\begin{center}{\Large\bfseries Electronic Companion}\par '''+TITLE+r'''\par Anonymous\end{center}
This companion separates the current evidence and operational interface from retained antecedent proofs and experiments. Historical counts, tolerances and timings describe their original execution, not the current rerun. The complete preceding readers remain separately available.
'''
    ec+=inp(f'{REL}/structural_validation58.tex')+inp(f'{REL}/diagnostics56.tex')+inp(f'{REL}/operations_interface.tex')
    ec+=r'\section*{Retained antecedent proofs and diagnostics}'+'\n'
    for p in ['or-r54-exact-price-path-20260926/diagnostics','or-r52-resource-path-20260925/algorithm','or-r52-resource-path-20260925/common_and_robustness','or-r53-catalog-safe-certificates-20260926/safe_catalog','or-r54-exact-price-path-20260926/retained_certificate_math','or-r52-resource-path-20260925/production']:
        ec+=inp('revisions/'+p+'.tex')
    ec+=r'''\paragraph{Interpretation of the retained production parameters.}
In the compatible-production illustration, a module's return coefficient is the modeled contribution of allocating one unit of the conserved production resource to that eligible module. Its capacity limits that allocation, and its installation charge is paid once when the module is selected. The recorded coefficients are synthetic scenario inputs, not estimated revenues or calibrated physical yields. The example illustrates the same capacity-repair mechanism in a different decision description; it does not supply an independent field validation.
'''
    ec+=r'\clearpage'+'\n'+inp(f'{REL}/references.tex')+r'\clearpage'+'\n'
    ec+=inp(f'{REL}/generated/proof_table56.tex')
    ec+=inp('revisions/or-r54-exact-price-path-20260926/generated/ec_tables.tex')
    ec+=inp('revisions/or-r54-exact-price-path-20260926/generated/main_tables.tex')+'\\end{document}\n'
    (R/'electronic_companion.tex').write_text(ec);(ROOT/'electronic_companion.tex').write_text(ec)
    response=pre+ext('main')+ext('electronic_companion')+r'\begin{document}\begin{center}{\Large\bfseries Response to the R56, R55, and R54 Referee Reports}\par '+TITLE+r'\par R58 --- September 26, 2026\end{center}'+'\n'+inp(f'{REL}/response_body.tex')+'\\end{document}\n'
    (R/'RESPONSE_TO_REFEREES.tex').write_text(response)

def build():
    assemble();OUT.mkdir(parents=True,exist_ok=True)
    sources=['main.tex','electronic_companion.tex',f'{REL}/RESPONSE_TO_REFEREES.tex']
    for cycle in range(4):
        for source in sources:
            stem=Path(source).stem
            job=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-recorder',f'-output-directory={OUT}',source],cwd=ROOT,capture_output=True,text=True,errors='replace')
            (OUT/(stem+'.console.txt')).write_text(job.stdout+job.stderr)
            if job.returncode:raise RuntimeError(job.stdout[-8000:])
    logs='\n'.join((OUT/(Path(s).stem+'.log')).read_text(errors='replace') for s in sources)
    diagnostics={key:len(re.findall(pattern,logs)) for key,pattern in dict(undefined_references=r'Reference .* undefined',undefined_citations=r'Citation .* undefined',duplicate_labels=r'Label .* multiply defined',overfull_boxes=r'Overfull \\[hv]box',undefined_control_sequences=r'Undefined control sequence').items()}
    pages={Path(s).stem:len(fitz.open(OUT/(Path(s).stem+'.pdf'))) for s in sources}
    aux=(OUT/'main.aux').read_text();allaux=aux+(OUT/'electronic_companion.aux').read_text()
    refpages=[]
    for label in ('refs-start','refs-end'):
        match=re.search(r'\\newlabel\{'+label+r'\}\{\{[^}]*\}\{(\d+)\}',aux)
        if match is None:raise RuntimeError('Missing reference label '+label)
        refpages.append(int(match.group(1)))
    nonrefs=pages['main']-(refpages[1]-refpages[0]+1)
    abstract=(R/'ABSTRACT.txt').read_text();intro=(R/'introduction.tex').read_text()
    labels=set(re.findall(r'\\newlabel\{([^}]+)\}',allaux))
    required={'thm:path52','thm:approx52','thm:common52','thm:screen53','prop:potential53','thm:hard54','thm:twocommand54','thm:price54','thm:packing54','thm:branch54'}
    pat=r'\\begin\{(?:theorem|proposition|lemma|corollary)\}(?:\[[^\]]*\])?\s*\\label\{([^}]+)\}'
    for p in R.glob('*.tex'):
        if p.name not in ['RESPONSE_TO_REFEREES.tex','response_body.tex']:required.update(re.findall(pat,p.read_text()))
    blanks={name:[i+1 for i,p in enumerate(fitz.open(OUT/(name+'.pdf'))) if not p.get_text().strip()] for name in pages}
    report=dict(status='PASS',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=sys.version,platform=platform.platform(),pages=pages,main_nonreference_pages=nonrefs,reference_page_range=refpages,abstract_words=len(abstract.split()),text_only_abstract=not any(t in abstract for t in ('$','\\[','\\(')),equation_free_introduction=not any(t in intro for t in ('$','\\[','\\(')),submission_category='Regular manuscript' if nonrefs<=30 else 'Lengthy manuscript',missing_required_labels=sorted(required-labels),required_mathematical_labels=sorted(required),blank_pages=blanks,**diagnostics)
    # FLS lists establish what is actually in the compiled readers.
    reader_inputs={}
    for name in pages:
        entries=set()
        for line in (OUT/(name+'.fls')).read_text().splitlines():
            if not line.startswith('INPUT '):continue
            p=Path(line[6:]);p=p if p.is_absolute() else ROOT/p
            try:r=p.resolve().relative_to(ROOT)
            except ValueError:continue
            if str(r).startswith('.build') or not p.is_file():continue
            entries.add(str(r))
        reader_inputs[name]=sorted(entries)
    report['reader_inputs']=reader_inputs
    report['source_sha256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(set().union(*map(set,reader_inputs.values())))}
    report['pdf_sha256']={name:hashlib.sha256((OUT/(name+'.pdf')).read_bytes()).hexdigest() for name in pages}
    report['theorem_number_map']={label:re.search(r'\\newlabel\{'+re.escape(label)+r'\}\{\{([^}]+)\}',allaux).group(1) for label in sorted(required) if label in labels}
    if any(diagnostics.values()) or report['missing_required_labels'] or any(blanks.values()) or report['abstract_words']>200 or not report['equation_free_introduction'] or not report['text_only_abstract'] or nonrefs>40 or pages['electronic_companion']>pages['main']:report['status']='FAIL'
    (R/'BUILD_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['reader_inputs','source_sha256','pdf_sha256','required_mathematical_labels','theorem_number_map']},indent=2))
    if report['status']!='PASS':raise RuntimeError('Reader validation failed')
    for name in ['main','electronic_companion']:
        shutil.copyfile(OUT/(name+'.pdf'),ROOT/(name+'.pdf'));shutil.copyfile(OUT/(name+'.pdf'),R/(name+'.pdf'))
    shutil.copyfile(OUT/'RESPONSE_TO_REFEREES.pdf',R/'RESPONSE_TO_REFEREES.pdf')
    return report
if __name__=='__main__':build()
