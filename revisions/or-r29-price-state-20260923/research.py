#!/usr/bin/env python3
"""Seeded, exact, coupled Markov-DAG experiments and boundary checks."""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import copy, json, random, time, platform, resource, sys
from price_solver import solve, recombining_example
from verify import check
R=Path(__file__).resolve().parent


def instance(T,S,seed,corridor=False):
    rng=random.Random(seed); beta=F(19,20)
    groups=[[0]]; n=1
    for t in range(1,T): groups.append(list(range(n,n+S))); n+=S
    rows=[]
    for t,group in enumerate(groups):
        for z,i in enumerate(group):
            ws=[1+((z+2*j+seed)%3) for j in range(S)]
            ps=[F(w,sum(ws)) for w in ws]
            center=F(7+(t%5),20)
            lo=max(F(0),center-F(1,4)) if corridor else F(0)
            hi=min(F(1),center+F(1,4)) if corridor else F(1)
            rows.append(dict(label=f'{t}:{z}',t=t,z=z,cell=t,r=F(rng.randrange(-4,45),20),
                             q=F(rng.randrange(8,25),10),a=F(rng.randrange(8,17),10),
                             lo=lo,hi=hi,cap=F(0),
                             edges=[] if t==T-1 else [[j,p] for j,p in zip(groups[t+1],ps)],center=center))
    base={}; annuity={}
    for i in range(n-1,-1,-1):
        v=rows[i]; base[i]=v['a']*v['center']+beta*sum(p*base[j] for j,p in v['edges'])
        annuity[i]=1+beta*sum(p*annuity[j] for j,p in v['edges'])
        # Tight and slack continuation caps alternate across time and state.
        slack=F((3*i+seed)%7,100)*annuity[i]
        v['cap']=base[i]+slack
    def enc(x):
        if isinstance(x,F): return str(x)
        if isinstance(x,list): return [enc(a) for a in x]
        if isinstance(x,dict): return {k:enc(a) for k,a in x.items()}
        return x
    raw=enc(dict(name=f'markov-T{T}-S{S}-seed{seed}'+('-corridor' if corridor else ''),
                 beta=beta,promise=base[0],nodes=rows,
                 design=dict(T=T,S=S,seed=seed,corridor=corridor,
                             history_nodes=str((S**T-1)//(S-1)),
                             target='exact system-level primal-dual equality',
                             fixed_shared_table='center by date' if corridor else None)))
    return raw


def boundary_cases():
    seed=recombining_example()
    out=[]
    # Upper-tail and lower-tail roots; redundant, binding-at-minimum, and fixed boxes.
    for root in ['0','1/8','1/2','5/8']:
        z=copy.deepcopy(seed); z['promise']=root; z['name']='root-promise-'+root.replace('/','-'); out.append(z)
    z={'name':'negative-root-price','beta':'1','promise':'3/4','nodes':[
        dict(label='root',r='0',q='1',a='1',lo='0',hi='1',cap='1',edges=[])]};out.append(z)
    z={'name':'minimum-cap-fixed-corridor','beta':'1/2','promise':'3/8','nodes':[
        dict(label='root',r='2',q='1',a='1',lo='1/4',hi='3/4',cap='3/8',edges=[[1,'1']]),
        dict(label='child',r='-1',q='2',a='1',lo='1/4',hi='1/4',cap='1/4',edges=[])]};out.append(z)
    # Equal child thresholds and zero-width root box.
    z=copy.deepcopy(seed);z['name']='tied-child-barriers';z['nodes'][2]['cap']='1/4';z['promise']='1/4';out.append(z)
    return out


def run():
    (R/"results").mkdir(parents=True,exist_ok=True)
    records=[]; measurements=[]
    raw_cases=[recombining_example()]+boundary_cases()
    for seed in range(12): raw_cases.append(instance(3+seed%3,2,seed+41,seed%2==1))
    for T,S in [(4,2),(8,2),(16,2),(32,2),(64,2),(8,3),(16,3),(32,3),(64,3)]:
        raw_cases.append(instance(T,S,101+T+S,False))
    for T,S in [(8,2),(16,2),(32,2),(64,2),(16,3),(32,3)]:
        raw_cases.append(instance(T,S,307+T+S,True))
    for raw in raw_cases:
        start=time.perf_counter(); cert=solve(raw); solve_s=time.perf_counter()-start
        b={'instance':raw,'certificate':cert}
        start=time.perf_counter(); report=check(b); verify_s=time.perf_counter()-start
        n=cert['statistics']['public_nodes']; curves=cert['curves']
        bits=max(max(F(v).numerator.bit_length(),F(v).denominator.bit_length())
                 for c in curves for line in c['lines'] for v in line)
        measurements.append(dict(name=raw['name'],solve_seconds=solve_s,verify_seconds=verify_s,
                                 coefficient_max_bits=bits,serialized_certificate_bytes=len(json.dumps(cert)),
                                 **cert['statistics']))
        records.append(b)
        print(raw['name'], n, cert['statistics']['global_breakpoints'], cert['statistics']['reachable_price_pairs'],round(solve_s,3),round(verify_s,3),flush=True)
    # Deliberate invalid inputs must fail, rather than produce an optimistic answer.
    rejected=[]
    bad=copy.deepcopy(recombining_example());bad['promise']='4';
    try:solve(bad)
    except ValueError:rejected.append('infeasible root')
    bad=copy.deepcopy(boundary_cases()[-2]);bad['nodes'][0]['cap']='0'
    try:solve(bad)
    except ValueError:rejected.append('infeasible lower envelope')
    assert len(rejected)==2
    report={'schema':'ndu-price-state-evidence-v1','instances':records,
            'memory_example':{'full':'27/32','public_only':'13/32','gain':'7/16',
                              'terminal_tiers':['1/4','3/4'],'effective_prices':['7/4','5/4']},
            'rejected_inputs':rejected}
    (R/'results/evidence.json').write_text(json.dumps(report,indent=2)+'\n')
    timing={'platform':platform.platform(),'python':sys.version,'clock':'perf_counter',
            'repetitions':1,'timing_scope':'response construction plus policy; independent exact audit separately',
            'peak_rss_kib_whole_generator':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'caution':'One sequential process, no isolated per-case memory or speedup claim; all instances exact at system level.',
            'measurements':measurements}
    (R/'results/timings.json').write_text(json.dumps(timing,indent=2)+'\n')

if __name__=='__main__':run()
