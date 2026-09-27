"""Check every scientific-parent blob; altered root readers require exact copies."""
from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
PARENT='7bdfda8f84b84f491e80b50a86089c37ea4c7f3a'
PROTOCOL_COMMIT='a2cbabde34abc94aa158367cd38ea6afcd789819'
REPLACED={'main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md'}
def blob(path):
    data=path.read_bytes();return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def run():
    listing=subprocess.check_output(['git','ls-tree','-r',PARENT],cwd=ROOT,text=True)
    entries=[];failures=[];unchanged=0;archived=0
    for line in listing.splitlines():
        metadata,path=line.split('\t',1);mode,kind,sha=metadata.split()
        if kind!='blob':continue
        now=ROOT/path
        if now.is_file() and blob(now)==sha:
            unchanged+=1;entries.append(dict(path=path,blob_sha=sha,status='unchanged'))
        elif path in REPLACED:
            saved=R/'predecessor'/path
            if saved.is_file() and blob(saved)==sha:
                archived+=1;entries.append(dict(path=path,blob_sha=sha,status='exact predecessor',saved=str(saved.relative_to(ROOT))))
            else:failures.append(path)
        else:failures.append(path)
    protocol=R/'PROTOCOL.json';rel=str(protocol.relative_to(ROOT))
    expected=subprocess.check_output(['git','rev-parse',f'{PROTOCOL_COMMIT}:{rel}'],cwd=ROOT,text=True).strip()
    if blob(protocol)!=expected:failures.append('immutable protocol changed')
    result=dict(status='PASS' if not failures else 'FAIL',parent=PARENT,parent_blobs=len(entries)+len(failures),
                unchanged=unchanged,exact_predecessor_copies=archived,failures=failures,
                protocol_commit=PROTOCOL_COMMIT,protocol_blob=expected,entries=entries)
    (R/'PRESERVATION_MANIFEST.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='entries'},indent=2))
    if failures:raise RuntimeError('Inherited blob preservation failed')
if __name__=='__main__':run()
