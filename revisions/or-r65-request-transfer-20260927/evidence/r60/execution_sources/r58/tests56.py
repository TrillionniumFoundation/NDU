"""Seeded exact regressions; every count is derived from completed checks."""
from pathlib import Path
from itertools import combinations
import random,time,copy,json
from rational import F,qstr,write,bits,digest
from cases56 import synthetic
from price_path import Model,spec_for,normalize,allocate,solve as price_solve
from deficit import solve,max_convolution
from compression import compress
from check_deficit import verify
from check_price import verify as verify_price
from enumeration import solve as enumerate_books
from check_enumeration import verify as verify_enum
HERE=Path(__file__).resolve().parent;OUT=HERE.parent/'results';OUT.mkdir(exist_ok=True)

def main():
    started=time.perf_counter();records=[];checks={};rng=random.Random(560056)
    for j in range(200):
        Q=rng.randrange(2,50);L=rng.randrange(1,Q+1)
        row=[None if rng.random()<.4 else F(rng.randrange(-50,50)) for _ in range(Q)]
        slopes=sorted([rng.randrange(-10,10) for _ in range(L-1)],reverse=True);g=[F(rng.randrange(-10,10))]
        for s in slopes:g.append(g[-1]+s)
        actual,ptr,cnt=max_convolution(row,g)
        ref=[];rp=[]
        for s in range(Q):
            items=[(row[z]+g[s-z],-z) for z in range(max(0,s-L+1),s+1) if row[z] is not None]
            best=max(items) if items else None;ref.append(None if best is None else best[0]);rp.append(None if best is None else -best[1])
        if actual!=ref or ptr!=rp:raise ArithmeticError('Convolution with holes disagrees')
    checks['convolution_holes']=200
    for ix in range(36):
        k=2+ix%4;n=4+ix%3;m=1+ix%min(3,n)
        spec=synthetic(k,n,m,560100+ix,hetero=bool(ix%2))
        dp=solve(spec,epsilon=F(1,8));cv=verify(dp['certificate'],digest(spec))
        ref=enumerate_books(spec);verify_enum(ref['certificate'],digest(spec))
        if not dp['lower']<=ref['lower']<=dp['upper']:raise ArithmeticError('Additive interval misses exact optimum')
        pp=price_solve(spec,seconds=10,max_nodes=4096);verify_price(pp['certificate'],digest(spec))
        if pp['gap'] or pp['lower']!=ref['lower']:raise ArithmeticError('Exact price regression disagrees')
        records.append({'kind':'general','index':ix,'instance_sha256':digest(spec),'spec':spec,'exact':ref['lower'],'dp_width':dp['gap'],'states':dp['allocated_states'],'price_nodes':pp['nodes'],'verification':cv})
    checks['general_models']=36
    for ix in range(36):
        spec=synthetic(2+ix%4,4+ix%3,1+ix%3,560200+ix,hetero=True,zero=True,H=8)
        dp=solve(spec,exact_lattice=True);verify(dp['certificate'],digest(spec));ref=enumerate_books(spec)
        if dp['gap'] or dp['lower']!=ref['lower']:raise ArithmeticError('Lattice exactness failed')
        records.append({'kind':'lattice','index':ix,'spec':spec,'instance_sha256':digest(spec),'value':dp['lower'],'grid':dp['grid_points'],'denominator_bits':dp['denominator_bits']})
    checks['lattice_models']=36
    for ix in range(36):
        spec=synthetic(3+ix%4,5+ix%3,5+ix%3,560300+ix,hetero=False,cap_count=1+ix%3)
        d,a,rho,B,m=normalize(spec);book=tuple(a);pol=allocate(d,book,B,dict(zip(a,rho)));co=compress(spec,pol)
        from check_price import check_policy
        from rational import encode
        check_policy(spec,encode(co['policy']))
        ref=enumerate_books(spec);optco=compress(spec,ref['certificate']['policy'])
        if optco['policy']['value']!=ref['lower']:raise ArithmeticError('Optimal compression changes value')
        records.append({'kind':'compression','index':ix,'spec':spec,'before_commands':len(book),'after_commands':len(co['policy']['book']),'distinct_caps':co['distinct_caps'],'optimum':ref['lower']})
    checks['cap_compression_models']=36
    for q in [1,2,3,4]:
        a=tuple(x for l in range(1,q+1) for x in (F(3*l-2,3*q),F(3*l-1,3*q)))
        b=tuple((a[2*l]+a[2*l+1])/2 for l in range(q));tau=a[1::2]
        d=Model.make(b,[F(1,q)]*q,[0]*q,tau,2,1);spec=spec_for(d,a,[0]*len(a),d.cap_total,2*q)
        ref=enumerate_books(spec);best=ref['lower'];smaller=[]
        for row in ref['certificate']['books']:
            if len(row['indices'])<2*q:smaller.append(F(row['upper']))
        if not best>max(smaller):raise ArithmeticError('2q tightness construction failed')
        records.append({'kind':'tightness','q':q,'spec':spec,'optimal_value':best,'best_smaller':max(smaller),'strict_gap':best-max(smaller)})
    checks['tight_constructions']=4
    huge=F(2**20000+1,2**20001+7)
    if F(qstr(huge))!=huge:raise ArithmeticError('Hexadecimal roundtrip failed')
    # A full certificate, not just a wire-format unit test, contains >4300 decimal digits.
    spec=synthetic(k=2,n=3,m=2,seed=560999,zero=True);spec['charges'][1]=qstr(F(1,2**20000+1))
    pp=price_solve(spec,seconds=10);verify_price(pp['certificate'],digest(spec));checks['hex_bits']=bits(pp['certificate'])
    from deficit import StateLimit
    try:solve(synthetic(2,3,2,5601,zero=True,H=2**20000),exact_lattice=True)
    except StateLimit as exc:
        checks['oversized_resource_state_bits']=exc.requested.bit_length()
        if exc.requested.bit_length()<19000:raise ArithmeticError('Expected genuinely oversized state count')
    else:raise ArithmeticError('Oversized lattice did not reject before allocation')
    tamper=[];base=solve(synthetic(k=3,n=5,m=2),epsilon='1/8')['certificate']
    for kind in ['upper','target','promise','eta','missing_anchor','path','hash']:
        c=copy.deepcopy(base)
        if kind=='upper':c['upper']=qstr(-100)
        elif kind=='target':c['policy']['targets'][0]=qstr(1)
        elif kind=='promise':c['spec']['promise']=qstr(F(c['spec']['promise'])+F(1,10))
        elif kind=='eta':c['eta']=qstr(F(c['eta'])/2)
        elif kind=='missing_anchor':c['states'][0][0][0]=None
        elif kind=='path':c['repaired_deficits'][0]=qstr(-1)
        elif kind=='hash':c['instance_sha256']='0'*64
        try:verify(c)
        except (ValueError,ArithmeticError):tamper.append(kind)
        else:raise ArithmeticError('Tampered certificate accepted: '+kind)
    checks['rejected_corruptions']=tamper
    write(OUT/'REGRESSION.json',{'status':'PASS','checks':checks,'seconds':time.perf_counter()-started,'records':records})
    print(json.dumps(checks,indent=2));print('seconds',time.perf_counter()-started)
if __name__=='__main__':main()
