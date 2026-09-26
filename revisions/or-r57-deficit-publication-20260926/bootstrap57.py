"""Decode and verify R57 scientific source against the immutable R54 parent."""
from pathlib import Path
import hashlib,json,lzma,subprocess
R=Path(__file__).resolve().parent
ROOT=R.parents[1]
BASE='eee0d39e08eaedc3a26cad792b71c9c5b5a8abd9'
EXPECTED='e5eb3b980b0e71613187bf8a995e3f2ed03966788d5c12a74e62a4c655f309b5'
def baseline(path):
    return subprocess.run(['git','show',BASE+':'+path],cwd=ROOT,capture_output=True,check=True).stdout
raw=b''.join((R/'transport'/f'source-{i:02d}.xz.part').read_bytes() for i in range(5))
assert hashlib.sha256(raw).hexdigest()==EXPECTED,'Transport digest mismatch'
records=json.loads(lzma.decompress(raw))
outputs={}
for name,rec in records.items():
    path=R/name
    assert R in path.resolve().parents and '..' not in Path(name).parts
    if 'text' in rec:
        text=rec['text']
    else:
        b=baseline(rec['base'])
        assert hashlib.sha256(b).hexdigest()==rec['sha'], 'Baseline mismatch: '+name
        lines=b.decode().splitlines(keepends=True)
        text=''.join(op if isinstance(op,str) else ''.join(lines[op[0]:op[1]]) for op in rec['ops'])
    b=text.encode()
    assert hashlib.sha256(b).hexdigest()==rec['output_sha256'],'Output mismatch: '+name
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b)
    outputs[name]=rec['output_sha256']
for name in ['README.md','main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','NDU_OR_submission_checklist.md']:
    path=R/'predecessor'/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(baseline(name))
(R/'TRANSPORT_VERIFICATION.json').write_text(json.dumps(dict(status='PASS',scientific_parent=BASE,transport_sha256=EXPECTED,decoded_files=outputs),indent=2)+'\n')
(R/'PUBLICATION_STATUS.json').write_text(json.dumps(dict(stage='SOURCE_ONLY',complete=False,note='Scientific source is decoded. The actual execution, reader build and remote publication must pass before this becomes a completed revision.'),indent=2)+'\n')
print('Verified',len(outputs),'R57 scientific source files against the immutable parent.')
