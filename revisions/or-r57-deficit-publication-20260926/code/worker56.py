"""Fresh-process method run, exact certificates, separate measured verification."""
from pathlib import Path
import gzip,json,resource,signal,sys,time,traceback,hashlib
from rational import F,write,encode,digest,canonical,bits,qstr
from price_path import normalize,allocate,solve,DeadlineExceeded,leaves
HERE=Path(__file__).resolve().parent;OUT=HERE.parent/'results'

def main():
    setup=time.perf_counter();case=json.loads(Path(sys.argv[1]).read_text());method=sys.argv[2];dest=Path(sys.argv[3]);dest.parent.mkdir(exist_ok=True,parents=True)
    phase=dest.with_suffix('.phase.json');limit=case['seconds'];spec=case['spec'];eps=F(case['epsilon'])
    if method=='direct-mip':
        from mip_reference import direct_milp
        import scipy.optimize
    elif method in ('deficit','lattice'):from deficit import solve as dp_solve,StateLimit
    elif method=='enumeration':from enumeration import solve as enum_solve
    elif method=='screen':from screening56 import solve_screen
    d,a,rho,B,m=normalize(spec);resource.setrlimit(resource.RLIMIT_AS,(2048*1024*1024,2048*1024*1024))
    def expire(signum,frame):raise DeadlineExceeded()
    signal.signal(signal.SIGALRM,expire);seed=allocate(d,(a[0],),B,dict(zip(a,rho)));certificate=None
    progress=dict(policy=seed,books_evaluated=0)
    record=dict(id=case['id'],family=case['family'],method=method,instance_sha256=digest(spec),epsilon=qstr(eps),algorithm_limit_seconds=limit,address_space_limit_mib=2048,setup_seconds=time.perf_counter()-setup)
    phase.write_text(json.dumps({'phase':'algorithm','time':time.monotonic()}));start=time.perf_counter();signal.setitimer(signal.ITIMER_REAL,limit)
    try:
        if method=='price':ans=solve(spec,eps,seconds=max(0,limit-.005),max_nodes=100000)
        elif method in ('deficit','lattice'):ans=dp_solve(spec,eps,exact_lattice=method=='lattice')
        elif method=='enumeration':ans=enum_solve(spec,seconds=max(0,limit-.005),progress=progress)
        elif method=='screen':ans=solve_screen(spec,eps,seconds=max(0,limit-.005))
        elif method=='direct-mip':ans={'status':'NUMERICAL','numerical':direct_milp(d,a,rho,B,m,segments=16,envelope='tangent',time_limit=limit)}
        else:raise ValueError('Unknown method')
        signal.setitimer(signal.ITIMER_REAL,0);certificate=ans.pop('certificate',None);record.update(encode(ans))
    except DeadlineExceeded:
        signal.setitimer(signal.ITIMER_REAL,0);from screening56 import fallback
        certificate=fallback(spec,progress['policy'] if method=='enumeration' else seed);record.update(status='TIME_LIMIT',lower=certificate['lower'],upper=certificate['upper'],gap=qstr(F(certificate['upper'])-F(certificate['lower'])),evidence_scope='Fallback policy/universal bound; interrupted internal solver work is not certified')
    except MemoryError:
        signal.setitimer(signal.ITIMER_REAL,0);record.update(status='MEMORY_LIMIT')
    except Exception as exc:
        signal.setitimer(signal.ITIMER_REAL,0);record.update(status='STATE_LIMIT' if exc.__class__.__name__=='StateLimit' else 'ERROR',error=repr(exc),traceback=traceback.format_exc())
        if hasattr(exc,'requested'):record.update(requested_state_bits=exc.requested.bit_length(),requested_states_hex=format(exc.requested,'x'),state_allowance=exc.limit)
    if method=='enumeration':record['books_evaluated']=progress['books_evaluated']
    record['algorithm_seconds']=time.perf_counter()-start;record['algorithm_limit_overrun_seconds']=max(0,record['algorithm_seconds']-limit);record['peak_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if certificate is not None:
        record['certificate_schema']=certificate['schema'];record['rational_bits']=bits(certificate)
        serial=time.perf_counter();raw=canonical(certificate);compressed=gzip.compress(raw,mtime=0);path=OUT/'certificates'/(dest.stem+'.json.gz');path.parent.mkdir(exist_ok=True);path.write_bytes(compressed)
        record.update(certificate=str(path.relative_to(OUT)),certificate_sha256=hashlib.sha256(compressed).hexdigest(),proof_bytes=len(raw),compressed_proof_bytes=len(compressed),serialization_seconds=time.perf_counter()-serial)
        if certificate['schema']=='NDU-price-path-v2-hex':
            ls=list(leaves(certificate['tree']));record['tree_leaves']=len(ls);record['created_tree_nodes']=2*len(ls)-1;record['max_depth']=max(len(req|ban) for nd,req,ban in ls)
            record['live_leaves']=sum(nd['proof']['type']!='infeasible' and F(nd['proof']['upper'])>F(certificate['lower'])+eps for nd,req,ban in ls)
            record['price_bits']=bits([nd['proof'].get('price') for nd,req,ban in ls])
        write(dest,record);phase.write_text(json.dumps({'phase':'verification','time':time.monotonic()}));signal.setitimer(signal.ITIMER_REAL,12);begin=time.perf_counter()
        try:
            schema=certificate['schema']
            if schema=='NDU-deficit-v1-hex':from check_deficit import verify
            elif schema=='NDU-enumeration-v1-hex':from check_enumeration import verify
            elif schema=='NDU-screen-v1-hex':from check_screen import verify
            else:from check_price import verify
            record['verification']=verify(certificate,digest(spec));record['verification_status']='PASS'
        except DeadlineExceeded:record['verification_status']='TIME_LIMIT'
        except Exception as exc:record.update(verification_status='FAIL',verification_error=repr(exc),verification_traceback=traceback.format_exc())
        finally:signal.setitimer(signal.ITIMER_REAL,0)
        record['verification_seconds']=time.perf_counter()-begin
    record['total_measured_seconds']=record['algorithm_seconds']+record.get('serialization_seconds',0)+record.get('verification_seconds',0)
    write(dest,record);phase.write_text(json.dumps({'phase':'done','time':time.monotonic()}));print(case['id'],method,record['status'],record.get('verification_status',''),flush=True)
if __name__=='__main__':main()
