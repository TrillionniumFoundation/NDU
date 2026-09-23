"""Materialize R27 only from the pinned R26 source; preserve every ancestor."""
from pathlib import Path
import hashlib,json,shutil,subprocess
R=Path(__file__).resolve().parent;B=R.parent.parent
BASE='38f99a5b46d8cfe4f1197fc869735d5f798c499a'
EXPECTED='9155cdf370b55bf18765c6acc414b8f6fd5a431cec3de9ae50caca6b17656713'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=B,text=True).splitlines()
files={name:digest(B/name) for name in paths}
assert hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()==EXPECTED,'Source is not the pinned scientific R26 tree'
(R/'INHERITED_SHA256.json').write_text(json.dumps(files,indent=2)+'\n')
names=['main.tex','main.pdf','main.bib','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md','computational_supplement.tex','computational_supplement.pdf','historical_supplement.tex','historical_supplement.pdf','r26-main-labels.aux','r26-ec-labels.aux']
(R/'predecessor').mkdir(exist_ok=True)
for name in names:shutil.copy2(B/name,R/'predecessor'/name)
(R/'PREDECESSOR_SHA256.json').write_text(json.dumps({'scientific_base':BASE,'files':{n:files[n] for n in names}},indent=2)+'\n')
subprocess.run(['git','apply','--check',str(R/'manuscript.patch')],cwd=B,check=True)
subprocess.run(['git','apply',str(R/'manuscript.patch')],cwd=B,check=True)
print('R27 materialized with',len(files),'pinned ancestor files and',len(names),'predecessor copies')
