"""Independent trimmed-fee projection checker: no optimizer imports.

Direct absolute sums deliberately differ from the optimizer's prefix-sum
implementation. At budget d there are d+1 retained windows, each of length
N-d. Verifying d and d-1 costs O(N log N + (d+1)N) rational operations.
Minimality is for total L1 distortion, not interval width or solver runtime.
"""
from rational import F
from check_price import require


def optimum(fees, d):
    n=len(fees)
    require(type(d) is int and 0<=d<n,'Invalid projection allowance')
    order=sorted(range(n),key=lambda i:(fees[i],i))
    length=n-d
    best=None
    for left in range(d+1):
        kept=order[left:left+length]
        center=fees[kept[(length-1)//2]]
        cost=sum((abs(fees[i]-center) for i in kept),F(0))
        key=(cost,center,left)
        if best is None or key<best[0]:best=(key,kept)
    (cost,center,_),kept=best
    projected=list(fees)
    for i in kept:projected[i]=center
    return dict(standard_fee=center,charges=projected,
        exceptions=[i for i,x in enumerate(projected) if x!=center],
        absolute_deviation=cost,retained_window=kept)


def verify_projection(cert, fees, surrogate_fees):
    fees=list(map(F,fees)); n=len(fees)
    require(len(surrogate_fees)==n,'Projection charge length mismatch')
    eps=F(cert['epsilon']);require(eps>=0,'Negative projection tolerance')
    d=cert['selected_exception_budget']
    expected=optimum(fees,d)
    given=cert['projection']
    require(type(given) is dict and set(given)==set(expected),'Projection schema mismatch')
    for key in ('retained_window','exceptions'):
        require(type(given[key]) is list and all(type(i) is int for i in given[key]),'Invalid projection index')
        require(given[key]==expected[key],'Nonoptimal or nondeterministic projection '+key)
    require(F(given['standard_fee'])==expected['standard_fee'],'Incorrect projection median')
    require(F(given['absolute_deviation'])==expected['absolute_deviation'],'Incorrect minimum distortion')
    require(list(map(F,given['charges']))==expected['charges'],'Nonoptimal projected charges')
    require(list(map(F,surrogate_fees))==expected['charges'],'Inner tariff differs from certified projection')
    require(expected['absolute_deviation']<=eps,'Projection L1 tolerance not met')
    previous=optimum(fees,d-1)['absolute_deviation'] if d else None
    require(previous is None or previous>eps,'Nonminimal selected projection allowance')
    return dict(projection_certified=True,selected_exception_budget=d,
        projected_exceptions=len(expected['exceptions']),
        projection_standard_fee=str(expected['standard_fee']),
        projection_l1=str(expected['absolute_deviation']),
        previous_projection_l1=None if previous is None else str(previous),
        minimum_allowance_certified=True,minimality_scope='total absolute fee distortion')
