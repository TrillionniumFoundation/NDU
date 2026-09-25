"""Boundary, robustness, application, and inherited evidence revalidation."""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations
from dataclasses import asdict
import sys,json,gzip,hashlib,time,runpy
from completion import *
from check_completion import check
from check_pooling import check as old_check
from box_solver import exhaustive_joint,fixed_allocate
R=Path(__file__).resolve().parents[1];OLD=ROOT/'revisions/or-r49-dispersion-certificates-20260925'

def run():
    cases=[
      (Instance.make([F(0)],[F(1)],[F(0)],[F(0)],1,0),(F(0),F(1,2),F(1)),F(0)),
      (Instance.make([F(1,3),F(4,5)],[F(2,5),F(3,5)],[F(0),F(0)],[F(2,5),F(1)],1,0),(F(1,10),F(1,5),F(2,5),F(3,5),F(1)),F(3,10)),
      (Instance.make([F(1,3),F(4,5)],[F(2,5),F(3,5)],[F(3),F(0)],[F(2,5),F(4,5)],2,2),(F(1,10),F(1,5),F(2,5),F(3,5),F(1)),F(46,75)),
      (Instance.make([F(1,2)]*3,[F(1,4),F(1,4),F(1,2)],[F(0),F(2),F(5)],[F(1,2),F(3,4),F(1)]),(F(0),F(1,4),F(1,2),F(3,4),F(1)),F(1,2))]
    boundary=price=0
    for D,a,B in cases:
        rho=tuple(F(i%3,50) for i in range(len(a)))
        for m in range(1,len(a)+1):
            z=solve(D,a,rho,B,m,price_steps=3);ref=exhaustive_joint(D,a,rho,B,m)
            assert z['gap']==0 and z['lower_bound']==ref['value'];check(encode(z));boundary+=1
            for p in range(m+1):
                for lam in [F(-2),F(0),F(3,2),F(3)]:
                    ans=priced_prefix(D,a,rho,B,m,p,lam,tables=True);vals=[]
                    for s in range(max(1,p),m+1):
                        for ids in combinations(range(len(a)),s):
                            c=tuple(a[i] for i in ids)
                            if not set(range(p))<=set(ids) or c[0]>B or c[0]>min(D.caps):continue
                            val=lam*B+sum(w*branch_support(D,j,c,c[0],D.caps[j],lam)[0] for j,w in enumerate(D.weights))-sum(rho[i] for i in ids);vals.append(val)
                    assert (ans is None and not vals) or ans['upper']==max(vals);price+=1
    # Derived capacity-reservation example, not a fitted operational dataset.
    D=Instance.make([F(3,10),F(11,20),F(4,5)],[F(1,4),F(1,2),F(1,4)],[F(0),F(2),F(7)],[F(2,5),F(13,20),F(19,20)],2,2)
    a=tuple(F(i,5) for i in range(6));rho=tuple(F(i,100) for i in range(6));B=D.cap_total*F(9,10)
    z=solve(D,a,rho,B,3,price_steps=3);assert z['gap']==0 and z['lower_bound']==exhaustive_joint(D,a,rho,B,3)['value']
    p=z['policy'];gross=sum(w*(sum(prob*2*(x*x/2+x*(1-x)) for x,prob in law)-gam*y*y/2) for w,law,gam,y in zip(D.weights,p['lotteries'],D.gamma,p['intermediate']))
    assert gross==p['gross'];verified=check(encode(z));(R/'results/application.json').write_text(json.dumps(encode(dict(interpretation='Synthetic stochastic capacity reservation; independent uniform-demand integration, no calibration',certificate=z,verified=verified)),indent=2)+'\n')
    # Perturbation jump and affected-mass inequality, with every other input fixed.
    a=(F(0),F(1,2));rho=(F(0),F(0));B=F(1,4);gamma=F(2)
    lo=Instance.make([B],[F(1)],[gamma],[F(49,100)]);hi=Instance.make([B],[F(1)],[gamma],[F(51,100)])
    low=solve(lo,a,rho,B,2,price_steps=2);high=solve(hi,a,rho,B,2,price_steps=2)
    assert low['lower_bound']==-gamma/32 and high['lower_bound']==F(7,16)
    assert high['lower_bound']-low['lower_bound']<=hi.reward(F(1))+gamma*B*B/2
    # Recheck every inherited certificate without modifying its source or result.
    start=time.perf_counter();hist=json.loads((OLD/'results/study.json').read_text())['cases'];checked=[]
    for row in hist:
        path=OLD/row['certificate'];data=path.read_bytes();assert hashlib.sha256(data).hexdigest()==row['certificate_sha256']
        result=old_check(json.loads(gzip.decompress(data)));checked.append(dict(id=row['id'],sha256=row['certificate_sha256'],check=result))
    out=dict(status='PASS',boundary_joint=boundary,boundary_price=price,uniform_demand_integral='PASS',threshold_jump='PASS',inherited_certificates=len(checked),inherited_check_seconds=time.perf_counter()-start,cases=checked)
    (R/'results/additional_checks.json').write_text(json.dumps(out,indent=2)+'\n')
    # R49 test suite writes only to this isolated new directory.
    target=R/'results/inherited_suite';(target/'results').mkdir(parents=True,exist_ok=True)
    suite=runpy.run_path(str(OLD/'code/tests.py'));suite['run'].__globals__['R']=target;suite['run']()
    print({k:v for k,v in out.items() if k!='cases'},flush=True)
if __name__=='__main__':run()
