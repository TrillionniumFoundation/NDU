"""Authenticate and expand the R52 publication source, preserving review provenance."""
from pathlib import Path, PurePosixPath
import base64, hashlib, json, lzma, subprocess, sys

R = Path(__file__).resolve().parent
ROOT = R.parents[1]
PARENT = '4f0b662bd4184fc77fb57bd09c339bffb6213a69'
FIRST = '2ac1490e5a4149f8c7e154407fbe6fa6208979db'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    transport = R / 'transport'
    manifest = json.loads((transport / 'manifest.json').read_text())
    if manifest['schema'] != 'NDU-R52-source-v1' or manifest['compression'] != 'xz':
        raise ValueError('Unsupported source manifest')
    chunks = []
    for item in manifest['parts']:
        name = PurePosixPath(item['path'])
        if len(name.parts) != 1 or name.is_absolute():
            raise ValueError('Invalid transport path')
        data = (transport / name.name).read_bytes()
        if sha(data) != item['sha256']:
            raise ValueError('Transport digest mismatch: ' + str(name))
        chunks.append(data.strip())
    packed = base64.b64decode(b''.join(chunks), validate=True)
    if sha(packed) != manifest['packed_sha256']:
        raise ValueError('Packed source digest mismatch')
    raw = lzma.decompress(packed)
    if sha(raw) != manifest['raw_sha256']:
        raise ValueError('Expanded source digest mismatch')
    files = json.loads(raw)
    if set(files) != set(manifest['files']):
        raise ValueError('Source coverage mismatch')
    for name, content in files.items():
        path = PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or not isinstance(content, str):
            raise ValueError('Invalid expanded source path')
        if sha(content.encode('utf-8')) != manifest['files'][name]:
            raise ValueError('Readable source digest mismatch: ' + name)
    if '--verify-only' in sys.argv:
        print('PASS: all transport and readable source hashes; files=' + str(len(files)))
        return
    for name, content in files.items():
        path = R / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
    reports = R / 'reports'
    reports.mkdir(exist_ok=True)
    sources = [(FIRST, 'reviews/operation_research_referee_report_r49_independent_harsh_2026-09-25.md', 'first-r49-report.md'),
               (PARENT, 'reviews/operation_research_referee_report_r49_second_independent_harsh_2026-09-25.md', 'second-r49-report.md')]
    for commit, source, name in sources:
        check = subprocess.run(['git', 'cat-file', '-e', commit], cwd=ROOT, capture_output=True)
        if check.returncode:
            subprocess.run(['git', 'fetch', 'origin', commit], cwd=ROOT, check=True)
        (reports / name).write_bytes(subprocess.check_output(['git', 'show', commit + ':' + source], cwd=ROOT))
    (R / 'PARENT_TREE.txt').write_bytes(subprocess.check_output(['git', 'ls-tree', '-r', PARENT], cwd=ROOT))
    record = dict(status='PASS', files=len(files), packed_sha256=sha(packed), raw_sha256=sha(raw),
                  expanded_files=manifest['files'], parent_commit=PARENT, first_report_commit=FIRST)
    (R / 'SOURCE_EXPANSION.json').write_text(json.dumps(record, indent=2) + '\n')
    print('PASS: authenticated readable sources and both immutable reviews')

if __name__ == '__main__':
    main()
