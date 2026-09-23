#!/usr/bin/env python3
"""Finite exact checks of the explicitly proved laminar-rank connection.

This enumerates integer packing examples; it is not a proof for real inputs.
"""
from itertools import product

def run():
    count=0; rankchecks=0; subchecks=0; feasible_count=0
    for parents in ((-1,0,0,1,1,2),(-1,0,1,2,3,4),(-1,0,0,0,0,0)):
        n=len(parents); children=[[j for j in range(n) if parents[j]==i] for i in range(n)]
        descendants=[{i} for i in range(n)]
        for i in reversed(range(n)):
            for j in children[i]:descendants[i]|=descendants[j]
        for seed in range(3):
            caps=[2+(i+seed)%4 for i in range(n)]; boxes=[1+(i+seed)%2 for i in range(n)]
            feasible=[u for u in product(*(range(c+1) for c in boxes))
                      if all(sum(u[j] for j in descendants[i])<=caps[i] for i in range(n))]
            ranks=[]
            for mask in range(1<<n):
                vals=[0]*n
                for i in reversed(range(n)):
                    vals[i]=min(caps[i],boxes[i]*bool(mask & (1<<i))+sum(vals[j] for j in children[i]))
                assert vals[0]==max(sum(u[j] for j in range(n) if mask&(1<<j)) for u in feasible)
                ranks.append(vals[0]);rankchecks+=1
            for a in range(1<<n):
                for b in range(1<<n):
                    assert ranks[a]+ranks[b]>=ranks[a|b]+ranks[a&b];subchecks+=1
            for u in product(*(range(c+1) for c in boxes)):
                rankok=all(sum(u[j] for j in range(n) if mask&(1<<j))<=ranks[mask] for mask in range(1<<n))
                assert rankok==(u in feasible)
            for total in range(ranks[-1]+1):
                truncated=[min(total,v) for v in ranks]
                for u in feasible:
                    if sum(u)==total:
                        assert all(sum(u[j] for j in range(n) if mask&(1<<j))<=truncated[mask] for mask in range(1<<n))
                        feasible_count+=1
            count+=1
    return dict(examples=count,exact_rank_identities=rankchecks,submodular_inequalities=subchecks,
                feasible_base_allocations=feasible_count,scope='finite integer checks, not the continuous proof')

if __name__=='__main__':
    import json
    print(json.dumps(run(),indent=2))
