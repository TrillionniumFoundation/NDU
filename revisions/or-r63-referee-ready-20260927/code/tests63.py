"""External-input binding regression and proof-mutation tests."""
from pathlib import Path
import copy, json
from rational import F, qstr, write
from binding63 import verify_bound
from support63 import design
from price_path import solve

def run():
    case=design()[5];spec=case['spec'];cert=solve(spec,F('1/1000'),seconds=2,max_nodes=100000)['certificate']
    verify_bound(cert,spec)
    decimal=copy.deepcopy(spec)
    for k,v in decimal['model'].items():decimal['model'][k]=[str(F(x)) for x in v]
    for k in ('catalog','charges'):decimal[k]=[str(F(x)) for x in decimal[k]]
    decimal['promise']=str(F(decimal['promise']))
    answer=verify_bound(cert,decimal)
    assert not answer['binding']['byte_identical']
    count=0
    def reject(c,s):
        nonlocal count
        try:verify_bound(c,s)
        except (ValueError,KeyError,AssertionError,TypeError):count+=1;return
        raise AssertionError('Mutation accepted')
    for k in sorted(spec['model']):
        x=copy.deepcopy(spec);i=1;x['model'][k][i]=qstr(F(x['model'][k][i])+F(1,1000));reject(cert,x)
    for k in ('catalog','charges'):
        x=copy.deepcopy(spec);x[k][1]=qstr(F(x[k][1])+F(1,1000));reject(cert,x)
    x=copy.deepcopy(spec);x['promise']=qstr(F(x['promise'])+F(1,1000));reject(cert,x)
    x=copy.deepcopy(spec);x['budget']+=1;reject(cert,x)
    for key in spec:
        x=copy.deepcopy(spec);del x[key];reject(cert,x)
    x=copy.deepcopy(spec);x['extra']='ignored?';reject(cert,x)
    x=copy.deepcopy(spec);x['model']['extra']=[0];reject(cert,x)
    c=copy.deepcopy(cert);c['policy']['value']=qstr(F(c['policy']['value'])+1);reject(c,spec)
    c=copy.deepcopy(cert);c['policy']['targets'][0]=qstr(F(c['policy']['targets'][0])+F(1,1000));reject(c,spec)
    c=copy.deepcopy(cert);c['instance_sha256']='0'*64
    # Historical price certificates use spec_sha256; corrupt the actually present digest.
    for key in ('spec_sha256','instance_sha256'):
        if key in cert:
            c=copy.deepcopy(cert);c[key]='0'*64;reject(c,spec)
    c=copy.deepcopy(cert);c['hybrid_probe_certificate']=copy.deepcopy(cert);verify_bound(c,spec)
    c['hybrid_probe_certificate']['spec']['budget']+=1;reject(c,spec)
    out={'status':'PASS','rejected_mutations':count,'equivalent_encodings_accepted':2,
         'nested_probe_binding':'PASS','external_budget_retained':'PASS'}
    write(Path(__file__).resolve().parents[1]/'results/BINDING_TESTS63.json',out);print(out)
if __name__=='__main__':run()
