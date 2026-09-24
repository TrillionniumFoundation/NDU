"""Independent upper-table and target-cover checker; does not import box_solver.

Checks Bellman INEQUALITIES, not a solver status flag, and reconstructs the
entire binary target cover. It also checks the original uneliminated policy.
"""
from fractions import Fraction as F
from pathlib import Path
import sys,json
OLD=Path(__file__).resolve().parents[2]/'or-r45-budgeted-compression-20260924'/'code'
sys.path.insert(0,str(OLD))
from compression import Instance
from independent import verify_policy


def model(raw):
    return Instance.make(raw['caps'],raw['weights'],raw['gamma'],raw['ceilings'],raw['r'],raw['curvature'])


def clipped_box(data,low,high,B):
    low,high=tuple(map(F,low)),tuple(map(F,high))
    if any(l>u or l<0 or u>b for l,u,b in zip(low,high,data.caps)): return None
    lowmass=sum(p*t for p,t in zip(data.weights,low)); highmass=sum(p*t for p,t in zip(data.weights,high))
    if B<lowmass or B>highmass: return None
    return (tuple(max(low[j],(B-sum(data.weights[i]*high[i] for i in range(len(low)) if i!=j))/data.weights[j]) for j in range(len(low))),
            tuple(min(high[j],(B-sum(data.weights[i]*low[i] for i in range(len(low)) if i!=j))/data.weights[j]) for j in range(len(low))))


def check_bound(data,a,rho,B,m,low,high,witness):
    price=F(witness['price']); n=len(a); score=[data.reward(x)-price*x for x in a]
    alpha=[[None if x is None else F(x) for x in row] for row in witness['alpha']]
    if len(alpha)!=m or any(len(row)!=n for row in alpha): raise ValueError('Prefix table dimensions')
    def short(j,base):
        lower=max(F(0),low[j]-base); upper=high[j]-base
        candidates=[lower,upper]
        if data.gamma[j]>0:
            candidates.append(min(upper,max(lower,-price/data.gamma[j])))
        return max(-data.gamma[j]*x*x/2-price*x for x in candidates)
    def edge(i,l,rising):
        base,top=a[i],a[l]; total=F(0)
        for j,p in enumerate(data.weights):
            target=high[j] if rising else low[j]
            if not base<=target<top: continue
            if top<=data.ceilings[j]:
                value=score[i]+(target-base)*(score[l]-score[i])/(top-base)
            elif rising:
                value=score[i]+short(j,base)
            else:
                value=score[i]-data.gamma[j]*(target-base)**2/2-price*(target-base)
            total+=p*value
        return total
    for i,x in enumerate(a):
        feasible=x<=min(high) and sum(p*max(l,x) for p,l in zip(data.weights,low))<=B
        if feasible and (alpha[0][i] is None or alpha[0][i]<-rho[i]):
            raise ValueError('Missing feasible anchor upper bound')
    for r in range(1,m):
        for l in range(n):
            for i in range(l):
                if alpha[r-1][i] is not None and score[i]<=score[l]:
                    rhs=alpha[r-1][i]+edge(i,l,True)-rho[l]
                    if alpha[r][l] is None or alpha[r][l]<rhs:
                        raise ValueError('Prefix Bellman inequality')
    if price<=0:
        if witness['beta'] is not None: raise ValueError('Unexpected descending table')
        stop=[sum((p*(score[i]+short(j,x)) for j,p in enumerate(data.weights) if high[j]>=x),F(0)) for i,x in enumerate(a)]
        candidates=[alpha[r][i]+stop[i] for r in range(m) for i in range(n) if alpha[r][i] is not None]
    else:
        beta=[[F(x) for x in row] for row in witness['beta']]
        if len(beta)!=m or any(len(row)!=n for row in beta): raise ValueError('Suffix dimensions')
        stop=[sum((p*(score[i]-data.gamma[j]*(low[j]-x)**2/2-price*(low[j]-x)) for j,p in enumerate(data.weights) if low[j]>=x),F(0)) for i,x in enumerate(a)]
        middle=[sum((p*score[i] for j,p in enumerate(data.weights) if low[j]<x<=high[j]),F(0)) for i,x in enumerate(a)]
        for r in range(m):
            for i in range(n):
                if beta[r][i]<stop[i]: raise ValueError('Suffix stopping inequality')
                if r>0:
                    for l in range(i+1,n):
                        if score[l]<=score[i] and beta[r][i]<edge(i,l,False)-rho[l]+beta[r-1][l]:
                            raise ValueError('Suffix Bellman inequality')
        candidates=[alpha[r][i]+middle[i]+beta[m-r-1][i] for r in range(m) for i in range(n) if alpha[r][i] is not None]
    upper=price*B+max(candidates)
    if F(witness['upper'])<upper: raise ValueError('Invalid final path upper bound')
    return F(witness['upper'])


def check(record):
    data,original=model(record['model']),model(record['original_model'])
    a,rho=tuple(map(F,record['catalog'])),tuple(map(F,record['charges']))
    B,m=F(record['promise']),record['budget']
    if not isinstance(m,int) or isinstance(m,bool) or not 1<=m<=len(a): raise ValueError('Budget')
    if len(a)!=len(rho) or any(x>=y for x,y in zip(a,a[1:])) or any(x<0 for x in rho): raise ValueError('Catalog')
    groups=record['groups']; covered=[]
    if len(groups)!=len(data.caps): raise ValueError('Type count')
    for z,group in enumerate(groups):
        if not group: raise ValueError('Empty type')
        covered+=list(group)
        if sum(original.weights[j] for j in group)!=data.weights[z]: raise ValueError('Type weights')
        for j in group:
            if (original.caps[j],original.gamma[j],sum(x<=original.ceilings[j] for x in a))!=(data.caps[z],data.gamma[z],sum(x<=data.ceilings[z] for x in a)):
                raise ValueError('Nonidentical type')
    if sorted(covered)!=list(range(len(original.caps))) or original.r!=data.r or original.curvature!=data.curvature:
        raise ValueError('Aggregation does not cover original instance')
    verify_policy(original,a,rho,record['policy'],B,m)
    lower=F(record['policy']['value'])
    if lower!=F(record['lower_bound']): raise ValueError('Lower bound is not policy value')
    nodes=record['nodes']; seen=set(); leaves=[]
    expected=clipped_box(data,(a[0],)*len(data.caps),data.caps,B)
    def visit(idx,box,parent):
        if idx in seen: raise ValueError('Cover cycle or duplicate node')
        seen.add(idx); node=nodes[idx]
        if node['id']!=idx or node['parent']!=parent: raise ValueError('Tree identity')
        lo,hi=tuple(map(F,node['lower'])),tuple(map(F,node['upper_targets']))
        if (lo,hi)!=box: raise ValueError('Uncovered target region')
        bound=check_bound(data,a,rho,B,m,lo,hi,node['witness'])
        if bound!=F(node['bound']): raise ValueError('Node bound mismatch')
        if node['children'] is None:
            leaves.append(idx); return
        axis,cut=node['split']; cut=F(cut)
        if not 0<=axis<len(lo) or not lo[axis]<cut<hi[axis]: raise ValueError('Invalid split')
        h=list(hi); h[axis]=cut; l=list(lo); l[axis]=cut
        expected_children=[z for z in (clipped_box(data,lo,h,B),clipped_box(data,l,hi,B)) if z is not None]
        if len(node['children'])!=len(expected_children): raise ValueError('Missing split child')
        for child,childbox in zip(node['children'],expected_children): visit(child,childbox,idx)
    visit(0,expected,None)
    if len(seen)!=len(nodes) or sorted(leaves)!=sorted(record['leaves']): raise ValueError('Incomplete leaf cover')
    upper=max([lower]+[F(nodes[i]['bound']) for i in leaves])
    if upper!=F(record['upper_bound']) or upper-lower!=F(record['gap']): raise ValueError('Global interval mismatch')
    eps=F(record['requested_epsilon'])
    if record['epsilon_guarantee'] is not None:
        if F(record['epsilon_guarantee'])!=eps or upper-lower>eps: raise ValueError('Unjustified accuracy')
    if record['status']=='COMPLETE' and upper-lower>eps: raise ValueError('False completion')
    return dict(status='PASS',checked_nodes=len(nodes),checked_leaves=len(leaves),lower=str(lower),upper=str(upper),gap=str(upper-lower))


if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('usage: check_certificate.py certificate.json')
    print(json.dumps(check(json.loads(Path(sys.argv[1]).read_text())),indent=2))
