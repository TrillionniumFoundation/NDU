"""Generate NEW, structured off-ray validation proposals. Not the verifier.
Inherited solver constructs proposals; replay.py independently rebuilds models,
checks rational feasibility, Fenchel bounds and cached upper envelopes.
"""
from __future__ import annotations
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import sys,json,gzip,time,platform,hashlib
from pathlib import Path
from fractions import Fraction as F
R=Path(__file__).resolve().parent;B=R.parent.parent;O=R/'results';O.mkdir(exist_ok=True)
sys.path.insert(0,str(R.parent/'or-r25-20260923'))
import study
import qp
qp.SO=R/'_osqp_bridge.so'

def main():
    p=json.loads((R.parent/'or-r25-20260923/results/radius_primitives.json').read_text())
    with gzip.open(R.parent/'or-r25-20260923/results/radius_certificates.jsonl.gz','rt') as fh:
        old=[json.loads(l) for l in fh]
    contexts=list(dict.fromkeys(tuple(r['context']) for r in old))
    design=[]
    for i,c in enumerate(contexts):
        for k,rho in enumerate((F(1,64),F(1,16),F(1,8))):
            theta=[(-5+3*i+2*k)%13-6,(4+2*i+5*k)%13-6,(7+4*i+3*k)%13-6]
            old_direction=next(r['theta'] for r in old if tuple(r['context'])==c and F(r['rho'])==F(1,16))
            # Exclude the inherited one-dimensional ray by coefficients only,
            # never by an observed performance or objective value.
            if not any(old_direction[a]*theta[b]!=old_direction[b]*theta[a] for a in range(3) for b in range(a+1,3)):
                for j in range(3):
                    candidate=theta.copy();candidate[j]=(candidate[j]+7)%13-6
                    if any(old_direction[a]*candidate[b]!=old_direction[b]*candidate[a] for a in range(3) for b in range(a+1,3)):
                        theta=candidate;break
            design.append({'id':f'offray-{i}-{k}','context_id':i,'context':list(c),'rho':str(rho),'theta':theta})
    (R/'DESIGN.json').write_text(json.dumps({'study':'structured sensitivity; not a random sample or field calibration','anchor_radii':['0','1/16','1/4'],'new_queries':design},indent=2)+'\n')
    records=[];start=time.perf_counter()
    for d in design:
        c=d['context'];rho=F(d['rho']);theta=d['theta']
        m=study.fine_model(p,c,rho,theta,False);outer=study.fine_model(p,c,rho,theta,True)
        full={k:v for k,v in m.items() if not k.startswith('_')};full['E']=[list(map(F,row)) for row in p['E']]
        r=dict(d)
        for kind,mm,ids in [('true',m,None),('outer',outer,None),('full',full,list(range(len(p['qnum']))))]:
            ans=study.solve(p,mm,ids=ids)
            r[kind]={'model':study.serial(mm),**ans}
        records.append(r)
        print(d['id'],'brackets',*[f'{r[k]["gap"]:.2g}' for k in ('true','outer','full')], 'elapsed',round(time.perf_counter()-start,2),flush=True)
    raw=''.join(json.dumps(x,separators=(',',':'))+'\n' for x in records).encode()
    # Deterministic gzip metadata.
    (O/'new_proposals.jsonl.gz').write_bytes(gzip.compress(raw,mtime=0))
    import numpy,scipy,casadi,fitz
    (O/'EXECUTION_PROVENANCE.json').write_text(json.dumps({'base_commit':'38f99a5b46d8cfe4f1197fc869735d5f798c499a','source_commit':os.environ.get('GITHUB_SHA','local working copy based on the pinned scientific predecessor'),'run_id':os.environ.get('GITHUB_RUN_ID'),'proposal_generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'python':sys.version,'platform':platform.platform(),'numpy':numpy.__version__,'scipy':scipy.__version__,'casadi':casadi.__version__,'pymupdf':fitz.VersionBind,'threads':1,'fresh_query_models':24,'new_optimizer_proposals':72,'inherited_anchor_solves':24,'historical_off_ray_queries':False,'interpretation':'New off-ray proposals. Inherited 56-ray holdouts are new bound evaluations of old optimization records, not new solves. No speedup or statistical calibration is claimed.'},indent=2)+'\n')
if __name__=='__main__':main()
