"""Materialize reviewed R59 text once; no scientific execution in transport code."""
from pathlib import Path
import hashlib,json,shutil,zlib
R=Path(__file__).resolve().parent;ROOT=R.parents[1]
EXPECTED='670df1347a2e7d7d4461ba41acc412f70505ae4ebb98b2c566eafa1ec9919663'
raw=b''.join((R/f'source_payload.part{i:02}').read_bytes() for i in range(4))
assert hashlib.sha256(raw).hexdigest()==EXPECTED,'Transport digest mismatch'
data=json.loads(zlib.decompress(raw));marker=R/'MATERIALIZED.json'
if not marker.exists():
    for rel,text in data.items():
        p=Path(rel);assert not p.is_absolute() and '..' not in p.parts
        dest=R/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text,encoding='utf-8')
    marker.write_text(json.dumps(dict(schema='NDU-R59-source-import-v1',transport_sha256=EXPECTED,initial_source_sha256={p:hashlib.sha256(t.encode()).hexdigest() for p,t in data.items()},scope='Initial import only; ordinary tracked source is authoritative after materialization.'),indent=2)+'\n')
else:
    assert all((R/p).exists() for p in data),'Incomplete prior materialization'
for p in ('results','generated','retained_r58'):(R/p).mkdir(exist_ok=True)
for name in ('main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md'):
    dest=R/'retained_r58'/name
    if not dest.exists():shutil.copyfile(ROOT/name,dest)
assert 'structural-referee-20260926' in (R/'retained_r58/main.tex').read_text()
(R/'requirements.txt').write_text('scipy==1.17.0\nsympy==1.14.0\nPyMuPDF==1.26.7\nmatplotlib==3.10.8\npyscipopt==6.2.1\n')
print('Readable scientific files materialized:',len(data))
