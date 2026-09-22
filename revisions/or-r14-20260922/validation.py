#!/usr/bin/env python3
"""Independent cohort for two already frozen scalar critics; no retraining."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import json,hashlib,math
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from star import Star
from study import Critic,contexts
OUT=Path(__file__).resolve().parent/'results'
def main():
    # These settings are fixed in this program before its first execution.
    seed=14999;n=2048;M=2;delta=.05
    s=Star(127,14001);models=json.loads((OUT/'frozen_models.json').read_text())[:2]
    nets=[]
    for m in models:
        c=Critic(np.random.default_rng(0));c.W=np.array(m['critic']['W']);c.b=np.array(m['critic']['b']);c.c=np.array(m['critic']['c'])
        nets.append((m['method'],c))
    # Value is increasing in h, decreasing in lambda, convex in alpha.
    # Therefore the two indicated corners bound the entire declared box.
    corners=[]
    for alpha in [-1.,1.]:
        th=[1.,alpha,.01];y,t,_=s.solve(th);corners.append(s.audit(th,y,t))
    B=max(F(c['dual_upper_fraction'])/F(19,10) for c in corners)
    cohort=contexts(np.random.default_rng(seed),n);records=[];gains={name:[] for name,_ in nets};gaps={name:[] for name,_ in nets}
    for j,theta in enumerate(cohort):
        for name,net in nets:
            _,v=net.predict(theta);y,t,eta,cap=s.surrogate(theta,2*v);a=s.audit(theta,y,t)
            if F(a['gain_fraction'])<0:
                y=np.zeros(s.n);a=s.audit(theta,y,t);gate=True
            else:gate=False
            gain=F(a['gain_fraction'])/F(19,10);assert 0<=gain<=B
            gains[name].append(float(gain));gaps[name].append(a['gap'])
            records.append({'method':name,'context_index':j,'gate_static':gate,'audit':a})
    radius=float(B)*math.sqrt(math.log(M/delta)/(2*n))
    summary={'seed':seed,'n':n,'M':M,'delta':delta,'B_fraction':str(B),'B':float(B),
             'model_sha256':hashlib.sha256((OUT/'frozen_models.json').read_bytes()).hexdigest(),
             'radius':radius,'corners':corners,'selection_rule':'maximize simultaneous gain lower bound; no retraining on this cohort',
             'methods':{name:{'empirical_gain':float(np.mean(gains[name])),
                              'simultaneous_gain_lower':float(np.mean(gains[name]))-radius,
                              'mean_gap':float(np.mean(gaps[name])),
                              'static_gates':sum(r['gate_static'] for r in records if r['method']==name)} for name,_ in nets}}
    summary['selected_method']=max(summary['methods'],key=lambda name:summary['methods'][name]['simultaneous_gain_lower'])
    with (OUT/'validation_policies.jsonl').open('w') as f:
        for r in records:f.write(json.dumps(r,separators=(',',':'))+'\n')
    (OUT/'validation.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='corners'},indent=2))
if __name__=='__main__':main()
