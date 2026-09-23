"""Build both R34 review documents, bind PDFs to source, and audit preservation."""
from pathlib import Path
import hashlib,json,os,re,subprocess,platform
ROOT=Path.cwd();R=ROOT/'revisions/or-r34-global-randomized-frontier-20260923'
B=ROOT/'.build/ndu-r34';B.mkdir(parents=True,exist_ok=True)
def run(args,log=None):
 p=subprocess.run(args,text=True,encoding='utf-8',errors='replace',stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 if log:Path(log).write_text(p.stdout)
 if p.returncode:
  print(p.stdout[-16000:]);raise RuntimeError(f'command failed: {args}')
 return p.stdout
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
if os.environ.get('NDU_LOCAL_VALIDATION')=='1':source='local-uncommitted; content hashes recorded'
else:source=run(['git','rev-parse','HEAD']).strip()
manifest=json.loads((R/'PRESERVATION_MANIFEST.json').read_text())
for f in manifest['unchanged_inherited_reader_files']:
 assert sha(ROOT/f['path'])==f['sha256'],f['path']
for name,digest in manifest['archived_wrappers'].items():
 assert sha(R/'predecessor'/name)==digest,name
main=(ROOT/'main.tex').read_text();ec=(ROOT/'electronic_companion.tex').read_text()
a=main.split(r'\textbf{Abstract.}',1)[1].split(r'\par\vspace',1)[0]
assert len(a.split())<=200 and '$' not in a
intro=(R/'introduction.tex').read_text()
assert '$' not in intro and r'\[' not in intro and r'\begin{equation}' not in intro
assert 'Revision R34' in main and 'Revision R34' in ec
assert main.count('global_frontier.tex')==1
assert main.index('evidence_table.tex',main.index('references.tex'))>main.index('references.tex')
for f in ('r34-main-labels.aux','r34-ec-labels.aux'):(ROOT/f).write_text('')
for i in range(1,5):
 for doc,labels in [('main','r34-main-labels.aux'),('electronic_companion','r34-ec-labels.aux')]:
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
assert records['main']['pages']<=40,records['main']
assert records['electronic_companion']['pages']<=records['main']['pages']
text=(B/'main.txt').read_text()
for phrase in ('Piecewise-Quadratic','Global Randomized Memory Frontier','Pathwise randomization','R34'):
 assert phrase.lower() in text.lower(),phrase
verification=json.loads((R/'verification.json').read_text());assert verification['status']=='PASS'
inherited=json.loads((R/'inherited_verification.json').read_text());assert inherited['status']=='PASS'
sources={'main.tex':sha(ROOT/'main.tex'),'electronic_companion.tex':sha(ROOT/'electronic_companion.tex')}
for name in ('global_frontier.tex','introduction.tex','evidence.tex','evidence_table.tex','companion_addendum.tex','randomized_frontier.py','verify.py','reproduce_inherited.py','build_validate.py'):
 sources[str((R/name).relative_to(ROOT))]=sha(R/name)
record={'status':'PASS','scientific_source_commit':source,'workflow_trigger_commit':os.environ.get('GITHUB_SHA'),
 'base_commit':manifest['base_commit'],'review_commit':'a017f474619e86be533547acac87a3c8354f64cf',
 'abstract_words':len(a.split()),'python':platform.python_version(),'runner':platform.platform(),
 'documents':records,'new_exact_verification':{key:verification[key] for key in ('status','cases','counts','source_sha256')},
 'inherited_exact_verification':inherited,'source_sha256':sources,
 'preserved_reader_files':len(manifest['unchanged_inherited_reader_files']),
 'preserved_predecessor_wrappers':len(manifest['archived_wrappers']),
 'submission_category':'Lengthy Manuscript; no journal submission performed',
 'format':{'font_points':11,'line_spacing':1.5,'margins_inches':1,'tables_after_references':True,
           'main_all_pages_at_most_40':True,'companion_not_longer_than_main':True},
 'note':'A clean build and exact tests do not certify referee acceptance, empirical calibration, or exhaustive literature priority.'}
(R/'BUILD_VALIDATION.json').write_text(json.dumps(record,indent=2)+'\n')
for doc in records:
 run(['pdftoppm','-f','1','-singlefile','-scale-to','1200','-png',str(B/f'{doc}.pdf'),str(B/f'{doc}-first')])
print(json.dumps({key:record[key] for key in ('status','scientific_source_commit','abstract_words','documents','preserved_reader_files')},indent=2))
