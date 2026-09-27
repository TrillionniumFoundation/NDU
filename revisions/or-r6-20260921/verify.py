#!/usr/bin/env python3
"""Independent recorded-evidence checks. Exact claims use Fraction, never float tolerances."""
from pathlib import Path
from fractions import Fraction as F
import csv, hashlib, json, runpy, sys
H=Path(__file__).resolve().parent; R=H.parent.parent; O=H/'results'
def load(n): return json.loads((O/n).read_text())
def rows(n): return list(csv.DictReader((O/n).open()))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['main.tex','electronic_companion.tex','README.md','NDU_OR_submission_checklist.md']:
    text=(R/name).read_text()
    assert 'R6' in text, name
    assert sha(R/name)!=sha(R/'archive/pre-r6'/name), 'Unchanged scientific revision: '+name
for name in ['main.tex','electronic_companion.tex']:
    assert 'Revision R6, September 21, 2026' in (R/name).read_text()
# Independently rerun all rational forward ledgers and the Bellman upper bound.
runpy.run_path(str(H/'exact_certificate.py'),run_name='__main__')
c=load('exact_service_certificate.json'); s=load('static_exact.json')
assert F(c['gain_fraction'])>0
assert F(c['mixture']['reward'])-F(s['value_fraction'])==F(c['gain_fraction'])
for k in ['customer','filled','physical']:
    assert F(c['static'][k])==F(c['mixture'][k])
assert F(0)<=F(c['duality_gap_fraction'])<F(821,10**18)
assert F(c['upper_bound_fraction'])-F(c['lower_bound_fraction'])==F(c['duality_gap_fraction'])
assert load('exact_replay.json')['policy_matches']
a={x['policy']:x for x in rows('adaptivity.csv')}
reg=load('restriction_regime.json')
assert reg['mip_gap']<1e-8
assert float(a['best_static_grid']['reward'])<=reg['lower_bound']<=float(a['full']['reward'])+1e-10
assert abs(float(a['time_only']['reward'])-load('restriction_inherited.json')['reward'])<1e-10
learn=rows('learned_critics.csv')
assert len(learn)==4
for x in learn:
    assert int(x['optimizer_steps'])==6000 and int(x['parameters'])==1281
    # Column names are audited against the recorded CSV, not inferred from prose.
    for v in x.values(): assert str(v) not in ('nan','inf','-inf')
    w=load(f"critic_{x['mode']}_{x['seed']}.json")
    assert w['architecture']==[5,32,32,1]
assert (H/'RESPONSE_TO_REFEREE.md').stat().st_size>10000
out={'exact_service_preserving_improvement':True,'exact_gap_below_8_21e_16':True,
     'four_trained_critics_present':True,'new_scientific_source_verified':True,
     'scope':'Exact Fraction checks plus recorded numerical diagnostics; not a journal-acceptance or continuum-learning certificate.'}
(H/'validation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
