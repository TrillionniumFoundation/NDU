import sys,json,gzip,time,signal,hashlib,datetime
from pathlib import Path
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'code'))
from rational import write
rows=[(p,json.loads(p.read_text())) for p in (r/'results/runs').glob('*.json') if '.phase.' not in p.name]
items=[(p,z) for p,z in rows if z.get('verification_status')=='TIME_LIMIT']
write(r/'VERIFY_REPLAY_PROTOCOL.json',{'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Post-inspection completion of initial 12-second verification limits. Original execution records remain unchanged. This is not a new solver timing or unseen sample.','timeout_seconds':90,'cases':[p.stem for p,z in items]})
class Limit(Exception):pass
signal.signal(signal.SIGALRM,lambda *args:(_ for _ in ()).throw(Limit()))
results=[]
write(r/'results/VERIFY_REPLAY.json',results)
for p,z in items:
 certpath=r/'results'/z['certificate'];raw=certpath.read_bytes();cert=json.loads(gzip.decompress(raw))
 schema=cert['schema']
 if schema=='NDU-deficit-v1-hex':from check_deficit import verify
 elif schema=='NDU-enumeration-v1-hex':from check_enumeration import verify
 elif schema=='NDU-screen-v1-hex':from check_screen import verify
 else:from check_price import verify
 begin=time.perf_counter();signal.setitimer(signal.ITIMER_REAL,90)
 try:out=verify(cert,z['instance_sha256']);status='PASS'
 except Limit:status='TIME_LIMIT';out=None
 except Exception as e:status='FAIL';out=repr(e)
 finally:signal.setitimer(signal.ITIMER_REAL,0)
 rec={'run_id':p.stem,'certificate_sha256':hashlib.sha256(raw).hexdigest(),'initial_verification_status':z['verification_status'],'replay_status':status,'seconds':time.perf_counter()-begin,'result':out}
 results.append(rec);write(r/'results/VERIFY_REPLAY.json',results);print(p.stem,status,rec['seconds'],flush=True)
