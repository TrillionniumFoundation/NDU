#!/usr/bin/env python3
"""Preserve exactly the reviewed base, independent of transport or build commits."""
from pathlib import Path
import subprocess,hashlib,json,argparse
p=argparse.ArgumentParser();p.add_argument('--base',default='5b1a62679f890006d8f6a234160fa9a02dcdbc5a');a=p.parse_args()
root=Path(__file__).resolve().parents[2];here=Path(__file__).resolve().parent
subprocess.run(['git','merge-base','--is-ancestor',a.base,'HEAD'],cwd=root,check=True)
allowed={'main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','historical_supplement.pdf','README.md','NDU_OR_submission_checklist.md'}
files=subprocess.check_output(['git','ls-tree','-r','--name-only',a.base],cwd=root,text=True).splitlines();hashes={}
pred=here/'predecessor';pred.mkdir(exist_ok=True)
for name in files:
    data=subprocess.check_output(['git','show',a.base+':'+name],cwd=root)
    if name not in allowed:hashes[name]=hashlib.sha256(data).hexdigest()
    if name in allowed:(pred/name).write_bytes(data)
(here/'BASELINE_SHA256.json').write_text(json.dumps(hashes,sort_keys=True,indent=2)+'\n')
(pred/'PDF_SHA256.json').write_text(json.dumps({n:hashlib.sha256((pred/n).read_bytes()).hexdigest() for n in allowed if n.endswith('.pdf')},sort_keys=True,indent=2)+'\n')
print('Preserved',len(hashes),'reviewed-base files and',len(allowed),'root documents')
