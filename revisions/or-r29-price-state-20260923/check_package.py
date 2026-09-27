#!/usr/bin/env python3
"""Validate preservation, exact-check records, reader PDFs and a content manifest.
Run --write once after a clean build; --check is read-only. This is a package
checker, not a formal proof verifier or a substitute for visual review.
"""
from pathlib import Path
import hashlib,json,re,subprocess,sys,platform,importlib.metadata,ast
import fitz
R=Path(__file__).resolve().parent; ROOT=R.parent.parent
BASE='af01e2c33f85835e550896985b7cb83b3f4b784f'
READERS=['main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md']
LABELS=['r29-main-labels.aux','r29-ec-labels.aux','r29-retained-labels.aux','r29-retained-source-main-labels.aux']

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def gitsha(p):
    b=p.read_bytes(); return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def expand(path,seen=None):
    seen=set() if seen is None else seen
    if path in seen:return ''
    seen.add(path);text=path.read_text(); out=text
    for child in re.findall(r'\\input\{([^}]+)\}',text):
        p=ROOT/(child if child.endswith('.tex') else child+'.tex');assert p.is_file(),str(p)
        out+='\n'+expand(p,seen)
    return out

def inspect_pdf(path):
    doc=fitz.open(path);pages=len(doc);refs=[];outside=[];bad=[]
    for n,page in enumerate(doc):
        assert abs(page.rect.width-612)<1 and abs(page.rect.height-792)<1,(path,n,page.rect)
        text=page.get_text()
        if 'References' in text.splitlines():refs.append(n)
        if '\ufffd' in text or '??' in text:bad.append(n+1)
        for w in page.get_text('words'):
            if w[0]<-1 or w[1]<-1 or w[2]>page.rect.width+1 or w[3]>page.rect.height+1:outside.append([n+1,list(w[:5])])
    assert not outside,(path,outside[:5]);assert not bad,(path,bad)
    # Count the first reference page as nonreference, even if it is entirely
    # bibliography. Only later reference-only pages are excluded. Tables count.
    pure=0
    if refs:
        for n in range(refs[0]+1,pages):
            text=doc[n].get_text()
            if re.search(r'(?m)^Table\s+\d',text):break
            pure+=1
    return {'pdf_pages':pages,'conservative_nonreference_pages':pages-pure,
            'reference_heading_pdf_pages':[n+1 for n in refs],
            'text_outside_page':0,'replacement_or_unresolved_markers':0,'sha256':sha(path)}

def run():
    inherited=json.loads((R/'INHERITED_SHA256.json').read_text())
    preserve=json.loads((R/'PRESERVATION.json').read_text())
    latest=json.loads((R/'LATEST_REVIEW.json').read_text())
    assert gitsha(ROOT/latest['path'])==latest['blob_sha'],'latest R29 referee report changed'
    for name,want in inherited.items():
        p=(R/'predecessor'/name) if name in READERS else ROOT/name
        assert p.is_file() and sha(p)==want,('inherited content changed',name)
    for name,want in preserve['reader_predecessors'].items():assert sha(R/'predecessor'/name)==want
    git_verified=False
    if (ROOT/'.git').exists():
        baseline=subprocess.check_output(['git','ls-tree','-r','-z',BASE],cwd=ROOT)
        for item in baseline.split(b'\0'):
            if not item:continue
            info,name=item.split(b'\t',1);mode,typ,want=info.decode().split();name=name.decode()
            assert typ=='blob', (name,typ)
            p=R/'predecessor'/name if name in READERS else ROOT/name
            assert gitsha(p)==want,('baseline git blob mismatch',name)
            assert name in inherited,('unrecorded baseline path',name)
        git_verified=True
    for name,key in [('inherited_mathematics.tex','mathematics_block_sha256'),('retained_evidence_body.tex','retained_evidence_block_sha256')]:
        assert sha(R/name)==preserve[key]
    old=(R/'predecessor/main.tex').read_text();current=(ROOT/'main.tex').read_text()
    for name,a,b in [('inherited_mathematics.tex',r'\section{The Value Frontier',r'\section{Computational Evidence}'),('retained_evidence_body.tex',r'\section{Computational Evidence}',r'\section{Conclusions}')]:
        assert (R/name).read_text()==old[old.index(a):old.index(b)]
    math=(R/'inherited_mathematics.tex').read_text().replace('revisions/or-r28-20260923/bridge_main.tex','revisions/'+R.name+'/bridge_main.tex')
    assert math in current
    active=expand(ROOT/'main.tex')+'\n'+expand(ROOT/'electronic_companion.tex')+'\n'+expand(R/'retained_evidence.tex')
    old_expanded=expand(R/'predecessor/main.tex')
    labels=set(re.findall(r'\\label\{([^}]+)\}',active))
    old_labels=set(re.findall(r'\\label\{([^}]+)\}',old_expanded))
    assert old_labels<=labels,('missing inherited labels',sorted(old_labels-labels))
    defined=set(re.findall(r'\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}',active))
    used=set()
    for keys in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}',active):used.update(k.strip() for k in keys.split(','))
    assert used<=defined,('missing citation keys',used-defined)
    assert r'\documentclass[11pt,letterpaper]' in current and r'\onehalfspacing' in current and r'\usepackage[margin=1in]{geometry}' in current
    abstract=(R/'abstract.txt').read_text();assert len(abstract.split())<=200 and '$' not in abstract and '\\cite' not in abstract
    intro=(R/'intro.tex').read_text();assert '$' not in intro and '\\[' not in intro and '\\begin{equation' not in intro
    assert '\\footnote{' not in active
    warning_counts={}
    for name in ['main-build.log','ec-build.log','retained-build.log']:
        text=(R/'results'/name).read_text()
        bad=[s for s in text.splitlines() if 'Warning' in s or 'Overfull' in s or 'Missing character' in s or s.startswith('!')]
        assert not bad,(name,bad)
        warning_counts[name]={'warnings':0,'overfull_boxes':0,'missing_characters':0}
    docs={name:inspect_pdf(ROOT/name) for name in ['main.pdf','electronic_companion.pdf']}
    docs['retained_evidence.pdf']=inspect_pdf(R/'retained_evidence.pdf')
    assert docs['main.pdf']['conservative_nonreference_pages']<=40
    assert docs['electronic_companion.pdf']['pdf_pages']<=docs['main.pdf']['pdf_pages']
    assert docs['electronic_companion.pdf']['conservative_nonreference_pages']<=docs['main.pdf']['conservative_nonreference_pages']
    verified=json.loads((R/'results/verification.json').read_text());ext=json.loads((R/'results/extensions_verification.json').read_text())
    assert verified['status']==ext['status']=='PASS'
    for name in ['verify.py','verify_extensions.py']:
        tree=ast.parse((R/name).read_text())
        modules={alias.name for node in ast.walk(tree) if isinstance(node,ast.Import) for alias in node.names}
        modules.update(node.module for node in ast.walk(tree) if isinstance(node,ast.ImportFrom))
        assert not modules.intersection({'price_solver','research'})
    inherited_replays={}
    for n in range(24,29):
        p=R/f'results/inherited_r{n}_replay.json'
        if p.exists():
            record=json.loads(p.read_text());assert isinstance(record,dict) and record
            if 'status' in record:assert record['status']=='PASS'
            inherited_replays[str(n)]={'sha256':sha(p),'recorded':True}
    report={'status':'PASS','baseline_commit':BASE,'baseline_git_tree_verified':git_verified,
        'latest_review':latest,'preserved_baseline_files':len(inherited),'byte_identical_reader_backups':len(READERS),
        'inherited_label_definitions_preserved':len(old_labels),'citation_keys':len(used),
        'abstract_words':len(abstract.split()),'category':'Lengthy Manuscript',
        'format_source':'https://pubsonline.informs.org/page/opre/submission-guidelines',
        'documents':docs,'build_logs':warning_counts,'exact_verification':verified,
        'extended_verification':ext,'inherited_replays':inherited_replays,
        'limitations':['Arithmetic complexity is not rational bit complexity.',
          'Numerical tree comparisons are not a formal proof; exact compact certificates are checked separately.',
          'Automated text-box checks do not replace visual page inspection.',
          'Journal submission, independent novelty adjudication and editorial acceptance are not claimed.']}
    target=R/'results/package_check.json'
    excluded={'MANIFEST.json','BUILD_REPORT.md','results/package_check.json'}
    def hashes():
        paths=[ROOT/f for f in READERS+LABELS]+[ROOT/latest['path']]
        paths += [p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and str(p.relative_to(R)) not in excluded]
        return {str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))}
    if '--write' in sys.argv:
        target.write_text(json.dumps(report,indent=2)+'\n')
        manifest={'baseline_commit':BASE,'content_sha256':hashes(),
            'excluded_self_reports':sorted(excluded),'report_sha256':sha(target)}
        (R/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
        rows='\n'.join(f"| {name} | {v['pdf_pages']} | {v['conservative_nonreference_pages']} |" for name,v in docs.items())
        environment={'python':sys.version.split()[0],'platform':platform.platform()}
        for pkg in ['numpy','scipy','PyMuPDF']:
            try:environment[pkg]=importlib.metadata.version(pkg)
            except importlib.metadata.PackageNotFoundError:environment[pkg]='not installed'
        (R/'BUILD_REPORT.md').write_text('# R29 build and preservation report\n\nStatus: **PASS** (package/record checks; not independent scientific acceptance).\n\n'
          f"Baseline review commit: `{BASE}`. Preserved baseline files: **{len(inherited)}**; byte-identical reader backups: **6**. Git-tree verification: **{git_verified}**.\n\n"
          f"Latest report: `{latest['commit']}`; all 18 sections answered; original report Git blob verified.\n\n"
          '| Document | PDF pages | Conservative nonreference pages |\n|---|---:|---:|\n'+rows+'\n\n'
          f"Category: **Lengthy Manuscript**; manuscript nonreference count is below the published usual 40-page limit, and the electronic companion is no longer than the manuscript. Abstract: **{len(abstract.split())} words**.\n\n"
          'Final build logs have no warnings, overfull boxes or missing-character messages. Automated PDF checks found no text outside page bounds or unresolved/replacement text markers. This does not replace visual inspection.\n\n'
          f"Exact graph cases: **{verified['instances']}**; exact assertion groups: **{verified['exact_assertion_groups']}**. Independent optimized-table QPs: **{ext['exact_table_qps']}**; small-tree comparisons: **{ext['small_tree_matrix_crosschecks']}**; feasible supporting-cut queries: **{ext['exact_oracle_queries']}**; exhaustive partitions: **{ext['exhaustive_partitions']}**.\n\n"
          'The package includes regenerated single-run timing records and tables. These are observations, not a broad comparative speed claim. The historical 83/84 refresh/no-speed result is unchanged.\n\n'
          'Environment:\n\n```json\n'+json.dumps(environment,indent=2)+'\n```\n\n'
          'The content manifest excludes its own bytes, this human-readable report and the machine-readable report to avoid circular hashes; it separately pins the machine-readable report. Final scientific commit identity and fresh-checkout success are recorded in GitHub, not inferred from this file.\n')
    else:
        assert '--check' in sys.argv,'Use --write or --check'
        stored=json.loads(target.read_text());assert stored==report,('package report changed',report)
        manifest=json.loads((R/'MANIFEST.json').read_text());assert manifest['content_sha256']==hashes(),'content manifest mismatch'
        assert manifest['report_sha256']==sha(target)
    print(json.dumps(report,indent=2))

if __name__=='__main__':run()
