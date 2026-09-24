"""Assemble the reviewed R43 source bundle without modifying historical paths.

Transport is content-addressed, not executable serialized data. Every member
is UTF-8 source text and is restricted to this revision or four reader paths.
Run --verify-only to check the archive without writing files.
"""
from pathlib import Path, PurePosixPath
import base64, hashlib, json, lzma, subprocess, sys

R = Path(__file__).resolve().parent
ROOT = R.parents[1]
BRANCH = 'revision/ndu-operations-research-r43-prefix-decomposition-20260924'
BASE = 'a0d1f4e3dfc3f7639f806cab01f1faae877d5361'
ARCHIVE_SHA256 = '1a10c86d3587e63c09e70bcb9efcecc38886555136a0a881153650e260e75ef5'
PREFIX = 'revisions/or-r43-prefix-decomposition-20260924/'
READERS = {'main.tex', 'electronic_companion.tex', 'README.md', 'NDU_OR_submission_checklist.md'}

def main():
    if sys.argv[1:] not in ([], ['--verify-only']):
        raise SystemExit('Usage: assemble.py [--verify-only]')
    encoded = ''.join((R/'transport'/('part%02d.b64'%i)).read_text().strip() for i in range(8))
    archive = base64.b64decode(encoded, validate=True)
    if hashlib.sha256(archive).hexdigest() != ARCHIVE_SHA256:
        raise RuntimeError('Source archive hash mismatch')
    members = json.loads(lzma.decompress(archive).decode('utf-8'))
    if not isinstance(members, dict) or len(members) != 28:
        raise RuntimeError('Unexpected source archive structure')
    hashes = {}
    for name, text in members.items():
        path = PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or not isinstance(text, str):
            raise RuntimeError('Invalid archive member: '+name)
        if not (name in READERS or name.startswith(PREFIX)):
            raise RuntimeError('Historical-path write refused: '+name)
        hashes[name] = hashlib.sha256(text.encode('utf-8')).hexdigest()
    if '--verify-only' in sys.argv:
        print(json.dumps({'status':'PASS','archive_sha256':ARCHIVE_SHA256,'files':hashes}, indent=2))
        return
    branch = subprocess.check_output(['git','branch','--show-current'], cwd=ROOT, text=True).strip()
    if branch != BRANCH:
        raise RuntimeError('Refusing assembly outside isolated revision branch')
    subprocess.run(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT,check=True)
    for name, text in members.items():
        destination = ROOT/name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(text.encode('utf-8'))
    (R/'ASSEMBLY_MANIFEST.json').write_text(json.dumps({'status':'PASS','base':BASE,'archive_sha256':ARCHIVE_SHA256,'files':hashes},indent=2)+'\n')
    print('Assembled 28 hash-verified R43 scientific source files on '+BRANCH)

if __name__ == '__main__':
    main()
