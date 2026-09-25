"""Canonical semantic witnesses; timing observations are kept in case records.

Publication replays deterministic searches at their originally evaluated node
counts. It does not rerun or replace the recorded timing study.
"""
from pathlib import Path
from fractions import Fraction as F
import gzip,json,hashlib,sys,time,platform
from coarsening import Instance,solve,encode
from check_coarsening import check
from box_solver import solve as raw_solve
from check_certificate import check as raw_check
R=Path(__file__).resolve().parents[1]

def semantic(x):
    if isinstance(x,dict):return {k:semantic(v) for k,v in x.items() if k not in ('seconds','lift_seconds')}
    if isinstance(x,list):return [semantic(v) for v in x]
    return x

def packed(c):
    raw=json.dumps(semantic(encode(c)),sort_keys=True,separators=(',',':')).encode()
    return gzip.compress(raw,mtime=0),len(raw)

def make_model(d):
    return Instance.make(d['caps'],d['weights'],d['gamma'],d['ceilings'],d['r'],d['curvature'])

def freeze():
    """Packaging only: strips timing metadata from exact semantic certificates."""
    file=R/'REPLAY_MANIFEST.json'
    if file.exists():raise RuntimeError('Semantic evidence already frozen')
    entries=[];mapping={}
    for path in sorted((R/'results/certificates').glob('*.json.gz')):
        c=json.loads(gzip.decompress(path.read_bytes()));inner=c.get('inner_certificate',c)
        is_coarse='inner_certificate' in c
        before=hashlib.sha256(path.read_bytes()).hexdigest()
        data,rawlen=packed(c);path.write_bytes(data)
        sha=hashlib.sha256(data).hexdigest()
        e=dict(path=str(path.relative_to(R)),sha256=sha,uncompressed_bytes=rawlen,
          original_model=c['original_model'],catalog=c['catalog'],charges=c['charges'],
          promise=c['promise'],budget=c['budget'],epsilon=c['requested_epsilon'],
          evaluated_nodes=inner['evaluated_nodes'],price_steps=8,coarse=is_coarse,
          groups=c['groups'] if is_coarse else None,
          inner_epsilon=inner['requested_epsilon'],prepackaging_sha256=before)
        entries.append(e);mapping[e['path']]=e
        (check if is_coarse else raw_check)(semantic(c))
    for name in ('joint','stress'):
        p=R/f'results/{name}.json';d=json.loads(p.read_text())
        def update(x):
            if isinstance(x,dict):
                if x.get('path') in mapping:
                    z=mapping[x['path']];x['sha256']=z['sha256'];x['uncompressed_bytes']=z['uncompressed_bytes']
                for v in x.values():update(v)
            elif isinstance(x,list):
                for v in x:update(v)
        update(d);p.write_text(json.dumps(d,indent=2)+'\n')
    manifest=dict(schema='ndu-r47-semantic-replay-v1',scope='Exact semantic witnesses; local timing observations remain in joint/stress/MIP records',entries=entries)
    file.write_text(json.dumps(manifest,indent=2)+'\n')
    print('FROZEN',len(entries))

def replay():
    manifest=json.loads((R/'REPLAY_MANIFEST.json').read_text());rows=[]
    outpath=R/'results/REPLAY_VALIDATION.json'
    prior=json.loads(outpath.read_text()) if outpath.exists() else {}
    done={z['path']:z for z in prior.get('certificates',[])}
    for e in manifest['entries']:
        p=R/e['path']
        if e['path'] in done and p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256'] and done[e['path']]['sha256']==e['sha256']:
            rows.append(done[e['path']]);continue
        D=make_model(e['original_model']);a=tuple(map(F,e['catalog']));rho=tuple(map(F,e['charges']))
        t=time.perf_counter()
        if e['coarse']:
            c=solve(D,a,rho,F(e['promise']),e['budget'],e['groups'],F(e['epsilon']),
              inner_epsilon=F(e['inner_epsilon']),max_nodes=e['evaluated_nodes'],seconds_limit=None,price_steps=e['price_steps'])
            checker=check
        else:
            c=raw_solve(D,a,rho,F(e['promise']),e['budget'],F(e['epsilon']),
              max_nodes=e['evaluated_nodes'],seconds_limit=None,price_steps=e['price_steps'],aggregate_types=True,record_tables=True)
            checker=raw_check
        data,n=packed(c);sha=hashlib.sha256(data).hexdigest()
        if sha!=e['sha256'] or n!=e['uncompressed_bytes']:raise AssertionError(('Semantic replay mismatch',e['path'],sha,e['sha256']))
        result=checker(json.loads(gzip.decompress(data)));p=R/e['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        rows.append(dict(path=e['path'],sha256=sha,status='PASS',replay_and_check_seconds=time.perf_counter()-t,checker=result))
        outpath.write_text(json.dumps(dict(status='RUNNING',certificates=rows),indent=2)+'\n')
        print('REPLAY PASS',e['path'],flush=True)
    out=dict(status='PASS',semantic_certificates=len(rows),python=sys.version,platform=platform.platform(),
        timing_scope='Publication deterministic replay and verification, not the original benchmark timing study',certificates=rows)
    (R/'results/REPLAY_VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
    return out
if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='freeze':freeze()
    else:replay()
