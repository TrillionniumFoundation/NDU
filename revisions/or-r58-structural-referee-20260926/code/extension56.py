"""Disclosed post-primary exact-target and encoding stress experiments."""
from pathlib import Path
import json,datetime,hashlib,subprocess,sys,os,time
from cases56 import synthetic
from rational import write,digest
HERE=Path(__file__).resolve().parent;OUT=HERE.parent/'results'

def main():
    cases=[]
    for k,n,m in [(8,9,3),(24,17,4),(96,25,4)]:
        for seed in [5601,5602,5603]:
            for sec in [.5,2.0]:cases.append(dict(id=f'exact-k{k}-{seed}-t{sec:g}',family='exact_extension',spec=synthetic(k,n,m,seed),epsilon='0',seconds=sec,methods=['price','enumeration'],k=k,n=n,m=m,seed=seed))
    for bit in [8,16,32]:cases.append(dict(id=f'encoding-H2power{bit}',family='encoding_extension',spec=synthetic(6,7,2,5601,zero=True,H=2**bit),epsilon='0',seconds=2.0,methods=['lattice'],k=6,n=7,m=2,seed=5601,granularity_bits=bit))
    for c in cases:c['instance_sha256']=digest(c['spec'])
    protocol=dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Post-inspection study, not an unseen confirmatory sample. The primary positive-tolerance price runs stopped at the root; these zero-width reruns expose branching on the same models. Encoding stress explicitly tests the numerical state limit.',matched_targets=True,retain_failures=True,comparison_count=36,encoding_count=3,cases=[c['id'] for c in cases],primary_records_unchanged=True)
    write(HERE.parent/'EXTENSION_PROTOCOL.json',protocol);write(OUT/'EXTENDED_CASES.json',cases)
    source={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.glob('*.py')};write(OUT/'EXTENSION_SOURCE_MANIFEST.json',source)
    records=[];begin=time.perf_counter()
    for c in cases:
        ip=OUT/'inputs'/(c['id']+'.json');write(ip,c)
        for method in c['methods']:
            dest=OUT/'runs'/(c['id']+'--'+method+'.json')
            cp=subprocess.run([sys.executable,str(HERE/'worker56.py'),str(ip),method,str(dest)],capture_output=True,text=True,timeout=c['seconds']+35,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
            if cp.returncode or not dest.exists():write(dest,dict(id=c['id'],family=c['family'],method=method,instance_sha256=c['instance_sha256'],status='PROCESS_ERROR',stderr=cp.stderr,stdout=cp.stdout))
            records.append(json.loads(dest.read_text()));print(cp.stdout.strip(),flush=True)
    write(OUT/'EXTENSION_AUDIT.json',dict(expected_runs=39,retained_runs=len(records),seconds=time.perf_counter()-begin,source_hashes_unchanged=all(hashlib.sha256((HERE/n).read_bytes()).hexdigest()==h for n,h in source.items()),runs_sha256={z['id']+'--'+z['method']:hashlib.sha256((OUT/'runs'/(z['id']+'--'+z['method']+'.json')).read_bytes()).hexdigest() for z in records}))
    print('EXTENSION COMPLETE',len(records),flush=True)
if __name__=='__main__':main()
