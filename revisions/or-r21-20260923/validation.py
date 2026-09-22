"""Independent validation of two predeclared deterministic frozen ensembles.
No new fitting or policy selection uses these contexts. The restricted economic
comparator is reoptimized inside the same accepted feasible set on every query.
"""
from core import *
from time_comparator import TimeComparator
import gzip,itertools,math
OUT=ROOT/'results';OUT.mkdir(exist_ok=True)
def run():
    s=Tree();poli=Polisher(s);tc=TimeComparator(s);models=frozen_models()
    names=['ensemble-tanh-gradient','ensemble-rbf-direct'];keys=['tanh-gradient','rbf-direct']
    (OUT/'time_primitives.json').write_text(json.dumps(tc.p)+'\n')
    domains={'iid':(23011,2048,-16,16,2,32),'shift':(23012,512,-24,24,1,48)}
    rows=[];bounds={};geometry=[];counts=0
    with gzip.open(OUT/'validation_certificates.jsonl.gz','wt') as f:
      for domain,(seed,count,hlo,hhi,llo,lhi) in domains.items():
        # Convexity of J in (h,lambda) gives a uniform box bound from all vertices.
        # No statistical validation outcomes are used to construct this bound.
        B=F(0)
        for j,cc in enumerate(itertools.product(*([(hlo,hhi)]*s.rank+[(llo,lhi)]))):
            c=np.array(cc);x,d,it=s.solve(c,previous=True);a=s.audit(c,x,d,record=True)
            assert a['gap']<1e-5
            B=max(B,F(a['upper_exact']))
            f.write(json.dumps({'kind':'corner','domain':domain,'id':j,'record':a['record']})+'\n');counts+=1
        bounds[domain]={'upper_exact':str(B),'upper':math.nextafter(float(B),math.inf),'vertices':2**(s.rank+1)}
        if domain=='iid':ct=contexts(seed,count,s.rank)
        else:
            rng=np.random.default_rng(seed)
            ct=np.column_stack([rng.integers(hlo,hhi+1,(count,s.rank)),rng.integers(llo,lhi+1,count)])
        preds={name:np.mean([m[key].predict(normalize(ct,s.rank)) for m in models],axis=0) for name,key in zip(names,keys)}
        for j,c in enumerate(ct):
            refx,refd,it=s.solve(c,previous=True);ref=s.audit(c,refx,refd,record=True)
            assert ref['gap']<1e-5
            # A deterministic policy is a map of this context, not a cache history.
            tc.solver.qp.close();tc.solver=Lifted(s,eps=1e-9,extra_equalities=tc.extra)
            comp=tc.solve(c,previous=False)
            item={'kind':'validation','domain':domain,'id':j,'reference':ref['record'],'comparator':comp['record'],'methods':{}}
            ge={'domain':domain,'id':j,'capacity_binding':int(np.sum(abs(s.C@refx[:s.n]-s.capnum/8)<1e-5)),
                'tier_boundary':int(np.sum((refx[:s.n]+s.znum/32<1e-5)|(1-s.znum/32-refx[:s.n]<1e-5))),
                'switching_kinks':ref['near_kinks']};geometry.append(ge)
            for name in names:
                eta=preds[name][j]
                s.base.close();s.base=QP(sparse.diags(np.r_[s.d,np.zeros(s.n)],format='csc'),s.M,s.lower,s.upper,eps=1e-9)
                x,d,ii=s.solve(c,price=eta);a=s.audit(c,x,d,price=eta,record=True)
                ap=poli.polish(a['record'],initial=a)
                # Deploy the better of two certified feasible policies; the comparator's
                # restricted optimization error is explicitly charged to its true optimum.
                chosen=max(F(ap['gain_exact']),F(comp['gain_exact']))
                excess=chosen-F(comp['upper_exact'])
                assert chosen>=F(0) and chosen<=B
                rows.append({'domain':domain,'id':j,'method':name,'context':c.tolist(),
                    'outside_gain':float(chosen),'restricted_gain_lower':float(excess),
                    'restricted_gain_upper':float(chosen-F(comp['gain_exact'])),
                    'restricted_gap':comp['gap'],'regret_upper':float(F(ref['upper_exact'])-chosen),
                    'raw_regret_upper':float(F(ref['upper_exact'])-F(ap['gain_exact'])),
                    'original_gap':a['gap'],'polished_gap':ap['gap'],'pass_1e-3':ap['gap']<=1e-3,
                    'pass_1e-5':ap['gap']<=1e-5,'comparator_selected':F(comp['gain_exact'])>F(ap['gain_exact']),
                    'reference_gain':ref['gain'],'comparator_gain':comp['gain']})
                item['methods'][name]={'before':a['record'],'after':ap['record']}
            f.write(json.dumps(item)+'\n');counts+=1
            if (j+1)%256==0:print(domain,j+1,'of',count,flush=True)
        (OUT/'validation_rows.json').write_text(json.dumps(rows)+'\n')
    summary=[];delta=.05;M=4
    for domain,(seed,count,*_) in domains.items():
      B=bounds[domain]['upper'];penalty=B*math.sqrt(math.log(M/delta)/(2*count))
      for name in names:
        rr=[r for r in rows if r['domain']==domain and r['method']==name]
        lower=float(np.mean([r['restricted_gain_lower'] for r in rr]))-penalty
        # S >= J_time - delta_max deterministically; do not falsely truncate to zero.
        slack=max(r['restricted_gap'] for r in rr)
        summary.append(dict(domain=domain,method=name,n=count,mean_outside_gain=float(np.mean([r['outside_gain'] for r in rr])),
          mean_restricted_gain_lower=float(np.mean([r['restricted_gain_lower'] for r in rr])),
          expected_restricted_gain_lower=lower,hoeffding_penalty=penalty,range_upper=B,
          mean_regret_upper=float(np.mean([r['regret_upper'] for r in rr])),
          pass_1e3=float(np.mean([r['pass_1e-3'] for r in rr])),pass_1e5=float(np.mean([r['pass_1e-5'] for r in rr])),
          max_comparator_gap=slack,comparator_selected=float(np.mean([r['comparator_selected'] for r in rr]))))
    result={'status':'PASS','observations':len(rows),'records':counts,'summary':summary,'bounds':bounds,
      'M':M,'delta':delta,'state_isolation':'Fresh response workspace for each policy/context; fresh restricted-comparator workspace per context. Adaptive penalty and warm-start state cannot leak between validation decisions.',
      'sampling':'Independent IID contexts within each separately declared domain; all eight fitted models frozen before validation. Simultaneous conditional bounds for four deterministic policy/domain pairs. No statement averages over training randomness.',
      'interval_proof':'The actual excess S-J_time lies in [-B,B], whether or not the numerical comparator is exact. We use width 2B. Each sample contributes the computable lower bound S-U_time; no future uniform numerical-tolerance assumption is required.',
      'timing':'The economic gate includes online reoptimization of a time-only amendment. This validation is not evidence of computational acceleration.',
      'scope':'Known synthetic model under reward/friction covariate shift. No unknown-demand, coefficient-misspecification, or field calibration claim.'}
    # Width 2B remains valid without extrapolating observed comparator accuracy
    # to every future context. Bound the true optimum, not only the candidate.
    for row in result['summary']:
        penalty=2*row['range_upper']*math.sqrt(math.log(M/delta)/(2*row['n']))
        row['hoeffding_penalty']=penalty
        row['expected_restricted_gain_lower']=row['mean_restricted_gain_lower']-penalty
    (OUT/'validation_summary.json').write_text(json.dumps(result,indent=2)+'\n')
    (OUT/'validation_geometry.json').write_text(json.dumps(geometry)+'\n')
    print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':run()
