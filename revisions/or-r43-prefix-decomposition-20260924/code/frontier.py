"""Instrument inherited exact faces without modifying historical code.

An explicit system-count budget permits comparable, reproducible stopping.
Partial face search yields no upper bound and is NEVER called a global solution.
"""
from fractions import Fraction as F
from itertools import product,combinations
from pathlib import Path
import sys,time,tracemalloc,resource
sys.path.append(str(Path(__file__).resolve().parents[2]/'or-r42-certified-joint-design-20260924'/'code'))
import faces


def audit(model,budget,B,delta,price=(0,0,0),system_limit=12000):
    begin=time.perf_counter(); tracemalloc.start()
    stats=dict(cells_started=0,cells_completed=0,infeasible_completed_cells=0,
               systems=0,nonsingular=0,feasible=0,max_candidate_bits=0,
               max_elimination_integer_bits=0,max_cell_inequalities=0)
    best=None; complete=True
    def solve(A,b):
        # Same fraction-free algorithm; observe EVERY intermediate integer.
        from math import lcm
        n=len(b)
        if not n: return []
        M=[]
        for row,z in zip(A,b):
            v=list(row)+[z]; den=lcm(*(x.denominator for x in v))
            M.append([int(x*den) for x in v])
        prev=1
        def observe():
            stats['max_elimination_integer_bits']=max(stats['max_elimination_integer_bits'],
                max((abs(x).bit_length() for row in M for x in row),default=0))
        observe()
        for h in range(n-1):
            pivot=next((i for i in range(h,n) if M[i][h]),None)
            if pivot is None: return None
            if pivot!=h: M[h],M[pivot]=M[pivot],M[h]
            val=M[h][h]
            for i in range(h+1,n):
                w=M[i][h]
                for j in range(h+1,n+1):
                    num=val*M[i][j]-w*M[h][j]
                    assert num%prev==0
                    M[i][j]=num//prev
                M[i][h]=0
            prev=val; observe()
        if not M[-1][-2]: return None
        x=[F(0)]*n
        for i in range(n-1,-1,-1):
            x[i]=(F(M[i][-1])-sum(M[i][j]*x[j] for j in range(i+1,n)))/M[i][i]
        return x
    try:
        for s in range(1,budget+1):
            types=[('S',i) for i in range(s)]+[('L',i) for i in range(s-1)]
            for modes in product(types,repeat=len(model.caps)):
                stats['cells_started']+=1
                H,a,c,G,h,v,offset=faces.cell(model,s,modes,F(B),F(delta),tuple(map(F,price)))
                d=len(a); M=len(G); cell_feasible=False
                assert M<=s+1+4*len(model.caps)
                stats['max_cell_inequalities']=max(stats['max_cell_inequalities'],M)
                for length in range(min(d,M)+1):
                    for ids in combinations(range(M),length):
                        if stats['systems']>=system_limit: raise StopIteration
                        A=[G[i] for i in ids]; b=[h[i] for i in ids]
                        K=[list(H[i])+[row[i] for row in A] for i in range(d)]
                        K.extend([list(row)+[F(0)]*length for row in A])
                        stats['systems']+=1
                        x=solve(K,[-z for z in a]+b)
                        if x is None: continue
                        stats['nonsingular']+=1
                        stats['max_candidate_bits']=max(stats['max_candidate_bits'],
                            max(max(z.numerator.bit_length(),z.denominator.bit_length()) for z in x))
                        x=x[:d]
                        if any(sum(g*z for g,z in zip(row,x))>rhs for row,rhs in zip(G,h)): continue
                        stats['feasible']+=1; cell_feasible=True
                        value=c+sum(ai*xi for ai,xi in zip(a,x))+sum(x[i]*H[i][j]*x[j] for i in range(d) for j in range(d))/2
                        if best is None or value>best: best=value
                stats['cells_completed']+=1
                if not cell_feasible: stats['infeasible_completed_cells']+=1
    except StopIteration:
        complete=False
    _,peak=tracemalloc.get_traced_memory(); tracemalloc.stop()
    stats.update(status='exact' if complete else 'system_limit',value=best,
        seconds=time.perf_counter()-begin,peak_traced_bytes=peak,
        process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        system_limit=system_limit,infeasible_cell_fraction=(stats['infeasible_completed_cells']/stats['cells_completed'] if stats['cells_completed'] else None))
    return stats
