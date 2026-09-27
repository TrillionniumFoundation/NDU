#!/usr/bin/env python3
"""Fixed-table exact oracle, including tied and zero-width endpoint normals."""
from copy import deepcopy
from fractions import Fraction as F
from quotient import compile_graph,execute

def oracle(raw,centers,width,omega=None,split='equal',root_price=None):
    centers=list(map(F,centers));delta=F(width)
    if delta<0:raise ValueError('Release width must be nonnegative.')
    omega=list(map(F,omega)) if omega is not None else [F(1)]*len(centers)
    if any(x<0 for x in omega):raise ValueError('Negative corridor weight.')
    bounded=deepcopy(raw)
    for i,v in enumerate(bounded['nodes']):
        cell=int(v.get('cell',i));lo,hi=F(v['lo']),F(v['hi'])
        v['lo']=str(max(lo,centers[cell]-delta*omega[cell]))
        v['hi']=str(min(hi,centers[cell]+delta*omega[cell]))
        if F(v['lo'])>F(v['hi']):raise ValueError('Empty physical/corridor intersection.')
    c=compile_graph(bounded);cert=execute(c,F(raw['promise']),eta=None if root_price is None else F(root_price))
    G=[F(0)]*len(centers);H=F(0);splits=[]
    for st in cert['states']:
        v=st['node'];row=raw['nodes'][v];cell=int(row.get('cell',v));x=F(st['x']);w=F(st['weight'])
        effective=bounded['nodes'][v];parts={}
        for orientation,key in [('lower','lo'),('upper','hi')]:
            mult=F(st[orientation]);endpoint=F(effective[key]);active=[]
            if endpoint==F(row[key]):active.append('physical')
            corridor=centers[cell]+(-1 if orientation=='lower' else 1)*delta*omega[cell]
            if endpoint==corridor:active.append('corridor')
            assert active
            if mult:assert x==endpoint
            if split=='equal':allocation={k:mult/len(active) for k in active}
            elif split in ['physical','corridor']:
                chosen=split if split in active else active[0];allocation={k:(mult if k==chosen else F(0)) for k in active}
            else:raise ValueError('Unknown normal-cone split.')
            assert sum(allocation.values())==mult
            parts[orientation]=allocation
        rm=parts['lower'].get('corridor',F(0));rp=parts['upper'].get('corridor',F(0))
        G[cell]+=w*(rp-rm);H+=w*omega[cell]*(rp+rm)
        splits.append(dict(node=v,lower={k:str(z) for k,z in parts['lower'].items()},upper={k:str(z) for k,z in parts['upper'].items()}))
    return dict(value=cert['value'],gradient=[str(z) for z in G],width_gradient=str(H),
                splits=splits,certificate=cert,bounded_instance=bounded)
