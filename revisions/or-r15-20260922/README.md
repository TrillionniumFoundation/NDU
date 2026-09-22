# R15 resource-gradient revision: executable study

Scientific predecessor: f34badb1acecd7eaebbb483b32688c77568f88a1.
Latest report: d4b3d13fc3798ef4f474fe4e4cdf0e66b8910462.
Prospective protocol: 13f669f43eae87563dd43453359dcc47c6819665.

Run from the repository root with Python 3.13, a C compiler, and one BLAS thread:

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python -m pip install -r revisions/or-r15-20260922/requirements.txt
python revisions/or-r15-20260922/structural_tests.py
python revisions/or-r15-20260922/study.py
python revisions/or-r15-20260922/star_reassessment.py
python -S revisions/or-r15-20260922/verify.py
```

`qp.py` compiles `osqp_bridge.c` against the OSQP library bundled with CasADi.
Both comparison solvers keep their factorizations cached and update only the
linear cost. The previous-context baseline has its own persistent workspace and
never inherits a solution to the current context from the cold comparator. They differ in whether the six-channel coupling quadratic is in
the online QP. This is not a comparison with a deliberately uncached solver.

The primary independent replication unit is a training/deployment pair. All
seven methods and all eight pairs are retained. Direct-price and non-neural
models are equally eligible for positive results. The primary endpoint and
random seeds are frozen in EXPERIMENT_PLAN.json before this executable source
and before execution. The value labels are numerical approximations with exact
Fenchel gap audits, not symbolic exact optima.

Star training uses 256 original, 128 critical-friction, and 128 high-capacity
contexts per fit. Star context coordinates are rounded to 0.001 before either
solving or learning because the inherited rational auditor uses that grid.
Primitive-shift cases use seeds 15401 through 15404 without fitting to them.
The diagnostic star comparison is distinct from the primary multistage test.

`exact.py` uses only integer arithmetic and Python fractions. It checks the
implemented policy's boxes, all continuation subtrees, both root equalities,
and four resource caps; it then verifies feasible switching/constraint prices
and a Fenchel upper bound. Scalar conjugates are rounded *up* to 1e-12, adding
at most dimension times 1e-12 to the exact dual value. The library-free replay
runs in a new Python interpreter with site packages disabled. This is independent
of the optimizer, not a second independent derivation of the certificate.

The gate protects only performance relative to the specified feasible outside
protocol under the stated model. It is not a misspecification guarantee. A
frozen-policy confidence bound is conditional on the fitted policies. Any
vacuous lower bound is retained, not replaced by an empirical range.

Diagnostic wrapper/derivation tests before this source commit used only seeds
15901--15904, outside every study population. No prespecified study outcome was
inspected before the remote source commit.
