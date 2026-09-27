"""Original-fee interval verifier; imports no optimizer."""
from copy import deepcopy
from rational import F, digest, encode
from check_tariff60 import verify as check_tariff
from check_price import check_policy, model, require

def verify(cert, expected_sha256=None):
    require(cert['schema']=='NDU-R61-robust-tariff-v1','Wrong schema')
    spec=cert['spec'];sha=digest(spec)
    require(sha==cert['instance_sha256'],'Wrong input digest')
    if expected_sha256 is not None:require(sha==expected_sha256,'Wrong requested input')
    inner=cert['surrogate_certificate'];other=deepcopy(spec);other['charges']=inner['spec']['charges']
    require(other==inner['spec'],'Physical or feasibility input changed')
    result=check_tariff(inner,digest(other))
    w,b,g,t,r,q,a,fees,B,m=model(spec)
    errors=[x-F(y) for x,y in zip(fees,other['charges'])]
    plus=sum(sorted([max(F(0),x) for x in errors],reverse=True)[:m],F(0))
    minus=sum(sorted([max(F(0),-x) for x in errors],reverse=True)[:m],F(0))
    expected=encode(dict(error=errors,positive_budget=plus,negative_budget=minus,regret_bound=plus+minus,absolute_deviation=sum(map(abs,errors),F(0))))
    require(expected==cert['error_budget'],'Wrong error budget')
    lower=check_policy(spec,cert['policy']);upper=F(result['upper'])+minus
    require(tuple(map(F,inner['policy']['book']))==tuple(map(F,cert['policy']['book'])),'Different selected book')
    require(lower==F(cert['lower']) and upper==F(cert['upper']),'Wrong original-fee interval')
    require(lower<=upper and upper-lower<=F(cert['epsilon']),'Unmet tolerance')
    return dict(status='PASS',lower=str(lower),upper=str(upper),branches=result['branches'])
