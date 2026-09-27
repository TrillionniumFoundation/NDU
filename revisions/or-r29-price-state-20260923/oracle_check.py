#!/usr/bin/env python3
"""Exact supporting-cut tests and a two-service scalar-commitment check."""
from fractions import Fraction as F
from pathlib import Path
import json,copy
from price_solver import solve
from verify import check
R=Path(__file__).resolve().parent


def run():
    data=json.loads((R/'results/evidence.json').read_text());out=[]
    for anchor in data['instances']:
        raw=anchor['instance'];des=raw.get('design',{})
        if not des.get('corridor') or des['T']>16:continue
        cert=anchor['certificate'];K=des['T'];G=[F(0)]*K;H=F(0)
        for s in cert['states']:
            v=raw['nodes'][s['node']];w=F(s['weight']);lo=F(s['lower']);up=F(s['upper'])
            assert F(v['lo'])==F(v['center'])-F(1,4)>0
            assert F(v['hi'])==F(v['center'])+F(1,4)<1
            G[v['cell']]+=w*(up-lo);H+=w*(up+lo)
        for j in range(6):
            perturb=[F(((i+2)*(j+3))%5-2,200) for i in range(K)];dd=F(j-2,200)
            query=copy.deepcopy(raw);query['name']=raw['name']+f'-query{j}'
            for v in query['nodes']:
                c=F(v['center'])+perturb[v['cell']];delta=F(1,4)+dd
                v['center']=str(c);v['lo']=str(max(F(0),c-delta));v['hi']=str(min(F(1),c+delta))
            try:qc=solve(query)
            except ValueError:
                out.append(dict(anchor=raw['name'],query=query['name'],feasible=False));continue
            check({'instance':query,'certificate':qc})
            U=F(cert['value'])+sum(a*b for a,b in zip(G,perturb))+H*dd
            assert U>=F(qc['value'])
            out.append(dict(anchor=raw['name'],query=query['name'],feasible=True,
                            gradient=list(map(str,G)),release_price=str(H),du=list(map(str,perturb)),ddelta=str(dd),
                            upper=str(U),gap=str(U-F(qc['value'])),instance=query,certificate=qc))
    # Two service coordinates at each public vertex. With beta=1 a deterministic
    # serial expansion is an exact independent implementation of the local vector
    # response. The artificial second-coordinate cap is deliberately redundant.
    base=copy.deepcopy(data['instances'][8]['instance']);base['beta']='1'
    original=[]
    for i,v in enumerate(base['nodes']):
        original.append(dict(r=[F(v['r']),F(v['r'])+F(1,3)],q=[F(v['q']),F(v['q'])+F(1,5)],
                             a=[F(v['a']),F(v['a'])+F(1,7)],edges=[(j,F(p)) for j,p in v['edges']]))
    pay={}
    for i in range(len(original)-1,-1,-1):
        v=original[i];pay[i]=sum(v['a'])*F(2,5)+sum(p*pay[j] for j,p in v['edges'])
    expanded=[]
    for i,v in enumerate(original):
        for k in range(2):
            expanded.append(dict(label=f'public-{i}-service-{k}',r=str(v['r'][k]),q=str(v['q'][k]),a=str(v['a'][k]),
                lo='0',hi='1',cap=str(pay[i]+F((i%3),20)) if k==0 else '1000',
                edges=[[2*i+1,'1']] if k==0 else [[2*j,str(p)] for j,p in v['edges']]))
    raw=dict(name='two-service-single-commitment',beta='1',promise=str(pay[0]),nodes=expanded)
    cert=solve(raw);check({'instance':raw,'certificate':cert})
    assert all(cert['barriers'][2*i+1] is None for i in range(len(original)))
    (R/'results/oracles.json').write_text(json.dumps(dict(queries=out,
          vector_extension=dict(original_public_nodes=len(original),service_coordinates=2,
                                implementation='deterministic serial expansion at beta=1; extra caps redundant',
                                instance=raw,certificate=cert)),indent=2)+'\n')
    print('Oracle queries',len(out),'feasible',sum(a['feasible'] for a in out),'vector extension PASS')

if __name__=='__main__':run()
