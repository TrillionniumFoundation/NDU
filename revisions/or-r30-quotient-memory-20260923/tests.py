#!/usr/bin/env python3
"""Exact regression, independent laminar comparison, memory and tie tests."""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations
from copy import deepcopy
import json,sys,time
R=Path(__file__).resolve().parent;OLD=R.parent/'or-r29-price-state-20260923';sys.path.insert(0,str(OLD))
# All inputs here are fixed, trusted tests or internally generated rational data.
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
from quotient import compile_graph,execute,solve,minimal_machine
from policy_audit import check_policy
from baselines import laminar,promise_grid
from verify import check
from research import instance
from price_solver import recombining_example
from corridor_oracle import oracle
from experiments import binary

def partitions(n):
    blocks=[]
    def visit(i):
        if i==n:yield tuple(tuple(x) for x in blocks);return
        for b in blocks:
            b.append(i);yield from visit(i+1);b.pop()
        blocks.append([i]);yield from visit(i+1);blocks.pop()
    yield from visit(0)

def frontier(bs,ps,f,cost):
    n=len(bs);C={}
    for i in range(n):
        for j in range(i,n):C[i,j]=sum(ps[h]*(f(bs[h])-f(bs[i])+cost(h,bs[h]-bs[i])) for h in range(i,j+1))
    dp={(0,0):F(0)}
    for k in range(1,n+1):
        for j in range(k,n+1):dp[k,j]=min(dp[k-1,i]+C[i,j-1] for i in range(k-1,j) if (k-1,i) in dp)
    return {k:dp[k,n] for k in range(1,n+1)}

def run():
    start=time.perf_counter();report={'status':'passed','tests':{}}
    inherited=json.loads((OLD/'results/evidence.json').read_text())['instances'];checks=0
    for record in inherited:
        raw=record['instance'];c=solve(raw)
        assert c['value']==record['certificate']['value'] and c['curves']==record['certificate']['curves']
        ans=check(dict(instance=raw,certificate=c));check_policy(dict(instance=raw,certificate=c))
        checks+=ans.get('checked_relations',ans.get('checks',0));minimal_machine(raw,c)
    report['tests']['inherited']=dict(instances=len(inherited),full_curve_and_value_equality=True,
        independent_full_curve_audit=True,checker_count_field_sum=checks)
    total=0;behavior_pairs=0
    for seed in range(40):
        raw=instance(3+seed%3,2,41+seed,seed%2==1);cert=solve(raw);tree=laminar(raw)
        assert cert['value']==tree['value'];check_policy(dict(instance=raw,certificate=cert));total+=1
        machine=minimal_machine(raw,cert);lookup={(s['node'],F(s['incoming'])):s for s in cert['states']}
        def plan(v,eta):
            s=lookup[v,eta];return (F(s['x']),tuple((j,plan(j,F(s['price']))) for j,p in raw['nodes'][v]['edges']))
        for group in machine['groups']:
            v=group['node']
            for a,b in combinations(group['states'],2):
                assert (a['label']==b['label'])==(plan(v,F(a['incoming']))==plan(v,F(b['incoming'])))
                behavior_pairs+=1
    report['tests']['independent_laminar']=dict(instances=total,exact_value_equality=True,expanded_behavior_pair_checks=behavior_pairs)
    # Two numerical price states at a terminal vertex have the SAME full behavior.
    raw={'beta':'1','promise':'3/4','nodes':[
       dict(r='0',q='1',a='1',lo='0',hi='0',cap='1',edges=[[1,'1/2'],[2,'1/2']]),
       dict(r='2',q='1',a='1',lo='0',hi='1',cap='1/2',edges=[[3,'1']]),
       dict(r='2',q='1',a='1',lo='0',hi='1',cap='1',edges=[[3,'1']]),
       dict(r='0',q='1',a='1',lo='1/4',hi='1/4',cap='1/4',edges=[])]}
    c=solve(raw);m=minimal_machine(raw,c)
    assert m['minimal_symbols']==1 and m['max_raw_states_at_vertex']==2
    report['tests']['strict_automaton_reduction']={k:m[k] for k in ['minimal_symbols','max_raw_states_at_vertex','writable_bits']}
    # Noncontiguous set partitions are compared with the ordered DP.
    count=0
    for n in range(2,8):
        bs=[F(i+1,n+1) for i in range(n)];ps=[F(i+1,n*(n+1)//2) for i in range(n)]
        for case in ['quadratic','piecewise-concave-cubic-cost']:
            f=(lambda c:2*c-c*c/2) if case=='quadratic' else (lambda c:min(3*c/2,c+F(1,8)))
            cost=(lambda j,y:F(j+1,3)*y*y/2) if case=='quadratic' else (lambda j,y:F(j+1,3)*y**3)
            exact={}
            for part in partitions(n):
                val=sum(sum(ps[h]*(f(bs[h])-f(bs[min(cell)])+cost(h,bs[h]-bs[min(cell)])) for h in cell) for cell in part)
                k=len(part);exact[k]=min(exact.get(k,val),val);count+=1
            assert exact==frontier(bs,ps,f,cost)
    report['tests']['heterogeneous_frontier']=dict(arbitrary_partition_checks=count,probabilities='unequal positive',
           rewards=['quadratic','strictly increasing piecewise concave'],costs=['heterogeneous quadratic','heterogeneous cubic'])
    bs=[F(i,9) for i in range(1,9)];d=frontier(bs,[F(1,8)]*8,lambda c:2*c-c*c/2,lambda j,y:y*y/2)
    assert [d[i] for i in [1,2,3]]==[F(119,162),F(5,18),F(49,324)]
    report['tests']['retained_eight_branch_frontier']={str(k):str(v) for k,v in d.items()}
    dispersion=0
    for n in range(2,8):
        ps=[F(i+1,n*(n+1)//2) for i in range(n)];mu=sum(p*i for i,p in enumerate(ps));ds=[F(i)-mu for i in range(n)]
        last={k:F(0) for k in range(1,n+1)}
        for eps in [F(i,100) for i in [1,2,4,8]]:
            bs=[F(1,2)+eps*z for z in ds];assert all(0<b<1 for b in bs)
            now=frontier(bs,ps,lambda c:2*c-c*c/2,lambda j,y:y*y/2)
            for k in range(1,n):assert now[k]>last[k];dispersion+=1
            last=now
    report['tests']['dispersion']=dict(exact_strict_inequalities=dispersion,mean_payment='1/2')
    # Original coupled graph, plus fixed endpoints, lower/upper ties and zero widths.
    examples=[recombining_example()]
    for r,lo,hi,b in [('2','0','1/2','1/2'),('0','1/2','1','1/2'),('2','1/2','1/2','1/2'),('0','1/2','1/2','1/2')]:
        examples.append(dict(beta='1',promise=b,nodes=[dict(r=r,q='1',a='1',lo=lo,hi=hi,cap='1',edges=[])]))
    cutchecks=anchors=ties=0
    for raw in examples:
        for i,v in enumerate(raw['nodes']):v['cell']=i
        n=len(raw['nodes'])
        for center in [F(1,4),F(1,2),F(3,4)]:
            u=[center]*n
            # Fixed root's zero tier is not changed by an unrelated center.
            for i,v in enumerate(raw['nodes']):
                if F(v['lo'])==F(v['hi']):u[i]=F(v['lo'])
            for delta in [F(0),F(1,4),F(1,2),F(1)]:
                for split in ['physical','corridor','equal']:
                    try:old=oracle(raw,u,delta,split=split)
                    except ValueError:continue
                    anchors+=1;check_policy(dict(instance=old['bounded_instance'],certificate=old['certificate']))
                    for st in old['splits']:
                        ties+=sum(len(st[k])==2 for k in ['lower','upper'])
                    for shift in [F(-1,8),F(0),F(1,8)]:
                        for dd in [F(-1,8),F(0),F(1,8)]:
                            if delta+dd<0:continue
                            unew=[z+shift for z in u]
                            try:new=oracle(raw,unew,delta+dd)
                            except ValueError:continue
                            upper=F(old['value'])+sum(F(g)*shift for g in old['gradient'])+F(old['width_gradient'])*dd
                            assert F(new['value'])<=upper;cutchecks+=1
    report['tests']['corridor_normals']=dict(feasible_anchors=anchors,tied_normal_occurrences=ties,exact_support_inequalities=cutchecks,
         splits=['physical first','corridor first','equal split'],fixed_and_zero_width_intersections=True)
    gridchecks=0
    for T in [3,5,7]:
        raw=binary(T);val=F(solve(raw)['value']);last=None
        for Q in [10,20,40]:
            z=promise_grid(raw,Q);value=F(z['value']);assert value<=val
            if last is not None:assert value>=last
            last=value;gridchecks+=1
    report['tests']['promise_grid']=dict(exact_feasible_replays=gridchecks,nested_grid_values_nondecreasing=True)
    raw=recombining_example();cert=solve(raw);mutations=0
    for key in ['x','weight','chi','upper']:
        bad=deepcopy(cert);bad['states'][0][key]=str(F(bad['states'][0][key])+1)
        try:check_policy(dict(instance=raw,certificate=bad))
        except (AssertionError,KeyError):mutations+=1
    assert mutations==4
    for transform in ['negative q','bad probability','infeasible promise']:
        bad=deepcopy(raw)
        if transform=='negative q':bad['nodes'][0]['q']='-1'
        elif transform=='bad probability':bad['nodes'][0]['edges'][0][1]='1/3'
        else:bad['promise']='100'
        try:solve(bad)
        except ValueError:mutations+=1
    assert mutations==7
    report['tests']['rejections']=dict(deliberate_invalid_cases=mutations)
    from polymatroid_check import run as rank_check
    report['tests']['laminar_polymatroid']=rank_check()
    report['elapsed_seconds']=time.perf_counter()-start
    (R/'results/tests.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':run()
