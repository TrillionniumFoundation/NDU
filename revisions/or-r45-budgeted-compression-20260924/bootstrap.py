"""Extract the hash-pinned R45 source delivery; never touch historical paths."""
from pathlib import Path, PurePosixPath
import hashlib, io, subprocess, tarfile
R = Path(__file__).resolve().parent
ROOT = R.parents[1]
BRANCH = 'revision/ndu-operations-research-r45-budgeted-compression-20260924'
BASE = '91583abe77208ec4ed25b5fbc5a15f89d54fcd6f'
DIGEST = 'c31718c3da130f8d46cee166a115d31aa6bbf91ae6b1c249a7e35683bd1b13fe'
PREFIX = PurePosixPath('revisions/or-r45-budgeted-compression-20260924')
if (ROOT/'.git').exists():
    branch = subprocess.check_output(['git','branch','--show-current'], cwd=ROOT, text=True).strip()
    if branch != BRANCH:
        raise RuntimeError('Refusing extraction outside the isolated R45 branch')
    subprocess.run(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT,check=True)
parts = [R/'transport'/('part-%02d.bin' % i) for i in range(8)]
data = b''.join(p.read_bytes() for p in parts)
if len(data) != 44600 or hashlib.sha256(data).hexdigest() != DIGEST:
    raise RuntimeError('Scientific source transport hash mismatch')
with tarfile.open(fileobj=io.BytesIO(data),mode='r:xz') as archive:
    members = archive.getmembers()
    if len(members) != 21:
        raise RuntimeError('Unexpected scientific source inventory')
    names = set()
    for member in members:
        p = PurePosixPath(member.name)
        if not member.isfile() or p.is_absolute() or '..' in p.parts or PREFIX not in p.parents:
            raise RuntimeError('Unsafe archive member: '+member.name)
        if p.name == 'bootstrap.py' or 'transport' in p.parts or member.name in names:
            raise RuntimeError('Unexpected archive member: '+member.name)
        names.add(member.name)
    for member in members:
        destination = ROOT/member.name
        destination.parent.mkdir(parents=True,exist_ok=True)
        source = archive.extractfile(member)
        if source is None:
            raise RuntimeError('Missing regular-file payload')
        destination.write_bytes(source.read())
print('Verified and extracted 21 R45 source files; SHA256 '+DIGEST)
