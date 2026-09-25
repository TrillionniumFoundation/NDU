"""Deterministic cross-formulation tests, independent witnesses and mutations."""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations
from copy import deepcopy
import sys,random,json,runpy,math
from completion import *
from check_completion import check
from box_solver import fixed_allocate,exhaustive_joint
R=Path(__file__).resolve().parents[1]
fixture=runpy.run_path(str(ROOT/'revisions/or-r49-dispersion-certificates-20260925/code/tests.py'))['fixture']


def dyadic(width,eta):
    count=1
    while width>eta:width/=2;count*=2
    return count


def run():
    counts=dict(fixed_book=0,mandatory_price=0,joint=0,intervals=0,dyadic=0,mutations=0)
    for seed in range(40):
        D,a,rho,B=fixture(51000+seed,2+seed%4,5+seed%2,seed%7==0);cmap=dict(zip(a,rho))
        if seed%4==0:B=D.cap_total
        if seed%11==0:B=F(0)
        for s in range(1,4):
            for book in combinations(a,s):
                if book[0]>min(D.caps) or book[0]>B:continue
                q=fixed_book(D,book,B,cmap);old=fixed_allocate(D,book,B,cmap)
                assert q['value']==old['value'],(seed,book,B,q,old)
                lam=q['allocation_price'];assert q['gross']==lam*B+sum(w*branch_support(D,j,book,book[0],D.caps[j],lam)[0] for j,w in enumerate(D.weights))
                counts['fixed_book']+=1
        for p in range(3):
            # All mandatory candidates here are feasible as an anchor at zero.
            for lam in [F(-3),F(-1,3),F(0),F(1),F(7,4),F(3)]:
                z=priced_prefix(D,a,rho,B,3,p,lam,tables=True);vals=[]
                for s in range(max(1,p),4):
                    for ids in combinations(range(len(a)),s):
                        if not set(range(p))<=set(ids):continue
                        book=tuple(a[i] for i in ids)
                        if book[0]>min(D.caps) or book[0]>B:continue
                        v=lam*B+sum(w*branch_support(D,j,book,book[0],D.caps[j],lam)[0] for j,w in enumerate(D.weights))-sum(rho[i] for i in ids)
                        vals.append(v)
                assert z['upper']==max(vals),(seed,p,lam,z['upper'],max(vals))
                counts['mandatory_price']+=1
        reference=exhaustive_joint(D,a,rho,B,3)['value']
        for steps in [0,2]:
            z=solve(D,a,rho,B,3,node_limit=10000,price_steps=steps)
            assert z['gap']==0 and z['lower_bound']==reference,(seed,steps,z['lower_bound'],reference)
            check(encode(z));counts['joint']+=1
        z=solve(D,a,rho,B,3,node_limit=1,price_steps=1)
        assert z['lower_bound']<=reference<=z['upper_bound'];check(encode(z));counts['intervals']+=1
    # Exact rational thresholds rather than floating log2 around powers of two.
    for w in [F(0),F(1,7),F(1,2),F(1)]:
        for eta in [F(1,3),F(1,4),F(1,8),F(2),F(1,9)]:
            count=dyadic(w,eta)
            assert w/count<=eta and (count==1 or w/F(count,2)>eta)
            assert count<2*max(F(1),w/eta) or count==1
            counts['dyadic']+=1
    assert dyadic(F(1),F(1,3))==4
    # Use a certificate with both internal nodes and price potentials.
    bases=[]
    for seed in range(30):
        D,a,rho,B=fixture(51500+seed,4,6,False)
        z=encode(solve(D,a,rho,B,3,node_limit=15,price_steps=2,screen=False));bases.append(z)
    base=max(bases,key=lambda z:len(z['nodes']));check(base)
    def reject(z,mut):
        q=deepcopy(z);mut(q)
        try:check(q)
        except (ValueError,KeyError,IndexError,TypeError,ZeroDivisionError):counts['mutations']+=1
        else:raise AssertionError('Accepted corrupted certificate')
    reject(base,lambda q:q.__setitem__('lower_bound',str(F(q['lower_bound'])+1)))
    reject(base,lambda q:q.__setitem__('upper_bound',str(F(q['upper_bound'])-1)))
    reject(base,lambda q:q.__setitem__('gap','-1'))
    reject(base,lambda q:q.__setitem__('budget',0))
    reject(base,lambda q:q.__setitem__('active',q['active'][1:]))
    reject(base,lambda q:q['policy']['targets'].__setitem__(0,'-1'))
    reject(base,lambda q:q['policy']['intermediate'].__setitem__(0,'-1'))
    reject(base,lambda q:q['policy']['lotteries'][0][0].__setitem__(1,'-1'))
    reject(base,lambda q:q['nodes'][0]['bound'].__setitem__('upper','-999'))
    reject(base,lambda q:q['screening'].__setitem__('gross_upper','-999'))
    reject(base,lambda q:q['nodes'].append(deepcopy(q['nodes'][-1])))
    split=next((i for i,z in enumerate(base['nodes']) if z['state']=='SPLIT'),None)
    if split is not None:
        reject(base,lambda q:q['nodes'][split]['children'].pop())
        reject(base,lambda q:q['nodes'][split].__setitem__('children',[0,0]))
    pricebase=next((z for z in bases if any(n.get('bound',{}).get('kind')=='price' for n in z['nodes'])),None)
    if pricebase:
        i=next(i for i,n in enumerate(pricebase['nodes']) if n.get('bound',{}).get('kind')=='price')
        reject(pricebase,lambda q:q['nodes'][i]['bound'].__setitem__('alpha',[]))
        reject(pricebase,lambda q:q['nodes'][i]['bound'].__setitem__('price','999'))
    out={'status':'PASS',**counts,'ratio_three_leaves':4,'mutation_base_nodes':len(base['nodes'])}
    (R/'results/tests.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':run()
