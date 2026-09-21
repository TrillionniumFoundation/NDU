#!/usr/bin/env python3
"""Exact algebraic envelope extension; floating implementations cross-checked.
Runtime figures are descriptive CPU measurements, not complexity proofs.
"""
from pathlib import Path
import time,json
import numpy as np
from compute import Model,primitives,save,csvsave

def hull(m,b,x):
    lines=[];starts=[]
    for k in range(len(m)):
        start=-np.inf
        while lines:
            j=lines[-1];start=(b[j]-b[k])/(m[k]-m[j])
            if len(lines)==1 or start>starts[-1]:break
            lines.pop();starts.pop()
        if not lines:start=-np.inf
        lines.append(k);starts.append(start)
    # Ordered queries: each hull segment is crossed at most once.
    act=np.zeros(len(x),int);j=0
    for i,xx in enumerate(x):
        while j+1<len(lines) and starts[j+1]<=xx:j+=1
        act[i]=lines[j]
    return b[act]+m[act]*x,act,lines,starts

def solve(n,power=.0,fast=True):
    M=Model(n=n);d=primitives(M);q=d['theta'];phi=q*q+power*q**4;grad=2*q+4*power*q**3
    V=np.zeros((M.T+1,3,n+1));pol=np.zeros((M.T,3,n+1),int);records=[]
    start=time.perf_counter()
    for t in reversed(range(M.T)):
      for z in range(3):
        b=d['B'][z]-M.lam*phi+M.beta*d['P'][z]@V[t+1]
        if fast:
            val,act,lines,starts=hull(M.lam*q,b,grad)
            if n==10:records.append(dict(t=t,z=z,contracts=[int(j) for j in lines],dual_thresholds=[None if not np.isfinite(a) else float(a) for a in starts]))
        else:
            obj=b[None,:]+M.lam*grad[:,None]*q[None,:]
            act=n-np.argmax(obj[:,::-1],axis=1);val=obj[np.arange(n+1),act]
        V[t,z]=M.lam*(phi-q*grad)+val;pol[t,z]=act
    return V,pol,time.perf_counter()-start,records

def main():
    rows=[]
    for p in (0.,.2):
      for n in (32,128,512,2048):
        vf,af,tf,_=solve(n,p,True);vb,ab,tb,_=solve(n,p,False)
        err=float(np.max(np.abs(vf-vb)));assert err<1e-10
        rows.append(dict(intervals=n,quartic=p,hull_seconds=tf,exhaustive_seconds=tb,speedup=tb/tf,maximum_value_difference=err,policy_mismatches=int(np.sum(af!=ab)),line_count=24*(n+1),exhaustive_comparisons=24*(n+1)**2,initial_value=float(vf[0,1,n//2])))
    csvsave('envelope_scaling.csv',rows)
    for p in (0.,.2):
        _,_,_,r=solve(10,p,True);save('thresholds_'+str(p)+'.json',r)
    print(rows)
if __name__=='__main__':main()
