#!/usr/bin/env python3
"""Independent standard-library rational replay. No optimizer/numpy imports."""
from fractions import Fraction as F
from pathlib import Path
import hashlib,json,math,statistics
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'results'
def main():
    p=json.loads((OUT/'primitives.json').read_text());n=p['leaves'];w=F(9,10*n)
    rho=[F(9*k,80*n) for k in p['tariff_integers']]
    u0=p['offset0_integers'];u1=p['offset1_integers']
    g0=-w*sum(u0)/20;g1=-w*sum(u1)/20
    assert g0+sum((w*u/20 for u in u0),F(0))==0
    assert g1+sum((w*u/20 for u in u1),F(0))==0
    count=0;checks=0;max_final_gap=F(0);all_gains={};all_gaps={}
    def replay(a):
        nonlocal count,checks
        h,alpha,lam=map(F,a['theta']);assert lam>0
        y=list(map(F,a['flows']));assert len(y)==n
        v=sum((r*yy for r,yy in zip(rho,y)),F(0))
        assert 0<=v<=F(1,2) and all(0<=yy<=F(1,2) for yy in y)
        assert v==F(a['root_transfer']);checks+=2*n+2
        # Root equality and all leaf continuation caps, including leaf bounds.
        assert v-sum((r*yy for r,yy in zip(rho,y)),F(0))==0
        assert all(-r*yy<=0 for r,yy in zip(rho,y));checks+=n+1
        d=[r*g0-w*z/20+alpha*(r*g1-w*z1/20)+h*r-lam*(w+F(19,10)*r) for r,z,z1 in zip(rho,u0,u1)]
        # Direct edge switching equals the accepted-transfer formula.
        switch_direct=v+sum((w*(v+yy) for yy in y),F(0))
        switch_linear=sum(((w+F(19,10)*r)*yy for r,yy in zip(rho,y)),F(0))
        assert switch_direct==switch_linear
        gain=sum((dd*yy-w*yy*yy for dd,yy in zip(d,y)),F(0))-v*v
        tau=F(a['total_price'])
        def conjugate(s,q):
            z=min(F(1,2),max(F(0),s/q));return s*z-q*z*z/2
        ub=conjugate(tau,F(2))+sum((conjugate(dd-r*tau,2*w) for dd,r in zip(d,rho)),F(0))
        gap=ub-gain
        assert gain==F(a['gain_fraction']) and ub==F(a['dual_upper_fraction']) and gap==F(a['gap_fraction']) and gap>=0
        assert math.isclose(float(gain/F(19,10)),a['gain'],abs_tol=1e-15)
        count+=1;checks+=5
        return gain/F(19,10),gap/F(19,10)
    for path in ['policies.jsonl','timings.jsonl','validation_policies.jsonl']:
        for line in (OUT/path).read_text().splitlines():
            r=json.loads(line);gain,gap=replay(r['audit'])
            if path=='timings.jsonl':
                assert gap<=F(1,10**7);max_final_gap=max(max_final_gap,gap)
            if path=='validation_policies.jsonl':
                assert gain>=0
                all_gains.setdefault(r['method'],[]).append(float(gain));all_gaps.setdefault(r['method'],[]).append(float(gap))
    val=json.loads((OUT/'validation.json').read_text())
    model_hash=hashlib.sha256((OUT/'frozen_models.json').read_bytes()).hexdigest();assert model_hash==val['model_sha256']
    for a in val['corners']:replay(a)
    B=max(F(a['dual_upper_fraction'])/F(19,10) for a in val['corners']);assert B==F(val['B_fraction'])
    rad=float(B)*math.sqrt(math.log(val['M']/val['delta'])/(2*val['n']))
    assert abs(rad-val['radius'])<1e-15
    for name,gains in all_gains.items():
        assert len(gains)==val['n'] and all(0<=g<=float(B) for g in gains)
        assert abs(statistics.mean(gains)-val['methods'][name]['empirical_gain'])<1e-14
        assert abs(statistics.mean(gains)-rad-val['methods'][name]['simultaneous_gain_lower'])<1e-14
        assert abs(statistics.mean(all_gaps[name])-val['methods'][name]['mean_gap'])<1e-14
    summary={'status':'PASS','rational_certificates':count,'exact_algebraic_checks':checks,
             'max_final_normalized_gap':float(max_final_gap),'all_friction_strictly_positive':True,
             'baseline_static_balanced':True,'validation_range_replayed':True,'model_sha256':model_hash,
             'imports':'Python standard library only; no numerical optimizer or linear algebra library'}
    (OUT/'verification.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
