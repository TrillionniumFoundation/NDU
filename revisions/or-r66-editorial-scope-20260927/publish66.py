"""Seal the full R66 revision and optionally update branch-local reader entry points."""
from pathlib import Path
import argparse,hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parent

def included(p):return p.is_file() and p!=R/'PACKAGE_MANIFEST.json' and not any(x in ('.build','__pycache__') for x in p.relative_to(R).parts)
def seal(repo=None):
    files={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(R.rglob('*')) if included(p)}
    (R/'PACKAGE_MANIFEST.json').write_text(json.dumps(dict(schema='NDU-R66-payload-manifest-v1',
        scope='Every delivered file except this manifest and disposable build caches',files=files),indent=2)+'\n')
    if repo is not None:
        repo=repo.resolve();rel=R.relative_to(repo).as_posix()
        for name in ('main','electronic_companion','RESPONSE_TO_REFEREES'):
            for ext in ('.tex','.pdf'):shutil.copy2(R/(name+ext),repo/(name+ext))
        build=json.loads((R/'results/r66/BUILD66.json').read_text())
        (repo/'README.md').write_text('# NDU — current Operations Research revision R66\n\n'
            f'The complete revision is [`{rel}/`]({rel}/).\n\n'
            f'[Main paper]({rel}/main.pdf) · [Electronic companion]({rel}/electronic_companion.pdf) · '
            f'[Response to the R65 referee]({rel}/RESPONSE_TO_REFEREES.pdf) · [Code, data and reproduction]({rel}/README.md)\n\n'
            f"The article has {build['main']['pages']} PDF pages ({build['main']['excluding_references']} excluding references), "
            f"the companion {build['electronic_companion']['pages']}, and the response {build['RESPONSE_TO_REFEREES']['pages']}.\n\n"
            'The R65 referee recommends Accept with nonblocking editorial comments. R66 clarifies receipt scope while retaining every accepted theorem, proof, table, checker, request schema and historical outcome. This does not assert a formal journal decision.\n\n'
            f'[All comment dispositions]({rel}/EDITORIAL_SCOPE66.md) · [Complete reader diff]({rel}/EDITORIAL_DIFF66.patch) · '
            f'[Pinned provenance]({rel}/PROVENANCE66.json)\n\n'
            'All 7,080 R65 payload entries remain preserved. The revision descends from the exact R65 author commit; '
            'the governing report is pinned as evidence, not merged as a scientific parent. Exact-head receipts verify delivered artifacts and executed checks, not editorial acceptance.\n')
        (repo/'CURRENT_REVISION.json').write_text(json.dumps(dict(revision='R66',path=rel,main='main.pdf',
            companion='electronic_companion.pdf',response='RESPONSE_TO_REFEREES.pdf',manifest=rel+'/PACKAGE_MANIFEST.json',
            scientific_parent='6bc195dcdbc93d1a796b1388639c053c0a11ddd0',governing_review_commit='0382789afc96be20497063930602d5a6be96909a',
            scope='Editorial-only receipt clarification; accepted science and checker unchanged'),indent=2)+'\n')
        with zipfile.ZipFile(repo/'CURRENT_SUBMISSION.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for p in sorted(R.rglob('*')):
                if included(p) or p==R/'PACKAGE_MANIFEST.json':z.write(p,'NDU_R66/'+p.relative_to(R).as_posix())
    print('Sealed',len(files),'files')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path);a=p.parse_args();seal(a.repo)
