"""Fresh-host total robust certification cost, including ensemble prediction.
Protocol fixed in ROBUST_COST_PROTOCOL.md before this additional execution.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import sys,json,gzip,time,platform
from pathlib import Path
from fractions import Fraction as F
import numpy as np
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'or-r23-20260923'))
from robust_study import (Tree,contexts,frozen_models,normalize,geometry,anchor,solve,
    dual_record,upper,repair,value,maximin,vector_record,VERTICES)


def run():
    out=R/'results';out.mkdir(exist_ok=True)
    t=time.perf_counter();models=frozen_models();load_seconds=time.perf_counter()-t
    p=json.loads((R.parent/'or-r23-20260923/results/primitives.json').read_text())
    cc=contexts(2407401,16,p['rank']);rows=[];failed=[];geotimes=[];started=time.perf_counter()
    with gzip.open(out/'robust_cost_certificates.jsonl.gz','wt') as f:
      for r in (0,4):
        t=time.perf_counter();go=geometry(p,r,'outer');gr=geometry(p,r,'robust');anc=anchor(p,gr)
        geotimes.append({'r':r,'seconds':time.perf_counter()-t})
        for j,context in enumerate(cc):
            c=list(map(int,context));duals=[];bounds=[];t=time.perf_counter()
            for vi,v in enumerate(VERTICES):
                try:
                    x,d,it=solve(p,go,c,r,v);dd=dual_record(p,go,c,r,v,x,d)
                except Exception as exc:
                    failed.append({'r':r,'id':j,'kind':'comparator','vertex':vi,'error':repr(exc)})
                    dd={'den':1,'p':[0]*p['rank'],'s':[0]*len(p['qnum']),
                        'mu':[0]*len(go['A_num']),'nu':[0]*len(go['E'])}
                du=upper(p,go,c,r,v,dd);duals.append(dd);bounds.append(du)
            shared=time.perf_counter()-t
            item={'r':r,'id':j,'context':c,'outer_duals':duals,'outer_upper':[str(v) for v in bounds],
                  'shared_comparator_seconds':shared,'methods':{}}
            methods=['protected-tanh-gradient','protected-rbf-direct','classical-robust-maximin']
            order=(j+r)%3;methods=methods[order:]+methods[:order]
            for method in methods:
                t0=time.perf_counter();pred_time=0.
                try:
                    if method=='classical-robust-maximin':
                        raw,it=maximin(p,gr,c,r,bounds)
                    else:
                        key=method.replace('protected-','');t=time.perf_counter()
                        eta=np.mean([m[key].predict(normalize(np.array(c)[None,:],p['rank']))[0] for m in models],axis=0)
                        pred_time=time.perf_counter()-t
                        raw,d,it=solve(p,gr,c,0,VERTICES[0],price=eta)
                    rec=repair(p,gr,raw,anc)
                    vv=[value(p,c,r,v,rec['x_num'],rec['x_den']) for v in VERTICES]
                    gate=min(vv)<0
                    if gate:
                        rec=vector_record([F(0)]*len(p['qnum']));rec['repair_fraction']='0';vv=[F(0)]*8
                    lower=min(v-u for v,u in zip(vv,bounds))
                    rec.update(vertex_values=[str(v) for v in vv],robust_gain_lower=str(lower),outside_gate=gate)
                    status='PASS'
                except Exception as exc:
                    failed.append({'r':r,'id':j,'kind':method,'error':repr(exc)})
                    rec=vector_record([F(0)]*len(p['qnum']));lower=-max(bounds)
                    rec.update(vertex_values=['0']*8,robust_gain_lower=str(lower),outside_gate=True,repair_fraction='0')
                    status='FAIL_RETAINED'
                own=time.perf_counter()-t0
                rec.update(own_seconds=own,prediction_seconds=pred_time,status=status)
                item['methods'][method]=rec
                rows.append({'r':r,'rho':r/16,'id':j,'method':method,'own_seconds':own,
                   'prediction_seconds':pred_time,'comparator_seconds':shared,'total_seconds':own+shared,
                   'gain_lower':float(lower),'status':status})
            f.write(json.dumps(item)+'\n');f.flush()
            if j%4==0:print('robust cost',r,j,flush=True)
    summary=[]
    for r in (0,4):
      for method in ['protected-tanh-gradient','protected-rbf-direct','classical-robust-maximin']:
        rr=[a for a in rows if a['r']==r and a['method']==method];s={'r':r,'rho':r/16,'method':method,'n':len(rr)}
        for key in ('prediction_seconds','own_seconds','comparator_seconds','total_seconds'):
            arr=np.array([v[key] for v in rr]);s[key]={'mean':float(arr.mean()),'median':float(np.median(arr)),
                'p25':float(np.quantile(arr,.25)),'p75':float(np.quantile(arr,.75))}
        s.update(mean_gain_lower=float(np.mean([v['gain_lower'] for v in rr])),min_gain_lower=min(v['gain_lower'] for v in rr))
        summary.append(s)
    (out/'robust_cost_rows.json').write_text(json.dumps(rows,indent=2)+'\n')
    (out/'robust_cost_summary.json').write_text(json.dumps({'status':'EXECUTED','contexts':16,'policy_records':len(rows),
        'comparator_certificates':16*2*8,'failed_solves':failed,'model_loading_seconds':load_seconds,
        'geometry_setup':geotimes,'summary':summary,'elapsed_seconds':time.perf_counter()-started,
        'platform':platform.platform(),'scope':'Fixed implementations, fresh matched-host per-query costs. Full comparator batch charged once per independently certified decision; reused in this experiment.'},indent=2)+'\n')
if __name__=='__main__':run()
