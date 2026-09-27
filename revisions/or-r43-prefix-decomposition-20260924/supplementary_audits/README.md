# Supplementary general-class stress check

This self-contained exact-arithmetic audit checks the general-cost and branch-specific-threshold version of the R43 price-decomposition theorem. It imports neither the published prefix solver nor the continuous face generator. The common reward is strictly increasing, concave and piecewise linear (not quadratic); branch costs are nondecreasing convex piecewise-linear functions. Branches have separately selected eligibility thresholds, caps and costs. All inputs and arithmetic are rational.

The script reconstructs the stated path recurrence directly and compares it with exhaustive books and explicit support maximization. The recorded local run covers 100 seeded inputs, 600 root-price equalities and 10,272 mandatory-prefix completion equalities. All pass. Exact replay needs only the Python standard library:

```bash
python revisions/or-r43-prefix-decomposition-20260924/supplementary_audits/verify_general_class.py
```

Run without Python's `-O` flag, which disables assertions. The adjacent JSON records the script hash, environment, seed and measured runtime. The original check was executed locally in addition to the publication pipeline. The reader-finalization workflow reruns it and records a separate `general_class_ci_result.json`. It is not counted among the manuscript's main rational-quadratic tests, scaling runs, continuous-enumeration frontier or six SCIP comparisons. It corroborates the general structural theorem; finite testing does not replace its proof.

The final layout moves the additional decomposition contribution paragraph from after the reference list back to the decomposition section, preserving its complete text. The main algorithms, model inputs, reported results and historical files are unchanged. The full scientific pipeline is run 35992653849, with tested scientific source commit bb3fa604d0e4f780fa697046d5b638775f30186c. Reader finalization explicitly verifies that the tested code and evidence remain byte-identical to that commit before recompilation.
