#!/usr/bin/env python3
"""Independent verification of table QPs, memory frontiers, and oracle cuts.
Only the independent base checker is imported; no generator/solver is imported.
"""
from fractions import Fraction as Q
from pathlib import Path
import json,sys,hashlib
from verify import check
R=Path(__file__).resolve().parent

def dot(a,b):return sum(x*y for x,y in zip(a,b))
def all_parts(n):
    if n==0:yield [];return
    for p in all_parts(n-1):
        yield p+[[n-1]]
        for i in range(len(p)):yield p[:i]+[p[i]+[n-1]]+p[i+1:]

def main():
    original=json.loads((R/'results/evidence.json').read_text())
    inputs={x['instance']['name']:x for x in original['instances']}
    tables=json.loads((R/'results/tables.json').read_text())['instances']
    for z in tables:
        raw=inputs[z['name']]['instance'];nodes=raw['nodes'];beta=Q(raw['beta']);K=z['table_coordinates'];N=len(nodes)
        H=[[Q(0)]*K for v in nodes];w=[Q(0)]*N;w[0]=1
        for i,v in enumerate(nodes):
            for j,p in v['edges']:w[j]+=w[i]*beta*Q(p)
        for i in reversed(range(N)):
            H[i][nodes[i]['cell']]=Q(nodes[i]['a'])
            for j,p in nodes[i]['edges']:
                H[i]=[a+beta*Q(p)*b for a,b in zip(H[i],H[j])]
        assert [[str(x) for x in a] for a in H]==z['H']
        assert w==list(map(Q,z['weights']))
        q=[Q(0)]*K;r=[Q(0)]*K
        for i,v in enumerate(nodes):q[v['cell']]+=w[i]*Q(v['q']);r[v['cell']]+=w[i]*Q(v['r'])
        assert list(map(str,q))==z['q'] and list(map(str,r))==z['r']
        A=[[Q(v) for v in a] for a in z['A']];b=list(map(Q,z['b']))
        assert A[:N-1]==H[1:] and b[:N-1]==[Q(v['cap']) for v in nodes[1:]]
        for k in range(K):
            unit=[Q(j==k) for j in range(K)]
            assert A[N-1+2*k]==unit and A[N+2*k]==[-a for a in unit]
            assert b[N-1+2*k]==1 and b[N+2*k]==0
        E=list(map(Q,z['E']));assert E==H[0]
        e=Q(z['e']);assert e==Q(raw['promise'])
        x=list(map(Q,z['x']));eta=Q(z['eta']);mu=list(map(Q,z['mu']))
        assert dot(E,x)==e and all(dot(a,x)<=v for a,v in zip(A,b))
        assert all(m>=0 and m*(v-dot(a,x))==0 for m,a,v in zip(mu,A,b))
        residual=[r[k]-eta*E[k]-sum(m*a[k] for m,a in zip(mu,A)) for k in range(K)]
        assert all(t==q[k]*x[k] for k,t in enumerate(residual))
        upper=eta*e+dot(mu,b)+sum(t*t/(2*v) for t,v in zip(residual,q))
        primal=dot(r,x)-sum(v*t*t/2 for v,t in zip(q,x))
        assert upper==primal==Q(z['table_value'])
        assert Q(z['full_value'])==Q(inputs[z['name']]['certificate']['value'])
        assert Q(z['gain'])==Q(z['full_value'])-primal>=0
    memory=json.loads((R/'results/memory.json').read_text())['families'];partition_count=0
    for z in memory:
        check(z);k=z['k'];caps=list(map(Q,z['caps']));full=sum(2*x-x*x/2 for x in caps)/k
        assert full==Q(z['full_value'])
        def cost(group):
            mn=min(caps[i] for i in group)
            return (2-mn)*sum(caps[i]-mn for i in group)/k
        dp={(0,0):Q(0)}
        for m in range(1,k+1):
            for j in range(m,k+1):
                dp[m,j]=min(dp[m-1,i]+cost(list(range(i,j))) for i in range(m-1,j) if (m-1,i) in dp)
        for row in z['frontier']:
            m=row['symbols'];assert len(row['groups'])==m
            assert sorted(i for g in row['groups'] for i in g)==list(range(k))
            assert sum(cost(g) for g in row['groups'])==Q(row['loss'])==dp[m,k]
            assert Q(row['value'])==full-dp[m,k] and row['bits']==(m-1).bit_length()
        if k<=6:
            best={}
            for p in all_parts(k):
                partition_count+=1;v=sum(cost(g) for g in p);m=len(p);best[m]=min(best.get(m,v),v)
            assert all(best[m]==dp[m,k] for m in best)
    oracle=json.loads((R/'results/oracles.json').read_text());queries=0
    for z in oracle['queries']:
        if not z['feasible']:continue
        check(z);queries+=1;anchor=inputs[z['anchor']];G=[Q(0)]*len(z['gradient']);H=Q(0)
        for state in anchor['certificate']['states']:
            v=anchor['instance']['nodes'][state['node']];weight=Q(state['weight'])
            up=Q(state['upper']);lo=Q(state['lower']);G[v['cell']]+=weight*(up-lo);H+=weight*(up+lo)
        assert list(map(str,G))==z['gradient'] and H==Q(z['release_price'])
        upper=Q(anchor['certificate']['value'])+dot(G,list(map(Q,z['du'])))+H*Q(z['ddelta'])
        assert upper==Q(z['upper']) and upper-Q(z['certificate']['value'])==Q(z['gap'])>=0
    check(oracle['vector_extension'])
    tree=json.loads((R/'results/tree_comparison.json').read_text())['instances']
    assert all(z['exact_matrix_kkt']=='PASS' and z['absolute_value_difference']<1e-7 and z['max_constraint_violation']<1e-8 for z in tree)
    report=dict(status='PASS',exact_table_qps=len(tables),exact_memory_families=len(memory),
                exhaustive_partitions=partition_count,exact_oracle_queries=queries,vector_extension=1,
                small_tree_matrix_crosschecks=len(tree),
                largest_numerical_tree_value_error=max(z['absolute_value_difference'] for z in tree),
                files={name:hashlib.sha256((R/'results'/name).read_bytes()).hexdigest() for name in
                    ['tables.json','memory.json','oracles.json','tree_comparison.json']})
    target=R/'results/extensions_verification.json'
    if '--check' in sys.argv:assert json.loads(target.read_text())==report
    else:target.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
