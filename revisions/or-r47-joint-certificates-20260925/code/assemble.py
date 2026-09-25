"""Assemble current readers without changing any inherited source input."""
from pathlib import Path
import re,json
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];P='revisions/or-r47-joint-certificates-20260925'
TITLE='Limited-Memory Renewal Contracts: Joint Design with Certified Response Coarsening'
ABSTRACT='''A renewal provider must jointly choose a limited command alphabet from a finite catalog and allocate an accepted service obligation across heterogeneous histories. We construct a certified reduction that groups different participation caps and quadratic service costs without changing the original contract. Weighted average caps preserve aggregate capacity, minimum cost curvatures give an optimistic model, and a minimum-cap guard preserves feasible commands. A groupwise recovery procedure restores every individual cap, the exact obligation, and every realization ceiling. Explicit dispersion bounds combine with an exact two-sided price-path oracle and adaptive target-box certificates. For bounded eligibility complexity and primitive scales, the resulting additive approximation scheme is polynomial in the history count and catalog size at any fixed positive accuracy; its accuracy dependence remains explicit and potentially large. Independent checkers verify both the reduced global bound and the original recovered policy. Twenty-four synthetic joint-design cases include up to 256 distinct histories, with exhaustive and uneliminated mixed-integer comparisons. Separate stress cases retain unresolved coarse relaxations and certify their refinement. Canonical contractual allocation, continuous quadratic design, Monge acceleration, budgeted compression, and their proofs remain available under their original assumptions.'''

def run():
    main=(R/'predecessor/main.tex').read_text();ec=(R/'predecessor/electronic_companion.tex').read_text()
    old='Limited-Memory Renewal Contracts: Two-Sided Decomposition and Certified Joint Design'
    forname={old:TITLE,'r46-ec-labels':'r47-ec-labels','r46-main-labels':'r47-main-labels'}
    for a,b in forname.items():main=main.replace(a,b);ec=ec.replace(a,b)
    main=main.replace('Limited-Memory Renewal Contracts:\\newline Two-Sided Decomposition and Certified Joint Design','Limited-Memory Renewal Contracts:\\newline Joint Design with Certified Response Coarsening')
    main=re.sub(r'(?<=\\textbf\{Abstract\.\} ).*?(?=\n\\par\\vspace)',lambda m:ABSTRACT,main,flags=re.S)
    for file in ('introduction','conclusion'):
        main=main.replace(f'revisions/or-r46-box-decomposition-20260925/{file}.tex',f'{P}/{file}.tex')
    main=main.replace('\\input{revisions/or-r45-budgeted-compression-20260924/certificates.tex}\n','')
    main=main.replace('\\input{revisions/or-r46-box-decomposition-20260925/study.tex}',f'\\input{{{P}/coarsening.tex}}\n\\input{{revisions/or-r45-budgeted-compression-20260924/certificates.tex}}\n\\input{{{P}/study.tex}}')
    main=main.replace('revisions/or-r46-box-decomposition-20260925/generated/references.tex',f'{P}/generated/references.tex')
    ec=ec.replace('revisions/or-r46-box-decomposition-20260925/generated/references.tex',f'{P}/generated/references.tex')
    main=main.replace('\\input{revisions/or-r46-box-decomposition-20260925/generated/main_tables.tex}',f'\\input{{{P}/generated/antecedent_main_tables.tex}}\n\\input{{{P}/generated/main_tables.tex}}')
    ec=ec.replace('This companion retains the complete preceding mathematical chain and supplies numerical and implementation details for joint target-box design. Historical numerical records and full predecessor readers remain separately preserved; they are not represented as new executions.',
       'This companion retains the preceding mathematical chain, the two-sided decomposition study, and supplemental certificates. It also supplies the distinct-history stress and independent mixed-integer comparisons. Inherited protocols and records are identified by their revision directories; they are not relabeled as new executions.')
    ec=ec.replace('\\input{revisions/or-r46-box-decomposition-20260925/protocol.tex}',
       '\\input{revisions/or-r46-box-decomposition-20260925/study.tex}\n\\input{revisions/or-r46-box-decomposition-20260925/protocol.tex}')
    ec=ec.replace('\\input{revisions/or-r46-box-decomposition-20260925/generated/companion_tables.tex}',
       f'\\input{{{P}/generated/companion_tables.tex}}\n\\input{{revisions/or-r46-box-decomposition-20260925/generated/companion_tables.tex}}')
    # Reader copy updates provenance, leaving all antecedent source files intact.
    oldtables=(R.parent/'or-r46-box-decomposition-20260925/generated/main_tables.tex').read_text()
    end=oldtables.index('\\end{table}')+len('\\end{table}')
    contribution=r'''\begin{table}[p]\centering
\caption{Theorem-level contribution map. Antecedent statements and proofs remain in the current readers.}\label{tab:r46-contributions}
\begin{tabular}{p{.29\textwidth}p{.38\textwidth}p{.23\textwidth}}\toprule
Component & Scope & Provenance \\\midrule
Canonical and continuous design & Exact response, institutional endpoints, continuous and Monge results & Antecedent, Theorems~\ref{thm:eligible}, \ref{thm:r37-linear} \\
Saturated charged path & Globally exact forced targets & R42; Corollary~\ref{cor:r45-saturated} \\
Unrestricted price path and prefix search & Polynomial oracle and finite joint search & R43; Theorems~\ref{thm:r43-price}--\ref{thm:r43-search} \\
Conditional compression and full net & Fixed targets; fixed-history additive scheme & R45; Theorems~\ref{thm:r45-frontier}, \ref{thm:r45-net} \\
Exact types, two-sided paths and box covers & Exact repeated-type reduction; polynomial box oracle; finite accuracy & R46; Proposition~\ref{prop:r46-types}, Theorems~\ref{thm:r46-box}, \ref{thm:r46-adaptive} \\
Guarded response coarsening & Different caps and costs; explicit original-contract loss and lift & New, Theorem~\ref{thm:r47-coarsening} \\
Variable-history additive scheme & Bounded eligibility and primitive scales; explicit accuracy dependence & New, Theorem~\ref{thm:r47-variable} \\
Certified refinement and checking & Nested valid intervals; original policy, grouping, Bellman and cover checks & New refinement, Proposition~\ref{prop:r47-refinement}; extended checker \\
\bottomrule\end{tabular}\end{table}'''
    (R/'generated/antecedent_main_tables.tex').write_text(contribution+oldtables[end:])
    ROOT.joinpath('main.tex').write_text(main);ROOT.joinpath('electronic_companion.tex').write_text(ec)
    cmap=dict(baseline='9f260e0d6c4e06cf4227f96865a88f4dab67e58e',
       preserved_original_readers='predecessor/main.pdf and predecessor/electronic_companion.pdf',
       relocated_intact_to_companion=['revisions/or-r46-box-decomposition-20260925/study.tex'],
       new_inputs=[f'{P}/{x}.tex' for x in ('introduction','coarsening','study','conclusion')],
       replaced_editorial_inputs_preserved=['R46 introduction','R46 conclusion','R46 theorem-map reader copy'],
       assertion='Every inherited theorem/proposition/lemma/corollary label is checked in the current main+companion. Every inherited repository file except authorized root readers/indexes remains byte-identical.')
    (R/'CONTENT_MAP.json').write_text(json.dumps(cmap,indent=2)+'\n')
    print('Abstract words',len(ABSTRACT.split()))
if __name__=='__main__':run()
