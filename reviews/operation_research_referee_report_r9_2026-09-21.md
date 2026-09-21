# Referee Report on R8 Scientific Revision

**Journal:** Operations Research  
**Manuscript:** *Neural Differential Utility: Accepted Dynamic Service Contracts and Certified Value-Gradient Learning*  
**Reviewed branch:** revision/ndu-operations-research-r8-20260921  
**Reviewed head:** 295c75a7a58a92794b0b9eb96bff8ce827a9e007  
**Immediate predecessor:** revision/ndu-operations-research-r7-20260921 at 26be0b3e3f0eb74134627099ac7d6901ace5d85e  
**Prior report carried into the revision:** reviews/operation_research_referee_report_r8_2026-09-21.md  
**Review branch:** review/operation-research-r9-harsh-20260921  
**Review date:** 2026-09-21  
**Round:** R9 external harsh review of the scientific R8 revision

## Recommendation

**Reject in the present form. I would not recommend another incremental patch on this branch as a journal revision.**

R8 moves in the right theoretical direction, but it is not yet a completed manuscript revision. The active root manuscript remains explicitly labeled **Revision R7**, the root README still identifies R7 as the current scientific revision, and the new R8 theory is stored only in a detached file:

revisions/or-r8-20260921/sections/general_theory.tex

That file is not input by main.tex. The active manuscript therefore does not contain the new R8 results at all.

Even if I generously review the detached theory file as the authors' intended R8 contribution, the revision does not resolve the principal editorial objection from the prior report. The new section replaces several specialized observations by broader convex-analysis statements, but the central results are standard critical-fractile, first-order optimality, normal-cone/KKT, Jensen, and Bregman arguments. They may be useful organizing lemmas for the paper, but they do not by themselves raise the manuscript to the originality and significance threshold of Operations Research.

The revision also does not make the architectural choice requested in the prior report. The active paper still places "Certified Value-Gradient Learning" in the title and abstract, while R8 makes no new computational change whatsoever. All previous objections about the learned polynomial inverse, the benchmark design, the lack of meaningful graph distribution shift, and the absence of a genuinely dynamic high-dimensional learning task therefore remain untouched.

The strongest charitable interpretation is that R8 is a promising **working note for a future Path-A reconstruction** of the paper around accepted adaptive service control. It is not yet that reconstruction.

---

# 1. Audit of what R8 actually changes

I compared the reviewed R8 head against the R7 scientific head.

The entire R8 branch is only three commits ahead of R7, and the scientific diff consists of three files:

1. .github/workflows/ndu-or-r8-validation.yml;
2. reviews/operation_research_referee_report_r8_2026-09-21.md;
3. revisions/or-r8-20260921/sections/general_theory.tex.

There is no R8 replacement of main.tex, no R8 replacement of electronic_companion.tex, no R8 response-to-referee document, no R8 build script, no R8 reproduce script, no R8 results directory, and no R8 manuscript package.

The root manuscript still contains:

- "Revision R7, September 21, 2026";
- inputs only from revisions/or-r7-20260921 and the retained R6 accounting section;
- no reference to general_theory.tex;
- no reference to revisions/or-r8-20260921.

The root README still begins:

"Neural Differential Utility — Operations Research revision R7"

and still states that the current scientific revision is revision/ndu-operations-research-r7-20260921.

This matters. A referee should evaluate the submitted manuscript, not infer a hypothetical future integration from an unattached source fragment.

**As committed, R8 has not revised the paper. It has added a candidate theory section next to the paper.**

That is the first and most concrete reason I cannot recommend acceptance or a normal minor/major revision decision on the supposed R8 manuscript.

---

# 2. What the new theory does improve

The detached R8 section is not empty formalism. It directly addresses several items I asked the authors to confront.

## 2.1 The stock-identification argument is no longer tied to the canonical discrete regime construction

The new quantile proposition correctly identifies the supporting objective

G_z(S) = C_z(S) - xi f_z(S)

with the newsvendor-type critical level

tau_xi = (p + xi - c)/(h + p + xi).

The proposition then explains identification through uniqueness of the constrained minimizer, and it separates the exact atom case from a smooth-demand quadratic-growth case.

This is a useful improvement over relying on the canonical translated demand family.

## 2.2 The authors now compare adaptivity directly against the reoptimized static protocol

The new convex program embeds the optimized static tier in the same accepted feasible set and states a first-order alternative: either the static point satisfies the relevant normal-cone condition or a feasible tangent direction provides a local improvement.

This is cleaner than presenting a special perturbation and then extrapolating from it.

## 2.3 The terminology around the inherited tier is improved

The proposition on the vanishing persistent-state increment explicitly recognizes that the inherited tier is an endogenous state produced by earlier decisions, not an exogenous signal about demand.

That correction was needed.

## 2.4 The authors attempt to separate quadratic-specific facts from general convex facts

The Bregman formulation makes clear that a quadratic "energy" identity is a special case of a more general convex loss decomposition.

That is conceptually useful.

These are genuine improvements. My objection is not that the R8 file is wrong everywhere. My objection is that these improvements are not integrated into the manuscript and, more importantly, that most of the mathematical machinery is standard once the problem is written as a finite-dimensional convex program.

---

# 3. Principal editorial issue: the new "global accepted-adaptivity alternative" is first-order convex optimality, not a flagship-level new theorem

Theorem R8-alternative states, for the reduced accepted convex program,

W(x) = p^T x - F(x) - C^s

over a polyhedral feasible set X, that the following are equivalent at the embedded static solution xbar:

1. some feasible adaptive policy has higher value;
2. there is a feasible tangent direction d with grad W(xbar)^T d > 0;
3. grad W(xbar) is not in the normal cone N_X(xbar).

This is mathematically reasonable. It is also the standard first-order optimality condition for maximizing a differentiable concave function over a convex set.

The accompanying second-order lower bound along a feasible line segment is a standard Taylor/Hessian estimate.

The theorem may be useful as a **lemma that organizes the paper**. It should not be sold as the principal general theory that answers the significance objection from the prior review.

To make this result scientifically substantive for Operations Research, the authors would need to derive from the primitives of the service system verifiable structural conditions that are not merely equivalent restatements of KKT optimality. For example:

- primitive conditions under which the static protocol must be globally optimal;
- primitive conditions under which a specific adaptive information structure creates strictly positive value;
- comparative statics showing how the value of adaptivity changes with adjustment friction, service penalties, persistence, or continuation participation;
- monotone or threshold structure for the optimizer under broad classes of demand and tariff primitives;
- a nontrivial bound relating the accepted adaptive gain to economically interpretable parameters;
- an operational characterization that avoids solving essentially the same high-dimensional convex program that defines W*.

At present, the theorem says: the static solution is improvable exactly when the gradient has a feasible improving direction.

That is correct, but it is not enough.

---

# 4. The new "Bregman loss identity" is also a standard KKT decomposition

Theorem R8-bregman writes the optimality gap as

W* - W(x)
=
D_F(x,x*)
+
eta*^T(b-Ax)
+
v*^T(x*-x),

under KKT stationarity and complementary slackness.

I do not see an algebraic error in the displayed identity under the stated sign convention.

But this is obtained by:

1. adding and subtracting the first-order term of F;
2. substituting KKT stationarity;
3. applying complementary slackness;
4. identifying the convex remainder as a Bregman divergence.

Again, this is a useful bookkeeping identity. It may unify several certificates in the paper. But it is not, as presently framed, a new theory of accepted dynamic contracts or of learning.

The manuscript needs to be very careful about the level of novelty claimed here.

If the authors retain this theorem, they should:

- cite and position it explicitly as a standard convex-analytic decomposition specialized to their accepted-control problem;
- explain exactly what new operational inference becomes possible because of the specialization;
- avoid presenting the algebraic identity itself as a major methodological contribution.

The detached R8 section contains no literature citations at all, despite relying heavily on textbook convex analysis and newsvendor structure. That is not adequate positioning for a flagship journal revision.

---

# 5. There is a real formulation error in the claimed unification with graph coupling

The R8 section claims that the same convex resource function includes "the graph coupling of the computational study" through terms of the form

F(x) = sum_n w_n { M_n(x_n) + A_n(x_n-x_pa(n)) + G_n(x_n) }.

As written, this expression is coordinate-separable apart from the parent adjustment term.

The portfolio experiment, however, uses graph-Laplacian coupling. A term such as

x^T L x

or a sum over service edges of (x_i-x_j)^2 is not representable as a sum of univariate functions G_n(x_n).

The notation could be repaired in at least two ways:

1. define a joint convex coupling G(x), rather than G_n(x_n); or
2. let x_n be a vector of service tiers at a regime-tree node and rewrite p, box constraints, adjustment, and continuation constraints with consistent vector dimensions.

But the current statement mixes a scalar information-set model with a vector graph model and then asserts that the latter is already included.

This is not merely stylistic. The section explicitly advertises a single convex formulation that links the contract theory and the learned portfolio deployment. The displayed formulation does not yet do that.

---

# 6. The quantile identification result is broader than R7, but the novelty remains modest

The new distribution-free identification proposition is one of the better R8 additions.

The derivative calculation is the familiar critical-fractile calculation for a newsvendor objective modified by the supporting service price xi. The exact identification then follows by summing a nonnegative supporting gap under the service-floor and physical-cost commitments.

The smooth-demand relaxation adds a quadratic-growth bound:

E sum_t beta^t ||S_t-s_z_t||^2
<=
(delta_C + xi delta_F)/alpha.

This is a reasonable stability statement.

However, the paper must distinguish **generalization of its own earlier lemma** from **novelty relative to the literature**.

The critical-fractile characterization, convex support argument, and strong-growth stability idea are not themselves surprising. The research question is whether combining them with accepted service commitments yields a new structural conclusion of broad OR value.

R8 does not yet demonstrate that broader conclusion.

There is also an under-specified extension sentence:

"The same assertion holds for vector stocks and any convex supporting gap satisfying (R8-growth)."

For a vector model the paper must define what replaces the scalar fill functional, what supporting multiplier(s) are used, how the service commitment is represented, and exactly which primitive assumptions imply the vector supporting gap. A sentence that any suitable supporting gap works is formally true but nearly tautological.

---

# 7. The customer-neutral reallocation corollary remains a local sufficient mechanism

The smooth-resource corollary identifies a payment-neutral direction that shifts tier toward a higher payment-rate regime and away from a lower payment-rate regime. With positive maintenance slope and zero first derivative of adjustment cost at zero, this produces a positive first-order reward improvement.

This is a useful explanation of the canonical mechanism.

It is still a local sufficient result under restrictive assumptions:

- an interior constant tier;
- ex ante expected-payment restriction;
- fixed stock;
- common maintenance derivative;
- no other tier-dependent cost;
- differentiable adjustment with A'(0)=0;
- two positive-probability regimes with unequal payment rates.

The section correctly notes that an absolute adjustment cost can invalidate the argument because switching friction then appears at first order.

This honesty is good.

But this corollary does not yet characterize the main model with continuation participation, multiple economically meaningful tier costs, or endogenous tariff design. It is not a substitute for broader comparative statics or a structural solution theorem.

---

# 8. The persistent-state result is too narrow to generalize the economically important R7 extension

The proposition bounding

0 <= W_full(lambda)-W_t,z(lambda)
<= lambda A(pi_0)

is a clean observation under:

- exogenous regimes;
- convex stage resource costs;
- compact continuous tiers;
- box constraints;
- ex ante expected linear payment commitments;
- no history-specific continuation promises.

The proof is a Jensen/conditional-mean argument at zero friction plus a comparison bound for lambda > 0.

The difficulty is that the R7 paper's strongest institutional repair was precisely the introduction of **history-specific continuation participation**.

The R8 proposition explicitly says its conditioning argument does not apply to unrestricted history-specific continuation promises.

Therefore the result does not generalize the part of the paper that matters most for the contracting interpretation.

If the authors want persistent-state feedback to be a central theoretical contribution, they need either:

- a theorem that survives the continuation-participation system; or
- a precise explanation that the bound applies only to the ex ante commitment model and that the continuation model may behave qualitatively differently.

At present the "general theory" section risks giving the impression of greater institutional generality than it actually has.

---

# 9. R8 does not make the required manuscript-identity choice

The prior report explicitly recommended choosing between two coherent papers.

## Path A: accepted adaptive service-contract/control theory

This path required:

- removing learning from the title and central contribution unless genuinely necessary;
- reducing historical companion material;
- generalizing the economic theory;
- clarifying endogenous-state language;
- deepening positioning against contract/control literature;
- making the certificate package self-contained;
- optionally adding a real or calibrated service application.

## Path B: certified learning for high-dimensional stochastic control

This path required:

- moving beyond a known quadratic inverse;
- demonstrating a genuinely multistage high-dimensional control task;
- fair amortized numerical-linear-algebra baselines;
- preconditioning and cached factorization;
- stronger distribution shift;
- statistically meaningful timing experiments;
- end-to-end certification costs;
- evidence that value-gradient supervision adds something.

R8 performs only one part of one item from Path A: it adds a detached general-theory section.

The active title is still:

*Neural Differential Utility: Accepted Dynamic Service Contracts and Certified Value-Gradient Learning.*

The active abstract still prominently advertises:

- learned value-gradient critics;
- transfer to 1,024 tier coordinates;
- certified loss per service below one millionth.

No computational file changed between R7 and R8.

Therefore every principal learning objection from the prior report remains open.

This is exactly the incremental-patch behavior the prior report said would not be sufficient.

---

# 10. The learning section is unchanged, so the previous computational rejection basis remains intact

Because R8 contains no new learning experiment, no new benchmark, and no new computational result, I will not repeat the previous report in full. The following blockers remain.

## 10.1 The learned actor is still a fitted polynomial inverse of a known SPD operator

The deployment problem is a structured quadratic solve with known operator form and known spectral enclosure.

The degree-12 learned Chebyshev representation is still competing against an analytic degree-12 Chebyshev inverse that requires no training.

R8 adds no evidence that learning is scientifically necessary.

## 10.2 The direct-solver timing comparison still does not establish a repeated-solve advantage

The previous source audit found that direct baselines factorize inside each timed solve, despite the repeated-decision interpretation on a fixed graph.

R8 does not add cached-factorization results or separate setup from online solve cost.

## 10.3 The graph-transfer claim is still weak

The test graphs remain too close to the training graph family.

R8 adds no random geometric, Erdos-Renyi, small-world, block, weighted, shifted-spectrum, or degree-shift experiments.

## 10.4 The task is still a single structured quadratic update, not the dynamic contract problem

R8 does not connect the learned approximation to the multistage continuation-participation control problem.

## 10.5 Value-gradient supervision still lacks a statistically established advantage

R8 adds no new seed study or statistical comparison.

## 10.6 End-to-end certification latency is still absent

The action time and certification time remain separate in the narrative without an operational end-to-end cost.

If learning stays in the title, these issues must be solved. They cannot be neutralized by adding a convex-analysis section elsewhere.

---

# 11. The fixed-tariff institution remains constrained stochastic control, not general contract design

R8 improves language about endogenous state, but it does not alter the contracting institution.

The model still assumes an externally fixed tariff and observable/contractible operational quantities. The provider chooses a contingent operating protocol subject to participation/service commitments.

That can be an interesting operations model.

It is not a general dynamic contract-design model in the economic sense.

The new normal-cone theorem does not change this. It characterizes when a static operating protocol is first-order optimal within the accepted feasible class; it does not introduce:

- endogenous price menus;
- private information;
- hidden effort;
- information rents;
- incentive compatibility;
- renegotiation bargaining;
- endogenous outside options.

The paper should therefore continue to use narrow language such as "adaptive service protocol under a fixed tariff" unless it expands the economic model.

---

# 12. The practical/application case remains weak

R8 adds no real data, calibration, field application, or independent operational environment.

The canonical accepted-control example remains synthetic.

The 31-case robustness exercise remains a neighborhood study around that synthetic construction.

The 1,024-service portfolio study remains synthetic and uses a highly structured operator whose inverse is analytically understood.

This matters under current Operations Research standards.

The current Stochastic Models statement says that publication decisions consider:

- the importance of the system;
- originality of modeling and analysis;
- quality of results;
- clarity;
- overall utility to the OR/MS community.

The Operations and Supply Chains statement also makes clear that established application areas such as standard inventory theory carry a high methodological bar, and that engineering solutions should be demonstrated in real rather than artificial environments if practical impact is the claim.

R8 does not strengthen either side of that theory/application tradeoff enough.

Official statements:
https://pubsonline.informs.org/page/opre/editorial-statement/area-editors-statements

---

# 13. Reproducibility is still not self-contained, and the new R8 workflow is not a scientific validation workflow

The prior report identified missing committed artifacts needed to inspect the original certified run directly.

R8 does not change the computational result package, so those concerns remain.

The new workflow is also much weaker than its name suggests.

The workflow:

- triggers on the R8 revision branch;
- is path-filtered only to .github/workflows/ndu-or-r8-validation.yml;
- checks out the repository;
- creates a tar archive of HEAD;
- records the commit SHA;
- uploads the archive for 14 days.

It does **not**:

- compile the manuscript;
- compile the electronic companion;
- run the exact certificate checks;
- run the reproduction script;
- verify the accepted hierarchy;
- run the continuation-participation certificate;
- run the portfolio certificate;
- validate the new R8 theorem section;
- trigger when general_theory.tex changes.

In particular, the final scientific commit that adds general_theory.tex is outside the workflow's path filter.

Thus "NDU OR R8 validation" is not validation of R8's science. It is a temporary source-export convenience.

Operations Research's current Data, Software, and Computation statement emphasizes both reproducibility and the scientific validity/generalizability of empirical testing. The code/data policy expects code, scripts, data, and instructions sufficient to reproduce computational results.

Official policy:
https://pubsonline.informs.org/page/opre/code-and-data-disclosure-policy

For this paper, an R8 validation workflow should at minimum build the actual R8 manuscript and replay the machine-checkable claims that appear in it.

---

# 14. Contribution-to-length and exposition are now worse unless the paper is reconstructed

The prior report already found the submission historically layered and overfull.

R8 adds another 118-line theory section without deleting, consolidating, or relocating any existing material.

If that section is eventually inserted into the current 31-page manuscript while the neural study and historical companion remain intact, the contribution-to-length ratio worsens.

The current Optimization area statement explicitly says that submissions are evaluated on modeling, theory, algorithms, computation, or applications; a paper should excel in at least one dimension, should be clear and concise, and is evaluated on contribution relative to length.

R8's correct response is not to append another theorem family.

It is to decide what the paper is and remove material that does not serve that identity.

---

# 15. Detailed mathematical comments on general_theory.tex

I list these separately so that the authors can distinguish correctness issues from editorial significance.

## 15.1 Quantile proposition

The scalar derivative calculation appears correct under the usual integrability assumptions and with left/right CDF values used at atoms.

Please define the one-sided derivative notation explicitly rather than saying only that F_z(S-) and F_z(S) are substituted.

Clarify the constrained-boundary case: if the critical fractile lies outside the attainable CDF range on the compact interval, the constrained minimizer is an endpoint rather than an interior quantile.

The proposition currently assumes 0 < tau_xi < 1, but that alone does not guarantee the selected constrained interval contains a point satisfying the quantile condition.

## 15.2 Exact identification from aggregate commitments

The supporting-gap argument relies on exogenous regime occupation weights being the same under the comparator and the adaptive policy.

This should be stated as a model assumption in the theorem, not left mainly to the proof.

If future versions allow tier decisions to affect demand regime transitions, the argument no longer carries through without modification.

## 15.3 Approximate identification

The quadratic-growth assumption is strong and should be presented as such.

The density-lower-bound example is fine, but the authors should state the exact stock interval over which the density lower bound is required.

Do not blur the canonical atomic exact-identification case with the smooth strongly curved approximate-identification case.

## 15.4 Global alternative

Define the tangent cone and normal cone formally once.

Define s_max.

If the claimed direction test is implemented as a linear program under an infinity-norm normalization, write that optimization problem explicitly.

Otherwise the statement "the direction test is a linear optimization problem" is more suggestive than operational.

## 15.5 Graph coupling

As noted above, replace the separable G_n(x_n) representation by a mathematically consistent joint coupling function if the theorem is intended to include the portfolio graph.

## 15.6 Customer-neutral direction

The proof correctly uses zero first-order adjustment cost at a constant tier.

But the paper should state whether outgoing and incoming switching terms at the perturbed node are all covered by the derivative-zero assumption. In a tree, changing one information-set action affects more than one adjacent adjustment term.

The argument appears repairable, but it should be written at the full objective level rather than verbally.

## 15.7 Persistent-state proposition

Define exactly what is meant by "full" history when the only endogenous carry-over is the inherited tier.

The conditional-mean argument depends on the absence of other history-dependent feasibility constraints and state variables.

The caveat about continuation promises is important and should be stated in the proposition header or immediately before it, not only after the proof.

## 15.8 Bregman identity

The algebra is fine under the stated stationarity sign convention.

But if equality constraints are used to represent shared coordinates for restricted information classes, state how they enter the KKT system. Encoding them as paired inequalities is possible but obscures the multiplier interpretation.

## 15.9 KKT existence sentence

The statement that polyhedral feasibility supplies the multipliers should be phrased carefully. What is needed is the normal-cone representation for the feasible polyhedron at an optimizer of a differentiable convex problem.

A short standard citation would be better than an unsupported blanket statement.

## 15.10 Notation overload

G_z is first used for the stock supporting objective/gap, while G_n later denotes a tier-resource term.

Use different symbols.

Similarly, F is overloaded conceptually between fill quantities and the script F resource objective. This is avoidable.

---

# 16. Literature positioning is insufficient for the new section

The R8 section currently contains no citations.

That is particularly problematic because its principal ingredients are mature:

- critical-fractile/newsvendor analysis;
- convex supporting hyperplanes;
- tangent and normal cones;
- first-order optimality for concave programs;
- KKT multipliers;
- Bregman divergences;
- Jensen conditional-mean arguments;
- strong convexity/quadratic-growth stability.

A top-journal revision cannot present a chain of standard tools as "general theory" without distinguishing:

1. what is textbook;
2. what is a known idea newly applied to this service model;
3. what is actually new.

The paper needs a direct literature map.

Without that map, I cannot determine that the new theorem package advances the OR literature rather than simply rewriting the accepted policy problem in convex-analytic notation.

---

# 17. What would constitute a serious next revision

I would not recommend R10 as another additive patch.

A credible next submission should be rebuilt around one of two coherent identities.

## Option A: accepted adaptive service control under a fixed tariff

This is still the more promising route.

A serious reconstruction would:

1. retitle the paper around adaptive service protocols, not "Neural Differential Utility";
2. remove "Certified Value-Gradient Learning" from the title unless learning becomes essential;
3. integrate the R8 general theory into the main theorem chain;
4. explicitly position every standard convex ingredient;
5. derive new primitive comparative statics beyond KKT restatements;
6. treat continuation participation inside the general theory, not only as a separate finite-tree experiment;
7. retain the exact continuous accepted hierarchy and commitment-value result;
8. use the learned portfolio study, if retained at all, only as a short implementation illustration;
9. prune historical diffusion/continuous-time material from the active companion;
10. make all certificate records independently inspectable from a versioned archival package;
11. preferably add a calibrated or real service-system application.

A successful Path-A paper would be smaller than the current submission, not larger.

## Option B: certified learned control

If the authors insist that learning is a central contribution, the current R8 theory patch is not enough.

The paper must:

1. solve a genuinely dynamic nonlinear control problem rather than a known quadratic inverse;
2. compare against cached sparse factorization and preconditioned iterative methods;
3. separate setup and repeated online cost;
4. report many timing repetitions and uncertainty;
5. test materially different graph/operator families;
6. evaluate spectral distribution shift;
7. show a reproducible advantage of value-gradient supervision;
8. include end-to-end certificate cost;
9. provide cumulative policy-quality guarantees;
10. demonstrate why a learned representation is preferable to deterministic polynomial approximation.

That is a different research paper.

---

# 18. Minimum requirements before I would recommend another referee round

At a minimum:

- The actual root manuscript must be an R8/R9 manuscript rather than R7.
- main.tex must include the claimed new theory.
- README and submission metadata must identify the same scientific revision.
- A point-by-point response must explain which prior objections are closed, partially closed, or deliberately abandoned.
- The graph-coupling formulation in the new theory must be repaired.
- The new convex results must be positioned against standard literature and claims of novelty narrowed accordingly.
- The authors must choose Path A or Path B.
- If Path A is chosen, the learning material must be demoted substantially unless new evidence makes it essential.
- If Path B is chosen, the computational benchmark must be redesigned rather than merely re-reported.
- The R8/R9 validation workflow must compile and replay the actual scientific claims it is said to validate.
- The reproducibility package must make the claimed original certificate records independently inspectable.

Until these are done, another incremental review round would mostly repeat the same editorial diagnosis.

---

# 19. Final assessment

R7 was a meaningful scientific revision. It fixed several substantive issues.

R8 is different. It is an **unintegrated theory patch**.

The patch contains some sound and useful generalizations, especially the broader stock-identification lemma and the explicit distinction between persistent endogenous state and exogenous information. I do not see a fatal algebraic collapse in the main scalar arguments of the new file.

But the two most prominently advertised "general" results are, in their present form, standard convex optimality/KKT identities specialized to the model. The section also contains a concrete inconsistency in claiming that a coordinate-separable G_n(x_n) term already includes the portfolio graph coupling.

Most importantly, none of this theory is in the active manuscript.

The root manuscript remains R7, the README remains R7, the learning claims remain central, the computational evidence remains unchanged, the reproducibility concerns remain open, and the requested choice between a focused service-control paper and a learned-control paper has not been made.

The current Operations Research Stochastic Models criteria emphasize importance, originality, quality, clarity, and broad OR/MS utility; the empirical standards separately emphasize reproducibility and valid generalization of computational evidence. R8 does not yet meet that combined bar.

**Recommendation: Reject. A substantially reconstructed Path-A manuscript could merit fresh review as a new submission. I would not support continuing the present architecture through another incremental revision cycle.**
