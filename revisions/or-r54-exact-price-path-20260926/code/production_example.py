"""A non-renewal compatible-module example with decreasing marginal returns."""
from fractions import Fraction as F
from pathlib import Path
from itertools import combinations
import json
P=(F(0),F(2),F(5),F(9))
# (linear return, curvature, fixed installation charge), independently specified.
DATA={(0,1):(F(5),F(1),F(1,2)),(0,2):(F(4),F(1,2),F(1)),(0,3):(F(3),F(1,2),F(0)),
      (1,2):(F(7),F(2),F(3,2)),(1,3):(F(9,2),F(1),F(1,4)),(2,3):(F(6),F(3,2),F(3,4))}

def allocate(edges,R):
    critical=sorted({v for u,w in edges for v in (DATA[u,w][0],DATA[u,w][0]-DATA[u,w][1]*(P[w]-P[u]))})
    for lo,hi in zip(critical,critical[1:]):
        mid=(lo+hi)/2;active=[];fixed=F(0)
        for e in edges:
            alpha,beta,charge=DATA[e];cap=P[e[1]]-P[e[0]]
            if alpha<=mid:continue
            if alpha-beta*cap>=mid:fixed+=cap
            else:active.append(e)
        if not active:continue
        price=(fixed+sum(DATA[e][0]/DATA[e][1] for e in active)-R)/sum(1/DATA[e][1] for e in active)
        if not lo<=price<=hi:continue
        x=[min(P[v]-P[u],max(F(0),(DATA[u,v][0]-price)/DATA[u,v][1])) for u,v in edges]
        if sum(x)!=R:continue
        value=sum(DATA[e][0]*y-DATA[e][1]*y*y/2-DATA[e][2] for e,y in zip(edges,x))
        upper=price*R+sum(max(DATA[e][0]*z-DATA[e][1]*z*z/2-price*z for z in (F(0),P[e[1]]-P[e[0]],y))-DATA[e][2] for e,y in zip(edges,x))
        assert value==upper
        return value,price,x
    raise ValueError('No allocation')

def run():
    rows=[]
    for h in (1,2,3):
        for R in (F(3),F(6),F(8)):
            answers=[]
            for s in range(h):
                for mid in combinations((1,2),s):
                    vertices=(0,)+mid+(3,);edges=list(zip(vertices,vertices[1:]));v,p,x=allocate(edges,R)
                    answers.append(dict(vertices=vertices,value=str(v),price=str(p),allocation=list(map(str,x))))
            best=max(answers,key=lambda x:F(x['value']))
            rows.append(dict(budget=h,order=str(R),optimum=best,all_configurations=answers))
    out=dict(status='PASS',vertices=list(map(str,P)),modules={str(e):list(map(str,x)) for e,x in DATA.items()},cases=rows)
    (Path(__file__).resolve().parents[1]/'results/PRODUCTION.json').write_text(json.dumps(out,indent=2)+'\n');return out
if __name__=='__main__':print(run())
