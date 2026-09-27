"""Compile anonymous Operations Research readers and reject typesetting errors."""
from pathlib import Path
import json,re,subprocess,shutil,hashlib,sys,platform,datetime
from assemble import run,ABSTRACT
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];B=ROOT/'.build/r52'
def tex(src):
    z=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-recorder',f'-output-directory={B}',str(src)],cwd=ROOT,capture_output=True,text=True,errors="replace")
    (B/(Path(src).stem+'.console.txt')).write_text(z.stdout+z.stderr)
    if z.returncode:raise RuntimeError(z.stdout[-7000:])
def build():
    B.mkdir(parents=True,exist_ok=True);run()
    for _ in range(3):
        for src in ['main.tex','electronic_companion.tex',str((R/'RESPONSE_TO_REFEREES.tex').relative_to(ROOT))]:tex(src)
    logs='\n'.join((B/(n+'.log')).read_text(errors='replace') for n in ['main','electronic_companion','RESPONSE_TO_REFEREES'])
    counts={k:len(re.findall(v,logs)) for k,v in dict(undefined_references=r'Reference .* undefined',undefined_citations=r'Citation .* undefined',duplicate_labels=r'Label .* multiply defined',overfull_boxes=r'Overfull \\[hv]box').items()}
    import fitz
    pages={n:len(fitz.open(B/(n+'.pdf'))) for n in ['main','electronic_companion','RESPONSE_TO_REFEREES']}
    aux=(B/'main.aux').read_text();a=int(re.search(r'\\newlabel\{refs-start\}\{\{[^}]*\}\{(\d+)\}',aux).group(1));b=int(re.search(r'\\newlabel\{refs-end\}\{\{[^}]*\}\{(\d+)\}',aux).group(1));nonrefs=pages['main']-(b-a+1)
    statement=re.compile(r'\\begin\{(?:theorem|proposition|lemma|corollary)\}(?:\[[^\]]*\])?\s*\\label\{([^}]+)\}')
    wanted=set()
    for p in R.glob('*.tex'):
        if p.name not in ['RESPONSE_TO_REFEREES.tex']:wanted.update(statement.findall(p.read_text()))
    allaux=aux+(B/'electronic_companion.aux').read_text();actual=set(re.findall(r'\\newlabel\{([^}]+)\}',allaux));missing=sorted(wanted-actual)
    source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in list(R.glob('*.tex'))+list((R/'code').glob('*.py'))}
    checks=dict(abstract_words=len(ABSTRACT.split()),main_nonreference_pages=nonrefs,submission_category='Regular manuscript' if nonrefs<=30 else 'Lengthy manuscript',equation_free_introduction=not any(z in (R/'introduction.tex').read_text() for z in ['$','\\[','\\(']),missing_math_labels=missing,math_labels=sorted(wanted),pages=pages,**counts)
    result=dict(status='PASS',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=sys.version,platform=platform.platform(),**checks,source_sha256=source_hashes,pdf_sha256={n:hashlib.sha256((B/(n+'.pdf')).read_bytes()).hexdigest() for n in pages})
    if any(counts.values()) or missing or nonrefs>40 or pages['electronic_companion']>pages['main'] or len(ABSTRACT.split())>200 or not checks['equation_free_introduction']:result['status']='FAIL'
    (R/'BUILD_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['source_sha256','pdf_sha256']},indent=2))
    for n in ['main','electronic_companion']:shutil.copy2(B/(n+'.pdf'),ROOT/(n+'.pdf'))
    shutil.copy2(B/'RESPONSE_TO_REFEREES.pdf',R/'RESPONSE_TO_REFEREES.pdf')
    if result['status']!='PASS':raise RuntimeError('Reader audit failed: inspect BUILD_VALIDATION.json and .build/r52')
if __name__=='__main__':build()
