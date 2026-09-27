"""Exact regression, theorem checks, and semantic mutation tests."""
from fractions import Fraction as F
from pathlib import Path
from itertools import combinations
from copy import deepcopy
import random,json,math
from harmonic import Instance,reduce,solve,lift,sqrt_partition,accuracy_partition,encode
from box_solver import exhaustive_joint,fixed_allocate
from coarsening import reduced_model as minimum_model
from check_harmonic import check
R=Path(__file__).resolve().parents[1]

def run():
    rng=random.Random(48001);A=tuple(F(i,4) for i in range(5));counts=dict(joint_order=0,book_lifts=0,dispersion=0,accuracy_partitions=0,refinement=0,certificate_mutations=0)
    for seed in range(32):
        k=3+seed%3;caps=[F(rng.randint(1,9),10) for _ in range(k)];raw=[rng.randint(1,5) for _ in range(k)];w=[F(x,sum(raw)) for x in raw]
        costs=[F(rng.randint(0,16),4) for _ in range(k)];D=Instance.make(caps,w,costs,[F(1)]*k)
        G=sqrt_partition(D,A,F(1),F(4));S,G,bounds=reduce(D,A,G);M,_,_=minimum_model(D,A,G)
        B=D.cap_total*F(1+seed%3,3);rho=tuple(F(rng.randint(0,3),100) for _ in A);m=1+seed%3
        p=exhaustive_joint(D,A,rho,B,m);s=exhaustive_joint(S,A,rho,B,m);mi=exhaustive_joint(M,A,rho,B,m)
        delta=sum(z['defect'] for z in bounds)
        assert p['value']<=s['value']<=mi['value'] and s['value']-p['value']<=delta
        counts['joint_order']+=1
        for size in range(1,m+1):
            for c in combinations(A,size):
                if c[0]>min(B,min(S.caps)):continue
                src=fixed_allocate(S,c,B,dict(zip(A,rho)));lo,clip,sp,post=lift(D,S,G,src,A,rho)
                assert lo['value']>=clip['value'] and 0<=src['value']-lo['value']<=post<=delta
                counts['book_lifts']+=1
        # Rational verification of (sqrt(v)-sqrt(u))^2 bound, avoiding roots.
        for b in bounds:
            g=G[bounds.index(b)];u=min(D.gamma[j] for j in g);v=max(D.gamma[j] for j in g);gap=b['arithmetic_gamma']-b['gamma']
            assert u+v-gap>=0 and (u+v-gap)**2>=4*u*v
            counts['dispersion']+=1
        for eps in [F(1,2),F(1,10),F(1,100)]:
            P=accuracy_partition(D,A,eps);ss,_,bd=reduce(D,A,P)
            assert sum(x['defect'] for x in bd)<=eps/2
            counts['accuracy_partitions']+=1
        group=next((g for g in G if len(g)>1),None)
        if group:
            refined=tuple(g for g in G if g!=group)+((group[0],),tuple(group[1:]))
            S2,_,_=reduce(D,A,refined);p2=exhaustive_joint(S2,A,rho,B,m)
            assert p['value']<=p2['value']<=s['value'];counts['refinement']+=1
    # Explicit positive-tail sharpness: harmonic is attained, min-cost is loose.
    D=Instance.make([F(9,10)]*2,[F(1,2)]*2,[F(1),F(4)],[F(1)]*2)
    S,G,_=reduce(D,(F(0),),((0,1),));B=F(1,4)
    assert S.gamma==(F(8,5),)
    source=fixed_allocate(S,(F(0),),B,{F(0):F(0)})
    lo,_,_,_=lift(D,S,G,source,(F(0),),(F(0),))
    assert source['value']==lo['value']==-F(1,20)
    # Nontrivial guard, clipping, zero curvature and code/checker separation.
    D=Instance.make([F(1,5),F(2,5),F(4,5)],[F(1,5),F(3,10),F(1,2)],[F(1),F(2),F(6)],[F(1)]*3)
    c=encode(solve(D,A,(F(0),)*5,D.cap_total,2,((0,),(1,2)),max_nodes=31))
    assert check(c)['status']=='PASS'
    mutations=[('upper_bound','-999'),('gap','0'),('budget',1),('uniform_defect','0'),('posterior_defect','-1'),('actual_lift_defect','-1'),('status','COMPLETE'),('requested_epsilon','0'),('groups_count',3)]
    for key,val in mutations:
        d=deepcopy(c);d[key]=val
        try:check(d)
        except (ValueError,AssertionError):counts['certificate_mutations']+=1
        else:raise AssertionError(('Mutation accepted',key))
    for action in range(5):
        d=deepcopy(c)
        if action==0:d['reduced_model']['gamma'][1]='2'
        elif action==1:d['group_supports'][1]['price']='999'
        elif action==2:d['groups'][1]=[1]
        elif action==3:d['policy']['targets'][1]='1'
        else:d['clipped_policy']['lotteries'][0][0][1]='0'
        try:check(d)
        except (ValueError,AssertionError):counts['certificate_mutations']+=1
        else:raise AssertionError(('Mutation accepted',action))
    counts['status']='PASS';(R/'results/tests.json').write_text(json.dumps(counts,indent=2)+'\n');print(counts)
if __name__=='__main__':run()
