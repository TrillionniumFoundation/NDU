#!/usr/bin/env python3
"""Full-tree friction paths and sparse continuation-flow computation."""
from experiment import *

def primitives(tr):
    return {'parent':tr.pa.tolist(),'weights':list(map(str,tr.wq)),'tariffs':list(map(str,tr.cq)),
            'forcing':[list(map(str,row)) for row in tr.gq], 'outside':'1/2','maintenance':'1','smooth_switching':'1/10'}

def paths():
    rows=[];models={}
    for depth in (4,5,6):
        tr=Tree(depth);models[str(depth)]=primitives(tr)
        for context in ((-.8,.4),(.2,-.4),(.9,-.7)):
            th=np.array([*context,.01]);critical,lptime,nnz=tr.critical_lp(th)
            for frac in (0.,.1,.25,.5,.75,.9,1.,1.1,1.25):
                th=np.array([*context,round(frac*critical,9)]);u,secs,it,ok=tr.solve(th)
                try:
                    ce=tr.cell(th,u);uu,mu,ss=eval_cell(ce,th)
                except RuntimeError:
                    a,lam=tr.pars(th);lp=linprog(np.zeros(len(tr.L)+tr.N),A_eq=np.column_stack((tr.L.T,tr.K.T)),b_eq=a,
                           bounds=[(0,None)]*len(tr.L)+[(-lam*k,lam*k) for k in tr.k],method='highs')
                    if not lp.success:raise
                    uu=np.zeros(tr.m);mu=lp.x[:len(tr.L)];ss=lp.x[len(tr.L):]
                audit=tr.audit(th,uu,mu,ss)
                assert audit['bound']<1e-7, (depth,context,frac,audit['bound'], audit['quadratic'], audit['acceptance_leakage'], audit['switching_leakage'])
                rows.append({'depth':depth,'nodes':tr.N,'context':list(context),'lambda':float(th[2]),'critical':critical,'fraction':frac,
                    'qp_seconds':secs,'iterations':it,'optimizer_success':ok,'active_continuation':int(np.sum(np.abs(uu)<1e-6)),
                    'fused_edges':int(np.sum(np.abs(tr.K@uu)<1e-6)),'saturated_tensions':int(np.sum(np.abs(ss)>=float(th[2])*tr.k-1e-8)),
                    'switching_per_review':float(tr.k@np.abs(tr.K@uu)/tr.mass),'audit':audit})
    compress(HERE/'results/friction_paths.json.gz',{'models':models,'records':rows})
    for depth in (4,5,6):
        rr=[r for r in rows if r['depth']==depth]
        assert all(rr[i]['switching_per_review']>=rr[i+1]['switching_per_review']-1e-7 for i in range(len(rr)-1) if rr[i]['context']==rr[i+1]['context'])
    print('friction paths',len(rows),flush=True)

def sparse_instance(N,kind):
    pa=np.array([-1]+([(i-1)//2 for i in range(1,N)] if kind=='binary' else [0]*(N-1)))
    wq=[F(9,20)**int(np.floor(np.log2(i+1))) for i in range(N)] if kind=='binary' else [F(1)]+[F(9,10*(N-1))]*(N-1)
    cq=[w*F(8+(i%5),10) for i,w in enumerate(wq)];rng=np.random.default_rng(1301)
    raw=[F(int(v),20)*w for v,w in zip(rng.integers(-14,15,N),wq)];avg=sum(raw)/sum(wq);gq=[v-avg*w for v,w in zip(raw,wq)]
    c=np.array(list(map(float,cq)));k=np.array(list(map(float,wq)));g=np.array(list(map(float,gq)))
    B=sparse.coo_matrix((np.r_[-np.ones(N-1),c[1:]/c[pa[1:]]],(np.r_[np.arange(1,N),pa[1:]],np.r_[np.arange(N-1),np.arange(N-1)])),shape=(N,N-1)).tocsr()
    D=sparse.eye(N,format='csr')+sparse.coo_matrix((-np.ones(N-1),(np.arange(1,N),pa[1:])),shape=(N,N)).tocsr()
    return pa,wq,cq,gq,c,k,g,B,D

def exact_bracket(pa,kq,cq,gq,t,lam,direction):
    N=len(pa);Ff=lambda x:F(str(float(x)))
    la=Ff(lam);tt=[max(-la,min(la,Ff(v))) for v in t];s=[k*v for k,v in zip(kq,tt)]
    def bt(v):return [cq[i]/cq[pa[i]]*v[pa[i]]-v[i] for i in range(1,N)]
    v=s.copy()
    for i in range(1,N):v[pa[i]]-=s[i]
    a=bt(gq);b=bt(v);r=[max(F(0),x-y) for x,y in zip(a,b)];dv=[F(0)]*N
    for i in range(1,N):dv[i]=cq[i]/cq[pa[i]]*dv[pa[i]]-r[i-1]
    ds=dv.copy()
    for i in range(N-1,0,-1):ds[pa[i]]+=ds[i]
    ss=[x+y for x,y in zip(s,ds)];upper=max(abs(x)/k for x,k in zip(ss,kq))
    u=[max(F(0),Ff(v)) for v in direction];x=[F(0)]*N
    for i in range(1,N):x[i]-=u[i-1];x[pa[i]]+=cq[i]/cq[pa[i]]*u[i-1]
    den=sum(kq[i]*abs(x[i]-(x[pa[i]] if i else 0)) for i in range(N))
    lower=max(F(0),sum(v*z for v,z in zip(a,u))/den) if den else F(0)
    assert lower<=upper
    return {'lower_fraction':str(lower),'upper_fraction':str(upper),'lower':float(lower),'upper':float(upper),
            'direction':list(map(str,u)),'upper_tensions':list(map(str,ss))}

def sparse_run(N,kind,tol=1e-4,maxit=12000):
    pa,kq,cq,gq,c,k,g,B,D=sparse_instance(N,kind);a=B.T@g
    A=sparse.diags(1/c[1:])@B.T;C=D.T@sparse.diags(k);b=a/c[1:]
    norm1=lambda X:float(abs(X).sum(axis=0).max());norminf=lambda X:float(abs(X).sum(axis=1).max())
    # Exact absolute row/column sums without materializing A@C.
    degree=np.bincount(pa[1:],minlength=N);childweight=np.bincount(pa[1:],weights=k[1:],minlength=N)
    d=(k+childweight)/c;row_norm=float(np.max(d[pa[1:]]+d[1:]))
    col=np.zeros(N);col[0]=degree[0]*k[0]/c[0]
    for i in range(1,N):
        p=pa[i];col[i]=k[i]*((degree[i]+1)/c[i]+(degree[p]+int(p!=0))/c[p])
    col_norm=float(np.max(col));lip=col_norm*row_norm
    if N<=31:
        MM=A@C;assert abs(norm1(MM)-col_norm)<1e-10 and abs(norminf(MM)-row_norm)<1e-10
    def repair(t,lam):
        r=np.maximum(b-A@(C@t),0);v=np.zeros(N)
        for i in range(1,N):v[i]=c[i]/c[pa[i]]*v[pa[i]]-c[i]*r[i-1]
        ds=v.copy()
        for i in range(N-1,0,-1):ds[pa[i]]+=ds[i]
        hi=float(np.max(np.abs(k*t+ds)/k));u=r/c[1:];den=k@np.abs(D@(B@u));lo=max(0.,float(a@u/den)) if den>1e-18 else 0.
        return lo,hi,u
    lo,hi,d=repair(np.zeros(N),0.);bestt=np.zeros(N);bestlam=0.;bestd=d.copy();count=0;outer=0;st=time.perf_counter()
    while hi-lo>tol and count<maxit:
        lam=(lo+hi)/2;t=np.zeros(N);y=t.copy();acc=1.;outer+=1
        while count<maxit:
            r=np.maximum(b-A@(C@y),0);new=np.clip(y+C.T@(A.T@r)/lip,-lam,lam)
            nxt=(1+np.sqrt(1+4*acc*acc))/2;y=new+(acc-1)/nxt*(new-t);t=new;acc=nxt;count+=1
            if count%20==0:
                ll,hh,dd=repair(t,lam)
                if ll>lo:lo=ll;bestd=dd.copy()
                if hh<hi:hi=hh;bestt=t.copy();bestlam=lam
                if hi-lo<=tol or ll>lam+1e-12 or hh<lam+tol/4:break
    secs=time.perf_counter()-st;wit=exact_bracket(pa,kq,cq,gq,bestt,bestlam,bestd)
    obj=np.r_[np.zeros(2*N),1.]
    Ae=sparse.hstack((D.T,-sparse.eye(N),sparse.csr_matrix((N,1))))
    Au=sparse.vstack((sparse.hstack((sparse.csr_matrix((N-1,N)),-B.T,sparse.csr_matrix((N-1,1)))),
        sparse.hstack((sparse.eye(N),sparse.csr_matrix((N,N)),-sparse.csr_matrix(k[:,None]))),
        sparse.hstack((-sparse.eye(N),sparse.csr_matrix((N,N)),-sparse.csr_matrix(k[:,None])))))
    st=time.perf_counter();lp=linprog(obj,A_ub=Au,b_ub=np.r_[-a,np.zeros(2*N)],A_eq=Ae,b_eq=np.zeros(N),bounds=[(None,None)]*(2*N)+[(0,None)],method='highs');lpsec=time.perf_counter()-st
    assert lp.success and wit['lower']-1e-7<=lp.x[-1]<=wit['upper']+1e-7
    st=time.perf_counter();K=D@B;raw=sparse.vstack((sparse.hstack((-K.T,sparse.csr_matrix((N-1,1)))),sparse.hstack((sparse.eye(N),-sparse.csr_matrix(k[:,None]))),sparse.hstack((-sparse.eye(N),-sparse.csr_matrix(k[:,None])))))
    rlp=linprog(np.r_[np.zeros(N),1],A_ub=raw,b_ub=np.r_[-a,np.zeros(2*N)],bounds=[(None,None)]*N+[(0,None)],method='highs');rawsec=time.perf_counter()-st
    assert rlp.success and abs(rlp.x[-1]-lp.x[-1])<1e-7
    return {'nodes':N,'topology':kind,'critical_lp':float(lp.x[-1]),'factored_lp_seconds':lpsec,'materialized_lp_seconds':rawsec,
        'factored_nonzeros':int(Au.nnz+Ae.nnz),'materialized_nonzeros':int(raw.nnz),'first_order_seconds':secs,'iterations':count,
        'outer':outer,'attained':wit['upper']-wit['lower']<=tol+1e-12,'tolerance':tol,'certificate':wit,
        'primitives':{'parent':pa.tolist(),'weights':list(map(str,kq)),'tariffs':list(map(str,cq)),'gradient':list(map(str,gq))}}

def scale():
    rows=[]
    for kind in ('binary','star'):
        for N in (31,63,127,255,511,1023):
            rows.append(sparse_run(N,kind));r=rows[-1];print(kind,N,r['attained'],r['iterations'],r['first_order_seconds'],r['factored_lp_seconds'],flush=True)
    compress(HERE/'results/scaling.json.gz',{'records':rows})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['paths','scale']);a=p.parse_args()
    paths() if a.stage=='paths' else scale()
