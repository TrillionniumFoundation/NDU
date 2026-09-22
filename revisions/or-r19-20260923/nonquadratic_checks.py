#!/usr/bin/env python3
"""Exact rational quartic-coupling checks, including switching and box boundaries."""
from fractions import Fraction as F
from pathlib import Path
import json
R=Path(__file__).resolve().parent/'results'
def run():
    rows=[]
    for i in range(64):
        d=F(2+i%4,3);u=F(1+i%3,2);v=F(1,8);lam=F(1+i%5,16)
        xs=[-F(1,2),-F(1,4),-v,F(0),F(1,3),F(1,2)][i%6]
        def psi(w):return w*w/2+w**4/4
        def gp(w):return w+w**3
        sg=F(1 if xs+v>0 else -1 if xs+v<0 else 0)
        b=d*xs+u*gp(u*xs)+lam*sg;eta=gp(u*xs)+F((i%9)-4,7)
        def base(x):return d*x*x/2+lam*(abs(x+v)-abs(v))-b*x+eta*u*x
        def val(x):return b*x-d*x*x/2-lam*(abs(x+v)-abs(v))-psi(u*x)
        w=(b-eta*u)/d+v
        soft=max(F(0),w-lam/d) if w>=0 else min(F(0),w+lam/d)
        xe=max(-F(1,2),min(F(1,2),soft-v))
        # Actual deployed y is rounded before any response error is calculated.
        y=F(round(xe*1000),1000);delta=base(y)-base(xe);assert delta>=0
        res=eta-gp(u*y);bound=2*delta+res*res*u*u/(2*(d/2+u*u))
        regret=val(xs)-val(y);assert 0<=regret<=bound
        L=u*u/d;LP=1+3*(u/2)**2
        pricebound=L*(1+LP*L)*(eta-gp(u*xs))**2/2
        assert val(xs)-val(xe)<=pricebound
        H=lambda p,x:b*x-d*x*x/2-lam*(abs(x+v)-abs(v))-p*u*x
        ep=gp(u*xs)
        identity=H(ep,xs)-H(eta,xe)+(u*xe)*(ep-eta)+psi(u*xe)-psi(u*xs)-ep*(u*xe-u*xs)
        assert identity==val(xs)-val(xe)
        rows.append({'case':i,'x_star':str(xs),'x_response':str(xe),'implemented':str(y),'base_gap':str(delta),'regret':str(regret),'inexact_bound':str(bound),'identity_exact':True})
    R.mkdir(exist_ok=True);(R/'nonquadratic_checks.json').write_text(json.dumps({'status':'PASS','cases':64,'arithmetic':'fractions.Fraction only; no numerical optimizer','rows':rows},indent=2)+'\n')
if __name__=='__main__':run()
