#!/usr/bin/env python3
"""Executed OR R4 revision: exact contract DP, independent rational replay,
paired simulation, natural-data conditioning, and boundary-complete PDE tests.
Run from anywhere: python execute.py. Python 3.11+, numpy and scipy required.
No network, training service, or historical 'pass' label is used.
"""
from __future__ import annotations
import csv, hashlib, json, math, platform, sys, time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from scipy.stats import t as student_t

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'
BETA = F(97,100)
PINT = ((14,5,1),(3,14,3),(1,5,14))
P = tuple(tuple(F(p,20) for p in row) for row in PINT)
DW = (1,3,4,2)
N = 10
T = 8
METHODS = ('joint_contract','expanded_action_mdp','frozen_contract',
           'capacity_matched_gate','physical_oracle')
COMP = ('net_reward','physical_cost','premium','liability','maintenance',
        'adjustment','filled_demand','lost_demand','demand',
        'undiscounted_filled','undiscounted_lost','undiscounted_demand')

def save(name, obj):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+'\n')

def savecsv(name, rows):
    if not rows: raise ValueError('No rows')
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def atoms(z, s2):
    over=sum(w*max(s2-2*(z+d),0) for d,w in enumerate(DW))
    lost=sum(w*max(2*(z+d)-s2,0) for d,w in enumerate(DW))
    return over,lost,60*s2+12*over+13*lost

def int_dp(n=10, method='joint_contract', factored=False):
    """Integer-scaled exact Bellman comparisons. Denominators are common by t.
    Expanded-action comparator deliberately uses a flattened action enumeration.
    Dummy gate evaluates all duplicate labels but never changes economic theta.
    """
    if n%2: raise ValueError('Even grid required by frozen contract and initial q')
    vals=[None]*(T+1); pol=[None]*T; dens=[None]*(T+1)
    vals[T]=[[0]*(n+1) for _ in range(3)]; dens[T]=1
    stage_cache={}; sopt={}; prep=0; count=0; terms=0
    for z in range(3):
        for j in range(n+1):
            candidates=[]
            for s2 in range(13):
                over,lost,cnum=atoms(z,s2)
                v=80*(3+7*z)*j*n-cnum*n*n-24*j*lost*n-600*j*j
                stage_cache[z,j,s2]=v
                candidates.append((v,s2)); prep+=1
            sopt[z,j]=max(candidates)[1]
    for tt in range(T-1,-1,-1):
        r=T-tt; scale=2000**(r-1); den=400*n*n*scale
        cont=[[97*sum(PINT[z][zp]*vals[tt+1][zp][j] for zp in range(3))
               if r>1 else 0 for j in range(n+1)] for z in range(3)]
        terms+=3*3*(n+1) if r>1 else 0
        vv=[]; pp=[]
        for z in range(3):
            vz=[]; pz=[]
            for i in range(n+1):
                if method=='expanded_action_mdp':
                    actions=[(idx//(n+1),idx%(n+1),idx%(n+1)) for idx in range(13*(n+1))]
                elif method=='capacity_matched_gate':
                    actions=[(s2,n//2,g) for s2 in range(13) for g in range(n+1)]
                elif method=='frozen_contract':
                    actions=[(s2,n//2,n//2) for s2 in range(13)]
                elif factored:
                    actions=[(sopt[z,j],j,j) for j in range(n+1)]
                else:
                    actions=[(s2,j,j) for s2 in range(13) for j in range(n+1)]
                best=None
                for s2,j,gate in actions:
                    if method=='physical_oracle':
                        _,_,cn=atoms(z,s2)
                        stage=-cn*n*n
                    else:
                        stage=stage_cache[z,j,s2]-240*(j-i)**2
                    v=stage*scale+cont[z][j]; count+=1
                    cand=(v,s2,j,gate)
                    if best is None or cand>best: best=cand
                vz.append(best[0]); pz.append((best[1],best[2]))
            vv.append(vz); pp.append(pz)
        vals[tt]=vv; pol[tt]=pp; dens[tt]=den
    return dict(n=n,method=method,values=vals,policy=pol,denominators=dens,
                bellman_candidates=count,stage_precomputations=prep,
                continuation_terms=terms)

def fractional_dp(method):
    """Independent implementation: construct costs from demand realizations,
    use Fraction at every arithmetic operation and direct product action lists.
    Does not call atoms(), int_dp(), or use their stage numerators.
    """
    vv={}; pp={}; count=0
    for z in range(3):
        for i in range(11): vv[T,z,i]=F(0)
    for tt in reversed(range(T)):
        for z in range(3):
            for i in range(11):
                q=F(i,10); choices=[]
                js=[5] if method in ('frozen_contract','capacity_matched_gate') else range(11)
                for s2 in range(13):
                    S=F(s2,2)
                    for j in js:
                        th=F(j,10); reward=F(0)
                        for d,w in enumerate(DW):
                            D=z+d; lo=max(D-S,0); ov=max(S-D,0)
                            phys=F(3,10)*S+F(3,5)*ov+F(13,20)*lo
                            r=-phys if method=='physical_oracle' else (
                                (F(3,5)+F(7,5)*z)*th-phys-F(6,5)*th*lo
                                -F(3,2)*th*th-F(3,5)*(th-q)**2)
                            reward+=F(w,10)*r
                        value=reward+BETA*sum(P[z][zp]*vv[tt+1,zp,j] for zp in range(3))
                        choices.append((value,s2,j)); count+=1
                best=max(choices)
                ties=[x for x in choices if x[0]==best[0]]
                assert all(x[1]<=best[1] and x[2]<=best[2] for x in ties)
                vv[tt,z,i]=best[0]; pp[tt,z,i]=(best[1],best[2])
    return vv,pp,count

def exact_ledger(solution):
    n=solution['n']; state={(1,n//2):F(1)}; ledger={c:F(0) for c in COMP}
    for tt in range(T):
        nxt={}
        for (z,i),mass in state.items():
            s2,j=solution['policy'][tt][z][i]; S=F(s2,2); th=F(j,n); q=F(i,n)
            for d,w in enumerate(DW):
                D=z+d; lost=max(F(D)-S,0); over=max(S-F(D),0); fill=F(D)-lost
                row={'physical_cost':F(3,10)*S+F(3,5)*over+F(13,20)*lost,
                     'premium':(F(3,5)+F(7,5)*z)*th,'liability':F(6,5)*th*lost,
                     'maintenance':F(3,2)*th*th,'adjustment':F(3,5)*(th-q)**2,
                     'filled_demand':fill,'lost_demand':lost,'demand':F(D)}
                row['net_reward']=row['premium']-sum(row[k] for k in ('physical_cost','liability','maintenance','adjustment'))
                weight=mass*F(w,10)
                for k,x in row.items(): ledger[k]+=BETA**tt*weight*x
                for k,src in (('undiscounted_filled','filled_demand'),('undiscounted_lost','lost_demand'),('undiscounted_demand','demand')):
                    ledger[k]+=weight*row[src]
            for zp in range(3): nxt[zp,j]=nxt.get((zp,j),F(0))+mass*P[z][zp]
        state=nxt
    assert sum(state.values())==1
    assert ledger['net_reward']==ledger['premium']-sum(ledger[k] for k in ('physical_cost','liability','maintenance','adjustment'))
    assert ledger['filled_demand']+ledger['lost_demand']==ledger['demand']
    return ledger

def envelope_check(solution):
    """Exact upper hull in q for the restricted-action dynamic problem.
    This is an exact max-affine-minus-quadratic critic, not a smooth PDE fit.
    """
    from bisect import bisect_right
    records=[]; checked=0
    for tt in range(T):
        for z in range(3):
            hull=[]; starts=[]
            for j in range(11):
                th=F(j,10); candidates=[]
                for s2 in range(13):
                    over,lost,cnum=atoms(z,s2)
                    base=(F(3,5)+F(7,5)*z)*th-F(cnum,400)-F(6,5)*th*F(lost,20)-F(21,10)*th*th
                    future=BETA*sum(P[z][zp]*F(solution['values'][tt+1][zp][j],solution['denominators'][tt+1]) for zp in range(3))
                    candidates.append((base+future,s2))
                intercept,s2=max(candidates); slope=F(6,5)*th
                cross=None
                while hull:
                    pm,pb,_,_=hull[-1]; cross=(pb-intercept)/(slope-pm)
                    if len(hull)==1 or cross>starts[-1]: break
                    hull.pop(); starts.pop()
                if not hull: cross=None
                hull.append((slope,intercept,s2,j)); starts.append(cross)
            for i in range(11):
                q=F(i,10); k=bisect_right(starts[1:],q)
                slope,base,s2,j=hull[k]
                val=base+slope*q-F(3,5)*q*q
                assert val==F(solution['values'][tt][z][i],solution['denominators'][tt])
                assert (s2,j)==solution['policy'][tt][z][i]; checked+=1
            records.append(dict(t=tt,regime=z,lines=[dict(slope=str(m),intercept=str(b),stock=str(F(s2,2)),contract=str(F(j,10)),start=None if x is None else str(x)) for (m,b,s2,j),x in zip(hull,starts)]))
    save('exact_envelopes.json',records)
    return checked

def smooth_neural_check(solution):
    """Construct (do not train) C2 cubic-ReLU critics from the exact envelope.
    All weights, grid evaluations and policy comparisons are rational.
    h_tau(x)=[(x+tau)_+^3-2*x_+^3+(x-tau)_+^3]/(6*tau^2).
    Its error above ReLU is in [0,tau/6], uniformly on the real line.
    """
    records=json.loads((OUT/'exact_envelopes.json').read_text())
    lookup={(r['t'],r['regime']):r['lines'] for r in records}
    result=[]
    for m in (4,8,12,16,20):
        tau=F(1,2**m); eps=tau/5; w={}; maxerr=F(0); maxunits=0
        for z in range(3):
            for i in range(11): w[T,z,i]=F(0)
        for tt in range(T):
            for z in range(3):
                lines=lookup[tt,z]; maxunits=max(maxunits,3*(len(lines)-1))
                for i in range(11):
                    q=F(i,10); val=F(lines[0]['intercept'])+F(lines[0]['slope'])*q-F(3,5)*q*q
                    for prev,line in zip(lines,lines[1:]):
                        delta=F(line['slope'])-F(prev['slope']); x=q-F(line['start'])
                        hinge=(max(x+tau,0)**3-2*max(x,0)**3+max(x-tau,0)**3)/(6*tau*tau)
                        val+=delta*hinge
                    exact=F(solution['values'][tt][z][i],solution['denominators'][tt])
                    assert 0<=val-exact<=eps
                    maxerr=max(maxerr,val-exact); w[tt,z,i]=val
        pv={}; maxloss=F(0); changed=0
        for z in range(3):
            for i in range(11): pv[T,z,i]=F(0)
        for tt in reversed(range(T)):
            for z in range(3):
                for i in range(11):
                    q=F(i,10); candidates=[]
                    for j in range(11):
                        th=F(j,10); stocks=[]
                        for s2 in range(13):
                            over,lost,cnum=atoms(z,s2)
                            stage=(F(3,5)+F(7,5)*z)*th-F(cnum,400)-F(6,5)*th*F(lost,20)-F(3,2)*th*th-F(3,5)*(th-q)**2
                            stocks.append((stage,s2))
                        stage,s2=max(stocks)
                        val=stage+BETA*sum(P[z][zp]*w[tt+1,zp,j] for zp in range(3))
                        candidates.append((val,s2,j,stage))
                    _,s2,j,stage=max(candidates)
                    changed+=int((s2,j)!=solution['policy'][tt][z][i])
                    pv[tt,z,i]=stage+BETA*sum(P[z][zp]*pv[tt+1,zp,j] for zp in range(3))
                    exact=F(solution['values'][tt][z][i],solution['denominators'][tt])
                    loss=exact-pv[tt,z,i]
                    bound=BETA*eps*sum(BETA**k for k in range(T-tt-1))
                    assert 0<=loss<=bound; maxloss=max(maxloss,loss)
        true0=F(solution['values'][0][1][5],solution['denominators'][0])
        bound=BETA*eps*sum(BETA**k for k in range(T-1))
        result.append(dict(m=m,tau=str(tau),uniform_value_bound=str(eps),
            uniform_policy_loss_bound=str(bound),policy_bound_decimal=float(bound),
            initial_policy_value=str(pv[0,1,5]),initial_policy_loss=str(true0-pv[0,1,5]),
            maximum_checked_value_error=str(maxerr),maximum_checked_policy_loss=str(maxloss),
            policy_states_changed=changed,max_cubic_relu_units=maxunits,states_checked=264,
            construction='Exact envelope compilation; no statistical training; analytic uniform bounds.'))
    savecsv('neural_critic_certificates.csv',result)
    return result

def simulation(solutions):
    rows=[]; raw={m:[] for m in METHODS}; cpf=np.cumsum(np.array(P,dtype=float),axis=1)
    for b in range(64):
        rng=np.random.default_rng(2026092300+b)
        # Two draws per period, generated before all policy evaluations.
        ud=rng.random((T,4096)); uz=rng.random((T,4096))
        zz=np.ones((T+1,4096),dtype=int); dd=np.zeros((T,4096),dtype=int)
        for tt in range(T):
            dd[tt]=zz[tt]+np.searchsorted(np.cumsum(np.array(DW)/10),ud[tt],side='right')
            zz[tt+1]=(uz[tt,:,None]>=cpf[zz[tt]]).sum(axis=1)
        for m in METHODS:
            ps=np.array(solutions[m]['policy']); qi=np.full(4096,5,dtype=int)
            acc=np.zeros((4096,len(COMP)))
            for tt in range(T):
                act=ps[tt,zz[tt],qi]; S=act[:,0]/2; theta=act[:,1]/10; q=qi/10
                D=dd[tt]; lost=np.maximum(D-S,0); over=np.maximum(S-D,0); fill=D-lost
                pc=.3*S+.6*over+.65*lost; premium=(.6+1.4*zz[tt])*theta
                liability=1.2*theta*lost; maintenance=1.5*theta**2; adjustment=.6*(theta-q)**2
                r=premium-pc-liability-maintenance-adjustment
                data=np.column_stack((r,pc,premium,liability,maintenance,adjustment,fill,lost,D,fill,lost,D))
                data[:,:9]*=.97**tt; acc+=data; qi=act[:,1]
            means=acc.mean(axis=0); raw[m].append(means)
            rows.append(dict(batch=b,seed=2026092300+b,method=m,**dict(zip(COMP,map(float,means)))))
    summary=[]; tq=float(student_t.ppf(.975,63)); ref=np.asarray(raw['frozen_contract'])
    for m in METHODS:
        ar=np.asarray(raw[m]); dif=ar-ref
        for k,c in enumerate(COMP):
            avg=float(ar[:,k].mean()); hw=tq*float(ar[:,k].std(ddof=1))/8
            dm=float(dif[:,k].mean()); dh=tq*float(dif[:,k].std(ddof=1))/8
            summary.append(dict(method=m,component=c,mean=avg,ci_low=avg-hw,ci_high=avg+hw,
                paired_minus_frozen=dm,paired_ci_low=dm-dh,paired_ci_high=dm+dh))
    savecsv('simulation_batches.csv',rows); savecsv('simulation_summary.csv',summary)
    assert np.array_equal(raw['joint_contract'],raw['expanded_action_mdp'])
    assert np.array_equal(raw['frozen_contract'],raw['capacity_matched_gate'])
    return summary

def conditioning():
    rows=[]
    for b in range(64):
        rng=np.random.default_rng(2026092400+b); u=rng.uniform(-1,1,2048); xi=rng.normal(size=2048)
        X=np.column_stack((u*u/2,np.ones_like(u)))
        for eps in (.1,.01,.001,.0001):
            sc=math.sqrt(2*eps); y=(u+sc*xi)**2/2
            Z=np.column_stack((u*u/(2*sc),np.ones_like(u)))
            k,inter=np.linalg.lstsq(X,y,rcond=None)[0]
            zeta,zinter=np.linalg.lstsq(Z,y,rcond=None)[0]
            inferred=zeta/sc
            rows.append(dict(batch=b,seed=2026092400+b,epsilon=eps,k=float(k),zeta=float(zeta),
                direct_p_mse=float((k-1)**2/3),inferred_p_mse=float((inferred-1)**2/3),
                induced_z_mse=float(2*eps*(inferred-1)**2/3),
                slope_parity_error=float(abs(k-inferred)),intercept_parity_error=float(abs(inter-zinter)),
                direct_design_condition=float(np.linalg.cond(X)),z_design_condition=float(np.linalg.cond(Z))))
    savecsv('conditioning_batches.csv',rows)
    summary=[]
    for eps in (.1,.01,.001,.0001):
        group=[r for r in rows if r['epsilon']==eps]
        summary.append(dict(epsilon=eps,**{key:float(np.mean([r[key] for r in group])) for key in
            ('direct_p_mse','inferred_p_mse','induced_z_mse','direct_design_condition','z_design_condition')},
            max_parity_error=max(r['slope_parity_error'] for r in group)))
    savecsv('conditioning_summary.csv',summary)
    assert max(r['slope_parity_error'] for r in rows)<1e-11
    return summary

def pde_sequence():
    rows=[]
    for m in (4,8,12,16,20):
        e=F(1,2**m); residual=F(23,10)*e+F(21,20)*e*e
        rows.append(dict(m=m,epsilon=str(e),residual_bound=str(residual),terminal_defect='0',
            lateral_defect='0',greedy_gap='0',value_bound=str(residual),policy_loss_bound=str(2*residual),
            actual_critic_error=str(e),policy_loss_bound_decimal=float(2*residual)))
    savecsv('analytic_pde_certificate.csv',rows)
    # A genuine joint space-time-action refinement, additional to the fixed R2 studies.
    meshes=[]
    for cells,intervals in ((4,8),(8,16),(16,32),(32,64)):
        h=2/cells; steps=math.ceil((.25/h**2+1.25/h)/.9); dt=1/steps
        grid=np.linspace(-1,1,cells+1); c,u=np.meshgrid(grid,grid,indexing='ij')
        exact=(c*c+u*u)/2; v=exact.copy(); act=np.linspace(-1,1,intervals+1)
        max_error=0.; max_defect=0.
        for _ in range(steps):
            cen=v[1:-1,1:-1]; cc=c[1:-1,1:-1]; uu=u[1:-1,1:-1]
            lap=.045*(v[2:,1:-1]-2*cen+v[:-2,1:-1])/h**2+.08*(v[1:-1,2:]-2*cen+v[1:-1,:-2])/h**2
            pc=(v[2:,1:-1]-cen)/h; mc=(cen-v[:-2,1:-1])/h
            pu=(v[1:-1,2:]-cen)/h; mu=(cen-v[1:-1,:-2])/h
            ac=act[:,None,None]
            ha=np.max(np.maximum(ac,0)*pc+np.minimum(ac,0)*mc-ac*ac,axis=0)
            ht=np.max((np.maximum(ac,0)*pu+np.minimum(ac,0)*mu)/4-1.25*ac*ac,axis=0)
            nxt=exact.copy(); nxt[1:-1,1:-1]=cen+dt*(lap+ha+ht-cc*cc/4-uu*uu/80-.125)
            # Exact V has local rate defect <= (|a|+|theta|/4)*h/2 + action-cover loss.
            max_error=max(max_error,float(np.max(np.abs(nxt-exact)))); v=nxt
        cover=1/intervals
        # For the quadratic Hamiltonian, action quantization costs at most 2.25*cover^2.
        bound=.625*h+2.25*cover*cover
        assert max_error<=bound+1e-12
        meshes.append(dict(spatial_cells_per_axis=cells,spatial_nodes=(cells+1)**2,time_steps=steps,
            action_points_per_coordinate=intervals+1,h=h,dt=dt,
            transition_exit_probability=dt*(.25/h**2+1.25/h),
            all_time_node_value_error=max_error,proved_node_value_bound=bound,
            bound_type='analytic quadratic-solution truncation plus nonexpansive Bellman propagation'))
    savecsv('space_time_action_refinement.csv',meshes)
    return rows,meshes

def regressions():
    # Exact sign reversal for penalty-only primitive.
    assert F(1,2)-F(1,5)/F(6,5) > F(1,2)-F(2,5)/F(6,5)
    p=np.array([.2,.3,.5]); v=np.array([-1.,.5,2.]); rho=.7
    q=p*np.exp(rho*float(BETA)*v); q/=q.sum()
    ent=math.log(float(np.sum(p*np.exp(rho*float(BETA)*v))))/rho
    vari=float(BETA)*float(q@v)-float(np.sum(q*np.log(q/p)))/rho
    assert abs(ent-vari)<1e-14
    # Heat equation with zero terminal and nonzero lateral data: w=exp(-x^2/(4s))/sqrt(s), s=1-t.
    # On K=[1,2], smooth zero extension at s=0; w_t+w_xx=0 but nonzero interior.
    boundary_witness=math.exp(-1.5**2/4)
    # One-step certificate: critic values +d and -d can reverse a greedy preference.
    delta=F(1); actions=((F(0),delta),(F(19,10),-delta))
    chosen=max(range(2),key=lambda j: actions[j][0]+actions[j][1])
    actual_loss=max(a[0] for a in actions)-actions[chosen][0]
    assert chosen==0 and delta<actual_loss<=2*delta
    # The difference between two value comparisons can approach 2d.
    return dict(penalty_sign_exact=True,gibbs_variational_error=abs(ent-vari),
        spatial_boundary_counterexample_value=boundary_witness,
        missing_boundary_counterexample='w(t,x)=(1-t)^(-1/2) exp(-x^2/[4(1-t)]), x in [1,2]',
        policy_two_comparisons='For optimal residual and greedy-gap bounds: 2*d_boundary+T*(2*d_H+d_A).',
        terminal_only_one_comparison_regression=dict(terminal_error=str(delta),bellman_error='0',greedy_error='0',actual_policy_loss=str(actual_loss)),
        QA_is_not_a_mathematical_certificate=True)

def main():
    protocol_path = HERE.parent / 'or-r2-20260920' / 'protocol.json'
    protocol_bytes = protocol_path.read_bytes()
    expected_protocol_hash = 'ef3b61559baa1b015a23ee06ade6e3fa4097273e09ca314559f68047f7809b5b'
    assert hashlib.sha256(protocol_bytes).hexdigest() == expected_protocol_hash, 'Frozen protocol changed'
    protocol = json.loads(protocol_bytes)
    assert protocol['model']['horizon'] == T
    assert F(protocol['model']['discount']) == BETA
    assert tuple(tuple(F(x) for x in row) for row in protocol['model']['transition']) == P
    assert tuple(F(x) for x in protocol['model']['probabilities']) == tuple(F(w,10) for w in DW)
    assert tuple(protocol['methods']) == METHODS
    assert protocol['evaluation']['batches'] == 64 and protocol['evaluation']['episodes_per_batch'] == 4096
    assert protocol['conditioning']['training_pairs'] == 2048
    started=time.perf_counter(); OUT.mkdir(parents=True,exist_ok=True)
    sol={m:int_dp(method=m) for m in METHODS}
    assert sol['joint_contract']['values']==sol['expanded_action_mdp']['values']
    assert sol['joint_contract']['policy']==sol['expanded_action_mdp']['policy']
    assert sol['frozen_contract']['values']==sol['capacity_matched_gate']['values']
    assert sol['frozen_contract']['policy']==sol['capacity_matched_gate']['policy']
    exactrows=[]; certificate=[]; ledgers={}; replays=0
    for method in METHODS:
        s=sol[method]; vl,pl,cnt=fractional_dp(method)
        for tt in range(T):
            for z in range(3):
                for i in range(11):
                    assert F(s['values'][tt][z][i],s['denominators'][tt])==vl[tt,z,i]
                    assert s['policy'][tt][z][i]==pl[tt,z,i]
                    replays+=1
        led=exact_ledger(s); ledgers[method]=led
        obj=F(s['values'][0][1][5],s['denominators'][0])
        assert obj==(-led['physical_cost'] if method=='physical_oracle' else led['net_reward'])
        exactrows.append(dict(method=method,optimization_value=str(obj),**{k:float(v) for k,v in led.items()},
            fill_rate=float(led['filled_demand']/led['demand']),unique_economic_actions=(13 if method in ('frozen_contract','capacity_matched_gate') else 143),
            bellman_candidates=s['bellman_candidates']))
        certificate.append(dict(method=method,initial_value=str(obj),ledger_exact={k:str(v) for k,v in led.items()},
            all_state_fraction_replay='exact',states_checked=264,terminal_defect='0',bellman_defect='0',greedy_gap='0',
            candidates=s['bellman_candidates'],independent_fraction_candidates=cnt))
    # All-state lattice checks in the actual model, not inferred from sample paths.
    sj=sol['joint_contract']; lattice_comparisons=0; min_cross=None
    for tt in range(T):
        for z in range(3):
            for i in range(11):
                for zp,ip in ((z+1,i),(z,i+1)):
                    if zp<3 and ip<11:
                        a=sj['policy'][tt][z][i]; b=sj['policy'][tt][zp][ip]
                        assert all(x<=y for x,y in zip(a,b)); lattice_comparisons+=1
        for z in range(2):
            for i in range(10):
                d=sj['values'][tt][z+1][i+1]+sj['values'][tt][z][i]-sj['values'][tt][z+1][i]-sj['values'][tt][z][i+1]
                assert d>=0
                f=F(d,sj['denominators'][tt]); min_cross=f if min_cross is None else min(min_cross,f)
    envelope_states=envelope_check(sj)
    neural=smooth_neural_check(sj)
    fact=int_dp(factored=True)
    assert fact['values']==sj['values'] and fact['policy']==sj['policy']
    # Export complete exact optimal value and policy table for the primary joint problem.
    policyrows=[]
    for tt in range(T):
        for z in range(3):
            for i in range(11):
                s2,j=sj['policy'][tt][z][i]
                policyrows.append(dict(t=tt,regime=z,previous_contract=str(F(i,10)),stock=str(F(s2,2)),contract=str(F(j,10)),
                    value=str(F(sj['values'][tt][z][i],sj['denominators'][tt]))))
    savecsv('joint_policy_exact.csv',policyrows); savecsv('exact_dp_summary.csv',exactrows)
    save('exact_certificates.json',certificate)
    nested=[]; prior=None; B=F(3691,250)  # 3.4+6+3+1.2+0.97*1.2 = 14.764
    for n in (10,20,40,80,160):
        s=int_dp(n=n,factored=True); value=F(s['values'][0][1][n//2],s['denominators'][0])
        if prior is not None: assert value>=prior
        bd=B*sum(BETA**t for t in range(T))/(2*n)
        quad=(F(21,10)*sum(BETA**t for t in range(T))+BETA*F(3,5)*sum(BETA**t for t in range(T-1)))/(4*n*n)
        nested.append(dict(intervals=n,initial_value=str(value),value_decimal=float(value),
            semiconvex_quadratic_loss_bound=str(quad),quadratic_bound_decimal=float(quad),
            continuous_value_upper_exact=str(value+quad),continuous_value_upper_decimal=float(value+quad),
            continuous_contract_loss_bound=str(bd),bound_decimal=float(bd),bellman_candidates=s['bellman_candidates'],
            stock_stage_precomputations=s['stage_precomputations'],continuation_terms=s['continuation_terms']))
        prior=value
    savecsv('contract_grid_refinement.csv',nested)
    sim=simulation(sol); cond=conditioning(); pde,mesh=pde_sequence()
    j,f,o=[ledgers[m] for m in ('joint_contract','frozen_contract','physical_oracle')]
    k=lambda row: row['net_reward']+row['physical_cost']
    assert f['physical_cost']-j['physical_cost']==j['net_reward']-f['net_reward']-(k(j)-k(f))
    assert 0<=j['physical_cost']-o['physical_cost']<=k(j)-k(o)
    report=dict(review_commit='a91b707883b2408de58d9392e4fc546e08a00881',
        protocol_blob='055cec67f297166cca69b60d92be3faeb0cb86f4',
        protocol_sha256='ef3b61559baa1b015a23ee06ade6e3fa4097273e09ca314559f68047f7809b5b',
        protocol_bytes_verified=True,independent_fraction_states_checked=replays,expanded_action_exact_equality=True,dummy_gate_exact_equality=True,
        all_state_monotonicity_comparisons=lattice_comparisons,minimum_value_cross_difference=str(min_cross),
        exact_envelope_states_checked=envelope_states,greatest_optimal_pair_checked=True,
        compiled_c2_neural_critic_levels=len(neural),compiled_neural_policy_states_checked=sum(r['states_checked'] for r in neural),
        factored_exact_equality=True,exhaustive_candidates=sj['bellman_candidates'],factored_candidates=fact['bellman_candidates'],
        stage_precomputations=fact['stage_precomputations'],
        net_reward_gain_over_frozen=str(j['net_reward']-f['net_reward']),
        physical_cost_reduction_over_frozen=str(f['physical_cost']-j['physical_cost']),
        physical_excess_over_oracle=str(j['physical_cost']-o['physical_cost']),
        batches=64,episodes_per_batch=4096,training_pairs_per_conditioning_batch=2048,
        regressions=regressions(),python=platform.python_version(),numpy=np.__version__,
        execution_seconds=time.perf_counter()-started,
        scientific_scope='Exact finite-model certificates and analytic manufactured-PDE bounds; natural-data least-squares experiment; no new large-neural training or field experiment.')
    save('validation.json',report)
    save('sha256.json',{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir()) if p.name!='sha256.json'})
    print(json.dumps(report,indent=2)); print('\nEXACT DP'); print(json.dumps(exactrows,indent=2)); print('\nCONDITIONING'); print(json.dumps(cond,indent=2)); print('\nMESH'); print(json.dumps(mesh,indent=2))

if __name__=='__main__': main()
