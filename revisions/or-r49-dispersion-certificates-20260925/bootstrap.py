"""Verify and expand the R49 scientific source without modifying ancestor material."""
from pathlib import Path
import base64
import hashlib
import io
import json
import lzma
import subprocess
import tarfile

R = Path(__file__).resolve().parent
ROOT = R.parents[1]
BRANCH = 'revision/ndu-operations-research-r49-dispersion-certificates-20260925'
BASE = '939cce84881a1d1eabf93aa3a2d3f4f4417ce53f'
PAYLOAD_SHA256 = 'fabadb04fd48e1088475f850b28b2f3b5e4b5a420eb2514ad54574eaba005346'
PROTOCOL_BLOB = 'e98bb3a939fa93490e349c5ef0708038dfccdf5d'
EXPECTED = {
    'code/study_r49.py', 'code/response_r49.py', 'code/check_pooling.py',
    'code/tables_r49.py', 'code/publication_r49.py', 'code/verify_r49.py',
    'code/preservation_r49.py', 'code/metadata_r49.py', 'code/assemble_r49.py',
    'code/tests.py', 'code/build_r49.py', 'code/pooling.py',
    'pooling.tex', 'group_boxes.tex', 'introduction.tex', 'study.tex',
    'conclusion.tex', 'RESPONSE_TO_REFEREES.md', 'LOCAL_EXECUTION.json', 'SOURCES.md'
}


def git(*args: str) -> bytes:
    return subprocess.check_output(['git', *args], cwd=ROOT)


def main() -> None:
    if git('branch', '--show-current').decode().strip() != BRANCH:
        raise RuntimeError('Publication must remain on the isolated R49 branch')
    subprocess.run(['git', 'merge-base', '--is-ancestor', BASE, 'HEAD'], cwd=ROOT, check=True)
    if git('hash-object', str(R / 'PROTOCOL.json')).decode().strip() != PROTOCOL_BLOB:
        raise RuntimeError('The protocol frozen before execution has changed')
    encoded = ''.join((R / 'transport' / f'part-{i}.b64').read_text().strip() for i in range(1, 6))
    payload = base64.b64decode(encoded, validate=True)
    if len(payload) != 44708 or hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA256:
        raise RuntimeError('Source transport checksum mismatch; do not execute')
    raw = lzma.decompress(payload)
    if len(raw) != 184320:
        raise RuntimeError('Unexpected decompressed source size')
    files = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:') as archive:
        members = archive.getmembers()
        if len(members) != 20:
            raise RuntimeError('Unexpected source member count')
        for member in members:
            path = (ROOT / member.name).resolve()
            if not member.isfile() or not path.is_relative_to(R) or member.size > 1000000:
                raise RuntimeError(f'Unsafe source member: {member.name}')
            relative = str(path.relative_to(R))
            if relative not in EXPECTED or relative in files:
                raise RuntimeError(f'Unexpected or duplicate source: {relative}')
            stream = archive.extractfile(member)
            if stream is None:
                raise RuntimeError(f'Missing member bytes: {relative}')
            data = stream.read()
            data.decode('utf-8')
            files[relative] = data
    if set(files) != EXPECTED:
        raise RuntimeError('Incomplete source set')
    for name, data in files.items():
        path = R / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    for name in ['generated', 'results', 'predecessor']:
        (R / name).mkdir(exist_ok=True)
    for name in ['main.tex', 'main.pdf', 'electronic_companion.tex', 'electronic_companion.pdf', 'README.md', 'NDU_OR_submission_checklist.md']:
        (R / 'predecessor' / name).write_bytes(git('show', f'{BASE}:{name}'))
    manifest = {
        'status': 'PASS', 'scientific_parent': BASE,
        'frozen_protocol_commit': '2a387b7b8856ca55140146a54a8728a5000f829b',
        'frozen_protocol_blob': PROTOCOL_BLOB,
        'compressed_sha256': PAYLOAD_SHA256,
        'files': {name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())},
        'scope': 'Only new R49 sources are expanded; the six root readers are archived from the immutable R48 parent before replacement.'
    }
    (R / 'TRANSPORT_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'source_files': len(files), 'scientific_parent': BASE}))


if __name__ == '__main__':
    main()
