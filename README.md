# NDU — Operations Research revision R37

**Service Contracts with Limited Memory: Participation, Randomization, and Exact Design**

Current branch: `revision/ndu-operations-research-r37-integrated-frontier-20260924`.

This revision addresses the **independent R36 report dated September 24, 2026**, at review commit `f26f4da71207a7613735b0504bc34dbe231813c1`, reviewing manuscript commit `8b17bed9079aa8e3bcaf52e6a5847a60cbf7d7ca`. It does not mistake the earlier R30 report for the current review.

## Current readers

The authoritative article is root `main.tex` / `main.pdf`; the authoritative electronic companion is root `electronic_companion.tex` / `electronic_companion.pdf`. The R37 package contains `RESPONSE_TO_REFEREES.md` / `.pdf`, the current `code/` directory, measured `results/`, and `BUILD_VALIDATION.json`. The build manifest records actual page counts, reader hashes, source identity, executed validation, and the complete base-tree preservation audit.

The paper is now organized around one decision problem: how participation timing changes the service value of a restricted writable alphabet. It preserves global optimization of the continuous highest codeword, the cap-anchoring result, the pathwise-versus-expected distinction, and the contractual Monge identity. Standard staircase completion and SMAWK are attributed to the appropriate full/partial-matrix literature. The main proof covers both favorable orientations, ties, wholly infeasible selected rows, column offsets, and predecessor reachability explicitly.

A stipulated renewal-desk/dispatch-gateway mechanism specifies offer timing, exit, draw visibility, and charged information. A bounded-overrun variant is solved for the existing three-branch example. Integrated pricing treats writable bits, a stated read-only implementation menu, evaluation work, and amortized compilation as separate resources.

## Executed evidence

The new exact suite checks 784 completed matrices, 282,832 selected-submatrix row minima, 98,728 wholly padded selected rows, 1,890 exact frontier equalities and controller replays, 190 independent bounded-overrun all-pairs equalities, 33 tolerance-frontier values, and 4,092 nonanchor-grid checks. These are regression tests, not proofs by finite enumeration. The unchanged R33–R36 suites also pass.

Twenty-four independently assembled reduced networks are solved with compiled HiGHS, then exactly repriced and certified with rational shortest-path potentials. The PADS comparator substitutes independently authored matrix search, while sharing the contractual oracle and reconstruction; this scope is disclosed rather than called a fully independent economic algorithm.

The 30-configuration time/memory/profile study completed without a 120-second process-limit observation. At 16,384 branches and budgets one through eight, expected-participation frontier times were 37.436 seconds for divide-and-conquer, 26.601 for the retained SMAWK implementation, and 26.160 for PADS search. Pathwise times were 52.054, 44.132, and 41.401 seconds, respectively. Smaller cases where linear search is slower remain in the data. These are single-run measurements on the recorded runner, not hardware-independent or native-implementation speed claims. Resident memory, Python-tracked heap, and exclusive profile categories are reported separately. All economic instances are synthetic, not calibrated customer data.

## Reproduce

Use a full Git checkout of this branch, with Python 3.12, SciPy 1.17.0 for the external solver comparison, pdfLaTeX with standard/newtx packages, and Poppler. From the repository root:

```sh
python -m pip install scipy==1.17.0
python revisions/or-r37-integrated-frontier-20260924/code/reproduce.py all
```

The single entry point also accepts `snapshot`, `verify`, `study`, `prepare`, or `build` to reproduce a particular stage. Exact frontier engines and their tests use the Python standard library; HiGHS comparison requires SciPy. `study` reruns timings and therefore need not reproduce the original wall times. `prepare` regenerates the reader tables only from executed result files and archives exact predecessor readers from the pinned base commit. `build` compiles and checks the current sources. A local dirty build is labeled as such instead of receiving a fabricated scientific commit identity. The script does not push, merge, or submit anything by itself.

Example programmatic use, with this package's `code/` on the Python import path:

```python
from frontier import instance, solve
problem = instance(64)
solutions, work = solve(problem, 8, institution='expected', engine='linear')
print(solutions[-1].loss, solutions[-1].codebook)
```

Valid institutions are `expected` and `pathwise`; engines are `quadratic`, `divide`, `linear`, and `pads`. Inputs to `Problem.make` must satisfy the ordered rational model interface. The PADS substitution is process-local, not thread-safe. For bounded-overrun evaluation, `bounded_loss` implements the explicitly pre-draw-intermediate-action protocol; it is not a solver for every possible risk-constrained dynamic contract.

## Preservation and scope

`PRESERVATION_MAP.md` / `.json` maps inherited theorem modules to the current article, companion, or exact preceding readers. `predecessor/` contains the exact R36 main/companion PDFs and wrappers. Historical cross-references with an `H.` prefix point into those preceding readers. Old theorem sources, code, and evidence remain unchanged, including unfavorable results. Older root computational/historical supplements are historical, not competing current submission readers.

The current companion retains the broader compact-response compiler, tight response-size bounds, piecewise-quadratic closure, exact behavioral memory, dispersion result, and shared-table comparison. Their original assumptions are not silently widened or transferred to a different architecture. Main and every earlier review/revision branch are untouched by the R37 write workflow. This is a new manuscript for referee review, not a journal submission or an editorial acceptance claim.
