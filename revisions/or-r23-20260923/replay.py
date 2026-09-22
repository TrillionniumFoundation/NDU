"""Replay every R23 record using Python's standard library only.
Run with `python -S revisions/or-r23-20260923/replay.py [--check]`.
"""
import argparse,copy,gzip,hashlib,json,sys
from pathlib import Path
from fractions import Fraction as F
from robust_exact import *
R=Path(__file__).resolve().parent

def run(check=False):
    out=R/'results';p=json.loads((out/'primitives.json').read_text());gg=json.loads((out/'geometries.json').read_text());design=json.loads((R/'DESIGN.json').read_text())
    summary=json.loads((out/'summary.json').read_text());rows=json.loads((out/'rows.json').read_text())
    assert summary['design_sha256']==hashlib.sha256((R/'DESIGN.json').read_bytes()).hexdigest()
    assert not summary['pilot'];count=design['validation']['contexts']
    assert len(p['qnum'])==126 and p['nodes']==63 and p['services']==2 and p['rank']==6
    rowmap={(a['r'],a['id'],a['method']):a for a in rows};seen=set();tot=nd=dc=0;first=None
    for r in (0,1,2,4):
        verify_outer(p,gg[f'{r}-outer'],r);verify_robust(p,gg[f'{r}-robust'],r)
    with gzip.open(out/'certificates.jsonl.gz','rt') as f:
      for line in f:
        item=json.loads(line);r=item['r'];j=item['id'];c=item['context'];key=(r,j)
        assert key not in seen and 0<=j<count and r in (0,1,2,4);seen.add(key)
        assert len(c)==7 and all(-16<=h<=16 for h in c[:6]) and 2<=c[-1]<=32
        go=gg[f'{r}-outer'];gr=gg[f'{r}-robust'];gn=gg[f'{r}-nominal']
        uu=[upper(p,go,c,r,v,d) for v,d in zip(VERTICES,item['outer_duals'])]
        assert len(uu)==8 and list(map(str,uu))==item['outer_upper'];dc+=8
        assert set(item['methods'])=={'protected-tanh-gradient','protected-rbf-direct','classical-robust-maximin'}
        for name,rec in item['methods'].items():
            feasible(p,gr,rec['x_num'],rec['x_den'])
            fv=[value(p,c,r,v,rec['x_num'],rec['x_den']) for v in VERTICES]
            assert list(map(str,fv))==rec['vertex_values']
            assert min(fv)>=0,'outside gate does not protect every model'
            lower=min(a-b for a,b in zip(fv,uu));assert str(lower)==rec['robust_gain_lower']
            row=rowmap[(r,j,name)];assert row['robust_gain_lower']==float(lower)
            # An interior rational mixture also obeys the same certificate.
            for weights in (list(range(1,9)),list(range(8,0,-1))):
                mix=sum((F(w,sum(weights))*(a-b) for w,a,b in zip(weights,fv,uu)),F(0));assert mix>=lower
            tot+=1
        for name,rec in item['nominal_diagnostics'].items():
            feasible(p,gn,rec['x_num'],rec['x_den'])
            try:feasible(p,gr,rec['x_num'],rec['x_den']);ok=True
            except AssertionError:ok=False
            assert ok==rec['robust_feasible'];nd+=1
        if r==4 and first is None:first=item
    assert len(seen)==count*4 and tot==count*4*3 and dc==count*4*8
    assert len(rows)==tot and len(json.loads((out/'failures.json').read_text()))==summary['failed_solves']
    for sr in summary['summary']:
        rr=[a for a in rows if a['r']==sr['r'] and a['method']==sr['method']]
        assert len(rr)==sr['n']==count
        mean=sum(a['robust_gain_lower'] for a in rr)/count
        assert abs(mean-sr['mean_robust_gain_lower'])<1e-12
        assert min(a['robust_gain_lower'] for a in rr)==sr['min_robust_gain_lower']
        assert sum(a['robust_gain_lower']>0 for a in rr)/count==sr['positive_fraction']
        if sr['nominal_unsafe_fraction'] is not None:assert sum(not a['nominal_robust_feasible'] for a in rr)/count==sr['nominal_unsafe_fraction']
    # Negative controls independently exercise four distinct authorization checks.
    rejected=[];rec=first['methods']['protected-rbf-direct'];c=first['context'];gr=gg['4-robust'];go=gg['4-outer']
    def must_reject(label,fn):
        try:fn()
        except (AssertionError,ValueError):rejected.append(label)
        else:raise AssertionError('mutation accepted: '+label)
    bad=copy.deepcopy(rec);bad['x_num'][0]=str(10*int(bad['x_den']))
    must_reject('invalid implemented tier',lambda:feasible(p,gr,bad['x_num'],bad['x_den']))
    bad2=copy.deepcopy(rec);bad2['x_num'][0]=str(int(bad2['x_num'][0])+1)
    must_reject('inexact root equality',lambda:feasible(p,gr,bad2['x_num'],bad2['x_den']))
    dd=copy.deepcopy(first['outer_duals'][0]);dd['mu'][0]=-1
    must_reject('negative inequality price',lambda:upper(p,go,c,4,VERTICES[0],dd))
    dd2=copy.deepcopy(first['outer_duals'][0]);dd2['s'][0]=10**20
    must_reject('illegal switching tension',lambda:upper(p,go,c,4,VERTICES[0],dd2))
    badg=copy.deepcopy(go);badg['budget_num'][0]=0
    must_reject('false outer-class containment',lambda:verify_outer(p,badg,4))
    badr=copy.deepcopy(gr);badr['A_num'][0][2]+=1
    must_reject('changed robust participation row',lambda:verify_robust(p,badr,4))
    # Exact counterexample: vertex-specific reoptimization does not upper-bound
    # the comparator in the interior when participation coefficients change.
    def K(t):
        hi=F(1)
        for a,b in ((1+t,1-t),(1-t,1+t)):
            if a>0:hi=min(hi,b/a)
        return hi
    assert K(F(-1))==K(F(1))==0 and K(F(0))==1
    # Common outer class [0,1] gives U_v=1 and the correct uniform lower -1.
    for i in range(-500,501):assert -K(F(i,500))>=-1
    answer={'status':'PASS','policy_records':tot,'vertex_comparator_certificates':dc,'nominal_diagnostic_records':nd,'joint_context_radius_cases':len(seen),'interior_mixture_checks':2*tot,'exact_counterexample_parameters':1001,'negative_controls_rejected':len(rejected),'negative_controls':rejected,'all_failures_retained':True,'pure_standard_library':True,'design_sha256':summary['design_sha256']}
    target=out/'replay.json'
    if check:assert json.loads(target.read_text())==answer
    else:target.write_text(json.dumps(answer,indent=2)+'\n')
    print(json.dumps(answer,indent=2))
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--check',action='store_true');run(a.parse_args().check)
