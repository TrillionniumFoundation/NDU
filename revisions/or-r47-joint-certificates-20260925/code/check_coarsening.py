"""Independent semantic checker for R47; does not import coarsening or search.

Recomputes the relaxation, group error bound, weighted clipping identity,
original policy constraints, and the inner R46 Bellman/coverage certificate.
"""
from fractions import Fraction as F
from pathlib import Path
import sys, json, gzip
P=Path(__file__).resolve().parents[2]/'or-r46-box-decomposition-20260925'/'code'
sys.path.insert(0,str(P))
from check_certificate import check as check_inner, model
from independent import verify_policy
sys.path.insert(0, str(Path(__file__).resolve().parent))


def same_model(left, right):
    fields=('caps','weights','gamma','ceilings')
    return all(tuple(map(F,left[key]))==tuple(map(F,right[key])) for key in fields) and all(F(left[key])==F(right[key]) for key in ('r','curvature'))


def check(record):
    if record.get('schema')!='ndu-r47-coarsening-certificate-v1':
        raise ValueError('Schema')
    original,small=model(record['original_model']),model(record['reduced_model'])
    a,rho=tuple(map(F,record['catalog'])),tuple(map(F,record['charges']))
    groups=record['groups']; k=len(original.caps); B=F(record['promise']); m=record['budget']
    if len(a)!=len(rho) or not a or a[0]<0 or a[-1]>1 or any(x>=y for x,y in zip(a,a[1:])) or any(r<0 for r in rho):
        raise ValueError('Catalog')
    if type(m) is not int or not 1<=m<=len(a):
        raise ValueError('Budget')
    if len(groups)!=len(small.caps) or len(record['group_bounds'])!=len(groups):
        raise ValueError('Group count')
    flat=[j for g in groups for j in g]
    if any(not g for g in groups) or any(type(j) is not int for j in flat) or sorted(flat)!=list(range(k)):
        raise ValueError('Partition')
    if original.r!=small.r or original.curvature!=small.curvature or min(original.caps)!=min(small.caps):
        raise ValueError('Reward or anchor guard')
    exact_types=len(set(zip(original.caps,original.gamma,(sum(x<=t for x in a) for t in original.ceilings))))
    if record['original_branches']!=k or record['groups_count']!=len(groups) or record['original_exact_types']!=exact_types:
        raise ValueError('History/type metadata')
    if record['status'] not in ('COMPLETE','UNRESOLVED'):
        raise ValueError('Unknown completion status')
    delta=F(0)
    for z,g in enumerate(groups):
        w=sum(original.weights[j] for j in g)
        b=sum(original.weights[j]*original.caps[j] for j in g)/w
        gamma=min(original.gamma[j] for j in g)
        ceiling=max(original.ceilings[j] for j in g)
        prefix=sum(x<=small.ceilings[z] for x in a)
        if any(sum(x<=original.ceilings[j] for x in a)!=prefix for j in g):
            raise ValueError('Eligibility mismatch')
        if (w,b,gamma,ceiling)!=(small.weights[z],small.caps[z],small.gamma[z],small.ceilings[z]):
            raise ValueError('Incorrect optimistic representative')
        L=max(original.r,gamma*max(original.caps[j] for j in g))
        dc=2*L*sum(original.weights[j]*max(F(0),b-original.caps[j]) for j in g)
        dh=sum(original.weights[j]*(original.gamma[j]-gamma)*(original.caps[j]-a[0])**2/2 for j in g)
        expected=dict(weight=w,cap=b,gamma=gamma,ceiling=ceiling,lipschitz=L,cap_defect=dc,cost_defect=dh,defect=dc+dh)
        if any(F(record['group_bounds'][z][key])!=value for key,value in expected.items()):
            raise ValueError('Defect metadata')
        delta+=dc+dh
    if original.cap_total!=small.cap_total or delta!=F(record['uniform_defect']):
        raise ValueError('Capacity/defect total')
    inner=record['inner_certificate']
    if not same_model(inner['original_model'],record['reduced_model']):
        raise ValueError('Inner certificate belongs to another model')
    if tuple(map(F,inner['catalog']))!=a or tuple(map(F,inner['charges']))!=rho or F(inner['promise'])!=B or inner['budget']!=m:
        raise ValueError('Inner contract mismatch')
    inner_check=check_inner(inner)
    verify_policy(original,a,rho,record['policy'],B,m)
    verify_policy(original,a,rho,record['lifted_policy'],B,m)
    source=inner['policy']; lifted=record['lifted_policy']
    if tuple(map(F,source['book']))!=tuple(map(F,lifted['book'])):
        raise ValueError('Lift changed the book')
    means=tuple(map(F,source['targets'])); targets=tuple(map(F,lifted['targets']))
    service=tuple(map(F,lifted['intermediate'])); dist=F(0); post=F(0)
    for z,g in enumerate(groups):
        if sum(original.weights[j]*targets[j] for j in g)!=small.weights[z]*means[z]:
            raise ValueError('Group mass not preserved')
        d=sum(original.weights[j]*abs(targets[j]-means[z]) for j in g)
        clipping=2*sum(original.weights[j]*max(F(0),means[z]-original.caps[j]) for j in g)
        if d!=clipping:
            raise ValueError('Lift clipping identity')
        L=max(original.r,small.gamma[z]*max(original.caps[j] for j in g))
        post+=L*d+sum(original.weights[j]*(original.gamma[j]-small.gamma[z])*service[j]**2/2 for j in g)
        dist+=d
    lower=F(record['policy']['value']); upper=F(inner['upper_bound']); gap=upper-lower
    if post!=F(record['posterior_defect']) or dist!=F(record['weighted_lift_distance']) or post>delta:
        raise ValueError('Posterior defect')
    if F(source['value'])-F(lifted['value'])>post or lower<F(lifted['value']):
        raise ValueError('Lift value bound')
    if (lower,upper,gap)!=(F(record['lower_bound']),F(record['upper_bound']),F(record['gap'])) or gap<0 or gap>F(inner['gap'])+delta:
        raise ValueError('Original interval')
    eps=F(record['requested_epsilon'])
    if eps<=0 or (record['status']=='COMPLETE')!=(gap<=eps):
        raise ValueError('Completion')
    expected=eps if gap<=eps else None
    if (None if record['epsilon_guarantee'] is None else F(record['epsilon_guarantee']))!=expected:
        raise ValueError('False original-space accuracy')
    return dict(status='PASS',branches=k,groups=len(groups),lower=str(lower),upper=str(upper),gap=str(gap),uniform_defect=str(delta),inner=inner_check)

if __name__=='__main__':
    if len(sys.argv)!=2:
        raise SystemExit('usage: check_coarsening.py certificate.json[.gz]')
    p=Path(sys.argv[1]); raw=gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes()
    print(json.dumps(check(json.loads(raw)),indent=2))
