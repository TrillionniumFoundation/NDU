"""Independent certificate checker; no optimizer imports."""
from itertools import combinations
import time
from rational import F,qstr,digest
from check_price import model,check_policy,price_bound,require

def verify(cert,expected_sha256=None):
    started=time.perf_counter();spec=cert['spec'];require(cert['schema']=='NDU-enumeration-v1-hex','Unknown schema')
    require(digest(spec)==cert['instance_sha256'] and (expected_sha256 is None or digest(spec)==expected_sha256),'Wrong instance')
    w,b,g,t,r,q,a,rho,B,m=model(spec);L=check_policy(spec,cert['policy']);U=F(cert['upper']);seen=set();ub=None;cache={}
    if cert['complete']:
        for row in cert['books']:
            ids=tuple(row['indices']);require(ids==tuple(sorted(set(ids))) and ids not in seen and ids and len(ids)<=m,'Repeated or invalid book')
            require(all(type(i)==int and 0<=i<len(a) for i in ids) and a[ids[0]]<=min(B,min(b)),'Book outside feasible universe')
            seen.add(ids);req=frozenset(ids);ban=frozenset(range(len(a)))-req
            upper=price_bound(spec,F(row['price']),req,ban,cache)
            require(upper==F(row['upper']),'Invalid book support price')
            ub=upper if ub is None else max(ub,upper)
        expected={ids for ell in range(1,m+1) for ids in combinations(range(len(a)),ell) if a[ids[0]]<=min(B,min(b))}
        require(seen==expected and ub==U==L,'Incomplete exact enumeration cover')
    else:
        require(U==sum(p*(rr-qq/2) for p,rr,qq in zip(w,r,q)),'Invalid interrupted enumeration fallback')
    require(L==F(cert['lower']) and L<=U,'Invalid interval')
    return {'status':'PASS','lower':qstr(L),'upper':qstr(U),'gap':qstr(U-L),'seconds':time.perf_counter()-started,'books_checked':len(seen),'instance_sha256':digest(spec)}
