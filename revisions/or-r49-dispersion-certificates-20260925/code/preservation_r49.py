"""Audit every inherited Git blob; authorize only archived root reader replacements."""
from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];BASE='939cce84881a1d1eabf93aa3a2d3f4f4417ce53f'
ALLOWED={'main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md'}
def blob(p):
    b=p.read_bytes();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def run():
    try:tree=subprocess.check_output(['git','ls-tree','-r',BASE],cwd=ROOT,text=True,stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:tree=Path('/mnt/data/ndu-parent-transport/PARENT_TREE.txt').read_text()
    changed=[];errors=[];count=0;preserved=[]
    for line in tree.splitlines():
        meta,name=line.split('\t',1);mode,kind,sha=meta.split();assert kind=='blob';count+=1;p=ROOT/name
        if not p.exists():errors.append([name,'missing']);continue
        now=blob(p)
        if now==sha:continue
        if name not in ALLOWED:errors.append([name,'unapproved mutation',sha,now]);continue
        copy=R/'predecessor'/name
        if not copy.exists() or blob(copy)!=sha:errors.append([name,'predecessor copy missing or not exact']);continue
        changed.append(dict(path=name,old_blob=sha,new_blob=now,archived_as=str(copy.relative_to(ROOT))))
    mapping=json.loads((R/'CONTENT_MAP.json').read_text())
    for name,sha in mapping['relocated_input_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=sha:errors.append([name,'relocation digest mismatch'])
    out=dict(status='PASS' if not errors else 'FAIL',baseline=BASE,inherited_blob_count=count,
        unchanged_blob_count=count-len(changed)-len(errors),archived_root_replacements=changed,errors=errors,
        scope='Current isolated R49 branch only; no deletion or ancestor-source alteration is allowed')
    (R/'PRESERVATION_MANIFEST.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
    if errors:raise RuntimeError('Inherited content preservation failed')
if __name__=='__main__':run()
