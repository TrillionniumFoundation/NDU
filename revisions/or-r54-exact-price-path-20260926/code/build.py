"""Compile all R54 readers and check journal layout, labels and file hashes."""
from pathlib import Path
import datetime,hashlib,json,re,shutil,subprocess,sys,platform
import fitz
from assemble import run as assemble
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];OUT=ROOT/'.build/r54'

def build():
    assemble();OUT.mkdir(parents=True,exist_ok=True)
    sources=['main.tex','electronic_companion.tex',str((R/'RESPONSE_TO_REFEREES.tex').relative_to(ROOT))]
    for cycle in range(4):
        for source in sources:
            stem=Path(source).stem
            job=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-recorder',f'-output-directory={OUT}',source],cwd=ROOT,capture_output=True,text=True,errors='replace')
            (OUT/(stem+'.console.txt')).write_text(job.stdout+job.stderr)
            if job.returncode:raise RuntimeError(job.stdout[-7000:])
    logs='\n'.join((OUT/(Path(s).stem+'.log')).read_text(errors='replace') for s in sources)
    diagnostics={key:len(re.findall(pattern,logs)) for key,pattern in dict(undefined_references=r'Reference .* undefined',undefined_citations=r'Citation .* undefined',duplicate_labels=r'Label .* multiply defined',overfull_boxes=r'Overfull \\[hv]box',undefined_control_sequences=r'Undefined control sequence').items()}
    pages={Path(s).stem:len(fitz.open(OUT/(Path(s).stem+'.pdf'))) for s in sources}
    aux=(OUT/'main.aux').read_text();allaux=aux+(OUT/'electronic_companion.aux').read_text()
    refpages=[]
    for label in ('refs-start','refs-end'):
        match=re.search(r'\\newlabel\{'+label+r'\}\{\{[^}]*\}\{(\d+)\}',aux)
        if match is None:raise RuntimeError('Missing reference-range label '+label)
        refpages.append(int(match.group(1)))
    nonrefs=pages['main']-(refpages[1]-refpages[0]+1)
    abstract=(R/'ABSTRACT.txt').read_text();intro=(R/'introduction.tex').read_text()
    equation_free=not any(token in intro for token in ('$','\\[','\\('))
    abstract_plain=not any(token in abstract for token in ('$','\\[','\\('))
    labels=set(re.findall(r'\\newlabel\{([^}]+)\}',allaux))
    required=set()
    pattern=r'\\begin\{(?:theorem|proposition|lemma|corollary)\}(?:\[[^\]]*\])?\s*\\label\{([^}]+)\}'
    for path in R.glob('*.tex'):
        if path.name not in ['RESPONSE_TO_REFEREES.tex','response_body.tex']:
            required.update(re.findall(pattern,path.read_text()))
    required.update(['thm:path52','thm:approx52','thm:common52','thm:screen53','prop:potential53','thm:hard54','thm:twocommand54','thm:price54','thm:packing54','thm:branch54'])
    missing=sorted(required-labels)
    blanks={name:[i+1 for i,p in enumerate(fitz.open(OUT/(name+'.pdf'))) if not p.get_text().strip()] for name in pages}
    report=dict(status='PASS',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=sys.version,platform=platform.platform(),pages=pages,main_nonreference_pages=nonrefs,reference_page_range=refpages,abstract_words=len(abstract.split()),text_only_abstract=abstract_plain,equation_free_introduction=equation_free,submission_category='Regular manuscript' if nonrefs<=30 else 'Lengthy manuscript',missing_required_labels=missing,required_mathematical_labels=sorted(required),blank_pages=blanks,**diagnostics)
    report['source_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(R.rglob('*')) if p.is_file() and p.suffix in ['.tex','.py'] and 'predecessor' not in p.parts}
    report['pdf_sha256']={name:hashlib.sha256((OUT/(name+'.pdf')).read_bytes()).hexdigest() for name in pages}
    if any(diagnostics.values()) or missing or any(blanks.values()) or len(abstract.split())>200 or not (equation_free and abstract_plain) or nonrefs>30 or pages['electronic_companion']>pages['main']:report['status']='FAIL'
    (R/'BUILD_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['source_sha256','pdf_sha256','required_mathematical_labels']},indent=2))
    if report['status']!='PASS':raise RuntimeError('Reader validation failed')
    for name in ['main','electronic_companion']:
        shutil.copyfile(OUT/(name+'.pdf'),ROOT/(name+'.pdf'));shutil.copyfile(OUT/(name+'.pdf'),R/(name+'.pdf'))
    shutil.copyfile(OUT/'RESPONSE_TO_REFEREES.pdf',R/'RESPONSE_TO_REFEREES.pdf')
    return report
if __name__=='__main__':build()
