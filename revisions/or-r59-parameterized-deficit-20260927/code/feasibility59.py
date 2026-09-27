"""Digest-bound infeasibility preflight and checker. Imports no optimizer."""
from pathlib import Path
import hashlib,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'revisions/or-r58-structural-referee-20260926/code'))
from rational import F,digest,encode

def primitives(spec):
    z=spec['model'];w,b,g,t,r,q=[tuple(map(F,z[key])) for key in ('weights','caps','gamma','ceilings','reward_r','reward_q')]
    if not b or any(len(v)!=len(b) for v in (w,g,t,r,q)):raise ValueError('Malformed history dimensions')
    if any(p<=0 for p in w) or sum(w)!=1:raise ValueError('Malformed probabilities')
    if any(not(0<=bj<=1 and tj>=bj and gj>=0 and rj>0 and 0<=qj<=rj) for bj,tj,gj,rj,qj in zip(b,t,g,r,q)):raise ValueError('Malformed primitives')
    a=tuple(map(F,spec['catalog']));rho=tuple(map(F,spec['charges']));B=F(spec['promise']);m=spec['budget']
    if a!=tuple(sorted(set(a))) or any(not 0<=v<=1 for v in a) or len(rho)!=len(a) or any(v<0 for v in rho) or type(m)!=int:raise ValueError('Malformed catalog/charges/budget')
    return a,b,B,m,sum(p*v for p,v in zip(w,b))

def preflight(spec):
    a,b,B,m,bar=primitives(spec)
    reasons=[]
    if not a:reasons.append('EMPTY_CATALOG')
    if m<1:reasons.append('NO_COMMAND_SLOT')
    if B<0:reasons.append('NEGATIVE_PROMISE')
    if B>bar:reasons.append('AGGREGATE_CAP')
    if a and a[0]>B:reasons.append('ANCHOR_PROMISE')
    if a and a[0]>min(b):reasons.append('ANCHOR_CAP')
    return dict(schema='NDU-R59-feasibility-v1',instance_sha256=digest(spec),status='INFEASIBLE' if reasons else 'FEASIBLE',reasons=reasons,incumbent=None)

def verify(spec,record,expected_digest):
    if digest(spec)!=expected_digest or record.get('instance_sha256')!=expected_digest:raise ValueError('Wrong original input digest')
    a,b,B,m,bar=primitives(spec)
    truth={'EMPTY_CATALOG':not a,'NO_COMMAND_SLOT':m<1,'NEGATIVE_PROMISE':B<0,'AGGREGATE_CAP':B>bar,'ANCHOR_PROMISE':bool(a and a[0]>B),'ANCHOR_CAP':bool(a and a[0]>min(b))}
    if record.get('schema')!='NDU-R59-feasibility-v1' or record.get('incumbent') is not None:raise ValueError('Malformed preflight record')
    if record.get('status')=='INFEASIBLE':
        if not record.get('reasons') or not all(truth.get(v,False) for v in record['reasons']):raise ValueError('Unsupported infeasibility inequality')
    elif record.get('status')!='FEASIBLE' or any(truth.values()) or record.get('reasons'):raise ValueError('False feasibility claim')
    return {'status':'PASS','classification':record['status']}

def tests():
    import copy
    good={'model':{'weights':['1'],'caps':['1/2'],'gamma':['1'],'ceilings':['1/2'],'reward_r':['1'],'reward_q':['0']},'catalog':['0','1/2'],'charges':['0','0'],'promise':'1/4','budget':2}
    cases=[good]
    for key,value in [('catalog',[]),('budget',0),('promise','-1/4'),('promise','3/4'),('catalog',['1/2'])]:
        s=copy.deepcopy(good);s[key]=value
        if key=='catalog':s['charges']=['0']*len(value)
        cases.append(s)
    s=copy.deepcopy(good);s['catalog']=['3/4'];s['charges']=['0'];s['promise']='1/2';cases.append(s)
    for s in cases:
        c=preflight(s);verify(s,c,digest(s));bad=copy.deepcopy(c);bad['instance_sha256']='0'*64
        try:verify(s,bad,digest(s));raise AssertionError('Digest mutation accepted')
        except ValueError:pass
    s=copy.deepcopy(good);s['model']['weights']=['0']
    try:preflight(s);raise AssertionError('Malformed probability accepted')
    except ValueError:pass
    print('Preflight PASS: 7 inputs, 7 digest mutations, malformed probability rejection')
if __name__=='__main__':tests()
