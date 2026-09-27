"""Merged-origin resource-deficit dynamic programming, rational throughout.

The optimizer uses forward exact-count states and monotone max-convolution.
check_deficit.py independently checks every Bellman inequality with explicit
quadratic loops and independently reconstructed kernels. No input is rounded.
"""
from __future__ import annotations
from bisect import bisect_left,bisect_right
from math import lcm
import time
from rational import F, qstr, encode, digest
from price_path import normalize, allocate

class StateLimit(Exception):
    def __init__(self,requested,limit):
        self.requested=requested;self.limit=limit
        super().__init__('Requested state count has '+str(requested.bit_length())+' bits; allowance '+str(limit))

class Kernel:
    def __init__(self,d,u,v):
        self.term=[];self.service=[]
        for j,(b,w,g,tau) in enumerate(zip(d.caps,d.weights,d.gamma,d.ceilings)):
            if v is not None and tau>=v:
                c=max(F(0),min(b,v)-u)
                if c:self.term.append((d.reward_r[j]-d.reward_q[j]*(u+v)/2,w*c))
            if tau>=u and (v is None or tau<v):
                c=max(F(0),b-u)
                if c:self.service.append((w,g,c))
        self.term.sort(reverse=True)
        self.terminal_ends=[];self.terminal_scores=[]
        total=score=F(0)
        for slope,cap in self.term:
            total+=cap;score+=slope*cap;self.terminal_ends.append(total);self.terminal_scores.append(score)
        self.T=sum((c for s,c in self.term),F(0))
        self.C=self.T+sum((w*c for w,g,c in self.service),F(0))
        # Piecewise affine marginal / quadratic value description of service.
        self.free=sum((w*c for w,g,c in self.service if not g),F(0))
        active=[(w,g,c) for w,g,c in self.service if g]
        self.service_events=[];z=self.free;cost=F(0);prev=F(0)
        recip=sum((w/g for w,g,c in active),F(0))
        groups={}
        for w,g,c in active:groups[g*c]=groups.get(g*c,F(0))+w/g
        for threshold in sorted(groups):
            nz=z+recip*(threshold-prev)
            nc=cost+recip*(threshold*threshold-prev*prev)/2
            self.service_events.append((z,nz,prev,recip,cost))
            recip-=groups[threshold]
            z,cost,prev=nz,nc,threshold
        self.service_cost_full=cost
        self.service_ends=[event[1] for event in self.service_events]

    def phi(self,x):
        if not 0<=x<=self.C:raise ValueError('Arc resource outside capacity')
        mass=min(x,self.T);value=F(0)
        if mass:
            ix=bisect_left(self.terminal_ends,mass)
            before=self.terminal_ends[ix-1] if ix else F(0)
            value=(self.terminal_scores[ix-1] if ix else F(0))+self.term[ix][0]*(mass-before)
        y=max(F(0),x-self.T)
        if y>self.free:
            ix=bisect_left(self.service_ends,y)
            if ix==len(self.service_events):raise ArithmeticError('Service kernel not covered')
            lo,hi,alpha,recip,cost=self.service_events[ix]
            value-=cost+alpha*(y-lo)+(y-lo)**2/(2*recip)
        return value

    def grid(self,eta,Q,center):
        length=min(Q-1,int(self.C//eta))
        return [self.phi(self.C-t*eta)+center*t*eta for t in range(length+1)]


def max_convolution(row,g):
    """Concave finite kernel; arbitrary None holes in row are permitted.

    The tie convention is smallest input index. Rows with no feasible finite
    column are discarded BEFORE divide-and-conquer; they cannot restrict later
    argmax searches. This detail matters for merged supports with holes.
    """
    Q=len(row);L=len(g)-1;cols=[i for i,v in enumerate(row) if v is not None]
    ans=[None]*Q;ptr=[None]*Q;comparisons=0
    if not cols:return ans,ptr,comparisons
    bounds={}
    for s in range(Q):
        lo=bisect_left(cols,s-L);hi=bisect_right(cols,s)-1
        if lo<=hi:bounds[s]=(lo,hi)
    rows=list(bounds)
    def rec(l,h,cl,ch):
        nonlocal comparisons
        if l>h:return
        mid=(l+h)//2;s=rows[mid]
        low=max(cl,bounds[s][0]);high=min(ch,bounds[s][1])
        if low>high:raise ArithmeticError('Monotone convolution invariant')
        best=None;winner=None
        for ix in range(low,high+1):
            z=cols[ix];val=row[z]+g[s-z];comparisons+=1
            if best is None or val>best:best=val;winner=ix
        ans[s]=best;ptr[s]=cols[winner]
        rec(l,mid-1,cl,winner);rec(mid+1,h,winner,ch)
    rec(0,len(rows)-1,0,len(cols)-1)
    return ans,ptr,comparisons


def lattice_scale(d,a,B):
    """Sufficient common lattice; value can be exponential in its bit length."""
    D=B.denominator
    for w,b in zip(d.weights,d.caps):
        D=lcm(D,(w*b).denominator)
        for x in a:D=lcm(D,(w*x).denominator)
    return D


def solve(spec,epsilon=F(1,20),exact_lattice=False,max_states=600000):
    started=time.perf_counter();d,a,rho,B,m=normalize(spec);n=len(a)
    R=d.cap_total-B;eps=F(epsilon);K=(max(d.reward_r)+max(d.gamma))/2
    center=(max(d.reward_r)-max(d.gamma))/2
    if exact_lattice:
        if any(d.gamma):raise ValueError('Exact lattice mode requires zero service cost')
        D=lattice_scale(d,a,B);eta=F(1,D);error=F(0);target=int(R*D)
        Q=target+1;accepted=[target]
    elif R==0:
        D=None;eta=F(1);error=F(0);Q=1;accepted=[0]
    else:
        if eps<=0:raise ValueError('Positive accuracy required outside exact modes')
        D=None;eta=eps/(2*K*m);error=K*m*eta
        Q=int(R//eta)+1
        accepted=[s for s in range(Q) if R-m*eta<=s*eta<=R]
    if m*n*Q>max_states:
        raise StateLimit(m*n*Q,max_states)
    edge={(i,j):Kernel(d,u,a[j] if j<n else None) for i,u in enumerate(a) for j in list(range(i+1,n))+[n]}
    p=[sum(w*min(b,u) for w,b in zip(d.weights,d.caps)) for u in a]+[d.cap_total]
    for (i,j),ker in edge.items():
        if ker.C!=p[j]-p[i]:raise ArithmeticError('Capacity conservation failed')
    grid={key:ker.grid(eta,Q,center) for key,ker in edge.items()}
    states=[[[None]*Q for _ in a] for _ in range(m)]
    previous={};comparisons=0;finite=0
    for i,u in enumerate(a):
        if u<=min(B,min(d.caps)):states[0][i][0]=d.mean_reward(u)-rho[i]
    for ell in range(1,m):
        for i in range(n):
            for j in range(i+1,n):
                vals,ptr,cnt=max_convolution(states[ell-1][i],grid[i,j]);comparisons+=cnt
                for s,val in enumerate(vals):
                    if val is not None and (states[ell][j][s] is None or val-rho[j]>states[ell][j][s]):
                        states[ell][j][s]=val-rho[j];previous[ell,j,s]=(i,ptr[s])
    best=None;endpoint=None
    for ell in range(m):
        for i in range(n):
            vals,ptr,cnt=max_convolution(states[ell][i],grid[i,n]);comparisons+=cnt
            for s in accepted:
                val=vals[s]
                if val is not None and (best is None or val>best):best=val;endpoint=(ell,i,ptr[s],s-ptr[s])
    if best is None:raise ArithmeticError('Rounded optimum has no feasible state')
    ell,i,s,tail_w=endpoint;ids=[i];deficits=[tail_w*eta]
    while ell:
        u,z=previous[ell,i,s];deficits.append((s-z)*eta);ids.append(u);ell,i,s=ell-1,u,z
    ids.reverse();deficits.reverse();book=tuple(a[i] for i in ids)
    missing=R-sum(deficits);repaired=list(deficits)
    for h,key in enumerate(list(zip(ids,ids[1:]))+[(ids[-1],n)]):
        add=min(missing,edge[key].C-repaired[h]);repaired[h]+=add;missing-=add
    if missing:raise ArithmeticError('Deficit repair failed')
    policy=allocate(d,book,B,dict(zip(a,rho)))
    upper=best-center*R+error
    if policy['value']>upper:raise ArithmeticError('Recovered value exceeds certified upper')
    if upper-policy['value']>2*error:raise ArithmeticError('Repair exceeds error theorem')
    cert=dict(schema='NDU-deficit-v1-hex',spec=spec,instance_sha256=digest(spec),mode='lattice' if exact_lattice else 'additive',
              epsilon=qstr(eps),eta=qstr(eta),center=qstr(center),error=qstr(error),D=None if D is None else format(D,'x'),
              states=encode(states),best=qstr(best),book_indices=ids,rounded_deficits=encode(deficits),repaired_deficits=encode(repaired),
              policy=encode(policy),lower=qstr(policy['value']),upper=qstr(upper))
    return dict(status='EXACT' if upper==policy['value'] else 'TOLERANCE',lower=policy['value'],upper=upper,gap=upper-policy['value'],
                certificate=cert,seconds=time.perf_counter()-started,grid_points=Q,allocated_states=m*n*Q,
                finite_states=sum(v is not None for layer in states for row in layer for v in row),comparisons=comparisons,
                denominator_bits=0 if D is None else D.bit_length(),lattice_capacity=Q-1)
