"""Materialize the full R22 source and integrate the R22 mathematical additions.

Executed before building, never by frozen verification. Earlier revision sources
are read-only. Ordinary R22 sources, rather than encoded bundles, are published.
"""
from pathlib import Path
import shutil,json
R=Path(__file__).resolve().parent
ROOT=R.parents[1]
OLD=ROOT/'revisions/or-r21-20260923'

def normalize(s):
    return s.replace('or-r21-20260923','or-r22-20260923').replace('R21','R22').replace('r21-','r22-').replace('ndu-or-r21/','ndu-or-r22/')
def edit(name,fn):
    p=R/name;s=p.read_text();p.write_text(fn(s))
def once(s,old,new):
    return s if new in s else s.replace(old,new)

def run():
    for src in OLD.rglob('*'):
        if src.is_file() and '__pycache__' not in src.parts:
            dst=R/src.relative_to(OLD)
            if not dst.exists():
                dst.parent.mkdir(parents=True,exist_ok=True)
                if 'predecessor' not in src.parts and src.suffix in ['.py','.sh','.tex','.md','.json']:
                    dst.write_text(normalize(src.read_text()))
                else: shutil.copy2(src,dst)
    (R/'results').mkdir(exist_ok=True)
    for name in ['package_metadata.py','RESPONSE_TO_REFEREE.md','run_all.sh']:
        edit(name,lambda s:s.replace('ndu-or-r21/','ndu-or-r22/'))
    def prep(s):
        s=s.replace("['certification.tex','benchmark.tex','empirical.tex']","['certification.tex','complete_dual.tex','benchmark.tex','empirical.tex']")
        s=once(s,'and supports monotone low-dimensional price repair.','and distinguishes limited price polishing from complete dual repair with attained optimal certificates.')
        s=once(s,'The benchmark-gate theorem then compares', 'A complete-price theorem further shows that full dual repair attains the best possible certificate without strict feasibility; it has a classical projected-gradient guarantee and an auditable nonlearned context warm start. The benchmark-gate theorem then compares')
        s=once(s,'A better upper bound does not change primal regret.', 'Allowing all prices to change removes this fixed-block limitation: the best attainable certificate equals true primal regret, and exact projected-gradient repair converges to that value without strict feasibility. A better upper bound does not change primal regret.')
        s=once(s,'New sections add certificate components, price repair, a charged regularization bound,', 'New sections add certificate components, block and complete dual repair, exact certificate attainment without strict feasibility, certified context transport, a charged regularization bound,')
        return s
    edit('prepare.py',prep)
    def response(s):
        s=s.replace('R22 starts from the review commit and preserves', 'R22 branches from the pinned R21 ordinary-source checkpoint `c2d25791bd1f4c2b1801a446376a86c50eb381fe`, which had not published executed results or new root manuscripts, and preserves')
        marker='## 1. Incomplete R20 review object and provenance'
        addition='''## Additional R22 result: complete repair closes the fixed-block certificate limitation

Beyond executing the inherited R21 design, R22 proves **complete dual-price repair and exact certificate attainment** (`thm:r22-complete`). For the stated quadratic accepted model, the full constrained dual minimum is attained and equals the primal optimum even if the accepted polyhedron has no strictly feasible point or has dependent equality rows. Therefore the best certificate for a fixed feasible decision equals its actual regret. Allowing all prices to vary can remove the extra switching/participation floor created by fixed-block repair; it cannot change that regret. The gradient and a global Lipschitz constant are explicit, and exact projected-gradient iterates have a proved nonincreasing upper bound and a reciprocal-iteration error rate. Numerical best-bound retention alone is not assigned that exact-iterate rate.

The accompanying context-transport corollary gives a nonlearned classical warm start with a fresh auditable certificate when reward and friction change but the accepted geometry remains fixed. It requires neither an optimal-face oracle nor a new primal solve if the fresh certificate already passes. This is not relabeled as the measured twelve-step block algorithm or claimed to have a measured speed advantage. Independent standard-library rational checks cover 225 exact primal/dual optima (45 without strict feasibility), 3,600 projected-gradient steps, and 450 new-context certificate transports. The proof, tests, and test counts are all ordinary repository files.

This separates the genuinely accepted-control consequence from its established tools: polyhedral normal cones and projected-gradient convergence are classical; exact attainable certificate floors and the resulting decision-versus-certificate intervention distinguish the operational questions here. Full earlier statements, proofs and adverse results are retained.

'''
        if '## Additional R22 result:' not in s:s=s.replace(marker,addition+marker)
        s=once(s,'Locations: `sections/literature.tex`, `sections/certification.tex`;', 'Locations: `sections/literature.tex`, `sections/certification.tex`, `sections/complete_dual.tex`, `complete_dual_checks.py`;')
        return s
    edit('RESPONSE_TO_REFEREE.md',response)
    def companion(s):
        s=once(s,'The 360 nonsmooth zero-curvature identities', 'The complete dual-repair checks independently optimize 225 small accepted problems, including 45 with no strict-feasibility point; they verify 3,600 exact projected-gradient steps and 450 reward/friction certificate transports. They do not call the numerical optimizer or the main certificate implementation. These are theorem checks, not speed comparisons. The 360 nonsmooth zero-curvature identities')
        s=once(s,'A code-inspection pilot used 23001 and 23002;', 'The inherited R21 audit note records a code-inspection pilot using 23001 and 23002;')
        return s
    edit('sections/companion.tex',companion)
    edit('sections/literature.tex',lambda s:once(s,'matched audits test total cost: algorithmic accounting, not a universal speed theorem.', 'Theorem~\\ref{thm:r22-complete} identifies the exact attainable floor when all prices vary, without strict feasibility. Matched audits test total cost; the standard convergence rate is not a new generic algorithm.'))
    edit('run_all.sh',lambda s:once(s,'python -S "$R/theory_checks.py"', 'python -S "$R/theory_checks.py"\npython -S "$R/complete_dual_checks.py"'))
    def checker(s):
        s=s.replace("['matched_summary','validation_summary','theory_checks','replay','analysis']", "['matched_summary','validation_summary','theory_checks','complete_dual_checks','replay','analysis']")
        anchor="    for name in ['RESPONSE_TO_REFEREE.md'"
        checks="    complete=read('results/complete_dual_checks.json')\n    assert complete['exact_optimum_and_attainment_cases']==225\n    assert complete['lower_dimensional_no_strict_feasibility_cases']==45\n    assert complete['exact_projected_gradient_steps']==3600\n    assert complete['new_context_certificate_transports']==450\n"
        if "    complete=read(" not in s:s=s.replace(anchor,checks+anchor)
        s=once(s,"'component_identities':320,'negative_controls_rejected':4,", "'complete_dual_exact_cases':225,'complete_dual_exact_steps':3600,'certificate_transports':450,\n        'component_identities':320,'negative_controls_rejected':4,")
        return s
    edit('check_package.py',checker)
    def metadata(s):
        s=once(s,'charge regularization bias, and connect implemented decisions', 'prove complete dual attainment and a convergent full-price repair without strict feasibility, certify context transport, charge regularization bias, and connect implemented decisions')
        s=once(s,'The inherited R19 standard-library replay is also rerun', '[Complete dual-repair checks]({P}/results/complete_dual_checks.json) additionally verify 225 exact optima, 3,600 projected-gradient steps and 450 context transports. The inherited R19 standard-library replay is also rerun')
        s=once(s,'python -S revisions/or-r22-20260923/replay.py --check', 'python -S revisions/or-r22-20260923/complete_dual_checks.py --check\npython -S revisions/or-r22-20260923/replay.py --check')
        s=once(s,"prov={'revision':'R22',", "prov={'revision':'R22','inherited_unexecuted_source':'c2d25791bd1f4c2b1801a446376a86c50eb381fe','evidence_workflow_run':os.getenv('EVIDENCE_RUN','local-development'),'evidence_artifact':os.getenv('EVIDENCE_ARTIFACT','local-development'),")
        return s
    edit('package_metadata.py',metadata)
    p=R/'CLAIM_EVIDENCE.md';s=p.read_text()
    if '| Complete dual repair' not in s:
        s+='\n| Complete dual repair attains the true-regret floor without strict feasibility | `sections/complete_dual.tex`; 225 exact optimality checks including 45 lower-dimensional cases, 3,600 exact steps | Classical projected-gradient rate applies to exact full-price iterates, not the twelve-step numerical block heuristic |\n| Nonlearned context transport is certifiable | Full proof and 450 exact reward/friction transports | Accepted geometry fixed; new coefficients are freshly audited and audit work is not free |\n'
        p.write_text(s)
    p=R/'LITERATURE_MAP.md';s=p.read_text()
    if '## R22 complete-price consequence' not in s:
        s+='''\n## R22 complete-price consequence

Full polyhedral normal-cone optimality supplies dual attainment even on a lower-dimensional accepted set. Standard smooth projected-gradient analysis gives the stated exact-iterate rate. The application consequence is that the best possible upper certificate for any fixed implemented decision is exactly its true regret, whereas fixing switching and participation prices can create a larger algorithmic floor. This result identifies which computational intervention can help; it is not an invention of strong duality or projected gradients. The auditable context-transport corollary gives a classical alternative without predicting a statistic.

Primary-source checks, September 23, 2026: Operations Research preparation requirements, https://pubsonline.informs.org/page/opre/submission-guidelines ; SPO issue and abstract, https://pubsonline.informs.org/doi/10.1287/mnsc.2020.3922 ; warm-start paper, https://www.jmlr.org/papers/v25/23-1174.html ; OSQP author-hosted publication record, https://web.stanford.edu/~boyd/papers/osqp.html . These support the bibliographic and positioning statements, not a claim that a search proves exhaustive novelty.
'''
        p.write_text(s)
    p=R/'DESIGN.json';d=json.loads(p.read_text())
    d.update(revision='R22',inherited_source='c2d25791bd1f4c2b1801a446376a86c50eb381fe',
      provenance_note='R21 was an ordinary source checkpoint, not a completed manuscript. R22 executes its numerical design without changing frozen models, seeds, tolerances or sampling targets.',
      additional_theory='Complete-price dual attainment without strict feasibility; exact-iterate projected-gradient rate; auditable context transport. Independent exact checks supplement the proofs.')
    p.write_text(json.dumps(d,indent=2)+'\n')
    print('R22 ordinary sources materialized and complete-dual additions integrated.')
if __name__=='__main__': run()
