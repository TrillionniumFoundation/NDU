"""Predeclared synthetic scaling and accuracy path; every run is retained."""
from pathlib import Path
from fractions import Fraction as F
import time,json,platform,sys,tracemalloc
from augmentation import Model,recover,encode
from check_augmentation import check
R=Path(__file__).resolve().parents[1]

def run():
    configs=[(8,8,1,0,0,1000),(8,8,2,0,0,1000),(32,16,4,0,0,1000),(64,16,4,F(1,8),0,1000),(128,32,8,0,0,1000),(256,32,8,F(1,8),0,1000),(128,64,8,F(1,8),0,1000),(64,32,4,F(1,8),F(1,100),1000),(64,32,4,F(1,8),F(1,20),1000),(32,16,2,0,0,10),(32,16,2,0,0,1000),(32,16,2,0,0,100000)]
    rows=[]; (R/'results/certificates').mkdir(parents=True,exist_ok=True)
    for n,(k,den,m,delta,slope,ed) in enumerate(configs):
        b=tuple(F(1,5)+F(3*j,5*(k-1)) for j in range(k))
        weights=[1+(j%5) for j in range(k)]; p=tuple(F(w,sum(weights)) for w in weights)
        g=tuple(F(1+j%9,3) for j in range(k))
        model=Model.make(b,p,g); a=tuple(F(i,den) for i in range(den+1)); rho=tuple(slope*x for x in a)
        B=F(4,5)*sum(x*y for x,y in zip(b,p))
        tracemalloc.start(); t=time.perf_counter()
        record=recover(model,a,rho,m,B,delta,F(1,ed))
        seconds=time.perf_counter()-t; _,peak=tracemalloc.get_traced_memory(); tracemalloc.stop()
        encoded=encode(record); (R/f'results/certificates/scaling_{n:02}.json').write_text(json.dumps(encoded,indent=2)+'\n')
        t=time.perf_counter(); ck=check(encoded); checksecs=time.perf_counter()-t
        row=dict(case=n,k=k,N=den+1,m=m,delta=str(delta),charge_slope=str(slope),epsilon=str(F(1,ed)),oracle_calls=record['oracle_calls'],union_size=ck['union_size'],max_dp_bits=record['max_dp_bits'],seconds=seconds,checker_seconds=checksecs,peak_bytes=peak,original_lower=str(record['original_lower']),original_upper=str(record['original_upper']),original_interval_width=str(record['original_upper']-record['original_lower']),augmented_value=str(record['augmented_policy']['value']),price_error=str(record['price_error']),charge_excess=str(record['charge_excess']),mesh_error=str((model.r+sum(w*gamma*cap for w,gamma,cap in zip(p,g,b))+m*slope)/den),exact_promise_residual='0',exact_positive_risk_violation='0',independent_check=True)
        rows.append(row); print(n,k,den+1,m,round(seconds,3),record['oracle_calls'],flush=True)
    out=dict(status='PASS',family='synthetic distinct caps, deterministic weights and heterogeneous gamma',timing='single tracemalloc-instrumented run per row; checker timed separately',platform=platform.platform(),python=sys.version,rows=rows)
    (R/'results/scaling.json').write_text(json.dumps(out,indent=2)+'\n')
    return out

if __name__=='__main__': run()
