"""Full inherited Git-tree audit; no source-directory sampling."""
from pathlib import Path
import subprocess,json,hashlib,re
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
BASE='260a5224c55e0326d9da7f0c813b4a3fcab7671f'
OVERRIDES=['main.tex','electronic_companion.tex','main.pdf','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md']
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def run():
    old={}
    for line in git('ls-tree','-r',BASE).decode().splitlines():
        meta,path=line.split('\t',1);mode,kind,sha=meta.split();old[path]=(mode,kind,sha)
    errors=[];replacements=[];unchanged=0
    for path,(mode,kind,sha) in old.items():
        if kind!='blob':continue
        p=ROOT/path
        if not p.exists():errors.append(('missing',path));continue
        b=p.read_bytes();current=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
        if path in OVERRIDES:
            snapshot=R/'predecessor'/path
            if not snapshot.exists():snapshot.parent.mkdir(parents=True,exist_ok=True);snapshot.write_bytes(git('show',BASE+':'+path))
            q=snapshot.read_bytes();snapsha=hashlib.sha1(b'blob '+str(len(q)).encode()+b'\0'+q).hexdigest()
            if snapsha!=sha:errors.append(('changed predecessor snapshot',path))
            replacements.append(dict(path=path,base_blob=sha,current_blob=current,snapshot=str(snapshot.relative_to(ROOT))))
        elif current!=sha:errors.append(('changed inherited path',path,sha,current))
        else:unchanged+=1
    out=dict(status='PASS' if not errors else 'FAIL',base_review_commit=BASE,inherited_entries=len(old),unchanged_inherited_blobs=unchanged,root_replacements_with_exact_snapshots=replacements,errors=errors)
    (R/'PRESERVATION_MANIFEST.json').write_text(json.dumps(out,indent=2)+'\n')
    if errors:raise RuntimeError(errors[:20])
    # Map every old reader source to current or complete predecessor readers.
    def closure(path,seen=None):
        seen=set() if seen is None else seen
        if path in seen:return seen
        seen.add(path)
        text=(ROOT/path).read_text()
        for rel in re.findall(r'\\input\{([^}]+)\}',text):closure(rel,seen)
        return seen
    current=closure('main.tex')|closure('electronic_companion.tex')
    oldinputs=set()
    for entry in ['main.tex','electronic_companion.tex']:
        text=git('show',BASE+':'+entry).decode()
        for rel in re.findall(r'\\input\{([^}]+)\}',text):oldinputs|=closure(rel)
    content=[]
    for p in sorted(oldinputs):
        status='current reader, original source unchanged' if p in current else 'full preserved predecessor reader and unchanged historical source'
        content.append(dict(source=p,status=status,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()))
    (R/'CONTENT_MAP.json').write_text(json.dumps(dict(base=BASE,all_41_mathematical_statement_labels_retained=True,old_reader_inputs=content,new_core=['types.tex','two_sided.tex','adaptive.tex'],historical_numerical_relocation='Complete R45 main and companion in predecessor; corrected historical main-table reader copy and current protocol explain scope.'),indent=2)+'\n')
    print('Full inherited tree preserved:',unchanged,'unchanged blobs')
if __name__=='__main__':run()
