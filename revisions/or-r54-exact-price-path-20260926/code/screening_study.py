"""Near-envelope and possible-anchor screening against exact inclusion relevance."""
from fractions import Fraction as F
from pathlib import Path
import json,random,sys,time,statistics
from price_path import Model,spec_for,allocate,Oracle,solve,encode
from check_price import price_bound,verify
from tests import books
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'revisions/or-r53-catalog-safe-certificates-20260926/code'))
from screening import screen,context_gain
from resource_path import Instance


def quantiles(values):
    s=sorted(values)
    return dict(minimum=min(s),median=statistics.median(s),q25=s[(len(s)-1)//4],q75=s[3*(len(s)-1)//4],maximum=max(s))


def run():
    rows=[];rng=random.Random(540928);a=tuple(map(F,('0','3/100','3/50','3/25','3/10','1/2','3/4','1')))
    for family in range(8):
        k=6;m=(2,3,4)[family%3];caps=[F(rng.randint(20,75),100) for j in range(k)]
        w=(F(1,k),)*k;g=[F(rng.randint(0,10),3) for j in range(k)];tau=[min(F(1),b+F(rng.randint(0,30),100)) for b in caps]
        d=Model.make(caps,w,g,tau);old=Instance.make(caps,w,g,tau);B=d.cap_total*F((3,6,9)[family%3],10)
        base=[F(rng.randint(0,8),100) for z in a];target=a[5+family%2];G=context_gain(old,a[0],target)
        for factor in (F(9,10),F(1),F(11,10)):
            rho=list(base);rho[a.index(target)]=factor*G;rho=tuple(rho);cost=dict(zip(a,rho));spec=spec_for(d,a,rho,B,m)
            begin=time.perf_counter();pool=[]
            for ids,c in books(d,a,B,m):pool.append((set(ids),allocate(d,c,B,cost)['value']))
            opt=max(v for ids,v in pool);enum_seconds=time.perf_counter()-begin
            included=[max((v for ids,v in pool if i in ids),default=None) for i in range(len(a))]
            excluded=[max((v for ids,v in pool if i not in ids),default=None) for i in range(len(a))]
            cheap=screen(old,a,rho,B);ans=solve(spec,epsilon=F(0),max_nodes=511);checked=verify(ans['certificate'])
            assert ans['lower']==ans['upper']==opt
            policy=ans['certificate']['policy'];price=F(policy['price']);prices={price,F(0)};oracle=Oracle(d,a,rho,B,m)
            begin=time.perf_counter();forced=[];entries=[]
            for i,z in enumerate(a):
                vals=[]
                for lam in prices:
                    bound=oracle.run(lam,frozenset({i}));val=None if bound is None else bound['upper']
                    assert val==price_bound(spec,lam,{i},set(),{})
                    if val is not None:vals.append(val)
                U=min(vals) if vals else None
                removable=U is None or U<ans['lower']
                if removable:forced.append(z);assert included[i] is None or included[i]<opt
                possible_anchor=z<=min(B,min(caps));gain=None if possible_anchor else context_gain(old,a[0],z)
                entries.append(dict(command=str(z),charge=str(rho[i]),gain_bound=None if gain is None else str(gain),
                    slack=None if gain is None else str(rho[i]-gain),possible_anchor=possible_anchor,
                    wholly_ineligible=all(t<z for t in tau),exact_inclusion_value=None if included[i] is None else str(included[i]),
                    exact_exclusion_value=None if excluded[i] is None else str(excluded[i]),
                    forced_price_upper=None if U is None else str(U),forced_screen=removable,
                    envelope_screen=any(F(x['candidate'])==z for x in cheap['deletions'])))
            pricing_seconds=time.perf_counter()-begin
            retained=[z for z in a if z not in forced]
            assert max(v for ids,v in pool if all(a[i] in retained for i in ids))==opt
            row=dict(id=f'family-{family}-factor-{factor}',family=family,m=m,spec=spec,target=str(target),multiplier=str(factor),
                     exact_value=str(opt),incumbent_seconds=ans['seconds'],envelope_seconds=cheap['seconds'],
                     forced_test_and_check_seconds=pricing_seconds,enumeration_seconds=enum_seconds,
                     envelope_removed=len(cheap['deletions']),forced_removed=len(forced),
                     forced_anchor_removed=sum(x['forced_screen'] and x['possible_anchor'] for x in entries),
                     strictly_irrelevant=sum(x is None or x<opt for x in included),entries=entries)
            rows.append(row)
    summary=dict(status='PASS',cases=len(rows),envelope_rate=quantiles([r['envelope_removed']/8 for r in rows]),
                 forced_rate=quantiles([r['forced_removed']/8 for r in rows]),
                 forced_anchor_removals=sum(r['forced_anchor_removed'] for r in rows),
                 rows=rows)
    (HERE.parent/'results/SCREENING.json').write_text(json.dumps(summary,indent=2)+'\n')
    print({k:v for k,v in summary.items() if k!='rows'});return summary
if __name__=='__main__':run()
