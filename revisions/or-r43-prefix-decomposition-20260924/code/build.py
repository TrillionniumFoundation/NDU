"""Reproducible readers and validation. Run from repository root.

python revisions/or-r43-prefix-decomposition-20260924/code/build.py prepare
python revisions/or-r43-prefix-decomposition-20260924/code/build.py build

Prepare executes all new and inherited exact tests in isolated paths; build
compiles the already prepared, committed sources and records their identities.
"""
from pathlib import Path
from datetime import datetime, timezone
import subprocess, sys, re, json, hashlib, shutil
R=Path(__file__).resolve().parents[1]; ROOT=R.parents[1]
BASE='a0d1f4e3dfc3f7639f806cab01f1faae877d5361'
REVIEW=BASE
BRANCH='revision/ndu-operations-research-r43-prefix-decomposition-20260924'
B=ROOT/'.build/ndu-r43'; B.mkdir(parents=True,exist_ok=True)


def run(cmd, **kwargs):
    return subprocess.run(cmd,cwd=ROOT,check=True,**kwargs)


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def escape(text):
    table={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#',
           '_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
    return ''.join(table.get(c,c) for c in text)


def inline(s):
    parts=re.split(r'(`[^`]+`|\*\*[^*]+\*\*)',s)
    out=[]
    for p in parts:
        if p.startswith('`') and p.endswith('`'):
            # url/path commands supply safe break points for long source identifiers.
            raw=p[1:-1]
            if ' ' not in raw: out.append(r'\nolinkurl{'+raw+'}')
            else: out.append(r'\texttt{'+escape(raw)+'}')
        elif p.startswith('**') and p.endswith('**'):
            out.append(r'\textbf{'+escape(p[2:-2])+'}')
        else: out.append(escape(p))
    return ''.join(out)


def response_tex():
    body=[]
    for line in (R/'RESPONSE_TO_REFEREES.md').read_text().splitlines():
        if line.startswith('# '): body.append(r'\section*{'+escape(line[2:])+'}')
        elif line.startswith('## '): body.append(r'\subsection*{'+escape(line[3:])+'}')
        else: body.append(inline(line.rstrip())+'\n')
    text=r'''\documentclass[11pt,letterpaper]{article}
\usepackage[margin=1in]{geometry}
\usepackage[T1]{fontenc}
\usepackage{newtxtext,newtxmath}
\usepackage{setspace}
\usepackage{xurl}
\usepackage[hidelinks]{hyperref}
\setstretch{1.12}\setlength{\emergencystretch}{4em}
\hypersetup{pdftitle={Response to the R42 Operations Research Referee Report},pdfauthor={Anonymous}}
\begin{document}
'''+ '\n'.join(body)+'\n\\end{document}\n'
    (R/'RESPONSE_TO_REFEREES.tex').write_text(text)


def preservation():
    (R/'predecessor').mkdir(parents=True,exist_ok=True)
    (R/'results').mkdir(parents=True,exist_ok=True)
    # Snapshot older readers from the immutable base when a full git checkout exists.
    result={'base_source_sha':BASE,'review_sha':REVIEW,'new_branch':BRANCH,'all_prior_revision_directories':'unchanged',
            'predecessor_readers':{}}
    if (ROOT/'.git').exists():
        assert git('branch','--show-current')==BRANCH,'Refusing build on another branch'
        existing=git('ls-tree','-r','--name-only',BASE).splitlines()
        permitted={'main.tex','electronic_companion.tex','main.pdf','electronic_companion.pdf',
                   'README.md','NDU_OR_submission_checklist.md'}
        # Check current working bytes of every inherited tracked file, not only staged differences.
        changed=git('diff','--name-only',BASE,'--').splitlines()
        unexpected=[p for p in changed if p in existing and p not in permitted]
        if unexpected: raise RuntimeError('Historical paths modified: '+str(unexpected))
        result['base_tracked_files']=len(existing)
        result['prior_paths_unchanged']=len(existing)-len(permitted.intersection(existing))
        result['preservation_checked_against_git_base']=True
        for name in permitted:
            p=R/'predecessor'/name
            old=subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT)
            if not p.exists(): p.write_bytes(old)
            assert p.read_bytes()==old,'Predecessor copy does not match base: '+name
    else:
        result['preservation_checked_against_git_base']=False
        result['local_scope']='Downloaded predecessor reader artifact; full-tree check runs in CI checkout.'
    for p in sorted((R/'predecessor').glob('*')):
        if p.is_file(): result['predecessor_readers'][p.name]=sha(p)
    (R/'PRESERVATION_MANIFEST.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def prepare():
    preservation()
    for script in ('tests.py','study.py','inherited.py','tables.py'):
        run([sys.executable,str(R/'code'/script)])
    response_tex()
    for src,dest in [('README.md','README.md'),('SUBMISSION_CHECKLIST.md','NDU_OR_submission_checklist.md')]:
        if (R/src).exists(): shutil.copy2(R/src,ROOT/dest)
    print('Prepared scientific sources, executed evidence, response, and preservation record.')


def labels(source,target):
    lines=(B/(source+'.aux')).read_text().splitlines()
    (ROOT/target).write_text('\\relax\n'+'\n'.join(x for x in lines if x.startswith('\\newlabel'))+'\n')


def compile_one(name):
    with (B/(Path(name).stem+'-console.log')).open('w') as log:
        run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error',
             '-recorder','-output-directory='+str(B),name],stdout=log,stderr=subprocess.STDOUT)


def pages(path):
    info=subprocess.check_output(['pdfinfo',str(path)],text=True)
    return int(re.search(r'Pages:\s+(\d+)',info).group(1))


def build():
    provenance=preservation()
    response_tex()
    for _ in range(4):
        compile_one('main.tex'); labels('main','r43-main-labels.aux')
        compile_one('electronic_companion.tex'); labels('electronic_companion','r43-ec-labels.aux')
    for _ in range(2): compile_one(str(R/'RESPONSE_TO_REFEREES.tex'))
    warnings={}
    for name in ('main','electronic_companion','RESPONSE_TO_REFEREES'):
        log=(B/(name+'.log')).read_text(errors='replace')
        bad=[x for x in log.splitlines() if any(t in x for t in
             ('undefined','Overfull \\hbox','Overfull \\vbox','multiply defined','Label(s) may have changed'))]
        if bad: warnings[name]=bad
    if warnings: raise RuntimeError('Reader validation warnings: '+json.dumps(warnings))
    # Read page labels rather than assume a fixed bibliography length.
    aux=(B/'main.aux').read_text()
    begin=int(re.search(r'\\newlabel\{refs-start\}\{\{[^}]*\}\{(\d+)\}',aux).group(1))
    end=int(re.search(r'\\newlabel\{refs-end\}\{\{[^}]*\}\{(\d+)\}',aux).group(1))
    main_pages=pages(B/'main.pdf'); ec_pages=pages(B/'electronic_companion.pdf')
    nonreference=main_pages-(end-begin+1)
    assert nonreference<=40,('Lengthy-paper nonreference limit',nonreference)
    assert ec_pages<=main_pages,('Companion longer than article',ec_pages,main_pages)
    abstract_words=len((R/'ABSTRACT.txt').read_text().split())
    assert abstract_words<=200,('Abstract exceeds journal limit',abstract_words)
    for name in ('main.pdf','electronic_companion.pdf'): shutil.copy2(B/name,ROOT/name)
    shutil.copy2(B/'RESPONSE_TO_REFEREES.pdf',R/'RESPONSE_TO_REFEREES.pdf')
    for name in ('verification.json','inherited.json'):
        record=json.loads((R/'results'/name).read_text())
        assert record.get('passed',False) or record.get('status','').upper() in ('PASS','PASSED')
    if (ROOT/'.git').exists():
        summary=json.loads((R/'results/study_summary.json').read_text())
        assert summary['independent_nonlinear_runs']==6
        assert summary['independent_comparisons_passed']==6
    # Only a committed, byte-identical source tree can receive a scientific SHA.
    dependencies=set()
    for reader in ('main','electronic_companion','RESPONSE_TO_REFEREES'):
        for line in (B/(reader+'.fls')).read_text().splitlines():
            if not line.startswith('INPUT '): continue
            p=Path(line[6:])
            if not p.is_absolute(): p=ROOT/p
            p=p.resolve()
            if p.is_file() and ROOT in p.parents and p.suffix in ('.tex','.sty','.cls','.bib'):
                dependencies.add(p)
    dependencies.update(R.glob('*.py'))
    dependencies.update((R/'code').glob('*.py'))
    dependencies.add(R/'RESPONSE_TO_REFEREES.md')
    tracked_source_files=[str(p.relative_to(ROOT)) for p in sorted(dependencies)]
    clean=False
    if (ROOT/'.git').exists():
        changed=git('diff','--name-only','HEAD','--',*tracked_source_files)
        untracked=git('ls-files','--others','--exclude-standard','--',*tracked_source_files)
        clean=not changed and not untracked
        if not clean: raise RuntimeError('Scientific source must be committed before build: '+changed+' '+untracked)
    manifest=dict(status='PASS',utc=datetime.now(timezone.utc).isoformat(),base_source_sha=BASE,review_sha=REVIEW,
                  source_commit=git('rev-parse','HEAD') if clean else 'local-artifact-worktree',source_tree_clean=clean,complete_reader_inputs={str(p.relative_to(ROOT)):sha(p) for p in sorted(dependencies)},toolchain=subprocess.check_output(['pdflatex','--version'],text=True).splitlines()[0],
                  branch=BRANCH,main_pages=main_pages,main_nonreference_pages=nonreference,
                  companion_pages=ec_pages,response_pages=pages(R/'RESPONSE_TO_REFEREES.pdf'),
                  abstract_words=abstract_words,undefined_references=0,overfull_boxes=0,
                  multiply_defined_labels_or_citations=0,preservation=provenance,
                  outputs={name:sha(ROOT/name) for name in ('main.pdf','electronic_companion.pdf')},
                  evidence={p.name:sha(p) for p in (R/'results').glob('*.json')},
                  source_hashes={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'main.tex',ROOT/'electronic_companion.tex']+
                    list(R.glob('*.tex'))+list((R/'code').glob('*.py'))+list((R/'derived').glob('*.tex'))+
                    list((R/'generated').glob('*.tex'))})
    (R/'BUILD_VALIDATION.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k not in ('source_hashes','preservation')},indent=2))


def render():
    response_tex()
    for _ in range(3):
        compile_one('main.tex'); labels('main','r43-main-labels.aux')
        compile_one('electronic_companion.tex'); labels('electronic_companion','r43-ec-labels.aux')
    for _ in range(2): compile_one(str(R/'RESPONSE_TO_REFEREES.tex'))
    print('Local draft rendered; full build validation has not been asserted.')


if __name__=='__main__':
    if len(sys.argv)!=2 or sys.argv[1] not in ('prepare','build','render'):
        raise SystemExit('Usage: build.py prepare|build|render')
    globals()[sys.argv[1]]()
