"""Full accepted-polyhedron scaling with refitted learned price comparisons."""
from core import *
import gzip,gc,platform
OUT=ROOT/'results'
def run():
    specs=json.loads((ROOT/'DESIGN.json').read_text())['scaling']['specs']
    rows=[];setup=[];primitives=[];fits=[];tolset=[1e-3,1e-5]
    with gzip.open(OUT/'scaling_certificates.jsonl.gz','wt') as f:
      for ix,spec in enumerate(specs):
        nodes,services,rank,capacities,curvature=spec
        t=perf_counter();s=Tree(nodes,services,rank,capacities=capacities,curvature=curvature);tree_time=perf_counter()-t
        poli=Polisher(s);n=s.n;primitives.append(s.primitives())
        # Refit on a separate, predeclared training population for this primitive.
        label_solver=Lifted(s,eps=1e-9)
        tr=contexts(25001+ix,64,rank);V=[];G=[];labelgaps=[];t=perf_counter()
        for j,c in enumerate(tr):
            x,d,it,eta=label_solver.solve(c,previous=True);a=s.audit(c,x,d,price=eta,record=True)
            assert a['gap']<=1e-5,(spec,j,a['gap'])
            if (j+1)%32==0:print('labels',ix,j+1,flush=True)
            V.append(s.value(c,x[:n]));G.append(s.U@x[:n]);labelgaps.append(a['gap'])
            f.write(json.dumps({'instance':ix,'kind':'label','context':j,'record':a['record']})+'\n')
        labeltime=perf_counter()-t;label_solver.qp.close();t=perf_counter();X=normalize(tr,rank)
        models={'tanh-gradient':Surrogate(Features(rank+1,'tanh',25001+ix),'gradient',rank).fit(X,np.array(V),np.array(G)),
                'rbf-direct':RBF().fit(X,np.array(V),np.array(G))}
        fitcost=perf_counter()-t
        fits.append({'instance':ix,'training_contexts':tr.tolist(),'values':V,'gradients':np.array(G).tolist(),
                     'label_gaps':labelgaps,'models':{k:m.frozen() for k,m in models.items()}})
        P=sparse.block_diag([sparse.csc_matrix(s.H),sparse.csc_matrix((n,n))],format='csc')
        P0=sparse.diags(np.r_[s.d,np.zeros(n)],format='csc')
        t=perf_counter();cold=QP(P,s.M,s.lower,s.upper,eps=1e-5);coldsetup=perf_counter()-t
        t=perf_counter();previous={tol:QP(P,s.M,s.lower,s.upper,eps=1e-5) for tol in tolset};prevsetup=perf_counter()-t
        lifted={tol:Lifted(s) for tol in tolset};base=QP(P0,s.M,s.lower,s.upper,eps=1e-5)
        setup.append(dict(spec=spec,variables=n,tree_initialization=tree_time,dense_setup=coldsetup,previous_setup=prevsetup,
                          lifted_setup=sum(v.setup for v in lifted.values()),dense_P_nnz=P.nnz,lifted_P_nnz=lifted[1e-3].P_nnz,
                          lifted_A_nnz=lifted[1e-3].A_nnz,label_seconds=labeltime,label_backend='lifted full objective, eps 1e-9, independently audited gap',fit_both_seconds=fitcost))
        names=['dense-cold','dense-previous','lifted-price-continuation']+list(models)
        for j,c in enumerate(contexts(24001+ix,8,rank)):
          b,lam=s.coefficients(c);q=np.r_[-b,lam*s.k];shift=(ix+j)%len(names)
          for name in names[shift:]+names[:shift]:
           for tol in tolset:
            t=perf_counter();eta=None
            try:
              if name=='dense-cold':x,d,it=cold.solve(q)
              elif name=='dense-previous':x,d,it=previous[tol].solve(q,previous=True)
              elif name=='lifted-price-continuation':x,d,it,eta=lifted[tol].solve(c,previous=True)
              else:
                eta=models[name].predict(normalize(c[None,:],rank))[0]
                x,d,it=base.solve(q+np.r_[s.U.T@eta,np.zeros(n)])
              a=s.audit(c,x,d,price=eta,record=True);ap=poli.polish(a['record'],initial=a)
              fallback=ap['gap']>tol;final=ap
              if fallback:
                x,d,ii=s.solve(c,warm=(x,d));final=s.audit(c,x,d,record=True)
              total=perf_counter()-t
              assert final['gap']<=tol
              rows.append(dict(instance=ix,spec=spec,context=j,method=name,tol=tol,total=total,iterations=it,
                               fallback=bool(fallback),original_gap=a['gap'],polished_gap=ap['gap'],gap=final['gap'],status='PASS'))
              f.write(json.dumps({'instance':ix,'kind':'deployment','context':j,'method':name,'tol':tol,'record':final['record']})+'\n')
            except Exception as e:
              rows.append(dict(instance=ix,spec=spec,context=j,method=name,tol=tol,total=perf_counter()-t,status='FAIL',error=repr(e)))
              print('FAIL',ix,j,name,repr(e),flush=True)
        for filename,obj in [('scaling_rows.json',rows),('scaling_fits.json',fits)]:
            (OUT/filename).write_text(json.dumps(obj)+'\n')
        with gzip.open(OUT/'scaling_primitives.json.gz','wt') as pf:json.dump(primitives,pf)
        print('scaling',ix,spec,'complete',len(rows),flush=True)
        for q in [cold,base,*previous.values(),*[ll.qp for ll in lifted.values()],s.full,s.previous_full,s.base]:q.close()
        del s,poli,cold,previous,lifted,base;gc.collect()
    summary=[]
    for ix,spec in enumerate(specs):
     for tol in tolset:
      for name in names:
        rr=[r for r in rows if r['instance']==ix and r['method']==name and r['tol']==tol];ok=[r for r in rr if r['status']=='PASS']
        summary.append(dict(instance=ix,spec=spec,method=name,tol=tol,attempts=len(rr),failures=len(rr)-len(ok),
            mean_ms=float(np.mean([r['total'] for r in rr])*1000),p95_ms=float(np.quantile([r['total'] for r in rr],.95)*1000),
            fallback=float(np.mean([r['fallback'] for r in ok])) if ok else None))
    (OUT/'scaling_summary.json').write_text(json.dumps({'status':'PASS' if all(r['status']=='PASS' for r in rows) else 'FAILURES_RETAINED',
      'observations':len(rows),'label_records':64*len(specs),'summary':summary,'setup':setup,'platform':platform.platform(),
      'scope':'Ten primitive configurations; one independent 64-label fit per configuration and eight held-out contexts. Descriptive structural scaling, not an algorithm-level confidence guarantee.'},indent=2)+'\n')
if __name__=='__main__':run()
