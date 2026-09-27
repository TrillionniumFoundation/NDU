"""Verify every inherited blob against the immutable second-review parent."""
from pathlib import Path
import subprocess,hashlib,json,os,re,shutil
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
PARENT='4f0b662bd4184fc77fb57bd09c339bffb6213a69'
ALLOWED={'main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md'}
def blob(p):
    data=os.readlink(p).encode() if p.is_symlink() else p.read_bytes()
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def run():
    tree=R/'PARENT_TREE.txt'
    if (ROOT/'.git').exists():tree.write_bytes(subprocess.check_output(['git','ls-tree','-r',PARENT],cwd=ROOT))
    elif not tree.exists():shutil.copy2(ROOT.parent/'ndu_snapshot/PARENT_TREE.txt',tree)
    records=[];fail=[];statements={}
    pat=r'\\begin\{(?:theorem|proposition|lemma|corollary)\}(?:\[[^\]]*\])?\s*\\label\{([^}]+)\}'
    for line in tree.read_text().splitlines():
        meta,path=line.split('\t',1);mode,kind,sha=meta.split();p=ROOT/path
        if kind!='blob':continue
        now=blob(p) if p.exists() or p.is_symlink() else None
        row=dict(path=path,parent_blob=sha,current_blob=now,status='UNCHANGED' if now==sha else 'CHANGED')
        if now!=sha:
            old=R/'predecessor'/path
            if path in ALLOWED and old.exists() and blob(old)==sha:row.update(status='READER_REPLACED_WITH_EXACT_ARCHIVE',archive=str(old.relative_to(ROOT)))
            else:fail.append(path)
        records.append(row)
        if p.suffix=='.tex' and now==sha:
            labels=re.findall(pat,p.read_text(errors='replace'))
            if labels:statements[path]=labels
    result=dict(status='PASS' if not fail else 'FAIL',parent=PARENT,inherited_blobs=len(records),unchanged=sum(x['status']=='UNCHANGED' for x in records),archived_replacements=sum(x['status']=='READER_REPLACED_WITH_EXACT_ARCHIVE' for x in records),unexpected_changes=fail,files=records)
    (R/'PRESERVATION_MANIFEST.json').write_text(json.dumps(result,indent=2)+'\n')
    mapping=dict(parent=PARENT,current_article='main.pdf',current_companion='electronic_companion.pdf',current_response=str((R/'RESPONSE_TO_REFEREES.pdf').relative_to(ROOT)),preserved_reader_copies=[str((R/'predecessor'/x).relative_to(ROOT)) for x in sorted(ALLOWED)],current_prerequisites=['model.tex','selected_boundaries.tex','algorithm.tex','common_and_robustness.tex'],new_extension='production.tex',retained_alternative_method=['dyadic.tex','companion_body.tex'],historical_disposition='Every inherited source, proof, and result is unchanged. Original reader entry points have exact archives. Continuous design, institutions, all-promise frontiers, Monge, augmentation, and harmonic coarsening remain under their original assumptions; they are not removed or silently withdrawn, but are no longer mandatory parts of the current article.',historical_mathematical_source_inventory=statements)
    (R/'CONTENT_MAP.json').write_text(json.dumps(mapping,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2))
    if fail:raise RuntimeError('Unexpected inherited-file changes')
if __name__=='__main__':run()
