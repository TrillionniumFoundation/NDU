"""Reoptimized accepted time-only amendments, with exact class-preserving repair."""
from core import *
from functools import reduce
from math import lcm
from copy import deepcopy

class TimeComparator:
    def __init__(self,s):
        self.s=s; self.extra=time_equalities(s); self.solver=Lifted(s,eps=1e-9,extra_equalities=self.extra)
        self.depth=[(j+1).bit_length()-1 for j in range(s.nodes)]; self.maxdepth=max(self.depth)
        # Strictly feasible in every inequality; equality restrictions are exact.
        x=[F(-1) if j else F(0) for j in range(s.nodes) for a in range(s.services)]
        for a in range(s.services):
            x[a]=-sum((int(s.c[j*s.services+a])*x[j*s.services+a] for j in range(1,s.nodes)),F(0))/int(s.c[a])
        scale=F(1)
        for i,z in enumerate(s.znum):
            if x[i]>0:scale=min(scale,F(32-int(z),64)/x[i])
            elif x[i]<0:scale=min(scale,F(-int(z),64)/x[i])
        for row,cap in zip(s.C,s.capnum):
            v=sum((int(v)*xx for v,xx in zip(row,x)),F(0))
            if v>0:scale=min(scale,F(int(cap),16)/v)
        self.anchor=[scale*xx for xx in x]
        self.p=deepcopy(s.primitives()); self.p['E']=self.p['E']+self.extra.toarray().astype(int).tolist()
        self.eq_extra_rows=self.extra.toarray().astype(int).tolist()
        self.constraints=[]
        for i,z in enumerate(s.znum):
            self.constraints.extend([([(i,1)],F(32-int(z),32)), ([(i,-1)],F(int(z),32))])
        for row,b in zip(np.vstack([s.Aacc,s.C]),np.r_[np.zeros(len(s.Aacc),dtype=int),s.capnum]):
            # Capacity budget /8, continuation budget zero.
            self.constraints.append(([(i,int(v)) for i,v in enumerate(row) if v],F(int(b),8)))
        self.anchor_values=[sum((a*self.anchor[i] for i,a in row),F(0)) for row,b in self.constraints]
        assert all(v<b for v,(row,b) in zip(self.anchor_values,self.constraints))
    def repair(self,raw):
        s=self.s; z={}
        for dep in range(1,self.maxdepth+1):
            js=[j for j,d in enumerate(self.depth) if d==dep]
            for a in range(s.services):
                z[dep,a]=F(int(round(float(np.mean([raw[j*s.services+a] for j in js]))*10**10)),10**10)
        for a in range(s.services):
            z[0,a]=-sum((int(s.c[j*s.services+a])*z[self.depth[j],a] for j in range(1,s.nodes)),F(0))/int(s.c[a])
        x=[z[self.depth[j],a] for j in range(s.nodes) for a in range(s.services)]
        alpha=F(0)
        for (row,b),anc in zip(self.constraints,self.anchor_values):
            val=sum((v*x[i] for i,v in row),F(0))
            if val>b:alpha=max(alpha,(val-b)/(val-anc))
        assert 0<=alpha<1
        x=[(1-alpha)*v+alpha*a for v,a in zip(x,self.anchor)]
        den=reduce(lcm,(v.denominator for v in x),1);num=[int(v*den) for v in x]
        for row in self.eq_extra_rows:assert sum(v*z for v,z in zip(row,num))==0
        return num,den,float(alpha)
    def solve(self,c,previous=True):
        t=perf_counter();s=self.s;raw,dd,it,price=self.solver.solve(c,previous=previous)
        xn,xd,alpha=self.repair(raw);den=10**9
        # Extra equalities enter the restricted dual; original accepted equalities remain.
        all_dual=self.solver.last[1]
        sn=np.rint((dd[s.row_pos]-dd[s.row_neg])*den).astype(np.int64)
        bound=den*int(c[-1])*s.knum//512;sn=np.clip(sn,-bound,bound)
        rec={'context':list(map(int,c)),'x_num':list(map(str,xn)),'x_den':str(xd),
          'price_num':np.rint(price*den).astype(np.int64).tolist(),
          'switch_num':sn.tolist(),'ineq_num':np.maximum(0,np.rint(dd[s.row_ineq]*den)).astype(np.int64).tolist(),
          'equality_num':np.rint(np.r_[dd[s.row_eq],all_dual[-self.extra.shape[0]:]]*den).astype(np.int64).tolist(),'dual_den':den}
        aa=audit_exact(self.p,c,rec['x_num'],rec['x_den'],rec['price_num'],rec['switch_num'],rec['ineq_num'],rec['equality_num'],den)
        assert aa['gap']<1e-5,('time comparator gap',aa['gap'])
        aa.update(record=rec,repair_fraction=alpha,iterations=it,total=perf_counter()-t)
        return aa
