"""Independent R48 checker; imports neither harmonic.py nor an optimizer.

Upper witnesses use the inherited independent Bellman-inequality/cover checker.
The harmonic aggregation, lift comparison, and group KKT equalities are rebuilt
here from the original primitives and explicit probabilities.
"""
from fractions import Fraction as F
from pathlib import Path
import sys,json,gzip
P=Path(__file__).resolve().parents[2]/'or-r46-box-decomposition-20260925'/'code'
sys.path.insert(0,str(P))
from check_certificate import check as check_inner, model
from independent import verify_policy,direct_branch


def check(rec):
    if rec.get('schema')!='ndu-r48-harmonic-certificate-v1':raise ValueError('Schema')
    D,S=model(rec['original_model']),model(rec['reduced_model'])
    A=tuple(map(F,rec['catalog']));rho=tuple(map(F,rec['charges']));B=F(rec['promise']);m=rec['budget'];G=rec['groups']
    if not A or len(A)!=len(rho) or A[0]<0 or A[-1]>1 or any(a>=b for a,b in zip(A,A[1:])) or any(x<0 for x in rho):raise ValueError('Catalog/charges')
    if type(m)!=int or not 1<=m<=len(A):raise ValueError('Budget')
    ids=[i for g in G for i in g]
    if any(not g for g in G) or any(type(i)!=int for i in ids) or sorted(ids)!=list(range(len(D.caps))):raise ValueError('Partition')
    if len(G)!=len(S.caps) or len(G)!=len(rec['group_bounds']) or len(G)!=len(rec['group_supports']):raise ValueError('Groups')
    if rec['original_branches']!=len(D.caps) or rec['groups_count']!=len(G):raise ValueError('Dimensions')
    if D.r!=S.r or D.curvature!=S.curvature or min(D.caps)!=min(S.caps):raise ValueError('Reward or guard')
    delta=F(0)
    for z,g in enumerate(G):
        w=sum(D.weights[j] for j in g);b=sum(D.weights[j]*D.caps[j] for j in g)/w
        inv=None if any(D.gamma[j]==0 for j in g) else sum(D.weights[j]/D.gamma[j] for j in g)
        h=F(0) if inv is None else w/inv;av=sum(D.weights[j]*D.gamma[j] for j in g)/w
        tau=max(D.ceilings[j] for j in g)
        if (w,b,h,tau)!=(S.weights[z],S.caps[z],S.gamma[z],S.ceilings[z]):raise ValueError('Harmonic representative')
        prefix=tuple(a for a in A if a<=tau)
        if any(tuple(a for a in A if a<=D.ceilings[j])!=prefix for j in g):raise ValueError('Eligibility')
        L=max(D.r,max(D.gamma[j] for j in g)*max(D.caps[j] for j in g))
        dc=2*L*sum(D.weights[j]*max(F(0),b-D.caps[j]) for j in g);dh=w*(av-h)*(b-A[0])**2/2
        values=dict(weight=w,cap=b,gamma=h,arithmetic_gamma=av,lipschitz=L,cap_defect=dc,cost_defect=dh,defect=dc+dh)
        if any(F(rec['group_bounds'][z][key])!=val for key,val in values.items()):raise ValueError('Group bound')
        delta+=dc+dh
    inner=rec['inner_certificate']
    for key in ('catalog','charges','promise','budget'):
        if inner[key]!=rec[key]:raise ValueError('Inner contract mismatch')
    if inner['original_model']!=rec['reduced_model']:raise ValueError('Inner model mismatch')
    result=check_inner(inner)
    source=inner['policy'];targets=tuple(map(F,rec['policy']['targets']));clipped=tuple(map(F,rec['clipped_policy']['targets']));means=tuple(map(F,source['targets']));book=tuple(map(F,source['book']))
    if tuple(sorted(book))!=book:raise ValueError('Ordered book required for support witness')
    for key in ('policy','clipped_policy'):
        verify_policy(D,A,rho,rec[key],B,m)
        if tuple(map(F,rec[key]['book']))!=book:raise ValueError('Changed book')
    post=F(0);gross=F(0)
    for z,g in enumerate(G):
        w=S.weights[z];s=means[z]
        if any(sum(D.weights[j]*t[j] for j in g)!=w*s for t in (targets,clipped)):raise ValueError('Group mass')
        if sum(D.weights[j]*abs(clipped[j]-s) for j in g)!=2*sum(D.weights[j]*max(F(0),s-D.caps[j]) for j in g):raise ValueError('Clipping witness')
        d=max(a for a in book if a<=S.ceilings[z]);bmax=max(D.caps[j] for j in g);av=sum(D.weights[j]*D.gamma[j] for j in g)/w
        post+=sum(D.weights[j]*max(D.r,D.gamma[j]*bmax)*abs(clipped[j]-s) for j in g)+w*(av-S.gamma[z])*max(F(0),s-d)**2/2
        lam=F(rec['group_supports'][z]['price']);dual=lam*s;actual=F(0)
        for j in g:
            knots={book[0],D.caps[j]}|{a for a in book if book[0]<=a<=min(D.ceilings[j],D.caps[j])}
            dj=max(a for a in book if a<=D.ceilings[j])
            if D.gamma[j]>0 and D.caps[j]>=dj:knots.add(min(D.caps[j],max(dj,book[0],dj-lam/D.gamma[j])))
            fun=lambda t:direct_branch(D.r,D.curvature,D.gamma[j],D.ceilings[j],book,t)
            dual+=D.weights[j]/w*max(fun(t)-lam*t for t in knots)
            actual+=D.weights[j]/w*fun(targets[j])
        if dual!=actual or actual!=F(rec['group_supports'][z]['gross']):raise ValueError('Group optimality support')
        gross+=w*actual
    low=F(rec['policy']['value']);clip=F(rec['clipped_policy']['value']);high=F(inner['upper_bound']);gap=high-low;defect=F(source['value'])-low
    if (low,high,gap)!=(F(rec['lower_bound']),F(rec['upper_bound']),F(rec['gap'])) or gap<0:raise ValueError('Interval')
    if gross-sum(rho[A.index(a)] for a in book)!=low or low<clip or defect<0:raise ValueError('Lift payoff')
    if delta!=F(rec['uniform_defect']) or post!=F(rec['posterior_defect']) or defect!=F(rec['actual_lift_defect']) or post>delta or F(source['value'])-clip>post:raise ValueError('Lift defect')
    if gap>F(inner['gap'])+delta:raise ValueError('Error composition')
    eps=F(rec['requested_epsilon']);status='COMPLETE' if gap<=eps else 'UNRESOLVED'
    if eps<=0 or rec['status']!=status or (None if rec['epsilon_guarantee'] is None else F(rec['epsilon_guarantee']))!=(eps if gap<=eps else None):raise ValueError('Accuracy claim')
    return dict(status='PASS',k=len(D.caps),groups=len(G),lower=str(low),upper=str(high),gap=str(gap),inner=result)

if __name__=='__main__':
    p=Path(sys.argv[1]);raw=gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes()
    print(json.dumps(check(json.loads(raw)),indent=2))
