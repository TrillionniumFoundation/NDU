"""Frozen R53 regression and controlled study; never overwrites R52 evidence."""
from __future__ import annotations
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
from dataclasses import asdict
import copy,gzip,hashlib,json,platform,random,sys,time
from screening import Instance,context_gain,bound_for,screen,solve,solve_screened,instance_record,encode,digest,fixed_allocate
from check_screening import verify,independent_bound,canonical_value
from resource_path import arc
from check_resource import verify as verify_resource
HERE=Path(__file__).resolve().parent;OUT=HERE.parent/'results';OUT.mkdir(exist_ok=True)

def dump(path,obj):
    path.write_text(json.dumps(obj,indent=2,default=str)+'\n')


def books(data,a,B,m):
    for s in range(1,min(m,len(a))+1):
        for c in combinations(a,s):
            if c[0]<=min(B,min(data.caps)):yield c


def enumerate_opt(data,a,rho,B,m):
    costs=dict(zip(a,rho));winner=None;winbook=None
    for c in books(data,a,B,m):
        v=fixed_allocate(data,c,B,costs)['value']
        if winner is None or v>winner:winner,winbook=v,c
    return winner,winbook


def value(data,j,book,t):
    eligible=[x for x in book if x<=data.ceilings[j]]
    return canonical_value(t,eligible,data.r,data.curvature,data.gamma[j])


def regress():
    begin=time.perf_counter();rng=random.Random(530926);counts=dict(models=0,capacity_identities=0,
        context_envelopes=0,pointwise_deletion_checks=0,exhaustive_equalities=0,screened_commands=0,transfer_certificates=0)
    sample=None
    for case in range(120):
        k=rng.randint(1,6);n=rng.randint(3,8);m=rng.randint(1,min(4,n))
        a=tuple(F(i,n-1) for i in range(n));b=tuple(F(rng.randint(0,10),10) for _ in range(k))
        raw=[rng.randint(1,5) for _ in b];w=tuple(F(x,sum(raw)) for x in raw)
        g=tuple(F(rng.randint(0,9),3) for _ in b);tau=tuple(min(F(1),bj+F(rng.randint(0,6),10)) for bj in b)
        data=Instance.make(b,w,g,tau);B=data.cap_total*F(rng.randint(0,10),10)
        rho=tuple(F(rng.randint(0,8),10) for _ in a)
        potential=lambda u:sum(wj*min(bj,u) for wj,bj in zip(w,b))
        for i,u in enumerate(a):
            for v in list(a[i+1:])+[None]:
                rhs=(data.cap_total if v is None else potential(v))-potential(u)
                assert arc(data,u,v)['capacity']==rhs;counts['capacity_identities']+=1
        for z in a[1:]:
            bound,_=bound_for(data,a,z)
            assert bound==independent_bound(encode(asdict(data)),list(a),z);counts['context_envelopes']+=1
        for c in books(data,a,B,m):
            for ix in range(1,len(c)):
                z=c[ix];u=c[ix-1];v=c[ix+1] if ix+1<len(c) else None;deleted=c[:ix]+c[ix+1:]
                totalmax=F(0)
                for j,bj in enumerate(b):
                    candidates=[c[0]+(bj-c[0])*F(t,10) for t in range(11)]
                    gains=[value(data,j,c,t)-value(data,j,deleted,t) for t in candidates]
                    localdata=Instance.make([bj],[F(1)],[g[j]],[tau[j]],data.r,data.curvature)
                    local=context_gain(localdata,u,z,v)
                    assert min(gains)>=0 and max(gains)<=local
                    totalmax+=w[j]*max(gains);counts['pointwise_deletion_checks']+=len(candidates)
                assert totalmax<=context_gain(data,u,z,v)<=bound_for(data,a,z)[0]
        reduced=screen(data,a,rho,B)
        full,_=enumerate_opt(data,a,rho,B,m)
        small,_=enumerate_opt(data,reduced['catalog'],reduced['charges'],B,m)
        assert full==small
        counts['exhaustive_equalities']+=1;counts['screened_commands']+=len(reduced['deletions'])
        if case<20:
            solved=solve_screened(data,a,rho,B,m,F(1,10));cert=solved['envelope']
            checked=verify(cert,digest(cert['original']))
            assert F(checked['lower'])<=full<=F(checked['upper'])
            counts['transfer_certificates']+=1
            if cert['deletions'] and sample is None:sample=cert
        counts['models']+=1
    assert sample is not None
    rejected=[]
    def mutation(name,change,expected=None):
        cert=copy.deepcopy(sample);change(cert)
        try:verify(cert,expected or sample['instance_sha256'])
        except (AssertionError,ValueError,KeyError,IndexError,ZeroDivisionError,TypeError):rejected.append(name)
        else:raise AssertionError('Accepted corruption: '+name)
    mutation('unknown schema',lambda c:c.update(schema='invalid'))
    mutation('false bound',lambda c:c['deletions'][0].update(gain_bound='-1'))
    mutation('false charge',lambda c:c['deletions'][0].update(charge='-1'))
    mutation('false strictness',lambda c:c['deletions'][0].update(strict=not c['deletions'][0]['strict']))
    mutation('anchor removal',lambda c:c['deletions'][0].update(candidate=c['original']['catalog'][0]))
    mutation('omitted deletion',lambda c:c['deletions'].pop())
    mutation('duplicate deletion',lambda c:c['deletions'].append(copy.deepcopy(c['deletions'][0])))
    mutation('false original digest',lambda c:c.update(instance_sha256='0'*64))
    mutation('different requested instance',lambda c:None,expected='f'*64)
    mutation('changed retained charge',lambda c:c['resource_certificate']['charges'].__setitem__(0,'-1'))
    mutation('changed root promise',lambda c:c['resource_certificate'].update(promise='-1'))
    mutation('changed upper bound',lambda c:c['resource_certificate'].update(upper='-100'))
    mutation('missing Bellman coverage',lambda c:c['resource_certificate']['tables'].clear())
    mutation('bad lottery mass',lambda c:c['resource_certificate']['policy']['lotteries'][0][0].__setitem__(1,'2'))
    d=Instance.make([F(1,4)],[F(1)],[F(0)],[F(1)])
    aa=(F(0),F(1,2));bound=bound_for(d,aa,F(1,2))[0]
    rr=(F(0),bound);z=screen(d,aa,rr,F(1,4))
    assert len(z['deletions'])==1 and not z['deletions'][0]['strict']
    assert enumerate_opt(d,aa,rr,F(1,4),2)[0]==enumerate_opt(d,z['catalog'],z['charges'],F(1,4),2)[0]
    zero=Instance.make([F(0)],[F(1)],[F(0)],[F(1,2)])
    z=solve_screened(zero,aa,(F(0),F(0)),F(0),2,F(1,10));verify(z['envelope'])
    out=dict(status='PASS',**counts,rejected_corruptions=rejected,
             equality_case='Both optimal books may exist; a retained optimum is certified',
             zero_cap_zero_promise='PASS',seconds=time.perf_counter()-begin)
    dump(OUT/'REGRESSION.json',out);print(json.dumps(out,indent=2));return out


def groups(data,a):return len({sum(x<=tau for x in a) for tau in data.ceilings})


def store_certificate(name,cert):
    raw=json.dumps(cert,sort_keys=True,separators=(',',':')).encode();packed=gzip.compress(raw,mtime=0)
    path=OUT/'certificates'/f'{name}.json.gz';path.parent.mkdir(exist_ok=True);path.write_bytes(packed)
    return dict(bytes=len(raw),compressed_bytes=len(packed),sha256=hashlib.sha256(packed).hexdigest())


def controlled():
    rows=[]
    for k in (4,16,64):
        data=Instance.make([F(1,4)]*k,[F(1,k)]*k,[F(j%4) for j in range(k)],
                           [F(1,2)+F(j+1,2*(k+1)) for j in range(k)])
        B=F(1,8);budget=2;eps=F(1,10)
        for nadd in (0,2,4,8):
            base=(F(0),F(1,4),F(1,2),F(1));added=tuple(F(1,2)+F(i,20) for i in range(1,nadd+1))
            a=tuple(sorted(base+added));rho=tuple(F(1,2) if x in added else F(0) for x in a)
            t=time.perf_counter();full=solve(data,a,rho,B,budget,eps);full_seconds=time.perf_counter()-t
            vf=verify_resource(full['certificate']);opt,book=enumerate_opt(data,a,rho,B,budget)
            small=solve_screened(data,a,rho,B,budget,eps);env=small['envelope'];vs=verify(env,digest(env['original']))
            assert F(vs['lower'])<=opt<=F(vs['upper']) and full['lower']<=opt<=full['upper']
            assert set(small['screening']['catalog'])==set(base)-{F(1)}
            assert enumerate_opt(data,small['screening']['catalog'],small['screening']['charges'],B,budget)[0]==opt
            name=f'k{k}-insert{nadd}'
            packed=store_certificate(name,env);fullpacked=store_certificate(name+'-full',full['certificate'])
            coarse=sum(F(1,2)>data.reward(F(1))-opt for z in added)
            row=dict(name=name,histories=k,insertions=nadd,catalog_size=len(a),full_classes=groups(data,a),
                 reduced_classes=groups(data,small['screening']['catalog']),selected_classes=groups(data,book),
                 screened=len(small['screening']['deletions']),coarse_screened=coarse,
                 exact_optimum=str(opt),winning_book=encode(book),
                 full_lower=str(full['lower']),full_upper=str(full['upper']),
                 screened_lower=vs['lower'],screened_upper=vs['upper'],
                 full_states=full['resource_states'],screened_states=small['answer']['resource_states'],
                 full_seconds=full_seconds,screening_seconds=small['screening']['seconds'],
                 reduced_seconds=small['answer']['seconds'],full_check_seconds=vf['seconds'],
                 transfer_check_seconds=vs['seconds'],full_certificate=fullpacked,transfer_certificate=packed,
                 instance_sha256=env['instance_sha256'])
            rows.append(row);dump(OUT/'CONTROLLED.json',rows)
            print(name,'PASS',len(a),'->',len(small['screening']['catalog']),flush=True)
    return rows


def main():
    begin=time.perf_counter();reg=regress();study=controlled()
    out=dict(status='PASS',cases=len(study),all_exact_values_preserved=True,regression=reg,
             seconds=time.perf_counter()-begin,python=sys.version,platform=platform.platform(),
             note='Finite synthetic validation; inherited R52 timings and results are not overwritten.')
    dump(OUT/'SUMMARY.json',out)
if __name__=='__main__':main()
