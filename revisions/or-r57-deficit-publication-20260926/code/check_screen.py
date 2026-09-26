"""Independent certificate checker; no optimizer imports."""
import time
from rational import F,qstr,digest
from check_price import model,check_policy,price_bound,verify as price_verify,require

def verify(cert,expected_sha256=None):
    begin=time.perf_counter();require(cert['schema']=='NDU-screen-v1-hex','Unknown screen schema')
    spec=cert['spec'];require(digest(spec)==cert['instance_sha256'] and (expected_sha256 is None or digest(spec)==expected_sha256),'Wrong original model')
    w,b,g,t,r,q,a,rho,B,m=model(spec);seed=check_policy(spec,cert['seed_policy']);removed=set();cache={}
    for proof in cert['fixings']:
        i=proof['index'];require(type(i)==int and 0<=i<len(a) and i not in removed,'Invalid fixing index')
        U=price_bound(spec,F(proof['price']),frozenset({i}),frozenset(),cache)
        require((U is None and proof['upper'] is None) or (U is not None and U==F(proof['upper']) and U<seed),'Unsafe forced-command fixing');removed.add(i)
    keep=[i for i in range(len(a)) if i not in removed];require(keep==cert['kept_indices'],'Reduced catalog mismatch')
    reduced=dict(spec,catalog=[spec['catalog'][i] for i in keep],charges=[spec['charges'][i] for i in keep]);sub=cert['reduced_certificate']
    require(sub['spec']==reduced,'Reduced model mismatch');check=price_verify(sub,digest(reduced));L=check_policy(spec,cert['policy']);U=F(check['upper'])
    require(F(cert['upper'])==U and F(cert['lower'])==L and L<=U,'Incorrect transferred interval')
    return dict(status='PASS',lower=qstr(L),upper=qstr(U),gap=qstr(U-L),seconds=time.perf_counter()-begin,fixings_checked=len(removed),reduced_check=check,instance_sha256=digest(spec))
