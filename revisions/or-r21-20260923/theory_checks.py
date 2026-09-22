"""Exact rational checks of nonsmooth/zero-curvature and regularization claims."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent

def run():
    n=0
    # q=0 on [-1,1] and Psi(u)=|u|: neither quadratic strong curvature nor
    # differentiable coupling is available. Fenchel components remain valid.
    for b,y,p,s,v in product([F(-3,2),F(0),F(5,3)],[F(-1),F(-1,3),F(0),F(3,4),F(1)],
                             [F(-1),F(-1,4),F(0),F(1)],[F(-2,3),F(0),F(2,3)],[F(-1,2),F(1,3)]):
        lam=F(2,3);r=b-p-s;upper=abs(r)-s*v+lam*abs(v)
        gain=b*y-abs(y)-lam*(abs(y+v)-abs(v))
        components=[abs(r)-r*y,abs(y)-p*y,lam*abs(y+v)-s*(y+v)]
        assert min(components)>=0 and sum(components)==upper-gain
        n+=1
    # x=(t,-t), 0<=t<=1; original objective may have zero curvature.
    reg=0
    for b,lam,q,eps in product([F(k,4) for k in range(-4,9)],[F(0),F(1,4),F(3,2)],
                               [F(0),F(1,4)],[F(1,100),F(1,10),F(1)]):
        def value(t,e=F(0)):return b*t-q*t*t/2-lam*(abs(t-F(1,2))-F(1,2))-e*t*t
        def optimum(e):
            candidates=[F(0),F(1,2),F(1)];d=q+2*e
            if d:
                candidates.extend([min(F(1,2),max(F(0),(b+lam)/d)), min(F(1),max(F(1,2),(b-lam)/d))])
            return max(candidates,key=lambda t:value(t,e))
        t=optimum(eps);star=optimum(F(0));loss=value(star)-value(t)
        assert 0<=loss<=eps*(1-t*t)
        reg+=1
    out={'status':'PASS','nonsmooth_zero_curvature_fenchel_identities':n,'regularization_bias_cases':reg,
         'interpretation':'Exact checks supplement, not replace, the proofs in the manuscript.'}
    (ROOT/'results/theory_checks.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':run()
