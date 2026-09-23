#!/usr/bin/env python3
"""Independent exact checker. Does not import price_solver or an optimizer.

It verifies whole response functions (not just the reported root), state flow,
all local KKT conditions, conditional obligations, and an extensive-form dual
objective represented by compact state weights. Floating timings are not proofs.
"""
from fractions import Fraction as Q
from bisect import bisect_right
from pathlib import Path
import json, sys, hashlib


def check(bundle):
    data=bundle['instance']; cert=bundle['certificate']; nodes=data['nodes']; n=len(nodes)
    beta=Q(data['beta']); b0=Q(data['promise'])
    cs=[]; checks=0
    for c in cert['curves']:
        ks=list(map(Q,c['knots'])); ls=[tuple(map(Q,a)) for a in c['lines']]
        assert len(ls)==len(ks)+1 and ks==sorted(set(ks))
        assert ls[0][0]==ls[-1][0]==0 and all(m<=0 for m,b in ls)
        for i,k in enumerate(ks):
            assert ls[i][0]*k+ls[i][1]==ls[i+1][0]*k+ls[i+1][1]
        cs.append((ks,ls))
    def val(i,p):
        k,l=cs[i]; m,b=l[bisect_right(k,p)]; return m*p+b
    for i,v in enumerate(nodes):
        r,q,a,lo,hi,cap=[Q(v[k]) for k in ('r','q','a','lo','hi','cap')]
        assert q>0 and a>0 and lo<=hi and 0<beta<=1
        edges=[(j,Q(p)) for j,p in v['edges']]
        assert all(i<j<n and p>0 for j,p in edges)
        assert not edges or sum(p for j,p in edges)==1
        ks=set(cs[i][0])|{(r-q*lo)/a,(r-q*hi)/a}
        for j,p in edges: ks.update(cs[j][0])
        al=cert['barriers'][i]; al=None if al is None else Q(al)
        if al is not None: ks.add(al)
        ks=sorted(ks); probes=[ks[0]-1,ks[-1]+1]+ks+[(x+y)/2 for x,y in zip(ks,ks[1:])]
        for z in probes:
            raw=a*max(lo,min(hi,(r-a*z)/q))+beta*sum(p*val(j,z) for j,p in edges)
            assert val(i,z)==min(cap,raw),('response identity',i,z)
            s=z if al is None else max(z,al)
            x=max(lo,min(hi,(r-a*s)/q))
            payment=a*x+beta*sum(p*val(j,s) for j,p in edges)
            assert payment==val(i,z)<=cap
            assert (s-z)*(cap-payment)==0
            checks+=1
    states={(s['node'],Q(s['incoming'])):s for s in cert['states']}
    assert len(states)==len(cert['states'])
    eta=Q(cert['root_price']); assert val(0,eta)==b0
    flow={(0,eta):Q(1)}; primal=Q(0); rootpay=Q(0); dual=eta*b0
    for (i,p),s in sorted(states.items()):
        v=nodes[i]; r,q,a,lo,hi,cap=[Q(v[k]) for k in ('r','q','a','lo','hi','cap')]
        x,w,eff,chi,low,up,pay=[Q(s[k]) for k in ('x','weight','price','chi','lower','upper','payment')]
        assert w==flow.get((i,p),0)>0 and lo<=x<=hi
        assert eff==p+chi and min(chi,low,up)>=0
        assert r-q*x-a*eff+low-up==0
        assert low*(x-lo)==up*(hi-x)==0
        assert pay==val(i,p)<=cap and chi*(cap-pay)==0
        expected=a*x
        for j,prob in v['edges']:
            prob=Q(prob); expected+=beta*prob*val(j,eff)
            key=(j,eff); assert key in states
            flow[key]=flow.get(key,Q(0))+w*beta*prob
        assert pay==expected
        primal+=w*(r*x-q*x*x/2); rootpay+=w*a*x
        dual+=w*(chi*cap+up*hi-low*lo+(r-a*eff+low-up)**2/(2*q))
        checks+=1
    assert set(flow)==set(states)
    assert primal==dual==Q(cert['value'])
    assert rootpay==Q(cert['payment'])==b0
    knots={v for ks,ls in cs for v in ks}
    assert len(knots)<=3*n and len(states)<=n*(n+1)
    st=cert['statistics']
    assert st['public_nodes']==n and st['global_breakpoints']==len(knots)
    assert st['reachable_price_pairs']==len(states)
    assert st['stored_segments']==sum(len(ls) for ks,ls in cs)
    return {'name':data['name'],'checks':checks,'value':str(primal),'dual':str(dual),
            'public_nodes':n,'price_states':len(states),'global_breakpoints':len(knots)}


def main():
    root=Path(__file__).resolve().parent
    evidence=json.loads((root/'results/evidence.json').read_text())
    rows=[check(x) for x in evidence['instances']]
    assert evidence['memory_example']['full']=='27/32'
    # Independent one-dimensional derivation of the optimal public-only table:
    # root 0, common terminal c, A action y, B action 1-2c-y.
    # A cap y+c<=1/4. For fixed c, reward increases up to y=1/4-c;
    # the resulting derivative 5/2-2*c is positive, hence c=1/4,y=0.
    c=Q(1,4); y=Q(0); z=1-2*c-y
    public_only=2*c-c*c/2-(y*y+z*z)/4
    assert public_only==Q(13,32)
    assert Q(27,32)-public_only==Q(7,16)
    # On the triangular domain, dW/dy=1/2-c-y>=1/4, so y=1/4-c.
    # Substitution gives dW/dc=5/2-2*c>=2, so c=1/4.
    assert Q(1,2)-c-y>=Q(1,4) and Q(5,2)-2*c>0 and z>=y
    report={'status':'PASS','instances':len(rows),'exact_assertion_groups':sum(r['checks'] for r in rows),
            'records':rows,'evidence_sha256':hashlib.sha256((root/'results/evidence.json').read_bytes()).hexdigest(),
            'memory_example_public_only':str(public_only),'memory_example_gain':'7/16'}
    target=root/'results/verification.json'
    if '--check' in sys.argv:
        assert json.loads(target.read_text())==report, 'Stored verification differs'
    else:
        target.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))

if __name__=='__main__': main()
