"""Cached OSQP adapter; no matrix update or hidden setup during repeated solves."""
from __future__ import annotations
import ctypes as ct
from pathlib import Path
import subprocess
import numpy as np
from scipy import sparse
import casadi
ROOT=Path(__file__).resolve().parent
LIBDIR=Path(casadi.__file__).resolve().parent
SO=ROOT/'_osqp_bridge.so'
def build():
    if not SO.exists() or SO.stat().st_mtime<(ROOT/'osqp_bridge.c').stat().st_mtime:
        subprocess.run(['cc','-O3','-shared','-fPIC',str(ROOT/'osqp_bridge.c'),
                        '-I'+str(LIBDIR/'include/osqp'),'-L'+str(LIBDIR),
                        '-Wl,-rpath,'+str(LIBDIR),'-losqp','-o',str(SO)],check=True)
    lib=ct.CDLL(str(SO)); ip=ct.POINTER(ct.c_longlong); dp=ct.POINTER(ct.c_double)
    lib.ndu_setup.restype=ct.c_void_p
    lib.ndu_setup.argtypes=[ct.c_longlong,ct.c_longlong,ct.c_longlong,ip,ip,dp,ct.c_longlong,ip,ip,dp,dp,dp,dp,ct.c_double]
    lib.ndu_solve.argtypes=[ct.c_void_p,dp,dp,dp,ct.c_int,dp,dp,ip]
    lib.ndu_solve.restype=ct.c_int;lib.ndu_close.argtypes=[ct.c_void_p]
    return lib
_LIB=None
class QP:
    def __init__(self,P,A,l,u,eps=1e-9):
        global _LIB
        if _LIB is None:_LIB=build()
        self.lib=_LIB;P=sparse.triu(sparse.csc_matrix(P),format='csc');A=sparse.csc_matrix(A)
        self.n=P.shape[0];self.m=A.shape[0];self.keep=[]
        def ptr(a,typ):
            a=np.ascontiguousarray(a,dtype=np.int64 if typ=='i' else np.float64);self.keep.append(a)
            return a.ctypes.data_as(ct.POINTER(ct.c_longlong if typ=='i' else ct.c_double))
        self.work=self.lib.ndu_setup(self.n,self.m,P.nnz,ptr(P.indptr,'i'),ptr(P.indices,'i'),ptr(P.data,'d'),A.nnz,ptr(A.indptr,'i'),ptr(A.indices,'i'),ptr(A.data,'d'),ptr(np.zeros(self.n),'d'),ptr(l,'d'),ptr(u,'d'),eps)
        if not self.work:raise RuntimeError('OSQP setup failed')
        self.xzero=np.zeros(self.n);self.yzero=np.zeros(self.m)
    def solve(self,q,warm=None,previous=False):
        def ptr(x):return x.ctypes.data_as(ct.POINTER(ct.c_double))
        q=np.ascontiguousarray(q,dtype=float);x=np.empty(self.n);y=np.empty(self.m);it=ct.c_longlong()
        x0,y0=(self.xzero,self.yzero) if warm is None else (np.ascontiguousarray(warm[0]),np.ascontiguousarray(warm[1]))
        status=self.lib.ndu_solve(self.work,ptr(q),ptr(x0),ptr(y0),int(not previous),ptr(x),ptr(y),ct.byref(it))
        if status not in (1,2):raise RuntimeError(f'OSQP status {status}, iterations {it.value}')
        return x,y,int(it.value)
    def close(self):
        if getattr(self,'work',None):self.lib.ndu_close(self.work);self.work=None
    def __del__(self):self.close()
