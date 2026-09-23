"""Build the R36 article, companion, and response and bind readers to exact sources."""
from pathlib import Path
import hashlib,json,os,re,subprocess,platform
ROOT=Path.cwd();R=ROOT/'revisions/or-r36-linear-frontier-20260924'
B=ROOT/'.build/ndu-r36';B.mkdir(parents=True,exist_ok=True)
def run(args,log=None):
 p=subprocess.run(args,text=True,encoding='utf-8',errors='replace',stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 if log:Path(log).write_text(p.stdout)
 if p.returncode:
  print(p.stdout[-18000:]);raise RuntimeError(f'command failed: {args}')
 return p.stdout

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
local=os.environ.get('NDU_LOCAL_VALIDATION')=='1'
source='local-uncommitted; content hashes recorded' if local else run(['git','rev-parse','HEAD']).strip()
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
assert 'Revision R36' in main and 'Revision R36' in ec
assert main.count('frontier_acceleration.tex')==1
assert main.count('linear_search.tex')==1
assert main.count('global_frontier.tex')==1
assert main.index('evidence_table.tex',main.index('references.tex'))>main.index('references.tex')
# Keep the exact inherited input modules in the reader. New introduction/references are additive copies.
old=(R/'predecessor/main.tex').read_text()
for p in re.findall(r'\\input\{([^}]+)\}',old):
 if p.endswith(('/introduction.tex','/references.tex')):continue
 assert r'\input{'+p+'}' in main,p
for p in re.findall(r'\\input\{([^}]+)\}',(R/'predecessor/electronic_companion.tex').read_text()):
 assert r'\input{'+p+'}' in ec,p
# Prove every old bibliography entry is kept in the expanded list.
oldrefs=(ROOT/'revisions/or-r31-tightness-minimal-machine-20260923/references.tex').read_text()
newrefs=(R/'references.tex').read_text()
for match in re.finditer(r'\\bibitem.*?(?=\\bibitem|\\end\{thebibliography\})',oldrefs,re.S):
 assert match.group().strip() in newrefs
run(['python',str(R/'response_reader.py')])
for f in ('r36-main-labels.aux','r36-ec-labels.aux'):(ROOT/f).write_text('')
for i in range(1,5):
 for doc,labels in [('main','r36-main-labels.aux'),('electronic_companion','r36-ec-labels.aux')]:
  run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error',f'-output-directory={B}',doc+'.tex'],B/f'{doc}-pass-{i}.stdout')
  lines=(B/f'{doc}.aux').read_text().splitlines()
  (ROOT/labels).write_text('\n'.join(x for x in lines if x.startswith(r'\newlabel'))+'\n')
for i in range(2):
 run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error',f'-output-directory={B}',str(R/'RESPONSE_TO_REFEREES.tex')],B/f'response-pass-{i}.stdout')
records={}
for doc in ('main','electronic_companion','RESPONSE_TO_REFEREES'):
 log=(B/f'{doc}.log').read_text(errors='replace')
 bad=re.findall(r'[^\n]*(?:undefined references|undefined citations|Citation .* undefined|Reference .* undefined|multiply defined|Overfull \\hbox|Overfull \\vbox)[^\n]*',log)
 if bad:print('\n'.join(bad));raise RuntimeError('Unresolved citation, reference, or layout warning')
 pdf=B/f'{doc}.pdf';out=run(['pdfinfo',str(pdf)])
 pages=int(re.search(r'^Pages:\s+(\d+)',out,re.M).group(1))
 target=(R if doc=='RESPONSE_TO_REFEREES' else ROOT)/f'{doc}.pdf'
 target.write_bytes(pdf.read_bytes())
 run(['pdftotext',str(pdf),str(B/f'{doc}.txt')])
 records[doc]={'pages':pages,'sha256':sha(pdf),'undefined_references_or_citations':0,'overfull_boxes':0}
# Explicit page breaks delimit the bibliography; subtract only its entire page range.
aux=(B/'main.aux').read_text()
def page(label):
 m=re.search(r'\\newlabel\{'+label+r'\}\{\{[^}]*\}\{(\d+)\}',aux)
 assert m,label
 return int(m.group(1))
refs_first,refs_last=page('r36-refs-start'),page('r36-refs-end')
reference_pages=refs_last-refs_first+1
nonreference_pages=records['main']['pages']-reference_pages
assert reference_pages>0
assert nonreference_pages<=40,{'documents':records,'nonreference_pages':nonreference_pages}
assert records['electronic_companion']['pages']<=nonreference_pages
text=(B/'main.txt').read_text()
for phrase in ('Piecewise-Quadratic','Global Randomized Memory Frontier','Pathwise randomization','Monge Structure','linear-work contractual frontiers','R36'):
 assert phrase.lower() in text.lower(),phrase
verification=json.loads((R/'verification.json').read_text());assert verification['status']=='PASS'
benchmark=json.loads((R/'benchmark.json').read_text());assert benchmark['status']=='PASS'
inherited=json.loads((R/'inherited_verification.json').read_text());assert inherited['status']=='PASS'
sources={'main.tex':sha(ROOT/'main.tex'),'electronic_companion.tex':sha(ROOT/'electronic_companion.tex')}
for f in sorted(R.iterdir()):
 if f.suffix in ('.tex','.py','.md') or f.name in ('PRESERVATION_MANIFEST.json','verification.json','benchmark.json','inherited_verification.json','scaling.csv'):
  sources[str(f.relative_to(ROOT))]=sha(f)
tree_audit={'status':'NOT_APPLICABLE_LOCAL_NON_GIT','note':'Remote build verifies all base paths.'}
if not local:
 # Check the complete base tree, not only files present in the downloaded reader snapshot.
 allowed={'main.tex','electronic_companion.tex','README.md','NDU_OR_submission_checklist.md','main.pdf','electronic_companion.pdf'}
 changes=run(['git','diff','--name-status',manifest['base_commit'],'HEAD']).splitlines()
 for line in changes:
  status,path=line.split('\t',1)
  assert status!='D',line
  assert path in allowed or path.startswith(str(R.relative_to(ROOT))+'/') or path.startswith('.r36-transport/') or path in ('.github/workflows/ndu-or-r36-publication.yml','r36-main-labels.aux','r36-ec-labels.aux'),line
 # The working tree also matters after results are generated.
 for line in run(['git','diff','--name-status',manifest['base_commit']]).splitlines():
  status,path=line.split('\t',1)
  assert status!='D',line
  assert path in allowed or path.startswith(str(R.relative_to(ROOT))+'/') or path.startswith('.r36-transport/') or path in ('.github/workflows/ndu-or-r36-publication.yml','r36-main-labels.aux','r36-ec-labels.aux'),line
 tree_audit={'status':'PASS','base_commit':manifest['base_commit'],'deleted_base_files':0,'unauthorized_changed_base_files':0,'all_base_paths_checked':True}
record={'status':'PASS','scientific_source_commit':source,'workflow_trigger_commit':os.environ.get('GITHUB_SHA'),
 'base_commit':manifest['base_commit'],'review_commit':'a017f474619e86be533547acac87a3c8354f64cf',
 'abstract_words':len(a.split()),'python':platform.python_version(),'runner':platform.platform(),
 'documents':records,'reference_pages':{'first':refs_first,'last':refs_last,'count':reference_pages},
 'main_pages_excluding_references':nonreference_pages,'page_count_rule':'Whole bibliography pages isolated by explicit page breaks; all title, text, and table pages counted.',
 'new_exact_verification':{key:verification[key] for key in ('status','cases','counts','source_sha256')},
 'benchmark_status':benchmark['status'],'inherited_exact_verification':inherited,'source_sha256':sources,
 'preserved_reader_files':len(manifest['unchanged_inherited_reader_files']),
 'preserved_predecessor_wrappers':len(manifest['archived_wrappers']),'whole_remote_tree_preservation':tree_audit,
 'submission_category':'Lengthy Manuscript; no journal submission performed',
 'format':{'font_points':11,'line_spacing':1.5,'margins_inches':1,'tables_after_references':True,
 'main_excluding_references_at_most_40':True,'companion_not_longer_than_main':True},
 'note':'A clean build and exact tests do not determine referee acceptance, empirical calibration, or exhaustive literature priority.'}
(R/'BUILD_VALIDATION.json').write_text(json.dumps(record,indent=2)+'\n')
for doc in records:
 run(['pdftoppm','-f','1','-singlefile','-scale-to','1200','-png',str(B/f'{doc}.pdf'),str(B/f'{doc}-first')])
print(json.dumps({key:record[key] for key in ('status','scientific_source_commit','abstract_words','documents','main_pages_excluding_references','preserved_reader_files')},indent=2))
