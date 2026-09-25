# Sources and audit trail

## Repository evidence

Scientific manuscript: R49 commit `2098592a99e47d36cc9fd16311f21d1858fa6e1e`.
First independent report: `2ac1490e5a4149f8c7e154407fbe6fa6208979db`, path `reviews/operation_research_referee_report_r49_independent_harsh_2026-09-25.md`.
Second independent report and branch parent: `4f0b662bd4184fc77fb57bd09c339bffb6213a69`, path `reviews/operation_research_referee_report_r49_second_independent_harsh_2026-09-25.md`.
Both reports are copied into `reports/` for the response package. The second was the latest review located before this revision; R50 and R51 had no later scientific manuscript at inspection.

The reviewed `group_boxes.tex` sets eta = epsilon/[2 L (E-1)] and displays a coarse factor 4 L (E-1)/epsilon. The second report changes eta to epsilon/[4 L (E-1)] in its counterexample. The revised companion gives an explicit product bound and resolves that difference instead of falsely attributing a missing factor to the original coarser bound.

The R45–R49 derivations and code establish canonical fixed-book allocation, fixed-target paths, group pooling, original-space price bounds, and independent checking. Every earlier derivation is preserved and inventoried in CONTENT_MAP.json. The new resource-path reduction and capacity-repair theorem are developed in this revision and tested against the unchanged original allocator.

## Primary external sources checked on September 25, 2026

Operations Research submission guidelines: https://pubsonline.informs.org/page/opre/submission-guidelines

Aggarwal et al. (1987), Algorithmica 2:195–208, doi:10.1007/BF01840359. Primary metadata: IBM Research and Technion; standard totally monotone matrix searching.

Hassin (1992), Mathematics of Operations Research 17(1):36–42, doi:10.1287/moor.17.1.36. Primary publisher record; constrained shortest-path approximation.

Lorenz and Raz (2001), Operations Research Letters 28(5):213–219, doi:10.1016/S0167-6377(01)00069-4. Primary Elsevier record; constrained shortest-path approximation.

Patriksson (2008), European Journal of Operational Research 185(1):1–46, doi:10.1016/j.ejor.2006.12.006. Primary publisher/author record; continuous nonlinear resource allocation.

Pages and Wilbertz, arXiv:1010.4642v2, March 27, 2012. Author manuscript; mean-preserving splitting and dual quantization. The cited version is identified explicitly, not assigned an unverified journal record.

Wu (1991), Journal of Algorithms 12(4):663–673, doi:10.1016/0196-6774(91)90039-2. Primary Elsevier record; optimal quantization by matrix searching.

Zhang (2012), Operations Research 60(4):850–864, doi:10.1287/opre.1120.1056. Primary INFORMS record; finite policy graphs in adverse selection.

Virtanen et al. (2020), Nature Methods 17:261–272, doi:10.1038/s41592-019-0686-2. SciPy scientific software reference; the executed package version is separately pinned and recorded.

No cited source is credited with the new selected-boundary identity. Classical allocation, interpolation, approximation, and matrix-search components are explicitly distinguished from that identity and its recovery guarantee.
