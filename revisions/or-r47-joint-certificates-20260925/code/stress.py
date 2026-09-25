"""Declared saturation/charge stress cases and successive certified refinements.

This supplementary protocol was added after the primary protocol, to expose
unresolved coarse relaxations; it is not an out-of-sample performance claim.
"""
from fractions import Fraction as F
from pathlib import Path
import json,time
from coarsening import Instance,solve,refine_partition,encode
from benchmark import savecert
from check_coarsening import check
from box_solver import exhaustive_joint
R=Path(__file__).resolve().parents[1]

def run():
    rows=[];a=tuple(F(i,4) for i in range(5))
    specifications=[dict(id=f'stress-{z}',gamma2=g,budget=m,charge=charge)
      for z,(g,m,charge) in enumerate(((F(5,2),2,F(0)),(F(6),2,F(0)),(F(5,2),1,F(0)),(F(6),1,F(1,20))))]
    (R/'STRESS_PROTOCOL.json').write_text(json.dumps(encode(dict(cases=specifications,
       caps=['1/5','2/5','4/5'],weights=['1/5','3/10','1/2'],ceilings=['1','1','1'],
       promise='sum weighted caps',initial_groups=[[0],[1,2]],requested_epsilon='1/1000',
       refinement='split maximum positive-defect group; stop at original tolerance',
       disclosure='Supplementary stress protocol added after primary runs; all four cases retained')),indent=2)+'\n')
    for spec in specifications:
        D=Instance.make([F(1,5),F(2,5),F(4,5)],[F(1,5),F(3,10),F(1,2)],[F(1),F(2),spec['gamma2']],[F(1)]*3)
        rho=(spec['charge'],)*5;B=D.cap_total;G=((0,),(1,2));stages=[];bestl=None;bestu=None
        reference=exhaustive_joint(D,a,rho,B,spec['budget'])
        for stage in range(3):
            c=solve(D,a,rho,B,spec['budget'],G,F(1,1000),max_nodes=301)
            cc=savecert(spec['id']+f'-stage-{stage}',c,check)
            bestl=c['lower_bound'] if bestl is None else max(bestl,c['lower_bound'])
            bestu=c['upper_bound'] if bestu is None else min(bestu,c['upper_bound'])
            assert bestl<=reference['value']<=bestu
            stages.append(dict(groups=len(G),lower=c['lower_bound'],upper=c['upper_bound'],gap=c['gap'],
                carried_lower=bestl,carried_upper=bestu,carried_gap=bestu-bestl,
                uniform_defect=c['uniform_defect'],posterior_defect=c['posterior_defect'],
                status=c['status'],seconds=c['seconds'],certificate=cc))
            if bestu-bestl<=F(1,1000):break
            G=refine_partition(D,a,G)
            if G is None:break
        rows.append(dict(**spec,reference_value=reference['value'],stages=stages))
    (R/'results/stress.json').write_text(json.dumps(encode(dict(cases=rows)),indent=2)+'\n')
    print(json.dumps(encode(rows),indent=2))
if __name__=='__main__':run()
