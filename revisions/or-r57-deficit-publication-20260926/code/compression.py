"""Construct cap-class compression from an original feasible policy."""
from rational import F
from price_path import normalize,Model,allocate

def compress(spec,policy):
    d,a,rho,B,m=normalize(spec)
    book=tuple(map(F,policy['book']));targets=list(map(F,policy['targets']))
    used=set();classes=[]
    types=sorted(set(zip(d.caps,d.reward_r,d.reward_q)))
    for cap,reward_r,reward_q in types:
        ids=[j for j,b in enumerate(d.caps) if (b,d.reward_r[j],d.reward_q[j])==(cap,reward_r,reward_q)]
        weight=sum(d.weights[j] for j in ids)
        mean=sum(d.weights[j]*targets[j] for j in ids)/weight
        if mean in book:keep=(mean,)
        elif book[-1]<mean:keep=(book[-1],)
        else:keep=(max(z for z in book if z<mean),min(z for z in book if z>mean))
        sub=Model.make([d.caps[j] for j in ids],[d.weights[j]/weight for j in ids],[d.gamma[j] for j in ids],[d.ceilings[j] for j in ids],reward_r,reward_q)
        pol=allocate(sub,keep,mean,{z:F(0) for z in keep})
        classes.append({'history_indices':ids,'conditional_promise':mean,'book':keep,'policy':pol})
        used.update(keep)
    out=allocate(d,tuple(sorted(used)),B,dict(zip(a,rho)))
    if len(used)>min(len(book),2*len(types)) or out['value']<F(policy['value']):
        raise ArithmeticError('Cap compression dominance failed')
    return {'policy':out,'classes':classes,'distinct_caps':len(set(d.caps)),'joint_types':len(types)}
