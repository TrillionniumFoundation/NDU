"""Independent original-policy MINLP, not the cell polynomial or price DP.

SCIP bounds are floating-point solver bounds within declared tolerances. They
are independent numerical corroboration, not rational proof certificates.
"""
from pathlib import Path
from fractions import Fraction as F
import importlib.metadata
import time


def solve(model,budget,B,delta,price=(0,0,0),seconds=20):
    from pyscipopt import Model as SCIP, quicksum
    k=len(model.caps); r,q=float(model.r),float(model.q)
    alpha,beta,eta=map(float,price); result=[]
    for s in range(1,budget+1):
        opt=SCIP('original_lottery_policy'); opt.hideOutput()
        opt.setRealParam('limits/time',seconds)
        opt.setRealParam('limits/gap',1e-7)
        opt.setRealParam('numerics/feastol',1e-8)
        opt.setIntParam('randomization/randomseedshift',43)
        c=[opt.addVar(name=f'c{i}',lb=0,ub=1) for i in range(s)]
        y=[opt.addVar(name=f'y{j}',lb=0,ub=float(b)) for j,b in enumerate(model.caps)]
        prob=[[opt.addVar(name=f'p{j}_{i}',lb=0,ub=1) for i in range(s)] for j in range(k)]
        used=[[opt.addVar(name=f'z{j}_{i}',vtype='B') for i in range(s)] for j in range(k)]
        for i in range(s-1): opt.addCons(c[i]<=c[i+1])
        targets=[]
        for j,b in enumerate(model.caps):
            opt.addCons(quicksum(prob[j])==1)
            t=y[j]+quicksum(prob[j][i]*c[i] for i in range(s)); targets.append(t)
            opt.addCons(t<=float(b))
            for i in range(s):
                opt.addCons(prob[j][i]<=used[j][i])
                # y <= b and c <= 1 make 2 a safe inactive risk big-M.
                opt.addCons(y[j]+c[i]<=float(b+delta)+2*(1-used[j][i]))
        opt.addCons(quicksum(float(p)*t for p,t in zip(model.probabilities,targets))==float(B))
        reward=quicksum(float(model.probabilities[j])*(
            quicksum(prob[j][i]*(r*c[i]-q*c[i]*c[i]/2) for i in range(s))
            -float(model.gamma[j])*y[j]*y[j]/2) for j in range(k))
        reward-=quicksum(alpha*x*x+beta*x+eta for x in c)
        rho_max=max(eta,alpha+beta+eta)
        if alpha<0 and 0<-beta/(2*alpha)<1:
            rho_max=max(rho_max,eta-beta*beta/(4*alpha))
        lower=-sum(float(p*g*b*b)/2 for p,g,b in zip(model.probabilities,model.gamma,model.caps))-s*rho_max-1
        obj=opt.addVar(name='objective_hypograph',lb=lower,ub=r)
        opt.addCons(obj<=reward); opt.setObjective(obj,'maximize')
        opt.optimize()
        primal=opt.getPrimalbound(); dual=opt.getDualbound()
        result.append(dict(s=s,status=str(opt.getStatus()),lower=primal,upper=dual,
                           seconds=opt.getSolvingTime(),nodes=opt.getNNodes(),
                           gap=opt.getGap(),solutions=opt.getNSols()))
    return dict(lower=max(x['lower'] for x in result),upper=max(x['upper'] for x in result),
                sizes=result,pyscipopt=importlib.metadata.version('pyscipopt'),
                interpretation='Numerical global bounds, feasibility tolerance 1e-8, relative gap target 1e-7.')
