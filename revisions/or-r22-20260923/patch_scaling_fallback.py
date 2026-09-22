"""Use a fresh structure-aware full-objective fallback in every scale pipeline.

The first source's dense 1e-9 fallback can dominate at larger trees. This
engineering amendment changes no model, seed, sample count or target. It applies
to every scale method, charges new-workspace setup, and is explicitly disclosed.
"""
from pathlib import Path
import json
R=Path(__file__).resolve().parent
MARK='R22 structure-aware scaling refinement amendment'

def patch():
    p=R/'scaling.py';s=p.read_text()
    old="x,d,ii=s.solve(c,warm=(x,d));final=s.audit(c,x,d,record=True)"
    new="""# Fresh workspace: no method inherits another method's refinement state.
                refine=Lifted(s,eps=1e-9)
                try:
                    x,d,ii,ref_price=refine.solve(c,previous=False)
                    final=s.audit(c,x,d,price=ref_price,record=True)
                finally:
                    refine.qp.close()"""
    if old in s:s=s.replace(old,new)
    assert 'refine=Lifted(s,eps=1e-9)' in s
    if "'refinement_protocol'" not in s:
        s=s.replace("'observations':len(rows),'label_records':64*len(specs)","'refinement_protocol':'Fresh lifted full-objective solve at numerical tolerance 1e-9 for every method; setup and final rational audit included in online time.','observations':len(rows),'label_records':64*len(specs)")
    p.write_text(s)
    design=json.loads((R/'DESIGN.json').read_text())
    design['scaling']['refinement_protocol']={'backend':'fresh lifted full objective','numerical_tolerance':1e-9,'setup_charged':True,'applies_to':'all five methods and both certificate targets','reason':'Avoid a known structurally weaker dense full-objective fallback at large trees. No new predictor, sample selection, target relaxation or discarded failed attempt.'}
    (R/'DESIGN.json').write_text(json.dumps(design,indent=2)+'\n')
    empirical=R/'sections/empirical.tex';s=empirical.read_text()
    para=r'''The scale study gives every method a fresh lifted full-objective refinement at numerical tolerance $10^{-9}$ when its certificate fails. Its workspace setup, solve and final rational audit all enter that attempt's online cost. Thus no method inherits another method's refinement state. This engineering amendment replaces the initial source's dense fallback, whose unnecessary over-solving was exposed during development; it changes no training population, held-out context, architecture or requested certificate. The 63-node matched study above retains its separately stated, fully recorded protocol. No runtime observation is pooled across these two protocols.'''
    marker=r'\input{revisions/or-r22-20260923/tables/scaling.tex}'
    if para not in s:s=s.replace(marker,para+'\n\n'+marker)
    empirical.write_text(s)
    response=R/'RESPONSE_TO_REFEREE.md';s=response.read_text()
    if MARK not in s:
        s+='\n## '+MARK+'\n\nDuring execution, the inherited large-tree code exposed a structurally weaker dense full-objective fallback at numerical tolerance 1e-9. The scale study now gives **all five methods at both targets** a fresh lifted full-objective fallback at the same numerical tolerance, charging its setup, solve and independent rational audit. There is no cross-method fallback state. Training labels, frozen rules, geometry, seeds, sample counts and certificate targets are unchanged. No time from the interrupted developmental dense-fallback run is used as publication evidence. The original source remains in R21 and the initial R22 source commit. The complete 63-node matched experiment keeps its documented protocol; the scale and matched timing results are not pooled. `audit_notes/SCALING_REFINEMENT_AMENDMENT.md` and `DESIGN.json` record this amendment.\n'
    response.write_text(s)
    notes=R/'audit_notes';notes.mkdir(exist_ok=True)
    (notes/'SCALING_REFINEMENT_AMENDMENT.md').write_text('''# R22 structure-aware scaling refinement amendment

The inherited R21 scale source used a dense full-objective OSQP refinement at numerical tolerance 1e-9. In local development, the 511-node instance entered a dense refinement exceeding 50,000 iterations, with primal residual around 8.8e-7; this was not an infeasibility or a failed mathematical certificate. It was expensive over-solving by a structure-obscuring fallback. That partial development run was stopped and is not used for publication timing or sample counts.

Every scaling method now receives the same fresh lifted full-objective refinement at numerical tolerance 1e-9. Initialization is inside the measured attempt; the workspace is closed after that call. The independent rational certificate, rather than a solver status, still decides whether the requested target has passed. All failures are retained. The implementation does not reuse another method's refinement history.

This changes no training population, geometry, seed, architecture, held-out sample, label criterion or certificate target. The original source is retained in R21 and R22 source commit b1b021c9a9e954edfe08f5759a5d06341cab384a. The 63-node matched experiment retains its original recorded common-refinement protocol. These studies are described separately, and host timings are not pooled. The amendment is an execution-time engineering disclosure, not an external preregistration or a claim that all possible classical baselines have been exhausted.
''')
    print(MARK+' applied; model and validation populations unchanged.')

if __name__=='__main__':patch()
