#!/usr/bin/env python3
"""Floating spectral diagnostics; never substituted for rational coercivity."""
from pathlib import Path
from fractions import Fraction as Q
import json
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh
BASE=Path(__file__).resolve().parent;R=BASE/'results';T=BASE/'tables'

def diagnose(p):
    d=p['d'];pa=p['parents'];N=len(p['weights']);w=np.array([float(Q(v)) for v in p['weights']])
    m=float(Q(p['m']));gam=float(Q(p['gamma']));lam=float(Q(p['lambda']));zeta=float(Q(p['zeta']))
    K=sparse.lil_matrix((N,N));K.setdiag((2*m+3*gam)*w)
    def edge(i,j,v):K[i,i]+=v;K[j,j]+=v;K[i,j]-=v;K[j,i]-=v
    for n in range(len(pa)):
        for j in range(d):
            i=n*d+j
            if n:edge(i,pa[n]*d+j,2*lam*w[i])
            else:K[i,i]+=2*lam*w[i]
        for j,k,v in p['edges']:edge(n*d+j,n*d+k,2*zeta*w[n*d]*v)
    H=sparse.diags(1/np.sqrt(w))@K.tocsr()@sparse.diags(1/np.sqrt(w))
    if N<200:e=np.linalg.eigvalsh(H.toarray());lo=float(e[0]);hi=float(e[-1])
    else:lo=float(eigsh(H,k=1,which='SA',return_eigenvectors=False)[0]);hi=float(eigsh(H,k=1,which='LA',return_eigenvectors=False)[0])
    degree=np.zeros(d)
    for i,j,v in p['edges']:degree[i]+=v;degree[j]+=v
    return {'N':N,'depth':p['depth'],'family':p['family'],'weighted_hessian_min':lo,
            'weighted_hessian_max':hi,'max_weighted_spatial_degree':float(max(degree))}

data=json.loads((R/'nonlinear_problems.json').read_text())
train=json.loads((R/'nonlinear_training.json').read_text())[0]['teacher_records'][0]['problem']
out=[{'id':'training-template',**diagnose(train)}]+[{'id':p['id'],**diagnose(p)} for p in data]
(R/'operator_diagnostics.json').write_text(json.dumps(out,indent=2)+'\n')
body=[]
for r in out:body.append(f"{r['id'].replace('weighted_block','block').replace('geometric','geo')} & {r['N']} & {r['weighted_hessian_min']:.2f} & {r['weighted_hessian_max']:.2f} & {r['max_weighted_spatial_degree']:.0f} \\\\")
(T/'operator_diagnostics.tex').write_text(r'''\begin{table}[p]\centering\small
\caption{Measured spectrum of the discounted-weight-normalized Hessian at the static tier and maximum weighted spatial degree. These floating diagnostics expose distribution shift; exact certificates use the proved lower curvature bound instead.}\label{tab:r10-spectrum}
\begin{tabular}{lrrrr}\toprule
Instance & Coordinates & Minimum & Maximum & Weighted degree\\\midrule
'''+ '\n'.join(body)+r'''
\bottomrule\end{tabular}\end{table}
''')
print(json.dumps(out,indent=2))
