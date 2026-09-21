#!/usr/bin/env python3
"""Derive unchanged/annotated R6 portions without editing their historical files.
All new R7 proofs are ordinary tracked TeX. This preparation step only preserves
and relocates reviewed material and adds the explicitly shown literature entries.
"""
from pathlib import Path
import hashlib
R=Path(__file__).resolve().parents[2];D=R/'revisions/or-r7-20260921';S=D/'sections';S.mkdir(exist_ok=True);old=R/'revisions/or-r6-20260921/sections'
EXPECTED={
'model_structure.tex':'f85cd1706f7bc15ca2a569fab7f8f25acb4f162b',
'accepted.tex':'aab22834bd36aef15dd40a5e4b982a192d4fd83e',
'extensions.tex':'65febbcae2fb44b6f498e85884bf9a0bf8ad7e59',
'study.tex':'c1784c2f07f0cf67f98a8586cd9d696b15e4930c',
'references.tex':'0b78af79c2a41f90413130204393d75bdb24384d'}
for name,expected in EXPECTED.items():
 b=(old/name).read_bytes();actual=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
 if actual!=expected:raise RuntimeError(f'Historical source differs from reviewed input: {name}')
# Preserve entire former sections, split only at a documented subsection boundary.
s=(old/'model_structure.tex').read_text(); marker=r'\subsection{Constructive smooth neural critics}'
a,b=s.split(marker,1)
a=a.replace(r'\section{Structure, exact reduction, and approximation}',r'\section{Structure of the provider relaxation}')
a=a.replace(r'\subsection{Exact representation and comparator classes}',r'\subsection{Exact representation and comparator classes}')
# Explicit recurring scope, without changing the existing theorem equations.
a=a.replace(r'\section{Structure of the provider relaxation}',r'\section{Structure of the provider relaxation}')
a=a.replace(r'\label{sec:structure}',r'\label{sec:structure}'+'\nThroughout this section, $V=V^{\\rm rel}$ denotes the provider relaxation. Accepted values are denoted $W^{\\rm acc}$ or $V^{\\rm acc}$; a relaxation property is not transferred to an accepted optimizer without checking its constraints.\n')
(S/'model_structure.tex').write_text(a)
(S/'constructive_critics.tex').write_text(r'\section{Retained constructive smooth neural critics}'+'\n'+b)
(S/'extensions.tex').write_text((old/'extensions.tex').read_text())
s=(old/'accepted.tex').read_text().replace('For deterministic $q_0$, the value of', 'For deterministic $q_0$ and deterministic protocols, the value of')
s=s.replace('The equality in the proposition concerns', 'Public randomized accepted classes are treated separately in Proposition~\\ref{prop:accepted-jensen}; the unconstrained mixture argument above is not sufficient for them. The equality in the proposition concerns')
s=s.replace('Checking all such candidates and the endpoints $0,1$ is exhaustive, including ties and nonconcavity across intervals.', 'Checking all such candidates and the endpoints $0,1$ is exhaustive, including ties and nonconcavity across intervals. One may instead first construct each stock upper envelope and enumerate only its surviving breakpoints; intersections never attaining that envelope are unnecessary. Both procedures return the same exhaustive candidate set of active intervals.')
(S/'accepted.tex').write_text(s)
s=(old/'study.tex').read_text().replace(r'\label{sec:study}',r'\label{ec:r6-study}').replace(r'\section{Computational study}',r'\section{Retained R6 computational study}')
(S/'legacy_study.tex').write_text(s)
for p in [S/'retained_ec_front.tex']:
 s=p.read_text().replace(r'\ref{sec:accounting}',r'\ref{sec:physical}').replace('Proposition~2.1 of the main paper',r'Proposition~\ref{prop:expanded} of the main paper');p.write_text(s)
refs=(old/'references.tex').read_text()
add=r'''
\bibitem[Defferrard et~al.(2016)]{Defferrard2016}
Defferrard M, Bresson X, Vandergheynst P (2016) Convolutional neural networks on graphs with fast localized spectral filtering. \emph{Advances in Neural Information Processing Systems} 29.
\bibitem[Henig et~al.(1997)]{Henig1997}
Henig M, Gerchak Y, Ernst R, Pyke DF (1997) An inventory model embedded in designing a supply contract. \emph{Management Science} 43(2):184--189. doi:10.1287/mnsc.43.2.184.
\bibitem[Nasser and Turcic(2019)]{NasserTurcic2019}
Nasser S, Turcic D (2019) Temporary contract adjustment to a retailer with a private demand forecast. \emph{Management Science} 65(1):209--229. doi:10.1287/mnsc.2017.2942.
'''
refs=refs.replace(r'\end{thebibliography}',add+'\n'+r'\end{thebibliography}')
# Alphabetize complete bibitems without editing their scholarly content.
import re
parts=re.split(r'(?=\\bibitem)',refs);start=parts[0];entries=parts[1:];tail=''
if entries:
 entries[-1],tail=entries[-1].split(r'\end{thebibliography}',1)
 entries.sort(key=lambda x:re.search(r'\\bibitem\[([^]]+)',x).group(1).lower())
 refs=start+''.join(entries)+r'\end{thebibliography}'+tail
(S/'references.tex').write_text(refs)

print("Prepared the preserved R6 portions of the R7 manuscript.")
