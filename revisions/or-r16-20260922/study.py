#!/usr/bin/env python3
"""Execute the preregistered repeated-train/independent-deployment R16 study."""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1')
import json,platform,sys,hashlib
from pathlib import Path
from time import perf_counter
import numpy as np
from scipy.stats import t as student
from fractions import Fraction as F
from multiresource import Tree,contexts
from surrogates import fit_all
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'results';OUT.mkdir(exist_ok=True)
def dump(name,data):
    (OUT/name).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
def normalize(c,rank):
    a=np.asarray(c,dtype=float).copy();a[:,:rank]/=16;a[:,-1]=(a[:,-1]-17)/15;return a

def run():
    s=Tree();dump('primitives.json',s.primitives())
    allcohorts=[];modelsout=[];traindata=[];testdata=[];timings=[]
    pol=(OUT/'policies.jsonl').open('w');records=0
    for seed in range(15011,15019):
        tr=contexts(seed,256,s.rank);te=contexts(seed+100,256,s.rank)
        trainvalues=[];traingrads=[];labelgaps=[]
        t0=perf_counter()
        for c in tr:
            x,d,it=s.solve(c,previous=True);audit=s.audit(c,x,d)
            if audit['gap']>1e-5:raise AssertionError(('label certificate too wide',audit['gap']))
            trainvalues.append(s.value(c,x[:s.n]));traingrads.append(s.U@x[:s.n]);labelgaps.append(audit['gap'])
        label_seconds=perf_counter()-t0
        X=normalize(tr,s.rank);t0=perf_counter();models=fit_all(X,np.array(trainvalues),np.array(traingrads),seed)
        fit_seconds=perf_counter()-t0
        modelsout.append({'seed':seed,'models':{name:m.frozen() for name,m in models.items()}})
        traindata.append({'seed':seed,'contexts':tr.tolist(),'values':trainvalues,'gradients':np.array(traingrads).tolist(),'reference_gaps':labelgaps,'label_seconds':label_seconds,'fit_all_seconds':fit_seconds})
        preds={name:m.predict(normalize(te,s.rank)) for name,m in models.items()}
        metrics={name:[] for name in models};refs=[]
        for j,c in enumerate(te):
            xr,dr,ir=s.solve(c,previous=True);ref=s.audit(c,xr,dr,record=True)
            if ref['gap']>1e-5:raise AssertionError(('reference certificate too wide',ref['gap']))
            pol.write(json.dumps({'id':f'{seed}:{j}:reference',**ref['record']})+'\n');records+=1
            refs.append({'gain':ref['gain'],'gap':ref['gap'],'iterations':ir,'positive_switches':ref['positive_switches'],'negative_switches':ref['negative_switches'],'near_kinks':ref['near_kinks'],'capacity_binding':int(np.sum(abs(s.C@xr[:s.n]-s.capnum/8)<1e-5)),'tier_boundary':int(np.sum((xr[:s.n]+s.znum/32<1e-5)|(1-s.znum/32-xr[:s.n]<1e-5)))})
            for name,etas in preds.items():
                eta=etas[j];xb,db,ib=s.solve(c,price=eta);a=s.audit(c,xb,db,price=eta,record=True)
                pol.write(json.dumps({'id':f'{seed}:{j}:{name}',**a['record']})+'\n');records+=1
                lo=max(0.,ref['gain']-a['gain']);hi=max(0.,ref['gain']+ref['gap']-a['gain'])
                row={'regret_lower':lo,'regret_upper':hi,'gain':a['gain'],'gap':a['gap'],'gate':a['gate'],'repair':a['repaired'],'iterations':ib,'gradient_mse':float(np.mean((eta-s.U@xr[:s.n])**2)),'pass_1e-3':a['gap']<=1e-3,'pass_1e-5':a['gap']<=1e-5}
                metrics[name].append(row)
        testdata.append({'seed':seed,'deployment_seed':seed+100,'contexts':te.tolist(),'reference':refs,'methods':metrics})
        cohort={name:{key:float(np.mean([r[key] for r in rows])) for key in rows[0]} for name,rows in metrics.items()}
        allcohorts.append({'seed':seed,'reference_gain':float(np.mean([r['gain'] for r in refs])),'methods':cohort})
        print('cohort',seed,'reference',allcohorts[-1]['reference_gain'],'regrets',{n:round(v['regret_upper'],6) for n,v in cohort.items()},flush=True)
        # Every seed is timed on its first 32 independent contexts, with no selection.
        for rep in range(3):
            for j,c in enumerate(te[:32]):
                for baseline in ['cached-full-cold','cached-full-previous']:
                    t0=perf_counter();x,d,it=(s.solve_previous(c) if baseline.endswith('previous') else s.solve(c));ts=perf_counter()-t0
                    a=s.audit(c,x,d)
                    timings.append({'seed':seed,'rep':rep,'context':j,'method':baseline,'tol':None,'prediction':0.,'response':ts,'first_audit':a['audit_seconds'],'refinement':0.,'second_audit':0.,'total':ts+a['audit_seconds'],'gap':a['gap'],'fallback':False,'iterations':it})
                for name,m in models.items():
                    t0=perf_counter();eta=m.predict(normalize(c[None,:],s.rank))[0];ti=perf_counter()-t0
                    t0=perf_counter();x,d,it=s.solve(c,price=eta);ts=perf_counter()-t0;a=s.audit(c,x,d,price=eta)
                    for tol in [1e-3,1e-5]:
                        fallback=a['gap']>tol;trf=0.;t2=0.;gap=a['gap']
                        if fallback:
                            t0=perf_counter();xf,df,iff=s.solve(c,warm=(x,d));trf=perf_counter()-t0;af=s.audit(c,xf,df);t2=af['audit_seconds'];gap=af['gap']
                        assert gap<=tol,('uncertified final pipeline',name,tol,gap)
                        timings.append({'seed':seed,'rep':rep,'context':j,'method':name,'tol':tol,'prediction':ti,'response':ts,'first_audit':a['audit_seconds'],'refinement':trf,'second_audit':t2,'total':ti+ts+a['audit_seconds']+trf+t2,'gap':gap,'fallback':bool(fallback),'iterations':it})
        dump('cohorts.json',allcohorts);dump('training.json',traindata);dump('deployment.json',testdata);dump('frozen_models.json',modelsout)
        pol.flush()
    pol.close();dump('timings.json',timings)
    names=list(allcohorts[0]['methods']);aggregate={}
    for name in names:
        keys=allcohorts[0]['methods'][name];aggregate[name]={key:float(np.mean([c['methods'][name][key] for c in allcohorts])) for key in keys}
    diff=np.array([c['methods']['tanh-gradient']['regret_upper']-c['methods']['tanh-value']['regret_upper'] for c in allcohorts]);se=float(np.std(diff,ddof=1)/np.sqrt(8));margin=float(student.ppf(.975,7)*se)
    timing_summary=[]
    for name in ['cached-full-cold','cached-full-previous']+names:
        for tol in ([None] if name.startswith('cached') else [1e-3,1e-5]):
            rows=[r for r in timings if r['method']==name and r['tol']==tol]
            timing_summary.append({'method':name,'tol':tol,**{k:float(np.median([r[k] for r in rows])) for k in ['total','prediction','response','first_audit','refinement','second_audit']},'fallback_rate':float(np.mean([r['fallback'] for r in rows]))})
    # A deterministic range for gated gain, uniform over the prescribed h box.
    # Completing the diagonal square bounds the best linear/quadratic part;
    # retaining the outside switching constant bounds any possible friction saving.
    exact_bound=sum((F((abs(int(s.bnum[i]))+sum(abs(int(u)) for u in s.Unum[:,i]))**2,128*int(s.qnum[i])) for i in range(s.n)),F(0))
    exact_bound+=F(sum(int(k)*abs(int(v)) for k,v in zip(s.knum,s.vnum)),512)
    # An integer upper bound avoids any floating-point underestimation of the range.
    bound=(exact_bound.numerator+exact_bound.denominator-1)//exact_bound.denominator
    M=8*len(names);penalty=bound*np.sqrt(np.log(M/.05)/(2*256))
    frozen=[{'seed':c['seed'],'method':name,'mean_gain':c['methods'][name]['gain'],'lower_bound':max(0.,c['methods'][name]['gain']-penalty)} for c in allcohorts for name in names]
    summary={'revision':'R16','replications':8,'training_contexts_per_replication':256,'independent_deployment_contexts_per_replication':256,'methods':aggregate,'paired_neural_regret_difference':{'mean':float(np.mean(diff)),'standard_error':se,'interval95':[float(np.mean(diff)-margin),float(np.mean(diff)+margin)],'units':'independent training/deployment pair; approximate Student interval'},'reference_mean_gain':float(np.mean([c['reference_gain'] for c in allcohorts])),'timing':timing_summary,'offline':{'full_setup':s.full_setup,'previous_full_setup':s.previous_setup,'base_setup':s.base_setup,'mean_labels_seconds':float(np.mean([r['label_seconds'] for r in traindata])),'mean_fit_all_seconds':float(np.mean([r['fit_all_seconds'] for r in traindata]))},'frozen_bounds':{'M':M,'delta':.05,'n':256,'deterministic_gain_range_upper':bound,'exact_range_bound':str(exact_bound),'penalty':float(penalty),'bounds':frozen,'note':'A zero lower bound is vacuous beyond comparator safety; no population training guarantee is inferred.'},'certificate_records':records,'python':sys.version,'platform':platform.platform()}
    dump('summary.json',summary);print(json.dumps(summary,indent=2),flush=True)
if __name__=='__main__':run()
