"""Seeded synthetic experiments; exact bounds separated from numerical checks."""
from pathlib import Path
from fractions import Fraction as F
from dataclasses import asdict,is_dataclass
from random import Random
import json,time,platform,sys,resource,tracemalloc,importlib.util
from math import comb
from decomposition import Model,solve_prefix
from checker import check
from frontier import audit
R=Path(__file__).resolve().parents[1]
OUT=R/'results'; OUT.mkdir(exist_ok=True)
(OUT/'certificates').mkdir(exist_ok=True)

def encode(x):
    if isinstance(x,F): return str(x)
    if is_dataclass(x): return encode(asdict(x))
    if isinstance(x,dict): return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)): return [encode(v) for v in x]
    return x

def save(name,x): (OUT/name).write_text(json.dumps(encode(x),indent=2)+'\n')

def scale():
    rows=[]
    designs=[(8,17,2,F(0),1,F(1,50)),(8,17,4,F(1,16),1,F(1,50)),
        (8,33,4,F(1),1,F(1,50)),(32,17,2,F(0),1,F(1,50)),
        (32,33,4,F(1,16),1,F(1,50)),(128,33,4,F(1,16),1,F(1,50)),
        (128,33,8,F(1,16),1,F(1,50)),(256,33,8,F(1),1,F(1,50)),
        (32,33,4,F(1,16),0,F(0)),(32,33,4,F(1,16),4,F(1,50)),
        (32,33,4,F(1,16),1,F(1,5)),(32,65,4,F(1,16),1,F(1,50))]
    for index,(k,n,m,delta,scale,slope) in enumerate(designs):
        caps=[F(1,4)+F(j+1,2*(k+2)) for j in range(k)]
        model=Model.make(caps,[F(1,k)]*k,[scale*(1+j%4) for j in range(k)])
        B=F(3,4)*sum(p*b for p,b in zip(model.probabilities,caps))
        a=tuple(F(i,n-1) for i in range(n)); charges=tuple(F(1,200)+slope*x for x in a)
        start=time.perf_counter(); tracemalloc.start()
        result=solve_prefix(model,a,charges,m,B,delta,iterations=6,max_nodes=40)
        seconds=time.perf_counter()-start; _,peak=tracemalloc.get_traced_memory(); tracemalloc.stop()
        cs=time.perf_counter(); verified=check(model,a,charges,m,B,delta,result)
        checker_seconds=time.perf_counter()-cs
        K=model.r+sum(p*g*b for p,g,b in zip(model.probabilities,model.gamma,caps))+m*slope
        entry=dict(case=index,k=k,N=n,m=m,delta=delta,gamma_scale=scale,charge_slope=slope,
            B=B,lower=result['lower'],catalog_upper=result['upper'],
            optimization_gap=result['upper']-result['lower'],mesh_error=K/(n-1),
            continuous_upper=result['upper']+K/(n-1),exact_catalog=result['exact'],
            expanded_nodes=result['expanded_nodes'],books_evaluated=result['books_evaluated'],
            all_subset_count=sum(comb(n,s) for s in range(1,m+1)),
            dp_prices=len(result['prices']),dp_bits=result['max_dp_bits'],
            seconds=seconds,checker_seconds=checker_seconds,peak_traced_bytes=peak,
            process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            checker=verified)
        rows.append(entry)
        save('certificates/case_%02d.json'%index,dict(model=asdict(model),catalog=a,charges=charges,
            budget=m,promise=B,delta=delta,result=result))
        save('scaling.json',rows)
        print('scale',index,k,n,m,entry['exact_catalog'],float(entry['optimization_gap']),round(seconds,3),flush=True)
    save('environment.json',dict(python=sys.version,platform=platform.platform(),processor=platform.processor(),
        implementation=platform.python_implementation(),note='Single measured runs with tracemalloc active; checker time is separate.'))
    return rows


def continuous():
    rng=Random(430925); rows=[]
    # Cross risk regimes and sizes; m=2 at k>=3 intentionally exposes the frontier.
    configs=[(k,m,d) for k in (1,2,3,4) for m in (1,2) for d in (F(0),F(1,8),F(1))]
    configs.append((5,1,F(1,8)))
    scip_available=importlib.util.find_spec('pyscipopt') is not None
    if scip_available: from scip_check import solve as independent
    for i,(k,m,delta) in enumerate(configs):
        caps=sorted(F(rng.randrange(2,10),10) for _ in range(k))
        w=[rng.randrange(1,4) for _ in caps]; model=Model.make(caps,[F(x,sum(w)) for x in w],[1+j%3 for j in range(k)])
        B=F(4,5)*sum(p*b for p,b in zip(model.probabilities,caps))
        price=(F(0),F(1,50),F(1,200))
        ans=audit(model,m,B,delta,price,system_limit=5000)
        row=dict(case=i,k=k,m=m,delta=delta,model=asdict(model),promise=B,price=price,face=ans)
        if scip_available and k<=2 and m==2:
            ext=independent(model,m,B,delta,price,seconds=20)
            row['independent_minlp']=ext
            if ans['status']=='exact':
                v=float(ans['value']); tol=2e-5
                row['comparison_passed']=ext['lower']-tol<=v<=ext['upper']+tol
                assert row['comparison_passed'],(i,ans,ext)
        else:
            row['independent_minlp']=dict(status='not_run',reason='dependency_unavailable' if not scip_available else 'outside_declared_six_case_crosscheck')
        rows.append(row); save('continuous_frontier.json',rows)
        print('faces',i,k,m,ans['status'],ans['systems'],round(ans['seconds'],3),flush=True)
    return rows

if __name__=='__main__':
    if len(sys.argv)==1: scale(); continuous()
    elif sys.argv[1]=='scale': scale()
    elif sys.argv[1]=='continuous': continuous()
    else: raise SystemExit('study.py [scale|continuous]')
