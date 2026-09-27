"""Hash a complete flat revision; optional root readers for its own branch."""
from pathlib import Path
import argparse,hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parent

def included(p):return p.is_file() and not any(x in ('.build','__pycache__') for x in p.relative_to(R).parts) and p != R/'PACKAGE_MANIFEST.json'
def seal(repo=None):
    files={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(R.rglob('*')) if included(p)}
    (R/'PACKAGE_MANIFEST.json').write_text(json.dumps({'schema':'NDU-R63-payload-manifest-v1','scope':'Every delivered file except this manifest and disposable build caches','files':files},indent=2)+'\n')
    if repo:
        for name in ('main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','RESPONSE_TO_REFEREES.tex','RESPONSE_TO_REFEREES.pdf'):
            shutil.copy2(R/name,repo/name)
        rel=R.relative_to(repo).as_posix()
        (repo/'README.md').write_text('# NDU — current Operations Research revision R63\n\n'
            f'The complete current revision is [`{rel}/`]({rel}/).\n\n'
            f'[Main paper]({rel}/main.pdf) · [Electronic companion]({rel}/electronic_companion.pdf) · '
            f'[Response to the R60 referee]({rel}/RESPONSE_TO_REFEREES.pdf) · '
            f'[Code/data and verification instructions]({rel}/README.md)\n\n'
            'The main reader has 28 PDF pages (26 excluding references), the companion 28, and the response 5. '
            'All prior scientific branches, reviewed readers, raw timing records and failure outcomes are preserved. '
            'This branch continues the author-only scientific history, not a reviewer-parent merge.\n')
        (repo/'CURRENT_REVISION.json').write_text(json.dumps({'revision':'R63','path':rel,'main':'main.pdf','companion':'electronic_companion.pdf','response':'RESPONSE_TO_REFEREES.pdf','manifest':rel+'/PACKAGE_MANIFEST.json'},indent=2)+'\n')
        with zipfile.ZipFile(repo/'CURRENT_SUBMISSION.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for p in sorted(R.rglob('*')):
                if included(p) or p.name=='PACKAGE_MANIFEST.json':z.write(p,'NDU_R63/'+str(p.relative_to(R)))
    print('Sealed',len(files),'files')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path);a=p.parse_args();seal(a.repo)
