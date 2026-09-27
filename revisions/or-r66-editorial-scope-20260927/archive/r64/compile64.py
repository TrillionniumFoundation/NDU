from pathlib import Path
import json,re,shutil,subprocess
R=Path(__file__).resolve().parent;B=R/'.build/r64';B.mkdir(parents=True,exist_ok=True)
for name in ('main','electronic_companion'):
 if (B/(name+'.aux')).exists():
  (B/(name+'_refs.aux')).write_text('\n'.join(x for x in (B/(name+'.aux')).read_text().splitlines() if x.startswith('\\newlabel'))+'\n')
for passno in range(3):
 for name in ('main','electronic_companion','RESPONSE_TO_REFEREES'):
  if not (R/(name+'.tex')).exists():continue
  run=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error','-output-directory=.build/r64',name+'.tex'],cwd=R,capture_output=True,text=True,errors='replace')
  (B/(name+'.stdout')).write_text(run.stdout+run.stderr)
  if run.returncode:raise RuntimeError(name+'\n'+run.stdout[-3000:])
  (B/(name+'_refs.aux')).write_text('\n'.join(x for x in (B/(name+'.aux')).read_text().splitlines() if x.startswith('\\newlabel'))+'\n')
for name in ('main','electronic_companion','RESPONSE_TO_REFEREES'):
 if (B/(name+'.pdf')).exists():shutil.copy2(B/(name+'.pdf'),R/(name+'.pdf'))
import fitz
report={}
for name in ('main','electronic_companion','RESPONSE_TO_REFEREES'):
 if not (R/(name+'.pdf')).exists():continue
 d=fitz.open(R/(name+'.pdf'));log=(B/(name+'.log')).read_text(errors='replace');aux=(B/(name+'.aux')).read_text()
 errors=[x for x in log.splitlines() if 'undefined' in x.lower() or 'multiply defined' in x.lower()]
 report[name]={'pages':len(d),'reference_warnings':errors,'overfull':[x for x in log.splitlines() if 'Overfull' in x]}
 if name=='main':
  start=int(re.search(r'\\newlabel\{refs-start\}\{\{[^}]*\}\{(\d+)\}',aux).group(1));end=int(re.search(r'\\newlabel\{refs-end\}\{\{[^}]*\}\{(\d+)\}',aux).group(1));report[name]['excluding_references']=len(d)-(end-start+1)
 assert not errors,(name,errors)
 assert not report[name]['overfull'],(name,report[name]['overfull'])
assert report['main']['excluding_references']<=30,report
assert report['electronic_companion']['pages']<=report['main']['pages'],report
abstract=(R/'main.tex').read_text().split(r'\textbf{Abstract.} ',1)[1].split(r'\par\vspace',1)[0]
words=len(abstract.split());assert words<=200,words
report['main']['abstract_words']=words
(R/'results/r64/BUILD64.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
