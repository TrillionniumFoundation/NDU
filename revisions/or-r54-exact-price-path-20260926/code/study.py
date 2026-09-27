"""Execute every frozen case; do not delete or replace failures."""
from pathlib import Path
import argparse,json,os,subprocess,sys,time,hashlib,platform
from cases import generate
HERE=Path(__file__).resolve().parent;OUT=HERE.parent/'results'

def run(only=None):
    cases=generate();jobs=[]
    for c in cases:
        path=OUT/'inputs'/f"{c['id']}.json";path.parent.mkdir(exist_ok=True);path.write_text(json.dumps(c,indent=2)+'\n')
        for method in ('price','uniform','enumeration','classbox','mip'):
            if only and method!=only:continue
            if c['heterogeneous'] and method in ('uniform','classbox'):continue
            jobs.append((c,path,method))
    for c,path,method in jobs:
        name=c['id']+'--'+method;result=OUT/'runs'/f'{name}.json';phase=result.with_suffix('.phase')
        if result.exists():
            old=json.loads(result.read_text())
            if old.get('instance_sha256')!=c['instance_sha256']:raise RuntimeError('Case changed after execution')
            continue
        env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
        log=OUT/'logs'/f'{name}.log';log.parent.mkdir(exist_ok=True)
        with log.open('w') as stream:
            p=subprocess.Popen([sys.executable,str(HERE/'worker.py'),str(path),method],stdout=stream,stderr=subprocess.STDOUT,env=env)
            started=time.monotonic();last=None
            while p.poll() is None:
                if phase.exists():
                    try:last=json.loads(phase.read_text())
                    except json.JSONDecodeError:pass
                budget=70 if last and last['phase']=='verification' else 5.0 if last else 45
                elapsed=time.monotonic()-(last['time'] if last else started)
                if elapsed>budget:p.kill();p.wait();break
                time.sleep(.03)
        if not result.exists():
            result.parent.mkdir(exist_ok=True);result.write_text(json.dumps(dict(id=c['id'],method=method,status='PROCESS_LIMIT',instance_sha256=c['instance_sha256'],returncode=p.returncode,last_phase=last),indent=2)+'\n')
        elif p.returncode!=0:
            record=json.loads(result.read_text());record['process_returncode']=p.returncode;record['last_phase']=last
            result.write_text(json.dumps(record,indent=2)+'\n')
        print(name,json.loads(result.read_text()).get('status'),flush=True)
    ids={c['id'] for c in cases}
    rows=[x for p in sorted((OUT/'runs').glob('*.json')) if (x:=json.loads(p.read_text())).get('id') in ids]
    summary=dict(status='PASS' if all(x.get('status')!='ERROR' and x.get('verification_status') not in ('FAIL','TIME_LIMIT') for x in rows) else 'FAIL',
                 cases=len(cases),runs=len(rows),python=sys.version,platform=platform.platform(),records=rows)
    (OUT/'STUDY.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--only');args=p.parse_args();run(args.only)
