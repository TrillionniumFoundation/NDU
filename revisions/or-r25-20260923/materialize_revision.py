"""Install the reviewed manuscript templates; never edit earlier revision files."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parent;B=R.parent.parent
pre=json.loads((R/'PREDECESSOR_SHA256.json').read_text())
for name,h in pre.items():
 p=R/'predecessor'/name
 if not p.exists():
  assert hashlib.sha256((B/name).read_bytes()).hexdigest()==h,name
  p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(B/name,p)
 assert hashlib.sha256(p.read_bytes()).hexdigest()==h,name
for p in (R/'manuscript').iterdir():
 assert p.name in {'main.tex','electronic_companion.tex','main.bib','README.md','NDU_OR_submission_checklist.md'}
 shutil.copyfile(p,B/p.name)
