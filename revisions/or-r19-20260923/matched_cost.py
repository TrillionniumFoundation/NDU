#!/usr/bin/env python3
"""Execute R16's unimplemented accuracy-targeted plan; no model selection."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import sys,json,platform
from pathlib import Path
from time import perf_counter
ROOT=Path(__file__).resolve().parent;OLD=ROOT.parent/'or-r16-20260922';sys.path.insert(0,str(OLD))
import numpy as np
from scipy import sparse
from scipy.stats import t as student
from multiresource import Tree
from qp import QP
from surrogates import Features,Surrogate,RBF,fit_all
from study import normalize

def thaw(d):
    if d['kind']=='cubic-rbf':return RBF().fit(np.array(d['X']),None,np.array(d['Y']))
    f=Features(7,d['kind'])
    if f.kind=='tanh':f.W=np.array(d['W']);f.bias=np.array(d['bias'])
    m=Surrogate(f,d['mode'],d['rank']);m.coef=np.array(d['coef']);return m

def run():
    out=ROOT/'results';s=Tree();n=s.n
    P=sparse.block_diag([sparse.csc_matrix(s.H),sparse.csc_matrix((n,n))],format='csc');P0=sparse.diags(np.r_[s.d,np.zeros(n)],format='csc')
    cold=QP(P,s.M,s.lower,s.upper,eps=1e-5);previous={tol:QP(P,s.M,s.lower,s.upper,eps=1e-5) for tol in [1e-3,1e-5]};base=QP(P0,s.M,s.lower,s.upper,eps=1e-5)
    frozen=json.loads((OLD/'results/frozen_models.json').read_text());deploy=json.loads((OLD/'results/deployment.json').read_text());train=json.loads((OLD/'results/training.json').read_text());rows=[];offline=[]
    for ix,(fm,cohort,tr) in enumerate(zip(frozen,deploy,train)):
        assert fm['seed']==cohort['seed']==tr['seed']
        models={k:thaw(v) for k,v in fm['models'].items()};names=['classical-cold','classical-previous']+list(models)
        # All label-generation and all seven model fits are charged to each
        # surrogate, measured on this host. Frozen deployment models are unchanged.
        t0=perf_counter();values=[];gradients=[]
        for label_index,c in enumerate(tr['contexts']):
            x,d,it=s.solve(c,previous=label_index>0);a=s.audit(c,x,d);assert a['gap']<=1e-5
            values.append(s.value(c,x[:n]));gradients.append(s.U@x[:n])
        labels=perf_counter()-t0;t0=perf_counter()
        fit_all(normalize(np.array(tr['contexts']),s.rank),np.array(values),np.array(gradients),tr['seed'])
        offline.append({'seed':tr['seed'],'label_seconds':labels,'fit_all_seconds':perf_counter()-t0})
        for rep in range(2):
            for j,cc in enumerate(cohort['contexts'][:16]):
                c=np.array(cc);b,lam=s.coefficients(c);q=np.r_[-b,lam*s.k];shift=(ix+j+rep)%len(names)
                for name in names[shift:]+names[:shift]:
                    for tol in [1e-3,1e-5]:
                        t0=perf_counter();eta=models[name].predict(normalize(c[None,:],s.rank))[0] if name in models else None
                        pred=perf_counter()-t0 if name in models else 0.;t0=perf_counter()
                        if name=='classical-cold':x,d,it=cold.solve(q)
                        elif name=='classical-previous':x,d,it=previous[tol].solve(q,previous=True)
                        else:x,d,it=base.solve(q+np.r_[s.U.T@eta,np.zeros(n)])
                        response=perf_counter()-t0;a=s.audit(c,x,d,price=eta);fallback=a['gap']>tol;refine=0.;second=0.;gap=a['gap']
                        if fallback:
                            t0=perf_counter();xf,df,iff=s.solve(c,warm=(x,d));refine=perf_counter()-t0
                            af=s.audit(c,xf,df);second=af['audit_seconds'];gap=af['gap']
                        assert gap<=tol,(name,tol,gap)
                        rows.append({'seed':fm['seed'],'rep':rep,'context':j,'method':name,'tol':tol,'prediction':pred,'response':response,'first_audit':a['audit_seconds'],'refinement':refine,'second_audit':second,'total':pred+response+a['audit_seconds']+refine+second,'fallback':fallback,'final_gap':gap})
        print('matched cost',fm['seed'],'PASS',flush=True);(out/'matched_cost_rows.json').write_text(json.dumps(rows)+'\n')
    summary=[];cost=float(np.mean([o['label_seconds']+o['fit_all_seconds'] for o in offline]))
    for tol in [1e-3,1e-5]:
        means={name:float(np.mean([r['total'] for r in rows if r['method']==name and r['tol']==tol])) for name in names};best=min(['classical-cold','classical-previous'],key=means.get)
        for name in names:
            rr=[r for r in rows if r['method']==name and r['tol']==tol];total=np.array([r['total'] for r in rr]);save=means[best]-means[name]
            diffs=[np.mean([r['total'] for r in rr if r['seed']==seed])-np.mean([r['total'] for r in rows if r['method']==best and r['tol']==tol and r['seed']==seed]) for seed in range(15011,15019)]
            mar=student.ppf(.975,7)*np.std(diffs,ddof=1)/np.sqrt(8)
            summary.append({'method':name,'tol':tol,'n':len(rr),'mean':float(total.mean()),'median':float(np.median(total)),'p95':float(np.quantile(total,.95)),'fallback_rate':float(np.mean([r['fallback'] for r in rr])),'classical_comparator':best,'mean_difference_interval95':[float(np.mean(diffs)-mar),float(np.mean(diffs)+mar)],'amortization_cost_seconds':cost if name in models else 0.,'break_even_queries':int(np.ceil((cost+s.base_setup)/save)) if name in models and save>0 else None})
    result={'status':'PASS','observations':len(rows),'plan_source':'revisions/or-r16-20260922/MATCHED_COST_PLAN.json','classification':'follow-up execution of an existing plan, not preregistered learning','state_isolation':'A separate previous-context solver instance is maintained for each requested deployment tolerance; no within-context cross-tolerance iterate reuse.', 'initial_qp_tolerance':1e-5,'refinement_qp_tolerance':1e-9,'summary':summary,'offline':offline,'all_final_certificates_meet_requested_tolerance':True,'inference':'Approximate Student intervals over eight cohort mean differences. Repeats are not independent fits; comparator selection is descriptive.','python':sys.version,'platform':platform.platform()}
    (out/'matched_cost.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':run()
