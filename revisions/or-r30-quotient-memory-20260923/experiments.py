#!/usr/bin/env python3
"""Reproducible R30 comparisons; each case/method uses a fresh worker process.

Three repetitions per worker; median/min/max are retained, not best-run timing.
Peak RSS is an absolute process high-water mark including imported libraries;
it is not a claim of allocator-level incremental algorithm memory.
"""
from __future__ import annotations
import argparse, json, os, platform, random, resource, statistics, subprocess, sys, time
from pathlib import Path
from fractions import Fraction as F
R=Path(__file__).resolve().parent
OLD=R.parent/'or-r29-price-state-20260923'
sys.path.insert(0,str(OLD))

def enc(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,list):return [enc(y) for y in x]
    if isinstance(x,dict):return {k:enc(v) for k,v in x.items()}
    return x

def binary(T,seed=13,stress=False):
    rng=random.Random(seed); groups=[[0]]+[list(range(2*t-1,2*t+1)) for t in range(1,T)]
    n=2*T-1;rows=[]
    for t,group in enumerate(groups):
        for v in group:
            rows.append(dict(t=t,cell=t,r=F(2*v+3,n+3) if stress else F(rng.randrange(4,35),10),
                q=F(1) if stress else F(rng.randrange(8,19),10),a=F(1),lo=F(0),hi=F(1),
                cap=F(T-t) if stress else F(2*(T-t),5)+F(1+rng.randrange(6),20),
                edges=[] if t==T-1 else [[j,F(1,2)] for j in groups[t+1]]))
    return enc(dict(name=f'{"slack" if stress else "binary"}-T{T}-s{seed}',beta=F(1),promise=F(2*T,5),nodes=rows))

def late_renewal(T,S=4):
    beta=F(19,20);groups=[[0]];idx=1
    for t in range(1,T):groups.append(list(range(idx,idx+S)));idx+=S
    rows=[];ann=[sum(beta**j for j in range(T-t)) for t in range(T)]
    for t,group in enumerate(groups):
        for z,v in enumerate(group):
            r=F(2) if t==T-1 else (F(0) if t==T-2 else F(v%3,2))
            cap=F(1,2)+F(z,10) if t==T-2 else ann[t]
            rows.append(dict(t=t,cell=t,r=r,q=F(1),a=F(1),lo=F(0),hi=F(1),cap=cap,
                edges=[] if t==T-1 else [[j,F(1,S)] for j in groups[t+1]]))
    return enc(dict(name=f'late-renewal-T{T}-S{S}',beta=beta,promise=ann[0]/4,nodes=rows,
          design=dict(T=T,S=S,active_cap_location='penultimate date',base_feasible_tier='1/4')))

def measured(fn,reps):
    vals=[];ans=None
    for _ in range(reps):
        t=time.perf_counter();ans=fn();vals.append(time.perf_counter()-t)
    return ans,dict(median=statistics.median(vals),minimum=min(vals),maximum=max(vals),runs=vals)

def worker(spec):
    # Import numerical libraries in every worker, so RSS scopes are comparable.
    import numpy, scipy
    # Only internally generated, trusted rational benchmark inputs are processed here.
    if hasattr(sys, 'set_int_max_str_digits'): sys.set_int_max_str_digits(0)
    from quotient import compile_graph,execute,minimal_machine
    from baselines import laminar,qp,promise_grid
    from verify import check as full_check
    from policy_audit import check_policy
    check = check_policy if spec.get('policy_audit_only',False) else full_check
    if spec['family']=='late-renewal':
        raw=late_renewal(spec['T'],spec.get('S',4))
    elif spec['family']=='markov':
        from research import instance
        raw=instance(spec['T'],spec['S'],spec.get('seed',131))
    elif spec['family']=='bounded':
        from research import instance
        raw=instance(spec['T'],spec['S'],spec.get('seed',131))
        raw['name']='bounded-'+raw['name'];raw['promise']='1/4'
        for i,v in enumerate(raw['nodes']):v['cap']=str(F(8+i%5,10))
        raw['design']['fixed_shared_table']=None
        raw['design']['cap_rule']='(8 + vertex_index mod 5)/10; feasible all-zero lower envelope'
    else:raw=binary(spec['T'],spec.get('seed',13),spec['family']=='slack')
    method=spec['method']; reps=spec.get('repetitions',3)
    out={'specification':spec,'name':raw['name'],'public_nodes':len(raw['nodes'])}
    if method=='quotient':
        c,pre=measured(lambda:compile_graph(raw),reps)
        b=F(raw['promise']);eta,inv=measured(lambda:c.curves[0].inverse(b),reps)
        cert,exe=measured(lambda:execute(c,b,eta=eta),spec.get('certificate_repetitions',reps))
        report,audit=measured(lambda:check({'instance':raw,'certificate':cert}),spec.get('audit_repetitions',reps))
        machine,mt=measured(lambda:minimal_machine(raw,cert),reps)
        curve=c.curves[0];promises=[curve.low+(curve.high-curve.low)*F(i,100) for i in range(101)]
        _,batch=measured(lambda:[curve.inverse(z) for z in promises],reps)
        out.update(value=cert['value'],statistics=c.statistics(),construction_seconds=pre,
            root_inversion_seconds=inv,certificate_seconds=exe,audit_seconds=audit,
            audit=report,reachable_pairs=cert['statistics']['reachable_price_pairs'],
            machine_symbols=machine['minimal_symbols'],machine_seconds=mt,batch_101_inversions_seconds=batch)
        (R/'results'/'certificates').mkdir(exist_ok=True)
        (R/'results'/'certificates'/f"{raw['name']}.json").write_text(json.dumps({'instance':raw,'certificate':cert},separators=(',',':'))+'\n')
    else:
        call=(lambda:laminar(raw)) if method=='laminar' else ((lambda:qp(raw)) if method=='qp' else (lambda:promise_grid(raw,spec['resolution'])))
        ans,timing=measured(call,reps);out.update(result=ans,total_seconds=timing)
    out.update(peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               python=sys.version,numpy=numpy.__version__,scipy=scipy.__version__,platform=platform.platform())
    return out

def suite(which,rerun=False):
    specs=[]
    if which=='comparisons':
        for T in [4,6,8,10]:
            for seed in [13,29]:
                for method in ['quotient','laminar','qp']:
                    specs.append(dict(family='binary',T=T,seed=seed,method=method,repetitions=3))
        for T in [4,8,12]:
            for seed in [13,29]:
                specs.append(dict(family='binary',T=T,seed=seed,method='quotient',repetitions=3))
                for Q in [10,20,40,80]:
                    specs.append(dict(family='binary',T=T,seed=seed,method='grid',resolution=Q,repetitions=3))
    elif which=='scaling':
        for T in [16,32,64]:
            specs.append(dict(family='markov',T=T,S=4,seed=131,method='quotient',repetitions=3,certificate_repetitions=1,audit_repetitions=1,policy_audit_only=True))
        specs.append(dict(family='bounded',T=128,S=4,seed=131,method='quotient',repetitions=3,certificate_repetitions=1,audit_repetitions=1,policy_audit_only=True))
        for T in [64,128,256,512]:
            specs.append(dict(family='late-renewal',T=T,S=4,method='quotient',repetitions=3,certificate_repetitions=1,audit_repetitions=1,policy_audit_only=True))
        for T in [32,64,128,256]:
            specs.append(dict(family='slack',T=T,seed=13,method='quotient',repetitions=3,certificate_repetitions=1,audit_repetitions=1,policy_audit_only=True))
    else:raise ValueError(which)
    if rerun:
        for cached in (R/'results').glob(f'{which}-[0-9][0-9][0-9].json'): cached.unlink()
    records=[]; dest=R/'results'/f'{which}.json'
    for i,spec in enumerate(specs):
        tag=f'{which}-{i:03d}';output=R/'results'/f'{tag}.json'
        if output.exists() and json.loads(output.read_text())['specification']==spec:ans=json.loads(output.read_text())
        else:
            env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
            cmd=[sys.executable,__file__,'--worker',json.dumps(spec),'--output',str(output)]
            result=subprocess.run(cmd,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=900)
            if result.returncode:
                (R/'results'/f'{tag}.error.txt').write_text(result.stderr)
                raise RuntimeError(f'{spec}: {result.stderr}')
            ans=json.loads(output.read_text())
        records.append(ans);dest.write_text(json.dumps({'records':records,'repetitions':3,'clock':'perf_counter',
          'rss_scope':'absolute fresh-worker process high-water mark, imports included',
          'timing_scope':'method phases after common numerical-library imports; no parallel workers'},indent=2)+'\n')
        print(i+1,len(specs),spec,'completed; N='+str(ans['public_nodes']),flush=True)
    return records

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--worker');p.add_argument('--output');p.add_argument('--suite',choices=['comparisons','scaling']);p.add_argument('--rerun',action='store_true')
    a=p.parse_args()
    if a.worker:
        Path(a.output).write_text(json.dumps(worker(json.loads(a.worker)),indent=2)+'\n')
    else:suite(a.suite,a.rerun)
