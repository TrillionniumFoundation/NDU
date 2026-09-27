"""Check protocol coverage and semantic verification without hiding timeouts."""
from pathlib import Path
from collections import Counter
from fractions import Fraction as F
import datetime,hashlib,json,sys
R=Path(__file__).resolve().parents[1];OUT=R/'results'
def read(name):return json.loads((OUT/name).read_text())
def need(ok,why):
    if not ok:raise RuntimeError(why)
def run():
    reg=read('REGRESSION.json');study=read('STUDY.json');anytime=read('ANYTIME.json');challenge=read('CHALLENGE.json')
    hard=read('HARDNESS_REGRESSION.json');screen=read('SCREENING.json');sharp=read('SHARP_SCREENING.json');prod=read('PRODUCTION.json')
    for name,obj in [('regression',reg),('study',study),('anytime',anytime),('challenge',challenge),('hardness regression',hard),('screening',screen),('sharp screening',sharp),('production',prod)]:need(obj.get('status')=='PASS','Failed '+name)
    need(reg['models']==130 and reg['global_certificates']==130 and reg['fixed_books']==2644,'Incomplete main regression')
    need(reg['common_cap_certificates']==60 and reg['heterogeneous_models']==30,'Incomplete subclass regression')
    need(study['cases']==30 and study['runs']==142 and len(study['records'])==142,'Incomplete original study')
    need(anytime['cases']==10 and len(anytime['records'])==10,'Incomplete anytime runs')
    need(len(challenge['cases'])==4 and len(challenge['runs'])==20,'Incomplete structural challenges')
    need(hard['models']==60 and hard['optional_subsets']==1692 and hard['full_catalog_books']==3004,'Incomplete reduction regression')
    need(screen['cases']==24,'Incomplete screening protocol')
    need(len(sharp['rows'])==3 and len(prod['cases'])==9,'Incomplete development examples')
    records=study['records']+anytime['records']+challenge['runs']
    need(len(records)==172,'Wrong number of timed runs')
    need(len({(x['id'],x.get('method','price')) for x in records})==172,'Duplicate timed result')
    prices=[x for x in records if x.get('method','price')=='price'];need(len(prices)==44,'Incomplete price certificates')
    for rec in prices:
        need(rec.get('verification_status')=='PASS','Unverified price certificate '+rec['id'])
        need(F(rec['lower'])<=F(rec['upper']),'Reversed price interval')
        if rec['status']=='EXACT':need(F(rec['lower'])==F(rec['upper']),'Inexact record labeled exact')
    for rec in records:need(rec['status'] not in ['ERROR','FAIL'],'Execution error '+rec['id'])
    counts={method:dict(Counter(x['status'] for x in study['records'] if x['method']==method)) for method in ['price','uniform','enumeration','classbox','mip']}
    result=dict(status='PASS',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),timed_runs=172,initial_study_runs=142,anytime_runs=10,challenge_runs=20,checked_price_certificates=len(prices),initial_method_outcomes=counts,anytime_outcomes=dict(Counter(x['status'] for x in anytime['records'])),challenge_outcomes={method:dict(Counter(x['status'] for x in challenge['runs'] if x['method']==method)) for method in counts},regression={k:v for k,v in reg.items() if k not in ['branched_regression_models','seconds']},hardness_regression={k:v for k,v in hard.items() if k not in ['rows','seconds']},screening_cases=24,forced_anchor_removals=screen['forced_anchor_removals'],protocol_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in R.glob('PROTOCOL*.json')},result_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*.json') if p.name!='EXECUTION_AUDIT.json'},interpretation='PASS means complete protocol accounting and checked proof records, not that every solver meets every requested tolerance. Numerical MIP, exact proofs and fallback intervals remain distinct.')
    (OUT/'EXECUTION_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['result_sha256','regression']},indent=2));return result
if __name__=='__main__':run()
