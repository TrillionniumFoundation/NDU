"""Direct, rationally audited R24 model-specific/outer comparator diagnostics."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
import json,gzip,sys,time,platform,argparse
from pathlib import Path
from fractions import Fraction as F
import numpy as np
R=Path(__file__).resolve().parent;REPO=R.parent.parent
sys.path.insert(0,str(R.parent/'or-r23-20260923'))
from robust_study import setup,QP
sys.path.insert(0,str(R))
from interior_exact import make_model,repair_time,objective,upper,mixture_weights


def solve(p,m):
    t=time.perf_counter()
    # Float proposals and exact certificate construction use distinct code paths.
    g={'A_num':[[float(a*16) for a in row] for row in m['A']],
       'budget_num':[float(a*512) for a in m['rhs']], 'E':m['E']}
    P,M,lo,hi=setup(p,g,True);n=len(p['qnum'])
    q=np.r_[-np.asarray(m['b'],float),float(m['lam'])*np.asarray(p['knum'])/8]
    solver=QP(P,M,lo,hi,eps=1e-9)
    try:x,d,it=solver.solve(q,previous=False)
    finally:solver.close()
    nm=len(m['A']);ne=len(m['E']);den=10**9
    pp=np.rint((np.asarray(p['Unum'])/32@x[:n])*den).astype(np.int64)
    mu=np.maximum(0,np.rint(d[n:n+nm]*den)).astype(np.int64)
    nu=np.rint(d[n+nm:n+nm+ne]*den).astype(np.int64)
    ss=np.rint((d[n+nm+ne:n+nm+ne+n]-d[n+nm+ne+n:n+nm+ne+2*n])*den).astype(np.int64)
    cap=np.array([int(m['lam']*F(int(k),8)*den) for k in p['knum']],dtype=np.int64)
    ss=np.clip(ss,-cap,cap)
    dual={'den':den,'p':pp.tolist(),'s':ss.tolist(),'mu':mu.tolist(),'nu':nu.tolist()}
    rec=repair_time(p,m,x[:n]); lower=objective(p,m,rec); ub=upper(p,m,dual)
    assert ub>=lower
    return {'policy':rec,'dual':dual,'lower':str(lower),'upper':str(ub),
            'gap':float(ub-lower),'iterations':it,'seconds':time.perf_counter()-t}


def run(limit=None):
    out=R/('pilot' if limit else 'results');out.mkdir(exist_ok=True)
    old=R.parent/'or-r23-20260923/results'
    p=json.loads((old/'primitives.json').read_text())
    with gzip.open(old/'certificates.jsonl.gz','rt') as f:items=[json.loads(line) for line in f]
    if limit:items=items[:limit]
    rng=np.random.default_rng(2402301);rows=[];failures=[];started=time.perf_counter()
    with gzip.open(out/'interior_certificates.jsonl.gz','wt') as fh:
      for item in items:
        for repetition in range(2):
            theta=rng.integers(-7,8,size=3).tolist()
            record={'r':item['r'],'id':item['id'],'context':item['context'],
                    'replicate':repetition,'theta_num_over_8':theta}
            ww=mixture_weights(theta)
            mix=sum((a*F(b) for a,b in zip(ww,item['outer_upper'])),F(0))
            record['vertex_mixture_upper']=str(mix)
            for kind,flag in [('true',False),('outer',True)]:
                model=make_model(p,item['context'],item['r'],theta,outer=flag)
                try:record[kind]=solve(p,model)
                except Exception as e:
                    failures.append({**{k:record[k] for k in ('r','id','replicate')},'kind':kind,'error':repr(e)})
                    # Retain a valid but potentially wide zero-policy/zero-dual bracket.
                    from interior_exact import vector_record
                    dual={'den':1,'p':[0]*p['rank'],'s':[0]*len(p['qnum']),
                          'mu':[0]*len(model['A']),'nu':[0]*len(model['E'])}
                    ub=upper(p,model,dual)
                    rec=vector_record([F(0)]*len(p['qnum']))
                    record[kind]={'policy':rec,'dual':dual,'lower':'0','upper':str(ub),
                                  'gap':float(ub),'failed':True,'seconds':None}
            lk,uk=[F(record['true'][a]) for a in ('lower','upper')]
            lo,uo=[F(record['outer'][a]) for a in ('lower','upper')]
            assert lk<=uk and lo<=uo and mix>=lk
            row={'r':item['r'],'rho':item['r']/16,'id':item['id'],'replicate':repetition,
                 'total_slack_lower':float(max(F(0),mix-uk)), 'total_slack_upper':float(mix-lk),
                 'outer_set_slack_lower':float(max(F(0),lo-uk)),'outer_set_slack_upper':float(uo-lk),
                 'interpolation_slack_lower':float(max(F(0),mix-uo)), 'interpolation_slack_upper':float(mix-lo),
                 'true_value_lower':float(lk),'outer_value_lower':float(lo),
                 'true_gap':record['true']['gap'],'outer_gap':record['outer']['gap']}
            rows.append(row);fh.write(json.dumps(record)+'\n');fh.flush()
        if item['id']%16==0:print('interior',item['r'],item['id'],len(rows),flush=True)
    summary=[]
    for r in sorted(set(a['r'] for a in rows)):
        rr=[a for a in rows if a['r']==r];res={'r':r,'rho':r/16,'models':len(rr)}
        for key in ('total_slack_lower','total_slack_upper','outer_set_slack_upper','interpolation_slack_upper','true_gap','outer_gap'):
            ar=np.array([a[key] for a in rr]);res[key]={'mean':float(ar.mean()),'median':float(np.median(ar)),
                'p25':float(np.quantile(ar,.25)),'p75':float(np.quantile(ar,.75)),'p95':float(np.quantile(ar,.95)),'max':float(ar.max())}
        summary.append(res)
    (out/'interior_rows.json').write_text(json.dumps(rows,indent=2)+'\n')
    (out/'interior_summary.json').write_text(json.dumps({'status':'EXECUTED','pilot':bool(limit),'models':len(rows),
      'comparator_solves':2*len(rows),'failures':failures,'summary':summary,'seconds':time.perf_counter()-started,
      'platform':platform.platform(),'scope':'Designed interior models; rational brackets; no population or field-calibration inference'},indent=2)+'\n')
    print(json.dumps({'models':len(rows),'failed':len(failures),'seconds':time.perf_counter()-started}),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--pilot',action='store_true');args=ap.parse_args();run(2 if args.pilot else None)
