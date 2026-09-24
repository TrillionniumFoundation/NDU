"""Compile current readers and emit one auditable build manifest.

Preparation and evidence generation precede the scientific source commit.
NDU_REMOTE_BUILD=1 requires a clean scientific tree. Local dirty builds record
hashes and the checkout head but never invent a scientific commit identity.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys

R = Path(__file__).resolve().parents[1]
ROOT = R.parents[1]
REL = str(R.relative_to(ROOT))
BASE = 'f26f4da71207a7613735b0504bc34dbe231813c1'
BRANCH = 'revision/ndu-operations-research-r37-integrated-frontier-20260924'
B = ROOT/'.build/ndu-r37'
B.mkdir(parents=True, exist_ok=True)
REMOTE = os.environ.get('NDU_REMOTE_BUILD') == '1'


def call(args, **kwargs):
    return subprocess.check_output(args, cwd=ROOT, text=True, **kwargs)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def required_record(name):
    data = json.loads((R/'results'/name).read_text())
    assert data['status'] in ('PASS', 'PASS_WITH_RECORDED_LIMITS'), name
    return data


def preserve():
    changes = []
    root_allowed = {'main.tex', 'electronic_companion.tex', 'README.md',
                    'NDU_OR_submission_checklist.md', 'main.pdf', 'electronic_companion.pdf'}
    def permitted(path):
        return (path in root_allowed or path.startswith(REL+'/')
                or path in {'.github/workflows/ndu-or-r37-validation.yml',
                            '.github/workflows/ndu-or-r37-publication.yml'}
                or re.fullmatch(r'r37-(?:main|ec|history-main|history-ec)-labels\.aux', path))
    for line in call(['git', 'diff', '--name-status', BASE]).splitlines():
        status, path = line.split('\t', 1)
        assert status in ('A', 'M'), 'A base path was removed or renamed: '+line
        assert permitted(path), 'Unexpected inherited change: '+line
        changes.append({'status': status, 'path': path})
    manifest = json.loads((R/'PRESERVATION_MAP.json').read_text())
    for item in manifest['inherited_reader_modules']:
        assert sha(ROOT/item['path']) == item['sha256']
    for name, digest in manifest['archived_predecessor_files'].items():
        path = R/'predecessor'/name
        assert sha(path) == digest
        original = subprocess.check_output(['git', 'show', BASE+':'+name], cwd=ROOT)
        assert hashlib.sha256(original).hexdigest() == digest
    base_blobs = call(['git', 'ls-tree', '-r', BASE]).splitlines()
    return {'status': 'PASS', 'base_commit': BASE, 'base_blob_count': len(base_blobs),
            'changes': changes, 'no_removed_or_renamed_base_files': True,
            'no_changed_legacy_theorem_code_or_evidence_files': True,
            'exact_predecessor_reader_hashes_verified': True}


def check_evidence():
    v = required_record('verification.json')
    x = required_record('external_solver.json')
    s = required_record('study.json')
    for path, digest in s['source_sha256'].items():
        assert sha(R/path) == digest, 'Studied source changed: '+path
    for path, data in json.loads((R/'code/ENGINE_PROVENANCE.json').read_text()).items():
        assert sha(R/path) == data['sha256'] == sha(ROOT/data['source'])
    assert all(item['status'] == 'PASS' for item in x['records'])
    assert all(item['status'] == 'PASS' for item in v['inherited_suites'].values())
    return v, x, s


def latex(source, pass_number):
    args = ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', '-file-line-error',
            '-output-directory='+str(B), source]
    proc = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    stem = Path(source).stem
    (B/(stem+f'-pass-{pass_number}.txt')).write_text(proc.stdout+'\n'+proc.stderr)
    if proc.returncode:
        raise RuntimeError('LaTeX failed: '+source+'; inspect '+str(B/(stem+'.log')))
    if stem in ('main', 'electronic_companion'):
        tag = 'main' if stem == 'main' else 'ec'
        labels = '\n'.join(line for line in (B/(stem+'.aux')).read_text().splitlines()
                           if line.startswith('\\newlabel'))+'\n'
        (ROOT/('r37-'+tag+'-labels.aux')).write_text(labels)


def log_check(stem):
    text = (B/(stem+'.log')).read_text(errors='replace')
    patterns = [r'LaTeX Warning: Reference .*? undefined',
                r'Package natbib Warning: Citation .*? undefined',
                r'There were undefined references', r'There were undefined citations',
                r'multiply[- ]defined', r'Overfull \\[hv]box',
                r'Float too large for page']
    problems = [pattern for pattern in patterns if re.search(pattern, text, re.S)]
    assert not problems, stem+' unresolved layout/reference issue: '+repr(problems)
    return {'undefined_references': 0, 'undefined_citations': 0,
            'multiply_defined_labels': 0, 'overfull_boxes': 0,
            'log_sha256': sha(B/(stem+'.log'))}


def pdf_info(path):
    info = call(['pdfinfo', str(path)])
    pages = int(re.search(r'^Pages:\s+(\d+)', info, re.M).group(1))
    text = call(['pdftotext', '-layout', str(path), '-'])
    assert text.strip() and '??' not in text, 'Empty reader or unresolved reference glyphs'
    (B/(path.stem+'-extracted.txt')).write_text(text)
    return {'pages': pages, 'bytes': path.stat().st_size, 'sha256': sha(path),
            'pdfinfo': info, 'characters': len(text)}


def label_page(label):
    text = (B/'main.aux').read_text()
    match = re.search(r'\\newlabel\{'+re.escape(label)+r'\}\{\{[^}]*\}\{(\d+)\}', text)
    if not match:
        raise ValueError('Missing page-accounting label '+label)
    return int(match.group(1))


def main():
    head = call(['git', 'rev-parse', 'HEAD']).strip()
    branch = call(['git', 'branch', '--show-current']).strip()
    before = call(['git', 'status', '--porcelain', '--untracked-files=all'])
    if REMOTE:
        assert branch == BRANCH, 'Remote build is restricted to the new revision branch'
        assert not before.strip(), 'Commit scientific sources/evidence before the remote build:\n'+before
    v, x, s = check_evidence()
    abstract = (R/'ABSTRACT.txt').read_text().strip()
    assert len(abstract.split()) <= 200
    assert '$' not in abstract and '\\(' not in abstract
    introduction = (R/'introduction.tex').read_text()
    assert '$' not in introduction and '\\begin{equation' not in introduction
    main_source = (ROOT/'main.tex').read_text()
    for expected in ('[11pt,letterpaper]', '[margin=1in]', '\\onehalfspacing',
                     'Area of review:} Optimization', 'Revision R37'):
        assert expected in main_source, expected
    assert main_source.index('generated/main_references.tex') < main_source.index('static_tables.tex')
    for tag in ('main', 'ec'):
        path = ROOT/('r37-'+tag+'-labels.aux')
        if not path.exists():
            path.write_text('')
    for iteration in range(1, 5):
        latex('main.tex', iteration)
        latex('electronic_companion.tex', iteration)
    for iteration in range(1, 3):
        latex(REL+'/RESPONSE_TO_REFEREES.tex', iteration)
    logs = {stem: log_check(stem) for stem in ('main', 'electronic_companion', 'RESPONSE_TO_REFEREES')}
    for stem, target in [('main', ROOT/'main.pdf'), ('electronic_companion', ROOT/'electronic_companion.pdf'),
                         ('RESPONSE_TO_REFEREES', R/'RESPONSE_TO_REFEREES.pdf')]:
        shutil.copy2(B/(stem+'.pdf'), target)
    readers = {name: pdf_info(path) for name, path in
               [('main', ROOT/'main.pdf'), ('electronic_companion', ROOT/'electronic_companion.pdf'),
                ('response', R/'RESPONSE_TO_REFEREES.pdf')]}
    bibliography_pages = label_page('r37-refs-end')-label_page('r37-refs-start')+1
    nonrefs = readers['main']['pages']-bibliography_pages
    readers['main']['bibliography_pages'] = bibliography_pages
    readers['main']['pages_excluding_references_including_title_and_tables'] = nonrefs
    assert 0 < bibliography_pages < readers['main']['pages']
    assert nonrefs <= 40, f'Main reader exceeds lengthy-manuscript ceiling: {nonrefs}'
    assert readers['electronic_companion']['pages'] <= nonrefs, 'Companion longer than main excluding references'
    preservation = preserve()
    roots = [ROOT/'main.tex', ROOT/'electronic_companion.tex', ROOT/'README.md',
             ROOT/'NDU_OR_submission_checklist.md']
    sources = {str(p.relative_to(ROOT)): sha(p) for p in roots}
    for p in R.rglob('*'):
        if p.is_file() and p.suffix in ('.tex', '.py', '.md', '.json', '.txt', '.csv') and p.name != 'BUILD_VALIDATION.json':
            sources[str(p.relative_to(ROOT))] = sha(p)
    # Representative raster images are created for visual inspection, not
    # mistaken for a completed human/model visual review in this manifest.
    for stem in ('main', 'electronic_companion', 'RESPONSE_TO_REFEREES'):
        subprocess.run(['pdftoppm', '-f', '1', '-singlefile', '-scale-to', '1400', '-png',
                        str(B/(stem+'.pdf')), str(B/(stem+'-first-page'))], check=True, cwd=ROOT)
    record = {'status': 'PASS', 'built_at_utc': datetime.now(timezone.utc).isoformat(),
              'scientific_source_commit': head if not before.strip() else None,
              'checkout_head': head, 'source_tree_clean_at_build_start': not before.strip(),
              'remote_branch': branch, 'workflow_run_id': os.environ.get('GITHUB_RUN_ID'),
              'review_base_commit': BASE,
              'reviewed_R36_commit': '8b17bed9079aa8e3bcaf52e6a5847a60cbf7d7ca',
              'reader_files': readers, 'final_logs': logs,
              'format': {'font_points': 11, 'line_spacing': 1.5, 'margins_inches': 1,
                         'abstract_words': len(abstract.split()), 'introduction_equation_free': True,
                         'anonymous_readers': True, 'area_proposed': 'Optimization',
                         'tables_after_references': True,
                         'observed_category': 'Regular length' if nonrefs <= 30 else 'Lengthy manuscript',
                         'main_nonreference_limit': 40, 'companion_within_main_nonreference_length': True},
              'new_exact_test_counts': v['counts'], 'inherited_suite_status': {k: z['status'] for k, z in v['inherited_suites'].items()},
              'external_HiGHS_exactly_certified_cases': len(x['records']),
              'study_status': s['status'], 'study_process_limit_cases': sum(z['status'] == 'TIME_LIMIT' for z in s['records']),
              'study_configurations': len(s['records']),
              'evidence_file_sha256': {n: sha(R/'results'/n) for n in ('verification.json', 'external_solver.json', 'study.json')},
              'preservation': preservation, 'source_sha256': sources,
              'environment': {'python': sys.version, 'platform': platform.platform(), 'pdflatex': call(['pdflatex', '--version']).splitlines()[0]},
              'visual_review': 'Representative raster images generated; visual inspection is a separate recorded step.',
              'journal_submission_performed': False}
    (R/'BUILD_VALIDATION.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps({'status': 'PASS', 'source_commit': record['scientific_source_commit'],
                      'main_pages': readers['main']['pages'], 'main_excluding_references': nonrefs,
                      'companion_pages': readers['electronic_companion']['pages'],
                      'response_pages': readers['response']['pages'], 'abstract_words': len(abstract.split())}, indent=2), flush=True)


if __name__ == '__main__':
    main()
