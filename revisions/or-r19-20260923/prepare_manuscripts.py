#!/usr/bin/env python3
"""Assemble the current manuscript; original revision sources are never edited."""
from pathlib import Path
import shutil,re
ROOT=Path(__file__).resolve().parents[2];R=Path(__file__).resolve().parent
p=R/'predecessor';p.mkdir(exist_ok=True)
for name in ['main.tex','main.pdf','main.bbl','main.bib','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md']:
    if not (p/name).exists():shutil.copy2(ROOT/name,p/name)
old=(p/'main.tex').read_text();pre=old.split('\\begin{document}')[0]
pre=pre.replace('NDU: Accepted Adaptive Service Control','NDU: Accepted Multistage Service Control')
pre=pre.replace('Accepted Adaptive Service Control and Certified Value-Gradient Learning','Accepted Multistage Service Control and Certified Value-Gradient Decisions')
pre=pre.replace('\\externaldocument{history-labels}[historical_supplement.pdf]','\\externaldocument{legacy-main-labels}[revisions/or-r19-20260923/predecessor/main.pdf]\n\\externaldocument{legacy-ec-labels}[revisions/or-r19-20260923/predecessor/electronic_companion.pdf]\n\\externaldocument{history-labels}[historical_supplement.pdf]')
intro=r'''\begin{document}
\begin{titlepage}\centering
{\Large\bfseries Neural Differential Utility:\\ Accepted Multistage Service Control and\\ Certified Value-Gradient Decisions\par}
\vspace{.3in}{Anonymous manuscript for Operations Research\par}\vspace{.25in}
\begin{minipage}{\textwidth}
\textbf{Abstract.}
A service provider can revise persistent contractual tiers only when customers accept the continuation protocol and physical service commitments remain intact. We characterize accepted adaptation by continuation prices, boundary scarcity, and switching capacities on a full scenario tree. Exact transfer coordinates yield constructive critical-friction brackets and profitable feasible deviations. A resource-price representation then connects a scalar value gradient to accepted multistage decisions with vector tiers, multiple capacities, nonconstant comparators, and endogenous switching signs. An exact decomposition gives a global quadratic regret bound without an optimal face; an inexact-response theorem incorporates separately certified solver error and numerical repair. Eight independent training/deployment pairs compare neural critics, direct-price regressors, polynomial response surfaces, and radial-basis interpolation on a coupled multistage problem. Derivative supervision improves the paired neural comparison, while direct-price and non-neural methods are stronger. Independent rational replay, targeted boundary tests, complete accuracy-targeted timing, and a conditional frozen-fleet gain bound distinguish decision quality from computational advantage. The resulting framework integrates acceptance, learnable resource statistics, and auditable implementation without assuming neural superiority or free online optimization.
\par\vspace{.16in}\textbf{Keywords:} accepted service control; resource prices; value-gradient decisions.
\par\vspace{.10in}\textbf{Subject classifications:} Inventory/production: service contracts; Dynamic programming/optimal control: stochastic control; Analysis of algorithms: approximation guarantees.
\par\vspace{.10in}\textbf{Area of review:} Stochastic Models.
\end{minipage}\vfill{Revision R19, September 23, 2026\par}\end{titlepage}
\section{Introduction}
A service provider can adapt physical stock and the contractual tier attached to it. Higher tiers can earn premiums but also increase indemnity, maintenance, and installation costs. A profitable revision is useful only if the customer accepts the resulting continuation and the provider respects its physical commitments. The operational question is therefore not simply whether an adaptive policy has a larger unconstrained objective. It is which accepted revisions create value, when switching friction prevents them, and how repeated decisions can be implemented and checked.

We study Neural Differential Utility as joint control of physical activity and a persistent, externally priced contractual state. Regimes, stock, tiers, and fulfillment are observable and contractible. The provider announces a contingent protocol; in the continuation model the customer may leave at each review. Tariffs and demand transitions are fixed before optimization. There is no private type or hidden effort. Expanded-state stochastic control remains the underlying framework. Acceptance is an explicit constraint, not a claim to escape standard dynamic programming.

The paper develops one chain of results: accepted-control geometry identifies profitable changes; resource prices provide a learnable decision statistic on that same geometry; independent certificates connect the resulting proposal to the implemented policy. This chain is not restricted to a two-date scalar allocation model. It retains multistage participation constraints, vector services, several resource capacities, a nonconstant outside protocol, and switching costs whose signs emerge from optimization.

Our first contribution gives a full-tree balance characterization. A protocol is optimal precisely when marginal operating rewards can be balanced by continuation prices, boundary scarcity, and capacity-constrained switching tensions. On a scalar tree, eliminating the tensions yields cumulative subtree cuts. Exact continuation-transfer coordinates give constructive critical-friction bounds and an explicit profitable accepted deviation when a lower witness separates the comparator from optimality. The normal-cone and total-variation tools are classical; the payment-transfer cone, cumulative continuation prices, and constructive service decisions are the application-specific structure. Large friction supports a zero-switching comparator on a ray, whereas a comparator that already changes can have a bounded optimality interval.

Our second contribution supplies a nonoracular value-gradient implementation on general accepted polyhedra. A scalar optimized value differentiated in specified resource-reward coordinates yields the resource vector of the optimal policy. Its marginal smooth resource cost is a price that drives a feasible response. An exact two-remainder identity converts price error into quadratic regret, globally across capacity and switching transitions. The response retains every acceptance row and the original nonsmooth switching penalty; it does not require the unknown optimal face or switching signs. The guarantee assumes stated curvature, not differentiability of the switching cost. Resource dimension need not be one, and low rank is useful but not mathematically required.

Our third contribution incorporates implementation error explicitly. An independently bounded response-subproblem error, together with an observable price residual, bounds regret for the actual repaired decision. A separate rational conjugate calculation certifies the full objective and every modeled commitment. Learning does not replace this calculation or make a multistage response free. The response can be driven by a neural critic, a non-neural value function, or direct price regression, so their quality and full computational costs can be compared under identical requirements.

Our fourth contribution executes that comparison. Eight independent training/deployment pairs evaluate seven methods on a coupled, two-service, multistage tree. Derivative supervision improves the specified neural comparison, but direct-price regression and simple non-neural surrogates are stronger. A new cost study gives classical algorithms the same initial numerical tolerance and independently certified deployment target. Deliberate tests require actual binding capacities, tier boundaries, and switching kinks, rather than counting generic instances as difficult geometry. Conditional inference for a deployed uniform fleet of frozen policies complements, rather than substitutes for, the eight-pair comparison. The earlier unresolved star comparison and nonlinear transfer failures remain part of the evidence.

These findings support an integrated accepted-control method, not a claim that neural approximation is always necessary. The practical choice among an exact solve, a value-derived price, and direct price prediction depends on approximation quality, required certification, and total cost. The general theory makes those choices comparable without changing customer commitments. All empirical primitives are synthetic; no service-provider calibration, model-misspecification robustness, or advantage of arbitrary retraining is inferred.
'''
related=old[old.index('\\subsection{Related literature'):old.index('\\input{revisions/or-r14-20260922/sections/model.tex}')]
related=related.replace('The acceptance-face theorem and certificate-risk selection result explain the role and limits of this separation.','The full-polyhedron resource-price bridge and its inexact-response certificate explain the role and limits of this separation; the earlier acceptance-face construction remains available in the companion.')
related=related.replace('Our additional contribution identifies the accepted-service reduction and the scalar value derivative that controls its regret, not a new generic multiplier method.','The scalar resource-allocation reduction is retained as a special case. The current bridge keeps general accepted polyhedra and endogenous nonsmooth switching, identifies the partial value gradient associated with coupled resources, and supplies an implemented-decision certificate; it is not a claim to invent a generic multiplier or envelope method.')
related=related[:related.index('The main paper contains')]+r'''The main paper contains the institution, general accepted-tree structure, essential proofs of the new resource-price and inexact-response results, and the repeated multistage comparison. The companion retains the complete scalar and verified-cell developments and details the new checks. Immutable predecessor manuscripts preserve the earlier continuous-time and nonlinear investigations in full, with an explicit relocation map.
'''
body=r'''
\input{revisions/or-r14-20260922/sections/model.tex}
\input{revisions/or-r12-20260922/retained/accepted.tex}
\input{revisions/or-r7-20260921/sections/accepted_continuous.tex}
\input{revisions/or-r14-20260922/sections/general_theory.tex}
\input{revisions/or-r14-20260922/sections/network_structure.tex}
\input{revisions/or-r13-20260922/sections/constructive_flow.tex}
\input{revisions/or-r19-20260923/sections/general_bridge.tex}
\input{revisions/or-r19-20260923/sections/experiment.tex}
\section{Conclusions and operational implications}
Accepted adaptation changes the allocation of resources while preserving announced commitments. Continuation prices and switching capacities identify when a protocol can improve and which branches finance the change. The critical-friction and constructive-transfer results therefore precede, rather than depend on, a choice of learning architecture.

The resource-price bridge now applies to multistage vector decisions with endogenous switching signs. Its value gradient is specified by a perturbation of resource rewards, with acceptance held fixed. Strong convexity supplies a global quadratic regret guarantee; the inexact-response theorem charges the actual subproblem error and repair. Nothing in that argument requires optimal faces or asserts a cheap response on every accepted polyhedron. Cases without the stated curvature retain the general balance theory but not its quadratic error constant without further regularization.

The repeated study demonstrates that derivative supervision can improve a neural critic's decisions in the declared multistage distribution. It also demonstrates stronger direct-price and non-neural alternatives. These observations identify how to implement the mathematical statistic, rather than requiring a preferred architecture to win. Complete accuracy-targeted timing and conservative offline accounting separate useful approximation from reduced resource consumption. The frozen-fleet bound is conditional on a precisely deployed finite collection of models, not an assurance about all future training. Operational calibration and robustness to a misspecified acceptance model remain separate empirical questions; the present certificates cover the known model and the actual implemented decision.
\section*{Data, software, and computation accessibility}
All current manuscript inputs, proofs, scripts, frozen models, primitive definitions, observations, exact audit records, and build instructions are supplied in the versioned review package. The current README identifies a single main manuscript and electronic companion. Earlier revision directories, reports, and scientific observations are preserved unchanged, and exact predecessor root documents are snapshotted with a relocation map. New follow-up measurements are distinguished from retrospective analyses of the R16 dataset. Source and result hashes accompany the published files. All experiments use synthetic data and no personal or confidential operational records.
\clearpage\label{r19-reference-start}
\input{revisions/or-r14-20260922/sections/references.tex}
\label{r19-reference-end}
\end{document}
'''
(R/'main_draft.tex').write_text(pre+intro+related+body)
# Companion: full displaced main components, with legacy diagnostics accessible
# through immutable prior PDFs rather than an ever-expanding current EC.
ecp=(p/'electronic_companion.tex').read_text().split('\\begin{document}')[0]
ecp=ecp.replace('\\usepackage{fancyhdr}', '\\usepackage{fancyhdr}\n\\usepackage[tablesonly,nomarkers,nolists,noheads]{endfloat}')
ecp=ecp.replace('Accepted Adaptive Service Control and Certified Value-Gradient Learning','Accepted Multistage Service Control and Certified Value-Gradient Decisions')
ecp=ecp.replace('\\externaldocument{history-labels}[historical_supplement.pdf]','\\externaldocument{legacy-main-labels}[revisions/or-r19-20260923/predecessor/main.pdf]\n\\externaldocument{legacy-ec-labels}[revisions/or-r19-20260923/predecessor/electronic_companion.pdf]\n\\externaldocument{history-labels}[historical_supplement.pdf]')
ec=r'''\begin{document}
\begin{center}{\Large\bfseries Electronic Companion\par}\medskip
{\large Neural Differential Utility: Accepted Multistage Service Control and Certified Value-Gradient Decisions\par}\medskip
Revision R19, September 23, 2026
\end{center}
This companion retains complete predecessor scalar, cell, and learning components while providing the current multistage implementation details. Their original experiment labels and claims refer to their own distributions and revision dates. They are not pooled as new R19 observations. The immutable R14 main manuscript and electronic companion, and the unchanged historical supplement, preserve all earlier scientific content, including the full nonlinear failures and continuous-time development. Cross-document references to material outside this companion point to those actual predecessor PDFs.
\input{revisions/or-r19-20260923/sections/companion.tex}
\input{revisions/or-r10-20260921/sections/tree_structure.tex}
\input{revisions/or-r13-20260922/sections/learning_bridge.tex}
\input{revisions/or-r13-20260922/sections/certified_cells.tex}
\input{revisions/or-r14-20260922/sections/star_bridge.tex}
\input{revisions/or-r13-20260922/sections/experiment.tex}
\input{revisions/or-r14-20260922/sections/experiment.tex}
\input{revisions/or-r13-20260922/sections/companion.tex}
\input{revisions/or-r14-20260922/sections/companion.tex}
\clearpage\input{revisions/or-r14-20260922/sections/references.tex}
\end{document}
'''
(R/'ec_draft.tex').write_text(ecp+ec)
print('drafts assembled; predecessor root documents preserved')
if __name__=='__main__':pass
