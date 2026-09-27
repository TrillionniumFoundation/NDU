"""Original-fee interval verifier; imports no optimizer."""
from copy import deepcopy
from rational import F, digest, encode
from check_tariff60 import verify as check_tariff
from check_price import check_policy, model, require
from check_projection64 import verify_projection

def verify(cert, expected_sha256=None):
    require(cert['schema']=='NDU-R61-robust-tariff-v1','Wrong schema')
    spec=cert['spec'];sha=digest(spec)
    require(sha==cert['instance_sha256'],'Wrong input digest')
    if expected_sha256 is not None:require(sha==expected_sha256,'Wrong requested input')
    inner=cert['surrogate_certificate'];other=deepcopy(spec);other['charges']=inner['spec']['charges']
    require(other==inner['spec'],'Physical or feasibility input changed')
    w,b,g,t,r,q,a,fees,B,m=model(spec)
    projection=verify_projection(cert,fees,other['charges'])
    result=check_tariff(inner,digest(other))
    errors=[x-F(y) for x,y in zip(fees,other['charges'])]
    plus=sum(sorted([max(F(0),x) for x in errors],reverse=True)[:m],F(0))
    minus=sum(sorted([max(F(0),-x) for x in errors],reverse=True)[:m],F(0))
    expected=encode(dict(error=errors,positive_budget=plus,negative_budget=minus,regret_bound=plus+minus,absolute_deviation=sum(map(abs,errors),F(0))))
    require(expected==cert['error_budget'],'Wrong error budget')
    lower=check_policy(spec,cert['policy']);upper=F(result['upper'])+minus
    require(tuple(map(F,inner['policy']['book']))==tuple(map(F,cert['policy']['book'])),'Different selected book')
    # Derive gross payoffs from independently checked allocations, not metadata.
    indices=[a.index(F(x)) for x in cert['policy']['book']]
    original_charge=sum((fees[i] for i in indices),F(0))
    surrogate_charge=sum((F(other['charges'][i]) for i in indices),F(0))
    inner_gross=F(result['lower'])+surrogate_charge
    outer_gross=lower+original_charge
    require(outer_gross==inner_gross,'Transferred policy has different gross payoff')
    transferred=F(result['lower'])-sum((errors[i] for i in indices),F(0))
    require(lower==transferred,'Incorrect same-book transfer lower formula')
    for policy,gross in ((inner['policy'],inner_gross),(cert['policy'],outer_gross)):
        if 'gross' in policy:require(F(policy['gross'])==gross,'False declared gross payoff')
    require(lower==F(cert['lower']) and upper==F(cert['upper']),'Wrong original-fee interval')
    require(lower<=upper and upper-lower<=F(cert['epsilon']),'Unmet tolerance')
    return dict(transfer_formula_certified=True,transferred_lower=str(transferred),equal_gross_certified=True,request_bound=False,status='PASS',lower=str(lower),upper=str(upper),branches=result['branches'],tariff_exceptions=result['exception_count'],tariff_standard_fee=result['standard_fee'],**projection)
