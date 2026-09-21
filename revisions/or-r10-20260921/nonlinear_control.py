#!/usr/bin/env python3
"""Multistage nonquadratic accepted service control.

Finite exogenous binary scenario trees, graph-coupled services, quartic
maintenance, inherited tiers, and participation at EVERY history. The learner
is a compatible nonlinear scalar potential, not an inverse polynomial. Both
fits see the same three scalar value observations per training instance.
Numerical proposals are independently certified using rational arithmetic.
No failed test is discarded. This is synthetic, not a calibrated field study.
"""
from __future__ import annotations
from fractions import Fraction as Q
from pathlib import Path
import argparse, json, time, sys, platform
import numpy as np
from scipy import sparse
from scipy.optimize import minimize, nnls
from scipy.sparse.linalg import splu, cg, LinearOperator

HERE=Path(__file__).resolve().parent
OUT=HERE/'results'; OUT.mkdir(exist_ok=True)
DEN=10**8


def graph(d: int, family: str, rng: np.random.Generator):
    edges={}
    def add(i,j,v=1):
        if i!=j: edges[tuple(sorted((int(i),int(j))))]=int(v)
    if family=='cycle':
        for i in range(d): add(i,(i+1)%d)
    elif family=='erdos':
        for i in range(d):
            for j in range(i):
                if rng.random()<min(.65,3/d): add(i,j)
    elif family=='geometric':
        points=rng.random((d,2))
        for i in range(d):
            for j in range(i):
                if np.linalg.norm(points[i]-points[j])<.55: add(i,j)
    elif family=='weighted_block':
        for i in range(d):
            for j in range(i):
                if rng.random() < (.7 if (i<d//2)==(j<d//2) else .12):
                    add(i,j,int(rng.integers(1,5)))
    else: raise ValueError(family)
    # Connectivity is not needed: the maintenance term provides coercivity.
    return [(i,j,v) for (i,j),v in sorted(edges.items())]


class Problem:
    def __init__(self,d=4,depth=3,family='cycle',seed=0,gamma=1,zeta=Q(1,4)):
        self.d=d; self.depth=depth; self.family=family
        self.m=Q(3,2); self.lam=Q(3,5); self.gamma=Q(gamma); self.zeta=Q(zeta)
        self.bar=Q(1,2); self.beta=Q(9,10)
        self.nodes=2**depth-1; self.N=self.nodes*d
        self.pa=[-1]+[(n-1)//2 for n in range(1,self.nodes)]
        self.wn=[self.beta**((n+1).bit_length()-1)/2**((n+1).bit_length()-1) for n in range(self.nodes)]
        self.wq=[w for w in self.wn for _ in range(d)]
        self.w=np.array([float(v) for v in self.wq]);self.sw=np.sqrt(self.w)
        rng=np.random.default_rng(seed); self.edges=graph(d,family,rng)
        # Public net-payment tariff; resource shocks affect the provider only.
        self.aq=[Q(4+(j%3),4) for n in range(self.nodes) for j in range(d)]
        self.a=np.array([float(v) for v in self.aq])
        shocks=[Q(int(v),100) for v in rng.integers(-90,91,self.N)]
        avg=sum((w*v for w,v in zip(self.wq,shocks)),Q(0))/sum(self.wq)
        # Ensures that 1/2 is the EXACT reoptimized constant tier, not a weak
        # fixed benchmark. Initial installation is also 1/2.
        self.pq=[self.m+self.gamma/2+v-avg for v in shocks]
        self.p=np.array([float(v) for v in self.pq])
        self.rq=[v-a for v,a in zip(self.pq,self.aq)]
        self.mass=float(sum(self.wq))
        rr=[];cc=[];vv=[]
        diag=2*float(self.m)*self.w
        self.c=np.zeros(self.N)
        def edge(i,j,v):
            diag[i]+=2*v;diag[j]+=2*v
            rr.extend([i,j]);cc.extend([j,i]);vv.extend([-2*v,-2*v])
        for n in range(self.nodes):
            for j in range(d):
                i=n*d+j
                if n==0:
                    diag[i]+=2*float(self.lam)*self.w[i]
                    self.c[i]=2*float(self.lam)*self.w[i]*float(self.bar)
                else: edge(i,self.pa[n]*d+j,float(self.lam)*self.w[i])
            for i,j,v in self.edges: edge(n*d+i,n*d+j,float(self.zeta)*float(self.wn[n])*v)
        rr.extend(range(self.N));cc.extend(range(self.N));vv.extend(diag)
        self.H=sparse.coo_matrix((vv,(rr,cc)),shape=(self.N,self.N)).tocsc()
        # Every row is the unconditional expected payment on one subtree.
        rows=[];cols=[];vals=[]
        for n in range(self.nodes):
            anc=n
            while anc>=0:
                for j in range(d):
                    i=n*d+j;rows.append(anc);cols.append(i);vals.append(self.w[i]*self.a[i])
                anc=self.pa[anc]
        self.A=sparse.coo_matrix((vals,(rows,cols)),shape=(self.nodes,self.N)).tocsr()
        self.cap=np.asarray(self.A@np.full(self.N,.5))
        self.row_scale=np.asarray(self.A@np.ones(self.N))
        self.C=sparse.diags(1/self.row_scale)@self.A
        self.b=self.cap/self.row_scale
        self.ystar=None
        # A fixed shifted Hessian may be factorized ONCE for repeated queries.
        t=time.perf_counter()
        self.base_factor=splu(self.H+sparse.diags(3*float(self.gamma)*self.w))
        self.setup_seconds=time.perf_counter()-t
        self.preconditioner=LinearOperator((self.N,self.N),matvec=self.base_factor.solve)
        # Weighted-self-adjoint local diffusion filters for the neural potential.
        off=self.H-sparse.diags(self.H.diagonal())
        deg=np.asarray(abs(off).sum(axis=1)).ravel()
        lap=sparse.diags(deg)+off
        radius=max(np.max(deg/self.w),1.)
        smooth=sparse.eye(self.N,format='csr')-sparse.diags(1/self.w)@lap/(2*radius)
        self.filters=[sparse.eye(self.N,format='csr'),smooth.tocsr(),(smooth@smooth).tocsr()]
        self.gbar=self.grad(np.full(self.N,.5))/self.w

    def F(self,x):
        # Fixed resource offset 10 per service-review is omitted from all
        # values: it cancels from every comparison and every derivative.
        # Linear operating offset r*x has been collected in p=a+r.
        return float(.5*x@(self.H@x)-self.c@x+float(self.gamma)*np.dot(self.w,x**4)
                     +float(self.lam)*self.d*.25)
    def grad(self,x): return self.H@x-self.c+4*float(self.gamma)*self.w*x**3
    def value(self,x,p=None):
        p=self.p if p is None else p
        return float(np.dot(self.w*p,x)-self.F(x))

    def inner(self,rhs,x=None,linear='fresh'):
        x=np.full(self.N,.5) if x is None else x.copy()
        for it in range(60):
            g=self.grad(x)-rhs
            if np.max(abs(g)/self.w)<2e-11: break
            K=self.H+sparse.diags(12*float(self.gamma)*self.w*x*x)
            if linear=='cached_pcg':
                step,info=cg(K,-g,M=self.preconditioner,rtol=1e-11,atol=1e-13,maxiter=5*self.N)
                if info: raise RuntimeError('PCG failed')
            else: step=splu(K.tocsc()).solve(-g)
            before=self.F(x)-rhs@x;s=1.
            for _ in range(40):
                y=x+s*step
                if self.F(y)-rhs@y <= before+1e-4*s*(g@step)+1e-13: break
                s*=.5
            x=y
        return x

    def solve(self,p=None,linear='fresh',eta0=None):
        p=self.p if p is None else p
        last=np.full(self.N,.5)
        def dual(ell):
            nonlocal last
            last=self.inner(self.w*p-self.C.T@ell,last,linear)
            return float(self.value(last,p)+ell@(self.b-self.C@last)), self.b-self.C@last
        res=minimize(dual,np.zeros(self.nodes) if eta0 is None else eta0,
            jac=True,method='L-BFGS-B',bounds=[(0,None)]*self.nodes,
            options={'maxiter':1500,'ftol':1e-14,'gtol':2e-9,'maxls':40,'maxcor':20})
        ell=np.maximum(res.x,0);x=self.inner(self.w*p-self.C.T@ell,last,linear)
        if x.min() < -1e-7 or x.max()>1+1e-7:
            raise RuntimeError('Interior dual proposal left the tier box; test must be recorded as failure')
        return x,ell/self.row_scale,{'iterations':int(res.nit),'success':bool(res.success)}

    def features(self,p,direction=None):
        """Sixty-three nonlinear softplus hidden units; linear trainable readout.
        Return scalar features, optional directional gradients, and tier basis.
        Finite-feature architecture is common to both loss functions.
        """
        e=p-self.gbar;features=[];ders=[];tiercols=[]
        for S in self.filters:
            z=np.asarray(S@e)
            su=None if direction is None else np.asarray(S@direction)
            for scale in (.6,1.5,3.):
                for shift in (-1.5,-1.,-.5,0.,.5,1.,1.5):
                    u=scale*z+shift
                    f=np.logaddexp(0,u)/scale
                    sig=1/(1+np.exp(-np.clip(u,-60,60)))
                    features.append(np.dot(self.w,f)/self.mass)
                    tiercols.append(np.asarray(S.T@(self.w*sig))/self.w)
                    if direction is not None:ders.append(np.dot(self.w*sig,su)/self.mass)
        return np.array(features),np.array(ders),np.asarray(tiercols).T

    def certificate(self,proposal,eta=None,verify_static=True):
        """Feasibility repair and exact rational nonlinear residual certificate.
        Uses the actual polynomial resource objective, no solver status.
        """
        begin=time.perf_counter()
        xx=np.clip(np.asarray(proposal),0,1)
        x=[Q(int(np.floor(v*DEN)),DEN) for v in xx]
        def payments(x):
            v=[sum((self.wq[n*self.d+j]*self.aq[n*self.d+j]*x[n*self.d+j] for j in range(self.d)),Q(0)) for n in range(self.nodes)]
            cap=[sum((self.wq[n*self.d+j]*self.aq[n*self.d+j]/2 for j in range(self.d)),Q(0)) for n in range(self.nodes)]
            for n in reversed(range(1,self.nodes)):
                v[self.pa[n]]+=v[n];cap[self.pa[n]]+=cap[n]
            return v,cap
        pay,cap=payments(x)
        scale=min([Q(1)]+[c/v for c,v in zip(cap,pay) if v>0])
        x=[Q((v*scale*DEN).numerator//(v*scale*DEN).denominator,DEN) for v in x]
        pay,cap=payments(x)
        xf=np.array([float(v) for v in x])
        if eta is None:
            # Nonnegative least squares is a proposal, NOT a proof. All dual
            # entries are rounded and every residual is recomputed below.
            B=(self.A@sparse.diags(1/self.sw)).T.toarray()
            eta=nnls(B,(self.w*self.p-self.grad(xf))/self.sw,maxiter=20*self.nodes)[0]
        ell=[Q(max(0,int(round(float(v)*DEN))),DEN) for v in eta]
        accum=[]
        for n in range(self.nodes):accum.append(ell[n]+(accum[self.pa[n]] if self.pa[n]>=0 else 0))
        residual=[self.wq[i]*(self.pq[i]-2*self.m*x[i]-4*self.gamma*x[i]**3-self.aq[i]*accum[i//self.d]) for i in range(self.N)]
        def val(tiers):
            out=Q(0)
            for n in range(self.nodes):
                for j in range(self.d):
                    i=n*self.d+j;parent=self.bar if n==0 else tiers[self.pa[n]*self.d+j]
                    out+=self.wq[i]*(self.pq[i]*tiers[i]-self.m*tiers[i]**2-self.gamma*tiers[i]**4-self.lam*(tiers[i]-parent)**2)
                for j,k,v in self.edges:out-=self.wn[n]*self.zeta*v*(tiers[n*self.d+j]-tiers[n*self.d+k])**2
            return out
        for n in range(self.nodes):
            for j in range(self.d):
                i=n*self.d+j;parent=self.bar if n==0 else x[self.pa[n]*self.d+j]
                term=2*self.lam*self.wq[i]*(x[i]-parent)
                residual[i]-=term
                if n: residual[self.pa[n]*self.d+j]+=term
            for j,k,v in self.edges:
                i=n*self.d+j;l=n*self.d+k
                term=2*self.wn[n]*self.zeta*v*(x[i]-x[l]);residual[i]-=term;residual[l]+=term
        slack=[c-v for c,v in zip(cap,pay)]
        assert min(slack)>=0 and all(0<=v<=1 for v in x)
        bound=sum((r*r/(4*self.m*w) for r,w in zip(residual,self.wq)),Q(0))+sum((v*s for v,s in zip(ell,slack)),Q(0))
        value=val(x);static=val([self.bar]*self.N)
        # This derivative is EXACTLY zero for the optimized static comparator.
        if verify_static:
            assert sum((w*(p-2*self.m*self.bar-4*self.gamma*self.bar**3) for w,p in zip(self.wq,self.pq)),Q(0))==0
        return {'value':float(value),'gain_over_static':float(value-static),'upper_gap':float(bound),
                'gap_per_service_review':float(bound)/self.mass,'scale':float(scale),
                'certificate_seconds':time.perf_counter()-begin,
                'value_fraction':str(value),'static_fraction':str(static),'bound_fraction':str(bound),
                'policy':[str(v) for v in x],'multipliers':[str(v) for v in ell],
                'minimum_slack_fraction':str(min(slack)),'feasible':True}

    def record(self):
        return {'d':self.d,'depth':self.depth,'family':self.family,'m':str(self.m),
                'lambda':str(self.lam),'gamma':str(self.gamma),'zeta':str(self.zeta),
                'weights':[str(v) for v in self.wq],'tariffs':[str(v) for v in self.aq],
                'forcing':[str(v) for v in self.pq],'edges':self.edges,'parents':self.pa}


def train(seed,instances=24,h=.025):
    if h != .025: raise ValueError("This frozen design uses exactly h=1/40")
    rng=np.random.default_rng(seed)
    X=[];Y=[];DX=[];DY=[];teacher=[]
    started=time.perf_counter()
    for k in range(instances):
        pr=Problem(d=4,depth=3,family='cycle',seed=seed*1000+k,gamma=1)
        direction=rng.choice([-1.,1.],pr.N)
        vals=[];certified_teacher=[]
        central_p=pr.p.copy();central_pq=pr.pq.copy()
        central_problem=pr.record()
        for sign in (-1,0,1):
            # Oracle endpoints change the reward forcing, not the contract.
            # Each value label is feasible with an exact upper error bar.
            pr.pq=[v+sign*Q(1,40)*int(u) for v,u in zip(central_pq,direction)]
            pr.p=np.array([float(v) for v in pr.pq])
            x,ell,status=pr.solve()
            cert=pr.certificate(x,ell,verify_static=(sign==0))
            v=cert['value'];fv,_,_=pr.features(pr.p)
            baseline=float(Q(cert['static_fraction']))
            X.append(fv);Y.append((v-baseline)/pr.mass);vals.append((v-baseline)/pr.mass)
            certified_teacher.append({'sign':sign,'certificate':cert,'solver':status})
        pr.p=central_p;pr.pq=central_pq
        _,df,_=pr.features(pr.p,direction)
        DX.append(df);DY.append((vals[2]-vals[0])/(2*h))
        teacher.append({'problem':central_problem,'direction':direction.astype(int).tolist(),
            'residual_values':vals,'certified_oracle_records':certified_teacher,
            'directional_error_bound':h/(4*float(pr.m))+
                (certified_teacher[0]['certificate']['upper_gap']+
                 certified_teacher[2]['certificate']['upper_gap'])/(2*h*pr.mass)})
    X=np.asarray(X);Y=np.asarray(Y);DX=np.asarray(DX);DY=np.asarray(DY)
    # Standardization and ridge are fixed for both methods. No test tuning.
    scale=np.sqrt(np.mean(X*X,axis=0)+np.mean(DX*DX,axis=0)+1e-8)
    def fit(weight):
        A=np.vstack([X/scale,weight*DX/scale,np.sqrt(1e-5)*np.eye(X.shape[1])])
        b=np.r_[Y,weight*DY,np.zeros(X.shape[1])]
        return np.linalg.lstsq(A,b,rcond=None)[0]/scale
    cv=fit(0);cgfit=fit(1)
    return {'value':cv,'gradient':cgfit}, {'seed':seed,'teacher_instances':instances,
        'raw_scalar_queries':3*instances,'h':h,'seconds':time.perf_counter()-started,
        'coefficients':{'value':cv.tolist(),'gradient':cgfit.tolist()},'teacher_records':teacher}


def run(seeds=10,instances=24,repetitions=15):
    start=time.perf_counter();fits=[];trainrecords=[]
    for s in range(seeds):
        fit,rec=train(12000+s,instances);fits.append(fit);trainrecords.append(rec)
        print('trained',s,rec['seconds'],flush=True)
    tests=[];records=[];timing=[]
    cases=[('cycle',4,3,1,Q(1,4)),('erdos',8,3,1,Q(1,4)),
           ('geometric',8,4,2,Q(1,2)),('weighted_block',32,5,3,Q(1))]
    for fam,d,depth,gamma,zeta in cases:
        for testseed in (33001,33002):
            pr=Problem(d,depth,fam,testseed,gamma,zeta);pid=f'{fam}-{d}-{depth}-{testseed}'
            # Fresh factorization and reused-factor PCG solve THE SAME
            # nonquadratic multistage problem; setup is reported separately.
            sols={}
            for method in ('fresh','cached_pcg'):
                elapsed=[];certtimes=[]
                for k in range(repetitions+1):
                    t=time.perf_counter();x,eta,status=pr.solve(linear=method)
                    ct=pr.certificate(x,eta);total=time.perf_counter()-t
                    if k:elapsed.append(total);certtimes.append(ct['certificate_seconds'])
                sols[method]=ct
                timing.append({'problem':pid,'method':method,'setup_seconds':pr.setup_seconds,
                    'repetitions':repetitions,'end_to_end_seconds':elapsed,
                    'certificate_seconds':certtimes,'median_end_to_end':float(np.median(elapsed)),
                    'q10':float(np.quantile(elapsed,.1)),'q90':float(np.quantile(elapsed,.9)),
                    'upper_gap':ct['upper_gap'],'solver':status})
                records.append({'problem':pid,'seed':None,'method':method,'certificate':ct})
            tests.append({'id':pid,**pr.record(),'mass':pr.mass,'N':pr.N})
            for seedidx,fit in enumerate(fits):
                for method,c in fit.items():
                    repeats=[]
                    actual_reps=repetitions if seedidx==0 else 1
                    for k in range(actual_reps+1):
                        t=time.perf_counter();_,_,basis=pr.features(pr.p)
                        proposal=.5+basis@c
                        ct=pr.certificate(proposal)
                        total=time.perf_counter()-t
                        if k:repeats.append(total)
                    records.append({'problem':pid,'seed':seedidx,'method':method,'certificate':ct,
                        'timing_repetitions':actual_reps,'end_to_end_seconds':repeats,
                        'median_end_to_end':float(np.median(repeats)),
                        'q10':float(np.quantile(repeats,.1)),'q90':float(np.quantile(repeats,.9))})
            print('tested',pid,pr.N,flush=True)
    # Paired training-seed means, NOT treating graphs as independent seeds.
    differences=[]
    for seed in range(seeds):
        vv=[r['certificate']['value']/next(t['mass'] for t in tests if t['id']==r['problem']) for r in records if r['seed']==seed and r['method']=='value']
        gg=[r['certificate']['value']/next(t['mass'] for t in tests if t['id']==r['problem']) for r in records if r['seed']==seed and r['method']=='gradient']
        differences.append(float(np.mean(gg)-np.mean(vv)))
    from scipy.stats import t as student
    mean=float(np.mean(differences));half=float(student.ppf(.975,seeds-1)*np.std(differences,ddof=1)/np.sqrt(seeds)) if seeds>1 else float('nan')
    summary={'scope':'synthetic multistage quartic service control with history-specific continuation participation',
        'seeds':seeds,'training_instances_per_seed':instances,'queries_per_seed':3*instances,
        'test_instances':len(tests),'max_coordinates':max(t['N'] for t in tests),
        'paired_seed_improvement':differences,'mean_improvement_per_service_review':mean,
        'student_95_interval':[mean-half,mean+half],'all_exactly_feasible':all(r['certificate']['feasible'] for r in records),
        'deployment_records':len(records),'seconds':time.perf_counter()-start,
        'environment':{'python':sys.version,'numpy':np.__version__,'platform':platform.platform()},
        'warning':'No speed superiority or distribution-free learning guarantee is assumed. Exact residual bounds certify submitted decisions, not statistical generalization.'}
    for name,obj in [('nonlinear_training',trainrecords),('nonlinear_problems',tests),('nonlinear_records',records),('nonlinear_timing',timing),('nonlinear_summary',summary)]:
        (OUT/(name+'.json')).write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--seeds',type=int,default=10);ap.add_argument('--instances',type=int,default=24);ap.add_argument('--repetitions',type=int,default=15)
    args=ap.parse_args();run(args.seeds,args.instances,args.repetitions)
