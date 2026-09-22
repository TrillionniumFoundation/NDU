# R23 theorem-level literature and novelty boundary

The complete R22 literature map remains unchanged at `../or-r22-20260923/LITERATURE_MAP.md`. The current main comparison table retains all of its rows and adds the following row.

| Established result and assumptions | What it already supplies | R23 accepted-service consequence |
|---|---|---|
| Ben-Tal and Nemirovski (2000), uncertain-data linear programming; Bertsimas and Sim (2004), tractable robust counterparts and conservatism tradeoffs | Nominal feasibility can fail under data perturbations; robust feasible sets and uncertainty/performance tradeoffs are established. | `thm:r23-robust` combines a robust implemented policy with vertex dual upper bounds on a **common outer class containing all model-specific restricted classes**. It protects gain against the truly reoptimized accepted comparator, not merely the robust restricted value. |
| Affine uncertainty over a polytope; convex combinations; weak duality | Vertex feasibility implies interior feasibility, and linear aggregation preserves upper bounds. | The theorem states exactly where these standard facts apply and where a model-dependent feasible comparator breaks naive vertex reoptimization. The explicit interior-comparator counterexample isolates that failure. |
| Concavity and convex mixing | Mixing with a strict feasible anchor repairs linear inequality violations. | Exact root reconstruction and the minimal rational mixing fraction preserve every uncertain continuation/capacity row and charge value loss for the implemented service policy. This repair's strict-anchor assumption is not imposed on the robust gain theorem. |
| Hoeffding concentration and a union bound for frozen rules | Finite-sample conditional expected-value bounds under independent bounded observations | Companion extension targets worst-hidden-model excess over the true restricted optimum with a safe width `2B`. The new experiment does not claim a positive population lower bound without executing that separate design. |

Verified primary metadata (accessed September 23, 2026):

- Ben-Tal A, Nemirovski A (2000), *Robust solutions of Linear Programming problems contaminated with uncertain data*, Mathematical Programming 88:411–424. DOI 10.1007/PL00011380. Publisher: https://link.springer.com/article/10.1007/PL00011380
- Bertsimas D, Sim M (2004), *The Price of Robustness*, Operations Research 52(1):35–53. DOI 10.1287/opre.1030.0065. Publisher: https://pubsonline.informs.org/doi/10.1287/opre.1030.0065

The new result is not described as inventing generic robust optimization, dual prediction, envelope sensitivity or concentration. Its claimed addition is the accepted-control implementation and the valid economic comparison under simultaneously changing objective and acceptance data.
