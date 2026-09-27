"""Independent exhaustive root-dual experiment on a frozen, balanced panel.

The ground truth enumerates original books and builds the concave upper hull of
all fixed-book value vertices. It does not use the price-path dynamic program.
The price solver is run only after this independent ground truth is computed.
"""
from __future__ import annotations
from pathlib import Path
from itertools import combinations
import collections, hashlib, json, time, platform, sys, gzip
from rational import F, encode, digest, write
from check_price import model
R=Path(__file__).resolve().parents[1]

def ground_truth(spec):
    w,b,g,t,r,q,a,fees,B,m=model(spec)
    assert not any(g) and not any(q) and len(set(r))==1
    rate=r[0];bar=sum(x*y for x,y in zip(w,b));books=[];points={}
    for s in range(1,m+1):
        for idx in combinations(range(len(a)),s):
            c=tuple(a[i] for i in idx)
            if c[0]>min(B,min(b)):continue
            D=sum(wj*min(bj,max(x for x in c if x<=tj)) for wj,bj,tj in zip(w,b,t))
            cost=sum(fees[i] for i in idx);vertices=[]
            for z in sorted({c[0],D,bar}):
                y=rate*min(z,D)-cost;vertices.append((z,y));points[z]=max(y,points.get(z,y))
            books.append(dict(book=c,capacity=D,cost=cost,vertices=vertices,value=rate*min(B,D)-cost))
    hull=[]
    for x,y in sorted(points.items()):
        while len(hull)>1:
            x0,y0=hull[-2];x1,y1=hull[-1]
            if (y1-y0)*(x-x1)>(y-y1)*(x1-x0):break
            hull.pop()
        hull.append((x,y))
    if B==hull[0][0]:lam=rate+1;upper=hull[0][1]
    elif B==hull[-1][0]:lam=-F(1);upper=hull[-1][1]
    else:
        i=next(i for i in range(len(hull)-1) if hull[i][0]<=B<=hull[i+1][0])
        x0,y0=hull[i];x1,y1=hull[i+1];lam=(y1-y0)/(x1-x0);upper=y0+lam*(B-x0)
    intercept=max(max(y-lam*z for z,y in c['vertices']) for c in books)
    assert upper==lam*B+intercept
    active=[]
    for c in books:
        high=max(y-lam*z for z,y in c['vertices'])
        if high!=intercept:continue
        zs=[z for z,y in c['vertices'] if y-lam*z==high];lo,hi=min(zs),max(zs)
        distance=max(lo-B,B-hi,F(0))
        assert upper-c['value']<=(rate+abs(lam))*distance
        active.append(dict(book=c['book'],support_low=lo,support_high=hi,distance=distance))
    lower=max(c['value'] for c in books);supported=any(x['distance']==0 for x in active)
    assert (upper==lower)==supported
    return encode(dict(books=len(books),price=lam,lower=lower,root_upper=upper,
                       root_gap=upper-lower,same_book_support=supported,active_books=active,hull=hull))

def design():
    from price_path import Model,spec_for
    out=[]
    caps=[F(0),F(1,3),F(2,3),F(1)];a=[F(i,6) for i in range(7)]
    for ceilings in (caps,[F(0),F(1,2),F(5,6),F(1)]):
        mod=Model.make(caps,[F(1,4)]*4,[0]*4,ceilings,1,0)
        for m in (2,4):
            for promise in (F(1,5),F(3,5),F(9,10)):
                for fees in ([F(0)]*7,[F(1,50)]*7,[F(1,4)]*7,
                             [F(1,50)+F(i%3,100) for i in range(7)]):
                    s=spec_for(mod,a,fees,mod.cap_total*promise,m)
                    out.append(dict(id=f'root-{len(out):02d}',spec=s,epsilon='1/1000',seconds=2))
    return out

def run():
    cases=design();source=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    frozen=dict(schema='NDU-R63-root-panel-v1',source_sha256=source,
                source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((R/'code').glob('*.py'))},
                environment={'python':sys.version,'platform':platform.platform()},cases=cases,
                design='48 complete factorial cells; not random independent observations; no time-based filtering')
    write(R/'results/SUPPORT_FREEZE63.json',frozen)
    from price_path import solve
    from binding63 import verify_bound
    rows=[]
    for c in cases:
        begin=time.perf_counter();truth=ground_truth(c['spec']);exact_seconds=time.perf_counter()-begin
        ans=solve(c['spec'],F(c['epsilon']),seconds=c['seconds'],max_nodes=100000)
        tick=time.perf_counter();receipt=verify_bound(ans['certificate'],c['spec']);verify_seconds=time.perf_counter()-tick
        assert F(ans['lower'])<=F(truth['lower'])<=F(ans['upper'])
        raw=gzip.compress(json.dumps(ans['certificate'],sort_keys=True).encode(),mtime=0)
        certificate='support_certificates/'+c['id']+'.json.gz'
        target=R/'results'/certificate;target.parent.mkdir(exist_ok=True);target.write_bytes(raw)
        rows.append(encode(dict(id=c['id'],input_sha256=digest(c['spec']),truth=truth,
            certificate=certificate,certificate_sha256=hashlib.sha256(raw).hexdigest(),
            ground_truth_seconds=exact_seconds,price_status=ans['status'],price_seconds=ans['seconds'],
            verification_seconds=verify_seconds,lower=ans['lower'],upper=ans['upper'],
            mechanics=ans['mechanics'],receipt=receipt)))
    count=collections.Counter(x['truth']['same_book_support'] for x in rows)
    out=dict(status='PASS',cases=len(rows),supported=count[True],positive_root_gap=count[False],
             enumerated_books=sum(x['truth']['books'] for x in rows),rows=rows,
             scope='Exhaustive root-dual truth with independent bound and original-policy checks; a diagnostic panel, not field evidence or a calibrated routing rule.')
    write(R/'results/SUPPORT_STUDY63.json',out)
    print('SUPPORT',len(rows),dict(count),out['enumerated_books'],flush=True)
if __name__=='__main__':run()
