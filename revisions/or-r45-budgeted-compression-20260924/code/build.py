"""Prepare, compile and audit the R45 scientific reader package.

In a Git checkout, prepare must precede a scientific-source commit and build.
The build manifest names that commit; publication commits the resulting PDFs.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,subprocess,re,json,hashlib,shutil,platform
from assemble import ROOT,R,BASE,BRANCH,run as assemble,expand
B=ROOT/'.build/ndu-r45'; B.mkdir(parents=True,exist_ok=True)
PERMITTED={'main.tex','electronic_companion.tex','main.pdf','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def run(cmd,**kwargs):return subprocess.run(cmd,cwd=ROOT,check=True,**kwargs)
def preservation():
    result=dict(base_review_commit=BASE,new_branch=BRANCH,full_git_tree_checked=False)
    if (ROOT/'.git').exists():
        assert git('branch','--show-current')==BRANCH,'Wrong publication branch'
        inherited=set(git('ls-tree','-r','--name-only',BASE).splitlines())
        changed=set(git('diff','--name-only',BASE,'--').splitlines())
        unexpected=(changed&inherited)-PERMITTED
        assert not unexpected,('Historical paths changed',sorted(unexpected))
        result.update(full_git_tree_checked=True,inherited_tracked_paths=len(inherited),
            inherited_paths_unchanged=len(inherited)-len(PERMITTED&inherited),replaced_root_paths=sorted(changed&PERMITTED))
        for name in PERMITTED:
            expected=subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT)
            assert (R/'predecessor'/name).read_bytes()==expected,'Bad predecessor snapshot '+name
    else:result['local_scope']='Downloaded immutable predecessor plus R44 reader overlay; full Git-tree audit is performed by the publication workflow.'
    # Check preservation of formal statements in the actual current readers.
    old=''
    for name in ['main.tex','electronic_companion.tex']:
        for p in re.findall(r'\\input\{([^}]+)\}',(R/'predecessor'/name).read_text()):old+=expand(p)
    new=expand('main.tex')+expand('electronic_companion.tex')
    formal=lambda s:set(re.findall(r'\\label\{((?:thm|theorem|prop|lemma|lem|cor)[^}]+)\}',s))
    before,after=formal(old),formal(new)
    assert before<=after,('Missing formal labels',before-after)
    result.update(inherited_mathematical_labels=sorted(before),new_mathematical_labels=sorted(after-before),
        all_inherited_mathematical_labels_in_current_readers=True,
        predecessor_hashes={p.name:sha(p) for p in (R/'predecessor').glob('*') if p.is_file()})
    (R/'PRESERVATION_MANIFEST.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

def escape(t):
    table={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
    return ''.join(table.get(c,c) for c in t)
def inline(t):
    out=[]
    for p in re.split(r'(`[^`]+`|\*\*[^*]+\*\*)',t):
        if p.startswith('`') and p.endswith('`'):
            raw=p[1:-1];out.append(r'\nolinkurl{'+raw+'}' if ' ' not in raw else r'\texttt{'+escape(raw)+'}')
        elif p.startswith('**') and p.endswith('**'):out.append(r'\textbf{'+escape(p[2:-2])+'}')
        else:out.append(escape(p))
    return ''.join(out)
def response():
    body=[]
    for line in (R/'RESPONSE_TO_REFEREES.md').read_text().splitlines():
        if line.startswith('# '):body.append(r'\section*{'+escape(line[2:])+'}')
        elif line.startswith('## '):body.append(r'\subsection*{'+escape(line[3:])+'}')
        else:body.append(inline(line)+'\n')
    text=r'''\documentclass[11pt,letterpaper]{article}
\usepackage[margin=1in]{geometry}\usepackage[T1]{fontenc}
\usepackage{newtxtext,newtxmath,setspace,xurl}\usepackage[hidelinks]{hyperref}
\setstretch{1.12}\setlength{\emergencystretch}{4em}
\hypersetup{pdftitle={Response to the R44 Operations Research Referee Report},pdfauthor={Anonymous}}
\begin{document}
'''+ '\n'.join(body)+'\n\\end{document}\n'
    (R/'RESPONSE_TO_REFEREES.tex').write_text(text)

def prepare():
    assemble()
    for script in ['tests.py','study.py','extended.py','inherited.py','tables.py']:
        run([sys.executable,str(R/'code'/script)])
    response();preservation()
    shutil.copy2(R/'README.md',ROOT/'README.md')
    shutil.copy2(R/'SUBMISSION_CHECKLIST.md',ROOT/'NDU_OR_submission_checklist.md')
    print('Prepared scientific sources, executed evidence, response and preservation audit.')

def compile_one(path):
    name=Path(path).stem
    with (B/(name+'-console.log')).open('w') as out:
        run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error','-recorder',
             '-output-directory='+str(B),str(path)],stdout=out,stderr=subprocess.STDOUT)
def labels(name,dst):
    lines=(B/(name+'.aux')).read_text().splitlines()
    (ROOT/dst).write_text('\\relax\n'+'\n'.join(l for l in lines if l.startswith('\\newlabel'))+'\n')
def pages(p):
    s=subprocess.check_output(['pdfinfo',str(p)],text=True)
    return int(re.search(r'Pages:\s+(\d+)',s).group(1))

def build():
    response()
    for _ in range(4):
        compile_one('main.tex');labels('main','r45-main-labels.aux')
        compile_one('electronic_companion.tex');labels('electronic_companion','r45-ec-labels.aux')
    for _ in range(2):compile_one(R/'RESPONSE_TO_REFEREES.tex')
    warnings={}
    for n in ['main','electronic_companion','RESPONSE_TO_REFEREES']:
        text=(B/(n+'.log')).read_text(errors='replace')
        bad=[l for l in text.splitlines() if any(q in l for q in ['undefined','Overfull \\hbox','Overfull \\vbox','multiply defined','Label(s) may have changed'])]
        if bad:warnings[n]=bad
    assert not warnings,warnings
    aux=(B/'main.aux').read_text()
    rp=[int(re.search(r'\\newlabel\{refs-'+key+r'\}\{\{[^}]*\}\{(\d+)\}',aux).group(1)) for key in ['start','end']]
    mp,ep=pages(B/'main.pdf'),pages(B/'electronic_companion.pdf');nonref=mp-(rp[1]-rp[0]+1)
    assert nonref<=40 and ep<=mp,(mp,ep,nonref)
    words=len((R/'ABSTRACT.txt').read_text().split());assert words<=200
    intro=(R/'introduction.tex').read_text();assert '$' not in intro and '\\[' not in intro
    dependencies=set()
    for n in ['main','electronic_companion','RESPONSE_TO_REFEREES']:
        for line in (B/(n+'.fls')).read_text().splitlines():
            if not line.startswith('INPUT '):continue
            p=Path(line[6:]);p=p if p.is_absolute() else ROOT/p;p=p.resolve()
            if ROOT in p.parents and p.is_file() and p.suffix in ['.tex','.sty','.cls','.bib']:dependencies.add(p)
    dependencies.update((R/'code').glob('*.py'));dependencies.add(R/'RESPONSE_TO_REFEREES.md')
    source_commit='local-downloaded-source-worktree';clean=False
    if (ROOT/'.git').exists():
        paths=[str(p.relative_to(ROOT)) for p in sorted(dependencies)]
        changed=git('diff','--name-only','HEAD','--',*paths)
        untracked=git('ls-files','--others','--exclude-standard','--',*paths)
        assert not changed and not untracked,('Commit scientific sources before build',changed,untracked)
        source_commit=git('rev-parse','HEAD');clean=True
    for n in ['tests','comparison','target_net','scaling','continuous','inexact','inherited']:
        assert json.loads((R/'results'/(n+'.json')).read_text())['status']=='PASS'
    for n in ['main.pdf','electronic_companion.pdf']:shutil.copy2(B/n,ROOT/n)
    shutil.copy2(B/'RESPONSE_TO_REFEREES.pdf',R/'RESPONSE_TO_REFEREES.pdf')
    audit=preservation()
    import scipy,sympy
    record=dict(status='PASS',utc=datetime.now(timezone.utc).isoformat(),branch=BRANCH,base_review_commit=BASE,
        source_commit=source_commit,scientific_source_clean=clean,main_pages=mp,main_nonreference_pages=nonref,
        companion_pages=ep,response_pages=pages(R/'RESPONSE_TO_REFEREES.pdf'),abstract_words=words,
        undefined_references=0,overfull_boxes=0,duplicate_labels=0,
        python=sys.version,scipy=scipy.__version__,sympy=sympy.__version__,platform=platform.platform(),
        tex=subprocess.check_output(['pdflatex','--version'],text=True).splitlines()[0],
        complete_reader_and_code_inputs={str(p.relative_to(ROOT)):sha(p) for p in sorted(dependencies)},
        outputs={n:sha(ROOT/n) for n in ['main.pdf','electronic_companion.pdf']},
        response_sha256=sha(R/'RESPONSE_TO_REFEREES.pdf'),
        evidence={p.name:sha(p) for p in sorted((R/'results').glob('*.json'))},preservation=audit)
    (R/'BUILD_VALIDATION.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if k not in ['complete_reader_and_code_inputs','preservation','evidence']},indent=2))

if __name__=='__main__':
    if len(sys.argv)!=2 or sys.argv[1] not in ['prepare','build']:raise SystemExit('Usage: build.py prepare|build')
    globals()[sys.argv[1]]()
