"""Exact reduction and prototype-frontier tests; no optimizer used for soundness.
Run from any directory. All model inputs and comparisons use Fraction.
"""
from __future__ import annotations
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
import hashlib, json, random, sys
ROOT=Path(__file__).resolve().parents[3]
OLD=ROOT/'revisions/or-r58-structural-referee-20260926/code'
sys.path.insert(0,str(OLD))
from price_path import Model, spec_for, normalize, allocate
from rational import encode
R=Path(__file__).resolve().parents[1]

def grouped_sum_model(groups: list[list[int]], target: int):
    """Group equality encoding is a source-instance property, not assumed here."""
    if not groups or any(not a or any(type(v)!=int or v<=0 for v in a) for a in groups):
        raise ValueError('Nonempty groups of positive integers required')
    g=len(groups); M=max(map(max,groups)); T=2*(g+1)*M; K=(2*g+1)*T
    if not 0<=target<=sum(map(max,groups)):raise ValueError('Target outside aggregate range')
    base=[F(i,g+1) for i in range(1,g+1)]
    caps=[F(0)]; a={F(0):F(0)}; optional={}
    for i,(l,group) in enumerate(zip(base,groups)):
        a[l]=F(0);caps.extend([l,l+F(max(group),T)])
        for w in set(group):
            z=l+F(w,T);a[z]=F(w,2*K);optional[z]=(i,w)
    D0=F(2,2*g+1)*sum(base); B=D0+F(target,K); zeta=D0+F(target,2*K)
    catalog=tuple(sorted(a)); d=Model.make(caps,[F(1,2*g+1)]*(2*g+1),[0]*(2*g+1),caps,1,0)
    return spec_for(d,catalog,tuple(a[z] for z in catalog),B,2*g+1),dict(g=g,T=T,K=K,D0=D0,target=target,zeta=zeta,baselines=base,optional=optional)

def linear_value(spec,book):
    """Independent original-model value for f(x)=x, h=0, tau=b, zero in book."""
    d,a,rho,B,m=normalize(spec)
    if not book or book[0]!=0 or len(book)>m:raise ValueError('Infeasible book')
    D=sum(p*max(z for z in book if z<=b) for p,b in zip(d.weights,d.caps))
    return min(B,D)-sum(dict(zip(a,rho))[z] for z in book)

def clique_groups(classes: list[list[int]], edges: set[tuple[int,int]]):
    """No-carry multicolored-clique to grouped-sum reduction (full construction)."""
    k=len(classes); pairs=list(combinations(range(k),2)); g=k+len(pairs)
    n=max(v for c in classes for v in c)+1; base=(2*g+2)*(n+1)+1
    incidences=[(i,j,i) for i,j in pairs]+[(i,j,j) for i,j in pairs]
    pos={c:g+t for t,c in enumerate(incidences)}
    target=sum(base**i for i in range(g))+sum(n*base**p for p in pos.values())
    groups=[]
    for i,cl in enumerate(classes):
        vals=[]
        for v in cl:
            val=base**i
            for p in pairs:
                if i in p:val+=(v+1)*base**pos[(*p,i)]
            vals.append(val)
        groups.append(vals)
    for t,(i,j) in enumerate(pairs):
        vals=[]
        for v in classes[i]:
            for w in classes[j]:
                if (min(v,w),max(v,w)) in edges:
                    vals.append(base**(k+t)+(n-v-1)*base**pos[(i,j,i)]+(n-w-1)*base**pos[(i,j,j)])
        if not vals:return None,target
        groups.append(vals)
    return groups,target

def grouped_medians(slopes,weights,caps,G):
    """Exact cap-preserving weighted 1D medoids; return optimum and prototypes.
    Slopes and weights are rational. Distortion is normalized by catalog span.
    """
    if not (len(slopes)==len(weights)==len(caps)) or any(w<=0 for w in weights):raise ValueError('Invalid data')
    bycap={}
    for j,b in enumerate(caps):bycap.setdefault(b,[]).append(j)
    if G<len(bycap):raise ValueError('Too few groups to preserve all caps')
    G=min(G,len(slopes)); per=[]
    for b,ids in sorted(bycap.items()):
        ids.sort(key=lambda j:(slopes[j],j));n=len(ids);cost={};center={}
        pw=[F(0)]; ps=[F(0)]
        for j in ids:pw.append(pw[-1]+weights[j]);ps.append(ps[-1]+weights[j]*slopes[j])
        for l in range(n):
            med=l
            for h in range(l,n):
                total=pw[h+1]-pw[l]
                while 2*(pw[med+1]-pw[l])<total:med+=1
                x=slopes[ids[med]]
                cost[l,h]=x*(pw[med+1]-pw[l])-(ps[med+1]-ps[l])+(ps[h+1]-ps[med+1])-x*(pw[h+1]-pw[med+1])
                center[l,h]=ids[med]
        dp={(0,0):(F(0),[])}
        for t in range(1,min(G,n)+1):
            for h in range(t,n+1):
                candidates=[]
                for l in range(t-1,h):
                    if (t-1,l) in dp:
                        v,cs=dp[t-1,l];candidates.append((v+cost[l,h-1],cs+[center[l,h-1]]))
                dp[t,h]=min(candidates,key=lambda z:(z[0],z[1]))
        per.append({t:dp[t,n] for t in range(1,min(G,n)+1)})
    dp={0:(F(0),[])}
    for options in per:
        nxt={}
        for s,(v,cs) in dp.items():
            for t,(w,ds) in options.items():
                if s+t<=G and (s+t not in nxt or v+w<nxt[s+t][0]):nxt[s+t]=(v+w,cs+ds)
        dp=nxt
    return min(dp.values(),key=lambda z:(z[0],z[1]))

def run_tests():
    rng=random.Random(590927);counts=dict(reduction_books=0,allocation_crosschecks=0,clique_instances=0,grouping_frontiers=0)
    for g in (1,2,3):
        for rep in range(8):
            groups=[sorted(rng.sample(range(1,10),2)) for _ in range(g)]
            W=rng.randrange(1,sum(map(max,groups))+1);spec,meta=grouped_sum_model(groups,W);d,a,rho,B,m=normalize(spec)
            best=None
            for ell in range(1,m+1):
                for tail in combinations(a[1:],ell-1):
                    book=(F(0),)+tail;value=linear_value(spec,book)
                    S=sum(meta['optional'][z][1] for z in book if z in meta['optional'])
                    bound=meta['zeta']-F(abs(S-W),2*meta['K'])
                    assert value<=bound
                    if value>=meta['zeta']:
                        assert all(l in book for l in meta['baselines']) and S==W
                        groups_used=[meta['optional'][z][0] for z in book if z in meta['optional']]
                        assert len(groups_used)==len(set(groups_used))
                    best=value if best is None else max(best,value);counts['reduction_books']+=1
                    if counts['reduction_books']%83==0:
                        assert allocate(d,book,B,dict(zip(a,rho)))['value']==value;counts['allocation_crosschecks']+=1
            # Here source allows absent groups; no-carry group digits later force all groups.
            possible=any(sum(v)==W for v in product(*[[0]+g0 for g0 in groups]))
            assert (best>=meta['zeta'])==possible
    for k in (2,3):
        classes=[list(range(2*i,2*i+2)) for i in range(k)]
        for rep in range(24):
            edges={(v,w) for i,j in combinations(range(k),2) for v in classes[i] for w in classes[j] if rng.random()<.5}
            yes=any(all((min(v,w),max(v,w)) in edges for v,w in combinations(choice,2)) for choice in product(*classes))
            groups,W=clique_groups(classes,edges)
            if groups is None:assert not yes
            else:
                witness=next((z for z in product(*groups) if sum(z)==W),None)
                assert (witness is not None)==yes
                if W<=sum(map(max,groups)):
                    spec,meta=grouped_sum_model(groups,W)
                    if witness:
                        book=tuple(sorted([F(0)]+meta['baselines']+[l+F(v,meta['T']) for l,v in zip(meta['baselines'],witness)]))
                        assert linear_value(spec,book)==meta['zeta']
            counts['clique_instances']+=1
    for rep in range(40):
        n=8;slopes=[F(rng.randrange(4,17),4) for _ in range(n)];weights=[F(rng.randrange(1,8)) for _ in range(n)]
        total=sum(weights);weights=[w/total for w in weights];caps=[F(j%2+1,3) for j in range(n)]
        for G in range(2,6):
            v,cs=grouped_medians(slopes,weights,caps,G)
            oracle=min(sum(weights[j]*min(abs(slopes[j]-slopes[c]) for c in cc if caps[c]==caps[j]) for j in range(n)) for cc in combinations(range(n),G) if set(caps[c] for c in cc)==set(caps))
            assert v==oracle;counts['grouping_frontiers']+=1
    out={'schema':'NDU-R59-exact-structural-tests-v1','seed':590927,'counts':counts,'status':'PASS','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'note':'Finite regressions supplement, not replace, the general proofs.'}
    (R/'results').mkdir(exist_ok=True);(R/'results/STRUCTURAL59.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':run_tests()
