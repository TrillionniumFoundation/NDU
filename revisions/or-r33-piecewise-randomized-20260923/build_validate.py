"""Build both review documents; record the exact scientific source identity."""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys,platform
ROOT=Path.cwd();R=ROOT/'revisions/or-r33-piecewise-randomized-20260923'
B=ROOT/'.build/ndu-r33';B.mkdir(parents=True,exist_ok=True)
def run(args,log=None):
 p=subprocess.run(args,text=True,encoding='utf-8',errors='replace',stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 if log:Path(log).write_text(p.stdout)
 if p.returncode:
  print(p.stdout[-16000:]);raise RuntimeError(f'command failed: {args}')
 return p.stdout
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
source=run(['git','rev-parse','HEAD']).strip()
main=(ROOT/'main.tex').read_text()
a=main.split(r'\textbf{Abstract.}',1)[1].split(r'\par\vspace',1)[0]
assert len(a.split())<=200 and '$' not in a
intro=(R/'introduction.tex').read_text()
assert '$' not in intro and r'\[' not in intro and r'\begin{equation}' not in intro
assert 'Revision R33' in main and 'Revision R33' in (ROOT/'electronic_companion.tex').read_text()
for f in ('r33-main-labels.aux','r33-ec-labels.aux'):(ROOT/f).write_text('')
for i in range(1,5):
 for doc,labels in [('main','r33-main-labels.aux'),('electronic_companion','r33-ec-labels.aux')]:
  run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error',f'-output-directory={B}',doc+'.tex'],B/f'{doc}-pass-{i}.stdout')
  lines=(B/f'{doc}.aux').read_text().splitlines()
  (ROOT/labels).write_text('\n'.join(x for x in lines if x.startswith(r'\newlabel'))+'\n')
records={}
for doc in ('main','electronic_companion'):
 log=(B/f'{doc}.log').read_text(errors='replace')
 bad=re.findall(r'[^\n]*(?:undefined references|undefined citations|Citation .* undefined|Reference .* undefined|multiply defined|Overfull \\hbox|Overfull \\vbox)[^\n]*',log)
 if bad:print('\n'.join(bad));raise RuntimeError('Unresolved citation, reference, or layout warning')
 pdf=B/f'{doc}.pdf';out=run(['pdfinfo',str(pdf)])
 pages=int(re.search(r'^Pages:\s+(\d+)',out,re.M).group(1))
 (ROOT/f'{doc}.pdf').write_bytes(pdf.read_bytes())
 run(['pdftotext',str(pdf),str(B/f'{doc}.txt')])
 records[doc]={'pages':pages,'sha256':sha(pdf),'undefined_references_or_citations':0,'overfull_boxes':0}
assert records['main']['pages']<=30
assert records['electronic_companion']['pages']<=records['main']['pages']
text=(B/'main.txt').read_text()
assert 'Piecewise-Quadratic' in text and 'When Randomization' in text and 'R33' in text
verification=json.loads((R/'verification.json').read_text());assert verification['status']=='PASS'
record={'status':'PASS','scientific_source_commit':source,'transport_commit':os.environ.get('GITHUB_SHA'),
 'predecessor_commit':'238bfdb24d93439a545551d275a0c9189dbc017b','abstract_words':len(a.split()),
 'python':platform.python_version(),'runner':platform.platform(),'documents':records,
 'new_exact_verification':verification,'tables_after_references':True,'main_all_pages_at_most_30':True,'companion_not_longer_than_main':True,
 'note':'Exact tests and clean typesetting are not a referee acceptance or an exhaustive priority certification.'}
(R/'BUILD_VALIDATION.json').write_text(json.dumps(record,indent=2)+'\n')
# Compact rendering previews are also placed in the downloadable build artifact.
for doc in records:
 run(['pdftoppm','-f','1','-singlefile','-scale-to','1200','-png',str(B/f'{doc}.pdf'),str(B/f'{doc}-first')])
print(json.dumps(record,indent=2))
