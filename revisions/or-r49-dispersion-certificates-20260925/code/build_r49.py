"""Build and audit R49 OR readers, without touching antecedent source files."""
from pathlib import Path
import re,json,subprocess,hashlib,shutil,sys,datetime,platform
from assemble_r49 import run as assemble,ABSTRACT
from tables_r49 import run as tables
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];B=ROOT/'.build/r49'

def labels(name,target):
    p=B/(name+'.aux')
    if p.exists():target.write_text('\\relax\n'+'\n'.join(s for s in p.read_text().splitlines() if s.startswith('\\newlabel'))+'\n')
def tex(p):
    z=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-recorder',f'-output-directory={B}',str(p)],cwd=ROOT,capture_output=True,text=True)
    (B/(Path(p).stem+'.console.txt')).write_text(z.stdout+z.stderr)
    if z.returncode:raise RuntimeError(z.stdout[-5000:])
def build():
    B.mkdir(parents=True,exist_ok=True);tables();assemble()
    for n,stub in [('main','main'),('electronic_companion','ec'),('COMPUTATIONAL_RECORD','cs')]:labels(n,ROOT/f'r49-{stub}-labels.aux')
    for _ in range(3):
        for n,stub in [('main','main'),('electronic_companion','ec'),('COMPUTATIONAL_RECORD','cs')]:
            p=n+'.tex' if n!='COMPUTATIONAL_RECORD' else str((R/(n+'.tex')).relative_to(ROOT))
            tex(p);labels(n,ROOT/f'r49-{stub}-labels.aux')
    response=R/'RESPONSE_TO_REFEREES.tex'
    if response.exists():
        for _ in range(2):tex(str(response.relative_to(ROOT)))
    for n in ['main','electronic_companion']:shutil.copy2(B/(n+'.pdf'),ROOT/(n+'.pdf'))
    for n in ['COMPUTATIONAL_RECORD','RESPONSE_TO_REFEREES']:
        if (B/(n+'.pdf')).exists():shutil.copy2(B/(n+'.pdf'),R/(n+'.pdf'))
    logs='\n'.join(p.read_text(errors='replace') for p in B.glob('*.log'))
    counts={k:len(re.findall(pat,logs)) for k,pat in dict(undefined_references=r'Reference .* undefined',undefined_citations=r'Citation .* undefined',duplicate_labels=r'Label .* multiply defined',overfull_boxes=r'Overfull \\[hv]box').items()}
    import fitz
    pages={n:len(fitz.open(B/(n+'.pdf'))) for n in ['main','electronic_companion','COMPUTATIONAL_RECORD','RESPONSE_TO_REFEREES'] if (B/(n+'.pdf')).exists()}
    aux=(B/'main.aux').read_text();a=int(re.search(r'\\newlabel\{refs-start\}\{\{[^}]*\}\{(\d+)\}',aux).group(1));b=int(re.search(r'\\newlabel\{refs-end\}\{\{[^}]*\}\{(\d+)\}',aux).group(1));nonrefs=pages['main']-(b-a+1)
    pat=r'\\begin\{(?:theorem|proposition|lemma|corollary)\}(?:\[[^\]]*\])?\s*\\label\{([^}]+)\}'
    old=set()
    for no,name in [(45,'budgeted-compression-20260924'),(46,'box-decomposition-20260925'),(47,'joint-certificates-20260925'),(48,'harmonic-coarsening-20260925')]:
        d=R.parent/f'or-r{no}-{name}'
        for p in (d.rglob('*.tex') if no==45 else d.glob('*.tex')):
            if any(s in str(p.relative_to(d)) for s in ['predecessor/','RESPONSE','generated/']):continue
            old.update(re.findall(pat,p.read_text()))
    allaux=(B/'main.aux').read_text()+(B/'electronic_companion.aux').read_text();now=set(re.findall(r'\\newlabel\{([^}]+)\}',allaux));missing=sorted(old-now)
    new=set(re.findall(pat,(R/'pooling.tex').read_text()+(R/'group_boxes.tex').read_text()))
    inputs={}
    for pp in B.glob('*.fls'):
        for line in pp.read_text().splitlines():
            if not line.startswith('INPUT '):continue
            p=Path(line[6:]);p=p if p.is_absolute() else ROOT/p
            if p.exists() and p.is_relative_to(ROOT) and p.suffix=='.tex':inputs[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    try:commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:commit=None
    result=dict(status='PASS',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_commit=commit,
        baseline='939cce84881a1d1eabf93aa3a2d3f4f4417ce53f',pages=pages,main_nonreference_pages=nonrefs,
        abstract_words=len(ABSTRACT.split()),retained_math_labels=len(old),new_math_labels=sorted(new),missing_math_labels=missing,
        equation_free_introduction='$' not in (R/'introduction.tex').read_text(),**counts,reader_inputs=inputs,
        pdf_sha256={n:hashlib.sha256((B/(n+'.pdf')).read_bytes()).hexdigest() for n in pages},python=sys.version,platform=platform.platform())
    if any(counts.values()) or missing or new-now or nonrefs>40 or pages['electronic_companion']>pages['main'] or len(ABSTRACT.split())>200:result['status']='FAIL'
    (R/'BUILD_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='reader_inputs'},indent=2))
    if result['status']!='PASS':raise RuntimeError('Build audit failed; see BUILD_VALIDATION.json')
if __name__=='__main__':build()
