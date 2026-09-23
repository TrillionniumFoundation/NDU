# Literature and style audit — September 23, 2026

## Closest sources and verified content

**Mjelde, K. M. (1983). Resource Allocation with Tree Constraints. Operations Research 31(5):881–890. DOI 10.1287/opre.31.5.881.** Publisher metadata and abstract identify concave resource allocation with subsets arranged as a tree. The current manuscript treats the unfolded problem as part of this lineage, not merely as nested allocation on a chain. Publisher page: https://pubsonline.informs.org/doi/10.1287/opre.31.5.881 . Access was intermittent; a later open returned 403. No full-text theorem-by-theorem implementation claim is made.

**Tang, C. S. (1990). Reducing Separable Convex Programs with Tree Constraints. Management Science 36(11):1407–1412. DOI 10.1287/mnsc.36.11.1407.** Publisher metadata and abstract were accessible. They describe a reduction with at most 2N one-variable convex subproblems. This is reported as a scalar-subproblem count. It is not relabeled as an elementary arithmetic, bit, or whole-parametric-curve bound. Publisher page: https://pubsonline.informs.org/doi/10.1287/mnsc.36.11.1407 . Full article text was not obtained.

**Federgruen, A., and H. Groenevelt (1986). The Greedy Procedure for Resource Allocation Problems: Necessary and Sufficient Conditions for Optimality. Operations Research 34(6):909–918. DOI 10.1287/opre.34.6.909.** The official abstract and metadata were read. The described allocation units are discrete, with a polymatroid feasible region and weakly concave objective. The citation is used to identify the broader feasible-set lineage, not to attribute a continuous rational DAG complexity theorem. Source: https://pubsonline.informs.org/doi/10.1287/opre.34.6.909 .

**Groenevelt, H. (1991). Two algorithms for maximizing a separable concave function over a polymatroid feasible region. European Journal of Operational Research 54(2):227–236. DOI 10.1016/0377-2217(91)90300-K.** Official ScienceDirect abstract and metadata were read. It says both algorithms apply to discrete and continuous versions; the polynomial assertions in that abstract are explicitly for specified discrete cases. Source: https://www.sciencedirect.com/science/article/pii/037722179190300K . This distinction is preserved in the paper. Full text was not obtained.

**Nested allocation.** Vidal–Jaillet–Maculan (2016), Schoot Uiterkamp–Hurink–Gerards (2021), and Wu–Nip–He (2021) remain cited as related nested-constraint algorithms. The exact ascending-chain input model is not silently transferred to arbitrary branching laminar families. Schoot Uiterkamp et al.'s author preprint is arXiv:2009.03880; the journal reference is Computers & Operations Research 135:105451, DOI 10.1016/j.cor.2021.105451.

**Policy graphs and decomposition.** Pereira–Pinto (1991), Girardeau–Leclère–Philpott (2015), and Dowson (2020) are retained. The new comparison is an implemented promise-state recursion on a public graph, not a falsely named SDDP implementation. The paper does not claim public-graph recombination itself is new.

**Numerical implementation.** The final environment was Python 3.13.5, NumPy 2.3.5, and SciPy 1.17.0. The generic convex baseline is SciPy trust-constr, with settings recorded in baselines.py and raw output. Virtanen et al. (2020), Nature Methods 17:261–272, DOI 10.1038/s41592-019-0686-2, was verified against the official Nature page. The general SciPy documentation was consulted, but the executed version, not a web page's latest version, defines these measurements.

## What is and is not verified about priority

The exact mathematical map, normalized memoization equivalence, quotient identities, rational bounds, and memory results are proved self-contained in R30. The manuscript explicitly recognizes that normalized memoization produces the same recursion as an occurrence-indexed marginal reduction. No speed superiority over an equivalent memoized implementation is claimed.

Full texts of all closest classical articles were not obtained in this session. Therefore neither exhaustive historical novelty nor the strongest published complexity under every tree/laminar representation is certified by this audit. The independent tree baseline is a completely specified marginal-allocation implementation, not original authors' code and not a claim of fastest known implementation. This is an evidence boundary, not a reason to discard or weaken the proved R30 results.

## Operations Research presentation

Official source: https://pubsonline.informs.org/page/opre/submission-guidelines , consulted September 23, 2026. The retrieved guidance requires a text-oriented abstract of at most 200 words, an introduction without equations or mathematical notation, an alphabetical author–year reference list, no footnotes, and readable mathematical exposition. The files use 11-point text, one-and-a-half spacing, one-inch margins, anonymous manuscript metadata, a 191-word abstract, and explicit subject classifications/review area. The main is 22 pages including its title page, references, and four tables; the electronic companion is 10 pages. These checks do not establish author consent, conflict declarations, exclusive submission, ORCID entries, or editor/reviewer nominations. Those items require the actual authors' submission records.
