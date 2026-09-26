"""Single R60 experiment. Parent enforces total wall time including imports."""
from __future__ import annotations
import time
START=time.perf_counter()
from pathlib import Path
import gzip,hashlib,json,resource,signal,sys,traceback
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];OLD=ROOT/'revisions/or-r58-structural-referee-20260926/code';sys.path.insert(0,str(OLD))
from rational import F,write,encode,digest,canonical,qstr
from price_path import normalize,allocate,DeadlineExceeded,leaves

def scip_solve(spec,remaining,epsilon):
    from pyscipopt import Model,quicksum
    d,a,rho,B,m=normalize(spec);s=Model('NDU exact convex original formulation');s.hideOutput();s.setRealParam('limits/time',max(.001,remaining));s.setRealParam('limits/absgap',float(epsilon));s.setRealParam('limits/gap',0.0);s.setIntParam('parallel/maxnthreads',1)
    x=[s.addVar(vtype='B',name=f'x{i}') for i in range(len(a))]
    y=[s.addVar(lb=0,ub=float(b),name=f'y{j}') for j,b in enumerate(d.caps)]
    h=[s.addVar(lb=0,name=f'h{j}') for j in range(len(y))];ps={};zs={}
    for j in range(len(y)):
        eligible=[i for i,z in enumerate(a) if z<=d.ceilings[j]]
        for i in eligible:
            ps[j,i]=s.addVar(lb=0,ub=1,name=f'p{j}_{i}');zs[j,i]=s.addVar(vtype='B',name=f'z{j}_{i}')
            s.addCons(ps[j,i]<=zs[j,i]);s.addCons(zs[j,i]<=x[i]);M=max(F(0),d.caps[j]+a[i]-d.ceilings[j])
            s.addCons(y[j]+float(M)*zs[j,i]<=float(d.ceilings[j]-a[i]+M))
        s.addCons(quicksum(ps[j,i] for i in eligible)==1)
        s.addCons(y[j]+quicksum(float(a[i])*ps[j,i] for i in eligible)<=float(d.caps[j]))
        if d.gamma[j]:s.addCons(h[j]>=float(d.gamma[j]/2)*y[j]*y[j])
        else:s.addCons(h[j]==0)
    s.addCons(quicksum(x)<=m);s.addCons(quicksum(float(d.weights[j])*(y[j]+quicksum(float(a[i])*ps[j,i] for jj,i in ps if jj==j)) for j in range(len(y)))==float(B))
    s.setObjective(quicksum(float(rho[i])*x[i] for i in range(len(x)))+quicksum(float(d.weights[j])*h[j] for j in range(len(y)))-quicksum(float(d.weights[j]*d.reward(j,a[i]))*p for (j,i),p in ps.items()),'minimize')
    s.optimize();sol=s.getBestSol();book=tuple(a[i] for i in range(len(a)) if sol is not None and s.getSolVal(sol,x[i])>.5)
    p=allocate(d,book if book and book[0]<=min(B,min(d.caps)) and len(book)<=m else (a[0],),B,dict(zip(a,rho)))
    ub=-s.getDualbound();valid=abs(ub)<1e19
    return dict(status='NUMERICAL_'+str(s.getStatus()),lower=p['value'],numerical_upper=ub if valid else None,numerical_bound_consistent=bool(valid and ub>=float(p['value'])-1e-8),numerical_absolute_gap=max(0,ub-float(p['value'])) if valid else None,solver_gap=s.getGap() if sol is not None else None,solver_nodes=s.getNNodes(),envelope_error=0,certificate=dict(schema='NDU-R59-SCIP-numerical-v1',instance=spec,instance_sha256=digest(spec),policy=p,numerical_upper=ub if valid else None,scope='Only the feasible policy is independently checked; the SCIP bound is numerical.'))

def main():
    c=json.loads(Path(sys.argv[1]).read_text());method=sys.argv[2];dest=Path(sys.argv[3]);spec=c['spec'];eps=F(c['epsilon']);d,a,rho,B,m=normalize(spec)
    record=dict(id=c['id'],method=method,instance_sha256=digest(spec),status='STARTED',epsilon=qstr(eps));write(dest,record)
    resource.setrlimit(resource.RLIMIT_AS,(3*1024**3,3*1024**3))
    def expire(signum,frame):raise DeadlineExceeded()
    signal.signal(signal.SIGALRM,expire);seed=allocate(d,(a[0],),B,dict(zip(a,rho)));progress=dict(policy=seed,books_evaluated=0)
    cert=None;opt=time.perf_counter();signal.setitimer(signal.ITIMER_REAL,max(.001,c['optimization_cutoff_seconds']-(opt-START)))
    try:
        if method=='price':
            from price_path import solve
            ans=solve(spec,eps,seconds=max(.001,c['optimization_cutoff_seconds']-(time.perf_counter()-START)-.025),max_nodes=100000)
        elif method=='deficit':
            from deficit import solve
            ans=solve(spec,eps,exact_lattice=not eps,max_states=600000)
        elif method=='enumeration':
            from enumeration import solve
            ans=solve(spec,seconds=max(.001,c['optimization_cutoff_seconds']-(time.perf_counter()-START)-.025),progress=progress)
        elif method=='tariff':
            from tariff60 import solve
            ans=solve(spec)
        elif method=='scip':ans=scip_solve(spec,max(.001,c['optimization_cutoff_seconds']-(time.perf_counter()-START)-.05),eps)
        else:raise ValueError('Unknown method')
        signal.setitimer(signal.ITIMER_REAL,0);cert=ans.pop('certificate',None);record.update(encode(ans))
    except DeadlineExceeded:
        signal.setitimer(signal.ITIMER_REAL,0)
        from screening56 import fallback
        cert=fallback(spec,progress['policy'] if method=='enumeration' else seed);record.update(status='OPTIMIZATION_DEADLINE',lower=cert['lower'],upper=cert['upper'],scope='Only the fallback original policy and universal upper bound are certified.')
    except Exception as e:
        signal.setitimer(signal.ITIMER_REAL,0);record.update(status='STATE_LIMIT' if e.__class__.__name__=='StateLimit' else 'ERROR',error=repr(e),traceback=traceback.format_exc())
        if hasattr(e,'requested'):record['requested_states']=str(e.requested)
    finally:signal.setitimer(signal.ITIMER_REAL,0)
    record['optimization_seconds']=time.perf_counter()-opt;record['setup_seconds']=opt-START;record['peak_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if cert:
        record['certificate_schema']=cert['schema'];st=time.perf_counter();raw=canonical(cert);b=gzip.compress(raw,mtime=0);p=R/'results/certificates'/f'{dest.stem}.json.gz';p.parent.mkdir(exist_ok=True);p.write_bytes(b)
        record.update(certificate=p.relative_to(R/'results').as_posix(),certificate_sha256=hashlib.sha256(b).hexdigest(),proof_bytes=len(raw),compressed_proof_bytes=len(b),serialization_seconds=time.perf_counter()-st)
        if cert['schema']=='NDU-price-path-v2-hex':
            ls=list(leaves(cert['tree']));record['max_depth']=max(len(req|ban) for nd,req,ban in ls);record['tree_leaves']=len(ls)
        write(dest,record);st=time.perf_counter()
        try:
            if cert['schema']=='NDU-R59-SCIP-numerical-v1':
                from check_price import check_policy
                value=check_policy(spec,cert['policy']);assert value==F(record['lower']);record['verification_status']='PASS_LOWER_ONLY'
            else:
                if cert['schema']=='NDU-R60-tariff-frontier-v1':from check_tariff60 import verify
                elif cert['schema']=='NDU-deficit-v1-hex':from check_deficit import verify
                elif cert['schema']=='NDU-enumeration-v1-hex':from check_enumeration import verify
                else:from check_price import verify
                ans=verify(cert,digest(spec));record['verification_status']='PASS';record['verification']=ans
        except Exception as e:record.update(verification_status='FAIL',verification_error=repr(e),verification_traceback=traceback.format_exc())
        record['verification_seconds']=time.perf_counter()-st;record['checker_peak_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    record['worker_seconds']=time.perf_counter()-START;write(dest,record)
if __name__=='__main__':main()
