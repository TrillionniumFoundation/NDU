"""Verify the immutable source transport and materialize readable R54 files."""
from pathlib import Path, PurePosixPath
import base64, hashlib, json, lzma
R=Path(__file__).resolve().parent
EXPECTED='478974db2f9199b6b1f57731b0235c2f919d4777794c2454468a53b7cc433cd5'
PARTS=['22d9b87370b076460c1b513933326934e1d2bd97','7635f38d98a693c8ff6eb0e02afe8a86f306dbfb','97120f4750f002876b14e6b894785e42ec796ede','f278c4cfcc379ceba993759b9e1ac20d7a8b8e90','71cef88dd56febac0ccfd37180a4dd91e6dcfb73','5ae978ea7eea6831d08186a0e0bb5fb4fed1d500','3e49f744843a2427e6c64ea0a9b46a2dc6ebfe2e','753d0739e45f59f35175d9f02a7b5e265cd2ba66','eab3859f2b73551f0478e5d5eecde31263c593ec','ad3116664215c1e64cf99fb2d9091d9862a2eb93']
def run():
    pieces=[]
    for i,expected in enumerate(PARTS):
        data=(R/'transport'/f'{i:02d}.b64').read_bytes()
        actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if actual!=expected:raise RuntimeError(f'Corrupt source part {i:02d}')
        pieces.append(b''.join(data.split()))
    payload=base64.b64decode(b''.join(pieces),validate=True)
    if len(payload)!=58376 or hashlib.sha256(payload).hexdigest()!=EXPECTED:
        raise RuntimeError('Source archive digest mismatch')
    sources=json.loads(lzma.decompress(payload).decode('utf-8'))
    if not isinstance(sources,dict) or len(sources)!=39:raise RuntimeError('Unexpected source manifest')
    hashes={}
    for name,content in sources.items():
        p=PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts or not p.parts or not isinstance(content,str):
            raise RuntimeError('Unsafe source path')
        if name in ('PROTOCOL.json','PROTOCOL_HARDNESS_ADDENDUM.json'):
            raise RuntimeError('Frozen protocols must not be transported')
        target=R.joinpath(*p.parts)
        if R.resolve() not in target.resolve().parents:raise RuntimeError('Source escaped revision directory')
        target.parent.mkdir(parents=True,exist_ok=True)
        data=content.encode('utf-8');target.write_bytes(data)
        hashes[name]=hashlib.sha256(data).hexdigest()
    record=dict(status='PASS',format='lzma-json-map-v1',payload_sha256=EXPECTED,payload_bytes=len(payload),files=hashes)
    (R/'SOURCE_ARCHIVE_SHA256.json').write_text(json.dumps(record,indent=2)+'\n')
    print(f'Verified and materialized {len(hashes)} readable R54 source files')
if __name__=='__main__':run()
