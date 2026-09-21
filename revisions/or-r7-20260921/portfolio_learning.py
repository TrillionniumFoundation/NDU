#!/usr/bin/env python3
"""Equal-oracle learned quadratic critics for coupled accepted service portfolios.
A degree-12 graph-filter network has a learned linear readout. Its scalar value
and gradient are compatible by construction. Coefficients are fitted, not set to
an analytic inverse. The Chebyshev inverse and sparse/direct/CG solvers are baselines.
Every deployed vector is rounded to rational tiers and certified in exact arithmetic.
"""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction as F
import json,time,platform,sys
import numpy as np
import scipy
from scipy.sparse import csr_matrix, eye, diags, coo_matrix
from scipy.sparse.linalg import spsolve, splu, cg
from scipy.linalg import cho_factor,cho_solve
HERE=Path(__file__).resolve().parent;OUT=HERE/'results';OUT.mkdir(exist_ok=True)
DEG=12;MU=2.1;HI=26.1;CENTER=(MU+HI)/2;RADIUS=(HI-MU)/2;Q=10**10

def graph(d,rng,gamma=None):
 # Cycle plus a random perfect matching: maximum degree at most three.
 edges={(i,(i+1)%d) for i in range(d)};perm=rng.permutation(d)
 edges|={tuple(sorted((int(perm[i]),int(perm[i+1])))) for i in range(0,d,2)}
 edges={tuple(sorted(e)) for e in edges if e[0]!=e[1]};rr=[];cc=[]
 for i,j in edges:rr.extend([i,j]);cc.extend([j,i])
 G=coo_matrix((np.ones(len(rr),dtype=np.int64),(rr,cc)),shape=(d,d)).tocsr();deg=np.asarray(G.sum(1)).ravel();L=diags(deg,dtype=np.int64)-G
 gamma=int(rng.integers(1,5)) if gamma is None else gamma
 Ki=(21*eye(d,format='csr',dtype=np.int64)+10*gamma*L).astype(np.int64).tocsr();K=Ki.astype(float)/10
 return Ki,K,int(gamma),int(len(edges))

def features(K,b,degree=DEG):
 # Each layer is sparse graph message passing; the scalar readout is quadratic.
 z0=b.copy();cols=[float(b@z0)/4];z1=(K@z0-CENTER*z0)/RADIUS
 if degree:cols.append(float(b@z1)/4)
 for k in range(2,degree+1):
  z2=2*(K@z1-CENTER*z1)/RADIUS-z0;cols.append(float(b@z2)/4);z0,z1=z1,z2
 return np.array(cols)

def apply(K,b,c):
 z0=b.copy();out=c[0]*z0
 if len(c)>1:
  z1=(K@z0-CENTER*z0)/RADIUS;out=out+c[1]*z1
  for k in range(2,len(c)):
   z2=2*(K@z1-CENTER*z1)/RADIUS-z0;out+=c[k]*z2;z0,z1=z1,z2
 return out

def train(seed,mode,graphs=96,h=.025):
 rng=np.random.default_rng(seed);X=[];y=[];DX=[];dy=[];start=time.perf_counter()
 for _ in range(graphs):
  d=int(rng.choice([32,64]));Ki,K,g,e=graph(d,rng);a=rng.integers(36,317,d)/100.;q=rng.uniform(.35,.65,d);u=rng.choice([-1.,1.],d);b=(1-.2)*a+1.2*q
  # The exact same three scalar oracle calls feed both methods.
  xx=[];yy=[]
  factor=splu(K.tocsc())
  for sign in [-1,0,1]:
   bs=b+sign*1.2*h*u;x=features(K,bs);v=float(bs@factor.solve(bs))/4
   xx.append(x);yy.append(v);X.append(x/d);y.append(v/d)
  DX.append((xx[2]-xx[0])/(2*h*np.sqrt(d)));dy.append((yy[2]-yy[0])/(2*h*np.sqrt(d)))
 X=np.array(X);y=np.array(y);DX=np.array(DX);dy=np.array(dy)
 if mode=='value_gradient':X=np.vstack([X,DX]);y=np.r_[y,dy]
 c,res,rank,sv=np.linalg.lstsq(X,y,rcond=1e-12)
 return c,dict(seed=seed,mode=mode,training_graphs=graphs,raw_scalar_oracle_calls=3*graphs,additional_raw_information=0,fd_step=h,degree=DEG,readout_parameters=DEG+1,training_seconds=time.perf_counter()-start,design_rank=int(rank),condition=float(sv[0]/sv[-1]),training_rmse=float(np.sqrt(np.mean((X@c-y)**2))),coefficients=c.tolist())

def chebyshev():
 s=np.sqrt(CENTER**2-RADIUS**2);rho=(CENTER-s)/RADIUS
 return np.array([1/s]+[2*(-rho)**k/s for k in range(1,DEG+1)])

def static_terms(aI):
 d=len(aI);As=int(aI.sum());theta=F(As+60*d,420*d);cap=F(As,100)*theta
 C=sum((F(103+30*(i%3),100) for i in range(d)),F(0))
 value=F(As,100)*theta-F(3*d,2)*theta**2-F(3*d,5)*(theta-F(1,2))**2-C
 return theta,cap,C,value

def calibrate(K,aI,solve):
 a=aI/100.;d=len(a);theta,cap,C,vs=static_terms(aI)
 # Evaluate two directions in a single batch where the solver supports it.
 B=np.stack([a+.6,a],axis=1);Y=solve(B);pb,pa=Y[:,0],Y[:,1]
 denominator=float(a@pa)
 if denominator<=0:raise ValueError('nonpositive learned acceptance slope')
 eta=max(0.,(float(a@pb)-2*float(cap))/denominator)
 x=.5*(pb-eta*pa);clipped=int(np.count_nonzero((x<0)|(x>1)));x=np.clip(x,0,1)
 # Exact feasibility is checked AFTER decimal deployment rounding.
 xI=np.floor(x*Q).astype(np.int64);pay=F(sum(int(ai)*int(xi) for ai,xi in zip(aI,xI)),100*Q)
 if pay>cap:
  correction=(pay-cap)/F(int(aI.sum()),100);steps=(correction.numerator*Q+correction.denominator-1)//correction.denominator
  xI=np.maximum(0,xI-int(steps))
 return xI,int(round(eta*Q)),clipped

def certify(Ki,aI,xI,etaI):
 """Exact rational, not a floating residual scan, for the rounded deployment."""
 d=len(aI);ts,cap,C,vstatic=static_terms(aI);assert xI.min()>=0 and xI.max()<=Q and etaI>=0
 pay=F(sum(int(ai)*int(xi) for ai,xi in zip(aI,xI)),100*Q);slack=cap-pay;assert slack>=0
 # Check the M-matrix and arithmetic envelope BEFORE int64 multiplication.
 assert (Ki-Ki.T).nnz==0
 assert np.all(np.asarray(Ki.sum(axis=1)).ravel()==21)
 off=Ki-diags(Ki.diagonal(),format='csr')
 assert np.all(off.data<=0)
 assert Q*int(np.asarray(abs(Ki).sum(axis=1)).max())<2**62
 kx=Ki@xI
 assert max(abs(int(v)) for v in kx)<2**62
 linear=F(sum((int(ai)+60)*int(xi) for ai,xi in zip(aI,xI)),100*Q)
 quadratic=F(sum(int(xi)*int(ki) for xi,ki in zip(xI,kx)),10*Q*Q)
 value=linear-quadratic-F(3*d,20)-C
 rn=[(Q-etaI)*int(ai)+60*Q-20*int(k) for ai,k in zip(aI,kx)]
 residual2=F(sum(r*r for r in rn),(100*Q)**2);eta=F(etaI,Q)
 bound=residual2*F(5,42)+eta*slack # 1/(4*mu), mu=21/10.
 return dict(tier_numerators=[int(v) for v in xI],tier_denominator=Q,dual_numerator=int(etaI),dual_denominator=Q,value=float(value),static_value=float(vstatic),gain=float(value-vstatic),gain_per_service=float((value-vstatic)/d),loss_bound=float(bound),loss_bound_per_service=float(bound/d),customer_slack=float(slack),tier_min=float(xI.min()/Q),tier_max=float(xI.max()/Q),eta=float(eta),exact_feasibility=True,exact_loss_bound_fraction=str(bound),exact_value_fraction=str(value),exact_gain_fraction=str(value-vstatic),exact_customer_slack_fraction=str(slack))

def runtime(solve,K,aI,repeats=3):
 times=[];result=None
 for _ in range(repeats):
  t=time.perf_counter();result=calibrate(K,aI,solve);times.append(time.perf_counter()-t)
 return result,float(np.median(times))

def main():
 coeff={};trainrows=[]
 for seed in range(101,111):
  for mode in ['value_only_equal_oracle','value_gradient']:
   c,meta=train(seed,mode);coeff[(seed,mode)]=c;trainrows.append(meta)
 (OUT/'portfolio_training.json').write_text(json.dumps(trainrows,indent=2)+'\n')
 rng=np.random.default_rng(9091);test=[];datasets=[]
 for d in [64,256,1024]:
  for rep in range(4):
   Ki,K,g,edges=graph(d,rng,gamma=rep+1);aI=rng.integers(36,317,d,dtype=np.int64)
   datasets.append(dict(d=d,rep=rep,gamma=g,a_integers=aI.tolist(),K_indptr=Ki.indptr.tolist(),K_indices=Ki.indices.tolist(),K_numerators=Ki.data.tolist(),K_denominator=10))
   methods=[(seed,mode,(lambda B,c=c:apply(K,B,c))) for (seed,mode),c in coeff.items()]
   methods.append((0,'chebyshev_degree12',lambda B:apply(K,B,chebyshev())))
   def sparse(B):return spsolve(K,B)
   def conjugate(B):
    columns=[]
    for j in range(B.shape[1]):
     x,info=cg(K,B[:,j],rtol=1e-4,atol=0,maxiter=4*d)
     if info!=0:raise RuntimeError(f'CG failed with status {info}')
     columns.append(x)
    return np.column_stack(columns)
   methods.extend([(0,'sparse_direct',sparse),(0,'cg_rtol1e-4',conjugate)])
   if d<=1024:
    def dense(B):return cho_solve(cho_factor(K.toarray(),lower=True,check_finite=False),B,check_finite=False)
    methods.append((0,'dense_cholesky',dense))
   optimum=None
   for seed,mode,solve in methods:
    (xI,etaI,clipped),secs=runtime(solve,K,aI);cer=certify(Ki,aI,xI,etaI)
    row=dict(d=d,rep=rep,gamma=g,seed=seed,method=mode,edges=edges,solve_seconds=secs,clipped_coordinates=clipped,**cer)
    test.append(row)
    if mode=='sparse_direct':optimum=cer
   for row in test:
    if row['d']==d and row['rep']==rep:
     row['numerical_loss_against_direct']=optimum['value']-row['value'];row['numerical_loss_per_service']=row['numerical_loss_against_direct']/d
     assert row['numerical_loss_against_direct']<=row['loss_bound']+optimum['loss_bound']+1e-8
   print('completed',d,rep,flush=True)
   (OUT/'portfolio_deployments.json').write_text(json.dumps(test,indent=2)+'\n')
 (OUT/'portfolio_test_graphs.json').write_text(json.dumps(datasets,separators=(',',':'))+'\n')
 # Separate held-out derivative-step sensitivity; no selection of the best seed.
 sensitivity=[]
 for h in [.01,.05,.1]:
  c,meta=train(101,'value_gradient',h=h)
  sensitivity.append(meta)
 (OUT/'portfolio_fd_sensitivity.json').write_text(json.dumps(sensitivity,indent=2)+'\n')
 summary=[]
 for d in [64,256,1024]:
  for mode in sorted({r['method'] for r in test}):
   rr=[r for r in test if r['d']==d and r['method']==mode]
   summary.append(dict(d=d,method=mode,n=len(rr),mean_loss_per_service=float(np.mean([r['numerical_loss_per_service'] for r in rr])),max_bound_per_service=max(r['loss_bound_per_service'] for r in rr),median_seconds=float(np.median([r['solve_seconds'] for r in rr])),minimum_gain_per_service=min(r['gain_per_service'] for r in rr),all_feasible=all(r['exact_feasibility'] for r in rr)))
 (OUT/'portfolio_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 (OUT/'portfolio_environment.json').write_text(json.dumps(dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__,platform=platform.platform(),threads='BLAS/OMP 1 requested',timing='median of three complete two-RHS solve plus acceptance calibration calls; excludes graph construction, offline training and rational audit',arithmetic='training and solve float64; deployment tiers and dual quantized to denominator 10^10; independent certificate exact Python integers/Fraction',network='degree-12 sparse graph message-passing feature network with learned 13-coefficient quadratic scalar readout',spectral_range=[MU,HI]),indent=2)+'\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
