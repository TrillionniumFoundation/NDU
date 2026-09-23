#!/usr/bin/env python3
"""Exact rational response-curve solver on a finite, recombining public DAG.

No scenario-tree construction, price grid, numerical optimization, or full-tree
multipliers are used here. Quadratic rewards, positive scalar payments, and no
intertemporal switching are essential. The verifier is a separate program.
"""
from __future__ import annotations
from bisect import bisect_right
from dataclasses import dataclass
from fractions import Fraction as F
from typing import Any


def rat(x: Any) -> F:
    if isinstance(x, float):
        raise TypeError('Use exact rational strings or integers, not floats.')
    return F(x)


def clip(x: F, lo: F, hi: F) -> F:
    return max(lo, min(hi, x))


@dataclass(frozen=True)
class Curve:
    knots: tuple[F, ...]
    lines: tuple[tuple[F, F], ...]  # slope, intercept; constant outer tails

    def at(self, x: F) -> F:
        m, c = self.lines[bisect_right(self.knots, x)]
        return m*x+c

    @property
    def low(self) -> F:
        return self.lines[-1][1]

    @property
    def high(self) -> F:
        return self.lines[0][1]

    def inverse(self, target: F) -> F:
        """A finite price giving exactly target; leftmost crossing except high tail."""
        if not self.low <= target <= self.high:
            raise ValueError(f'Promise {target} outside [{self.low}, {self.high}]')
        if not self.knots:
            return F(0)
        if target == self.high:
            return self.knots[0]-1
        for i, (m,c) in enumerate(self.lines):
            if m < 0:
                x = (target-c)/m
                if (i == 0 or self.knots[i-1] <= x) and (i == len(self.knots) or x <= self.knots[i]):
                    return x
        raise ArithmeticError('Continuous decreasing response did not cross target')

    def json(self) -> dict:
        return {'knots': list(map(str,self.knots)),
                'lines': [[str(m), str(c)] for m,c in self.lines]}


def curve_from_values(knots: list[F], vals: list[F], high: F, low: F) -> Curve:
    if not knots:
        assert high == low
        return Curve((), ((F(0),high),))
    assert len(knots) == len(vals) and vals[0] == high and vals[-1] == low
    lines=[(F(0),high)]
    for x,y,v,w in zip(knots,knots[1:],vals,vals[1:]):
        m=(w-v)/(y-x)
        assert m <= 0
        lines.append((m,v-m*x))
    lines.append((F(0),low))
    kept_k=[]; kept_l=[lines[0]]
    for k,line in zip(knots,lines[1:]):
        if line != kept_l[-1]:
            kept_k.append(k); kept_l.append(line)
    return Curve(tuple(kept_k),tuple(kept_l))


def read_instance(raw: dict) -> tuple[list[dict], F, F]:
    beta=rat(raw.get('beta',1)); promise=rat(raw['promise'])
    assert 0 < beta <= 1
    nodes=[]
    for i,n in enumerate(raw['nodes']):
        v={k:rat(n[k]) for k in ['r','q','a','lo','hi','cap']}
        assert v['q']>0 and v['a']>0 and 0<=v['lo']<=v['hi']<=1
        v['edges']=[(int(j),rat(p)) for j,p in n.get('edges',[])]
        assert all(i<j<len(raw['nodes']) and p>0 for j,p in v['edges'])
        assert not v['edges'] or sum(p for _,p in v['edges'])==1
        v['label']=n.get('label',str(i)); nodes.append(v)
    assert nodes
    return nodes,beta,promise


def solve(raw: dict, make_certificate: bool=True) -> dict:
    nodes,beta,b0=read_instance(raw)
    curves: dict[int,Curve]={}; barriers: dict[int,F|None]={}
    for i in range(len(nodes)-1,-1,-1):
        v=nodes[i]; a,r,q,lo,hi=(v[k] for k in ['a','r','q','lo','hi'])
        keys=set()
        if lo < hi:
            keys.update([(r-q*hi)/a,(r-q*lo)/a])
        for j,p in v['edges']:
            keys.update(curves[j].knots)
        ks=sorted(keys)
        def d(x: F) -> F:
            return a*clip((r-a*x)/q,lo,hi)+beta*sum(p*curves[j].at(x) for j,p in v['edges'])
        high=a*hi+beta*sum(p*curves[j].high for j,p in v['edges'])
        low=a*lo+beta*sum(p*curves[j].low for j,p in v['edges'])
        if v['cap'] < low:
            raise ValueError(f'Infeasible continuation at node {i}')
        before=curve_from_values(ks,[d(k) for k in ks],high,low)
        alpha=None if v['cap']>=high else before.inverse(v['cap'])
        barriers[i]=alpha
        if alpha is None:
            curves[i]=before
        else:
            keys=set(before.knots); keys.add(alpha); ks=sorted(keys)
            curves[i]=curve_from_values(ks,[min(v['cap'],before.at(k)) for k in ks],v['cap'],low)
    eta=curves[0].inverse(b0)
    # Forward distribution on the finite (public node, incoming price) state graph.
    reach: dict[int,dict[F,F]]={0:{eta:F(1)}}
    states=[]; reward=F(0); payment=F(0)
    for i,v in enumerate(nodes):
        for incoming,w in sorted(reach.get(i,{}).items()):
            al=barriers[i]; effective=incoming if al is None else max(incoming,al)
            x=clip((v['r']-v['a']*effective)/v['q'],v['lo'],v['hi'])
            grad=v['r']-v['q']*x-v['a']*effective
            lower=max(F(0),-grad); upper=max(F(0),grad)
            stage=v['r']*x-v['q']*x*x/2
            reward+=w*stage; payment+=w*v['a']*x
            if make_certificate:
                states.append({'node':i,'incoming':str(incoming),'price':str(effective),
                               'weight':str(w),'x':str(x),'chi':str(effective-incoming),
                               'lower':str(lower),'upper':str(upper),
                               'payment':str(curves[i].at(incoming))})
            for j,p in v['edges']:
                reach.setdefault(j,{})[effective]=reach.get(j,{}).get(effective,F(0))+w*beta*p
    assert payment==b0
    knots=set(k for c in curves.values() for k in c.knots)
    output={'value':str(reward),'payment':str(payment),'root_price':str(eta),
            'barriers':[None if barriers[i] is None else str(barriers[i]) for i in range(len(nodes))],
            'curves':[curves[i].json() for i in range(len(nodes))],
            'states':states,
            'statistics':{'public_nodes':len(nodes),'public_edges':sum(len(v['edges']) for v in nodes),
                          'global_breakpoints':len(knots),'stored_segments':sum(len(c.lines) for c in curves.values()),
                          'max_node_segments':max(len(c.lines) for c in curves.values()),
                          'reachable_price_pairs':sum(len(x) for x in reach.values()),
                          'distinct_incoming_prices':len(set(p for d in reach.values() for p in d))}}
    assert len(knots)<=3*len(nodes)
    assert output['statistics']['reachable_price_pairs']<=len(nodes)*(len(nodes)+1)
    return output


def recombining_example() -> dict:
    return {'name':'strict_value_of_price_memory','beta':'1','promise':'1/2','nodes':[
        {'label':'root','r':'0','q':'1','a':'1','lo':'0','hi':'0','cap':'1','edges':[[1,'1/2'],[2,'1/2']]},
        {'label':'A','r':'0','q':'1','a':'1','lo':'0','hi':'1','cap':'1/4','edges':[[3,'1']]},
        {'label':'B','r':'0','q':'1','a':'1','lo':'0','hi':'1','cap':'1','edges':[[3,'1']]},
        {'label':'C','r':'2','q':'1','a':'1','lo':'0','hi':'1','cap':'1','edges':[]}]}

if __name__=='__main__':
    import json,sys
    instance=json.load(open(sys.argv[1])) if len(sys.argv)>1 else recombining_example()
    print(json.dumps({'instance':instance,'certificate':solve(instance)},indent=2))
