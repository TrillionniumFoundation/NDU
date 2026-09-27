"""Zero-target-width reruns and complete per-oracle checkpoint records."""
from pathlib import Path
import json,subprocess,sys,os,time
from cases import generate
R=Path(__file__).resolve().parents[1];OUT=R/'results'
def run():
    selected=[c for c in generate() if c['id'].startswith('historical-') or c['id'] in ['catalog-33','catalog-65','budget-8','budget-12']]
    if len(selected)!=10:
        # Historical identifiers in the fixed generator are hard-<seed>.
        selected=[c for c in generate() if c['id'].startswith('hard-') or c['id'] in ['catalog-33','catalog-65','budget-8','budget-12']]
    if len(selected)!=10:raise RuntimeError('Incomplete anytime case selection')
    rows=[]
    for original in selected:
        case=dict(original,id='anytime-'+original['id'],epsilon='0')
        inp=OUT/'inputs'/(case['id']+'.json');inp.write_text(json.dumps(case,indent=2)+'\n')
        target=OUT/'runs'/(case['id']+'--price.json');phase=target.with_suffix('.phase')
        if not target.exists():
            env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
            with (OUT/'logs'/(case['id']+'.log')).open('w') as log:
                job=subprocess.Popen([sys.executable,str(R/'code/worker.py'),str(inp),'price'],stdout=log,stderr=subprocess.STDOUT,env=env)
                start=time.monotonic();last=None
                while job.poll() is None:
                    if phase.exists():
                        try:last=json.loads(phase.read_text())
                        except json.JSONDecodeError:pass
                    allowance=70 if last and last['phase']=='verification' else 5 if last else 45
                    if time.monotonic()-(last['time'] if last else start)>allowance:job.kill();job.wait();break
                    time.sleep(.03)
            if not target.exists():target.write_text(json.dumps(dict(id=case['id'],status='PROCESS_LIMIT',returncode=job.returncode)))
        row=json.loads(target.read_text());rows.append(row)
        print(case['id'],row['status'],row.get('gap'),flush=True)
    result=dict(status='PASS' if all(x.get('verification_status')=='PASS' for x in rows) else 'FAIL',cases=len(rows),records=rows)
    (OUT/'ANYTIME.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':run()
