"""Evaluate a frozen R27 comparator cache; no optimization or query labels.
Example: python -S revisions/or-r27-20260923/query_cache.py --context-id 0 --rho 1/8 --theta -3 4 5
"""
from __future__ import annotations
import argparse,json
from fractions import Fraction as F
from pathlib import Path
from replay import R,OLD,read,system,cache_upper,digest,require

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--context-id',type=int,required=True)
    p.add_argument('--rho',required=True,help='Exact radius, e.g. 1/8')
    p.add_argument('--theta',type=int,nargs=3,required=True,help='Three integer numerators; actual coordinates are divided by 8')
    args=p.parse_args()
    data=read(R/'results/deployment_cache.json')
    require(0<=args.context_id<len(data['contexts']),'unknown context id')
    require(digest(OLD/'radius_primitives.json')==data['primitive_sha256'],'changed fixed primitives')
    model=system(read(OLD/'radius_primitives.json'),data['contexts'][args.context_id],F(args.rho),args.theta)
    cached=data['prices_by_context'][args.context_id]
    upper,best,all_values=cache_upper(model,cached)
    print(json.dumps({'restricted_comparator_upper_exact':str(upper),'selected_anchor_radius':cached[best]['rho'],
                      'all_anchor_upper_exact':[str(v) for v in all_values],
                      'restricted_optimization_calls':0,'interpretation':'Upper bound only; a positive economic-gain claim additionally needs a feasible implemented policy value.'},indent=2))
if __name__=='__main__':main()
