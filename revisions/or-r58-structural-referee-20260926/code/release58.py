"""Fail-closed R58 release checks and bounded dependency-complete ZIP."""
from pathlib import Path
import datetime, hashlib, json, os, shutil, subprocess, sys, tempfile, zipfile
R = Path(__file__).resolve().parents[1]
ROOT = R.parents[1]
REL = R.relative_to(ROOT)
PARENT = 'debd4dfa4053cf5f3d6fcf06633b749ef6144ed6'
BASE = 'eee0d39e08eaedc3a26cad792b71c9c5b5a8abd9'
CHECKS = ['BUILD_VALIDATION.json', 'PRESERVATION_MANIFEST.json', 'results/PUBLICATION_AUDIT.json',
          'results/REGRESSION.json', 'results/JOINT_TYPE_REGRESSION.json',
          'results/CHECKER_DEPENDENCIES.json', 'results/STRUCTURAL_R58.json']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def read(path):
    return json.loads(path.read_text())


def preservation():
    allowed = {'README.md', 'main.tex', 'main.pdf', 'electronic_companion.tex',
               'electronic_companion.pdf', 'NDU_OR_submission_checklist.md'}
    errors, records = [], []
    for base in [BASE, PARENT]:
        raw = subprocess.check_output(['git', 'ls-tree', '-rz', base], cwd=ROOT)
        for line in raw.split(b'\0'):
            if not line:
                continue
            meta, name = line.split(b'\t', 1)
            mode, kind, old = meta.decode().split()
            if kind != 'blob':
                continue
            name = name.decode()
            path = ROOT / name
            if not path.is_file():
                errors.append('Missing ' + name)
                continue
            data = path.read_bytes()
            now = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            retained = name
            if now != old:
                retained = str(REL / 'predecessor' / name)
                q = ROOT / retained
                if name not in allowed or not q.is_file():
                    errors.append('Unpreserved replacement ' + name)
                    continue
                b = q.read_bytes()
                if hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest() != old:
                    errors.append('Wrong predecessor ' + name)
            records.append(dict(base=base, path=name, original_blob=old, retained_at=retained))
    write(R / 'PRESERVATION_MANIFEST.json', dict(status='PASS' if not errors else 'FAIL',
        checked_parents=[BASE, PARENT], checked_entries=len(records), errors=errors, files=records))
    if errors:
        raise RuntimeError('; '.join(errors[:20]))
    print('Preservation PASS:', len(records), 'parent entries')


def verify():
    for name in CHECKS:
        if read(R / name).get('status') != 'PASS':
            raise RuntimeError('Failed check: ' + name)
    structural = read(R / 'results/STRUCTURAL_R58.json')
    expected = (24, 168, 48)
    actual = tuple(structural[k] for k in ('approximate_type_models', 'independently_checked_budget_certificates', 'rejected_corruptions'))
    if actual != expected:
        raise RuntimeError('Incomplete R58 structural suite')
    source = {p.name: sha(p) for p in (R / 'code').glob('*.py')}
    if source != read(R / 'results/SOURCE_MANIFEST.json')['source_hashes']:
        raise RuntimeError('Scientific code differs from timed execution')
    build = read(R / 'BUILD_VALIDATION.json')
    for p, expected_hash in build['source_sha256'].items():
        if sha(ROOT / p) != expected_hash:
            raise RuntimeError('Reader source drift: ' + p)
    for name, expected_hash in build['pdf_sha256'].items():
        if sha(R / (name + '.pdf')) != expected_hash:
            raise RuntimeError('Reader PDF drift: ' + name)
    cases = read(R / 'results/CASES.json') + read(R / 'results/EXTENDED_CASES.json')
    expected_ids = {c['id'] + '--' + method for c in cases for method in c['methods']}
    run_files = {p.stem: p for p in (R / 'results/runs').glob('*.json') if '.phase.' not in p.name}
    if set(run_files) != expected_ids or len(expected_ids) != 225:
        raise RuntimeError('Declared run set differs from retained records')
    for p in run_files.values():
        row = read(p)
        if 'certificate' in row and sha(R / 'results' / row['certificate']) != row['certificate_sha256']:
            raise RuntimeError('Official certificate changed: ' + p.name)
    audit = read(R / 'results/PUBLICATION_AUDIT.json')
    for name, expected_hash in audit['record_sha256'].items():
        if sha(R / 'results/runs' / name) != expected_hash:
            raise RuntimeError('Changed official run: ' + name)
    freeze = read(R / 'SOURCE_FREEZE.json')
    if freeze['source_hashes'] != source:
        raise RuntimeError('Source-freeze disagreement')
    for name in ('main.tex', 'main.pdf', 'electronic_companion.tex', 'electronic_companion.pdf'):
        if (ROOT / name).read_bytes() != (R / name).read_bytes():
            raise RuntimeError('Root is not the current reader: ' + name)
    print('Release verification PASS: source, reader graph and all 225 declared records')


def package():
    verify()
    entries = set()
    dest = R / 'CODE_AND_DATA.zip'
    exclude = {'CODE_AND_DATA.zip', 'PACKAGE_MANIFEST.json', 'PUBLICATION_STATUS.json',
               'EXTRACTED_PACKAGE_VALIDATION.json', 'CURRENT_RELEASE.json'}
    for p in R.rglob('*'):
        if p.is_file() and p.name not in exclude and '__pycache__' not in p.parts and 'transport' not in p.parts:
            entries.add(p)
    # Retained tables rely on these original records. Earlier unrelated large
    # benchmark archives stay unchanged in Git; they are not current dependencies.
    for folder in ('or-r52-resource-path-20260925', 'or-r53-catalog-safe-certificates-20260926', 'or-r54-exact-price-path-20260926'):
        for p in (ROOT / 'revisions' / folder).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.zip', '.part', '.pyc'):
                entries.add(p)
    # Include the actual recorder-derived reader closure, not a guessed path list.
    for path in read(R / 'BUILD_VALIDATION.json')['source_sha256']:
        entries.add(ROOT / path)
    for name in ('README.md', 'main.tex', 'main.pdf', 'electronic_companion.tex',
                 'electronic_companion.pdf', 'NDU_OR_submission_checklist.md', 'informs3.cls', 'main.bib', 'ormsv080.bst'):
        if (ROOT / name).exists():
            entries.add(ROOT / name)
    # Historical code is inexpensive and preserves script dependencies.
    entries.update(p for p in (ROOT / 'revisions').rglob('*.py') if '__pycache__' not in p.parts and 'transport' not in p.parts)
    forbidden_fonts = {'.ttf', '.otf', '.woff', '.woff2', '.pfb', '.afm', '.ttc'}
    if any(p.suffix.lower() in forbidden_fonts for p in entries):
        raise RuntimeError('Font binary must not enter deliverable')
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(entries):
            z.write(p, p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(dest) as z:
        if z.testzip() is not None:
            raise RuntimeError('Corrupt archive')
    size = dest.stat().st_size
    if size >= 95 * 1024 * 1024:
        raise RuntimeError('Archive exceeds the explicit 95 MiB publication safety limit')
    write(R / 'PACKAGE_MANIFEST.json', dict(status='PASS', sha256=sha(dest), bytes=size,
        files=len(entries), file_sha256={p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(entries)},
        scope='Self-contained R58 current study and compiled-reader closure; original R52-R54 table evidence; older unrelated benchmarks preserved in Git.'))
    print('Package PASS:', size, 'bytes;', len(entries), 'files')


def extracted_check():
    manifest = read(R / 'PACKAGE_MANIFEST.json')
    if sha(R / 'CODE_AND_DATA.zip') != manifest['sha256']:
        raise RuntimeError('Archive hash mismatch')
    with tempfile.TemporaryDirectory(prefix='ndu-r58-extracted-') as tmp:
        root = Path(tmp)
        with zipfile.ZipFile(R / 'CODE_AND_DATA.zip') as z:
            for name in z.namelist():
                if name.startswith('/') or '..' in Path(name).parts:
                    raise RuntimeError('Unsafe ZIP entry')
            z.extractall(root)
        for name, expected in manifest['file_sha256'].items():
            if sha(root / name) != expected:
                raise RuntimeError('Extracted hash mismatch: ' + name)
        rr = root / REL
        commands = [['tests56.py'], ['structural58.py'], ['revision57.py', 'joint_type_tests', 'checker_import_test'], ['build56.py']]
        runs = []
        for args in commands:
            cp = subprocess.run([sys.executable, str(rr / 'code' / args[0]), *args[1:]], cwd=root,
                                capture_output=True, text=True, timeout=240)
            runs.append(dict(command=args, returncode=cp.returncode, output=cp.stdout[-4000:], stderr=cp.stderr[-2000:]))
            if cp.returncode:
                write(R / 'EXTRACTED_PACKAGE_VALIDATION.json', dict(status='FAIL', runs=runs))
                raise RuntimeError('Extracted-copy check failed: ' + str(args) + '\n' + cp.stdout[-4000:] + cp.stderr[-2000:])
        rebuilt = read(rr / 'BUILD_VALIDATION.json')
        if rebuilt['pages'] != read(R / 'BUILD_VALIDATION.json')['pages']:
            raise RuntimeError('Extracted-copy pagination differs')
    write(R / 'EXTRACTED_PACKAGE_VALIDATION.json', dict(status='PASS', archive_sha256=manifest['sha256'],
        all_entry_hashes_match=True, clean_copy_tests_and_build=True, runs=runs,
        note='Timings were not rerun or overwritten. PDF byte identity is not claimed across build timestamps.'))
    print('Clean extracted-copy tests and reader rebuild PASS')


def finalize():
    verify()
    for name in ('PACKAGE_MANIFEST.json', 'EXTRACTED_PACKAGE_VALIDATION.json'):
        if read(R / name)['status'] != 'PASS':
            raise RuntimeError('Failed release dependency: ' + name)
    reader_hash = {n: sha(R / n) for n in ('main.pdf', 'electronic_companion.pdf', 'RESPONSE_TO_REFEREES.pdf', 'CODE_AND_DATA.zip')}
    write(R / 'PUBLICATION_STATUS.json', dict(stage='COMPLETE', complete=True, revision='R58',
        created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        source_commit=read(R / 'SOURCE_FREEZE.json')['source_commit'], run_id=os.environ.get('GITHUB_RUN_ID'),
        checks=CHECKS + ['PACKAGE_MANIFEST.json', 'EXTRACTED_PACKAGE_VALIDATION.json'], reader_sha256=reader_hash,
        scope='Completed finite tests, source/result integrity, original-policy certificates, reader builds and repository publication package. Mathematical proofs await referee assessment; no editorial acceptance claim.'))
    print('R58 publication package COMPLETE')

if __name__ == '__main__':
    actions = {'preservation': preservation, 'verify': verify, 'package': package,
               'extracted_check': extracted_check, 'finalize': finalize}
    for task in sys.argv[1:]:
        actions[task]()
