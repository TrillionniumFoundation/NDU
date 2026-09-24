"""Recover byte-identified scientific inputs without altering historical paths."""
from pathlib import Path, PurePosixPath
import base64, hashlib, json, lzma, subprocess
ROOT=Path(__file__).resolve().parents[2]
R=ROOT/'revisions/or-r42-certified-joint-design-20260924'
BASE='6e48c4858a54317f8189664f5a57fb5cc4ac6e4f'
BRANCH='revision/ndu-operations-research-r42-certified-joint-design-20260924'
DIGEST='eb33cbc7fc367e20be4fc477a2df86d066195867db45e0b6b5d29022f853d1bf'
PARTS=['e342a4552e855d3bd5db6837aee737331fc00e1653878d6319980c7fc149cad8','cb83da276dfb39d86ced225e7659320e5249fde5041fdb7b530c6f1951b8f936','69d58a24ba246269e441797d13aecf8e47b49c865f7dc0ffd58c9cd0933ca9a3','a911e10eef3f1d9b992432eddaec860136dc8b7bd8eca08863c1fa6cf31a15bc','a9a2de8cbf33fd66140f9f8374f0568278d48bb28798158f78347404e1411056']
ALLOWED={'main.tex','electronic_companion.tex','README.md','NDU_OR_submission_checklist.md'}
def sha(b):return hashlib.sha256(b).hexdigest()
def base_bytes(path):
    if (ROOT/'.git').exists():
        return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
    p=R/'predecessor'/path if '/' not in path else ROOT/path
    return p.read_bytes()
def main():
    if (ROOT/'.git').exists():
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
        assert branch==BRANCH,'Refusing another branch'
    chunks=[]
    for i,want in enumerate(PARTS,1):
        p=ROOT/'.r42-transport'/f'part-{i:02d}.b64';b=p.read_bytes()
        assert sha(b)==want,('Transport part mismatch',i,sha(b))
        chunks.append(b.strip())
    packed=base64.b64decode(b''.join(chunks),validate=True)
    assert sha(packed)==DIGEST,'Transport digest mismatch'
    entries=json.loads(lzma.decompress(packed))
    ready={}
    for name,item in entries.items():
        p=PurePosixPath(name)
        assert not p.is_absolute() and '..' not in p.parts
        assert name in ALLOWED or name.startswith('revisions/or-r42-certified-joint-design-20260924/')
        if 'text' in item:text=item['text']
        else:
            old=base_bytes(item['base']);assert sha(old)==item['base_sha256'],item['base']
            lines=old.decode().splitlines(keepends=True)
            for start,end,replacement in reversed(item['edits']):
                lines[start:end]=[replacement]
            text=''.join(lines)
        assert sha(text.encode())==item['sha256'],name
        ready[name]=text
    (R/'predecessor').mkdir(parents=True,exist_ok=True)
    for name in sorted(ALLOWED|{'main.pdf','electronic_companion.pdf'}):
        old=base_bytes(name);target=R/'predecessor'/name
        if target.exists():assert target.read_bytes()==old,name
        else:target.write_bytes(old)
    for name,text in ready.items():
        p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
    (R/'SOURCE_TRANSPORT_SHA256.json').write_text(json.dumps({k:sha(v.encode()) for k,v in ready.items()},indent=2)+'\n')
    print('Recovered and verified',len(ready),'scientific source files from immutable review base.')
if __name__=='__main__':main()
