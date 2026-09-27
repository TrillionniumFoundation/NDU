"""Matched scalar-critic and direct-price surrogates; no test-set selection."""
from __future__ import annotations
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.linalg import solve

class Features:
    def __init__(self,dim,kind='tanh',seed=0,width=192):
        self.dim=dim;self.kind=kind
        if kind=='tanh':
            rng=np.random.default_rng(seed);self.W=rng.normal(0,1,(dim,width));self.bias=rng.uniform(-1,1,width)
        else:
            from itertools import combinations_with_replacement
            self.pairs=list(combinations_with_replacement(range(dim),2))
            if kind=='cubic':self.pairs+=list(combinations_with_replacement(range(dim),3))
    def evaluate(self,X):
        X=np.atleast_2d(X);n,d=X.shape
        if self.kind=='tanh':
            T=np.tanh(X@self.W+self.bias);F=np.c_[np.ones(n),X,T]
            D=np.zeros((n,d,F.shape[1]));D[:,:,1:d+1]=np.eye(d)[None,:,:]
            D[:,:,d+1:]=(1-T*T)[:,None,:]*self.W[None,:,:]
        else:
            F=np.c_[np.ones(n),X,np.array([np.prod(X[:,inds],axis=1) for inds in self.pairs]).T]
            D=np.zeros((n,d,F.shape[1]));D[:,:,1:d+1]=np.eye(d)[None,:,:]
            for k,inds in enumerate(self.pairs):
                for pos,i in enumerate(inds):D[:,i,1+d+k]+=np.prod(X[:,inds[:pos]+inds[pos+1:]],axis=1)
        return F,D
class Surrogate:
    def __init__(self,feature,mode,rank,ridge=1e-7):self.feature=feature;self.mode=mode;self.rank=rank;self.ridge=ridge
    def fit(self,X,values,gradients):
        F,D=self.feature.evaluate(X)
        if self.mode=='direct':A=F;Y=gradients
        elif self.mode=='value':A=F;Y=values
        else:A=np.concatenate([F,D[:,:self.rank].reshape(-1,F.shape[1])]);Y=np.r_[values,gradients.ravel()]
        self.coef=solve(A.T@A+self.ridge*len(A)*np.eye(A.shape[1]),A.T@Y,assume_a='pos')
        return self
    def predict(self,X):
        F,D=self.feature.evaluate(X)
        return F@self.coef if self.mode=='direct' else np.einsum('nkp,p->nk',D[:,:self.rank],self.coef)
    def frozen(self):
        out={'mode':self.mode,'kind':self.feature.kind,'rank':self.rank,'coef':self.coef.tolist()}
        if self.feature.kind=='tanh':out.update(W=self.feature.W.tolist(),bias=self.feature.bias.tolist())
        return out
class RBF:
    def fit(self,X,values,gradients):self.model=RBFInterpolator(X,gradients,kernel='cubic',smoothing=1e-7);self.X=X;self.Y=gradients;return self
    def predict(self,X):return self.model(np.atleast_2d(X))
    def frozen(self):return {'kind':'cubic-rbf','X':self.X.tolist(),'Y':self.Y.tolist(),'smoothing':1e-7}

def fit_all(X,V,G,seed):
    models={}
    for kind in ['tanh','quadratic']:
        feat=Features(X.shape[1],kind,seed)
        for mode in ['value','gradient','direct']:
            models[kind+'-'+mode]=Surrogate(feat,mode,G.shape[1]).fit(X,V,G)
    models['rbf-direct']=RBF().fit(X,V,G)
    return models
