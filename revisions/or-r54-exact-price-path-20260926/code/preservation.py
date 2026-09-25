"""Verify every inherited Git blob and the two immutable R54 protocols."""
from pathlib import Path
import hashlib,json,os,subprocess
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
PARENT='fcd7b7ab1719f00e547cd29e94cbb421fab59b0a'
REPLACED={'main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md'}
PROTOCOLS={'PROTOCOL.json':'310f7d42ad45ff529f40c4cd0c3ac1c1b12cfe14','PROTOCOL_HARDNESS_ADDENDUM.json':'97f4fd9b356cfbaadddc96a135952d10c9ef6f6b'}
def blob(path):
    data=os.readlink(path).encode() if path.is_symlink() else path.read_bytes()
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def run():
    if not (ROOT/'.git').exists():raise RuntimeError('A full Git checkout is required for the inherited-tree audit')
    raw=subprocess.check_output(['git','ls-tree','-r','-z',PARENT],cwd=ROOT)
    entries=[];errors=[];unchanged=archived=0
    for line in raw.split(b'\0'):
        if not line:continue
        meta,path=line.decode().split('\t',1);mode,kind,sha=meta.split()
        if kind!='blob':continue
        current=ROOT/path
        if (current.is_file() or current.is_symlink()) and blob(current)==sha:
            unchanged+=1;entries.append(dict(path=path,sha=sha,status='unchanged'))
        elif path in REPLACED and (R/'predecessor'/path).is_file() and blob(R/'predecessor'/path)==sha:
            archived+=1;entries.append(dict(path=path,sha=sha,status='exact predecessor',saved=str((R/'predecessor'/path).relative_to(ROOT))))
        else:errors.append(path)
    protocols={}
    for name,commit in PROTOCOLS.items():
        path=R/name;rel=str(path.relative_to(ROOT));expected=subprocess.check_output(['git','rev-parse',commit+':'+rel],cwd=ROOT,text=True).strip()
        actual=blob(path);protocols[name]=dict(commit=commit,expected_blob=expected,actual_blob=actual)
        if expected!=actual:errors.append('Changed immutable protocol: '+name)
    record=dict(status='PASS' if not errors else 'FAIL',review_parent=PARENT,parent_blobs=len(entries)+len([e for e in errors if not e.startswith('Changed')]),unchanged=unchanged,exact_predecessor_copies=archived,failures=errors,protocols=protocols,entries=entries)
    (R/'PRESERVATION_MANIFEST.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if k!='entries'},indent=2))
    if errors:raise RuntimeError('Inherited content preservation failed')
    return record
if __name__=='__main__':run()
