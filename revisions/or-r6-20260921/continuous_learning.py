#!/usr/bin/env python3
"""Nonmanufactured inventory-contract reconfiguration and trained scalar critics.
The discrete scheme is an explicitly specified controlled Markov chain. Certificates
are for that chain; grid-refinement differences are NOT continuum error bounds.
Gradient labels come from the fine operational teacher, not an analytic solution.
"""
from __future__ import annotations
import sys,time,json,math
from pathlib import Path
import numpy as np
import torch
from compute import Model,primitives,save,csvsave,OUT

torch.set_num_threads(1)
T=8.;rho=-math.log(.97);lam=.6;speed=.5
Q=primitives()['P']-np.eye(3)

def setup(n):
    q=np.linspace(0,1,n+1);h=1/n
    nt=math.ceil(T*(speed/h+max(-np.diag(Q)))/.8);dt=T/nt;disc=math.exp(-rho*dt)
    d=primitives(Model(n=n));reward=d['B']
    assert dt*(speed/h+max(-np.diag(Q)))<=1+1e-14
    return q,nt,dt,disc,reward

def apply(V,reward,dt,disc,h,actor=None):
    """Value for one review of length dt. Drift sign selects the upwind branch.
    Positive/negative quadratic optimizations are exact over continuous speeds.
    At q=0 only nonnegative speeds; at q=1 only nonpositive speeds.
    """
    df=np.zeros_like(V);db=np.zeros_like(V)
    df[:,:-1]=(V[:,1:]-V[:,:-1])/h;db[:,1:]=(V[:,1:]-V[:,:-1])/h
    if actor is None:
        vp=np.clip(disc*df/(2*lam),0,speed);vm=np.clip(disc*db/(2*lam),-speed,0)
        vp[:,-1]=0;vm[:,0]=0
        p=disc*vp*df-lam*vp**2;m=disc*vm*db-lam*vm**2
        actor=np.where(p>=m,vp,vm)
    actor=np.asarray(actor).copy();actor[:,0]=np.maximum(actor[:,0],0);actor[:,-1]=np.minimum(actor[:,-1],0)
    gain=disc*(np.maximum(actor,0)*df+np.minimum(actor,0)*db)-lam*actor**2
    return dt*reward+disc*(V+dt*Q@V)+dt*gain,actor

def solve(n):
    q,nt,dt,disc,R=setup(n);V=np.zeros((nt+1,3,n+1));U=np.zeros((nt,3,n+1))
    start=time.perf_counter()
    for t in reversed(range(nt)):V[t],U[t]=apply(V[t+1],R,dt,disc,1/n)
    return dict(q=q,nt=nt,dt=dt,disc=disc,R=R,V=V,U=U,seconds=time.perf_counter()-start)

class Critic(torch.nn.Module):
    def __init__(self):
        super().__init__();self.net=torch.nn.Sequential(torch.nn.Linear(5,32),torch.nn.Tanh(),torch.nn.Linear(32,32),torch.nn.Tanh(),torch.nn.Linear(32,1))
    def forward(self,x):return (1-x[:,0:1])*T*self.net(x)

def sample(teacher,n,seed):
    rng=np.random.default_rng(seed);t=rng.uniform(0,T,n);q=rng.uniform(0,1,n);z=rng.integers(0,3,n)
    tf=t/teacher['dt'];qf=q*(len(teacher['q'])-1);it=np.minimum(tf.astype(int),teacher['nt']-1);iq=np.minimum(qf.astype(int),len(teacher['q'])-2);a=tf-it;b=qf-iq
    V=teacher['V'];G=np.gradient(V,teacher['q'],axis=2,edge_order=2)
    def interp(Y):return (1-a)*((1-b)*Y[it,z,iq]+b*Y[it,z,iq+1])+a*((1-b)*Y[it+1,z,iq]+b*Y[it+1,z,iq+1])
    x=np.c_[t/T,q,np.eye(3)[z]]
    return torch.tensor(x,dtype=torch.float32),torch.tensor(interp(V)[:,None],dtype=torch.float32),torch.tensor(interp(G)[:,None],dtype=torch.float32)

def evaluate(net,reference):
    q=reference['q'];nt=reference['nt'];dt=reference['dt'];N=len(q)
    allx=np.array([[t/nt,qq,*np.eye(3)[z]] for t in range(nt+1) for z in range(3) for qq in q],dtype=np.float32)
    vals=[];grads=[]
    for ix in range(0,len(allx),4096):
        X=torch.tensor(allx[ix:ix+4096],requires_grad=True);Y=net(X);G=torch.autograd.grad(Y.sum(),X)[0][:,1]
        vals.extend(Y.detach().numpy().ravel());grads.extend(G.detach().numpy())
    w=np.array(vals,dtype=np.float64).reshape(nt+1,3,N);grad=np.array(grads,dtype=np.float64).reshape(nt+1,3,N)
    Va=np.zeros_like(w);res=[];gap=[];maxspeed=0.
    for t in reversed(range(nt)):
        actor=np.clip(reference['disc']*grad[t+1]/(2*lam),-speed,speed);actor[:,0]=np.maximum(actor[:,0],0);actor[:,-1]=np.minimum(actor[:,-1],0)
        Va[t],_=apply(Va[t+1],reference['R'],dt,reference['disc'],q[1]-q[0],actor)
        opt,_=apply(w[t+1],reference['R'],dt,reference['disc'],q[1]-q[0])
        dep,_=apply(w[t+1],reference['R'],dt,reference['disc'],q[1]-q[0],actor)
        res.append(np.max(np.abs(w[t]-opt)));gap.append(max(0.,np.max(opt-dep)))
    res=np.array(res[::-1]);gap=np.array(gap[::-1]);weights=reference['disc']**np.arange(nt)
    terminal=float(np.max(np.abs(w[-1])))
    bound=float(2*terminal+(weights*(2*res+gap)).sum())
    true=reference['V'];loss=true[0,1,N//2]-Va[0,1,N//2]
    assert loss>=-1e-10 and loss<=bound+1e-8
    return dict(initial_teacher_value=float(true[0,1,N//2]),initial_policy_value=float(Va[0,1,N//2]),initial_policy_loss=float(loss),max_value_error=float(np.max(np.abs(w-true))),value_rmse=float(np.sqrt(np.mean((w-true)**2))),max_one_step_residual=float(res.max()),max_one_step_actor_gap=float(gap.max()),finite_chain_policy_bound=bound,terminal_defect=terminal,certificate_state_count=(nt+1)*3*N)

def main(train=True):
    refs={};rows=[]
    for n in (20,40,80,160):
        r=solve(n);refs[n]=r
        rows.append(dict(intervals=n,time_steps=r['nt'],dt=r['dt'],initial_value=float(r['V'][0,1,n//2]),seconds=r['seconds']))
    csvsave('operational_refinement.csv',rows)
    if not train:return
    teacher=refs[160];reference=refs[80];learn=[]
    for seed in (17,29):
      for mode in ('value_only','value_gradient'):
        torch.manual_seed(seed);net=Critic();X,Y,G=sample(teacher,2048,seed)
        optimizer=torch.optim.Adam(net.parameters(),lr=.003)
        gen=torch.Generator().manual_seed(seed+100);start=time.perf_counter()
        for step in range(6000):
            if step in (3000,5000):
                for group in optimizer.param_groups:group['lr']*=.35
            ix=torch.randint(len(X),(256,),generator=gen);x=X[ix].detach().requires_grad_(True)
            pred=net(x);loss=torch.mean((pred-Y[ix])**2)
            if mode=='value_gradient':
                derivative=torch.autograd.grad(pred.sum(),x,create_graph=True)[0][:,1:2]
                loss=loss+.1*torch.mean((derivative-G[ix])**2)
            optimizer.zero_grad();loss.backward();optimizer.step()
        seconds=time.perf_counter()-start
        metrics=evaluate(net,reference)
        row=dict(mode=mode,seed=seed,training_points=2048,optimizer_steps=6000,parameters=sum(p.numel() for p in net.parameters()),training_seconds=seconds,**metrics);learn.append(row)
        name=f'critic_{mode}_{seed}.json'
        save(name,dict(architecture=[5,32,32,1],activation='tanh',output='8*(1-time_fraction)*net(x)',input=['time_fraction','contract','regime_0','regime_1','regime_2'],state_dict={k:v.detach().numpy().tolist() for k,v in net.state_dict().items()}))
        print(row,flush=True)
    csvsave('learned_critics.csv',learn)
    save('continuous_spec.json',dict(T=T,rho=rho,lambda_speed=lam,max_speed=speed,regime_generator=Q.tolist(),diffusion=0.,boundary='inward velocities, no exit or reflection',teacher_intervals=160,evaluation_intervals=80,discount='exact per review, reward rate by rectangle rule',torch_version=torch.__version__,certificate='finite controlled Markov chain only; no uncomputed continuum enclosure'))
if __name__=='__main__':main('--no-train' not in sys.argv)
