"""Verify every inherited Git blob; save exact replaced readers from the base."""
from pathlib import Path
import subprocess,hashlib,json
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
BASE='df1e192fd0846315ff0938e57d797efcd04109aa'
ALLOWED=['main.tex','electronic_companion.tex','main.pdf','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md']
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def prepare():
    for name in ALLOWED:
        p=R/'predecessor'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(git('show',BASE+':'+name))
def run():
    entries=[];bad=[];changed=[];kept=0
    for row in git('ls-tree','-rz',BASE).split(b'\0'):
        if not row:continue
        info,name=row.split(b'\t',1);mode,typ,sha=info.decode().split();path=name.decode()
        if typ!='blob':continue
        p=ROOT/path
        if not p.exists():bad.append([path,'missing']);continue
        data=p.read_bytes();actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if path in ALLOWED:
            old=(R/'predecessor'/path).read_bytes();oldsha=hashlib.sha1(b'blob '+str(len(old)).encode()+b'\0'+old).hexdigest()
            if oldsha!=sha:bad.append([path,'incorrect preserved predecessor'])
            changed.append(path)
        elif actual!=sha:bad.append([path,'changed inherited blob'])
        else:kept+=1
        entries.append(dict(path=path,base_blob=sha,classification='preserved predecessor and new reader' if path in ALLOWED else 'byte-identical'))
    out=dict(status='PASS' if not bad else 'FAIL',base=BASE,inherited_files=len(entries),byte_identical=kept,authorized_reader_replacements=changed,errors=bad,files=entries)
    (R/'PRESERVATION_MANIFEST.json').write_text(json.dumps(out,indent=2)+'\n')
    print({k:v for k,v in out.items() if k!='files'})
    if bad:raise ValueError('Inherited content modified')
if __name__=='__main__':run()
