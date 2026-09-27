"""Create a runnable code/data archive, retaining all inherited dependencies."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED,ZipInfo
import hashlib,json
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
def run():
    old=ROOT/'revisions/or-r52-resource-path-20260925/CODE_AND_DATA.zip'
    output=R/'CODE_AND_DATA.zip';files={}
    with ZipFile(old) as z:
        for name in z.namelist():
            if not name.endswith('/'):files[name]=z.read(name)
    for name in ['main.tex','electronic_companion.tex','README.md','NDU_OR_submission_checklist.md']:
        files[name]=(ROOT/name).read_bytes()
    for path in sorted(R.rglob('*')):
        if not path.is_file() or any(x in path.parts for x in ['predecessor','__pycache__']):continue
        if path.name in ['CODE_AND_DATA.zip','CODE_AND_DATA_SHA256.json','SOURCE_PACKAGE.zip','SOURCE_PACKAGE.b64']:continue
        if path.suffix=='.pdf':continue
        files[str(path.relative_to(ROOT))]=path.read_bytes()
    with ZipFile(output,'w',ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(files.items()):
            info=ZipInfo(name,date_time=(2026,9,26,0,0,0));info.compress_type=ZIP_DEFLATED;info.external_attr=0o644<<16
            z.writestr(info,data)
    record=dict(sha256=hashlib.sha256(output.read_bytes()).hexdigest(),bytes=output.stat().st_size,entries=len(files))
    (R/'CODE_AND_DATA_SHA256.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
if __name__=='__main__':run()
