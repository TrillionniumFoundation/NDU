"""One fresh process per method, matched time/address-space budgets."""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations
import gzip,json,os,resource,signal,sys,time,traceback
from price_path import Model,normalize,allocate,solve,DeadlineExceeded,encode
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
OUT=HERE.parent/'results';LIMIT=4.0

def main():
    setup=time.perf_counter();case=json.loads(Path(sys.argv[1]).read_text());method=sys.argv[2];name=case['id']+'--'+method
    dest=OUT/'runs'/f'{name}.json';phase=dest.with_suffix('.phase');dest.parent.mkdir(exist_ok=True)
    d,a,rho,B,m=normalize(case['spec']);eps=F(case['epsilon']);routine=None;checker=None
    if method=='price':
        from check_price import verify as checker
    elif method in ('uniform','classbox'):
        sys.path.insert(0,str(ROOT/'revisions/or-r52-resource-path-20260925/code'))
        from resource_path import Instance
        old=Instance.make(d.caps,d.weights,d.gamma,d.ceilings,d.reward_r[0],d.reward_q[0])
        if method=='uniform':
            from resource_path import solve as routine
            from check_resource import verify as checker
        else:
            from pooling import solve as routine
            from check_pooling import check as checker
    elif method=='mip':
        from mip_reference import direct_milp as routine
        import scipy.optimize
    elif method!='enumeration':raise ValueError(method)
    resource.setrlimit(resource.RLIMIT_AS,(2048*1024*1024,2048*1024*1024))
    def expire(signum,frame):raise DeadlineExceeded()
    signal.signal(signal.SIGALRM,expire)
    phase.write_text(json.dumps(dict(phase='algorithm',time=time.monotonic())))
    start=time.perf_counter();signal.setitimer(signal.ITIMER_REAL,LIMIT)
    record=dict(id=case['id'],method=method,instance_sha256=case['instance_sha256'],epsilon=str(eps),
                setup_seconds=start-setup,algorithm_limit_seconds=LIMIT,address_space_limit_mib=2048)
    certificate=None;seed=allocate(d,(a[0],),B,dict(zip(a,rho)));best=seed['value'];seen=0
    try:
        if method=='price':
            ans=solve(case['spec'],eps,12,255,seconds=LIMIT-0.02);certificate=ans.pop('certificate');record.update(encode(ans))
        elif method=='uniform':
            ans=routine(old,a,rho,B,m,eps);certificate=ans.pop('certificate');record.update(encode(ans));record['status']='TOLERANCE'
        elif method=='classbox':
            ans=routine(old,a,rho,B,m,epsilon=eps,max_nodes=255,price_steps=4);certificate=encode(ans)
            record.update(status=ans['status'],lower=str(ans['lower_bound']),upper=str(ans['upper_bound']),gap=str(ans['gap']),nodes=ans['evaluated_nodes'])
        elif method=='enumeration':
            policy=seed
            for size in range(1,m+1):
                for book in combinations(a,size):
                    if book[0]>min(B,min(d.caps)):continue
                    p=allocate(d,book,B,dict(zip(a,rho)));seen+=1
                    if p['value']>best:best=p['value'];policy=p
            record.update(status='EXACT',lower=str(best),upper=str(best),gap='0',books=seen,policy=encode(policy))
        elif method=='mip':
            answers={e:routine(d,a,rho,B,m,segments=32,envelope=e,time_limit=LIMIT/2) for e in ('tangent','secant')}
            up=answers['tangent'].get('numerical_upper');low=answers['secant'].get('value')
            record.update(status='NUMERICAL',envelopes=answers,lower=low,upper=up,gap=None if up is None or low is None else up-low,
                          solver_limit_seconds_per_envelope=LIMIT/2)
        signal.setitimer(signal.ITIMER_REAL,0)
    except DeadlineExceeded:
        signal.setitimer(signal.ITIMER_REAL,0)
        record.update(status='TIME_LIMIT',lower=str(best),upper=str(d.mean_reward(F(1))),gap=str(d.mean_reward(F(1))-best),books=seen,
                      partial_scope='Original feasible incumbent and universal upper; interrupted solver work is not a global proof')
    except MemoryError:
        signal.setitimer(signal.ITIMER_REAL,0);record.update(status='MEMORY_LIMIT')
    except Exception as e:
        signal.setitimer(signal.ITIMER_REAL,0);record.update(status='ERROR',error=repr(e),traceback=traceback.format_exc())
    record['algorithm_seconds']=time.perf_counter()-start
    record['algorithm_peak_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    dest.write_text(json.dumps(record,indent=2)+'\n')
    if certificate is not None:
        path=OUT/'certificates'/f'{name}.json.gz';path.parent.mkdir(exist_ok=True)
        raw=json.dumps(certificate,sort_keys=True,separators=(',',':')).encode();data=gzip.compress(raw,mtime=0);path.write_bytes(data)
        record.update(certificate=str(path.relative_to(OUT)),certificate_bytes=len(data),uncompressed_certificate_bytes=len(raw))
        phase.write_text(json.dumps(dict(phase='verification',time=time.monotonic())))
        begin=time.perf_counter();signal.setitimer(signal.ITIMER_REAL,60)
        try:record['verification']=checker(certificate);record['verification_status']='PASS'
        except DeadlineExceeded:record['verification_status']='TIME_LIMIT'
        except Exception as e:record.update(verification_status='FAIL',verification_error=repr(e),verification_traceback=traceback.format_exc())
        finally:signal.setitimer(signal.ITIMER_REAL,0)
        record['verification_seconds']=time.perf_counter()-begin
    record['process_peak_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    dest.write_text(json.dumps(record,indent=2)+'\n');phase.write_text(json.dumps(dict(phase='done',time=time.monotonic())))
    print(name,record['status'],record.get('gap'),flush=True)
if __name__=='__main__':main()
