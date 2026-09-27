"""R24 matched repeated-query costs, with offline labels and fallback charged.
Timing intervals describe a fixed fitted implementation, not retraining risk.
Run this alone (no concurrent numerical study) for the reported timing results.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import sys,json,gzip,time,platform,gc,resource,argparse,hashlib
from pathlib import Path
import numpy as np
from scipy import sparse
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'or-r22-20260923'))
from core import Tree,Lifted,Polisher,QP,contexts,normalize,Features,Surrogate,RBF

SPECS=[[63,2,6,4,1],[127,2,12,8,1],[255,2,6,4,1]]
TARGETS=[1e-3,1e-5]
NAMES=['lifted-price-continuation','tanh-gradient','rbf-direct']
PHASES=['prediction','initial_solve','first_audit','polishing','fallback_setup','fallback_solve','fallback_audit']


def array_bytes(obj):
    seen=set()
    def visit(x):
        if id(x) in seen:return 0
        seen.add(id(x))
        if isinstance(x,np.ndarray):return int(x.nbytes)
        if isinstance(x,dict):return sum(visit(v) for v in x.values())
        if isinstance(x,(tuple,list)):return sum(visit(v) for v in x)
        if hasattr(x,'__dict__'):return visit(vars(x))
        return 0
    return visit(obj)


def sparse_bytes(a):return int(a.data.nbytes+a.indices.nbytes+a.indptr.nbytes)


def run(pilot=False):
    out=R/('timing-pilot' if pilot else 'results');out.mkdir(exist_ok=True)
    specs=SPECS[:1] if pilot else SPECS
    ntrain,ntest,nrep=(16,2,1) if pilot else (64,32,3)
    rows=[]; setups=[]; fits=[]; primitives=[];failed_labels=[]
    order=np.random.default_rng(2404401)
    started=time.perf_counter()
    with gzip.open(out/'timing_certificates.jsonl.gz','wt') as stream:
      for ix,spec in enumerate(specs):
        nodes,services,rank,capacities,curvature=spec
        t=time.perf_counter();s=Tree(nodes,services,rank,capacities=capacities,curvature=curvature)
        tree_seconds=time.perf_counter()-t
        primitives.append(s.primitives());n=s.n;polisher=Polisher(s)
        t=time.perf_counter();teacher=Lifted(s,eps=1e-9);teacher_setup=time.perf_counter()-t
        train=contexts(2402401+ix,ntrain,rank);V=[];G=[];labelgaps=[]
        for j,c in enumerate(train):
            x,d,it,eta=teacher.solve(c,previous=True)
            audit=s.audit(c,x,d,price=eta,record=True)
            if audit['gap']>1e-5:failed_labels.append({'instance':ix,'id':j,'gap':audit['gap']})
            V.append(s.value(c,x[:n]));G.append(s.U@x[:n]);labelgaps.append(audit['gap'])
            stream.write(json.dumps({'instance':ix,'kind':'label','id':j,'record':audit['record']})+'\n')
        label_seconds=time.perf_counter()-t
        teacher.qp.close()
        if failed_labels:raise AssertionError(('label tolerance',failed_labels))
        X=normalize(train,rank);V=np.array(V);G=np.array(G)
        t=time.perf_counter()
        tanh=Surrogate(Features(rank+1,'tanh',2402401+ix),'gradient',rank).fit(X,V,G)
        fit_tanh=time.perf_counter()-t
        t=time.perf_counter();rbf=RBF().fit(X,V,G);fit_rbf=time.perf_counter()-t
        models={'tanh-gradient':tanh,'rbf-direct':rbf}
        frozen={k:m.frozen() for k,m in models.items()}
        memory={k:{'serialized_bytes':len(json.dumps(frozen[k],separators=(',',':')).encode()),
                   'reachable_array_bytes':array_bytes(m)} for k,m in models.items()}
        fits.append({'instance':ix,'models':frozen,'training_contexts':train.tolist(),
                     'values':V.tolist(),'gradients':G.tolist(),'label_gaps':labelgaps})
        P0=sparse.diags(np.r_[s.d,np.zeros(n)],format='csc')
        coupling=sparse.hstack([-sparse.csc_matrix(s.U),sparse.csc_matrix((rank,n)),sparse.eye(rank)],format='csc')
        LA=sparse.vstack([sparse.hstack([s.M,sparse.csc_matrix((s.M.shape[0],rank))]),coupling],format='csc')
        LP=sparse.diags(np.r_[s.d,np.zeros(n),np.ones(rank)],format='csc')
        setup_rows=[]
        test=contexts(2403401+ix,ntest,rank)
        for rep in range(nrep):
          # Each target has its own continuation state; every method sees the same
          # ordered contexts. Method execution order is randomized within context.
          lifted={};base={}
          for tol in TARGETS:
            t=time.perf_counter();lifted[tol]=Lifted(s,eps=1e-5);ls=time.perf_counter()-t
            t=time.perf_counter();base[tol]=QP(P0,s.M,s.lower,s.upper,eps=1e-5);bs=time.perf_counter()-t
            setup_rows.append({'replicate':rep,'tol':tol,'lifted':ls,'response':bs})
          for j,c in enumerate(test):
            for tol in TARGETS:
              for method in order.permutation(NAMES):
                row={'instance':ix,'spec':spec,'context_id':j,'replicate':rep,'tol':tol,'method':str(method),
                     'context':c.tolist(),'status':'PASS',**{k:0.0 for k in PHASES}}
                t0=time.perf_counter();eta=None
                try:
                    b,lam=s.coefficients(c);q=np.r_[-b,lam*s.k]
                    if method=='lifted-price-continuation':
                        t=time.perf_counter();x,d,it,eta=lifted[tol].solve(c,previous=True)
                        row['initial_solve']=time.perf_counter()-t
                    else:
                        t=time.perf_counter();eta=models[method].predict(normalize(c[None,:],rank))[0]
                        row['prediction']=time.perf_counter()-t
                        t=time.perf_counter();x,d,it=base[tol].solve(q+np.r_[s.U.T@eta,np.zeros(n)])
                        row['initial_solve']=time.perf_counter()-t
                    t=time.perf_counter();initial=s.audit(c,x,d,price=eta,record=True)
                    row['first_audit']=time.perf_counter()-t
                    t=time.perf_counter();polished=polisher.polish(initial['record'],initial=initial)
                    row['polishing']=time.perf_counter()-t
                    row.update(original_gap=initial['gap'],polished_gap=polished['gap'],
                               initial_iterations=it,fallback=bool(polished['gap']>tol),fallback_iterations=0)
                    final=polished
                    if row['fallback']:
                        t=time.perf_counter();refine=Lifted(s,eps=1e-9)
                        row['fallback_setup']=time.perf_counter()-t
                        try:
                            t=time.perf_counter();xx,dd,ii,pp=refine.solve(c,previous=False)
                            row['fallback_solve']=time.perf_counter()-t;row['fallback_iterations']=ii
                            t=time.perf_counter();final=s.audit(c,xx,dd,price=pp,record=True)
                            row['fallback_audit']=time.perf_counter()-t
                        finally:refine.qp.close()
                    row['gap']=final['gap'];assert final['gap']<=tol,('target',final['gap'],tol)
                    row['total']=time.perf_counter()-t0
                    row['unallocated_overhead']=row['total']-sum(row[k] for k in PHASES)
                    stream.write(json.dumps({'instance':ix,'kind':'deployment','context_id':j,'replicate':rep,
                         'tol':tol,'method':str(method),'record':final['record']})+'\n');stream.flush()
                except Exception as error:
                    row.update(status='FAIL',error=repr(error),total=time.perf_counter()-t0)
                    print('FAIL',row,flush=True)
                rows.append(row)
            if j%8==0:print('timing',ix,rep,j,len(rows),flush=True)
          for v in lifted.values():v.qp.close()
          for v in base.values():v.close()
        setups.append({'instance':ix,'spec':spec,'tree_seconds_common':tree_seconds,
          'teacher_setup_included_in_label_seconds':teacher_setup,'label_seconds':label_seconds,
          'label_count':ntrain,'fit_seconds':{'tanh-gradient':fit_tanh,'rbf-direct':fit_rbf},
          'workspace_setup_repetitions':setup_rows,'memory_predictors':memory,
          'response_sparse_matrix_bytes':sparse_bytes(P0)+sparse_bytes(s.M),
          'lifted_sparse_matrix_bytes':sparse_bytes(LP)+sparse_bytes(LA),
          'peak_process_rss_kib_to_this_point':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
        for name,data in [('timing_rows.json',rows),('timing_setup.json',setups),('timing_fits.json',fits)]:
            (out/name).write_text(json.dumps(data,indent=2)+'\n')
        with gzip.open(out/'timing_primitives.json.gz','wt') as f:json.dump(primitives,f)
        for q in (s.full,s.previous_full,s.base):q.close()
        print('completed spec',spec,'rows',len(rows),flush=True)
        del s,polisher,tanh,rbf,models;gc.collect()
    (out/'timing_execution.json').write_text(json.dumps({'status':'EXECUTED','pilot':pilot,
       'rows':len(rows),'failures':sum(a['status']!='PASS' for a in rows),'label_records':ntrain*len(specs),
       'seconds':time.perf_counter()-started,'platform':platform.platform(),'python':sys.version,
       'numpy':np.__version__,'threads':1,'timing_scope':'One study process; numerical studies not run concurrently. Three repetitions per fixed fit and held-out context.',
       'memory_scope':'Model reachable array bytes may include views; sparse input matrix bytes exclude solver factorization. Peak RSS is whole process, not per method.',
       'fallback_scope':'Fresh full solve from zero state; no predictor or previous-context state is passed to fallback.'},indent=2)+'\n')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--pilot',action='store_true');a=ap.parse_args();run(a.pilot)
