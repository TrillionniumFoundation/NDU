"""Execute R53 plus the inherited regression without changing old evidence."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
def run():
    (R/'results').mkdir(exist_ok=True)
    old=ROOT/'revisions/or-r52-resource-path-20260925/results/tests.json'
    saved=old.read_bytes() if old.exists() else None
    try:
        job=subprocess.run([sys.executable,'revisions/or-r52-resource-path-20260925/code/tests.py'],cwd=ROOT,capture_output=True,text=True)
        (R/'results/BASELINE_REGRESSION.log').write_text(job.stdout+job.stderr)
        if job.returncode:raise RuntimeError('Inherited regression failed')
        record=json.loads(old.read_text());record['inherited_result_sha256']=None if saved is None else hashlib.sha256(saved).hexdigest()
        (R/'results/BASELINE_REGRESSION.json').write_text(json.dumps(record,indent=2)+'\n')
    finally:
        if saved is None:old.unlink(missing_ok=True)
        else:old.write_bytes(saved)
    subprocess.run([sys.executable,str(R/'code/validate.py')],cwd=ROOT,check=True)
    subprocess.run([sys.executable,str(R/'code/tables.py')],cwd=ROOT,check=True)
if __name__=='__main__':run()
