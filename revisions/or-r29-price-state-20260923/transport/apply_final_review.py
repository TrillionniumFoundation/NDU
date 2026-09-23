#!/usr/bin/env python3
"""Auditable follow-up to the immutable source receipt; no historical source edits."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
ROOT=R.parents[1]

def replace(name,old,new):
    p=R/name;s=p.read_text();assert s.count(old)==1,(name,old)
    p.write_text(s.replace(old,new))

# A clean checkout has no untracked results directory. The generator owns its output.
replace('research.py','def run():','def run():\n    (R/"results").mkdir(parents=True,exist_ok=True)')
replace('price_main.tex','storing $O(N^2+M)$ rational coefficients and graph entries. These are arithmetic, not unit-cost bit-complexity, bounds.',
        'storing $O(N^2+M)$ coefficient and graph entries. Coefficients are rational when the primitives are rational. These are arithmetic, not unit-cost bit-complexity, bounds.')
replace('price_main.tex','The theorem generates its own thresholds before solving the root query.',
        'The bound is relative to the supplied public graph, not to an unbounded family of history augmentations. Arbitrarily enlarging public memory can enlarge $N$; the theorem instead constructs its own bounded price record on that fixed graph. The theorem generates its own thresholds before solving the root query.')

latest=dict(branch='review/operation-research-r29-harsh-20260923',commit='1647d416e7a2806d36b1c9972aff0c0b54779912',
    path='reviews/operation_research_referee_report_r29_2026-09-23.md',blob_sha='ce85546dfcb30764376e9187d558ce8f1db607a2',
    scientific_object='Unchanged R28 manuscript on the nominal, separate R29 branch',
    integration='Read in full during final remote reconciliation; latest report preserved verbatim and all 18 sections answered before scientific publication.')
raw=(ROOT/latest['path']).read_bytes()
assert hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==latest['blob_sha']
(R/'LATEST_REVIEW.json').write_text(json.dumps(latest,indent=2)+'\n')

reply=r'''# Response to the latest R29 referee report and the preceding R28 report

**Actual revised manuscript:** *Accepted Service Adaptation: Finite Continuation Prices and the Value of Memory*  
**Scientific revision branch:** `revision/ndu-operations-research-r29-price-state-20260923`  
**Latest report read in full:** `reviews/operation_research_referee_report_r29_2026-09-23.md`, commit `1647d416e7a2806d36b1c9972aff0c0b54779912`.  
**Earlier report and scientific baseline:** R28 report at `af01e2c33f85835e550896985b7cb83b3f4b784f`; scientific R28 at `b53d644be66e9d27bb58cd0f8529aba0c91ec14c`.

## Version reconciliation

The latest report became visible during final remote reconciliation of this work. It reviews `revision/ndu-operations-research-r29-20260923`, not this new `r29-price-state` branch. Its version audit is correct: the nominal R29 branch contained the R28 manuscript unchanged and did not constitute a scientific revision. We do not count that branch, the creation of our new branch, or our compressed-source receipt as a revised manuscript.

This delivery changes the mathematical content, manuscript, companion, bibliography, README, and checklist, and commits all new sources, evidence, three compiled readers, six byte-identical predecessor readers, and the response below. The final scientific commit is checked separately in a fresh checkout. The latest report is copied verbatim into this branch and independently hash-checked against its reviewed commit. The scientific predecessor remains R28: no intervening revised theorem is silently substituted or omitted.

## Responses to the latest report, Sections 1–18

### 1. No scientific delta on the nominal R29 branch

We agree with the factual audit and correct the delivery, rather than contesting the branch label. Main Sections 4–6 are new: constructive finite continuation prices; a necessary-memory theorem and exact retention frontier; and optimized shared-table condensation and exact fixed-table supporting cuts. Section 7 supplies new coupled-graph evidence. The title page and reader entry points now identify the price-state R29 revision. The manifest, Git diff, exact evidence, compiled readers, and final-SHA status distinguish this scientific revision from an upload receipt or an empty renamed branch.

### 2. Representation versus a new consequence theorem

The old bridge is not relabeled as a new algorithm. It is retained in Appendix C as extensive-form-dual representability. Theorem 4.1 proves a different claim: in the stated positive-scalar-payment, separable-quadratic, no-switching institution, a cap truncates a monotone response and creates at most one threshold. The union of all response breakpoints is bounded by 3N on the compact public graph. This produces both an exact construction and a finite realized memory state. The theorem-specific conclusion, rather than generic duality or the existence of a linking variable, carries the revision.

### 3. Constructive discovery, storage and degeneracy

Theorem 4.1 starts with graph primitives, not an extensive-form optimum. A backward piecewise-affine merge constructs every payment response; one scalar inversion gives the root equality price; forward propagation uses the running maximum of state barriers. The proof supplies O((N+M)N log(N+1)) arithmetic operations/comparisons, O(N^2+M) coefficient/graph storage, at most N+1 price labels, and at most N(N+1) public/incoming-price pairs. Rational primitives produce rational coefficients. No rational bit-complexity bound is asserted. Plateau and tail prices, tied barriers, fixed intervals, binding minimum caps, and infeasible promises are addressed explicitly. Independent code verifies these cases. The bound concerns complete payment responses, not an unproved bound on generic Benders value cuts.

### 4. Benders-style master and a genuinely constructive oracle

The root shared-design master is expressly called Benders-style. Proposition 6.2 constructs an exact fixed-table, positive-release value and supporting cut with the finite-price engine, without full-tree dual input. The table is globally fixed during that oracle call. Optimizing a continuously varying positive-release table is not assigned an unproved finite-cut bound. Proposition 6.1 separately condenses the optimized zero-release table to a graph-sized convex program. The standard master and standard QP are not themselves claimed as new optimization algorithms.

### 5. Modern comparison

Section 2 and the closest-results matrix directly compare Girardeau–Leclere–Philpott, Dowson, Füllner–Rebennack, and Lan, as well as the nested resource-allocation work of Vidal–Jaillet–Maculan, Schoot Uiterkamp–Hurink–Gerards, and Wu–Nip–He. Publication/version metadata and primary sources are recorded in the audit. Water filling, policy graphs, linking variables, convex duality, dynamic programming and Benders/SDDP are treated as established. The exact union bound on a recombining contract graph and the derived necessary-memory/retention frontier are the residual claims submitted for scrutiny. This comparison is not presented as exhaustive proof of priority.

### 6. Construction-scale rather than evaluation-only compression

The production algorithm takes a compact graph and a promise. It neither materializes a history tree nor accepts tree multipliers. The induction bounds response storage before the root query is solved. The compact primal-dual certificate is generated after that construction, not imported from an extensive-form solve. The separate full-tree checker is used only for small-instance independent comparison; it is not called by the graph solver. Thus the new claim concerns construction and storage, not only cheap evaluation after an unspecified expensive offline procedure.

### 7. Table dimension and information accounting

We keep K explicit in the zero-release formulation: K+N variables and O(N+M+K) nonzero occurrences. No arbitrary full-history table is claimed to have small K. The public graph may itself be large if externally augmented with a growing history. Theorem 4.1 instead derives its own at-most-N+1-label record on the supplied graph. Theorem 5.1 quantifies both its worst-case necessity and the value attainable with a limited number of labels. The writable-bit statement counts a changing record index, not the read-only table or the numerical precision of its prices. These distinctions prevent table storage, price precision or exogenous graph growth from being hidden in a memory claim.

### 8. Scope of the new theorem versus the retained general framework

The principal narrative is organized around the constructive institution; the broad signed/general-constraint framework remains in print appendices and companion proofs with its original assumptions. Corollary 4.2 extends the construction to several separable service coordinates under one scalar additive commitment, replacing 3N by 2D+N. Independent separable commitments can be treated coordinatewise. Coupled vector promises, arbitrary signed/nonadditive constraints and intertemporal switching are not silently assigned the ordered-scalar result. For those cases the retained general formulation remains a different statement. We pursue the report's requested deeper structural result, rather than deleting valid mathematics or claiming an unsupported generalization.

### 9. Information design from primitives

Theorem 5.1 derives a concrete retention technology: at most m distinguishable symbols at a common future public state. Binding continuation caps make each branch's required accepted payment distinct. Exact implementation needs at least k symbols for a k-branch family. With fewer symbols, the theorem proves that optimal cells are contiguous in sorted caps, derives their exact welfare loss, and computes the optimal frontier in O(mk^2) arithmetic operations. This is not a supplied acquisition-cost function followed by a first-order condition. A cost can subsequently be compared against the derived value, but no cost calibration or optimal-memory-depth theorem for arbitrary institutions is claimed.

### 10. Adverse cache evidence

The abstract and main computational discussion explicitly retain the 83/84 refresh result and the absence of measured cache speed improvement. The full old computational section is reproduced in the retained appendix, not discarded. Weak-duality governance and active-face checks remain useful boundary material; they do not carry a positive speed claim or the new theorem's novelty. No favorable deployment regime is fabricated.

### 11. Genuinely multistage evidence and meaningful comparators

The new exact suite includes 35 instances, nonstationary recombining graphs through 64 dates and 190 public vertices, heterogeneous coefficients, binding continuation caps, a root equality commitment, and positive-release corridors. Fourteen small instances are independently unfolded and checked using exact full-tree constraint matrices and a numerical convex solve. Eleven shared-table comparators are optimized and independently KKT-certified. Fifty-four feasible table/release perturbations test the supporting-cut inequality. The memory study exhausts all set partitions through six regimes and reports larger frontiers through 32 regimes. This evidence is not independent replication of two-period blocks. It is also not advertised as a broad timing victory over tuned SDDP; the claimed computational result is the proved graph-input construction with exact system-level certificates.

### 12. Conditional covering rates and dimension

The inherited dimension-dependent envelope rates are preserved with their conditional regularity assumptions, but are not used to prove Theorem 4.1. The finite-price construction has no promise grid or epsilon-net and does not turn a d-dimensional covering rate into a dimension-free assertion. Multiple coupled commitments and other excluded features retain their original state/approximation burden. The separation of these results is explicit in the main theorem and comparison matrix.

### 13. Focus without deletion

The main narrative follows one chain: finite prices, necessary memory, optimized restrictions, exact coupled-graph evidence. Release sensitivity, rents, switching paths, the broad promise recursion, correlated caches, governance and the adaptive Bernstein test remain in numbered print appendices and companion proofs. The old empirical section and closest-results table are separately compiled without abridgment. The preservation checker verifies every original mathematical block and all original manuscript labels, rather than relying on a statement that material was merely moved.

### 14. Application status

No field data, estimated outside options, switching or memory costs, managerial deployment, or calibrated service system is invented. The manuscript is a theory submission. The operational conclusion is a primitive-driven retention/value frontier, not an empirical adoption claim. The report's alternative theoretical route is addressed by Theorems 4.1 and 5.1.

### 15. Technical observations

The correct shared-table quantifier and factor-two corridor geometry remain. Global cuts remain valid for every feasible table; exact fixed-table cuts now come from the constructive price oracle. The normalization highlighted in Section 15.4 leads to the reflected-price/running-maximum consequence, the finite label bound and the memory lower bound. Release sensitivity and cache governance retain their original qualifications and are not counted as new general optimization results. The adaptive Bernstein condition remains expressly sufficient, not necessary; neither completeness nor a dimension-independent conservatism bound is asserted for it.

### 16. Presentation and positioning

The abstract now leads with the constructive result and necessary memory, not existential extensive-form reconstruction. The retained representation and master have the requested conventional names. Adverse cache evidence is visible immediately. The main argument is consolidated while all older content remains accessible. We use the official Lengthy Manuscript category rather than falsely claim the regular 30-page category. Actual PDF and conservative nonreference counts, anonymous formatting, references and companion length are checked after compilation.

### 17. Requested fundamental advance

We pursue routes A and B: a graph-input finite exact construction in a stated nontrivial subclass, a sufficient finite dual record, a necessary-memory family, and an exact optimal retention frontier. This is a change of the theorem-level center, not another certificate surrounding the unchanged R28 bridge. We do not claim the alternative field-study route C, or delete and split the user's retained material under route D. The proofs, actual scientific diff and independent checks are the objects to be assessed.

### 18. Editorial recommendation

We acknowledge that the latest report rejected the unchanged nominal R29. That recommendation is not evidence about the new price-state theorem before it is read. Conversely, our new derivations and passing software checks are not evidence of editorial acceptance. The package supplies the stronger scientific response and complete preserved record for a further independent assessment of correctness, priority and significance. No journal-system submission or referee approval is claimed.

---

# Detailed response to the preceding R28 report (preserved)

'''
old=(R/'RESPONSE_TO_REFEREES.md').read_text()
(R/'RESPONSE_TO_REFEREES.md').write_text(reply+old)

replace('README.template.md','Latest referee-report base: `af01e2c33f85835e550896985b7cb83b3f4b784f`',
        'Scientific preservation base / preceding R28 report: `af01e2c33f85835e550896985b7cb83b3f4b784f`  \nLatest R29 report: `1647d416e7a2806d36b1c9972aff0c0b54779912` (read and integrated during final remote reconciliation)')
replace('README.template.md','- [Latest referee report, unchanged](reviews/operation_research_referee_report_r28_2026-09-23.md)',
        '- [Latest R29 referee report, unchanged](reviews/operation_research_referee_report_r29_2026-09-23.md) · [Preceding R28 report](reviews/operation_research_referee_report_r28_2026-09-23.md)')
replace('README.template.md','## New results',
        'The latest report examined the separate nominal `revision/ndu-operations-research-r29-20260923` branch, which carried R28 unchanged. This `r29-price-state` branch is the actual scientific revision, with a new theorem chain, new experiments and compiled readers. The response covers all 18 latest-report sections as well as the preceding report.\n\n## New results')
replace('submission_checklist.template.md','- [x] Latest R28 report read at review commit `af01e2c33f85835e550896985b7cb83b3f4b784f`; report unchanged.',
        '- [x] Latest R29 report read in full at `1647d416e7a2806d36b1c9972aff0c0b54779912`, preserved verbatim, and answered in all 18 sections.\n- [x] Preceding R28 report read at `af01e2c33f85835e550896985b7cb83b3f4b784f`; report and scientific baseline preserved unchanged.')
p=R/'DERIVATION_PROVENANCE.md';p.write_text(p.read_text()+'''\n## Latest-review reconciliation before scientific publication\n\nThe R29 report at `1647d416e7a2806d36b1c9972aff0c0b54779912` appeared during this work and was read in full before publication. It evaluates unchanged R28 content on the separate nominal R29 branch. Its original file is preserved at `reviews/operation_research_referee_report_r29_2026-09-23.md`, Git blob `ce85546dfcb30764376e9187d558ce8f1db607a2`. `LATEST_REVIEW.json` and the package checker verify this additional report. The response now answers Sections 1–18 and preserves the full preceding R28 response. The new source receipt is explicitly not treated as the scientific revision; only the final committed manuscripts/evidence and its fresh-checkout status are delivery evidence.\n\nThe final source overlay also makes output-directory initialization safe on a clean checkout and clarifies that stored coefficients are rational for rational primitives. It does not change the exact algorithm, the input suite, or any original theorem's hypotheses.\n''')

replace('check_package.py',"    preserve=json.loads((R/'PRESERVATION.json').read_text())", "    preserve=json.loads((R/'PRESERVATION.json').read_text())\n    latest=json.loads((R/'LATEST_REVIEW.json').read_text())\n    assert gitsha(ROOT/latest['path'])==latest['blob_sha'],'latest R29 referee report changed'")
replace('check_package.py',"        'preserved_baseline_files':len(inherited)", "        'latest_review':latest,'preserved_baseline_files':len(inherited)")
replace('check_package.py',"        paths=[ROOT/f for f in READERS+LABELS]", "        paths=[ROOT/f for f in READERS+LABELS]+[ROOT/latest['path']]")
replace('check_package.py',"          '| Document | PDF pages", "          f\"Latest report: `{latest['commit']}`; all 18 sections answered; original report Git blob verified.\\n\\n\"\n          '| Document | PDF pages")
print('Final overlay: clean-output initialization, rational-data wording, latest R29 report and all 18 responses; historical content unchanged.')
