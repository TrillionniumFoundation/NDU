"""Independent certificate checker; never imports the tariff optimizer.

Reconstructs capacities from each history's eligible prefix, checks EVERY
Bellman state and exception subset, then verifies the original-space policy.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from rational import F
from check_price import model,check_policy,fingerprint,require


def verify(cert, expected_sha256=None):
    require(cert['schema']=='NDU-R60-tariff-frontier-v1','Wrong schema')
    spec=cert['spec'];sha=fingerprint(spec)
    require(sha==cert['instance_sha256'],'Wrong input digest')
    if expected_sha256 is not None: require(sha==expected_sha256,'Wrong requested input')
    w,b,g,t,r,q,a,charges,B,m=model(spec)
    require(not any(g) and not any(q) and len(set(r))==1,'Wrong model subclass')
    fee=F(cert['standard_fee']);require(fee>=0,'Negative standard fee')
    # Independent parameterization check; do not import tariff60.standard_fee.
    frequencies={}
    for charge in charges:frequencies[charge]=frequencies.get(charge,0)+1
    modal=min(frequencies,key=lambda x:(-frequencies[x],x))
    require(fee==modal,'Noncanonical standard fee: expected smallest rational mode')
    ex=[i for i,v in enumerate(charges) if v!=fee]
    require(ex==cert['exceptions'],'Incomplete exception inventory')
    require(cert.get('modal_tie_rule')=='smallest rational fee','Incorrect modal tie-rule metadata')
    guard=cert.get('configured_guard')
    require(type(guard) is int and guard>=0,'Invalid configured exception guard')
    require(len(ex)<=guard,'Certificate exceeds configured exception guard')
    # Enumeration count is checked before visiting any supplied branch.
    require(len(cert['branches'])==2**len(ex),'Incomplete exception cover')
    require([z['mask'] for z in cert['branches']]==list(range(2**len(ex))),'Bad mask order/cover')
    n=len(a);arc={}
    for v in range(n):
        for u in range(v):
            gain=F(0)
            for j in range(len(b)):
                if a[v]<=t[j]:
                    gain+=w[j]*(max(F(0),min(b[j],a[v])-a[u]))
            arc[u,v]=gain
    uppers=[];checked=0
    for branch in cert['branches']:
        chosen=[ex[j] for j in range(len(ex)) if branch['mask'] >> j & 1]
        forbidden=set(ex)-set(chosen)
        rows=branch['rows'];require(len(rows)==m and all(len(row)==n for row in rows),'Bad table shape')
        table=[[None if x is None else F(x) for x in row] for row in rows]
        for level in range(m):
            for v in range(n):
                vals=[]
                if v not in forbidden:
                    if level==0:
                        if a[v]<=B and all(a[v]<=c for c in b) and not any(j<v for j in chosen):vals=[a[v]]
                    else:
                        for u in range(v):
                            if u not in forbidden and table[level-1][u] is not None and not any(u<j<v for j in chosen):
                                vals.append(table[level-1][u]+arc[u,v])
                require(table[level][v]==(max(vals) if vals else None),'False or omitted capacity state')
                checked+=1
        vals=[]
        for level,row in enumerate(table):
            cost=fee*(level+1-len(chosen))+sum((charges[j] for j in chosen),F(0))
            for v,capacity in enumerate(row):
                if capacity is not None and v not in forbidden and not any(j>v for j in chosen):
                    vals.append(r[0]*min(B,capacity)-cost)
        upper=max(vals) if vals else None
        require((None if branch['upper'] is None else F(branch['upper']))==upper,'False branch upper bound')
        if upper is not None:uppers.append(upper)
    require(uppers,'No feasible branch')
    upper=max(uppers);lower=check_policy(spec,cert['policy'])
    require(lower==F(cert['lower'])==F(cert['upper'])==upper,'Global interval not closed')
    return dict(status='PASS',lower=str(lower),upper=str(upper),checked_states=checked,branches=len(cert['branches']),standard_fee=str(modal),exception_count=len(ex),parameterization_certified=True)
