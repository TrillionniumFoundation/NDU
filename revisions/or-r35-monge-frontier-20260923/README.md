# R35 source package

Run from the repository root:

```sh
R=revisions/or-r35-monge-frontier-20260923
python "$R/verify.py"
python "$R/benchmark.py"
python "$R/reproduce_inherited.py"
python "$R/build_validate.py"
```

The test/benchmark scripts require only Python 3.12+. Reader construction also uses pdfLaTeX, newtx, standard LaTeX packages, and Poppler. The unchanged R33/R34 source modules remain dependencies under their original directories. Exact Fraction inputs and the validated `Problem.make` interface are mandatory; floating input is not silently approximated.

`monge_frontier.py` exposes `randomized_frontiers(problem, budget)` and `deterministic_frontiers(problem, budget)`, each returning globally optimal solutions for every requested budget and a work-counter object. The algorithm uses proved leftmost monotone minima and the continuous quadratic terminal oracle. Retained seeds, branch identities, or previous tiers are not hidden decoder inputs.

`verification.json`, `benchmark.json`, `scaling.csv`, `inherited_verification.json`, and `BUILD_VALIDATION.json` are generated records. The reader table is generated from the benchmark; do not hand-edit its times. `RESPONSE_TO_REFEREES.md` is the authoritative reply text; `response_reader.py` generates its typeset source. `PRESERVATION_MANIFEST.json` and the build's whole-tree audit check inherited content.
