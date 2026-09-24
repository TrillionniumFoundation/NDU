"""Executed same-budget net, varied scaling and adaptive-catalog comparisons."""
from pathlib import Path
from fractions import Fraction as F
from dataclasses import asdict
import random,sys,time,json,resource,statistics
from compression import Instance,frontier,ideal_targets,jensen_certificate,encode,repair_targets,policy
from independent import verify_policy
from target_net import solve
from study import Model,exhaustive_joint,recover
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R.parent/'or-r34-global-randomized-frontier-20260923'))
from randomized_frontier import Problem,randomized_frontiers


def run():
    nets=[]
    for seed in [104729,130363,155921,181081]:
        rng=random.Random(seed)
        for k in [2,3]:
            b=tuple(sorted(F(rng.randint(1,7),8) for _ in range(k)))
            weights=[rng.randint(1,4) for _ in b]; p=tuple(F(x,sum(weights)) for x in weights)
            g=tuple(F(rng.randint(0,4),2) for _ in b); delta=F(seed%3,8)
            data=Instance.make(b,p,g,[x+delta for x in b]); model=Model.make(b,p,g)
            a=tuple(F(i,4) for i in range(5)); rho=tuple(F(rng.randint(0,10),100) for _ in a)
            B=F(3,4)*data.cap_total; m=2
            exact=exhaustive_joint(model,data,a,rho,B,delta,m)[-1]
            for eps in ([F(1,4),F(1,8),F(1,16)] if k==2 else [F(1,2),F(1,4)]):
                start=time.perf_counter(); ans=solve(data,a,rho,B,m,eps); secs=time.perf_counter()-start
                gap=exact['value']-ans['policy']['value']; assert 0<=gap<=eps
                verify_policy(data,a,rho,ans['policy'],B,m)
                nets.append(dict(seed=seed,model=asdict(data),catalog=a,charges=rho,B=B,m=m,epsilon=eps,
                    result=ans,exact=exact,actual_gap=gap,seconds=secs))
    interrupted=solve(data,a,rho,B,m,F(1,100),max_profiles=1)
    assert interrupted['status']=='INTERRUPTED' and interrupted['epsilon_guarantee'] is None
    (R/'results/target_net.json').write_text(json.dumps(encode(dict(status='PASS',rows=nets,
        comparisons=len(nets),interruption_guard=True)),indent=2)+'\n')
    print('net comparisons',len(nets),flush=True)
    scaling=[]
    for seed in [104729,205019]:
        rng=random.Random(seed)
        for k,N,m in [(32,17,4),(128,33,8),(256,65,8)]:
            b=tuple(sorted(F(rng.randint(4,60),64) for _ in range(k)))
            ww=[rng.randint(1,16) for _ in b]; p=tuple(F(x,sum(ww)) for x in ww)
            g=tuple(F(rng.randint(0,16),4) for _ in b)
            # Heterogeneous headroom: not confined to a common delta.
            tau=tuple(x+F(rng.randint(0,3),16) for x in b)
            data=Instance.make(b,p,g,tau); B=F(4,5)*data.cap_total
            a=tuple(F(i,N-1) for i in range(N))
            for charged in [False,True]:
                rho=tuple(F(rng.randint(0,25),1000) if charged else F(0) for _ in a)
                timings=[]
                for _ in range(3):
                    start=time.perf_counter(); ans=jensen_certificate(data,a,rho,B,m)
                    timings.append(time.perf_counter()-start)
                for q,poli in enumerate(ans['at_most'],1): verify_policy(data,a,rho,poli,B,q)
                bits=max(max(x.numerator.bit_length(),x.denominator.bit_length()) for row in ans['dp_table'] for x in row if x is not None)
                scaling.append(dict(seed=seed,k=k,N=N,m=m,charged=charged,model=asdict(data),catalog=a,
                    charges=rho,B=B,frontier=ans['at_most'],gaps=ans['same_budget_gaps'],upper=ans['jensen_upper'],
                    timings=timings,median_seconds=statistics.median(timings),stored_dp_bits=bits,
                    process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                    rss_scope='whole Python process cumulative Linux ru_maxrss; not allocation tracing'))
                print('scaling',seed,k,N,charged,timings,flush=True)
    (R/'results/scaling.json').write_text(json.dumps(encode(dict(status='PASS',rows=scaling,
        distributions='random ordered caps, weights, curvatures, heterogeneous ceilings and nonnegative charges',
        repetitions=3)),indent=2)+'\n')
    continuous=[]
    # Interior promise with an exact ideal continuous optimizer on two levels.
    data=Instance.make([F(3,10),F(9,10)],[F(2,5),F(3,5)],[1,2],[F(3,10),F(9,10)])
    B=F(4,5)*data.cap_total; t=ideal_targets(data,B); exact=sum(w*data.reward(z) for w,z in zip(data.weights,t))
    for N in [5,9,17,33,65]:
        a=tuple(F(i,N-1) for i in range(N)); ans=frontier(data,a,[0]*N,t,2)['at_most'][-1]
        continuous.append(dict(case='interior-ideal',grid='uniform',N=N,model=asdict(data),B=B,m=2,targets=t,
            catalog=a,policy=ans,continuous_optimum=exact,gap=exact-ans['value']))
    a=tuple(sorted({F(0),F(1),*t})); ans=frontier(data,a,[0]*len(a),t,2)['at_most'][-1]; assert ans['value']==exact
    continuous.append(dict(case='interior-ideal',grid='target-adaptive',N=len(a),model=asdict(data),B=B,m=2,
        catalog=a,targets=t,policy=ans,continuous_optimum=exact,gap=F(0)))
    # Saturation: targets are forced. The inherited exact continuous solver is
    # independent of our catalog DP and returns a nontrivial intrinsic memory loss.
    problems=[('off-cap-top',Problem.make([F(1,4),F(1,2),F(3,4)],
                [F(7,20),F(3,5),F(1,20)],[1,1,1]),2)]
    for seed in [104729,205019]:
        rng=random.Random(seed); caps=sorted(F(x,32) for x in rng.sample(range(2,30),7))
        ww=[rng.randint(1,9) for _ in caps]; pp=[F(x,sum(ww)) for x in ww]
        problems.append((f'saturated-{seed}',Problem.make(caps,pp,[F(rng.randint(0,8),2) for _ in caps]),3))
    for name,p0,m in problems:
        data=Instance.make(p0.caps,p0.probabilities,p0.gamma,[b+1 for b in p0.caps])
        exactsol=randomized_frontiers(p0,m)[-1]
        W=sum(w*data.reward(b) for w,b in zip(data.weights,data.caps)); exact=W-exactsol.loss
        for N in [9,17,33,65]:
            a=tuple(F(i,N-1) for i in range(N)); ans=frontier(data,a,[0]*N,data.caps,m)['at_most'][-1]
            assert ans['value']<=exact
            continuous.append(dict(case=name,grid='uniform',N=N,model=asdict(data),B=data.cap_total,m=m,
                catalog=a,policy=ans,continuous_optimum=exact,continuous_book=exactsol.codebook,gap=exact-ans['value']))
        a=tuple(sorted({F(0),F(1),*data.caps}))
        for step in range(5):
            ans=frontier(data,a,[0]*len(a),data.caps,m)['at_most'][-1]
            assert ans['value']<=exact
            continuous.append(dict(case=name,grid='adaptive-midpoint',N=len(a),model=asdict(data),B=data.cap_total,m=m,
                catalog=a,policy=ans,continuous_optimum=exact,continuous_book=exactsol.codebook,gap=exact-ans['value']))
            if ans['value']==exact: break
            options=[]
            for u,v in zip(a,a[1:]):
                candidate=tuple(sorted((*a,(u+v)/2)))
                f=frontier(data,candidate,[0]*len(candidate),data.caps,m)['at_most'][-1]
                options.append((f['value'],v-u,candidate))
            a=max(options)[-1]
    (R/'results/continuous.json').write_text(json.dumps(encode(dict(status='PASS',rows=continuous,
        scope='exact continuous comparisons only in stated Jensen-attaining or saturated expected regimes; adaptive grid selection is a heuristic')),indent=2)+'\n')
    print('continuous comparisons',len(continuous),flush=True)
    # Full error identities, including deliberately suboptimal support policies.
    errors=[]
    for ix,row in enumerate(nets[::2]):
        raw=row['model']; data=Instance(**raw); a=row['catalog']; rho=row['charges']; B=row['B']; m=row['m']
        model=Model.make(data.caps,data.weights,data.gamma)
        delta=data.ceilings[0]-data.caps[0]
        rec=recover(model,a,rho,m,B,delta,F(1,10000)); left=rec['left']; right=rec['right']; cmap=dict(zip(a,rho))
        # Fixed singleton endpoint policies remain feasible but may be far from priced-optimal.
        pm=policy(data,(a[0],),data.caps,cmap)
        pp=policy(data,(a[0],),(a[0],)*len(data.caps),cmap)
        Sm=pm['promise']; Sp=pp['promise']; theta=(B-Sp)/(Sm-Sp)
        t=tuple(theta*u+(1-theta)*v for u,v in zip(pm['targets'],pp['targets']))
        lm=left['price']; lp=right['price']; U=min(left['upper'],right['upper'])
        zm=left['upper']-(pm['value']+lm*(B-Sm)); zp=right['upper']-(pp['value']+lp*(B-Sp))
        assert zm>=0 and zp>=0
        e=(lp-lm)*(Sm-B)*(B-Sp)/(Sm-Sp)
        mixed=theta*pm['value']+(1-theta)*pp['value']
        assert mixed>=U-e-theta*zm-(1-theta)*zp
        result=frontier(data,a,rho,t,m)['at_most'][-1]
        assert result['value']>=mixed
        errors.append(dict(row=ix,theta=theta,U=U,e=e,zeta_minus=zm,zeta_plus=zp,policy=result,
            bound=U-e-theta*zm-(1-theta)*zp))
    (R/'results/inexact.json').write_text(json.dumps(encode(dict(status='PASS',rows=errors)),indent=2)+'\n')
    print('inexact checks',len(errors),flush=True)

if __name__=='__main__': run()
