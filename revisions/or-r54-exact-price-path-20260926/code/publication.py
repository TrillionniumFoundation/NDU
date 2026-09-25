"""Run the entire declared R54 evidence package; retain all resource failures."""
from pathlib import Path
import datetime,hashlib,json,os,platform,subprocess,sys
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];OUT=R/'results'
FILES=['tests.py','study.py','anytime.py','screening_study.py','sharp_screening.py','hardness.py','production_example.py','tables.py']
def hashes():
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((R/'code').glob('*.py'))}
def run():
    if sys.flags.optimize:raise RuntimeError('Reproduction requires enabled regression assertions')
    OUT.mkdir(exist_ok=True);(OUT/'inputs').mkdir(exist_ok=True);(OUT/'runs').mkdir(exist_ok=True);(OUT/'logs').mkdir(exist_ok=True)
    manifest=OUT/'SOURCE_MANIFEST.json';code=hashes()
    if manifest.exists():
        previous=json.loads(manifest.read_text())
        if previous.get('code_sha256')!=code:raise RuntimeError('Recorded results use a different code version; use a separate fresh copy for reruns')
    else:manifest.write_text(json.dumps(dict(code_sha256=code,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=sys.version,platform=platform.platform()),indent=2)+'\n')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
    for name in FILES:
        print('RUN '+name,flush=True)
        subprocess.run([sys.executable,str(R/'code'/name)],cwd=ROOT,env=env,check=True)
    subprocess.run([sys.executable,str(R/'code/audit.py')],cwd=ROOT,env=env,check=True)
if __name__=='__main__':run()
