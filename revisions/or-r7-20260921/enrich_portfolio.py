#!/usr/bin/env python3
"""Reconstruct saved candidates, retaining original benchmark timing records."""
import json
from pathlib import Path
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import spsolve,cg
from scipy.linalg import cho_factor,cho_solve
import portfolio_learning as p
O=Path(__file__).resolve().parent/'results'
rows=json.loads((O/'portfolio_deployments.json').read_text())
models={(r['seed'],r['mode']):np.array(r['coefficients']) for r in json.loads((O/'portfolio_training.json').read_text())}
graphs=json.loads((O/'portfolio_test_graphs.json').read_text())
for g in graphs:
 d=g['d'];Ki=csr_matrix((np.array(g['K_numerators'],dtype=np.int64),g['K_indices'],g['K_indptr']),shape=(d,d));K=Ki.astype(float)/10;a=np.array(g['a_integers'],dtype=np.int64)
 for r in rows:
  if (r['d'],r['rep'])!=(d,g['rep']):continue
  mode=r['method']
  if (r['seed'],mode) in models:solve=lambda B,c=models[r['seed'],mode]:p.apply(K,B,c)
  elif mode=='chebyshev_degree12':solve=lambda B:p.apply(K,B,p.chebyshev())
  elif mode=='sparse_direct':solve=lambda B:spsolve(K,B)
  elif mode=='dense_cholesky':solve=lambda B:cho_solve(cho_factor(K.toarray(),lower=True,check_finite=False),B,check_finite=False)
  elif mode=='cg_rtol1e-4':
   def solve(B):
    cols=[]
    for j in range(B.shape[1]):
     v,status=cg(K,B[:,j],rtol=1e-4,atol=0,maxiter=4*d);assert status==0;cols.append(v)
    return np.column_stack(cols)
  else:raise ValueError(mode)
  x,e,_=p.calibrate(K,a,solve);cert=p.certify(Ki,a,x,e)
  assert cert['exact_value_fraction']==r['exact_value_fraction'],(d,mode)
  assert cert['exact_loss_bound_fraction']==r['exact_loss_bound_fraction']
  for k in ['tier_numerators','tier_denominator','dual_numerator','dual_denominator']:r[k]=cert[k]
(O/'portfolio_deployments.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
# All FD steps are evaluated on all four predesignated 1024-service test graphs.
sens=json.loads((O/'portfolio_fd_sensitivity.json').read_text())
for r in sens:
 rr=[];coeff=np.array(r['coefficients'])
 for g in graphs:
  if g['d']!=1024:continue
  d=g['d'];Ki=csr_matrix((np.array(g['K_numerators'],dtype=np.int64),g['K_indices'],g['K_indptr']),shape=(d,d));K=Ki.astype(float)/10;a=np.array(g['a_integers'],dtype=np.int64)
  x,e,_=p.calibrate(K,a,lambda B:p.apply(K,B,coeff));c=p.certify(Ki,a,x,e);rr.append({'rep':g['rep'],'maximum_bound_per_service':c['loss_bound_per_service'],'exact_bound_fraction':c['exact_loss_bound_fraction']})
 r['held_out_1024_graphs']=rr
(O/'portfolio_fd_sensitivity.json').write_text(json.dumps(sens,indent=2)+'\n')
print('Enriched',len(rows),'deployments; all exact values and bounds unchanged.')
