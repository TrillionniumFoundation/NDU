"""Independent R22 evidence replay. Run with python -S; standard library only."""
from pathlib import Path
from fractions import Fraction as F
from functools import reduce
from math import lcm,sqrt,log,nextafter,inf
import json,gzip,copy,statistics,sys
from certificate import audit_exact,decompose
R=Path(__file__).resolve().parent;O=R/'results'
def audit(p,x):
    return audit_exact(p,x['context'],x['x_num'],x['x_den'],x['price_num'],x['switch_num'],x['ineq_num'],x['equality_num'],x['dual_den'])
def stream(name):
    with gzip.open(O/name,'rt') as f:
        for line in f:yield json.loads(line)
def run(check_only=False):
    p=json.loads((O/'primitives.json').read_text());pt=json.loads((O/'time_primitives.json').read_text())
    counts={'matched':0,'validation':0,'scaling':0};first=None
    rows={x['id']:x for x in json.loads((O/'matched_rows.json').read_text())}
    decomps={x['id']:x for x in json.loads((O/'decompositions.json').read_text())};dc=0
    for x in stream('matched_certificates.jsonl.gz'):
        aa=[audit(p,x[k]) for k in ['before','after','final']];counts['matched']+=3
        if first is None:first=x['before']
        for key in ['x_num','x_den','switch_num','ineq_num']:assert x['before'][key]==x['after'][key]
        assert F(aa[1]['upper_exact'])<=F(aa[0]['upper_exact'])
        assert aa[0]['gain_exact']==aa[1]['gain_exact']
        assert F(aa[2]['upper_exact'])-F(aa[2]['gain_exact'])<=F(str(x['tolerance']))
        rr=rows.pop(x['id']);assert abs(rr['final_gap']-aa[2]['gap'])<1e-12
        if x['id'] in decomps:
            for stage in ['before','after']:
                assert decompose(p,x[stage])==decomps[x['id']][stage];dc+=1
    assert not rows and counts['matched']==15360 and dc==320
    vs=json.loads((O/'validation_summary.json').read_text());vr={(x['domain'],x['id'],x['method']):x for x in json.loads((O/'validation_rows.json').read_text())}
    B={};values={};contexts={};time_example=None;corners={}
    for x in stream('validation_certificates.jsonl.gz'):
        domain=x['domain']
        if x['kind']=='corner':
            a=audit(p,x['record']);counts['validation']+=1
            B[domain]=max(B.get(domain,F(0)),F(a['upper_exact']));corners.setdefault(domain,set()).add(tuple(x['record']['context']));continue
        ref=audit(p,x['reference']);tc=audit(pt,x['comparator']);counts['validation']+=2
        contexts.setdefault(domain,[]).append(tuple(x['reference']['context']))
        if time_example is None:time_example=x['comparator']
        for method,z in x['methods'].items():
            a=audit(p,z['before']);b=audit(p,z['after']);counts['validation']+=2
            assert F(b['upper_exact'])<=F(a['upper_exact'])
            for key in ['x_num','x_den','switch_num','ineq_num']:assert z['before'][key]==z['after'][key]
            chosen=max(F(b['gain_exact']),F(tc['gain_exact']));w=chosen-F(tc['upper_exact'])
            assert F(0)<=chosen<=B[domain]
            rr=vr.pop((domain,x['id'],method));assert abs(float(w)-rr['restricted_gain_lower'])<1e-12
            assert abs(float(F(ref['upper_exact'])-chosen)-rr['regret_upper'])<1e-12
            values.setdefault((domain,method),[]).append(float(w))
    assert not vr and counts['validation']==15616
    assert len(contexts['iid'])==2048 and len(contexts['shift'])==512
    for domain in ['iid','shift']:
        assert len(corners[domain])==128
        assert F(vs['bounds'][domain]['upper_exact'])==B[domain]
    for row in vs['summary']:
        domain=row['domain'];n=row['n'];bound=nextafter(float(B[domain]),inf)
        lower=statistics.mean(values[domain,row['method']])-2*bound*sqrt(log(4/.05)/(2*n))
        assert abs(lower-row['expected_restricted_gain_lower'])<1e-12
    with gzip.open(O/'scaling_primitives.json.gz','rt') as f:ps=json.load(f)
    sr=json.loads((O/'scaling_rows.json').read_text());lookup={(x['instance'],x['context'],x['method'],x['tol']):x for x in sr if x['status']=='PASS'}
    labels=0
    for x in stream('scaling_certificates.jsonl.gz'):
        a=audit(ps[x['instance']],x['record']);counts['scaling']+=1
        if x['kind']=='label':
            labels+=1;assert F(a['upper_exact'])-F(a['gain_exact'])<=F(1,100000)
        else:
            rr=lookup.pop((x['instance'],x['context'],x['method'],x['tol']))
            assert F(a['upper_exact'])-F(a['gain_exact'])<=F(str(x['tol']))
    assert not lookup and labels==640 and len(sr)==800
    # Independent negative controls for dual and primal claims.
    negative=0
    for kind in ['mu','tension','box']:
        z=copy.deepcopy(first)
        if kind=='mu':z['ineq_num'][0]=-1
        elif kind=='tension':z['switch_num'][0]=z['dual_den']*z['context'][-1]*p['knum'][0]//512+1
        else:z['x_num'][0]=str(2*int(z['x_den']))
        try:audit(p,z)
        except AssertionError:negative+=1
        else:raise AssertionError('negative control accepted: '+kind)
    # A strict time anchor, perturbed across siblings, remains fully accepted
    # but is not a time-only amendment. The restricted verifier must reject it.
    sv=p['services'];nodes=p['nodes'];xx=[F(-1) if j else F(0) for j in range(nodes) for a in range(sv)]
    for a in range(sv):xx[a]=-sum((p['c'][j*sv+a]*xx[j*sv+a] for j in range(1,nodes)),F(0))/p['c'][a]
    factor=F(1,10000);xx=[factor*v for v in xx]
    xx[sv]+=F(1,10**12*p['c'][sv]);xx[2*sv]-=F(1,10**12*p['c'][2*sv])
    den=reduce(lcm,(v.denominator for v in xx),1);z=copy.deepcopy(time_example)
    z['x_num']=[str(int(v*den)) for v in xx];z['x_den']=str(den)
    full=copy.deepcopy(z);full['equality_num']=full['equality_num'][:sv]
    audit(p,full)
    try:audit(pt,z)
    except AssertionError as e:
        assert 'additional equality' in str(e);negative+=1
    else:raise AssertionError('non-time amendment accepted by restricted verifier')
    training=json.loads((R.parent/'or-r16-20260922/results/training.json').read_text());oldtrain={tuple(c) for cohort in training for c in cohort['contexts']}
    out={'status':'PASS','independent_policy_replays':sum(counts.values()),'groups':counts,'component_identities':dc,
      'negative_controls_rejected':negative,'scaling_labels':labels,'scaling_target_failures_retained':sum(x['status']!='PASS' for x in sr),
      'validation_unique_contexts':{k:len(set(v)) for k,v in contexts.items()},'validation_training_context_overlap':{k:len(set(v)&oldtrain) for k,v in contexts.items()},
      'statistical_target':'Fixed deterministic ensembles with fully reset solver state, restricted optimum, two fresh context populations; four simultaneous lower bounds independently reconstructed.'}
    if check_only:assert json.loads((O/'replay.json').read_text())==out
    else:(O/'replay.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':run('--check' in sys.argv)
