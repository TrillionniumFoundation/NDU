"""Seal the complete R65 package, then optionally publish branch-local readers."""
from pathlib import Path
import argparse,hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parent

def included(p):return p.is_file() and p!=R/'PACKAGE_MANIFEST.json' and not any(x in ('.build','__pycache__') for x in p.relative_to(R).parts)
def seal(repo=None):
    files={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(R.rglob('*')) if included(p)}
    m={'schema':'NDU-R65-payload-manifest-v1','scope':'Every delivered file except this manifest and disposable build caches','files':files}
    (R/'PACKAGE_MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n')
    if repo is not None:
        repo=repo.resolve();rel=R.relative_to(repo).as_posix()
        for name in ('main','electronic_companion','RESPONSE_TO_REFEREES'):
            for ext in ('.tex','.pdf'):shutil.copy2(R/(name+ext),repo/(name+ext))
        build=json.loads((R/'results/r65/BUILD65.json').read_text())
        (repo/'README.md').write_text('# NDU — current Operations Research revision R65\n\n'
            f'The complete revision is [`{rel}/`]({rel}/).\n\n'
            f'[Main paper]({rel}/main.pdf) · [Electronic companion]({rel}/electronic_companion.pdf) · '
            f'[Response to the R64 referee]({rel}/RESPONSE_TO_REFEREES.pdf) · [Code, data and reproduction]({rel}/README.md)\n\n'
            f"The article has {build['main']['pages']} PDF pages ({build['main']['excluding_references']} excluding references), "
            f"the companion {build['electronic_companion']['pages']}, and the response {build['RESPONSE_TO_REFEREES']['pages']}.\n\n"
            'R65 binds the complete external request and verifies the exact transferred-policy lower formula. It reproduces both R64 referee witnesses, adds request and metadata adversaries, and replays all frozen proofs without changing their original outcomes. All principal results, original failures, historical records and prior branches are preserved.\n\n'
            'The revision descends from the reviewed author commit; the R64 report is pinned as evidence, not merged as a scientific parent. Exact-head execution receipts verify the delivered artifacts and checks, not editorial acceptance.\n')
        (repo/'CURRENT_REVISION.json').write_text(json.dumps({'revision':'R65','path':rel,'main':'main.pdf','companion':'electronic_companion.pdf','response':'RESPONSE_TO_REFEREES.pdf','manifest':rel+'/PACKAGE_MANIFEST.json','governing_review_commit':'3fa2fc1db4257a15af4b3a437c54b306a4589e63'},indent=2)+'\n')
        with zipfile.ZipFile(repo/'CURRENT_SUBMISSION.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for p in sorted(R.rglob('*')):
                if included(p) or p==R/'PACKAGE_MANIFEST.json':z.write(p,'NDU_R65/'+p.relative_to(R).as_posix())
    print('Sealed',len(files),'files')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path);a=p.parse_args();seal(a.repo)
