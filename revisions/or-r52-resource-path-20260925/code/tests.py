"""Independent regression suite for the R52 identities, grid, and checker."""
from fractions import Fraction as F
from pathlib import Path
from itertools import combinations
import sys,random,time,json,copy,math
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from resource_path import *
from check_resource import convolution,verify

def run():
    start=time.perf_counter();rng=random.Random(52520);identities=0;intervals=0;sample=None
    for case in range(100):
        k=rng.randint(1,6);n=rng.randint(3,8);m=rng.randint(1,min(n,4))
        a=tuple(F(i,n-1) for i in range(n));b=[F(rng.randint(0,10),10) for _ in range(k)]
        raw=[rng.randint(1,5) for _ in b];w=[F(x,sum(raw)) for x in raw]
        g=[F(rng.randint(0,10),3) for _ in b];tau=[min(F(1),x+F(rng.randint(0,5),10)) for x in b]
        data=Instance.make(b,w,g,tau);B=data.cap_total*F(rng.randint(0,10),10)
        rho=tuple(F(rng.randint(0,5),100) for _ in a);opt=None
        for s in range(1,m+1):
            for book in combinations(a,s):
                if book[0]>min(min(b),B):continue
                old=fixed_allocate(data,book,B,dict(zip(a,rho)))['value']
                new=book_resource_value(data,book,B,dict(zip(a,rho)))
                assert old==new,(case,book,old,new);identities+=1
                opt=old if opt is None else max(opt,old)
        ans=solve(data,a,rho,B,m,F(1,10));assert ans['lower']<=opt<=ans['upper']
        verify(ans['certificate']);intervals+=1
        if sample is None and len(ans['certificate']['tables'])>1 and ans['resource_states']>15:sample=ans['certificate']
    rng=random.Random(52521)
    for _ in range(2000):
        n=rng.randint(1,50);m=rng.randint(1,50);lim=rng.randint(0,n+m+2)
        previous=[rng.randint(-1000,1000) for _ in range(n)];kernel=[rng.randint(-100,100)]
        for d in sorted([rng.randint(-100,100) for _ in range(m-1)],reverse=True):kernel.append(kernel[-1]+d)
        exact=brute_convolution(previous,kernel,lim)
        assert max_convolution(previous,kernel,lim)[0]==exact
        assert convolution(previous,kernel,lim)==exact
    # Exact dyadic product, including widths/eta=3, zero widths, and anisotropy.
    dyadic=0
    for width in [F(0),F(1,10),F(1,3),F(1,2),F(1)]:
        for eta in [F(1,3),F(1,7),F(1,16),F(2)]:
            leaves=1
            while width/leaves>eta:leaves*=2
            exponent=0
            while F(2)**exponent<width/eta:exponent+=1
            assert leaves==2**exponent
            assert leaves<=2*max(F(1),width/eta);dyadic+=1
    assert 2**math.ceil(math.log2(3))==4
    assert sample is not None
    mutations=[]
    def add(name,func):
        c=copy.deepcopy(sample);func(c);mutations.append((name,c))
    add('missing anchor',lambda c:c['tables'].pop(next(iter(c['tables']))))
    add('missing Bellman row',lambda c:next(iter(c['tables'].values())).pop(next(iter(next(iter(c['tables'].values()))))))
    add('false upper',lambda c:c.update(upper=str(F(c['upper'])-1)))
    add('false lower',lambda c:c.update(lower=str(F(c['lower'])+1)))
    add('false score',lambda c:c.update(grid_score=str(F(c['grid_score'])+1)))
    add('wrong denominator',lambda c:c.update(denominator=str(int(c['denominator'])+1)))
    add('wrong promise',lambda c:c.update(promise=str(F(c['promise'])/2)))
    add('wrong Lipschitz bound',lambda c:c.update(lipschitz='0'))
    add('false tolerance',lambda c:c.update(epsilon='1/100000000'))
    add('negative service',lambda c:c['policy']['intermediate'].__setitem__(0,'-1'))
    add('false lottery mass',lambda c:c['policy']['lotteries'][0][0].__setitem__(1,'2'))
    add('unsupported schema',lambda c:c.update(schema='unrecognized'))
    rejected=[]
    for name,cert in mutations:
        try:verify(cert)
        except (AssertionError,ValueError,KeyError,IndexError,ZeroDivisionError):rejected.append(name)
        else:raise AssertionError('Accepted corruption '+name)
    out=dict(status='PASS',book_resource_identities=identities,exact_enumeration_intervals=intervals,
             independent_resource_certificates=intervals,convolution_cross_checks=2000,dyadic_counts=dyadic,
             rejected_corruptions=rejected,seconds=time.perf_counter()-start)
    (HERE.parent/'results').mkdir(exist_ok=True)
    (HERE.parent/'results/tests.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2));return out
if __name__=='__main__':run()
