"""Deterministic exact regression tests for the R60 theorems, not proof substitutes."""
from __future__ import annotations
from pathlib import Path
import copy, itertools, json, random, sys
from fractions import Fraction as Q
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'code'))
from tariff60 import solve
from check_tariff60 import verify
from paths60 import recognize,bounded_recognize,repair
from price_path import Model,spec_for,normalize,allocate,Oracle,support_range
from rational import F,encode,digest
from deficit import max_convolution


def cases():
    for seed in range(160):
        rng=random.Random(600100+seed);n=3+seed%7;k=2+seed%5
        a=sorted(rng.sample(range(1,32),n-1));a=[F(0)]+[F(v,32) for v in a]
        b=[F(rng.randrange(2,33),32) for _ in range(k)]
        if seed%9==0:b[0]=F(0)
        tau=[min(F(1),x+F(rng.randrange(9),32)) for x in b]
        weights=[rng.randrange(1,8) for _ in b];weights=[F(v,sum(weights)) for v in weights]
        d=Model.make(b,weights,[0]*k,tau,F(1+seed%3),0)
        fees=[F(seed%4,20)]*n
        for j in rng.sample(range(n),seed%4):fees[j]+=F(1+j,37)
        B=d.cap_total*F(1+seed%5,5);m=1+seed%min(n,5)
        yield spec_for(d,a,fees,B,m)
    # No zero anchor: all start choices must respect the original feasibility rule.
    for seed in range(12):
        a=[F(v,16) for v in range(1,9)]
        d=Model.make([F(1,4),F(5,8)],[F(2,5),F(3,5)],[0,0],[F(1,2),1],1,0)
        yield spec_for(d,a,[F(1,17)]*8,F(1,8)+F(seed,64),1+seed%4)


def test_tariffs():
    count=books=0;maxbits=0;rejects=0
    for spec in cases():
        ans=solve(spec);cert=ans['certificate'];verify(cert,digest(spec))
        d,a,rho,B,m=normalize(spec);best=None
        for s in range(1,m+1):
            for book in itertools.combinations(a,s):
                if book[0]>min(B,min(d.caps)):continue
                value=allocate(d,book,B,dict(zip(a,rho)))['value'];books+=1
                best=value if best is None else max(best,value)
        assert ans['lower']==best
        if count<24:
            bad=copy.deepcopy(cert);bad['branches']=bad['branches'][:-1]
            try:verify(bad)
            except (ValueError,KeyError):rejects+=1
            else:raise AssertionError('Incomplete subset cover accepted')
            bad=copy.deepcopy(cert)
            for branch in bad['branches']:
                changed=False
                for row in branch['rows']:
                    for i,x in enumerate(row):
                        if x is not None:row[i]=str(F(x)+1);changed=True;break
                    if changed:break
                if changed:break
            try:verify(bad)
            except (ValueError,KeyError):rejects+=1
            else:raise AssertionError('False capacity accepted')
        count+=1
    # Binary encoding stress changes arithmetic bit length, not state count.
    for bits in (32,64,128,256,512):
        D=2**bits+1;a=[F(v,D) for v in (0,1,2,3,5,8)]
        d=Model.make([F(4,D),F(8,D)],[F(1,3),F(2,3)],[0,0],[F(6,D),F(8,D)],1,0)
        spec=spec_for(d,a,[F(0)]+[F(1,D*100)]*5,F(2,D),4)
        ans=solve(spec);verify(ans['certificate']);maxbits=max(maxbits,D.bit_length())
        exact=max(allocate(d,book,F(2,D),dict(zip(a,map(F,spec['charges']))))['value']
            for s in range(1,5) for book in itertools.combinations(a,s) if book[0]<=F(2,D))
        assert ans['lower']==exact
    return dict(instances=count,big_integer_instances=5,books_cross_checked=books,
                maximum_input_denominator_bits=maxbits,corrupt_certificates_rejected=rejects)


def enumerate_paths(vertices,edges,source,sink,h=None):
    adj={v:[] for v in vertices}
    for u,v,c in edges:adj[u].append((v,F(c)))
    out=[]
    def visit(u,path,total):
        if u==sink:out.append((path,total));return
        if h is not None and len(path)-1>=h:return
        for v,c in adj[u]:visit(v,path+[v],total+c)
    visit(source,[source],F(0));return out


def test_paths():
    accepted=rejected=bounded=0
    for seed in range(160):
        rng=random.Random(601000+seed);n=4+seed%7;vs=list(range(n));ss=[0,1]
        potentials=[F(n-i,7) for i in vs];potentials[-1]=F(0)
        pairs={(i,i+1) for i in range(n-1)}|{(0,n-1),(1,n-1)}
        pairs|={(i,j) for i in vs for j in vs if i<j and rng.random()<.25}
        edges=[(i,j,potentials[i]-potentials[j]) for i,j in sorted(pairs)]
        ans=recognize(vs,edges,ss,n-1);assert ans['accepted'];accepted+=1
        for s in ss:assert ans['potential'][s]==potentials[s]
        changed=[(u,v,c+F(1,13) if (u,v)==(0,n-1) else c) for u,v,c in edges]
        ans=recognize(vs,changed,ss,n-1);assert not ans['accepted'];rejected+=1
        costs={(u,v):c for u,v,c in changed};p,q=ans['witness']
        assert p[0]==q[0] and p[-1]==q[-1]==n-1
        assert sum(costs[u,v] for u,v in zip(p,p[1:]))!=sum(costs[u,v] for u,v in zip(q,q[1:]))
        for h in (1,2,n-1):
            bounded+=1;ans=bounded_recognize(vs,changed,ss,n-1,h)
            brute={s:enumerate_paths(vs,changed,s,n-1,h) for s in ss}
            ok=all(len(set(x for p,x in paths))<=1 for paths in brute.values())
            assert ans['accepted']==ok
            if not ok:
                p,q=ans['witness'];assert max(len(p),len(q))-1<=h
                assert sum(costs[u,v] for u,v in zip(p,p[1:]))!=sum(costs[u,v] for u,v in zip(q,q[1:]))
    # Full-graph rejection, bounded-path acceptance is deliberately nonvacuous.
    edges=[(0,2,F(1)),(0,1,F(1)),(1,2,F(1))]
    assert not recognize(range(3),edges,[0],2)['accepted']
    assert bounded_recognize(range(3),edges,[0],2,1)['accepted']
    for seed in range(400):
        rng=random.Random(602000+seed);h=1+seed%8
        caps=[F(rng.randrange(1,100),101) for _ in range(h)]
        original=[c*F(rng.randrange(101),100) for c in caps];R0=sum(original);eta=F(1,53)
        rounded=[int(w//eta)*eta for w in original];done=repair(caps,rounded,R0)
        assert sum(done)==R0 and all(0<=w<=c for c,w in zip(caps,done))
        assert sum(w-z for w,z in zip(done,rounded))<h*eta
        Qn=1+seed%41;row=[None if rng.random()<.55 else F(rng.randrange(-9,10)) for _ in range(Qn)]
        L=seed%13;slopes=sorted([rng.randrange(-5,8) for _ in range(L)],reverse=True);ker=[F(0)]
        for slope in slopes:ker.append(ker[-1]+slope)
        vals,ptr,_=max_convolution(row,ker)
        for t0 in range(Qn):
            possible=[(row[i]+ker[t0-i],i) for i in range(Qn) if row[i] is not None and 0<=t0-i<len(ker)]
            if possible:
                best=max(v for v,i in possible);idx=min(i for v,i in possible if v==best)
                assert vals[t0]==best and ptr[t0]==idx
            else:assert vals[t0] is None
    return dict(potential_graphs=accepted,perturbed_witnesses=rejected,
                bounded_vs_exhaustive=bounded,round_repair=400,holey_convolution=400,
                maximum_vertices=10,maximum_edges=45)


def test_price_gap():
    # Uniform fees, a forced zero command, an actual strict price gap.
    d=Model.make([0,1],[F(1,2)]*2,[0,0],[0,1],1,0)
    spec=spec_for(d,[0,1],[F(1,4)]*2,F(1,8),2)
    from check_price import price_bound
    upper=price_bound(spec,F(1,2),set(),set(),{})
    ans=solve(spec);assert ans['lower']==F(-1,4) and upper==F(-3,16)
    return dict(exact_value=str(ans['lower']),supporting_price_upper=str(upper),gap='1/16')


def main():
    ans=dict(schema='NDU-R60-exact-regressions-v1',status='PASS',tariff=test_tariffs(),
             paths=test_paths(),price_gap=test_price_gap())
    text=json.dumps(ans,indent=2)+'\n'
    if '--output' in sys.argv:Path(sys.argv[sys.argv.index('--output')+1]).write_text(text)
    print(text)
if __name__=='__main__':main()
