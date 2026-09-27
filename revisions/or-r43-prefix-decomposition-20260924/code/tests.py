from fractions import Fraction as F
from itertools import combinations
from random import Random
from pathlib import Path
import json,copy,time
from decomposition import Model,PriceDP,solve_prefix
from checker import support,BoundCheck,check
from unified import solve_catalog
R=Path(__file__).resolve().parents[1]

def run():
    start=time.perf_counter(); rng=Random(430924); counts=dict(models=0,priced_root=0,priced_prefix=0,global_comparisons=0,interrupted=0,tamper=0)
    for seed in range(72):
        k=1+seed%5; n=5+seed%3; a=tuple(F(i,n-1) for i in range(n)); m=1+seed%3
        caps=sorted(F(rng.randrange(1,8),8) for _ in range(k)); w=[rng.randrange(1,5) for _ in caps]; z=sum(w)
        model=Model.make(caps,[F(x,z) for x in w],[rng.randrange(5) for _ in caps],r=2,q=1)
        B=sum(p*b for p,b in zip(model.probabilities,model.caps))*F((seed//9)%4,3)
        delta=[F(0),F(1,8),F(1)][(seed//3)%3]
        ch=tuple(F(rng.randrange(4),100) for x in a) # includes nonmonotone charges
        books=[ids for s in range(1,m+1) for ids in combinations(range(n),s)
               if a[ids[0]]<=min(B,min(caps))]
        for lam in [F(-3),F(-1,3),F(0),F(3,2),F(7,4),F(3)]:
            dp=PriceDP(model,a,ch,m,B,delta,lam)
            scores={ids:lam*B+sum(p*support(model,j,tuple(a[i] for i in ids),lam,delta)
                for j,p in enumerate(model.probabilities))-sum(ch[i] for i in ids) for ids in books}
            assert dp.bound()[0]==max(scores.values())
            assert dp.bound()[0]==BoundCheck(model,a,ch,m,B,delta,lam).bound(())
            counts['priced_root']+=1
            for p in books:
                exact=max(v for ids,v in scores.items() if ids[:len(p)]==p)
                assert dp.bound(p)[0]==exact,(seed,lam,p,dp.bound(p)[0],exact)
                counts['priced_prefix']+=1
        ans=solve_prefix(model,a,ch,m,B,delta,iterations=4)
        brute=solve_catalog(model,a,ch,m,B,delta)
        assert ans['lower']==ans['upper']==brute['net_value']
        check(model,a,ch,m,B,delta,ans); counts['global_comparisons']+=1
        stop=solve_prefix(model,a,ch,m,B,delta,prices=[F(0)],max_nodes=1)
        assert stop['lower']<=brute['net_value']<=stop['upper']
        check(model,a,ch,m,B,delta,stop); counts['interrupted']+=1
        bad=copy.deepcopy(ans); bad['upper']+=1
        try: check(model,a,ch,m,B,delta,bad)
        except AssertionError: counts['tamper']+=1
        else: raise AssertionError('Altered global bound accepted.')
        counts['models']+=1
    # Fixed one-branch mesh lower bound, no charge, any realization tolerance.
    model=Model.make([F(1,2)],[1],[1],r=1,q=1)
    sharp=[]
    for N in (3,5,9,17,33):
        a=tuple(F(i,N) for i in range(N+1))
        ans=solve_prefix(model,a,[F(0)]*len(a),1,F(1,2),iterations=2)
        loss=F(3,8)-ans['lower']; assert loss==F(1,4*N)+F(1,4*N*N)
        sharp.append(dict(N=N,loss=str(loss),loss_over_h=str(loss*N)))
    counts.update(passed=True,seconds=time.perf_counter()-start,sharpness=sharp)
    (R/'results'/'verification.json').write_text(json.dumps(counts,indent=2)+'\n')
    print(json.dumps(counts,indent=2))
    return counts
if __name__=='__main__': run()
