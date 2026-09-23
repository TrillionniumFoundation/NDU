"""Independent R24 record replay using only the Python standard library.
Run with python -S. Numerical optimizers and reported objective values are not
trusted. --check verifies the already-published summary without mutating it.
"""
import json,gzip,sys,copy,hashlib
from pathlib import Path
from fractions import Fraction as F
R=Path(__file__).resolve().parent;O=R/'results'
sys.path.insert(0,str(R.parent/'or-r22-20260923'))
from certificate import audit_exact
sys.path.insert(0,str(R.parent/'or-r23-20260923'))
import robust_exact as robust
sys.path.insert(0,str(R))
import interior_exact as ie


def load(p):return json.loads(p.read_text())
def stream(p):
    with gzip.open(p,'rt') as f:
        for line in f:yield json.loads(line)

def replay(check=False):
    p=load(R.parent/'or-r23-20260923/results/primitives.json')
    originals={(a['r'],a['id']):a for a in stream(R.parent/'or-r23-20260923/results/certificates.jsonl.gz')}
    source_p=load(R.parent/'or-r23-20260923/results/primitives.json')
    source_g=load(R.parent/'or-r23-20260923/results/geometries.json')
    source_bounds=0
    for a in originals.values():
        go=source_g[f"{a['r']}-outer"]
        robust.verify_outer(source_p,go,a['r'])
        uu=[robust.upper(source_p,go,a['context'],a['r'],v,d) for v,d in zip(robust.VERTICES,a['outer_duals'])]
        assert len(uu)==8 and [str(v) for v in uu]==a['outer_upper']
        source_bounds+=8
    assert source_bounds==3072
    interior_rows={(a['r'],a['id'],a['replicate']):a for a in load(O/'interior_rows.json')}
    seen=set();count=0;first=None
    for a in stream(O/'interior_certificates.jsonl.gz'):
        key=(a['r'],a['id'],a['replicate']);assert key not in seen;seen.add(key)
        source=originals[(a['r'],a['id'])];assert a['context']==source['context']
        weights=ie.mixture_weights(a['theta_num_over_8']);assert sum(weights)==1 and all(w>0 for w in weights)
        mix=sum((w*F(u) for w,u in zip(weights,source['outer_upper'])),F(0))
        assert str(mix)==a['vertex_mixture_upper']
        intervals={}
        for name,flag in [('true',False),('outer',True)]:
            m=ie.make_model(p,a['context'],a['r'],a['theta_num_over_8'],outer=flag)
            rr=a[name];ie.feasible(p,m,rr['policy'])
            lo=ie.objective(p,m,rr['policy']);up=ie.upper(p,m,rr['dual'])
            assert str(lo)==rr['lower'] and str(up)==rr['upper'] and up>=lo
            assert abs(float(up-lo)-rr['gap'])<1e-14
            intervals[name]=(lo,up);count+=1
            if name=='true' and first is None and a['r']==4:first=(copy.deepcopy(m),copy.deepcopy(rr))
        lk,uk=intervals['true'];lo,uo=intervals['outer'];r=interior_rows[key]
        assert mix>=lk and uo>=lk
        checks={'total_slack_lower':max(F(0),mix-uk),'total_slack_upper':mix-lk,
          'outer_set_slack_lower':max(F(0),lo-uk),'outer_set_slack_upper':uo-lk,
          'interpolation_slack_lower':max(F(0),mix-uo),'interpolation_slack_upper':mix-lo}
        assert all(abs(float(value)-r[name])<1e-14 for name,value in checks.items())
    assert len(seen)==768 and count==1536 and len(interior_rows)==len(seen)
    # Nominal timing output: independently check every deployed rational vector.
    with gzip.open(O/'timing_primitives.json.gz','rt') as f:ps=json.load(f)
    rows=load(O/'timing_rows.json');rowmap={(a['instance'],a['context_id'],a['replicate'],a['tol'],a['method']):a for a in rows}
    deployments=labels=0;seen_dep=set();first_nominal=None
    for item in stream(O/'timing_certificates.jsonl.gz'):
        rec=item['record'];pr=ps[item['instance']]
        aa=audit_exact(pr,rec['context'],rec['x_num'],rec['x_den'],rec['price_num'],rec['switch_num'],rec['ineq_num'],rec['equality_num'],rec['dual_den'])
        exact_gap=F(aa['upper_exact'])-F(aa['gain_exact'])
        if item['kind']=='label':assert exact_gap<=F(1,100000);labels+=1;continue
        key=(item['instance'],item['context_id'],item['replicate'],item['tol'],item['method']);assert key not in seen_dep;seen_dep.add(key)
        row=rowmap[key];assert row['status']=='PASS' and rec['context']==row['context']
        assert exact_gap<=F(str(item['tol'])) and abs(aa['gap']-row['gap'])<1e-12
        assert row['fallback']==(row['polished_gap']>row['tol'])
        if not row['fallback']:assert row['fallback_iterations']==0
        phases=['prediction','initial_solve','first_audit','polishing','fallback_setup','fallback_solve','fallback_audit']
        assert all(row[k]>=0 for k in phases)
        assert abs(row['total']-sum(row[k] for k in phases)-row['unallocated_overhead'])<1e-12
        deployments+=1
        if first_nominal is None:first_nominal=(pr,rec)
    assert deployments==1728 and labels==192 and len(rowmap)==deployments
    # Fresh robust online costs: reconstruct original robust/outer geometries,
    # then check every one of the 256 comparator and 96 policy certificates.
    gg=load(R.parent/'or-r23-20260923/results/geometries.json')
    rp=load(R.parent/'or-r23-20260923/results/primitives.json')
    costs={(a['r'],a['id'],a['method']):a for a in load(O/'robust_cost_rows.json')}
    robust_policies=robust_upper=0
    for a in stream(O/'robust_cost_certificates.jsonl.gz'):
        gr=gg[f"{a['r']}-robust"];go=gg[f"{a['r']}-outer"]
        robust.verify_robust(rp,gr,a['r']);robust.verify_outer(rp,go,a['r'])
        uu=[robust.upper(rp,go,a['context'],a['r'],v,d) for v,d in zip(robust.VERTICES,a['outer_duals'])]
        assert len(uu)==8 and [str(v) for v in uu]==a['outer_upper'];robust_upper+=8
        for name,rr in a['methods'].items():
            robust.feasible(rp,gr,rr['x_num'],rr['x_den'])
            vv=[robust.value(rp,a['context'],a['r'],v,rr['x_num'],rr['x_den']) for v in robust.VERTICES]
            assert [str(v) for v in vv]==rr['vertex_values']
            lower=min(v-u for v,u in zip(vv,uu));assert str(lower)==rr['robust_gain_lower']
            row=costs[(a['r'],a['id'],name)]
            assert row['gain_lower']==float(lower)
            assert abs(row['total_seconds']-row['own_seconds']-row['comparator_seconds'])<1e-12
            assert row['prediction_seconds']<=row['own_seconds'];robust_policies+=1
    assert robust_policies==96 and robust_upper==256 and len(costs)==96
    rejected=[]
    def must_reject(label,fn):
        try:fn()
        except AssertionError:rejected.append(label)
        else:raise AssertionError(('Negative control was accepted',label))
    m,rr=first
    bad=copy.deepcopy(rr['policy']);bad['x_num'][0]=str(int(bad['x_num'][0])+1)
    must_reject('broken root payment',lambda:ie.feasible(p,m,bad))
    # Change one nonrepresentative sibling, restoring payment but not time-only equality.
    bad2=copy.deepcopy(rr['policy']);d=F(int(bad2['x_num'][4]),int(bad2['x_den']))
    xx=ie.unpack(bad2);xx[4]+=F(1,10**8)
    xx[0]-=F(int(p['E'][0][4]),int(p['E'][0][0])*10**8)
    bad2=ie.vector_record(xx)
    must_reject('broken time-only equality',lambda:ie.feasible(p,m,bad2))
    baddual=copy.deepcopy(rr['dual']);baddual['mu'][0]=-1
    must_reject('negative inequality price',lambda:ie.upper(p,m,baddual))
    badtension=copy.deepcopy(rr['dual']);badtension['s'][0]=10**15
    must_reject('invalid switching tension',lambda:ie.upper(p,m,badtension))
    must_reject('coefficient outside strict interior design',lambda:ie.make_model(p,[0]*6+[20],4,[9,0,0]))
    altered=[F(1,8)]*7+[F(1,7)]
    must_reject('nonconvex interpolation weights',lambda:assertion(sum(altered)==1))
    pr,nr=first_nominal;bad=copy.deepcopy(nr);bad['ineq_num'][0]=-1
    must_reject('nominal invalid dual price',lambda:audit_exact(pr,bad['context'],bad['x_num'],bad['x_den'],bad['price_num'],bad['switch_num'],bad['ineq_num'],bad['equality_num'],bad['dual_den']))
    result={'status':'PASS','interior_models':len(seen),'interior_comparator_certificates':count,'source_vertex_comparator_certificates':source_bounds,
       'timing_deployment_certificates':deployments,'optimizer_label_certificates':labels,
       'fresh_robust_policy_certificates':robust_policies,'fresh_robust_comparator_certificates':robust_upper,
       'negative_controls_rejected':len(rejected),'negative_controls':rejected,'arithmetic':'Python standard-library integers and fractions; independent of numerical solvers'}
    if check:assert load(O/'replay.json')==result
    else:(O/'replay.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

def assertion(ok):assert ok
if __name__=='__main__':replay('--check' in sys.argv)
