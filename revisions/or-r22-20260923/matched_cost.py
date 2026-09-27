"""All seven frozen predictors versus three classical pipelines at matched accuracy."""
from core import *
import gzip, platform
from scipy.stats import t as student
OUT=ROOT/'results';OUT.mkdir(exist_ok=True)
def run():
    s=Tree();poli=Polisher(s);n=s.n
    P=sparse.block_diag([sparse.csc_matrix(s.H),sparse.csc_matrix((n,n))],format='csc')
    P0=sparse.diags(np.r_[s.d,np.zeros(n)],format='csc')
    cold=QP(P,s.M,s.lower,s.upper,eps=1e-5)
    previous={tol:QP(P,s.M,s.lower,s.upper,eps=1e-5) for tol in [1e-3,1e-5]}
    lifted={tol:Lifted(s) for tol in [1e-3,1e-5]}
    base=QP(P0,s.M,s.lower,s.upper,eps=1e-5)
    cohortdata=json.loads((OLD/'results/deployment.json').read_text())
    models=frozen_models();rows=[];decompositions=[]
    (OUT/'primitives.json').write_text(json.dumps(s.primitives())+'\n')
    with gzip.open(OUT/'matched_certificates.jsonl.gz','wt') as f:
      for ix,(cohort,mm) in enumerate(zip(cohortdata,models)):
        names=['classical-cold','classical-previous','lifted-price-continuation']+list(mm)
        for rep in range(2):
          for j,cc in enumerate(cohort['contexts'][:16]):
            c=np.array(cc);b,lam=s.coefficients(c);q=np.r_[-b,lam*s.k]
            shift=(ix+j+rep)%len(names)
            for name in names[shift:]+names[:shift]:
              for tol in [1e-3,1e-5]:
                start=perf_counter();t0=start
                eta=mm[name].predict(normalize(c[None,:]))[0] if name in mm else None
                pred=perf_counter()-t0 if name in mm else 0.;t0=perf_counter()
                if name=='classical-cold':x,d,it=cold.solve(q)
                elif name=='classical-previous':x,d,it=previous[tol].solve(q,previous=True)
                elif name=='lifted-price-continuation':x,d,it,eta=lifted[tol].solve(c,previous=True)
                else:x,d,it=base.solve(q+np.r_[s.U.T@eta,np.zeros(n)])
                response=perf_counter()-t0
                a=s.audit(c,x,d,price=eta,record=True)
                ap=poli.polish(a['record'],initial=a)
                fallback=ap['gap']>tol;refine=0.;second=0.;final=ap
                if fallback:
                    t0=perf_counter();xx,dd,ii=s.solve(c,warm=(x,d));refine=perf_counter()-t0
                    final=s.audit(c,xx,dd,record=True);second=final['audit_seconds']
                total=perf_counter()-start
                assert final['gap']<=tol,(name,tol,final['gap'])
                assert F(ap['upper_exact'])<=F(a['upper_exact'])
                ident=f'{ix}:{rep}:{j}:{name}:{tol}'
                f.write(json.dumps({'id':ident,'before':a['record'],'after':ap['record'],
                                    'final':final['record'],'tolerance':tol})+'\n')
                rows.append(dict(id=ident,cohort=ix,rep=rep,context=j,method=name,tol=tol,
                    prediction=pred,response=response,audit=a['audit_seconds'],polishing=ap['polishing_seconds'],
                    refinement=refine,second_audit=second,total=total,original_gap=a['gap'],
                    polished_gap=ap['gap'],final_gap=final['gap'],fallback=bool(fallback),
                    original_pass=bool(a['gap']<=tol),polished_pass=bool(ap['gap']<=tol),
                    polish_steps=ap['polish_steps'],iterations=it))
                if rep==0 and j==0:
                    decompositions.append({'id':ident,'before':decompose(s.p,a['record']),
                                           'after':decompose(s.p,ap['record'])})
        print('matched',ix,'complete',len(rows),flush=True)
        (OUT/'matched_rows.json').write_text(json.dumps(rows)+'\n')
    summary=[]
    for tol in [1e-3,1e-5]:
      means={name:float(np.mean([r['total'] for r in rows if r['method']==name and r['tol']==tol])) for name in names}
      best=min(names[:3],key=means.get)
      for name in names:
        rr=[r for r in rows if r['method']==name and r['tol']==tol]
        diff=[np.mean([r['total'] for r in rr if r['cohort']==k])-np.mean([r['total'] for r in rows if r['method']==best and r['tol']==tol and r['cohort']==k]) for k in range(8)]
        mar=student.ppf(.975,7)*np.std(diff,ddof=1)/np.sqrt(8)
        summary.append(dict(method=name,tol=tol,n=len(rr),mean_ms=1000*means[name],
          median_ms=float(np.median([r['total'] for r in rr])*1000),p95_ms=float(np.quantile([r['total'] for r in rr],.95)*1000),
          original_pass=float(np.mean([r['original_pass'] for r in rr])),polished_pass=float(np.mean([r['polished_pass'] for r in rr])),
          fallback=float(np.mean([r['fallback'] for r in rr])),polish_ms=float(np.mean([r['polishing'] for r in rr])*1000),
          mean_difference_interval95_ms=[float((np.mean(diff)-mar)*1000),float((np.mean(diff)+mar)*1000)],classical_comparator=best))
    result={'observations':len(rows),'status':'PASS','summary':summary,'host':platform.platform(),
      'python':sys.version,'design':'DESIGN.json','first_eps':1e-5,'fallback_eps':1e-9,
      'all_final_certificates_valid':True,'all_primal_unchanged_by_price_polishing':True,
      'factorization':'All OSQP objects cache matrices and workspaces; adaptive rho and polishing can trigger numerical refactorization. No symbolic/numeric reuse is claimed across different formulations.',
      'warm_state':'Previous and lifted retain primal and all dual iterates in separate instances per target; cold and surrogate response reset iterates.',
      'timing':'Actual sequential wall time includes prediction, response, rational repair/audit, polishing, actual fallback and final audit. Host-specific; cohort Student intervals are descriptive.'}
    (OUT/'matched_summary.json').write_text(json.dumps(result,indent=2)+'\n')
    (OUT/'decompositions.json').write_text(json.dumps(decompositions)+'\n')
    print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':run()
