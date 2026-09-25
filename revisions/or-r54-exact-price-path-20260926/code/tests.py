"""Exact tests of the new structural claims and semantic certificates."""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
from dataclasses import asdict
import copy,json,random,sys,time
from price_path import Model,spec_for,allocate,Oracle,solve,encode,digest
from check_price import verify,price_bound,check_policy,verify_common_cap
from common_cap import solve_common_cap
from packing import edges as packed_edges,reconstruct,from_policy
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'revisions/or-r52-resource-path-20260925/code'))
from resource_path import Instance,fixed_allocate,arc,arc_value
from pooling import capped_cost


def books(d,a,B,m,req=frozenset(),ban=frozenset()):
    for s in range(1,min(m,len(a))+1):
        for ids in combinations(range(len(a)),s):
            if not req<=set(ids) or ban&set(ids) or a[ids[0]]>min(B,min(d.caps)):continue
            yield ids,tuple(a[i] for i in ids)


def direct_support(d,book,lam):
    answer=F(0)
    for j,(b,w,g,tau) in enumerate(zip(d.caps,d.weights,d.gamma,d.ceilings)):
        eligible=[x for x in book if x<=tau];last=eligible[-1]
        points={book[0],b}|{x for x in eligible if x<=b}
        if g and last<=last-lam/g<=b:points.add(last-lam/g)
        values=[]
        for t in points:
            mu=min(t,last)
            if mu in eligible:f=d.reward(j,mu)
            else:
                u=max(x for x in eligible if x<mu);v=min(x for x in eligible if x>mu)
                f=((v-mu)*d.reward(j,u)+(mu-u)*d.reward(j,v))/(v-u)
            values.append(f-g*max(F(0),t-last)**2/2-lam*t)
        answer+=w*max(values)
    return answer


def nested(d,book,B):
    t=[book[0]]*len(d.caps);mass=B-book[0];layers=[]
    for u,v in zip(book,book[1:]):
        capacities=[max(F(0),min(b,v)-u) if tau>=v else F(0) for b,tau in zip(d.caps,d.ceilings)]
        T=sum(w*c for w,c in zip(d.weights,capacities));used=min(mass,T);res=used
        for j,c in enumerate(capacities):
            if c:assert t[j]==u  # All earlier selected layers are fully filled.
            take=min(res,d.weights[j]*c);t[j]+=take/d.weights[j];res-=take
        assert res==0;mass-=used;layers.append((T,used))
        if used<T:break
    last=[max(x for x in book if x<=tau) for tau in d.ceilings]
    y=[F(0)]*len(t)
    if mass:
        assert all(tj==min(b,z) for tj,b,z in zip(t,d.caps,last))
        costs=capped_cost(d.weights,d.gamma,tuple(max(F(0),b-z) for b,z in zip(d.caps,last)),mass)
        y=list(costs['service']);t=[x+z for x,z in zip(t,y)]
    assert sum(w*x for w,x in zip(d.weights,t))==B
    gross=F(0)
    for j,tj in enumerate(t):
        mu=tj-y[j];eligible=[x for x in book if x<=d.ceilings[j]]
        if mu in eligible:f=d.reward(j,mu)
        else:
            u=max(x for x in eligible if x<mu);v=min(x for x in eligible if x>mu)
            f=((v-mu)*d.reward(j,u)+(mu-u)*d.reward(j,v))/(v-u)
        gross+=d.weights[j]*(f-d.gamma[j]*y[j]**2/2)
    return gross,layers


def run():
    begin=time.perf_counter();rng=random.Random(540926)
    counts=dict(models=0,fixed_books=0,oracle_comparisons=0,global_certificates=0,nested_allocations=0,
                rearrangement_inequalities=0,heterogeneous_packing_checks=0,optimal_component_equalities=0,common_cap_models=0,common_cap_mixed_eligibility=0,heterogeneous_models=0)
    branched=[];common=[];sample=None
    for case in range(130):
        k=rng.randint(1,6);n=rng.randint(3,8);m=rng.randint(1,min(n,5));a=tuple(F(i,n-1) for i in range(n))
        caps=[F(rng.randint(0,10),10) for j in range(k)]
        if case<60:caps=[F(rng.randint(1,7),10)]*k
        raw=[rng.randint(1,5) for j in range(k)];w=[F(x,sum(raw)) for x in raw]
        g=[F(rng.randint(0,9),3) for j in range(k)];tau=[min(F(1),b+F(rng.randint(0,7),10)) for b in caps]
        rr=[F(2)+F(rng.randint(0,4),10) for j in range(k)] if case>=100 else 2
        d=Model.make(caps,w,g,tau,rr);B=d.cap_total*F(rng.randint(0,10),10)
        rho=tuple(F(rng.randint(0,8),100) for i in a);cost=dict(zip(a,rho));spec=spec_for(d,a,rho,B,m)
        catalog_books=list(books(d,a,B,m));opt=None;opt2=None
        old=Instance.make(caps,w,g,tau) if case<100 else None
        for ids,book in catalog_books:
            policy=allocate(d,book,B,cost);val=policy['value'];counts['fixed_books']+=1
            assert policy['gross']==policy['price']*B+direct_support(d,book,policy['price'])
            assert check_policy(spec,encode(policy))==val
            es=packed_edges(d,book);capacity=sum(e['C'] for e in es)
            resources=[(B-book[0])*e['C']/capacity if capacity else F(0) for e in es]
            packed,score=reconstruct(d,book,B,cost,resources);assert check_policy(spec,encode(packed))>=score-sum(cost[z] for z in book)
            counts['heterogeneous_packing_checks']+=1
            packed,score=reconstruct(d,book,B,cost,from_policy(d,book,policy));assert packed['value']==val and score==policy['gross']
            counts['optimal_component_equalities']+=1
            if old:
                assert fixed_allocate(old,book,B,cost)['value']==val
                gross,layers=nested(d,book,B);assert gross==policy['gross'];counts['nested_allocations']+=1
                edges=[arc(old,u,v) for u,v in zip(book,book[1:])]+[arc(old,book[-1])]
                C=sum(e['capacity'] for e in edges)
                resources=[(B-book[0])*e['capacity']/C if C else F(0) for e in edges]
                relaxed=old.reward(book[0])+sum(arc_value(old,e,x) for e,x in zip(edges,resources))
                assert gross>=relaxed;counts['rearrangement_inequalities']+=1
            opt=val if opt is None else max(opt,val)
            if len(book)<=2:opt2=val if opt2 is None else max(opt2,val)
        if case<60:
            assert opt==opt2;counts['common_cap_models']+=1
            pair=solve_common_cap(spec);assert pair['lower']==opt
            verify_common_cap(pair['certificate'],digest(spec))
            E=len({sum(x<=t for x in a) for t in tau});counts['common_cap_mixed_eligibility']+=int(E>1)
            common.append(dict(case=case,k=k,n=n,m=m,E=E,value=str(opt)))
        if case>=100:counts['heterogeneous_models']+=1
        oracle=Oracle(d,a,rho,B,m)
        for rep in range(3):
            req=frozenset([rng.randrange(n)]) if rep==1 else frozenset()
            ban=frozenset([rng.randrange(n)]) if rep==2 else frozenset()
            lam=F(rng.randint(-12,12),4);possible=list(books(d,a,B,m,req,ban));ans=oracle.run(lam,req,ban)
            expected=max((lam*B+direct_support(d,c,lam)-sum(cost[z] for z in c) for ids,c in possible),default=None)
            assert (None if ans is None else ans['upper'])==expected
            assert price_bound(spec,lam,set(req),set(ban),{})==expected
            counts['oracle_comparisons']+=1
        ans=solve(spec,epsilon=F(0),price_steps=12,max_nodes=1023)
        v=verify(ans['certificate'],digest(spec));assert ans['lower']==opt==ans['upper']
        counts['global_certificates']+=1
        if v['splits']:branched.append(dict(case=case,nodes=ans['nodes'],splits=v['splits']));sample=ans['certificate']
        counts['models']+=1
    # A deliberate unsupported optimum exercises a strictly positive root dual gap.
    d=Model.make([1],[1],[0],[1],1,0);a=(F(0),F(1,2));rho=(F(0),F(1,10));B=F(1,20)
    special=spec_for(d,a,rho,B,2);ans=solve(special,epsilon=F(0),max_nodes=63)
    assert ans['lower']==ans['upper']==0;assert verify(ans['certificate'])['splits']>0;sample=ans['certificate']
    corruptions=[]
    def reject(name,fn):
        c=copy.deepcopy(sample);fn(c)
        try:verify(c,sample['instance_sha256'])
        except (ValueError,KeyError,IndexError,TypeError,ZeroDivisionError):corruptions.append(name)
        else:raise AssertionError('Accepted corruption '+name)
    reject('wrong instance',lambda c:c.update(instance_sha256='0'*64))
    reject('wrong global bound',lambda c:c.update(upper='-1'))
    reject('wrong lower',lambda c:c.update(lower='10'))
    reject('missing branch',lambda c:c['tree']['split'].pop('included'))
    reject('invalid split',lambda c:c['tree']['split'].update(index=-1))
    reject('bad lottery',lambda c:c['policy']['lotteries'][0][0].__setitem__(1,'2'))
    reject('wrong root target',lambda c:c['policy']['targets'].__setitem__(0,'1'))
    reject('negative service',lambda c:c['policy']['intermediate'].__setitem__(0,'-1'))
    def damage_leaf(c):
        n=c['tree']
        while 'split' in n:n=n['split']['included']
        n['proof']={'type':'price','price':'0','upper':'-10'}
    reject('false leaf price bound',damage_leaf)
    # A deliberately resource-limited run must still have a complete valid cover.
    stopped=solve(special,epsilon=F(0),max_nodes=1);vv=verify(stopped['certificate']);assert not vv['tolerance_met']
    oversized=dict(special,budget=9);verify(solve(oversized)['certificate'],digest(oversized))
    result=dict(status='PASS',common_cap_certificates=60,oversized_budget_binding='PASS',**counts,branched_regression_models=branched,rejected_corruptions=corruptions,
                unsupported_optimum='PASS',interrupted_cover='PASS',seconds=time.perf_counter()-begin)
    out=HERE.parent/'results';out.mkdir(exist_ok=True)
    (out/'REGRESSION.json').write_text(json.dumps(result,indent=2)+'\n')
    (out/'COMMON_CAP.json').write_text(json.dumps(common,indent=2)+'\n')
    (out/'GAP_EXAMPLE.json').write_text(json.dumps(dict(spec=special,complete=encode(ans),limited=encode(stopped)),indent=2)+'\n')
    print(json.dumps(result,indent=2));return result
if __name__=='__main__':run()
