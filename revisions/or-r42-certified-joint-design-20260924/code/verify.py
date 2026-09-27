"""Independent rational regression, boundary, cell and transport checks."""
from __future__ import annotations
import json, random, sys
from pathlib import Path
from fractions import Fraction as F
from dataclasses import asdict
from itertools import combinations
from collections import Counter
from unified import Model, solve_allocation, solve_catalog, branch_rule, response, certified_grid
from faces import solve_continuous, qp_faces, linear_solve
import catalog as old_catalog
import allocation as old_allocation
ROOT=Path(__file__).resolve().parents[1]


def encode(x):
    if isinstance(x,F): return str(x)
    if hasattr(x,'__dataclass_fields__'): return asdict(x)
    raise TypeError(type(x).__name__)


def support_oracle(model,j,book,t,delta):
    """Enumerate ALL one/two-point supports, optimizing their mean directly."""
    b,g=model.caps[j],model.gamma[j]
    vals=[model.reward(c)-g*(t-c)**2/2 for c in book if c<=t]
    for u,v in combinations(book,2):
        mu=min(t,v)
        if mu<u or t-mu+v>b+delta: continue
        vals.append(((v-mu)*model.reward(u)+(mu-u)*model.reward(v))/(v-u)-g*(t-mu)**2/2)
    return max(vals)


def run():
    rng=random.Random(420924); counts=Counter(); witnesses={}
    for it in range(160):
        k=rng.randrange(1,8)
        caps=sorted(F(rng.randrange(1,16),16) for _ in range(k))
        weights=[rng.randrange(1,7) for _ in caps]; total=sum(weights)
        model=Model.make(caps,[F(w,total) for w in weights],[rng.randrange(5) for _ in caps])
        a=tuple(sorted({F(0)}|{F(rng.randrange(1,17),16) for _ in range(rng.randrange(1,6))}))
        bar=sum(p*b for p,b in zip(model.probabilities,caps)); B=bar*F(rng.randrange(17),16)
        for delta in (F(0),F(1,16),F(1,8),F(1)):
            ans=solve_allocation(model,a,B,delta); counts['fixed_book_dual_equalities']+=1
            for j,b in enumerate(caps):
                for t in {ans.targets[j],b,b*F(rng.randrange(17),16)}:
                    assert response(model,j,a,t,delta)==support_oracle(model,j,a,t,delta)
                    counts['all_support_branch_equalities']+=1
            if delta==1:
                old=old_allocation.solve_allocation(model,a,B)
                assert ans.value==old.value
                counts['inherited_unrestricted_allocation_equalities']+=1
            # One-sided repair retains each target, not merely the total promise.
            for den in (3,5,8):
                rounded=tuple(sorted({F((z*den).__floor__(),den) for z in a}))
                repaired=sum(p*response(model,j,rounded,ans.targets[j],delta)
                             for j,p in enumerate(model.probabilities))
                constant=model.r+sum(p*g*b for p,g,b in zip(model.probabilities,model.gamma,caps))
                assert repaired>=ans.value-constant/den
                for j,t in enumerate(ans.targets):
                    y,draws=branch_rule(model,j,rounded,t,delta)
                    assert y+sum(c*w for c,w in draws)==t
                    assert all(y+c<=caps[j]+delta for c,w in draws)
                counts['exact_target_floor_repairs']+=1
        if it<32:
            a=tuple(F(j,8) for j in range(9)); prices=[F(j%3,100) for j in range(9)]
            for delta in (F(0),F(1,8),F(1)):
                new=solve_catalog(model,a,prices,2,bar,delta)
                old=old_catalog.solve(model,a,prices,2,delta)
                full=sum(p*model.reward(b) for p,b in zip(model.probabilities,caps))
                assert new['net_value']==full-old[-1].total
                counts['inherited_saturated_catalog_equalities']+=1
    # Homogeneous repeated caps may be aggregated at EVERY promise/tolerance.
    model=Model.make(['1/4','1/2','1/2','3/4'],['1/5','1/10','3/10','2/5'],[1,2,2,3])
    aggregated=Model.make(['1/4','1/2','3/4'],['1/5','2/5','2/5'],[1,2,3])
    for q in range(17):
        B=sum(p*b for p,b in zip(model.probabilities,model.caps))*F(q,16)
        for delta in (F(0),F(1,10),F(1)):
            for a in [(F(0),F(3,8)),(F(0),F(1,4),F(5,8))]:
                assert solve_allocation(model,a,B,delta).value==solve_allocation(aggregated,a,B,delta).value
                counts['all_promise_homogeneous_aggregation_equalities']+=1
    # Degenerate/indefinite quadratics: optima on lower-dimensional faces.
    G=[[F(-1),F(0)],[F(0),F(-1)],[F(1),F(0)],[F(0),F(1)]]; h=[F(0),F(0),F(1),F(1)]
    for H,a,expected in [([[0,0],[0,0]],[0,0],0),([[0,1],[1,0]],[0,0],1),([[-2,0],[0,0]],[1,0],F(1,4))]:
        H=[list(map(F,row)) for row in H]; a=list(map(F,a))
        result,_=qp_faces(H,a,F(0),G,h); assert result[0][0]==expected
        counts['singular_and_indefinite_face_checks']+=1
    import sympy as sp
    for n in range(1,7):
        for _ in range(12):
            A=[[F(rng.randrange(-5,6),rng.randrange(1,5)) for j in range(n)] for i in range(n)]
            b=[F(rng.randrange(-5,6),rng.randrange(1,5)) for i in range(n)]
            sol=linear_solve(A,b)
            S=sp.Matrix(A)
            if S.det()==0: assert sol is None
            else: assert list(map(sp.Rational,sol))==list(S.inv()*sp.Matrix(b))
            counts['independent_symbolic_linear_system_equalities']+=1
    # Exact global cases: saturation, nonsaturation, binding risk and charged levels.
    off=Model.make(['1/4','1/2','3/4'],['7/20','3/5','1/20'],[1,1,1])
    bar=F(17,40); full=sum(p*off.reward(b) for p,b in zip(off.probabilities,off.caps))
    for delta in (F(0),F(1,16),F(1,8),F(1)):
        ans=solve_continuous(off,2,bar,delta)
        z=F(1,2)+min(delta,F(1,8))
        assert ans['codebook']==(F(1,4),z)
        assert full-ans['net_value']==z*z/20-z/16+F(3,80)
        witnesses['off_cap_delta_'+str(delta)]=ans
        counts['analytic_continuous_global_equalities']+=1
    small=Model.make(['1/4','3/4'],['1/2','1/2'],[1,2])
    for B in (F(0),F(1,8),F(2,5),F(1,2)):
        for delta in (F(0),F(1,8),F(1)):
            for price in [(0,0,0),(F(1,100),F(1,50),F(1,100))]:
                ans=solve_continuous(small,2,B,delta,price)
                grid=certified_grid(small,2,B,delta,16,lambda c:price[0]*c*c+price[1]*c+price[2],2*price[0]+price[1])
                assert grid['continuous_lower']<=ans['net_value']<=grid['continuous_upper']
                counts['continuous_grid_value_enclosures']+=1
    # Interior continuous pathwise lottery gain with a nonnegative quadratic charge.
    m=Model.make(['9/10'],[1],[1])
    p=solve_continuous(m,2,F(9,20),0,(-3,3,0))
    d=solve_continuous(m,2,F(9,20),0,(-3,3,0),True)
    assert p['net_value']==F(171,400) and d['net_value']==F(9,160)
    assert p['codebook']==(F(0),F(9,10)) and d['codebook']==(F(9,20),)
    witnesses['continuous_interior_pathwise_randomization']={'randomized':p,'deterministic':d}
    counts['analytic_continuous_global_equalities']+=2
    # Counterexample to naive floor-and-compensate, repaired without risk slack.
    m=Model.make(['1/2'],[1],[1]); a=(F(1,4),F(5,8)); t=F(1,2); delta=F(1,8)
    y,law=branch_rule(m,0,a,t,delta)
    floored=[(F((c*8).__floor__(),8),p) for c,p in law] # exact grid; perturb lower instead
    lower=F(0); upper=F(5,8)
    naivemu=sum((lower if c==F(1,4) else upper)*p for c,p in law)
    naiverisk=t-naivemu+upper
    assert naiverisk>F(5,8)
    ry,rlaw=branch_rule(m,0,(lower,upper),t,delta)
    assert max(ry+c for c,p in rlaw)==F(5,8)
    witnesses['naive_compensation_counterexample']={'old_law':law,'new_lower':lower,'naive_maximum':naiverisk,'risk_limit':F(5,8),'repaired_law':rlaw}
    # Invalid domains are not silently coerced.
    for f in [lambda:solve_allocation(small,[F(0),F(0)],0),lambda:solve_allocation(small,[F(0)],0,-1),lambda:solve_catalog(small,[0,1],[0,-1],2,0),lambda:solve_continuous(small,True,0),lambda:solve_continuous(small,2,0,price=(0,-1,0))]:
        try: f()
        except (ValueError,TypeError): counts['invalid_input_rejections']+=1
        else: raise AssertionError('Invalid input accepted')
    result={'status':'passed','seed':420924,'arithmetic':'exact rational; no tolerance','counts':dict(counts),'witnesses':witnesses}
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'results'/'verification.json').write_text(json.dumps(result,default=encode,indent=2)+'\n')
    print(json.dumps(dict(counts),indent=2),flush=True)
    return result
if __name__=='__main__': run()
