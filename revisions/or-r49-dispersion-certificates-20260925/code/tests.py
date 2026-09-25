"""Deterministic exact regression against the untouched R46 exhaustive oracle."""
from pooling import *
from box_solver import exhaustive_joint
from pathlib import Path
import random,json
R=Path(__file__).resolve().parents[1]

def fixture(seed,k=4,n=5,common=False):
    rng=random.Random(seed)
    b=tuple(F(rng.randint(1,9),10) for _ in range(k));gw=tuple(rng.randint(1,5) for _ in b)
    w=tuple(F(x,sum(gw)) for x in gw)
    gamma=tuple(F(rng.randint(0,16),4) for _ in b)
    tau=tuple(F(1) if common else min(F(1),x+F(rng.randint(0,5),10)) for x in b)
    D=Instance.make(b,w,gamma,tau)
    a=tuple(F(i,n-1) for i in range(n));rho=tuple(F(rng.randint(0,4),50) for _ in a)
    B=D.cap_total*F(rng.randint(1,10),10)
    return D,a,rho,B

def mutation_tests():
    from check_pooling import check
    from copy import deepcopy
    D=Instance.make([F(3,10),F(7,10),F(9,10)],[F(1,3)]*3,[F(0),F(1),F(9)],[F(1)]*3)
    a=tuple(F(i,4) for i in range(5));rho=(F(8,100),F(11,100),F(1,100),F(9,100),F(15,100));B=D.cap_total*F(19,20)
    single=encode(solve(D,a,rho,B,2,epsilon=F(0),max_nodes=1))
    D2,a2,r2,B2=fixture(49201,4,5,False)
    multi=encode(solve(D2,a2,r2,B2,3,epsilon=F(1,1000),max_nodes=15,price_steps=2))
    assert check(single)['status']=='PASS' and check(multi)['status']=='PASS'
    rejected=0
    def reject(base,mutator):
        nonlocal rejected
        record=deepcopy(base);mutator(record)
        try:check(record)
        except (ValueError,AssertionError,IndexError,KeyError,TypeError):rejected+=1
        else:raise AssertionError('Certificate mutation accepted')
    def w(r):return r['nodes'][0]['witness']['service_witnesses'][0]
    reject(single,lambda r:w(r).__setitem__('value',str(F(w(r)['value'])+1)))
    reject(single,lambda r:w(r).__setitem__('correction',str(F(w(r)['correction'])+1)))
    reject(single,lambda r:w(r).__setitem__('multiplier',str(F(w(r)['multiplier'])+100)))
    reject(single,lambda r:w(r).__setitem__('service',['-1']+w(r)['service'][1:]))
    reject(single,lambda r:w(r).__setitem__('mean',str(F(w(r)['mean'])+1)))
    reject(single,lambda r:r['nodes'][0]['witness']['service_witnesses'].pop())
    reject(single,lambda r:r['nodes'][0]['witness']['alpha'][0].__setitem__(0,'-100'))
    reject(single,lambda r:r.__setitem__('lower_bound',str(F(r['lower_bound'])+1)))
    reject(single,lambda r:r.__setitem__('upper_bound',str(F(r['upper_bound'])-1)))
    reject(single,lambda r:r.__setitem__('budget',1))
    reject(single,lambda r:r.__setitem__('eligibility_groups',2))
    reject(multi,lambda r:r['nodes'][0]['children'].pop())
    reject(multi,lambda r:r['leaves'].pop())
    reject(multi,lambda r:r['nodes'][1].__setitem__('parent',99))
    reject(multi,lambda r:r['nodes'][0].__setitem__('split',[r['nodes'][0]['split'][0],r['nodes'][0]['upper_targets'][r['nodes'][0]['split'][0]]]))
    reject(multi,lambda r:r.__setitem__('status','COMPLETE'))
    return dict(independent_base_certificates=2,rejected_mutations=rejected)


def run():
    counts=dict(group_price_comparisons=0,pooled_fixed_mean=0,common_eligibility_joint=0,multigroup_intervals=0)
    for seed in range(24):
        D,a,rho,B=fixture(49000+seed,2+seed%4,5,seed%3==0)
        groups=eligibility_groups(D,a);G=group_model(D,groups)
        rawlo=(F(0),)*len(groups);rawhi=G.caps
        root=project_box(G,rawlo,rawhi,B)
        mid=ideal_targets(G,B)
        boxes=[root,(mid,mid)]
        for h in range(len(groups)):
            hi=list(root[1]);hi[h]=(root[0][h]+root[1][h])/2
            p=project_box(G,root[0],hi,B)
            if p:boxes.append(p)
        for lo,hi in boxes:
            for lam in [F(-3),F(-1,3),F(0),F(1),F(3,2),F(3)]:
                p=price_path(D,a,rho,B,3,groups,lo,hi,lam,reference_check=True)
                q=exhaustive_box(D,a,rho,B,3,groups,lo,hi,lam)
                assert p['upper']==q,(seed,lo,hi,lam,p['upper'],q)
                counts['group_price_comparisons']+=1
        for book in [(a[0],),(a[0],a[2]),(a[0],a[1],a[-1])]:
            p=recover(D,groups,book,mid,dict(zip(a,rho)))
            ref=sum(sum(D.weights[j] for j in ids)*fixed_allocate(subinstance(D,ids),book,t,{x:F(0) for x in book})['gross'] for ids,t in zip(groups,mid))-sum(dict(zip(a,rho))[x] for x in book)
            assert p['value']==ref
            counts['pooled_fixed_mean']+=1
        if len(groups)==1:
            p=solve(D,a,rho,B,3,epsilon=F(0),max_nodes=1)
            q=exhaustive_joint(D,a,rho,B,3)
            assert p['gap']==0 and p['lower_bound']==q['value']
            counts['common_eligibility_joint']+=1
        elif seed<10:
            p=solve(D,a,rho,B,3,epsilon=F(1,100),max_nodes=15,price_steps=2)
            q=exhaustive_joint(D,a,rho,B,3)
            assert p['lower_bound']<=q['value']<=p['upper_bound']
            counts['multigroup_intervals']+=1
        print(seed,counts,flush=True)
    # Boundary regimes are not selected from the study outcomes.
    boundary = [
      (Instance.make([F(1,3)],[F(1)],[F(0)],[F(1)]),(F(0),F(1,4),F(1)),F(0)),
      (Instance.make([F(1,3),F(4,5)],[F(2,5),F(3,5)],[F(0),F(0)],[F(1),F(1)]),(F(1,10),F(2,5),F(3,5),F(1)),F(3,10)),
      (Instance.make([F(1,3),F(4,5)],[F(2,5),F(3,5)],[F(3),F(0)],[F(1),F(1)]),(F(1,10),F(2,5),F(3,5),F(1)),F(46,75))
    ]
    counts['boundary_joint_comparisons']=0
    for D,a,B in boundary:
        rho=tuple(F(i%3,50) for i in range(len(a)))
        for m in range(1,len(a)+1):
            z=solve(D,a,rho,B,m,epsilon=F(0),max_nodes=1)
            q=exhaustive_joint(D,a,rho,B,m)
            assert z['gap']==0 and z['lower_bound']==q['value']
            counts['boundary_joint_comparisons']+=1
    counts.update(mutation_tests())
    R.joinpath('results/TESTS.json').write_text(json.dumps(counts,indent=2)+'\n')
    return counts
if __name__=='__main__':print(run())
