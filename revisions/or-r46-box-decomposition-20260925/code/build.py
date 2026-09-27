"""Build anonymous Operations Research readers and record checked provenance."""
from pathlib import Path
import re,subprocess,hashlib,json,sys,shutil,datetime,platform
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];B=ROOT/'.build/r46'
sys.path.insert(0,str(R/'code'))
from assemble import ABSTRACT,run as assemble
from tables import run as tables
BASE='260a5224c55e0326d9da7f0c813b4a3fcab7671f'
BRANCH='revision/ndu-operations-research-r46-box-decomposition-20260925'
def labels(src,dst):
    dst.write_text('\\relax\n'+'\n'.join(x for x in src.read_text().splitlines() if x.startswith('\\newlabel'))+'\n')
def tex(name):
    p=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-recorder',f'-output-directory={B}',name],cwd=ROOT,capture_output=True,text=True)
    (B/(Path(name).stem+'.console.txt')).write_text(p.stdout+p.stderr)
    if p.returncode:raise RuntimeError(p.stdout[-3000:])
def build():
    tables();assemble();B.mkdir(parents=True,exist_ok=True)
    # Remove stale auxiliary bibliography data imported by old unfiltered files.
    for x in ['main.aux','electronic_companion.aux']:
        f=B/x
        if f.exists():labels(f,ROOT/('r46-main-labels.aux' if x=='main.aux' else 'r46-ec-labels.aux'))
    for _ in range(3):
        tex('main.tex');labels(B/'main.aux',ROOT/'r46-main-labels.aux')
        tex('electronic_companion.tex');labels(B/'electronic_companion.aux',ROOT/'r46-ec-labels.aux')
    response=str((R/'RESPONSE_TO_REFEREES.tex').relative_to(ROOT))
    if (R/'RESPONSE_TO_REFEREES.tex').exists():
        for _ in range(2):tex(response)
        shutil.copy2(B/'RESPONSE_TO_REFEREES.pdf',R/'RESPONSE_TO_REFEREES.pdf')
    for stem in ['main','electronic_companion']:shutil.copy2(B/(stem+'.pdf'),ROOT/(stem+'.pdf'))
    logs='\n'.join((B/(n+'.log')).read_text() for n in ['main','electronic_companion'])
    errors={z:len(re.findall(p,logs)) for z,p in {'undefined_references':r'Reference .* undefined','undefined_citations':r'Citation .* undefined','duplicate_labels':r'Label .* multiply defined','duplicate_citations':r'Citation .* multiply defined','overfull_boxes':r'Overfull \\[hv]box'}.items()}
    if any(errors.values()):raise RuntimeError(errors)
    import fitz
    pages={n:len(fitz.open(ROOT/(n+'.pdf'))) for n in ['main','electronic_companion']}
    aux=(B/'main.aux').read_text();start=int(re.search(r'\\newlabel\{refs-start\}\{\{[^}]*\}\{(\d+)\}',aux).group(1));end=int(re.search(r'\\newlabel\{refs-end\}\{\{[^}]*\}\{(\d+)\}',aux).group(1));nonrefs=pages['main']-(end-start+1)
    if nonrefs>40 or pages['electronic_companion']>pages['main']:raise RuntimeError(('OR page constraint',pages,nonrefs))
    # All mathematical statement labels of R45 remain in the current readers.
    oldlabels=[]
    for f in (R.parent/'or-r45-budgeted-compression-20260924').rglob('*.tex'):
        if any(x in str(f.relative_to(R.parent/'or-r45-budgeted-compression-20260924')) for x in ['predecessor/','RESPONSE','generated/']):continue
        oldlabels+=re.findall(r'\\begin\{(?:theorem|proposition|lemma|corollary)\}(?:\[[^\]]*\])?\s*\\label\{([^}]+)\}',f.read_text())
    labelsnow=set(re.findall(r'\\newlabel\{([^}]+)\}',(B/'main.aux').read_text()+(B/'electronic_companion.aux').read_text()))
    missing=sorted(set(oldlabels)-labelsnow)
    if missing:raise RuntimeError(('Lost mathematical labels',missing))
    inputs={}
    for name in ['main','electronic_companion','RESPONSE_TO_REFEREES']:
        ff=B/(name+'.fls')
        if not ff.exists():continue
        for line in ff.read_text().splitlines():
            if not line.startswith('INPUT '):continue
            p=Path(line[6:]);p=p if p.is_absolute() else ROOT/p
            if p.exists() and p.is_relative_to(ROOT) and p.suffix=='.tex':inputs[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    git=lambda *args:subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
    try:source=git('rev-parse','HEAD');branch=git('branch','--show-current')
    except subprocess.CalledProcessError:source=None;branch='local-working-container'
    audit=dict(status='PASS',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),base_review_commit=BASE,branch=branch,source_commit=source,main_pages=pages['main'],main_nonreference_pages=nonrefs,companion_pages=pages['electronic_companion'],abstract_words=len(ABSTRACT.split()),mathematical_labels_retained=len(set(oldlabels)),missing_mathematical_labels=missing,**errors,python=sys.version,platform=platform.platform(),reader_input_sha256=inputs,pdf_sha256={n:hashlib.sha256((ROOT/(n+'.pdf')).read_bytes()).hexdigest() for n in ['main','electronic_companion']})
    (R/'BUILD_VALIDATION.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps({k:v for k,v in audit.items() if k not in ['reader_input_sha256']},indent=2))
if __name__=='__main__':build()
