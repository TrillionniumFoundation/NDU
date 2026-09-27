"""Independent eligibility-pooling certificate checker; no optimizer imports.

Checks Bellman INEQUALITIES, not a solver status flag, and reconstructs the
entire binary target cover. It also checks the original uneliminated policy.
"""
from fractions import Fraction as F
from pathlib import Path
import sys,json,gzip
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


def equalize(caps,weights,mean):
    """Independent cap-threshold enumeration, not the optimizer water fill."""
    total=sum(w*b for w,b in zip(weights,caps))
    if mean==total:return tuple(caps)
    saturated_weight=F(0);saturated_mass=F(0);previous=F(0)
    for j in sorted(range(len(caps)),key=lambda j:caps[j]):
        threshold=caps[j]
        at_threshold=saturated_mass+threshold*(1-saturated_weight)
        if mean<=at_threshold:
            z=(mean-saturated_mass)/(1-saturated_weight)
            out=tuple(min(b,z) for b in caps)
            if z<previous or sum(w*x for w,x in zip(weights,out))!=mean:raise ValueError('Invalid cap equalization')
            return out
        saturated_weight+=weights[j];saturated_mass+=weights[j]*caps[j];previous=threshold
    raise ValueError('Infeasible group mean')


def pooling_bounds(data,a,groups,group_low,group_high,witness):
    price=F(witness['price']);low=[None]*len(data.caps);high=[None]*len(data.caps)
    normalized=[]
    for ids,l,u in zip(groups,group_low,group_high):
        W=sum(data.weights[j] for j in ids);weights=tuple(data.weights[j]/W for j in ids)
        caps=tuple(data.caps[j] for j in ids);normalized.append((W,weights))
        for j,x,y in zip(ids,equalize(caps,weights,l),equalize(caps,weights,u)):
            low[j],high[j]=x,y
    supplied={}
    for row in witness['service_witnesses']:
        key=(row['group'],row['index'])
        if key in supplied:raise ValueError('Duplicate service witness')
        supplied[key]=row
    used=set();corr={};prefixes=[]
    for h,ids in enumerate(groups):
        W,weights=normalized[h]
        kh=sum(x<=min(data.ceilings[j] for j in ids) for x in a);prefixes.append(kh)
        for i,d in enumerate(a[:kh]):
            D=sum(w*min(data.caps[j],d) for w,j in zip(weights,ids))
            if group_high[h]<D:corr[h,i]=F(0);continue
            key=(h,i)
            if key not in supplied:raise ValueError('Missing pooled service witness')
            used.add(key);row=supplied[key];nu=F(row['multiplier']);mu=price+nu
            qlo=max(F(0),group_low[h]-D);qhi=group_high[h]-D
            capacities=tuple(max(F(0),data.caps[j]-d) for j in ids)
            # Weak duality over the total-service interval. Each scalar maximum
            # is independently checked at endpoints and a clipped stationary point.
            dual=nu*(qhi if nu>=0 else qlo)
            naive=F(0)
            for w,j,c in zip(weights,ids,capacities):
                gamma=data.gamma[j];points=[F(0),c]
                if gamma>0:points.append(min(c,max(F(0),-mu/gamma)))
                dual+=w*max(-gamma*y*y/2-mu*y for y in points)
                yl=max(F(0),low[j]-d);yu=max(F(0),high[j]-d);p=[yl,yu]
                if gamma>0:p.append(min(yu,max(yl,-price/gamma)))
                naive+=w*max(-gamma*y*y/2-price*y for y in p)
            # Primal/dual equality proves exact pooling, rather than merely an upper bound.
            ys=tuple(map(F,row['service']))
            if len(ys)!=len(ids) or any(y<0 or y>c for y,c in zip(ys,capacities)):raise ValueError('Pooled service feasibility')
            q=sum(w*y for w,y in zip(weights,ys))
            primal=sum(w*(-data.gamma[j]*y*y/2-price*y) for w,j,y in zip(weights,ids,ys))
            if not qlo<=q<=qhi or q!=F(row['mean']) or primal!=dual or dual!=F(row['value']):raise ValueError('Pooled primal/dual equality')
            delta=W*(dual-naive)
            if delta<0 or delta!=F(row['correction']):raise ValueError('Invalid pooling correction')
            corr[key]=delta
    if used!=set(supplied):raise ValueError('Extraneous pooled service witnesses')
    def extra(i,v=None):
        return sum((corr[h,i] for h,kh in enumerate(prefixes) if i<kh and (v is None or v>=kh)),F(0))
    return tuple(low),tuple(high),extra


def check_bound(data,a,rho,B,m,groups,group_low,group_high,witness):
    low,high,extra=pooling_bounds(data,a,groups,group_low,group_high,witness)
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
        base,top=a[i],a[l]; total=extra(i,l)
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
        stop=[extra(i)+sum((p*(score[i]+short(j,x)) for j,p in enumerate(data.weights) if high[j]>=x),F(0)) for i,x in enumerate(a)]
        candidates=[alpha[r][i]+stop[i] for r in range(m) for i in range(n) if alpha[r][i] is not None]
    else:
        beta=[[F(x) for x in row] for row in witness['beta']]
        if len(beta)!=m or any(len(row)!=n for row in beta): raise ValueError('Suffix dimensions')
        stop=[extra(i)+sum((p*(score[i]-data.gamma[j]*(low[j]-x)**2/2-price*(low[j]-x)) for j,p in enumerate(data.weights) if low[j]>=x),F(0)) for i,x in enumerate(a)]
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
    data=model(record['model'])
    a,rho=tuple(map(F,record['catalog'])),tuple(map(F,record['charges']))
    B,m=F(record['promise']),record['budget']
    if record['schema']!='ndu-r49-eligibility-certificate-v1':raise ValueError('Schema')
    if not isinstance(m,int) or isinstance(m,bool) or not 1<=m<=len(a):raise ValueError('Budget')
    if not a or a[0]<0 or a[-1]>1 or len(a)!=len(rho) or any(x>=y for x,y in zip(a,a[1:])) or any(x<0 for x in rho):raise ValueError('Catalog')
    groups=record['groups'];covered=[];gw=[];gb=[];signatures=[]
    for ids in groups:
        if not ids:raise ValueError('Empty eligibility group')
        if any(not isinstance(j,int) or isinstance(j,bool) or not 0<=j<len(data.caps) for j in ids):raise ValueError('Invalid group membership')
        covered.extend(ids)
        if len({sum(x<=data.ceilings[j] for x in a) for j in ids})!=1:raise ValueError('Mixed eligibility')
        signatures.append(sum(x<=data.ceilings[ids[0]] for x in a))
        W=sum(data.weights[j] for j in ids);gw.append(W);gb.append(sum(data.weights[j]*data.caps[j] for j in ids)/W)
    if sorted(covered)!=list(range(len(data.caps))):raise ValueError('Incomplete eligibility partition')
    if len(set(signatures))!=len(groups) or record['eligibility_groups']!=len(groups) or record['raw_branches']!=len(data.caps):raise ValueError('Eligibility dimension metadata')
    means=Instance.make(gb,gw,[F(0)]*len(gw),[F(1)]*len(gw),data.r,data.curvature)
    verify_policy(data,a,rho,record['policy'],B,m)
    lower=F(record['policy']['value'])
    if lower!=F(record['lower_bound']): raise ValueError('Lower bound is not policy value')
    nodes=record['nodes']; seen=set(); leaves=[]
    expected=clipped_box(means,(a[0],)*len(groups),means.caps,B)
    if expected is None:raise ValueError('Infeasible root promise')
    def visit(idx,box,parent):
        if idx in seen: raise ValueError('Cover cycle or duplicate node')
        seen.add(idx); node=nodes[idx]
        if node['id']!=idx or node['parent']!=parent: raise ValueError('Tree identity')
        lo,hi=tuple(map(F,node['lower'])),tuple(map(F,node['upper_targets']))
        if (lo,hi)!=box: raise ValueError('Uncovered target region')
        bound=check_bound(data,a,rho,B,m,groups,lo,hi,node['witness'])
        if bound!=F(node['bound']): raise ValueError('Node bound mismatch')
        if node['children'] is None:
            leaves.append(idx); return
        axis,cut=node['split']; cut=F(cut)
        if not 0<=axis<len(lo) or not lo[axis]<cut<hi[axis]: raise ValueError('Invalid split')
        h=list(hi); h[axis]=cut; l=list(lo); l[axis]=cut
        expected_children=[z for z in (clipped_box(means,lo,h,B),clipped_box(means,l,hi,B)) if z is not None]
        if len(node['children'])!=len(expected_children): raise ValueError('Missing split child')
        for child,childbox in zip(node['children'],expected_children): visit(child,childbox,idx)
    visit(0,expected,None)
    if len(seen)!=len(nodes) or sorted(leaves)!=sorted(record['leaves']): raise ValueError('Incomplete leaf cover')
    upper=max([lower]+[F(nodes[i]['bound']) for i in leaves])
    if upper!=F(record['upper_bound']) or upper-lower!=F(record['gap']): raise ValueError('Global interval mismatch')
    eps=F(record['requested_epsilon'])
    if eps<0:raise ValueError('Negative accuracy')
    if record['status']!=('COMPLETE' if upper-lower<=eps else 'INTERRUPTED'):raise ValueError('False completion status')
    if record['evaluated_nodes']!=len(nodes):raise ValueError('Node accounting')
    return dict(status='PASS',checked_nodes=len(nodes),checked_leaves=len(leaves),lower=str(lower),upper=str(upper),gap=str(upper-lower))


if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('usage: check_certificate.py certificate.json')
    p=Path(sys.argv[1]);raw=gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes()
    print(json.dumps(check(json.loads(raw)),indent=2))
