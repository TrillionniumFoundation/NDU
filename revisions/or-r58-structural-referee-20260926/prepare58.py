"""Construct R58 from immutable readable R57 sources, never from its outcomes."""
from pathlib import Path
import datetime, hashlib, json, shutil
R = Path(__file__).resolve().parent
ROOT = R.parents[1]
OLD = ROOT / 'revisions/or-r57-deficit-publication-20260926'
PARENT = 'debd4dfa4053cf5f3d6fcf06633b749ef6144ed6'
BASE = 'eee0d39e08eaedc3a26cad792b71c9c5b5a8abd9'
old_rel = OLD.relative_to(ROOT).as_posix()
new_rel = R.relative_to(ROOT).as_posix()


def replace_identity(text):
    return text.replace(old_rel, new_rel).replace('R57', 'R58').replace('.build/r57', '.build/r58').replace('ndu-operations-research-r57-deficit-publication-20260926', 'ndu-operations-research-r58-structural-referee-20260926')


def main():
    if (R / 'PUBLICATION_STATUS.json').exists() and json.loads((R / 'PUBLICATION_STATUS.json').read_text()).get('complete'):
        raise RuntimeError('Published evidence is immutable: reproduce in a separate working copy, not in place')
    for p in OLD.glob('*.tex'):
        if p.name not in ('main.tex', 'electronic_companion.tex', 'RESPONSE_TO_REFEREES.tex'):
            (R / p.name).write_text(replace_identity(p.read_text()))
    for name in ('ABSTRACT.txt', 'CONTENT_MAP.md', 'ROOT_README.md'):
        (R / name).write_text(replace_identity((OLD / name).read_text()))
    (R / 'code').mkdir(exist_ok=True)
    for p in (OLD / 'code').glob('*.py'):
        (R / 'code' / p.name).write_text(replace_identity(p.read_text()).replace('st_size()', 'st_size').replace("'screening56','compression'}", "'screening56','compression','saturation'}"))
    shutil.copytree(OLD / 'predecessor', R / 'predecessor', dirs_exist_ok=True)
    shutil.copytree(OLD / 'development', R / 'development', dirs_exist_ok=True)
    build = R / 'code/build56.py'
    s = build.read_text().replace("'small_menus','price_duality'", "'small_menus','robust_types','price_duality'").replace("'deficit_paths','lattice'", "'deficit_paths','saturation','lattice'")
    s = s.replace("ec+=inp(f'{REL}/diagnostics56.tex')", "ec+=inp(f'{REL}/structural_validation58.tex')+inp(f'{REL}/diagnostics56.tex')")
    build.write_text(s)
    abstract = '''A renewal provider chooses a paid command book and allocates an accepted obligation across histories with expected caps and realization ceilings. We derive exact resource and price path representations with heterogeneous concave terminal rewards. Under a common reward, an optimum uses at most twice the number of distinct expected caps, and the bound is tight. Joint cap and reward classes admit the same reduction. Approximate reward classes yield an oscillation-based loss certificate without changing any feasibility constraint. Complementing edge resources merges all feasible anchors into one deficit dynamic program. Centered kernels and exact promise repair give an additive approximation with quadratic rather than cubic catalog dependence. Zero service costs yield exact lattice optimization at arbitrary command budgets; a saturated promise yields an exact all-budget frontier even with positive service costs. These regimes distinguish numerical granularity from binary encoding and complement weak SUBSET SUM hardness with a nonbinding budget. Price paths support finite branching and independent rational certificates. Synthetic experiments separate exact targets from positive tolerances, expose search mechanics, retain resource limits, and measure screening together with downstream solution and verification. A service-credit architecture distinguishes implementability from empirical calibration.'''
    (R / 'ABSTRACT.txt').write_text(abstract + '\n')
    intro = R / 'introduction.tex'
    intro.write_text(intro.read_text().replace('The exact design decision problem is NP-complete', 'The exact design decision problem is weakly NP-complete') + '\nApproximate reward types extend the menu guarantee beyond exact tariff equality. A catalog-wide reward-oscillation certificate bounds the loss from grouping rewards while leaving probabilities and every feasibility constraint unchanged. At the opposite end of the obligation range, a saturated promise fixes every individual target at its cap. The deficit representation then computes the exact menu-value frontier for all command budgets in one polynomial pass, even with heterogeneous rewards and positive service costs. These two results separate reward similarity, menu size and obligation slack as distinct sources of tractability.\n')
    response = R / 'response_body.tex'
    text = response.read_text()
    start = text.index('The original optimization problem is retained:')
    pre = r'''\section*{Revision basis and scientific changes}
We thank the referee for distinguishing genuine scientific revisions from branch names and publication plans. The latest R56 report at review commit \path{1bf0400f3540605d2ac68d2a40e8bcfb377d5446} correctly identified the missing R56 manuscript. The last complete predecessor was R54 at \path{eee0d39e08eaedc3a26cad792b71c9c5b5a8abd9}.

R58 starts from the subsequent, readable R57 source commit \path{debd4dfa4053cf5f3d6fcf06633b749ef6144ed6}, which itself starts directly from the R54 scientific tip. R57's workflow executed its declared study and built its readers, but failed while writing archive metadata, before the final repository publication. We do not describe that workflow as a completed publication. R58 repairs the packaging and publication checks, supplies additional structural results, and executes a new source-frozen study. Its numerical statements are generated from the new records, not copied from the failed run.

The new structural results are an oscillation-certified approximate-type compression theorem and an exact all-budget saturated-promise frontier. They strengthen the small-menu and heterogeneous-reward answer while preserving the recovered cap-count, deficit, lattice and price-path work. Reviewer-output commits are not added to the author-revision delta. All inherited scientific-source blobs remain unchanged outside the explicitly versioned root readers, whose exact predecessors are retained. Existing branches remain unchanged.

'''
    text = pre + text[start:]
    text = text.replace('R58 starts directly from that R54 scientific tip.', 'R58 preserves the clean scientific ancestry through the R57 source tip.')
    text += r'''
\section{Additional R58 structural answers and verification}
\subsection{Reward types need not coincide exactly}
Theorem~\ref{thm:robusttypes58} proves a menu-size versus approximation tradeoff in the original feasible set. It compares expectations of the catalog reward error under two feasible policies, so the loss is bounded by its weighted oscillation rather than an unnecessarily larger absolute-level error. Additive reward offsets cancel. The result supplies both a compression of any given policy and an optimization procedure through a prototype problem. No unknown optimum is required as algorithmic input. The implementation checks 24 original/prototype pairs against exhaustive enumeration, including zero-dispersion cases, and independently verifies the recovered original policies.

\subsection{A genuinely polynomial arbitrary-budget regime with positive service costs}
Corollary~\ref{cor:saturation58} exploits a saturated accepted promise, not zero service cost. The original target constraints force every target to its own cap. Every deficit is zero, so evaluating full-capacity arc weights and one selected-count recursion produces the complete at-most-budget value frontier. The method retains heterogeneous caps, ceilings, rewards and positive costs. A separate implementation is compared with exhaustive enumeration on 24 models across all seven budgets. All 168 original-space budget certificates are checked by the existing independent deficit verifier, which does not import the new frontier solver. Off-saturation requests and altered upper bounds are rejected.

\subsection{Publication failure repaired without altering the evidence}
The R57 failure called a file-size property as a function after the PDFs had already been built. The old archive also gathered unrelated historical evidence into one unnecessarily large ZIP. R58 supplies a checked, self-contained current-study and reader package with all original records used in its retained R52--R54 tables. Earlier repository evidence is preserved in Git, not deleted to make the archive smaller. Archive integrity, reader dependencies, current source hashes, the declared execution set and inherited Git blobs are checked before publication. A clean extracted copy rechecks the structural tests and rebuilds the readers. Automated PASS denotes these finite checks and artifact integrity; the universal proofs remain mathematical arguments submitted for referee review.
'''
    response.write_text(text)
    conclusions = R / 'conclusion.tex'
    conclusions.write_text(conclusions.read_text() + '\nApproximate reward types provide a certified tradeoff between menu size and value without perturbing feasibility. Saturation provides a separate exact all-budget regime with positive service costs. Together these results show why the useful structural parameters are not interchangeable with numerical precision or command count alone.\n')
    content = R / 'CONTENT_MAP.md'
    content.write_text(content.read_text() + '\n## R58 additions\n\n- `robust_types.tex`: oscillation-certified approximate reward-type compression; original feasibility unchanged.\n- `saturation.tex`: exact all-budget saturated-promise frontier with positive service costs.\n- `code/saturation.py`: one-pass frontier and compatible certificate export.\n- `code/structural58.py`, `results/STRUCTURAL_R58.json`: 24 prototype pairs and 168 independently checked budget certificates.\n- `structural_validation58.tex`: exact validation scope; separate from 225 timed method runs.\n- `code/release58.py`: preservation, dependency-complete packaging and extracted-copy validation.\n')
    readme = R / 'ROOT_README.md'
    t = readme.read_text().replace('Scientific parent: `eee0d39e08eaedc3a26cad792b71c9c5b5a8abd9` (the actual R54 scientific tip).', 'Source parent: `debd4dfa4053cf5f3d6fcf06633b749ef6144ed6` (R57 readable source).\nLast complete scientific predecessor: `eee0d39e08eaedc3a26cad792b71c9c5b5a8abd9` (R54).')
    t = t.replace('python "$R/code/revision57.py" preservation package', 'python "$R/code/release58.py" preservation package extracted_check finalize')
    t = t.replace('python "$R/code/tests56.py"', 'python "$R/code/tests56.py"\npython "$R/code/structural58.py"')
    t = t.replace('`CODE_AND_DATA.zip` contains retained runnable source/data dependencies', '`CODE_AND_DATA.zip` contains the self-contained current study, compiled-reader dependencies, and original R52--R54 evidence used in retained tables')
    t += '\n## Additional R58 results and exact reproduction\n\nApproximate reward groups carry an oscillation loss certificate while all feasibility inputs remain fixed. A one-pass saturated-promise algorithm computes the exact frontier at every budget, including positive service costs. `STRUCTURAL_R58.json` contains 24 prototype pairs, 168 independent budget checks and 48 expected rejection tests. These theorem regressions are separate from the 225 timed method runs.\n\nThe preceding R57 Actions run `36248623200` built PDFs but failed in ZIP metadata before pushing the readers. This revision does not reuse its timings. `SOURCE_LINEAGE.json` records that distinction. Older branches and files are preserved. The current ZIP intentionally excludes unrelated earlier benchmark archives; those remain in Git.\n\nTo validate existing evidence without rerunning benchmarks, use `python "$R/code/release58.py" verify`. To rebuild the readers use `python "$R/code/build56.py"`. Full timing reruns belong in a separate copy with the old `results/` archived first. The additional structural test uses exact arithmetic and can be rerun independently; timings and machine-dependent outcomes must never be relabeled as the committed study.\n'
    readme.write_text(t)
    protocol = json.loads((OLD / 'PROTOCOL.json').read_text())
    protocol.update(revision='R58', source_parent=PARENT, scientific_parent=BASE,
        changes='New oscillation compression and saturated all-budget frontier; fresh execution of the disclosed 225-run design; publication and archive closure repaired.',
        additional_structural_protocol=dict(seeds=list(range(5800, 5824)), prototype_groups=2, histories=4, catalog_commands=7, budgets=list(range(1, 8)), expected_type_models=24, expected_budget_certificates=168, expected_rejections=48, not_pooled_with_timed_runs=True))
    (R / 'PROTOCOL.json').write_text(json.dumps(protocol, indent=2) + '\n')
    (R / 'SOURCE_LINEAGE.json').write_text(json.dumps(dict(revision='R58',source_parent=PARENT,last_complete_scientific_parent=BASE,governing_review='1bf0400f3540605d2ac68d2a40e8bcfb377d5446',previous_failed_publication_run=36248623200,previous_artifact_id=10908577185,previous_artifact_sha256='809e71432aeb85696f7aad938d405253493046324769633cc9a1f2a4ac1fc5ba',previous_failure='ZIP metadata called st_size as a function after all three PDFs compiled. Final push was skipped.',timings_reused=False,new_referee_outputs_merged=False),indent=2)+'\n')
    (R / 'PUBLICATION_STATUS.json').write_text(json.dumps(dict(stage='SOURCE_PREPARED', complete=False),indent=2)+'\n')
    print('Prepared R58 source; no timed output copied from R57.')

if __name__ == '__main__':
    main()
