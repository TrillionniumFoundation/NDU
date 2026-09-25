"""Publish runnable code/data with exact predecessor readers and dependencies."""
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
import hashlib,json
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
def run():
    old=ROOT/'revisions/or-r53-catalog-safe-certificates-20260926/CODE_AND_DATA.zip'
    if not old.exists():old=ROOT/'NDU/NDU/revisions/or-r53-catalog-safe-certificates-20260926/CODE_AND_DATA.zip'
    if not old.exists():raise RuntimeError('Missing inherited runnable code/data archive')
    files={}
    with ZipFile(old) as z:
        for info in z.infolist():
            if info.is_dir():continue
            path=Path(info.filename)
            if path.is_absolute() or '..' in path.parts:raise RuntimeError('Unsafe inherited archive path')
            files[info.filename]=z.read(info)
    for name in ['main.tex','electronic_companion.tex','README.md','NDU_OR_submission_checklist.md']:
        files[name]=(ROOT/name).read_bytes()
    for path in sorted(R.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts or 'transport' in path.parts:continue
        if path.name in ['CODE_AND_DATA.zip','CODE_AND_DATA_SHA256.json','SOURCE_ARCHIVE_SHA256.json']:continue
        if path.suffix in ['.pyc','.phase']:continue
        if path.suffix=='.pdf' and 'predecessor' not in path.parts:continue
        files[str(path.relative_to(ROOT))]=path.read_bytes()
    review='reviews/operation_research_referee_report_r53_independent_harsh_2026-09-26.md'
    if (ROOT/review).exists():files[review]=(ROOT/review).read_bytes()
    dest=R/'CODE_AND_DATA.zip'
    with ZipFile(dest,'w',ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(files.items()):
            info=ZipInfo(name,(2026,9,26,0,0,0));info.compress_type=ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,data)
    result=dict(sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),bytes=dest.stat().st_size,entries=len(files),scope='Complete runnable inherited code/data dependencies plus R54 source/evidence and current root-reader predecessors. Older complete reader PDFs remain in Git.')
    (R/'CODE_AND_DATA_SHA256.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':run()
