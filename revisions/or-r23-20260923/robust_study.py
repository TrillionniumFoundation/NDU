"""Predeclared R23 joint-misspecification study. Numerical outputs are proposals;
robust_exact.py independently licenses feasibility and each gain lower bound.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import sys,json,gzip,argparse,platform,time,hashlib
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from scipy import sparse
R=Path(__file__).resolve().parent;REPO=R.parent.parent
sys.path.insert(0,str(R.parent/'or-r22-20260923'))
from core import Tree,QP,contexts,frozen_models,normalize,time_equalities
sys.path.insert(0,str(R))
from robust_exact import VERTICES,coefficients,feasible,value,upper,repair,verify_outer,verify_robust,vector_record

def geometry(p,r,kind):
    n=len(p['qnum']);sign=[1 if (i//p['services'])%2==0 else -1 for i in range(n)]
    if kind=='robust':
        A=[[int(a)*(16+r*v*sign[i]) for i,a in enumerate(row)] for v in (-1,1) for row in p['Aacc']]
        A += [[16*int(a) for a in row] for row in p['C']]
        b=[0]*(2*len(p['Aacc']))+[(16-r)*int(c)*4 for c in p['capnum']]
        E=p['E']
    elif kind=='outer':
        A=[[16*int(a) for a in row] for row in p['Aacc']+p['C']]
        b=[r*sum(int(a)*max(int(z),32-int(z)) for a,z in zip(row,p['znum'])) for row in p['Aacc']]
        b += [(16+r)*int(c)*4 for c in p['capnum']]
        E=[list(row) for row in p['E']]
        for j in range(p['nodes']):
            dep=(j+1).bit_length()-1;rep=(1<<dep)-1
            if rep==j:continue
            for a in range(p['services']):
                row=[0]*n;row[j*p['services']+a]=1;row[rep*p['services']+a]=-1;E.append(row)
    elif kind=='nominal':
        A=[[16*int(a) for a in row] for row in p['Aacc']+p['C']]
        b=[0]*len(p['Aacc'])+[64*int(c) for c in p['capnum']];E=p['E']
    else:raise ValueError(kind)
    return {'A_num':A,'budget_num':b,'E':E}

def setup(p,g,full=True):
    n=len(p['qnum']);A=np.asarray(g['A_num'],float)/16;E=np.asarray(g['E'],float);B=np.asarray(p['B'],float)
    U=np.asarray(p['Unum'],float)/32;d=np.asarray(p['qnum'],float)/16
    I=sparse.eye(n,format='csc');Z=sparse.csc_matrix((n,n));m=len(A);e=len(E)
    M=sparse.vstack([sparse.hstack([I,Z]),sparse.hstack([sparse.csc_matrix(A),sparse.csc_matrix((m,n))]),sparse.hstack([sparse.csc_matrix(E),sparse.csc_matrix((e,n))]),sparse.hstack([sparse.csc_matrix(B),-I]),sparse.hstack([-sparse.csc_matrix(B),-I])],format='csc')
    lo=np.r_[-np.asarray(p['znum'])/32,np.full(m,-np.inf),np.zeros(e),np.full(2*n,-np.inf)]
    hi=np.r_[(32-np.asarray(p['znum']))/32,np.asarray(g['budget_num'])/512,np.zeros(e),-np.asarray(p['vnum'])/32,np.asarray(p['vnum'])/32]
    H=np.diag(d)+(U.T@U if full else 0)
    P=sparse.block_diag([sparse.csc_matrix(H),sparse.csc_matrix((n,n))],format='csc')
    return P,M,lo,hi

def dual_record(p,g,c,r,v,x,d):
    n=len(p['qnum']);m=len(g['A_num']);e=len(g['E']);den=10**9
    U=np.asarray(p['Unum'])/32
    pp=np.rint((U@x[:n])*den).astype(np.int64)
    mu=np.maximum(0,np.rint(d[n:n+m]*den)).astype(np.int64)
    nu=np.rint(d[n+m:n+m+e]*den).astype(np.int64)
    sw=np.rint((d[n+m+e:n+m+e+n]-d[n+m+e+n:n+m+e+2*n])*den).astype(np.int64)
    _,ln=coefficients(p,c,r,v);cap=np.array([den*ln*int(k)//8192 for k in p['knum']],dtype=np.int64)
    sw=np.clip(sw,-cap,cap)
    return {'den':den,'p':pp.tolist(),'s':sw.tolist(),'mu':mu.tolist(),'nu':nu.tolist()}

def solve(p,g,c,r,v,price=None):
    P,M,lo,hi=setup(p,g,full=price is None);n=len(p['qnum'])
    bn,ln=coefficients(p,c,r,v);b=np.array(bn)/8192;lam=ln/1024
    q=np.r_[-b,lam*np.asarray(p['knum'])/8]
    if price is not None:q[:n] += (np.asarray(p['Unum'])/32).T@price
    solver=QP(P,M,lo,hi,eps=1e-8)
    try:x,d,it=solver.solve(q,previous=False)
    finally:solver.close()
    return x,d,it

def anchor(p,g):
    n=len(p['qnum']);sv=p['services'];x=[F(0)]*sv+[F(-1)]*(n-sv)
    for a in range(sv):x[a]=-sum((int(p['E'][a][i])*x[i] for i in range(sv,n)),F(0))/int(p['E'][a][a])
    scale=F(1)
    for xx,z in zip(x,p['znum']):
        if xx>0:scale=min(scale,F(32-int(z),64)/xx)
        elif xx<0:scale=min(scale,F(-int(z),64)/xx)
    for row,b in zip(g['A_num'],g['budget_num']):
        vv=sum((int(a)*xx for a,xx in zip(row,x)),F(0))
        if vv>0:scale=min(scale,F(int(b),64)/vv)
    return [scale*xx for xx in x]

def maximin(p,g,c,r,uu):
    P,M,lo,hi=setup(p,g,True);n=len(p['qnum'])
    M=sparse.hstack([M,sparse.csc_matrix((M.shape[0],1))],format='csc')
    vv=np.asarray(p['vnum'])/32;k=np.asarray(p['knum'])/8
    extra=[];rhs=[]
    for v,u in zip(VERTICES,uu):
        bn,ln=coefficients(p,c,r,v);b=np.array(bn)/8192;lam=ln/1024
        extra.append(np.r_[-b,lam*k,1.]);rhs.append(float(lam*np.dot(k,np.abs(vv))-float(u)))
    M=sparse.vstack([M,sparse.csc_matrix(extra)],format='csc')
    lo=np.r_[lo,np.full(len(extra),-np.inf)];hi=np.r_[hi,rhs]
    P=sparse.block_diag([P,sparse.csc_matrix((1,1))],format='csc')
    solver=QP(P,M,lo,hi,eps=1e-8)
    try:x,d,it=solver.solve(np.r_[np.zeros(2*n),-1.],previous=False)
    finally:solver.close()
    return x[:n],it

def run(pilot=False):
    spec=json.loads((R/'DESIGN.json').read_text());count=spec['pilot' if pilot else 'validation']['contexts'];seed=spec['pilot' if pilot else 'validation']['seed']
    out=R/('pilot' if pilot else 'results');out.mkdir(exist_ok=True)
    tree=Tree();p=tree.primitives();mods=frozen_models();cc=contexts(seed,count,tree.rank)
    prices={k:np.mean([m[k].predict(normalize(cc,tree.rank)) for m in mods],axis=0) for k in ['tanh-gradient','rbf-direct']}
    geometries={};records=[];failures=[];started=time.perf_counter()
    for r in spec['uncertainty']['radii_numerator_over_16']:
        for kind in ('robust','outer','nominal'):geometries[f'{r}-{kind}']=geometry(p,r,kind)
        verify_outer(p,geometries[f'{r}-outer'],r);verify_robust(p,geometries[f'{r}-robust'],r)
    # Unmodified primitives and integer geometry are the verifier's only inputs.
    (out/'primitives.json').write_text(json.dumps(p)+'\n')
    (out/'geometries.json').write_text(json.dumps(geometries)+'\n')
    with gzip.open(out/'certificates.jsonl.gz','wt') as f:
      for r in spec['uncertainty']['radii_numerator_over_16']:
        gr=geometries[f'{r}-robust'];go=geometries[f'{r}-outer'];gn=geometries[f'{r}-nominal'];anc=anchor(p,gr);an=anchor(p,gn)
        for j,c in enumerate(cc):
            c=list(map(int,c));t=time.perf_counter();bounds=[];duals=[]
            for vi,v in enumerate(VERTICES):
                try:
                    x,d,it=solve(p,go,c,r,v);dual=dual_record(p,go,c,r,v,x,d)
                except RuntimeError as err:
                    failures.append({'r':r,'id':j,'kind':'outer','vertex':vi,'error':str(err)})
                    dual={'den':1,'p':[0]*p['rank'],'s':[0]*tree.n,'mu':[0]*len(go['A_num']),'nu':[0]*len(go['E'])}
                u=upper(p,go,c,r,v,dual);bounds.append(u);duals.append(dual)
            shared=time.perf_counter()-t
            item={'r':r,'id':j,'context':c,'outer_duals':duals,'outer_upper':[str(u) for u in bounds],'shared_comparator_seconds':shared,'methods':{},'nominal_diagnostics':{}}
            for key in ['tanh-gradient','rbf-direct']:
                name='protected-'+key;t=time.perf_counter();eta=prices[key][j]
                # The response uses observed nominal coefficients on the robust set.
                try:raw,d,it=solve(p,gr,c,0,VERTICES[0],price=eta)
                except RuntimeError as err:
                    failures.append({'r':r,'id':j,'kind':name,'error':str(err)});raw=np.zeros(tree.n)
                rec=repair(p,gr,raw,anc)
                gains=[value(p,c,r,v,rec['x_num'],rec['x_den']) for v in VERTICES]
                lower=min(a-b for a,b in zip(gains,bounds))
                # Outside gate is only against zero; not an optimized-comparator guarantee.
                if min(gains)<0:
                    rec=vector_record([F(0)]*tree.n);rec['repair_fraction']='0';rec['outside_gate']=True;gains=[F(0)]*8;lower=-max(bounds)
                else:rec['outside_gate']=False
                rec.update(vertex_values=[str(a) for a in gains],robust_gain_lower=str(lower),own_seconds=time.perf_counter()-t)
                item['methods'][name]=rec
                # Unsafe nominal proposals are retained only as diagnostics, never deployed.
                try:
                    raw,d,it=solve(p,gn,c,0,VERTICES[0],price=eta);nr=repair(p,gn,raw,an)
                    try:feasible(p,gr,nr['x_num'],nr['x_den']);valid=True
                    except AssertionError:valid=False
                    nr['robust_feasible']=valid;item['nominal_diagnostics'][key]=nr
                except RuntimeError as err:failures.append({'r':r,'id':j,'kind':'nominal-'+key,'error':str(err)})
            t=time.perf_counter()
            try:raw,it=maximin(p,gr,c,r,bounds)
            except RuntimeError as err:failures.append({'r':r,'id':j,'kind':'classical-maximin','error':str(err)});raw=np.zeros(tree.n)
            rec=repair(p,gr,raw,anc);gains=[value(p,c,r,v,rec['x_num'],rec['x_den']) for v in VERTICES]
            lower=min(a-b for a,b in zip(gains,bounds))
            if min(gains)<0:
                rec=vector_record([F(0)]*tree.n);rec['repair_fraction']='0';rec['outside_gate']=True;gains=[F(0)]*8;lower=-max(bounds)
            else:rec['outside_gate']=False
            rec.update(vertex_values=[str(a) for a in gains],robust_gain_lower=str(lower),own_seconds=time.perf_counter()-t)
            item['methods']['classical-robust-maximin']=rec
            f.write(json.dumps(item)+'\n');f.flush()
            for name,rec in item['methods'].items():
                row={'r':r,'id':j,'method':name,'robust_gain_lower':float(F(rec['robust_gain_lower'])),'worst_outside_gain':min(float(F(a)) for a in rec['vertex_values']),'repair_fraction':float(F(rec['repair_fraction'])),'own_seconds':rec['own_seconds'],'shared_comparator_seconds':shared,'outside_gate':rec['outside_gate']}
                if name.startswith('protected-'):row['nominal_robust_feasible']=item['nominal_diagnostics'].get(name[10:],{}).get('robust_feasible',False)
                records.append(row)
            if (j+1)%8==0 or pilot:print('radius',r,'context',j+1,'/',count,'elapsed',round(time.perf_counter()-started,1),flush=True)
    (out/'rows.json').write_text(json.dumps(records)+'\n');(out/'failures.json').write_text(json.dumps(failures,indent=2)+'\n')
    ss=[]
    for r in spec['uncertainty']['radii_numerator_over_16']:
      for name in ['protected-tanh-gradient','protected-rbf-direct','classical-robust-maximin']:
        rr=[a for a in records if a['r']==r and a['method']==name];g=[a['robust_gain_lower'] for a in rr]
        ss.append({'r':r,'rho':r/16,'method':name,'n':len(rr),'mean_robust_gain_lower':float(np.mean(g)),'min_robust_gain_lower':min(g),'positive_fraction':sum(a>0 for a in g)/len(g),'nominal_unsafe_fraction':None if not name.startswith('protected-') else sum(not a['nominal_robust_feasible'] for a in rr)/len(rr),'outside_gates':sum(a['outside_gate'] for a in rr),'max_repair_fraction':max(a['repair_fraction'] for a in rr)})
    summary={'status':'EXECUTED','pilot':pilot,'contexts':count,'policy_records':len(records),'vertex_comparator_certificates':count*4*8,'nominal_diagnostic_records':count*4*2,'failed_solves':len(failures),'summary':ss,'seconds':time.perf_counter()-started,'host':platform.platform(),'python':platform.python_version(),'numpy':np.__version__,'uncertainty_scope':spec['uncertainty'],'design_sha256':hashlib.sha256((R/'DESIGN.json').read_bytes()).hexdigest()}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2),flush=True)
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--pilot',action='store_true');run(a.parse_args().pilot)
