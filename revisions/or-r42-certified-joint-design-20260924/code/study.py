"""Exact synthetic parameter paths; machine-dependent timing is separate."""
from __future__ import annotations
import csv,json,platform,sys,time
from pathlib import Path
from fractions import Fraction as F
from unified import Model,certified_grid,solve_catalog
from faces import solve_continuous
from verify import encode
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'results'
def save(name,rows):
    (OUT/(name+'.json')).write_text(json.dumps(rows,default=encode,indent=2)+'\n')
    with (OUT/(name+'.csv')).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]); w.writeheader()
        for row in rows:
            w.writerow({k:json.dumps(v,default=encode) if isinstance(v,(tuple,list,dict)) else str(v) for k,v in row.items()})
def run():
    OUT.mkdir(exist_ok=True)
    (OUT/'environment.json').write_text(json.dumps({'python':sys.version,'platform':platform.platform(),'processor':platform.processor(),'arithmetic':'fractions.Fraction','repetitions':1,'timing_scope':'single solve, no import or PDF build; exact reference implementation'},indent=2)+'\n')
    equal=Model.make(['1/4','1/2','3/4'],['1/3']*3,[1,1,1]); gap=[]
    for B in (F(1,8),F(1,4),F(1,3),F(3,8),F(5,12),F(11,24),F(23,48),F(1,2)):
        row={'B':B}
        for name,delta,det in [('expected',F(1),False),('pathwise',F(0),False),('deterministic',F(0),True)]:
            start=time.perf_counter(); ans=solve_continuous(equal,2,B,delta,deterministic=det)
            row[name]=ans['net_value']; row[name+'_book']=ans['codebook']; row[name+'_seconds']=time.perf_counter()-start
        row['expected_pathwise_gap']=row['expected']-row['pathwise']; row['pathwise_deterministic_gap']=row['pathwise']-row['deterministic']
        row['transport_sufficient_lower']=max(F(0),F(11,96)-F(11,4)*(F(1,2)-B))
        assert row['expected_pathwise_gap']>=row['transport_sufficient_lower'] and row['pathwise_deterministic_gap']>=0
        gap.append(row); print('gap',B,row['expected_pathwise_gap'],row['pathwise_deterministic_gap'],flush=True)
    save('promise_gap',gap)
    off=Model.make(['1/4','1/2','3/4'],['7/20','3/5','1/20'],[1,1,1]); paths=[]
    for B in (F(1,3),F(3,8),F(2,5),F(17,40)):
        for delta in (F(0),F(1,16),F(1,8),F(1)):
            for beta,eta in [(F(0),F(0)),(F(1,50),F(1,200))]:
                start=time.perf_counter(); ans=solve_continuous(off,2,B,delta,price=(0,beta,eta)); elapsed=time.perf_counter()-start
                paths.append(dict(B=B,delta=delta,beta=beta,eta=eta,net=ans['net_value'],codebook=ans['codebook'],targets=ans['allocation'].targets,intermediate=ans['allocation'].intermediate,lotteries=ans['allocation'].lotteries,seconds=elapsed,counts=ans['counts']))
        print('joint path B',B,flush=True)
    save('joint_paths',paths)
    price=lambda c:F(1,50)*c+F(1,200); B,delta=F(2,5),F(1,16)
    exact=solve_continuous(off,2,B,delta,price=(0,F(1,50),F(1,200))); meshes=[]
    for den in (8,16,32,64,128):
        start=time.perf_counter(); ans=certified_grid(off,2,B,delta,den,price,F(1,50)); elapsed=time.perf_counter()-start
        assert ans['continuous_lower']<=exact['net_value']<=ans['continuous_upper']
        meshes.append(dict(N=den+1,h=F(1,den),B=B,delta=delta,codebook=ans['codebook'],grid_value=ans['net_value'],continuous_value=exact['net_value'],actual_gap=exact['net_value']-ans['net_value'],certified_gap=ans['certified_error'],books=ans['books_certified'],seconds=elapsed))
        print('mesh',den,meshes[-1]['actual_gap'],flush=True)
    save('mesh_convergence',meshes); timing=[]
    for k,den in [(8,16),(8,32),(8,64),(32,16),(32,32),(32,64),(128,16),(128,32)]:
        caps=[F(1,4)+F(j+1,2*(k+2)) for j in range(k)]; model=Model.make(caps,[F(1,k)]*k,[1+j%4 for j in range(k)])
        B=F(3,4)*sum(p*b for p,b in zip(model.probabilities,caps)); catalog=[F(i,den) for i in range(den+1)]
        start=time.perf_counter(); ans=solve_catalog(model,catalog,[price(c) for c in catalog],2,B,F(1,16)); elapsed=time.perf_counter()-start
        timing.append(dict(k=k,N=den+1,m=2,B=B,delta=F(1,16),books=ans['books_certified'],seconds=elapsed,net_value=ans['net_value'],codebook=ans['codebook']))
        print('timing',k,den,elapsed,flush=True)
    save('new_algorithm_scaling',timing)
    return {'gap_cases':len(gap),'joint_cases':len(paths),'mesh_cases':len(meshes),'scaling_cases':len(timing)}
if __name__=='__main__': print(run(),flush=True)
