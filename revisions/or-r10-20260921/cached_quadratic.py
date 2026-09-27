#!/usr/bin/env python3
"""Cached-factor, preconditioned and end-to-end audit of the unchanged R7 task."""
from pathlib import Path
import json,sys,time
import numpy as np
from scipy.sparse import csr_matrix,diags
from scipy.sparse.linalg import splu,spsolve,cg
from scipy.linalg import cho_factor,cho_solve
BASE=Path(__file__).resolve().parent;OLD=BASE.parent/'or-r7-20260921'
sys.path.insert(0,str(OLD));import portfolio_learning as old
R=BASE/'results';T=BASE/'tables'

def run():
    data=json.loads((OLD/'results/portfolio_test_graphs.json').read_text())
    trained=json.loads((OLD/'results/portfolio_training.json').read_text())
    coeff=np.array(next(x['coefficients'] for x in trained if x['seed']==101 and x['mode']=='value_gradient'))
    rows=[];records=[]
    for p in data:
        d=p['d'];pid=f"{d}-{p['rep']}";a=np.array(p['a_integers'],dtype=np.int64)
        Ki=csr_matrix((np.array(p['K_numerators'],dtype=np.int64),p['K_indices'],p['K_indptr']),shape=(d,d));K=Ki.astype(float)/10
        start=time.perf_counter();factor=splu(K.tocsc());sparse_setup=time.perf_counter()-start
        start=time.perf_counter();chol=cho_factor(K.toarray(),check_finite=False);dense_setup=time.perf_counter()-start
        start=time.perf_counter();pre=diags(1/K.diagonal());pcg_setup=time.perf_counter()-start
        def iterative(B):
            cols=[]
            for b in B.T:
                x,info=cg(K,b,M=pre,rtol=1e-10,atol=0,maxiter=5*d)
                assert info==0;cols.append(x)
            return np.stack(cols,axis=1)
        methods={'fresh_sparse':(lambda B:spsolve(K,B),0.),'cached_sparse':(factor.solve,sparse_setup),
                 'cached_dense':(lambda B:cho_solve(chol,B,check_finite=False),dense_setup),
                 'jacobi_pcg':(iterative,pcg_setup),'analytic_filter':(lambda B:old.apply(K,B,old.chebyshev()),0.),
                 'learned_gradient':(lambda B:old.apply(K,B,coeff),0.)}
        for method,(solve,setup) in methods.items():
            elapsed=[];audit=[]
            for rep in range(16):
                start=time.perf_counter();xi,eta,clip=old.calibrate(K,a,solve);mid=time.perf_counter()
                cert=old.certify(Ki,a,xi,eta);end=time.perf_counter()
                if rep:elapsed.append(end-start);audit.append(end-mid)
            rows.append({'problem':pid,'d':d,'method':method,'setup_seconds':setup,
                         'end_to_end_seconds':elapsed,'audit_seconds':audit,'repetitions':15,
                         'median':float(np.median(elapsed)),'q10':float(np.quantile(elapsed,.1)),
                         'q90':float(np.quantile(elapsed,.9)),'bound_per_service':cert['loss_bound_per_service']})
            records.append({'problem':pid,'method':method,'certificate':cert})
    (R/'cached_quadratic_problems.json').write_text(json.dumps(data,indent=2)+'\n')
    (R/'cached_quadratic_records.json').write_text(json.dumps(records,indent=2)+'\n')
    (R/'cached_quadratic_timing.json').write_text(json.dumps(rows,indent=2)+'\n')
    labels={'fresh_sparse':'Sparse, fresh','cached_sparse':'Sparse, cached','cached_dense':'Dense, cached',
            'jacobi_pcg':'Jacobi--PCG','analytic_filter':'Analytic filter','learned_gradient':'Learned gradient'}
    body=[]
    for d in [64,256,1024]:
        for method in labels:
            sub=[r for r in rows if r['d']==d and r['method']==method]
            body.append(f"{d} & {labels[method]} & {1000*np.mean([r['setup_seconds'] for r in sub]):.2f} & {1000*np.mean([r['median'] for r in sub]):.2f} & {max(r['bound_per_service'] for r in sub):.3g} \\\\")
    (T/'cached_quadratic.tex').write_text(r'''\begin{table}[p]\centering\small
\caption{R10 re-audit of the unchanged quadratic portfolio task. End-to-end time includes multiplier calibration, rational repair, and exact audit. Setup is paid once per graph; four graph-specific medians are averaged, each using 15 repetitions after one warmup. The learned coefficients use the prespecified first training seed. Accuracy is not matched.}\label{tab:r10-cached}
\begin{tabular}{rlrrr}\toprule
Services & Method & Setup (ms) & End-to-end (ms) & Max. bound/service\\\midrule
'''+ '\n'.join(body)+r'''
\bottomrule\end{tabular}\end{table}
''')
    print('Cached quadratic audit complete:',len(records),'decisions')
if __name__=='__main__':run()
