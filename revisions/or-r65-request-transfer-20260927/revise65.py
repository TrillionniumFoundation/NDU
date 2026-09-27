from pathlib import Path
import json
R=Path(__file__).resolve().parent
p=R/'main.tex';s=(R/'archive/r64/main.tex').read_text().replace('.build/r64/','.build/r65/').replace('--- R64','--- R65')
s=s.replace('using a minimum-distortion fee projection.','using a minimum-distortion fee projection within a specified sparse-exception class.')
s=s.replace('Independent checking certifies both the projection and failure of the preceding allowance; it does not trust the binary-search trace.', 'Independent checking binds the model, tolerance, certificate class, and computational guard to an external request. It certifies the projection and failure of the preceding allowance, and checks the transferred policy\'s gross payoff and exact lower formula in \\eqref{eq:robust63}; implementation details are in the companion.')
p.write_text(s)
p=R/'electronic_companion.tex';s=(R/'archive/r64/electronic_companion.tex').read_text().replace('.build/r64/','.build/r65/').replace('--- R64','--- R65')
s=s.replace('Implementation Boundaries and External-Input Verification','Implementation Boundaries and Request-Level Verification')
old='The current adapter requires both the certificate and the external frozen input. It validates the complete set of fields, the original integer allowance, and all model constraints. It then proves exact equality of every rational field, recording the requested byte digest, the certificate-input byte digest, and a canonical rational digest. Only after this binding does the independent mathematical checker verify the proof. A second policy check uses the external original input directly; embedded hybrid probes are bound recursively. Unknown or missing fields, changed parameters, and altered policies are rejected. The adapter imports no optimization routine. A change of rational notation is distinguished from a change of problem data, not accepted on trust.'
new=r'''The request-level adapter receives the certificate and a separately supplied request. Its schema has exactly five fields: schema version, complete physical specification, nonnegative rational tolerance, mathematical certificate class, and configured exception guard. A guard is a nonnegative integer for tariff and robust-tariff proofs and is null for other classes. The physical specification includes the original integer command allowance, even if the algorithm uses a smaller effective allowance. Canonicalization checks all fields and model constraints and compares rational values exactly. Unknown fields and inexact floating-point tolerance encodings are rejected. The certificate envelope contains a copy of the request and its canonical digest; neither a self-declared request nor its digest supplies the external trust anchor. The independent checker requires agreement with the caller's request, checks the mathematical proof, and rechecks the policy against the original input. Embedded hybrid price probes are model-bound recursively. The adapter imports no optimizer.

For a robust proof, the projection tolerance must equal the external tolerance. Its inner tariff guard must equal the requested guard and be at least the independently recomputed modal exception count. The canonical modal tie-rule string is also checked. Thus changing a tolerance, guard, or redundant tie-rule declaration cannot preserve request-level acceptance. A guard check certifies compatibility with the requested configuration, not that a particular executable ran with that configuration. Execution and deadline claims require separate immutable records. Low-level legacy checkers establish mathematical statements only; the current request-level entry point is \texttt{binding65.verify\_request}.'''
assert old in s;s=s.replace(old,new)
s=s.replace('Numerical solver upper bounds are never promoted to exact rational bounds.', 'Numerical solver upper bounds are never promoted to exact rational bounds. The new replay binds all 389 proofs to requests reconstructed from the frozen cases and recorded certificate classes. All 42 robust proofs also pass the tolerance and transfer checks. Their guard is taken from the case, or from the frozen hybrid rule of four exceptions, never inferred from the submitted proof. Legacy proof bytes remain unchanged; the binding envelope is constructed at replay, not asserted to have existed during the original experiment.')
s=s.replace('For a robust certificate the checker first binds the externally requested physical input.', 'For a robust certificate the checker first binds the complete external request.')
s=s.replace('Recomputing these two projections takes $O(N\\log N+(d_{\\rm allow}+1)N)$ rational operations.', 'Recomputing these two projections, with a separate sort for each allowance, takes $O(N\\log N+(d_{\\rm allow}+1)N)$ rational operations.')
s=s.replace('All original policy, one-sided error-budget, and final interval checks remain in force. The compatibility verifier delegates to the independent checker rather than retaining a weaker second verification path.', 'All original policy, one-sided error-budget, and final interval checks remain in force. Minimality is relative to the external tolerance and the stated sparse-exception class, not a self-declared tolerance. The mathematical compatibility verifier delegates to the independent checker; request-level acceptance additionally requires the external binding.')
insert=r'''
\subsection{Certifying the transferred lower policy}\label{sec:transfer65}
Let $\widetilde c$ be the inner proof's selected book, $\widetilde V$ its exact value, and $G_{\rm in}$ its gross payoff before opening charges. The checker independently validates the inner and outer physical policies, requires the same book and equal gross payoffs, and verifies
\[
 G_{\rm out}=G_{\rm in}=\widetilde V+\sum_{i\in\widetilde c}\widetilde\rho_i,
 \qquad L=\widetilde V-\sum_{i\in\widetilde c}(\rho_i-\widetilde\rho_i).
\]
Gross payoffs are recomputed from checked net payoffs and the appropriate book charges, not trusted as metadata. These conditions preserve the theorem's lower formula while allowing a different fixed-book optimal allocation at a tie. They do not assert identity of the physical fields. A feasible same-book allocation with a smaller gross payoff is rejected even when its wider objective interval remains valid. Any declared gross-payoff metadata must agree with this calculation.

Two coordinated regressions reproduce the referee's examples on a three-command, two-history instance. A certificate generated for tolerance $1/200$ has allowance two, whereas the external tolerance $1/10$ permits allowance zero. A second certificate keeps the book and feasibility but reduces the gross payoff by shifting terminal obligation to free preliminary service. The archived model-only checks accept both; the current request-level checker rejects both. The new suite accepts 66 valid request checks, including equivalent rational encodings and a different equal-gross policy, and rejects 25 complete request or metadata adversaries. These are implementation tests, not additional optimization-study observations.
'''
s=s.replace('\n\\subsection{Source closure and reproduction}',insert+'\n\\subsection{Source closure and reproduction}')
s=s.replace('R64 preserves the R63 readers, code, and result snapshot; their unchanged R60/R61 evidence remains shared at its original paths.', 'R65 preserves the complete R64 payload: changed readers and code are archived, and unchanged historical evidence remains at its original paths. The R64 preservation map in turn retains the R63 material and its R60/R61 evidence.')
p.write_text(s)
# Stable standalone response: scientific main narrative unchanged except local scope/binding sentences.
response=r'''\documentclass[11pt,letterpaper]{article}
\usepackage[margin=1in]{geometry}
\usepackage[T1]{fontenc}
\usepackage{amsmath,newtxtext,newtxmath,setspace,xurl}
\usepackage[hidelinks]{hyperref}
\onehalfspacing\setlength{\emergencystretch}{2em}
\begin{document}
\begin{center}{\Large\bfseries Response to the R64 Referee Report}\par
Finite-Catalog Resource Allocation: A Tariff-Sensitive Complexity Frontier\par
Anonymous revision R65 --- September 27, 2026\end{center}
We thank the referee for identifying two distinctions between a valid objective interval and the stronger claims made by its certificate. We have repaired the request-level binding and the transferred-policy check, reproduced both counterexamples, and replayed the frozen evidence. The model, contribution hierarchy, all principal results, proofs, computational observations, and unfavorable outcomes are retained. No new optimization campaign is used to replace the existing evidence.

\section*{1. External request and requested tolerance}
\textbf{Comment.} The previous adapter bound the physical model but not the tolerance determining the minimum projection allowance.

\textbf{Response.} The independent entry point now receives an external request containing the complete physical specification, requested rational tolerance, certificate class, configured guard, and schema version. The envelope contains a canonical request and digest, but these are compared with the caller's separately supplied request rather than trusted. In a robust certificate, its projection tolerance must equal the external tolerance. Minimal allowance is then checked against that same tolerance through the optimal distortion at the reported allowance and failure at its predecessor.

The reproduced three-command example rejects the proof for tolerance $1/200$ when the external request asks for $1/10$, even though its physical model and exact interval are valid. A coordinated change to both envelope and envelope digest also fails against the unchanged external request. Exact rational equivalence is accepted; a floating-point tolerance, unknown field, or changed original command allowance is not silently normalized away. Details are in Companion Section~\ref*{dummy}\hspace{-0.05em}\textnormal{}% replaced below
The executable entry point is \texttt{code/binding65.py}; \texttt{code/produce65.py} emits request-bound envelopes for the tariff and robust-tariff producers. Legacy model-only routines remain available for historical mathematics, not as substitutes for request-level acceptance.

\section*{2. Exact transferred lower formula}
\textbf{Comment.} Equality of the selected book does not establish the theorem's same-policy transfer value.

\textbf{Response.} We adopt the referee's tie-compatible contract. Both policies are independently checked for feasibility and value. The outer policy must select the inner book, have exactly the inner policy's gross payoff, and satisfy
\[
 L=\widetilde V-\sum_{i\in\widetilde c}(\rho_i-\widetilde\rho_i).
\]
The check derives gross payoff from the validated net value and book charges; any separately declared gross value is also checked. It therefore permits a different equally good fixed-book policy without falsely claiming identical physical fields.

The second referee witness retains book $(0,1/2)$ and moves $1/50$ of the first history's obligation to preliminary service. Its interval $[23/100,6/25]$ remains valid, but its lower value is below the required $6/25$. The strengthened checker rejects it for this reason. The unchanged legacy checker accepts it, which is recorded in the regression evidence. A positive test swaps the two identical histories while retaining gross payoff and is accepted. Theorem~6.1 and its perturbation proof are unchanged; the main text and Companion Section ``Certifying the transferred lower policy'' now state what is checked.

\section*{3. Guard and redundant metadata}
\textbf{Comment.} The configured guard and modal tie-rule string were not verified.

\textbf{Response.} The tariff checker validates the canonical string ``smallest rational fee,'' recomputes the modal fee, and requires a nonnegative integer guard at least as large as the actual modal exception count. The request-level checker also requires equality to the external guard. Boolean guards and altered or missing tie-rule declarations are rejected. A uniform surrogate with guard zero remains valid.

This establishes agreement with a declared mathematical request, not an attestation of runtime settings or wall-clock behavior. The companion and receipt make that boundary explicit. For non-tariff proof classes the guard field is null rather than unused but apparently certified metadata.

\section*{4. Regressions and unchanged historical evidence}
The new suite records 66 valid request checks and 25 rejected adversaries, including both coordinated referee witnesses. The retained semantic suite again checks 288 projections against exhaustive retained-subset enumeration, accepts 577 valid certificates, and rejects the ten earlier semantic adversaries. Structural, binding, and exact root-support checks are retained in the qualification record.

We replay all 405 frozen requests. The 389 available proofs comprise 342 rational two-sided certificates and 47 numerical-solver lower policies; 16 requests have no certificate. Every available proof is request-bound. All 42 robust certificates pass both the externally requested tolerance and the exact transfer checks. The replay derives physical inputs and tolerances from frozen cases, certificate classes from immutable records, and guards from the cases or the frozen hybrid rule of four exceptions. It never infers a requested tolerance or guard from the certificate under examination.

The historical files are byte-preserved. An envelope for an old proof is constructed only at replay and is not backdated. The 16 equivalent but byte-different input encodings remain distinguishable from changed inputs. The 45 previously incomplete or unsuccessful checks are not promoted to original timed successes. Parallel replay times are post-study integrity measurements, not replacements for the original optimization or checking times. No numerical solver upper bound is relabeled as a rational certificate.

\section*{5. Exposition and delivery}
The abstract now specifies that minimum-distortion projection is within a stated sparse-exception class. The main narrative adds only the request/transfer contract; implementation detail remains in the companion. The companion explicitly notes the separate sorts for the two checked allowances. The projection-quality table, regret-bound brackets, original timings, failure cases, and stylized service-credit interpretation are preserved. Exact surrogate optimality, exact original feasibility, and additive original optimality remain distinct.

The new branch descends directly from the reviewed R64 author commit. The R64 report is pinned by commit, path, and blob. The package archives the earlier readers and modified sources and verifies every file in the previous manifest through an explicit preservation map. The current manuscript, companion, response, code, data, manifest, and qualification records are delivered together. A read-only check on the actual published commit and a fresh proof replay produce the exact-head receipt. These certify the delivered artifacts and enumerated checks, not editorial acceptance.
\end{document}
'''
response=response.replace('Details are in Companion Section~\\ref*{dummy}\\hspace{-0.05em}\\textnormal{}% replaced below\n', 'The request schema and trust boundary are documented in the companion section ``Binding a mathematical proof to its requested input.''\n\n')
response=response.replace('input.\n', "input.''\n")
assert response.count('``') == response.count("''")
(R/'RESPONSE_TO_REFEREES.tex').write_text(response)
# Current compiler keeps existing style and page limits.
s=(R/'compile64.py').read_text().replace('r64','r65').replace('BUILD64','BUILD65')
(R/'compile65.py').write_text(s)
provenance=dict(revision='R65',scientific_parent='5704e3b4572da9726cab8bdcc8d74d0194f77d9e',scientific_parent_tree='e6d96192b83e764b1c78d437d7861f6f70d4c802',governing_review=dict(branch='review/operation-research-r64-independent-harsh-20260927',commit='3fa2fc1db4257a15af4b3a437c54b306a4589e63',path='reviews/operation_research_referee_report_r64_independent_harsh_2026-09-27.md',blob='4c8f3d94cfa14cf76d1834b0adb1c5251ded056b'),original_artifact=dict(run=36294263291,id=10923925646,sha256='2be4140274d2f3ef5ff01fd40a7f1ce770545bba4de876c471d5451a0759cfb8'),scope='Request and transfer certificate correction. No historical timing or optimization result replaced.')
(R/'PROVENANCE65.json').write_text(json.dumps(provenance,indent=2)+'\n')
