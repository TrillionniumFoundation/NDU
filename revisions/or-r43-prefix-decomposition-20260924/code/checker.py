"""Independent rational checker; imports neither the DP nor the face generator.

Branch support is computed from explicit feasible targets and chord lotteries.
Price tables and the entire prefix partition are rebuilt from the input data.
Checking time is polynomial per recorded price and linear in tree size, apart
from per-prefix support evaluation. This checks a global bound, not just hashes.
"""
from fractions import Fraction as F


def support(model,j,book,lam,delta):
    b,gam=model.caps[j],model.gamma[j]
    levels=tuple(x for x in book if x<=b+delta)
    candidates={x for x in levels if x<=b}; candidates.add(b)
    if gam: candidates.add(max(levels[-1],min(b,levels[-1]-lam/gam)))
    vals=[]
    for t in candidates:
        if not levels[0]<=t<=b: continue
        if t>=levels[-1]:
            y=t-levels[-1]; val=model.reward(levels[-1])-gam*y*y/2
        else:
            upper=next(i for i,x in enumerate(levels) if x>=t)
            if levels[upper]==t: val=model.reward(t)
            else:
                u,v=levels[upper-1:upper+1]
                val=((v-t)*model.reward(u)+(t-u)*model.reward(v))/(v-u)
        vals.append(val-lam*t)
    return max(vals)


class BoundCheck:
    def __init__(self,model,a,charges,m,B,delta,lam):
        self.M,self.a,self.c,self.m,self.B,self.d,self.lam=model,a,charges,m,B,delta,lam
        n=len(a); g=[model.reward(x)-lam*x for x in a]
        self.g=g
        self.tail=[sum((p*support(model,j,(u,),lam,delta)
            for j,(p,b) in enumerate(zip(model.probabilities,model.caps)) if b>=u),F(0))
            for u in a]
        self.edge={}
        # Independent edge evaluation: maximize actual one/two-level lotteries.
        for i in range(n):
            for l in range(i+1,n):
                if g[l]<g[i]: continue
                self.edge[i,l]=sum((p*support(model,j,(a[i],a[l]),lam,delta)
                    for j,(p,b) in enumerate(zip(model.probabilities,model.caps))
                    if a[i]<=b<a[l]),F(0))
        self.rows={1:self.tail}
        for r in range(2,m+1):
            self.rows[r]=[max([self.tail[i]]+[e-charges[l]+self.rows[r-1][l]
                for (h,l),e in self.edge.items() if h==i]) for i in range(n)]
    def bound(self,p):
        M,a,ch,m,B,d,l=self.M,self.a,self.c,self.m,self.B,self.d,self.lam
        if not p:
            return l*B+max(self.rows[m][i]-ch[i] for i,x in enumerate(a)
                          if x<=min(B,min(M.caps)))
        if any(self.g[j]<self.g[i] for i,j in zip(p,p[1:])):
            v=sum(w*support(M,j,tuple(a[i] for i in p),l,d)
                  for j,w in enumerate(M.probabilities))
        else:
            v=sum((self.edge[i,j] for i,j in zip(p,p[1:])),F(0))+self.rows[m-len(p)+1][p[-1]]
        return l*B+v-sum(ch[i] for i in p)


def check(model,a,charges,m,B,delta,result):
    """Reject modified bounds, invalid lottery witnesses, and missing tree nodes."""
    m=min(m,len(a)); B,delta=F(B),F(delta)
    checks={}
    def bound(p,lam):
        if lam not in checks: checks[lam]=BoundCheck(model,a,charges,m,B,delta,lam)
        return checks[lam].bound(p)
    assert len(model.caps)==len(model.probabilities)==len(model.gamma)
    assert all(0<b<=1 for b in model.caps) and all(p>0 for p in model.probabilities)
    assert sum(model.probabilities)==1 and all(g>=0 for g in model.gamma)
    assert model.r>=model.q>0 and delta>=0
    assert all(x>=0 for x in charges) and len(a)==len(charges)
    assert all(u<v for u,v in zip(a,a[1:])) and 0<=a[0]<=a[-1]<=1
    alloc=result['allocation']; book=result['codebook']
    assert len(alloc.intermediate)==len(model.caps)
    assert all(u<v for u,v in zip(book,book[1:]))
    if not book or len(book)>m or any(x not in a for x in book):
        raise AssertionError('Invalid winning book.')
    if len(alloc.lotteries)!=len(model.caps): raise AssertionError('Wrong branch count.')
    value=F(0); mean=F(0)
    for j,(p,b,y,law) in enumerate(zip(model.probabilities,model.caps,
                                      alloc.intermediate,alloc.lotteries)):
        if y<0 or sum(w for _,w in law)!=1: raise AssertionError('Invalid law.')
        if any(w<0 or x not in book or y+x>b+delta for x,w in law):
            raise AssertionError('Risk or support violation.')
        t=y+sum(x*w for x,w in law)
        if t>b: raise AssertionError('Expectation cap violated.')
        mean+=p*t
        value+=p*(sum(w*model.reward(x) for x,w in law)-model.gamma[j]*y*y/2)
    value-=sum(charges[a.index(x)] for x in book)
    assert mean==B and value==result['lower']
    nodes={}
    for entry in result['ledger']:
        p=tuple(entry['prefix']); assert p not in nodes; nodes[p]=entry
    for entry in result['frontier']:
        p=tuple(entry['prefix']); assert p not in nodes
        nodes[p]=dict(entry,kind='frontier')
    stack=[()]; visited=set(); pending=[]
    while stack:
        p=stack.pop(); assert p in nodes and p not in visited
        visited.add(p); node=nodes[p]; kind=node['kind']
        if kind in ('pruned','frontier'):
            u=bound(p,node['price']); assert u==node['upper']
            if kind=='pruned': assert u<=value
            else: pending.append(u)
        elif kind=='leaf':
            # No unverified leaf objective: an inner price provides its upper.
            assert len(p)==m
            bookp=tuple(a[i] for i in p)
            # The checker may use all sampled prices; the solver evaluates exact
            # primal at a leaf. Its inner price must also be recorded.
            lam=node['inner_price']
            u=lam*B+sum(w*support(model,j,bookp,lam,delta)
                       for j,w in enumerate(model.probabilities))-sum(charges[i] for i in p)
            assert u==node['value'] and u<=value
        elif kind=='split':
            if p:
                lam=node['inner_price']; bookp=tuple(a[i] for i in p)
                u=lam*B+sum(w*support(model,j,bookp,lam,delta)
                           for j,w in enumerate(model.probabilities))-sum(charges[i] for i in p)
                assert u==node['value'] and u<=value
            expected=[p+(i,) for i in range(p[-1]+1 if p else 0,len(a))
                      if p or a[i]<=min(B,min(model.caps))]
            assert [tuple(x) for x in node['children']]==expected
            stack.extend(expected)
        else: raise AssertionError('Unknown partition state.')
    assert visited==set(nodes)
    assert result['upper']==max([value]+pending)
    assert result['exact']==(result['upper']==value)
    return dict(nodes_checked=len(visited),price_tables_checked=len(checks),
                exact=result['upper']==value,passed=True)


def load_and_check(path):
    import json,re
    from types import SimpleNamespace
    from pathlib import Path
    def decode(v):
        if isinstance(v,str) and re.fullmatch(r'-?\d+(?:/\d+)?',v): return F(v)
        if isinstance(v,list): return [decode(x) for x in v]
        if isinstance(v,dict): return {k:decode(x) for k,x in v.items()}
        return v
    data=decode(json.loads(Path(path).read_text()))
    mod=SimpleNamespace(**data['model'])
    mod.reward=lambda x:mod.r*x-mod.q*x*x/2
    ans=data['result']; ans['allocation']=SimpleNamespace(**ans['allocation'])
    return check(mod,tuple(data['catalog']),tuple(data['charges']),data['budget'],
                 data['promise'],data['delta'],ans)

if __name__=='__main__':
    import sys,json
    if len(sys.argv)!=2: raise SystemExit('Usage: checker.py certificate.json')
    print(json.dumps(load_and_check(sys.argv[1]),indent=2))
