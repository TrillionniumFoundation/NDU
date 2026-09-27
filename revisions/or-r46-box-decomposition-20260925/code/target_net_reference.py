"""Preserved R45 grid reference with the single-branch redundancy repaired."""
from pathlib import Path
import importlib.util,sys
from fractions import Fraction as F
P=Path(__file__).resolve().parents[2]/'or-r45-budgeted-compression-20260924'/'code'
sys.path.insert(0,str(P))
from compression import frontier,rat
spec=importlib.util.spec_from_file_location('archival_target_net',P/'target_net.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)

def solve(instance,catalog,charges,promise,budget,epsilon,max_profiles=None):
    epsilon=rat(epsilon)
    if epsilon<=0: raise ValueError('Positive accuracy required')
    if len(instance.caps)!=1:
        return old.solve(instance,catalog,charges,promise,budget,epsilon,max_profiles)
    t=(rat(promise),)
    answer=frontier(instance,catalog,charges,t,budget)['at_most'][-1]
    return dict(status='COMPLETE',policy=answer,evaluated_profiles=1,cartesian_candidates=1,
                epsilon_guarantee=F(0),requested_epsilon=epsilon,scope='exact one-branch joint catalog design')
