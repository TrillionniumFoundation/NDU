"""Produce a self-contained code/data archive without fonts or build caches."""
from pathlib import Path
import zipfile,hashlib,json
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
def run():
    # All historical Python modules preserve path-based imports without selection.
    files=set(ROOT.glob('revisions/**/*.py'))
    files|={p for p in R.rglob('*') if p.is_file() and 'predecessor' not in p.parts and 'transport' not in p.parts and p.suffix.lower() not in ['.pdf','.zip','.pyc','.aux','.log','.out','.fls'] and '__pycache__' not in p.parts}
    files|={ROOT/'main.tex',ROOT/'electronic_companion.tex',ROOT/'README.md'}
    # Historical study data provide immutable paired inputs and expected requests.
    for p in ROOT.glob('revisions/or-r49*/results/*.json'):files.add(p)
    for p in ROOT.glob('revisions/or-r48*/results/*.json'):files.add(p)
    files={p for p in files if p.exists() and p.name not in ['CODE_AND_DATA_SHA256.json']}
    dest=R/'CODE_AND_DATA.zip'
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(files):
            info=zipfile.ZipInfo(p.relative_to(ROOT).as_posix(),date_time=(2026,9,25,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,p.read_bytes())
    out=dict(path=str(dest.relative_to(ROOT)),files=len(files),bytes=dest.stat().st_size,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),scope='No font files, caches, compiled readers, or transport payloads are included. Exact historical Python imports and paired input records retain repository-relative paths.')
    (R/'CODE_AND_DATA_SHA256.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':run()
