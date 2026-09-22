#!/usr/bin/env python3
"""R14 star reassessment with direct/non-neural models and difficult strata.
All contexts are rounded to the original exact auditor's 0.001 grid BEFORE
solving or fitting. No audit silently changes the optimization context.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
import sys,json
from time import perf_counter
import numpy as np
from surrogates import fit_all,Features,Surrogate
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'results'
sys.path.insert(0,str(ROOT.parent/'or-r14-20260922'))
from star import Star

def population(rng,n,stratum,s):
    c=np.c_[rng.uniform(-.4,.4,n),rng.uniform(-.5,.5,n),rng.uniform(.01,.20,n)]
    if stratum=='critical-friction':
        c[:,2]=[max(.001,s.critical(t)*r) for t,r in zip(c,rng.uniform(.9,1.1,n))]
    elif stratum=='capacity-activation':c[:,0]=rng.uniform(1.8,3.2,n)
    return np.round(c,3)

def run():
    star=Star();rng=np.random.default_rng(15399)
    strata=['original','critical-friction','capacity-activation','primitive-perturbation']
    # Perturbations change tariffs and forcing, not merely a fitted-context value.
    shifted=[Star(seed=15401+j) for j in range(4)]
    tests={name:population(rng,128,name,star) for name in strata}
    allrows=[];timings=[];trainrows=[]
    for seed in range(15311,15315):
        rg=np.random.default_rng(seed)
        # An equal mixture of the original, critical, and capacity strata is
        # specified in the executable source before its first remote run.
        train=np.concatenate([population(rg,256,'original',star),population(rg,128,'critical-friction',star),population(rg,128,'capacity-activation',star)])
        target=np.array([star.targets(c)[:2] for c in train]);models=fit_all(train,target[:,0],target[:,1,None],seed)
        models['cubic-value']=Surrogate(Features(3,'cubic'), 'value',1).fit(train,target[:,0],target[:,1,None])
        trainrows.append({'seed':seed,'contexts':train.tolist(),'values':target[:,0].tolist(),'derivatives':target[:,1].tolist(),'models':{n:m.frozen() for n,m in models.items()}})
        for stratum in strata:
            for j,c in enumerate(tests[stratum]):
                s=shifted[j%4] if stratum=='primitive-perturbation' else star
                exact,price,_=s.solve(c,'newton');ref=s.audit(c,exact,price);d=s.d(c)
                active=(exact>1e-7)&(exact<s.b-1e-7);nearest=float(np.min(abs(np.r_[d/s.rho,(d-s.q*s.b)/s.rho]-price)))
                base={'seed':seed,'stratum':stratum,'context':c.tolist(),'primitive_seed':s.seed,'critical_friction':s.critical(c),'friction_distance':float(c[-1]-s.critical(c)),'capacity_binding':bool(abs(s.rho@exact-s.b0)<1e-7),'active_leaves':int(np.sum(active)),'saturated_leaves':int(np.sum(exact>s.b-1e-7)),'breakpoint_distance':nearest,'optimal_gain_lower':ref['gain'],'optimal_gap':ref['gap']}
                for name,m in models.items():
                    t0=perf_counter();eta=s.q0*float(m.predict(c[None,:])[0,0]);predict=perf_counter()-t0
                    t0=perf_counter();y,tau,learned,projection=s.surrogate(c,eta);response=perf_counter()-t0
                    t0=perf_counter();a=s.audit(c,y,tau);audit=perf_counter()-t0
                    gain=max(0.,a['gain']);gap=a['gap']+a['gain']-gain
                    row={**base,'method':name,'gain':gain,'gate':a['gain']<0,'gap':gap,'regret_upper':max(0.,ref['gain']+ref['gap']-gain),'root_repair':projection,'pass_1e-7':gap<=1e-7,'pass_1e-3':gap<=1e-3}
                    allrows.append(row)
                    if j<32:timings.append({'seed':seed,'stratum':stratum,'context':j,'method':name,'prediction':predict,'response':response,'audit':audit,'total':predict+response+audit})
                if j<32:
                    for method in ['newton','brent']:
                        t0=perf_counter();y,tau,_=s.solve(c,method);response=perf_counter()-t0;t0=perf_counter();s.audit(c,y,tau);audit=perf_counter()-t0
                        timings.append({'seed':seed,'stratum':stratum,'context':j,'method':method,'response':response,'audit':audit,'total':response+audit})
        print('star reassessment',seed,'completed',flush=True)
    summary=[]
    for stratum in strata:
        for name in models:
            rows=[r for r in allrows if r['stratum']==stratum and r['method']==name]
            summary.append({'stratum':stratum,'method':name,**{k:float(np.mean([r[k] for r in rows])) for k in ['regret_upper','gain','gap','gate','root_repair','pass_1e-7','pass_1e-3','capacity_binding','active_leaves','saturated_leaves','optimal_gain_lower']},'contexts':len(rows)})
    for name,obj in [('star_rows.json',allrows),('star_timings.json',timings),('star_training.json',trainrows),('star_summary.json',summary)]:
        (OUT/name).write_text(json.dumps(obj,indent=2)+'\n')
if __name__=='__main__':run()
