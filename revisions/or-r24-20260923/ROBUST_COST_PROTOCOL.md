# R24 additional robust cost check

Before running this additional check, fix 16 contexts with seed 2407401, radii 0 and 1/4, and the two unchanged eight-model ensembles plus classical robust maximin. Run sequentially, not concurrently with other timing studies.

Record model loading separately. For each context and radius, measure all eight outer-comparator solves and rational audits. Then measure each complete candidate computation, including individual ensemble prediction, fresh robust optimization, rational repair, and all vertex evaluations. Charge the entire comparator batch once to each independently certified method; also disclose its actual reuse among methods in the study. Preserve every rational decision, dual certificate, and failure.

The purpose is to distinguish complete fresh-host online cost from R23's archived timers, which omitted ensemble prediction. Do not splice newly measured prediction time into archived machine timings. Results are descriptive for fixed implementations, not guarantees over retraining or empirical calibration of the uncertainty set. This is a supplementary design declaration, not an external preregistration.
