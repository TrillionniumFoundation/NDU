"""R25 new experiments. Proposals: OSQP/HiGHS/IPOPT and singleton algebra. Acceptance: independent rational audit.
Run from a repository checkout. No network, pretrained models, or hidden data.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import gzip,json,sys,time,platform,copy,math
from pathlib import Path
from fractions import Fraction as F
import numpy as np
R=Path(__file__).resolve().parent; REPO=R.parent.parent; OUT=R/'results';OUT.mkdir(exist_ok=True)
sys.path[:0]=[str(R.parent/'or-r24-20260923'),str(R.parent/'or-r23-20260923')]
from interior_exact import make_model,cache,vector_record,unpack,feasible,objective,upper,repair_time
from robust_study import setup,QP

CLASSES=('fixed amendment','time-only','current regime','memory two','full history')
def groupids(p,kind):
    result=[];lookup={}
    for j in range(p['nodes']):
        bits=bin(j+1)[3:]; t=len(bits)
        info={'fixed amendment':(), 'time-only':(t,), 'current regime':(t,bits[-1:]),
              'memory two':(t,bits[-2:]), 'full history':(j,)}[kind]
        for a in range(p['services']):
            key=info+(a,)
            if key not in lookup:lookup[key]=len(lookup)
            result.append(lookup[key])
    return result

def restrict(p,m,kind):
    m={k:copy.deepcopy(v) for k,v in m.items() if not k.startswith('_')}
    n=len(p['qnum']); ids=groupids(p,kind); rep={}
    m['E']=[list(map(F,row)) for row in p['E']]
    for i,g in enumerate(ids):
        if g in rep:
            row=[F(0)]*n;row[i]=F(1);row[rep[g]]=F(-1);m['E'].append(row)
        else:rep[g]=i
    return m,ids

def repair(p,m,raw,ids):
    if len(set(ids))==p['services']:
        ans=vector_record([F(0)]*len(raw));feasible(p,m,ans);return ans
    ng=max(ids)+1; amp=[F(0)]*ng; counts=[0]*ng
    for v,g in zip(raw,ids):amp[g]+=F(round(float(v)*10**10),10**10);counts[g]+=1
    amp=[a/c for a,c in zip(amp,counts)]
    sv=p['services']; n=len(raw)
    for a in range(sv):
        rg=ids[a]; assert ids.count(rg)==1
        amp[rg]=-sum((F(int(p['E'][a][i]))*amp[ids[i]] for i in range(sv,n)),F(0))/F(int(p['E'][a][a]))
    x=[amp[g] for g in ids]
    # Strict anchor is in every date-refining information class.
    ac=[F(0)]*sv+[F(-1)]*(n-sv)
    for a in range(sv):ac[a]=-sum((F(int(p['E'][a][i]))*ac[i] for i in range(sv,n)),F(0))/F(int(p['E'][a][a]))
    cache(p,m);rows=list(zip(m['_A'],m['rhs']))
    rows += [([(i,F(1))],F(32-int(z),32)) for i,z in enumerate(p['znum'])]
    rows += [([(i,F(-1))],F(int(z),32)) for i,z in enumerate(p['znum'])]
    scale=F(1)
    for row,rhs in rows:
        v=sum((a*ac[i] for i,a in row),F(0))
        if v>0:scale=min(scale,rhs/(2*v))
    assert scale>0
    ac=[a*scale for a in ac];alpha=F(0)
    for row,rhs in rows:
        xx=sum((a*x[i] for i,a in row),F(0));aa=sum((a*ac[i] for i,a in row),F(0))
        assert aa<rhs,(aa,rhs)
        if xx>rhs:alpha=max(alpha,(xx-rhs)/(xx-aa))
    assert 0<=alpha<1
    rec=vector_record([(1-alpha)*a+alpha*b for a,b in zip(x,ac)]);rec['repair_fraction']=str(alpha)
    feasible(p,m,rec);return rec

def solve(p,m,ids=None):
    n=len(p['qnum']);nm=len(m['A']);ne=len(m['E']);den=10**10
    g={'A_num':[[float(a*16) for a in row] for row in m['A']],
       'budget_num':[float(a*512) for a in m['rhs']],'E':m['E']}
    P,M,lo,hi=setup(p,g,True)
    q=np.r_[-np.asarray(m['b'],float),float(m['lam'])*np.asarray(p['knum'])/8]
    start=time.perf_counter()
    if ids is not None and len(set(ids))==p['services']:
        from functools import reduce
        sv=p['services'];ss=[m['lam']*F(int(k),8)*(1 if v>0 else -1 if v<0 else 0) for k,v in zip(p['knum'],p['vnum'])]
        residual=[m['b'][i]-sum((F(int(row[i]))*a for row,a in zip(p['B'],ss)),F(0)) for i in range(n)]
        nu=[sum((residual[i] for i in range(a,n,sv)),F(0))/sum((F(int(p['E'][a][i])) for i in range(a,n,sv)),F(0)) for a in range(sv)]
        nu += [residual[i]-nu[i%sv]*F(int(p['E'][i%sv][i])) for i in range(sv,n)]
        den=reduce(math.lcm,(a.denominator for a in ss+nu),1)
        dual={'den':den,'p':[0]*p['rank'],'s':[int(a*den) for a in ss],'mu':[0]*nm,'nu':[int(a*den) for a in nu]}
        rec=vector_record([F(0)]*n);feasible(p,m,rec);ub=upper(p,m,dual);assert ub==0
        return {'policy':rec,'dual':dual,'lower':'0','upper':'0','gap':0.0,'solver_seconds':0.0,'iterations':0,'proposal':'exact singleton class'}
    attempts=[];engine="OSQP"
    if ids is not None and p["services"]==1:
        import casadi as ca
        HH=ca.DM(P);AA=ca.DM(M)
        proposer=ca.conic('r25_hierarchy','highs',{'h':HH.sparsity(),'a':AA.sparsity()},
          {'highs':{'output_flag':False,'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9},'error_on_fail':True})
        try:
            result=proposer(h=HH,g=q,a=AA,lba=lo,uba=hi)
            x=np.asarray(result['x']).ravel();d=np.asarray(result['lam_a']).ravel();it=int(proposer.stats()['qp_iteration_count']);engine='HiGHS'
        except RuntimeError as exc:
            attempts.append({'engine':'HiGHS','error':str(exc)})
            yy=ca.MX.sym('y',2*n);ff=ca.dot(yy,HH@yy)/2+ca.dot(ca.DM(q),yy)
            opt=ca.nlpsol('r25_fallback','ipopt',{'x':yy,'f':ff,'g':AA@yy},
                {'print_time':False,'ipopt.print_level':0,'ipopt.sb':'yes','ipopt.tol':1e-10,'ipopt.max_iter':3000})
            rr=opt(x0=np.r_[np.zeros(n),np.abs(np.asarray(p['vnum'])/32)],lbg=lo,ubg=hi)
            x=np.asarray(rr['x']).ravel();d=np.asarray(rr['lam_g']).ravel();it=int(opt.stats()['iter_count']);engine='IPOPT fallback' 
    else:
        solver=QP(P,M,lo,hi,eps=1e-9)
        try:x,d,it=solver.solve(q,previous=False)
        finally:solver.close()
    sec=time.perf_counter()-start
    dual={'den':den,'p':np.rint((np.asarray(p['Unum'])/32@x[:n])*den).astype(np.int64).tolist(),
          'mu':np.maximum(0,np.rint(d[n:n+nm]*den)).astype(np.int64).tolist(),
          'nu':np.rint(d[n+nm:n+nm+ne]*den).astype(np.int64).tolist()}
    ss=np.rint((d[n+nm+ne:n+nm+ne+n]-d[n+nm+ne+n:n+nm+ne+2*n])*den).astype(np.int64)
    cap=np.array([int(m['lam']*F(int(k),8)*den) for k in p['knum']],dtype=np.int64)
    dual['s']=np.clip(ss,-cap,cap).tolist()
    rec=repair_time(p,m,x[:n]) if ids is None else repair(p,m,x[:n],ids)
    lower=objective(p,m,rec);ub=upper(p,m,dual)
    assert ub>=lower, 'weak duality failed'
    return {'policy':rec,'dual':dual,'lower':str(lower),'upper':str(ub),'gap':float(ub-lower),'solver_seconds':sec,'iterations':it,'proposal':engine,'failed_proposals':attempts}

def serial(m):return {k:([[str(a) for a in row] for row in v] if k in ('A','E') else [str(a) for a in v] if isinstance(v,list) else str(v)) for k,v in m.items() if not k.startswith('_')}
def clean(p):return {k:v for k,v in p.items() if not k.startswith('_')}
def dump(name,x): (OUT/name).write_text(json.dumps(x,indent=2)+'\n')

def canonical(context):
    """Public Markov coefficients, deterministic tier baseline 1/2, 6 dates.
    Integer weights are probability weights multiplied by 32, not observations.
    """
    N=63;c=[2**(5-((j+1).bit_length()-1)) for j in range(N)]
    p={'nodes':N,'services':1,'rank':1,'znum':[16]*N,'Unum':[[0]*N],
       'qnum':[],'bnum':[0]*N,'knum':[8*a for a in c],'vnum':[0]*N,'B':[],'E':[c],'Aacc':[],'C':[],'capnum':[]}
    reward=[]
    for j in range(N):
        depth=(j+1).bit_length()-1;reg=0 if j==0 else (1 if j%2==0 else -1)
        p['qnum'].append((16+4*reg)*c[j])
        reward.append(F(c[j])*(F(context[0],32)+F(reg*context[1],32)+F(depth*context[2],128)))
        row=[0]*N;row[j]=1
        if j:row[(j-1)//2]=-1
        p['B'].append(row)
    caps=[]
    for j in range(1,N):
        row=[0]*N
        for i in range(j,N):
            k=i
            while k>j:k=(k-1)//2
            if k==j:row[i]=c[i]
        p['Aacc'].append(row)
        depth=(j+1).bit_length()-1;reg=1 if j%2==0 else -1
        caps.append(F(c[j]*(6-depth)*(3+reg),64))
    m={'A':[list(map(F,row)) for row in p['Aacc']],'rhs':caps,'E':[list(map(F,c))],
       'b':reward,'lam':F(context[3],128)}
    return p,m

def hierarchy():
    old=R.parent/'or-r23-20260923/results';p=json.loads((old/'primitives.json').read_text())
    with gzip.open(old/'certificates.jsonl.gz','rt') as f:items=[json.loads(line) for line in f]
    contexts=[a['context'] for a in items if a['r']==0][:24]
    rng=np.random.default_rng(250923);designs=[[int(rng.integers(8,25)),int(rng.integers(12,33)),int(rng.integers(-6,7)),int(rng.integers(1,6))] for _ in range(24)]
    records=[]
    for family in ('R24 amendments','Markov service tiers'):
      for j,context in enumerate(contexts if family=='R24 amendments' else designs):
        if family=='R24 amendments': pp=p;base=make_model(pp,context,0,[0,0,0])
        else:pp,base=canonical(context)
        entry={'family':family,'id':j,'context':context,'primitives':clean(pp),'classes':[]}
        for kind in CLASSES:
            print('solve',family,j,kind,flush=True);m,ids=restrict(pp,base,kind);ans=solve(pp,m,ids)
            entry['classes'].append({'name':kind,'model':serial(m),'groups':ids,**ans})
        vals=[F(a['lower']) for a in entry['classes']]
        for a,b in zip(entry['classes'],entry['classes'][1:]):assert F(a['lower'])<=F(b['upper'])
        entry['increments']=[float(b-a) for a,b in zip(vals,vals[1:])]
        records.append(entry);print('hierarchy',family,j,entry['increments'],flush=True)
    with gzip.open(OUT/'hierarchy_certificates.jsonl.gz','wt') as fh:
        for entry in records:fh.write(json.dumps(entry)+'\n')
    summary=[]
    for family in ('R24 amendments','Markov service tiers'):
        rows=[r for r in records if r['family']==family];arr=np.array([r['increments'] for r in rows]);tot=arr.sum(axis=1)
        summary.append({'family':family,'instances':len(rows),'increment_means':arr.mean(axis=0).tolist(),'increment_min':arr.min(axis=0).tolist(),
        'mean_total':float(tot.mean()),'shares_of_mean_total':(arr.mean(axis=0)/tot.mean()).tolist(),
        'mean_increment_interval_lower':[float(sum((max(F(0),F(r['classes'][j+1]['lower'])-F(r['classes'][j]['upper'])) for r in rows),F(0))/len(rows)) for j in range(4)],
        'mean_increment_interval_upper':[float(sum((F(r['classes'][j+1]['upper'])-F(r['classes'][j]['lower']) for r in rows),F(0))/len(rows)) for j in range(4)],
        'max_gap':max(a['gap'] for r in rows for a in r['classes'])})
    dump('hierarchy_summary.json',{'status':'EXECUTED','certificates':len(records)*5,'summary':summary,
    'interpretation':'R24 ties amendments to heterogeneous legacy tiers; Markov family ties actual tiers. Current regime never includes inherited tier or promised payment.'})

def fine_model(p,context,rho,theta,outer):
    # make_model is affine in rho. Reconstruct rational coefficients from 0 and 1/16.
    m0=make_model(p,context,0,theta,outer);m1=make_model(p,context,1,theta,outer);t=16*rho
    m={}
    for key in ('b','rhs'):m[key]=[a+t*(b-a) for a,b in zip(m0[key],m1[key])]
    m['A']=[[a+t*(b-a) for a,b in zip(ar,br)] for ar,br in zip(m0['A'],m1['A'])]
    m['E']=m0['E'];m['lam']=m0['lam']+t*(m1['lam']-m0['lam']);return m

def radius_study():
    old=R.parent/'or-r23-20260923/results';p=json.loads((old/'primitives.json').read_text())
    with gzip.open(old/'certificates.jsonl.gz','rt') as f:items=[json.loads(line) for line in f]
    contexts=[a['context'] for a in items if a['r']==0][:8]
    radii=[F(0)]+[F(1,2**k) for k in (16,14,12,10,8,6,4,3,2)]
    records=[]
    for i,context in enumerate(contexts):
        theta=[(-5+2*i)%13-6,(3+i)%11-5,(7+i)%13-6]
        for rho in radii:
            r={'id':i,'context':context,'rho':str(rho),'theta':theta}
            for kind,flag in [('true',False),('outer',True)]:
                m=fine_model(p,context,rho,theta,flag);r[kind]={'model':serial(m),**solve(p,m)}
            r['outer_slack_upper']=float(F(r['outer']['upper'])-F(r['true']['lower']))
            records.append(r)
        print('radius',i,flush=True)
    with gzip.open(OUT/'radius_certificates.jsonl.gz','wt') as fh:
        for row in records:fh.write(json.dumps(row)+'\n')
    dump('radius_primitives.json',clean(p))
    summary=[{'rho':str(rho),'mean_outer_slack_upper':float(np.mean([r['outer_slack_upper'] for r in records if r['rho']==str(rho)]))} for rho in radii]
    dump('radius_summary.json',{'status':'EXECUTED','certificates':2*len(records),'summary':summary,
    'max_gap':max(r[k]['gap'] for r in records for k in ('true','outer'))})

def sqrt_upper(x,den=10**12):
    assert x>=0
    n=(x.numerator*den*den+x.denominator-1)//x.denominator
    k=math.isqrt(n)
    if k*k<n:k+=1
    return F(k,den)

def cache_study():
    import sympy as sp
    old=R.parent/'or-r23-20260923/results';p=json.loads((old/'primitives.json').read_text());n=len(p['qnum'])
    base=make_model(p,[0]*p['rank']+[29],0,[0,0,0]); E=sp.Matrix(base['E']);V=sp.Matrix.hstack(*E.nullspace())
    D=sp.diag(*[sp.Rational(int(q),16) for q in p['qnum']]);U=sp.Matrix([[sp.Rational(int(a),32) for a in row] for row in p['Unum']])
    LY=(U*V*(V.T*D*V).inv()*V.T*U.T).trace();LF=F(int(LY.p),int(LY.q))
    anchors=[];rng=np.random.default_rng(25923)
    for j in range(4):
        h=[F(int(a),16) for a in rng.integers(-12,13,size=p['rank'])]
        m=copy.deepcopy(base);m['b']=[b+sum((F(int(p['Unum'][a][i]),32)*h[a] for a in range(p['rank'])),F(0)) for i,b in enumerate(base['b'])]
        ans=solve(p,m);x=unpack(ans['policy']);grad=[sum((F(int(a),32)*xx for a,xx in zip(row,x)),F(0)) for row in p['Unum']]
        anchors.append({'h':list(map(str,h)),'gradient':list(map(str,grad)),'model':serial(m),**ans})
    queries=[]
    for j in range(32):
        a=anchors[j%4];h0=list(map(F,a['h']));h=[z+F(int(v),256) for z,v in zip(h0,rng.integers(-4,5,size=p['rank']))]
        m=copy.deepcopy(base);m['b']=[b+sum((F(int(p['Unum'][a][i]),32)*h[a] for a in range(p['rank'])),F(0)) for i,b in enumerate(base['b'])]
        exact=solve(p,m);envelopes=[]
        for a in anchors:
            dh=[x-F(y) for x,y in zip(h,a['h'])];s=sum((x*x for x in dh),F(0));delta=F(a['upper'])-F(a['lower'])
            val=F(a['upper'])+sum((F(g)*d for g,d in zip(a['gradient'],dh)),F(0))+sqrt_upper(2*LF*delta)*sqrt_upper(s)+LF*s/2
            envelopes.append(val)
        cached=min(envelopes);assert cached>=F(exact['lower'])
        queries.append({'h':list(map(str,h)),'model':serial(m),'envelopes':list(map(str,envelopes)),
        'cached_upper':str(cached),'slack_upper':float(cached-F(exact['lower'])),**exact})
    dump('cache_primitives.json',clean(p));dump('cache_certificates.json',{'L':str(LF),'anchors':anchors,'queries':queries})
    dump('cache_summary.json',{'status':'EXECUTED','anchors':4,'queries':32,'query_optimizer_calls':0,'validation_optimizer_calls':32,
    'L_trace_bound':float(LF),'max_slack_upper':max(q['slack_upper'] for q in queries),'mean_slack_upper':float(np.mean([q['slack_upper'] for q in queries])),
    'scope':'Fixed participation geometry, information restriction, switching coefficient; reward perturbations only. Validation solves are offline, not charged as deployment.'})

if __name__=='__main__':
    part=sys.argv[1] if len(sys.argv)>1 else 'all';start=time.perf_counter()
    for name,fn in [('hierarchy',hierarchy),('radius',radius_study),('cache',cache_study)]:
        if part in ('all',name):fn()
    dump('execution_'+part+'.json',{'python':sys.version,'platform':platform.platform(),'seconds':time.perf_counter()-start,'numpy':np.__version__,'source':'R25 new studies; proposal solver excluded from rational replay'})
