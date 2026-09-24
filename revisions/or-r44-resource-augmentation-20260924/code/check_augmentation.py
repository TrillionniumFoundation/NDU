"""Independent exact checker: no recovery, allocator, or cell-solver imports."""
from fractions import Fraction as F
from pathlib import Path
from types import SimpleNamespace
import importlib.util, sys, json
P=Path(__file__).resolve().parents[2]/'or-r43-prefix-decomposition-20260924'/'code'/'checker.py'
spec=importlib.util.spec_from_file_location('r43_independent',P)
old=importlib.util.module_from_spec(spec); spec.loader.exec_module(old)

def check(data):
    def req(ok,msg):
        if not ok: raise ValueError(msg)
    a=tuple(map(F,data['catalog'])); rho=tuple(map(F,data['charges']))
    m=data['budget']; B=F(data['promise']); delta=F(data['delta']); eps=F(data['epsilon'])
    inp=data['model']; model=SimpleNamespace(**{k:tuple(map(F,v)) if isinstance(v,(list,tuple)) else F(v) for k,v in inp.items()})
    model.reward=lambda x:model.r*x-model.q*x*x/2
    b,p,g=model.caps,model.probabilities,model.gamma
    req(len(b)==len(p)==len(g)>0 and sum(p)==1 and all(x>0 for x in p),'model dimensions/weights')
    req(all(0<x<1 for x in b) and all(x>=0 for x in g) and model.r>=model.q>0,'model domain')
    req(len(a)==len(rho)>0 and list(a)==sorted(set(a)) and 0<=a[0]<=a[-1]<=1,'catalog')
    req(all(x>=0 for x in rho) and isinstance(m,int) and not isinstance(m,bool) and 1<=m<=len(a),'charges/budget')
    req(delta>=0 and eps>0 and a[0]<=min(B,min(b)) and B<=sum(w*x for w,x in zip(p,b)),'feasibility')
    cost=dict(zip(a,rho))
    def validate_policy(d,limit,root=None):
        book=tuple(map(F,d['book'])); t=tuple(map(F,d['targets'])); y=tuple(map(F,d['intermediate']))
        req(list(book)==sorted(set(book)) and 1<=len(book)<=limit and all(x in cost for x in book),'book')
        req(len(t)==len(y)==len(d['lotteries'])==len(b),'policy dimensions')
        net=-sum(cost[x] for x in book)
        for j,raw in enumerate(d['lotteries']):
            law=[(F(x),F(q)) for x,q in raw]
            req(law and all(x in book and q>0 for x,q in law) and sum(q for _,q in law)==1,'support/normalization')
            req(y[j]>=0 and 0<=t[j]<=b[j] and y[j]+sum(x*q for x,q in law)==t[j],'branch target')
            req(all(y[j]+x<=b[j]+delta for x,q in law),'risk')
            net+=p[j]*(sum(q*model.reward(x) for x,q in law)-g[j]*y[j]**2/2)
        total=sum(w*x for w,x in zip(p,t))
        req(F(d['charge'])==sum(cost[x] for x in book) and F(d['value'])==net,'paid charge/value')
        req(F(d['total'])==total and (root is None or total==root),'root promise')
        return book,t,total,net
    ends=[]
    for name in ('left','right'):
        e=data[name]; book,t,s,j=validate_policy(e['policy'],m)
        lam=F(e['price']); expected=old.BoundCheck(model,a,rho,m,B,delta,lam).bound(())
        req(F(e['upper'])==expected,'independent global price bound')
        req(j+lam*(B-s)==expected,'price optimality')
        req(book[0]<=min(B,min(b)),'priced-book domain')
        ends.append((e,book,t,s,j,lam,expected))
    left,right=ends
    req(left[5]<=right[5] and left[3]>=B>=right[3],'price/target bracket')
    theta=F(data['theta']); req(0<=theta<=1,'mixing weight')
    req(theta*left[3]+(1-theta)*right[3]==B,'mixture promise')
    union,t,total,net=validate_policy(data['augmented_policy'],min(2*m,len(a)),B)
    req(set(union)==set(left[1])|set(right[1]),'fixed union alphabet')
    req(t==tuple(theta*x+(1-theta)*y for x,y in zip(left[2],right[2])),'mixed branch targets')
    mixed=theta*left[4]+(1-theta)*right[4]
    excess=sum(cost[x] for x in union)-theta*sum(cost[x] for x in left[1])-(1-theta)*sum(cost[x] for x in right[1])
    spread=(right[5]-left[5])*(left[3]-B)*(B-right[3])/(left[3]-right[3]) if left[3]!=right[3] else F(0)
    upper=min(left[6],right[6]); original=validate_policy(data['original_policy'],m,B)
    req(F(data['mixed_value'])==mixed and F(data['charge_excess'])==excess and excess>=0,'charge excess/mixture')
    req(F(data['price_error'])==spread and 0<=spread<=eps,'price error')
    req(net>=mixed-excess>=upper-spread-excess,'resource guarantee')
    req(F(data['original_lower'])==original[3]<=upper==F(data['original_upper']),'original-budget interval')
    return dict(valid=True,original_gap=str(upper-original[3]),union_size=len(union),price_error=str(spread),charge_excess=str(excess),exact_promise_residual='0',exact_positive_risk_violation='0')

if __name__=='__main__':
    for path in sys.argv[1:]: print(path,json.dumps(check(json.loads(Path(path).read_text())),sort_keys=True))
