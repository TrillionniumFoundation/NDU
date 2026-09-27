from rational import F,digest
from price_path import normalize,allocate
def scip_solve(spec,remaining,epsilon):
    from pyscipopt import Model,quicksum
    d,a,rho,B,m=normalize(spec);s=Model('NDU exact convex original formulation');s.hideOutput();s.setRealParam('limits/time',max(.001,remaining));s.setRealParam('limits/absgap',float(epsilon));s.setRealParam('limits/gap',0.0);s.setIntParam('parallel/maxnthreads',1)
    x=[s.addVar(vtype='B',name=f'x{i}') for i in range(len(a))]
    y=[s.addVar(lb=0,ub=float(b),name=f'y{j}') for j,b in enumerate(d.caps)]
    h=[s.addVar(lb=0,name=f'h{j}') for j in range(len(y))];ps={};zs={}
    for j in range(len(y)):
        eligible=[i for i,z in enumerate(a) if z<=d.ceilings[j]]
        for i in eligible:
            ps[j,i]=s.addVar(lb=0,ub=1,name=f'p{j}_{i}');zs[j,i]=s.addVar(vtype='B',name=f'z{j}_{i}')
            s.addCons(ps[j,i]<=zs[j,i]);s.addCons(zs[j,i]<=x[i]);M=max(F(0),d.caps[j]+a[i]-d.ceilings[j])
            s.addCons(y[j]+float(M)*zs[j,i]<=float(d.ceilings[j]-a[i]+M))
        s.addCons(quicksum(ps[j,i] for i in eligible)==1)
        s.addCons(y[j]+quicksum(float(a[i])*ps[j,i] for i in eligible)<=float(d.caps[j]))
        if d.gamma[j]:s.addCons(h[j]>=float(d.gamma[j]/2)*y[j]*y[j])
        else:s.addCons(h[j]==0)
    s.addCons(quicksum(x)<=m);s.addCons(quicksum(float(d.weights[j])*(y[j]+quicksum(float(a[i])*ps[j,i] for jj,i in ps if jj==j)) for j in range(len(y)))==float(B))
    s.setObjective(quicksum(float(rho[i])*x[i] for i in range(len(x)))+quicksum(float(d.weights[j])*h[j] for j in range(len(y)))-quicksum(float(d.weights[j]*d.reward(j,a[i]))*p for (j,i),p in ps.items()),'minimize')
    s.optimize();sol=s.getBestSol();book=tuple(a[i] for i in range(len(a)) if sol is not None and s.getSolVal(sol,x[i])>.5)
    p=allocate(d,book if book and book[0]<=min(B,min(d.caps)) and len(book)<=m else (a[0],),B,dict(zip(a,rho)))
    ub=-s.getDualbound();valid=abs(ub)<1e19
    return dict(status='NUMERICAL_'+str(s.getStatus()),lower=p['value'],numerical_upper=ub if valid else None,numerical_bound_consistent=bool(valid and ub>=float(p['value'])-1e-8),numerical_absolute_gap=max(0,ub-float(p['value'])) if valid else None,solver_gap=s.getGap() if sol is not None else None,solver_nodes=s.getNNodes(),envelope_error=0,certificate=dict(schema='NDU-R59-SCIP-numerical-v1',instance=spec,instance_sha256=digest(spec),policy=p,numerical_upper=ub if valid else None,scope='Only the feasible policy is independently checked; the SCIP bound is numerical.'))
