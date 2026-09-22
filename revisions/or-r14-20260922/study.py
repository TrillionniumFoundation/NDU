#!/usr/bin/env python3
"""Frozen paired scalar-critic study, including complete rational audit costs."""
from __future__ import annotations
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import json,time,hashlib,platform,sys
from pathlib import Path
import numpy as np
from scipy.stats import t as student
import scipy
from star import Star
HERE=Path(__file__).resolve().parent;OUT=HERE/'results';OUT.mkdir(exist_ok=True)
PLAN=json.loads((HERE/'EXPERIMENT_PLAN.json').read_text())
def contexts(rng,n):
    return np.column_stack([rng.integers(-1000,1001,n),rng.integers(-1000,1001,n),rng.integers(10,201,n)])/1000
class Critic:
    def __init__(self,rng,k=192):
        self.W=rng.normal(0,PLAN['weight_scale'],(3,k));self.b=rng.uniform(-1,1,k)
    def features(self,theta):
        x=np.atleast_2d(theta).copy();x[:,2]=(x[:,2]-.105)/.095
        t=np.tanh(x@self.W+self.b)
        phi=np.column_stack([np.ones(len(x)),x,t])
        dh=np.column_stack([np.zeros(len(x)),np.ones(len(x)),np.zeros((len(x),2)),(1-t*t)*self.W[0]])
        return phi,dh
    def fit(self,theta,value,grad,gamma):
        p,dh=self.features(theta);n=len(theta)
        self.c=np.linalg.solve((p.T@p+gamma*dh.T@dh)/n+PLAN['ridge_coefficient']*np.eye(p.shape[1]),
                               (p.T@value+gamma*dh.T@grad)/n)
    def predict(self,theta):
        p,dh=self.features(theta);return float(p[0]@self.c),float(dh[0]@self.c)
    def dump(self):return {'W':self.W.tolist(),'b':self.b.tolist(),'c':self.c.tolist()}
def paired_ci(values):
    x=np.asarray(values,dtype=float);r=float(student.ppf(.975,len(x)-1)*x.std(ddof=1)/np.sqrt(len(x)))
    return {'n_training_seeds':len(x),'mean':float(x.mean()),'lower':float(x.mean()-r),'upper':float(x.mean()+r),
            'method':'paired Student t interval across independent training seeds, conditional on the shared test cohort'}
def main():
    start=time.perf_counter();s=Star(127,PLAN['primitive_seed'])
    (OUT/'primitives.json').write_text(json.dumps(s.primitives(),indent=2)+'\n')
    test=contexts(np.random.default_rng(PLAN['test_seed']),PLAN['test_contexts'])
    truth=[s.targets(t) for t in test]
    frozen=[];records=[];rows=[];training=[];pipelines=[]
    for seed in PLAN['paired_training_seeds']:
        rng=np.random.default_rng(seed);x=contexts(rng,PLAN['training_contexts_per_seed'])
        st=time.perf_counter();targets=np.asarray([s.targets(t)[:2] for t in x]);labeltime=time.perf_counter()-st
        initial=Critic(rng,PLAN['hidden_tanh_units'])
        for name,gamma in [('value',0.),('value-gradient',PLAN['gradient_loss_weight'])]:
            net=Critic(np.random.default_rng(0),PLAN['hidden_tanh_units']);net.W=initial.W.copy();net.b=initial.b.copy()
            st=time.perf_counter();net.fit(x,targets[:,0],targets[:,1],gamma);fit=time.perf_counter()-st
            frozen.append({'seed':seed,'method':name,'critic':net.dump()})
            training.append({'seed':seed,'method':name,'label_seconds':labeltime,'fit_seconds':fit,
                             'contexts':x.tolist(),'values':targets[:,0].tolist(),'partial_gradients':targets[:,1].tolist()})
            vals=[]
            for j,(theta,(opt,vstar,etastar)) in enumerate(zip(test,truth)):
                predicted,vg=net.predict(theta);y,tau,eta,cap=s.surrogate(theta,s.q0*vg)
                audit=s.audit(theta,y,tau);actual=(opt-s.value(theta,y))/s.mass
                global_bound=.5*s.q0**2*s.R*(1+s.q0*s.R)*(vg-vstar)**2/s.mass
                price_bound=.5*s.kappa*(eta-s.q0*(s.rho@y))**2/s.mass
                assert actual>=-1e-11 and actual<=global_bound+1e-10 and actual<=price_bound+1e-10
                row={'seed':seed,'method':name,'context_index':j,'optimal_gain':opt/s.mass,
                     'raw_gain':s.value(theta,y)/s.mass,'raw_regret':max(0.,actual),'value_error':predicted-opt,
                     'partial_gradient_error':vg-vstar,'predicted_coupling_price':eta,'cap_projection':cap,
                     'residual_bound':price_bound,'gradient_bound':global_bound,
                     'refinement_required':audit['gap']>PLAN['certificate_tolerance_per_discounted_review'],
                     'static_gate':audit['gain']<0,'audit':audit}
                records.append(row);vals.append(row)
            rows.append({'seed':seed,'method':name,'mean_regret':float(np.mean([v['raw_regret'] for v in vals])),
                         'mean_gain':float(np.mean([v['raw_gain'] for v in vals])),
                         'value_mse':float(np.mean([v['value_error']**2 for v in vals])),
                         'gradient_mse':float(np.mean([v['partial_gradient_error']**2 for v in vals])),
                         'mean_certificate':float(np.mean([v['audit']['gap'] for v in vals])),
                         'mean_gradient_bound':float(np.mean([v['gradient_bound'] for v in vals])),
                         'mean_residual_bound':float(np.mean([v['residual_bound'] for v in vals])),
                         'immediate_fraction':float(np.mean([not v['refinement_required'] for v in vals])),
                         'static_gate_fraction':float(np.mean([v['static_gate'] for v in vals])),
                         'cap_projection_fraction':float(np.mean([v['cap_projection'] for v in vals]))})
            if seed==PLAN['paired_training_seeds'][0]:pipelines.append((name,net))
        print('paired seed complete',seed,flush=True)
    timing=[]
    for rep in range(PLAN['timing_repetitions']):
        for j,theta in enumerate(test[:PLAN['timing_contexts']]):
            choices=[('cold-newton',None),('Brent',None),('breakpoints',None)]+pipelines
            off=(rep+j)%len(choices);choices=choices[off:]+choices[:off]
            for name,net in choices:
                st=time.perf_counter_ns();pred_ns=repair_ns=audit_ns=refine_ns=0;refined=False;cap=False;its=0
                if net is None:
                    method={'cold-newton':'newton','Brent':'brent','breakpoints':'sort'}[name]
                    tt=time.perf_counter_ns();y,tau,meta=s.solve(theta,method);refine_ns=time.perf_counter_ns()-tt;its=meta['iterations']
                    tt=time.perf_counter_ns();a=s.audit(theta,y,tau);audit_ns=time.perf_counter_ns()-tt
                else:
                    tt=time.perf_counter_ns();_,v=net.predict(theta);pred_ns=time.perf_counter_ns()-tt
                    tt=time.perf_counter_ns();y,tau,eta,cap=s.surrogate(theta,s.q0*v);repair_ns=time.perf_counter_ns()-tt
                    tt=time.perf_counter_ns();a=s.audit(theta,y,tau);audit_ns=time.perf_counter_ns()-tt
                    if a['gap']>PLAN['certificate_tolerance_per_discounted_review']:
                        refined=True;tt=time.perf_counter_ns();y,tau,meta=s.solve(theta,'newton',initial=tau);refine_ns=time.perf_counter_ns()-tt;its=meta['iterations']
                        tt=time.perf_counter_ns();a=s.audit(theta,y,tau);audit_ns+=time.perf_counter_ns()-tt
                total=time.perf_counter_ns()-st
                assert a['gap']<=PLAN['certificate_tolerance_per_discounted_review']
                timing.append({'repetition':rep,'context_index':j,'method':name,'total_ms':total/1e6,
                    'prediction_ms':pred_ns/1e6,'repair_ms':repair_ns/1e6,'audit_ms':audit_ns/1e6,
                    'refinement_ms':refine_ns/1e6,'iterations':its,'refined':refined,'cap_projection':cap,'audit':a})
    def means(key,name):return float(np.mean([r[key] for r in rows if r['method']==name]))
    comparison={}
    for metric in ['mean_regret','gradient_mse','value_mse','mean_certificate']:
        comparison[metric]=paired_ci([next(r[metric] for r in rows if r['seed']==seed and r['method']=='value-gradient')-
                                      next(r[metric] for r in rows if r['seed']==seed and r['method']=='value')
                                      for seed in PLAN['paired_training_seeds']])
    sums={name:{key:means(key,name) for key in rows[0] if key not in ('seed','method')} for name in ['value','value-gradient']}
    timingsummary={}
    for name in sorted(set(v['method'] for v in timing)):
        rr=[v for v in timing if v['method']==name]
        timingsummary[name]={'median_total_ms':float(np.median([v['total_ms'] for v in rr])),
                            'median_audit_ms':float(np.median([v['audit_ms'] for v in rr])),
                            'median_prediction_ms':float(np.median([v['prediction_ms'] for v in rr])),
                            'median_repair_ms':float(np.median([v['repair_ms'] for v in rr])),
                            'median_solver_ms':float(np.median([v['refinement_ms'] for v in rr])),
                            'mean_iterations':float(np.mean([v['iterations'] for v in rr])),
                            'refinement_fraction':float(np.mean([v['refined'] for v in rr]))}
    summary={'plan_sha256':hashlib.sha256((HERE/'EXPERIMENT_PLAN.json').read_bytes()).hexdigest(),
             'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'platform':platform.platform(),
             'leaves':s.n,'positive_friction':True,'test_contexts':len(test),'paired_training_seeds':8,
             'policy_records':len(records),'timing_records':len(timing),'R':s.R,'kappa':s.kappa,
             'mean_optimal_gain':float(np.mean([v[0]/s.mass for v in truth])),
             'methods':sums,'paired_differences':comparison,'timing':timingsummary,
             'total_training_label_seconds':sum(v['label_seconds'] for v in training if v['method']=='value'),
             'fit_seconds':{name:sum(v['fit_seconds'] for v in training if v['method']==name) for name in sums},
             'wall_seconds':time.perf_counter()-start}
    for name,obj in [('frozen_models.json',frozen),('training.json',training),('paired_seeds.json',rows),
                     ('summary.json',summary),('contexts.json',test.tolist())]:
        (OUT/name).write_text(json.dumps(obj,indent=2)+'\n')
    for name,obj in [('policies.jsonl',records),('timings.jsonl',timing)]:
        with (OUT/name).open('w') as f:
            for r in obj:f.write(json.dumps(r,separators=(',',':'))+'\n')
    print(json.dumps(summary,indent=2),flush=True)
if __name__=='__main__':main()
