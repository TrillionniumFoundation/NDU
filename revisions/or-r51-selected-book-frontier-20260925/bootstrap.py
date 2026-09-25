"""Validate the transport and reconstruct only the isolated R51 revision."""
from pathlib import Path
import base64,hashlib,json,lzma,subprocess
R=Path(__file__).resolve().parent; ROOT=R.parents[1]
BRANCH='revision/ndu-operations-research-r51-selected-book-frontier-20260925'
BASE='4f0b662bd4184fc77fb57bd09c339bffb6213a69'
FIRST='2ac1490e5a4149f8c7e154407fbe6fa6208979db'
ROOT_WRITES={'main.tex','electronic_companion.tex'}
ARCHIVE={'main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md'}
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def main():
    assert git('branch','--show-current').decode().strip()==BRANCH
    subprocess.run(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT,check=True)
    manifest=json.loads((R/'transport/MANIFEST.json').read_text())
    encoded=''.join((R/'transport'/f'part-{i}.b64').read_text().strip() for i in range(1,manifest['parts']+1))
    payload=base64.b64decode(encoded,validate=True)
    assert len(payload)==manifest['compressed_bytes'] and hashlib.sha256(payload).hexdigest()==manifest['compressed_sha256']
    raw=lzma.decompress(payload);assert len(raw)==manifest['uncompressed_bytes']
    files=json.loads(raw);assert set(files)==set(manifest['files'])
    for name,text in files.items():
        path=(ROOT/name).resolve()
        assert path.is_relative_to(R) or name in ROOT_WRITES,name
        assert isinstance(text,str) and hashlib.sha256(text.encode()).hexdigest()==manifest['files'][name],name
    # Derive the preservation manifest from the actual immutable Git tree.
    original={}
    for item in git('ls-tree','-r','-z',BASE).split(b'\0'):
        if not item:continue
        meta,name=item.split(b'\t',1);mode,kind,blob=meta.split();assert kind==b'blob'
        name=name.decode();path=ROOT/name
        data=git('show',f'{BASE}:{name}') if name in ARCHIVE else path.read_bytes()
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==blob.decode(),name
        original[name]=hashlib.sha256(data).hexdigest()
        if name in ARCHIVE:
            archive=R/'predecessor'/name;archive.parent.mkdir(parents=True,exist_ok=True);archive.write_bytes(data)
    assert len(original)==2660,len(original)
    (R/'INHERITED_SHA256.json').write_text(json.dumps(original,indent=2,sort_keys=True)+'\n')
    for name,text in files.items():
        path=ROOT/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
    assert hashlib.sha256((R/'PROTOCOL.json').read_bytes()).hexdigest()==manifest['protocol_sha256']
    (R/'sources').mkdir(exist_ok=True)
    report=git('show',FIRST+':reviews/operation_research_referee_report_r49_independent_harsh_2026-09-25.md')
    (R/'sources/first-r49-report.md').write_bytes(report)
    for name in ['results','results/certificates','generated']:(R/name).mkdir(parents=True,exist_ok=True)
    (R/'TRANSPORT_MANIFEST.json').write_text(json.dumps({'status':'PASS','baseline':BASE,'source_files':manifest['files'],'compressed_sha256':manifest['compressed_sha256'],'inherited_files':len(original),'first_report_sha256':hashlib.sha256(report).hexdigest()},indent=2)+'\n')
    print({'status':'PASS','source_files':len(files),'preserved_baseline_files':len(original)})
if __name__=='__main__':main()
