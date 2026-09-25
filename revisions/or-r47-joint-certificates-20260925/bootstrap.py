"""Decode checked R47 sources and retain the immutable R46 readers."""
from pathlib import Path, PurePosixPath
import base64, hashlib, json, lzma, subprocess, tarfile

BASE = '9f260e0d6c4e06cf4227f96865a88f4dab67e58e'
BRANCH = 'revision/ndu-operations-research-r47-joint-certificates-20260925'
DIGEST = '3bf742a076e613719bcf94a19dffef379be9935d635d512b01c3e3371512c722'
R = Path(__file__).resolve().parent
ROOT = R.parents[1]
PREFIX = R.relative_to(ROOT).as_posix() + '/'
READERS = {'main.tex', 'main.pdf', 'electronic_companion.tex', 'electronic_companion.pdf', 'README.md', 'NDU_OR_submission_checklist.md'}

def run():
    branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip()
    if branch != BRANCH:
        raise RuntimeError('Publication is restricted to the isolated R47 branch')
    parts = sorted((R / 'transport').glob('part-*.b64'))
    if [p.name for p in parts] != [f'part-{i:02d}.b64' for i in range(8)]:
        raise RuntimeError('The transport must contain exactly eight ordered parts')
    packed = base64.b64decode(''.join(p.read_text().strip() for p in parts), validate=True)
    if hashlib.sha256(packed).hexdigest() != DIGEST:
        raise RuntimeError('Source transport digest mismatch; no sources were installed')
    payload = json.loads(lzma.decompress(packed))
    if len(payload) != 28:
        raise RuntimeError('Unexpected scientific source count')
    for name, content in payload.items():
        p = PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts or not isinstance(content, str):
            raise RuntimeError('Invalid transport path or nontext content')
        if not (name.startswith(PREFIX) or name in {'README.md', 'NDU_OR_submission_checklist.md'}):
            raise RuntimeError('Transport would modify an inherited source: ' + name)
    predecessor = R / 'predecessor'
    predecessor.mkdir(parents=True, exist_ok=True)
    hashes = {}
    proc = subprocess.Popen(['git', 'archive', '--format=tar', BASE], cwd=ROOT, stdout=subprocess.PIPE)
    with tarfile.open(fileobj=proc.stdout, mode='r|') as archive:
        for member in archive:
            if not member.isfile():
                continue
            data = archive.extractfile(member).read()
            hashes[member.name] = hashlib.sha256(data).hexdigest()
            if member.name in READERS:
                (predecessor / member.name).write_bytes(data)
    if proc.wait() != 0 or len(hashes) != 2308 or not READERS.issubset(hashes):
        raise RuntimeError('Immutable baseline export is incomplete')
    (R / 'BASELINE_SHA256.json').write_text(json.dumps(hashes, sort_keys=True, indent=2) + '\n')
    source_hashes = {}
    for name, content in payload.items():
        destination = ROOT / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding='utf-8')
        source_hashes[name] = hashlib.sha256(destination.read_bytes()).hexdigest()
    manifest = dict(status='PASS', base_commit=BASE, review_commit='260a5224c55e0326d9da7f0c813b4a3fcab7671f', branch=BRANCH, compressed_sha256=DIGEST, compressed_bytes=len(packed), source_files=len(payload), inherited_files=len(hashes), source_sha256=source_hashes)
    (R / 'TRANSPORT_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({k:v for k,v in manifest.items() if k != 'source_sha256'}, indent=2))

if __name__ == '__main__':
    run()
