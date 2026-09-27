"""One timed request: startup, solve, serialize and independent checking share a deadline."""
import time
START=time.perf_counter()
from pathlib import Path
import gzip,hashlib,json,resource,signal,sys,traceback,subprocess
from rational import F,write,encode,digest,canonical
from price_path import normalize,allocate,DeadlineExceeded,leaves
from tariff60 import standard_fee,NotApplicable,GuardExceeded
R=Path(__file__).resolve().parents[1]

def fallback(spec,policy):
    d,a,rho,B,m=normalize(spec)
    return encode(dict(schema='NDU-price-path-v2-hex',spec=spec,instance_sha256=digest(spec),
        epsilon='0',tree={'proof':{'type':'universal','upper':d.mean_reward(F(1))}},
        policy=policy,lower=policy['value'],upper=d.mean_reward(F(1)),root_diagnostics=[]))

def check(cert,spec):
    schema=cert['schema']
    if schema=='NDU-R59-SCIP-numerical-v1':
        from check_price import check_policy
        v=check_policy(spec,cert['policy']);return dict(status='PASS_LOWER_ONLY',lower=str(v))
    if schema=='NDU-R60-tariff-frontier-v1':from check_tariff60 import verify
    elif schema=='NDU-R61-robust-tariff-v1':from check_robust61 import verify
    elif schema=='NDU-deficit-v1-hex':from check_deficit import verify
    elif schema=='NDU-enumeration-v1-hex':from check_enumeration import verify
    else:from check_price import verify
    out=verify(cert,digest(spec))
    if schema=='NDU-price-path-v2-hex':
        from diagnostics61 import verify_root
        out['root_diagnostics']=verify_root(spec,cert.get('root_diagnostics',[]))
    if 'hybrid_probe_certificate' in cert:
        out['hybrid_probe']=check(cert['hybrid_probe_certificate'],spec)
    return out

def main():
    c=json.loads(Path(sys.argv[1]).read_text());method=sys.argv[2];dest=Path(sys.argv[3]);spec=c['spec'];eps=F(c['epsilon'])
    d,a,fees,B,m=normalize(spec);fee=standard_fee(fees);count=sum(x!=fee for x in fees);guard=c.get('guard',12)
    applicable=not any(d.gamma) and not any(d.reward_q) and len(set(d.reward_r))==1
    record=dict(id=c['id'],method=method,instance_sha256=digest(spec),status='STARTED',
        tariff_metadata=dict(standard_fee=str(fee),exceptions=count,configured_guard=guard,
            mathematical_applicability=applicable,within_guard=count<=guard,tie_rule='smallest rational modal fee'))
    write(dest,record);resource.setrlimit(resource.RLIMIT_AS,(3*1024**3,3*1024**3))
    def expire(*_):raise DeadlineExceeded()
    signal.signal(signal.SIGALRM,expire)
    opt=time.perf_counter();cutoff=c['optimization_cutoff_seconds'];remaining=lambda:max(.001,cutoff-(time.perf_counter()-START)-.02)
    seed=allocate(d,(a[0],),B,dict(zip(a,fees)));cert=None;progress={'policy':seed};root=None
    signal.setitimer(signal.ITIMER_REAL,remaining())
    try:
        if method=='tariff':
            from tariff60 import solve
            ans=solve(spec,max_exceptions=guard)
        elif method=='robust':
            from robust61 import solve
            ans=solve(spec,eps,max_exceptions=guard)
        elif method=='price':
            from price_path import solve
            ans=solve(spec,eps,seconds=remaining(),max_nodes=100000)
        elif method=='enumeration':
            from enumeration import solve
            ans=solve(spec,seconds=remaining(),progress=progress)
        elif method=='deficit':
            from deficit import solve
            ans=solve(spec,eps,max_states=600000)
        elif method=='scip':
            from scip61 import scip_solve
            ans=scip_solve(spec,remaining(),eps)
        elif method=='hybrid':
            from price_path import solve as price
            from robust61 import simplify,solve as robust
            root=price(spec,eps,price_steps=3,max_nodes=1,seconds=max(.001,remaining()/4))
            record['probe_mechanics']=encode(root['mechanics']);record['probe_seconds']=root['seconds']
            if root['upper']-root['lower']<=eps:
                ans=root;record['selected_route']='root_price'
            elif applicable and simplify(fees,min(4,len(fees)-1))['absolute_deviation']<=eps:
                record['selected_route']='robust_tariff_d_le_4';ans=robust(spec,eps,max_exceptions=4)
            else:
                record['selected_route']='price_restart';ans=price(spec,eps,seconds=remaining(),max_nodes=100000)
        else:raise ValueError('Unknown method')
        signal.setitimer(signal.ITIMER_REAL,0);cert=ans.pop('certificate',None);record.update(encode(ans))
    except NotApplicable as e:record.update(status='MATHEMATICALLY_INAPPLICABLE',error=str(e))
    except GuardExceeded as e:record.update(status='ENGINEERING_GUARD',error=str(e))
    except DeadlineExceeded:
        cert=root['certificate'] if root else fallback(spec,progress['policy']);record.update(status='OPTIMIZATION_DEADLINE',lower=cert['lower'],upper=cert['upper'])
    except Exception as e:
        record.update(status='STATE_LIMIT' if e.__class__.__name__=='StateLimit' else 'ERROR',error=repr(e),traceback=traceback.format_exc())
    finally:signal.setitimer(signal.ITIMER_REAL,0)
    record.update(optimization_seconds=time.perf_counter()-opt,setup_seconds=opt-START,optimizer_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    write(dest,record)
    if cert:
        if root and 'certificate' in root and cert is not root['certificate']:
            cert['hybrid_probe_certificate']=root['certificate']
        tick=time.perf_counter();raw=canonical(cert);compressed=gzip.compress(raw,mtime=0);path=R/'results/certificates'/f'{dest.stem}.json.gz';path.parent.mkdir(exist_ok=True);path.write_bytes(compressed)
        record.update(certificate=path.relative_to(R/'results').as_posix(),certificate_schema=cert['schema'],certificate_sha256=hashlib.sha256(compressed).hexdigest(),
            proof_bytes=len(raw),compressed_proof_bytes=len(compressed),serialization_seconds=time.perf_counter()-tick)
        if cert['schema']=='NDU-price-path-v2-hex':
            ls=list(leaves(cert['tree']));record['tree_leaves']=len(ls);record['max_depth']=max(len(req|ban) for nd,req,ban in ls)
        write(dest,record);tick=time.perf_counter()
        try:
            receipt_path=dest.with_suffix('.check.json')
            subprocess.run([sys.executable,str(R/'code/checker61.py'),str(path),str(receipt_path)],check=True)
            receipt=json.loads(receipt_path.read_text());record.update(verification_status=receipt['status'],verification=receipt,checker_peak_rss_kib=receipt['peak_rss_kib'])
        except Exception as e:record.update(verification_status='FAIL',verification_error=repr(e),verification_traceback=traceback.format_exc())
        record.update(verification_seconds=time.perf_counter()-tick,checker_process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    record['worker_seconds']=time.perf_counter()-START;write(dest,record)

if __name__=='__main__':main()
