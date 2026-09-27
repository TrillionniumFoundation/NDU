"""Build and audit the R53 article, companion, and point-by-point response."""
from pathlib import Path
import datetime,hashlib,json,re,shutil,subprocess,sys
import fitz
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];OUT=ROOT/'.build/r53'
def build():
    OUT.mkdir(parents=True,exist_ok=True)
    for name in ('main.tex','electronic_companion.tex'):
        (ROOT/name).write_bytes((R/name).read_bytes())
    sources=['main.tex','electronic_companion.tex',str((R/'RESPONSE_TO_REFEREES.tex').relative_to(ROOT))]
    for _ in range(3):
        for source in sources:
            job=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-recorder',f'-output-directory={OUT}',source],cwd=ROOT,capture_output=True,text=True,errors='replace')
            (OUT/(Path(source).stem+'.console.txt')).write_text(job.stdout+job.stderr)
            if job.returncode:raise RuntimeError(job.stdout[-8000:])
    logs='\n'.join((OUT/(Path(x).stem+'.log')).read_text(errors='replace') for x in sources)
    counts={name:len(re.findall(pattern,logs)) for name,pattern in dict(undefined_references=r'Reference .* undefined',undefined_citations=r'Citation .* undefined',duplicate_labels=r'Label .* multiply defined',overfull_boxes=r'Overfull \\[hv]box').items()}
    pages={Path(x).stem:len(fitz.open(OUT/(Path(x).stem+'.pdf'))) for x in sources}
    aux=(OUT/'main.aux').read_text();start=int(re.search(r'\\newlabel\{refs-start\}\{\{[^}]*\}\{(\d+)\}',aux).group(1));end=int(re.search(r'\\newlabel\{refs-end\}\{\{[^}]*\}\{(\d+)\}',aux).group(1))
    nonrefs=pages['main']-(end-start+1)
    words=len((R/'ABSTRACT.txt').read_text().split());equation_free=not any(s in (R/'introduction.tex').read_text() for s in ('$','\\[','\\('))
    required=['prop:potential53','thm:screen53','cor:transfer53','thm:path52','thm:approx52','thm:common52','tab:screen53']
    missing=[x for x in required if '\\newlabel{'+x+'}' not in aux]
    record=dict(status='PASS',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),pages=pages,
                main_nonreference_pages=nonrefs,abstract_words=words,equation_free_introduction=equation_free,
                missing_required_labels=missing,submission_category='Regular manuscript' if nonrefs<=30 else 'Lengthy manuscript',
                **counts,pdf_sha256={n:hashlib.sha256((OUT/(n+'.pdf')).read_bytes()).hexdigest() for n in pages})
    record['source_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(R.rglob('*')) if p.is_file() and p.suffix in ('.tex','.py') and 'predecessor' not in p.parts}
    if any(counts.values()) or missing or not equation_free or words>200 or nonrefs>30 or pages['electronic_companion']>pages['main']:record['status']='FAIL'
    (R/'BUILD_VALIDATION.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if k!='source_sha256'},indent=2))
    if record['status']!='PASS':raise RuntimeError('R53 layout audit failed')
    for name in ('main','electronic_companion'):
        shutil.copyfile(OUT/(name+'.pdf'),ROOT/(name+'.pdf'))
        shutil.copyfile(OUT/(name+'.pdf'),R/(name+'.pdf'))
    shutil.copyfile(OUT/'RESPONSE_TO_REFEREES.pdf',R/'RESPONSE_TO_REFEREES.pdf')
if __name__=='__main__':build()
