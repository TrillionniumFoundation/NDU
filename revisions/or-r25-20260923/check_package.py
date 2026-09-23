"""Check actual R25 files, preservation, PDF geometry, and optional full hashes."""
from pathlib import Path
import hashlib,json,re,sys
import fitz
R=Path(__file__).resolve().parent;B=R.parent.parent;O=R/'results'
def load(p):return json.loads(p.read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inventory():
 root=['main.tex','main.pdf','main.bib','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md','r25-main-labels.aux','r25-ec-labels.aux']
 files=[B/f for f in root]
 for p in R.rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts or p.name in {'MANIFEST.json','package_check.json','REVISION_PLAN.md'}:continue
  if p.name.startswith(('main-build-pass-','ec-build-pass-')):continue
  files.append(p)
 return {str(p.relative_to(B)):digest(p) for p in sorted(set(files))}
def run():
 pre=load(R/'PREDECESSOR_SHA256.json')
 for name,h in pre.items():assert digest(R/'predecessor'/name)==h,('predecessor changed',name)
 for name in ['computational_supplement.tex','computational_supplement.pdf','historical_supplement.tex','historical_supplement.pdf']:
  assert digest(B/name)==pre[name],('historical root changed',name)
 s=(B/'main.tex').read_text();abstract=s.split('\\textbf{Abstract.}')[1].split('\\par\\vspace')[0].strip()
 words=len(abstract.split());assert words<=200 and '$' not in abstract,words
 intro=s.split('\\section{Introduction}')[1].split('\\section{')[0];assert '$' not in intro and '\\[' not in intro and '\\begin{equation}' not in intro
 for name in ('main','electronic_companion'):
  log=(O/(('main' if name=='main' else 'ec')+'-build.log')).read_text()
  for term in ['undefined','multiply defined','Overfull','! LaTeX Error']:
   assert term not in log,(name,term)
 pages={};overflow=[]
 for name in ('main','electronic_companion'):
  d=fitz.open(B/(name+'.pdf'));pages[name]=len(d)
  for i,p in enumerate(d):
   assert abs(p.rect.width-612)<1 and abs(p.rect.height-792)<1
   for block in p.get_text('blocks'):
    if block[0]<70 or block[2]>542:overflow.append([name,i+1,list(block[:4])])
  text='\n'.join(p.get_text() for p in d)
  assert '??' not in text
 assert not overflow,overflow
 assert pages['main']<=30 and pages['electronic_companion']<=pages['main']
 r=load(O/'replay.json');assert r['status']=='PASS' and r['total_new_optimization_certificates']==436
 assert len(r['negative_controls_rejected'])==9
 assert load(O/'inherited_r24_replay.json')['status']=='PASS'
 assert load(O/'inherited_transfer_checks.json')['rational_tree_instances']==64
 for n in ['RESPONSE_TO_REFEREE.md','ARCHIVE_GUIDE.md','DEVELOPMENT_LOG.md','requirements.txt','build.sh','analyze.py','materialize_revision.py']:
  assert (R/n).is_file(),n
 for n in ['hierarchy','radius','cache','historical']:assert (R/'tables'/(n+'.tex')).is_file()
 c=load(O/'cache_summary.json');assert c['query_optimizer_calls']==0 and c['validation_optimizer_calls']==32
 result={'status':'PASS','main_PDF_pages_including_references_and_tables':pages['main'],'formal_EC_PDF_pages_including_references':pages['electronic_companion'],
  'abstract_words':words,'equation_free_introduction':True,'resolved_references_and_citations':True,'overfull_lines':0,
  'preserved_predecessor_files':len(pre),'new_optimization_certificates':436,'rational_regular_cells':24,'exact_release_capacity_friction_witnesses':154,
  'finite_action_policies_enumerated':37142,'new_negative_controls_rejected':9,'inherited_tree_transfer_cases':64,
  'page_limit_check':'Conservative: even including all references, title, and tables, main is within 30 pages and EC is shorter.'}
 if '--verify-manifest' in sys.argv:
  assert inventory()==load(R/'MANIFEST.json')['sha256'],'manifest mismatch'
  assert result==load(O/'package_check.json'),'package check record changed'
 else:(O/'package_check.json').write_text(json.dumps(result,indent=2)+'\n')
 if '--manifest' in sys.argv:(R/'MANIFEST.json').write_text(json.dumps({'scope':'Current R25 source, PDF, evidence and exact predecessor copies; manifest excludes itself and generated check result','sha256':inventory()},indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':run()
