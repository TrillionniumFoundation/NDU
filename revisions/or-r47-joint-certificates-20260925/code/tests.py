"""Deterministic theorem and independent-certificate regression tests."""
from fractions import Fraction as F
from pathlib import Path
from itertools import combinations
import random,json,copy,time,hashlib,sys
from coarsening import Instance,bin_partition,reduced_model,lift,solve,accuracy_partition,certified_scheme,encode,fixed_allocate
from box_solver import exhaustive_joint,branch_value
from check_coarsening import check
R=Path(__file__).resolve().parents[1]


def random_model(seed,k):
    rng=random.Random(seed)
    caps=tuple(F(rng.randint(3,18),20) for _ in range(k))
    weights=tuple(rng.randint(1,7) for _ in range(k)); total=sum(weights)
    gamma=tuple(F(rng.randint(0,30),10) for _ in range(k))
    ceilings=tuple(F(1) if seed%2 else max(b,F(3,4)) for b in caps)
    return Instance.make(caps,[F(w,total) for w in weights],gamma,ceilings)


def run(output=None):
    start=time.perf_counter(); counts=dict(exhaustive_joint_pairs=0,fixed_book_lifts=0,
          cap_deviation_bounds=0,accuracy_partitions=0,certificates_checked=0,
          refinement_comparisons=0,mutations_rejected=0)
    mutations=[]; examples=[]; sample=None
    for seed in range(72):
        k=3+seed%4; D=random_model(seed,k)
        a=tuple(F(i,4) for i in range(5))
        rho=tuple(F((seed+7*i)%13,80) if seed%3 else F(0) for i in range(5))
        if seed%17==0: rho=tuple(x+3 for x in rho) # negative net values
        B=D.cap_total* (F(1) if seed%6==0 else F(13+seed%6,20));m=1+seed%3
        G=bin_partition(D,a,F(1,2),F(2))
        S,G,bd=reduced_model(D,a,G); delta=sum(x['defect'] for x in bd)
        p=exhaustive_joint(D,a,rho,B,m); pbar=exhaustive_joint(S,a,rho,B,m)
        assert p['value']<=pbar['value']<=p['value']+delta
        counts['exhaustive_joint_pairs']+=1
        for s in range(1,m+1):
            for book in combinations(a,s):
                if book[0]>min(B,min(D.caps)):continue
                reduced=fixed_allocate(S,book,B,dict(zip(a,rho)))
                actual,dist,post=lift(D,S,G,reduced,a,rho)
                assert reduced['value']-actual['value']<=post<=delta
                assert actual['promise']==B
                if B==D.cap_total:assert actual['targets']==D.caps
                counts['fixed_book_lifts']+=1
        for beta,eta in ((F(1,3),F(1,2)),(F(1),F(4))):
            SS,GG,bb=reduced_model(D,a,bin_partition(D,a,beta,eta))
            L=max(D.r,max(D.gamma))
            assert sum(z['defect'] for z in bb)<=L*beta/2+eta/2
            for g in GG:
                w=sum(D.weights[j] for j in g);mu=sum(D.weights[j]*D.caps[j] for j in g)/w
                assert sum(D.weights[j]*max(F(0),mu-D.caps[j]) for j in g)<=w*beta/4
                counts['cap_deviation_bounds']+=1
        for eps in (F(1,2),F(1,20),F(1,1000)):
            _,GG,bb=reduced_model(D,a,accuracy_partition(D,a,eps))
            assert sum(x['defect'] for x in bb)<=eps/2
            counts['accuracy_partitions']+=1
        # Split one nontrivial group; the optimistic optimum cannot increase.
        for z,g in enumerate(G):
            if len(g)>1:
                fine=G[:z]+((g[0],),tuple(g[1:]))+G[z+1:]
                SS,_,_=reduced_model(D,a,fine)
                pf=exhaustive_joint(SS,a,rho,B,m)
                assert p['value']<=pf['value']<=pbar['value']
                counts['refinement_comparisons']+=1;break
        if seed<24:
            cert=solve(D,a,rho,B,m,G,F(1,1000),max_nodes=7,price_steps=4)
            assert cert['lower_bound']<=p['value']<=cert['upper_bound']
            check(encode(cert));counts['certificates_checked']+=1
            if sample is None and cert['gap']>0:sample=encode(cert)
    # A genuine cap-clipping lift at saturation, with unequal original weights.
    D=Instance.make([F(1,5),F(2,5),F(4,5)],[F(1,5),F(3,10),F(1,2)],[F(1),F(2),F(5,2)],[F(1)]*3)
    a=tuple(F(i,4) for i in range(5));rho=(F(0),)*5;G=((0,),(1,2));B=D.cap_total
    c=solve(D,a,rho,B,2,G,F(1,1000),max_nodes=3)
    assert c['weighted_lift_distance']>0 and c['lifted_policy']['targets']==D.caps
    check(encode(c));counts['certificates_checked']+=1
    examples.append(dict(name='saturation_clips_and_restores_individual_caps',distance=c['weighted_lift_distance'],gap=c['gap']))
    # Guard failure is not cosmetic: one averaged branch admits an invalid anchor.
    guard=Instance.make([F(1,5),F(4,5)],[F(1,2)]*2,[F(1)]*2,[F(1)]*2)
    try:reduced_model(guard,a,((0,1),))
    except ValueError:pass
    else:raise AssertionError('Missing anchor guard accepted')
    wrong=Instance.make([F(1,5),F(2,5),F(3,5)],[F(1,3)]*3,[F(1)]*3,[F(1),F(1,2),F(1)])
    try:reduced_model(wrong,a,((0,),(1,2)))
    except ValueError:pass
    else:raise AssertionError('Mixed eligibility accepted')
    # Nonzero catalog anchor, zero shortfall curvature, and total-cap endpoint.
    anchored=Instance.make([F(1,4),F(3,5),F(7,10)],[F(1,5),F(3,10),F(1,2)],[F(0),F(0),F(3,2)],[F(1)]*3)
    aa=(F(1,10),F(1,4),F(1,2),F(3,4));rr=(F(1,30),)*4
    ca=solve(anchored,aa,rr,anchored.cap_total,2,((0,),(1,2)),F(1,1000),max_nodes=3)
    check(encode(ca));counts['certificates_checked']+=1
    pa=exhaustive_joint(anchored,aa,rr,anchored.cap_total,2)
    assert ca['lower_bound']<=pa['value']<=ca['upper_bound']
    # Exact repeated groups have zero error; no compression requires no repair.
    exact=Instance.make([F(1,4),F(3,4),F(3,4)],[F(1,3)]*3,[F(1),F(2),F(2)],[F(1)]*3)
    _,_,bb=reduced_model(exact,a,((0,),(1,2)))
    assert sum(z['defect'] for z in bb)==0
    single=Instance.make([F(3,4)],[F(1)],[F(2)],[F(1)])
    c1=certified_scheme(single,a,rho,F(1,2),2,F(1,1000));assert c1['gap']==0
    check(encode(c1));counts['certificates_checked']+=1
    # Frozen certificate mutation checks recompute semantics, not hashes.
    sample=sample or encode(c)
    def reject(name,mutate):
        x=copy.deepcopy(sample);mutate(x)
        try:check(x)
        except (ValueError,AssertionError,KeyError,IndexError,TypeError,ZeroDivisionError):
            mutations.append(name);counts['mutations_rejected']+=1
        else:raise AssertionError('Accepted mutation: '+name)
    reject('overstate_lower',lambda x:x.__setitem__('lower_bound',str(F(x['lower_bound'])+1)))
    reject('understate_upper',lambda x:x.__setitem__('upper_bound',str(F(x['upper_bound'])-1)))
    reject('zero_reported_gap',lambda x:x.__setitem__('gap','0'))
    reject('change_original_promise',lambda x:x.__setitem__('promise',str(F(x['promise'])/2)))
    reject('change_charge',lambda x:x['charges'].__setitem__(0,str(F(x['charges'][0])+1)))
    reject('drop_original_branch',lambda x:x['groups'][0].pop())
    reject('duplicate_group',lambda x:x['groups'].__setitem__(0,x['groups'][-1]))
    reject('reduce_reported_defect',lambda x:x.__setitem__('uniform_defect','-1'))
    reject('change_representative_cap',lambda x:x['reduced_model']['caps'].__setitem__(0,'1'))
    reject('change_representative_cost',lambda x:x['reduced_model']['gamma'].__setitem__(0,'100'))
    reject('change_group_bound',lambda x:x['group_bounds'][0].__setitem__('lipschitz','0'))
    reject('change_lift_distance',lambda x:x.__setitem__('weighted_lift_distance','-1'))
    reject('change_posterior',lambda x:x.__setitem__('posterior_defect','-1'))
    reject('remove_coverage_leaf',lambda x:x['inner_certificate']['leaves'].clear())
    reject('misstate_history_count',lambda x:x.__setitem__('original_branches',999))
    reject('misstate_exact_types',lambda x:x.__setitem__('original_exact_types',999))
    reject('unknown_completion_flag',lambda x:x.__setitem__('status','UNVERIFIED'))
    reject('decrease_node_bound',lambda x:x['inner_certificate']['nodes'][0].__setitem__('bound','-1000'))
    out=dict(status='PASS',protocol='Fixed seeds 0..71; all feasible books with cardinalities 1..m',counts=counts,
        mutations=mutations,examples=examples,elapsed_seconds=time.perf_counter()-start,python=sys.version)
    (R/'results').mkdir(exist_ok=True)
    (Path(output) if output is not None else R/'results/tests.json').write_text(json.dumps(encode(out),indent=2)+'\n')
    print(json.dumps(encode(out),indent=2),flush=True)
    return out
if __name__=='__main__':run()
