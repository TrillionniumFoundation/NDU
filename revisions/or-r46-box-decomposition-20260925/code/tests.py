"""Deterministic exact regression and adversarial certificate checks."""
from fractions import Fraction as F
from pathlib import Path
from itertools import combinations,product
import random,json,time,copy,sys
from box_solver import *
from check_certificate import check
from compression import repair_targets
import target_net_reference
R=Path(__file__).resolve().parents[1]

def run():
    started=time.perf_counter(); rng=random.Random(460025); price_checks=0; joint_checks=0; coverage_checks=0
    for seed in range(100):
        k=rng.randrange(1,5); bs=tuple(F(rng.randrange(2,10),10) for _ in range(k))
        w0=[rng.randrange(1,6) for _ in bs]; ws=tuple(F(w,sum(w0)) for w in w0)
        gs=tuple(F(rng.randrange(5)) for _ in bs)
        tau=tuple(min(F(1),b+F(rng.randrange(4),10)) for b in bs)
        d=Instance.make(bs,ws,gs,tau); a=tuple(F(i,5) for i in range(6));rho=tuple(F(rng.randrange(4),100) for _ in a)
        low=tuple(b*F(rng.randrange(4),5) for b in bs); high=tuple(l+(b-l)*F(rng.randrange(1,6),5) for l,b in zip(low,bs))
        B=sum(w*(l+h)/2 for w,l,h in zip(ws,low,high));m=rng.randrange(1,4)
        for lam in [F(-3),F(-1,2),F(0),F(4,3),F(7,4),F(3)]:
            got=price_path(d,a,rho,B,m,low,high,lam,tables=True)
            truth=exhaustive_price(d,a,rho,B,m,low,high,lam)
            assert got['upper']==truth
            price_checks+=1
        if seed<24:
            out=solve(d,a,rho,B,m,F(1,200),max_nodes=151,price_steps=6)
            ref=exhaustive_joint(d,a,rho,B,m)
            assert out['lower_bound']<=ref['value']<=out['upper_bound']
            check(encode(out));joint_checks+=1
    d=Instance.make([F(1,5),F(1,2),F(4,5)],[F(1,3)]*3,[1]*3,[1]*3)
    a=(F(1,5),F(1,2),F(4,5));rho=(F(0),)*3;t=d.caps;B=d.cap_total;lam=F(3,2)
    p=price_path(d,a,rho,B,3,t,t,lam,tables=True)
    ascending=[]
    for n in range(1,4):
        for book in combinations(a,n):
            if book[0]>min(t):continue
            vals=[d.reward(x)-lam*x for x in book]
            if any(u>v for u,v in zip(vals,vals[1:])):continue
            ascending.append(sum(w*branch_support(d,j,book,t[j],t[j],lam)[0] for j,w in enumerate(d.weights))+lam*B)
    ascending=max(ascending);assert p['upper']>ascending
    counter=dict(targets=t,price=lam,book=p['book'],two_sided_value=p['upper'],rising_only_value=ascending,loss=p['upper']-ascending)
    # Genuine clipping below anchor and above cap, both signs of mass repair.
    clip_cases=0
    for raw in ((F(-1),F(2),F(3)),(F(-1),F(-2),F(-3)),(F(2),F(2),F(2))):
        repaired,clipping,repair=repair_targets(d,raw,F(1,10),F(2,5))
        assert clipping>0 and all(F(1,10)<=t<=b for t,b in zip(repaired,d.caps))
        assert sum(w*t for w,t in zip(d.weights,repaired))==F(2,5);clip_cases+=1
    one=Instance.make([F(4,5)],[1],[2],[1])
    single=target_net_reference.solve(one,tuple(F(i,8) for i in range(9)),(F(0),)*9,F(2,5),3,F(1,1000))
    assert single['evaluated_profiles']==1 and single['epsilon_guarantee']==0
    # Independent finite lattice regression for the constructive net cover.
    for k in (2,3,4):
        dd=Instance.make([F(4,5)]*k,[F(1,k)]*k,[1]*k,[1]*k)
        for targets in product([F(i,10) for i in range(2,9)],repeat=k):
            B=sum(dd.weights[j]*targets[j] for j in range(k));anchor=F(1,10);eta=F(1,37)
            masses=[eta*((dd.weights[j]*(targets[j]-anchor))//eta) for j in range(k-1)]
            masses.append(min(dd.weights[-1]*(dd.caps[-1]-anchor),B-anchor-sum(masses)))
            rounded=tuple(anchor+x/w for x,w in zip(masses,dd.weights))
            repaired,_,_=repair_targets(dd,rounded,anchor,B)
            distance=sum(w*abs(s-t) for w,s,t in zip(dd.weights,targets,repaired))
            assert distance<=2*(k-1)*eta;coverage_checks+=1
    dd=Instance.make([F(2,5),F(7,10),F(9,10)],[F(1,5),F(3,10),F(1,2)],[1,2,3],[F(1,2),F(4,5),1])
    aa=tuple(F(i,8) for i in range(9));rr=tuple(F((13*i)%9,100) for i in range(9));BB=dd.cap_total*F(4,5)
    out=solve(dd,aa,rr,BB,3,F(1,1000),max_nodes=1000);record=encode(out);check(record)
    (R/'results'/'checked_certificate.json').write_text(json.dumps(record,indent=2)+'\n')
    # Exact aggregation permits different ceilings within the same eligibility cell.
    big=Instance.make([F(2,5)]*4+[F(7,10)]*4,[F(1,8)]*8,[1]*4+[2]*4,[F(51+i,100) for i in range(4)]+[F(81+i,100) for i in range(4)])
    small,groups=aggregate(big,aa);assert len(small.caps)==2
    joint_big=exhaustive_joint(big,aa,rr,big.cap_total*F(4,5),2)
    joint_small=exhaustive_joint(small,aa,rr,big.cap_total*F(4,5),2)
    assert joint_big['value']==joint_small['value']
    mutations=[]
    def reject(name,fn):
        x=copy.deepcopy(record);fn(x)
        try:check(x)
        except (ValueError,AssertionError,TypeError,IndexError,KeyError):mutations.append(name)
        else:raise AssertionError('Mutation accepted: '+name)
    reject('root_cover',lambda x:x['nodes'][0]['lower'].__setitem__(0,'1/3'))
    reject('missing_child',lambda x:x['nodes'][0]['children'].pop())
    reject('wrong_split',lambda x:x['nodes'][0]['split'].__setitem__(1,'1'))
    reject('missing_leaf',lambda x:x['leaves'].pop())
    reject('policy_promise',lambda x:x['policy']['targets'].__setitem__(0,'0'))
    reject('opening_charge',lambda x:x['policy'].__setitem__('charge','100'))
    reject('false_upper',lambda x:x.__setitem__('upper_bound','0'))
    reject('false_accuracy',lambda x:x.__setitem__('requested_epsilon','0'))
    reject('invalid_types',lambda x:x['groups'][0].append(1))
    reject('prefix_bound',lambda x:x['nodes'][0]['witness']['alpha'][0].__setitem__(0,'-100'))
    plus=next((n for n in record['nodes'] if F(n['witness']['price'])>0),None)
    if plus is not None:
        nodeid=plus['id'];reject('suffix_bound',lambda x:x['nodes'][nodeid]['witness']['beta'][0].__setitem__(0,'-100'))
    stopped=solve(dd,aa,rr,BB,3,F(1,1000000),max_nodes=1)
    assert stopped['status']=='INTERRUPTED' and stopped['epsilon_guarantee'] is None
    check(encode(stopped))
    result=dict(status='PASS',price_comparisons=price_checks,joint_intervals_checked=joint_checks,net_lattice_coverage_checks=coverage_checks,
        clipping_cases=clip_cases,k1_calls=single['evaluated_profiles'],aggregation_exact=True,mutation_rejections=mutations,
        interrupted_interval_checked=True,two_sided_counterexample=counter,seconds=time.perf_counter()-started)
    (R/'results'/'tests.json').write_text(json.dumps(encode(result),indent=2)+'\n')
    print(json.dumps(encode(result),indent=2))
if __name__=='__main__':run()
