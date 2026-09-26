"""Certified simultaneous command exclusion; same total downstream budget."""
import time
from rational import F,qstr,encode,digest
from price_path import normalize,allocate,Oracle,solve,DeadlineExceeded
from check_price import model,check_policy,price_bound,verify as price_verify,require

def fallback(spec,policy):
    d,a,rho,B,m=normalize(spec);U=d.mean_reward(F(1))
    return dict(schema='NDU-price-path-v2-hex',spec=spec,instance_sha256=digest(spec),epsilon=qstr(0),tree={'proof':{'type':'universal','upper':qstr(U)}},policy=encode(policy),lower=qstr(policy['value']),upper=qstr(U))

def solve_screen(spec,epsilon=F(1,100),seconds=2.0):
    begin=time.perf_counter();d,a,rho,B,m=normalize(spec);eps=F(epsilon)
    seed=allocate(d,(a[0],),B,dict(zip(a,rho)));removals=[];proofs=[];categories={};calls=0
    seed_seconds=0.
    try:
        z=time.perf_counter();pre=solve(spec,eps,seconds=seconds*.15,max_nodes=32)
        seed=pre['certificate']['policy'];seed={**seed,'value':F(seed['value'])};seed_seconds=time.perf_counter()-z
        oracle=Oracle(d,a,rho,B,m)
        for i,u in enumerate(a):
            if time.perf_counter()-begin>=seconds*.5:break
            for lam in [F(seed['price']),F(0)]:
                if time.perf_counter()-begin>=seconds*.5:break
                ans=oracle.run(lam,frozenset({i}));calls+=1
                if ans is None or ans['upper']<seed['value']:
                    removals.append(i);proofs.append({'index':i,'price':qstr(lam),'upper':None if ans is None else qstr(ans['upper'])})
                    categories[i]='wholly_ineligible' if all(u>t for t in d.ceilings) else 'possible_anchor' if u<=min(B,min(d.caps)) else 'ordinary'
                    break
        screen_seconds=time.perf_counter()-begin;keep=[i for i in range(len(a)) if i not in removals]
        reduced=dict(spec,catalog=[spec['catalog'][i] for i in keep],charges=[spec['charges'][i] for i in keep])
        z=time.perf_counter();ans=solve(reduced,eps,seconds=max(0,seconds-screen_seconds),max_nodes=4096);reduced_seconds=time.perf_counter()-z
        pol=ans['certificate']['policy'] if ans['lower']>=seed['value'] else encode(seed);L=F(pol['value']);U=ans['upper']
        cert=dict(schema='NDU-screen-v1-hex',spec=spec,instance_sha256=digest(spec),seed_policy=encode(seed),fixings=proofs,kept_indices=keep,reduced_certificate=ans['certificate'],policy=pol,lower=qstr(L),upper=qstr(U))
        return dict(status='EXACT' if U==L else 'TOLERANCE' if U-L<=eps else ans['status'],lower=L,upper=U,gap=U-L,seconds=time.perf_counter()-begin,screen_seconds=screen_seconds,seed_seconds=seed_seconds,reduced_seconds=reduced_seconds,commands_removed=len(removals),removal_categories=categories,forced_oracle_calls=calls,downstream_nodes=ans['nodes'],downstream_oracle_calls=ans['oracle_calls'],certificate=cert,trace=ans['trace'])
    except DeadlineExceeded:
        cert=fallback(spec,seed);L=F(cert['lower']);U=F(cert['upper'])
        return dict(status='TIME_LIMIT',lower=L,upper=U,gap=U-L,seconds=time.perf_counter()-begin,screen_seconds=time.perf_counter()-begin,seed_seconds=seed_seconds,reduced_seconds=0,commands_removed=0,partial_fixings_not_applied=proofs,certificate=cert)

from check_screen import verify  # Compatibility alias; independent checker module.
