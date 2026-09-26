"""Execute all declared R56 cases; retain failures and source binding."""
from pathlib import Path
import hashlib,json,os,platform,subprocess,sys,time
from cases56 import synthetic
from rational import write,digest
HERE=Path(__file__).resolve().parent;OUT=HERE.parent/'results'

def generate():
    cases=[]
    for family,(k,n,m) in zip(['common-small','heterogeneous-small','heterogeneous-medium','heterogeneous-large'],[(6,7,3),(8,9,3),(24,17,4),(96,25,4)]):
        for seed in [5601,5602,5603]:
            spec=synthetic(k,n,m,seed,hetero=family!='common-small')
            for sec in [.5,2.0]:cases.append(dict(id=f'{family}-{seed}-t{sec:g}',family=family,spec=spec,epsilon='1/20',seconds=sec,methods=['price','deficit','enumeration','direct-mip'],k=k,n=n,m=m,seed=seed))
    for seed in [5601,5602,5603]:
        for den in [50,100]:cases.append(dict(id=f'accuracy-{seed}-e{den}',family='accuracy',spec=synthetic(8,9,3,seed),epsilon=f'1/{den}',seconds=2.0,methods=['price','deficit','enumeration'],k=8,n=9,m=3,seed=seed))
    for H in [8,16,32]:
        for m in [2,4]:
            for seed in [5601,5602,5603]:cases.append(dict(id=f'lattice-H{H}-m{m}-{seed}',family='lattice',spec=synthetic(6,7,m,seed,zero=True,H=H),epsilon='0',seconds=2.0,methods=['lattice','enumeration'],k=6,n=7,m=m,seed=seed))
    for k,n,m in [(8,9,3),(24,17,4)]:
        for charge in ['0','1/100','1/10']:
            for seed in [5601,5602,5603]:cases.append(dict(id=f'screen-k{k}-c{charge.replace("/","_")}-{seed}',family='screening',spec=synthetic(k,n,m,seed,charge=charge),epsilon='1/100',seconds=2.0,methods=['price','screen'],k=k,n=n,m=m,seed=seed))
    for case in cases:case['instance_sha256']=digest(case['spec'])
    return cases

def main():
    OUT.mkdir(exist_ok=True);(OUT/'inputs').mkdir(exist_ok=True);(OUT/'runs').mkdir(exist_ok=True)
    cases=generate();write(OUT/'CASES.json',cases);source={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.glob('*.py')}
    manifest=OUT/'SOURCE_MANIFEST.json'
    if not manifest.exists():write(manifest,dict(source_hashes=source,protocol_sha256=hashlib.sha256((HERE.parent/'PROTOCOL.json').read_bytes()).hexdigest(),created_before_timed_execution=True,python=sys.version,platform=platform.platform(),native_threads=1))
    elif json.loads(manifest.read_text())['source_hashes']!=source:raise ValueError('Publication code changed: preserve old run separately before re-executing')
    expected=[];start=time.perf_counter()
    for case in cases:
        ip=OUT/'inputs'/(case['id']+'.json');write(ip,case)
        for method in case['methods']:
            name=case['id']+'--'+method;expected.append(name);dest=OUT/'runs'/(name+'.json')
            if dest.exists():
                if json.loads(dest.read_text()).get('instance_sha256')!=case['instance_sha256']:raise ValueError('Resume input mismatch')
                continue
            try:
                cp=subprocess.run([sys.executable,str(HERE/'worker56.py'),str(ip),method,str(dest)],capture_output=True,text=True,timeout=case['seconds']+30,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
                if cp.returncode or not dest.exists():write(dest,dict(id=case['id'],method=method,family=case['family'],instance_sha256=case['instance_sha256'],status='PROCESS_ERROR',returncode=cp.returncode,stdout=cp.stdout,stderr=cp.stderr))
                print(cp.stdout.strip() or name+' PROCESS_ERROR',flush=True)
            except subprocess.TimeoutExpired:
                previous=json.loads(dest.read_text()) if dest.exists() else None
                write(dest,dict(id=case['id'],method=method,family=case['family'],instance_sha256=case['instance_sha256'],status='PARENT_TIMEOUT',last_record=previous))
    records=[json.loads((OUT/'runs'/(name+'.json')).read_text()) for name in expected];counts={};ver={}
    for row in records:counts[row['status']]=counts.get(row['status'],0)+1;v=row.get('verification_status','not_applicable');ver[v]=ver.get(v,0)+1
    write(OUT/'EXECUTION_AUDIT.json',dict(expected_runs=len(expected),retained_runs=len(records),all_planned_records_present=True,run_ids=expected,status_counts=counts,verification_counts=ver,execution_seconds=time.perf_counter()-start,source_hashes_unchanged=all(hashlib.sha256((HERE/name).read_bytes()).hexdigest()==h for name,h in source.items()),evidence_scope='New source-frozen R57 execution, not the absent R55 archive',runs_sha256={name:hashlib.sha256((OUT/'runs'/(name+'.json')).read_bytes()).hexdigest() for name in expected}))
    print('COMPLETE',len(records),counts,ver,flush=True)
if __name__=='__main__':main()
