"""R64 referee witnesses and request/transfer contract regressions."""
from copy import deepcopy
from pathlib import Path
import argparse,json,subprocess,sys,time
from rational import F,encode,digest,write
from price_path import Model,spec_for
from robust61 import solve
from check_price import check_policy
from binding65 import make_request,bind_legacy,verify_request,ROBUST,TARIFF
from produce65 import produce
R=Path(__file__).resolve().parents[1]


def run(output):
    start=time.perf_counter();output=output.resolve();output.mkdir(parents=True,exist_ok=True)
    model=Model.make([1,1],[F(1,2)]*2,[0,0],[1,1],1,0)
    spec=spec_for(model,[0,F(1,2),1],[0,F(1,100),F(2,100)],F(1,4),3)
    req=make_request(spec,F(1,10),ROBUST,3)
    valid=solve(spec,F(1,10),3)['certificate'];envelope=bind_legacy(valid,req)
    ans=verify_request(envelope,req);assert F(ans['lower'])==F(6,25)
    assert ans['selected_exception_budget']==0 and ans['request_bound']
    strict=solve(spec,F(1,200),3)['certificate'];assert strict['selected_exception_budget']==2
    degraded=deepcopy(valid);p=degraded['policy']
    p['intermediate'][0]='1/50';p['lotteries'][0]=[['0','1/25'],['1/2','24/25']]
    p['gross']='6/25';p['value']='23/100';degraded['lower']='23/100'
    assert check_policy(spec,p)==F(23,100) # feasible, not random corruption
    witness=dict(spec=spec,external_request=req,strict_certificate=strict,degraded_certificate=degraded)
    write(output/'REFEREE_WITNESSES65.json',witness)
    script="""import sys,json
sys.path.insert(0,sys.argv[1])
from binding63 import verify_bound
from check_robust61 import verify
w=json.load(open(sys.argv[2]))
print(json.dumps({'strict_tolerance':verify_bound(w['strict_certificate'],w['spec'])['status'],
                 'degraded_policy':verify(w['degraded_certificate'])['status']}))
"""
    old=json.loads(subprocess.check_output([sys.executable,'-c',script,str(R/'archive/r64/code'),
                      str(output/'REFEREE_WITNESSES65.json')],cwd='/tmp',text=True))
    assert old=={'strict_tolerance':'PASS','degraded_policy':'PASS'},old
    bad=[]
    def add(name,e,r=None):bad.append((name,e,deepcopy(req if r is None else r)))
    # Coordinated wrapper: external physical input and wrapper digest agree, but
    # the proof was actually generated for a stricter projection tolerance.
    add('stricter-self-declared-tolerance',bind_legacy(strict,req))
    add('feasible-degraded-same-book-policy',bind_legacy(degraded,req))
    e=deepcopy(envelope);e['request']['epsilon']='1/200';e['request_sha256']=digest(e['request']);add('coordinated-request-and-digest',e)
    e=deepcopy(envelope);e['certificate']['surrogate_certificate']['configured_guard']=4;add('guard-larger-than-external',e)
    e=deepcopy(envelope);e['certificate']['surrogate_certificate']['configured_guard']=True;add('boolean-proof-guard',e)
    e=deepcopy(envelope);e['certificate']['surrogate_certificate']['modal_tie_rule']='largest rational fee';add('false-modal-tie-rule',e)
    e=deepcopy(envelope);del e['certificate']['surrogate_certificate']['modal_tie_rule'];add('missing-modal-tie-rule',e)
    e=deepcopy(envelope);e['certificate']['policy']['gross']='7/25';add('false-outer-gross-metadata',e)
    e=deepcopy(envelope);e['certificate']['surrogate_certificate']['policy']['gross']='7/25';add('false-inner-gross-metadata',e)
    e=deepcopy(envelope);e['request_sha256']='0'*64;add('stale-request-digest',e)
    e=deepcopy(envelope);e['request']['extra']='unrecognized';add('unknown-request-field',e)
    e=deepcopy(envelope);del e['request']['epsilon'];add('missing-request-tolerance',e)
    e=deepcopy(envelope);e['request']['certificate_class']=TARIFF;e['request_sha256']=digest(e['request']);add('wrong-request-class',e)
    e=deepcopy(envelope);e['certificate']['schema']=TARIFF;add('wrong-proof-class',e)
    for field,value in [('epsilon',True),('epsilon',0.1),('epsilon','-1'),('configured_guard',True),('configured_guard',-1),('configured_guard',None)]:
        r=deepcopy(req);r[field]=value;add('invalid-external-'+field+'-'+repr(value),envelope,r)
    r=deepcopy(req);r['spec']['promise']='1/3';add('changed-external-promise',envelope,r)
    r=deepcopy(req);r['spec']['budget']=4;add('changed-external-command-allowance',envelope,r)
    r=deepcopy(req);r['configured_guard']=4;add('changed-external-guard',envelope,r)
    e=deepcopy(envelope);e['extra']='unknown';add('unknown-envelope-field',e)
    rejected=[]
    for name,e,r in bad:
        try:verify_request(e,r)
        except (ValueError,KeyError,TypeError,ArithmeticError) as exc:rejected.append(dict(name=name,reason=str(exc)))
        else:raise AssertionError('Accepted '+name)
    # Different physical tie solution: interchange identical histories. Gross
    # payoff and book are equal, so this is intentionally accepted.
    tie=deepcopy(valid)
    for key in ('intermediate','targets','lotteries'):tie['policy'][key].reverse()
    assert tie['policy']['targets']!=valid['policy']['targets']
    verify_request(bind_legacy(tie,req),req)
    # Equivalent rational encodings bind to one canonical request hash.
    equivalent=deepcopy(req);equivalent['epsilon']='2/20'
    for key,vec in equivalent['spec']['model'].items():equivalent['spec']['model'][key]=[str(F(x)) for x in vec]
    equivalent['spec']['catalog']=[str(F(x)) for x in equivalent['spec']['catalog']]
    equivalent['spec']['charges']=[str(F(x)) for x in equivalent['spec']['charges']]
    equivalent['spec']['promise']='2/8'
    assert verify_request(envelope,equivalent)['request_binding']['canonical_request_sha256']==digest(req)
    zero=make_request(spec,0,ROBUST,3);verify_request(produce(zero),zero)
    nonuniform=make_request(spec,0,TARIFF,3);verify_request(produce(nonuniform),nonuniform)
    e=produce(nonuniform);e['certificate']['configured_guard']=0
    add('guard-smaller-than-exception-count',e,nonuniform)
    try:verify_request(e,nonuniform)
    except ValueError as exc:rejected.append(dict(name='guard-smaller-than-exception-count',reason=str(exc)))
    else:raise AssertionError('Guard mutation accepted')
    # Guard zero is valid for a uniform surrogate despite nonuniform original fees.
    uniform=make_request(spec,F(1,10),ROBUST,0);verify_request(produce(uniform),uniform)
    count=6
    for n in range(2,7):
        for seed in range(4):
            fees=[F((i*i+3*seed*i)%11,100) for i in range(n)]
            s=spec_for(model,[F(i,n-1) for i in range(n)],fees,F(1,4),min(n,4))
            for eps in (F(0),F(1,100),F(1,10)):
                q=make_request(s,eps,ROBUST,n);verify_request(produce(q),q);count+=1
    closure="import sys;sys.path.insert(0,sys.argv[1]);import binding65;assert not {'tariff60','robust61','price_path','produce65'} & set(sys.modules)"
    subprocess.run([sys.executable,'-c',closure,str(R/'code')],cwd='/tmp',check=True)
    result=dict(status='PASS',legacy_witnesses_accepted=old,coordinated_witnesses_rejected=2,
        rejected_adversaries=len(rejected),rejections=rejected,positive_request_checks=count,
        equal_gross_different_policy_accepted=True,equivalent_rational_request_accepted=True,
        optimizer_free_request_checker=True,seconds=time.perf_counter()-start,
        scope='Finite exact regression; not an editorial acceptance or timing claim')
    write(output/'REQUEST_TESTS65.json',result)
    write(output/'REQUEST_ADVERSARIES65.json',{'cases':[dict(name=n,envelope=e,external_request=r) for n,e,r in bad]})
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=R/'results/r65');a=p.parse_args()
    print(json.dumps(run(a.output),indent=2))
