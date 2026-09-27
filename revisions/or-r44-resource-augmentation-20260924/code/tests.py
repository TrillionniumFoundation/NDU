"""Deterministic exact regression, exhaustive comparisons, and corruption tests."""
from fractions import Fraction as F
from pathlib import Path
from copy import deepcopy
import random,json,time
from augmentation import Model,recover,encode
from check_augmentation import check
from unified import solve_catalog
R=Path(__file__).resolve().parents[1]

def run():
    started=time.perf_counter(); rng=random.Random(2026092444); cases=[]
    for z in range(144):
        k=1+z%6; den=4+(z//6)%4; a=tuple(F(i,den) for i in range(den+1))
        b=sorted(F(rng.randint(1,15),16) for _ in range(k))
        w=[rng.randint(1,5) for _ in b]; p=[F(x,sum(w)) for x in w]
        g=[F(rng.randint(0,12),3) for _ in b]; model=Model.make(b,p,g,r=1+z%3)
        bar=sum(x*y for x,y in zip(b,p)); frac=(F(0),F(1,5),F(2,5),F(4,5),F(1))[z%5]
        B=frac*bar; m=1+(z//5)%3; delta=(F(0),F(1,16),F(1,4),F(1))[z%4]
        charges=tuple(F(0) if z%3==0 else (F(z%5,100)+F(z%7,100)*x if z%3==1 else F(rng.randint(0,15),100)) for x in a)
        record=recover(model,a,charges,m,B,delta,F(1,10000))
        checked=check(encode(record)); exact=solve_catalog(model,a,charges,m,B,delta)
        v=exact['net_value']; assert record['original_lower']<=v<=record['original_upper']
        assert record['augmented_policy']['value']>=v-record['price_error']-record['charge_excess']
        cases.append(dict(id=z,k=k,N=len(a),m=m,delta=str(delta),B=str(B),exact_value=str(v),original_gap=str(record['original_upper']-v),union_value=str(record['augmented_policy']['value']),union_size=checked['union_size'],oracle_calls=record['oracle_calls'],price_error=str(record['price_error']),charge_excess=str(record['charge_excess'])))
    model=Model.make([F(1,4),F(3,4)],[F(1,2)]*2,[1,2]); a=tuple(F(i,8) for i in range(9))
    witness=recover(model,a,[0]*len(a),2,F(2,5),0,F(1,10**8))
    exact=solve_catalog(model,a,[0]*len(a),2,F(2,5),0)
    from decomposition import PriceDP
    d,ids=PriceDP(model,a,(F(0),)*9,2,F(2,5),F(0),F(23,16)).bound()
    assert d==F(453,640) and exact['net_value']==F(45,64)
    assert witness['mixed_value']==d and witness['augmented_policy']['value']==d
    assert d-exact['net_value']==F(3,640)
    boundary=0
    for a0 in [F(0),F(1,8)]:
        a=tuple(a0+i*(1-a0)/4 for i in range(5))
        model=Model.make([F(1,4),F(3,4)],[F(1,2)]*2,[0,0],r=1,q=1)
        for B in [a0,F(1,2)]:
            for m in [1,len(a)]:
                for eps in [F(1,10**6),F(10)]:
                    check(encode(recover(model,a,[F(1,100)]*len(a),m,B,0,eps))); boundary+=1
    mutations=[]; raw=encode(witness)
    def mutate(name,f):
        data=deepcopy(raw); f(data)
        try: check(data)
        except (ValueError,KeyError,ZeroDivisionError): mutations.append(name)
        else: raise AssertionError('Accepted corrupted '+name)
    mutate('upper',lambda d:d.__setitem__('original_upper','0'))
    mutate('price_bound',lambda d:d['left'].__setitem__('upper','0'))
    mutate('endpoint_value',lambda d:d['left']['policy'].__setitem__('value','0'))
    mutate('price',lambda d:d['left'].__setitem__('price','-99'))
    mutate('theta',lambda d:d.__setitem__('theta','1/3'))
    mutate('target',lambda d:d['augmented_policy']['targets'].__setitem__(0,'0'))
    mutate('risk_tier',lambda d:d['augmented_policy']['intermediate'].__setitem__(1,'1'))
    mutate('normalization',lambda d:d['augmented_policy']['lotteries'][1][0].__setitem__(1,'1/2'))
    mutate('omitted_installed_level',lambda d:d['augmented_policy']['book'].pop())
    mutate('charge',lambda d:d['augmented_policy'].__setitem__('charge','1/100'))
    mutate('charge_excess',lambda d:d.__setitem__('charge_excess','-1'))
    mutate('price_error',lambda d:d.__setitem__('price_error','0'))
    mutate('budget',lambda d:d.__setitem__('budget',1))
    mutate('original_lower',lambda d:d.__setitem__('original_lower','2'))
    rejected=0
    for kw in [dict(epsilon=0),dict(epsilon=0.001),dict(budget=0),dict(delta=-1),dict(promise=1)]:
        args=dict(model=model,catalog=a,charges=[0]*len(a),budget=2,promise=F(1,4),delta=0,epsilon=F(1,100)); args.update(kw)
        try: recover(**args)
        except (TypeError,ValueError): rejected+=1
        else: raise AssertionError('Invalid input accepted')
    out=dict(status='PASS',seed=2026092444,exhaustive_comparisons=len(cases),boundary_cases=boundary,corruption_rejections=mutations,invalid_input_rejections=rejected,cases=cases,exact_gap_witness={'catalog_optimum':'45/64','dual_optimum':'453/640','gap':'3/640','supporting_price':'23/16','augmented_book':['1/4','1/2','5/8'],'augmented_value':'453/640'},wall_seconds=time.perf_counter()-started)
    (R/'results/certificates').mkdir(parents=True,exist_ok=True)
    (R/'results/verification.json').write_text(json.dumps(out,indent=2)+'\n')
    (R/'results/certificates/strict_gap.json').write_text(json.dumps(encode(witness),indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='cases'},indent=2))
    return out

if __name__=='__main__': run()
