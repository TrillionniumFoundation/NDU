"""Unpack checksum-pinned R46 sources without modifying inherited source paths."""
from pathlib import Path, PurePosixPath
import base64, hashlib, json, lzma, subprocess

R = Path(__file__).resolve().parent
ROOT = R.parents[1]
BASE = '260a5224c55e0326d9da7f0c813b4a3fcab7671f'
BRANCH = 'revision/ndu-operations-research-r46-box-decomposition-20260925'
PREFIX = 'revisions/or-r46-box-decomposition-20260925/'
EXPECTED = 'cf32a4f38645eec32dc63a2c5ea90b74f2a209eda7672d94f0a5e239cf4162f6'
OVERRIDES = ['main.tex', 'electronic_companion.tex', 'main.pdf', 'electronic_companion.pdf', 'README.md', 'NDU_OR_submission_checklist.md']

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def main():
    branch = git('branch', '--show-current').decode().strip()
    if branch != BRANCH:
        raise RuntimeError('R46 publication is restricted to its new revision branch')
    git('merge-base', '--is-ancestor', BASE, 'HEAD')
    parts = [R / 'transport' / ('part%02d.b64' % i) for i in range(7)]
    blob = base64.b64decode(''.join(p.read_text().strip() for p in parts), validate=True)
    digest = hashlib.sha256(blob).hexdigest()
    if digest != EXPECTED:
        raise RuntimeError('Source transport checksum mismatch: ' + digest)
    delivery = json.loads(lzma.decompress(blob))
    if len(delivery) != 34:
        raise RuntimeError('Unexpected source file count')
    for name in delivery:
        p = PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts or not (name.startswith(PREFIX) or name in ['README.md', 'NDU_OR_submission_checklist.md']):
            raise RuntimeError('Disallowed source path: ' + name)
        if not isinstance(delivery[name], str):
            raise TypeError(name)
    # Byte-exact snapshots precede any replacement of the current readers.
    for name in OVERRIDES:
        p = R / 'predecessor' / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(git('show', BASE + ':' + name))
    records = []
    for name, content in delivery.items():
        p = ROOT / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding='utf-8')
        records.append({'path': name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
    manifest = dict(status='PASS', base_review_commit=BASE, branch=branch, source_transport_sha256=digest, decoded_files=len(records), files=records)
    (R / 'SOURCE_DELIVERY.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('R46 source transport verified; 34 readable files unpacked; six exact predecessor snapshots preserved.')

if __name__ == '__main__':
    main()
