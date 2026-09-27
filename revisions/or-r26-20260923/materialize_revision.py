"""Materialize only this new revision; preserve the pinned scientific predecessor."""
from pathlib import Path
import hashlib,json,shutil,subprocess
R=Path(__file__).resolve().parent;B=R.parent.parent
meta=json.loads((R/'PREDECESSOR_SHA256.json').read_text())
for name,h in meta['files'].items():
    p=B/name
    if hashlib.sha256(p.read_bytes()).hexdigest()!=h:raise ValueError(('source predecessor mismatch',name))
    dest=R/'predecessor'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
allowed={'main.tex','electronic_companion.tex','main.bib','README.md','NDU_OR_submission_checklist.md'}
for line in (R/'manuscript.patch').read_text().splitlines():
    if line.startswith('+++ b/') and line[6:] not in allowed:raise ValueError('patch outside manuscript scope')
subprocess.run(['git','apply','--check',str(R/'manuscript.patch')],cwd=B,check=True)
subprocess.run(['git','apply',str(R/'manuscript.patch')],cwd=B,check=True)
for name in ('results','tables'):(R/name).mkdir(exist_ok=True)
print('Preserved the exact R25 source/PDFs and materialized the R26 manuscript only.')
