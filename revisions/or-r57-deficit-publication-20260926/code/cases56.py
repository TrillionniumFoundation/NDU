from rational import F
from price_path import Model,spec_for
import random

def synthetic(k=8,n=9,m=3,seed=5601,hetero=True,charge='1/100',zero=False,cap_count=None,H=16):
    rng=random.Random(seed)
    choices=[F(rng.randrange(2,H),H) for _ in range(cap_count or k)]
    caps=[choices[j%len(choices)] for j in range(k)]
    weights=[F(1,k)]*k
    gamma=[F(0) if zero else F(rng.randrange(0,5),4) for _ in caps]
    ceiling=[min(F(1),b+F(rng.randrange(0,H//2+1),H)) for b in caps]
    rr=[F(rng.randrange(8,13),4) for _ in caps] if hetero else 2
    qq=[F(rng.randrange(1,5),4) for _ in caps] if hetero else 1
    d=Model.make(caps,weights,gamma,ceiling,rr,qq)
    a=tuple(F(i,n-1) for i in range(n));rho=tuple(F(charge)*rng.randrange(0,6) for _ in a)
    # Rational lattice target for zero service; nonzero cases remain exact input.
    B=F(int(d.cap_total*k*H*F(3,4)),k*H) if zero else d.cap_total*F(3,4)
    return spec_for(d,a,rho,B,m)
