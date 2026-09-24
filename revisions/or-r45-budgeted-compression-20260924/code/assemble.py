"""Assemble R45 readers without altering any inherited scientific source."""
from pathlib import Path
import re,json,hashlib,shutil,subprocess
R=Path(__file__).resolve().parents[1]; ROOT=R.parents[1]
BASE='91583abe77208ec4ed25b5fbc5a15f89d54fcd6f'
BRANCH='revision/ndu-operations-research-r45-budgeted-compression-20260924'
TITLE='Limited-Memory Renewal Contracts: Budgeted Compression and Certified Joint Design'
RP=R.relative_to(ROOT).as_posix()
OLDMAIN=['revisions/or-r43-prefix-decomposition-20260924/decomposition.tex',
         'revisions/or-r39-robust-quantizer-20260924/derived/global.tex',
         'revisions/or-r39-robust-quantizer-20260924/derived/monge.tex',
         'revisions/or-r43-prefix-decomposition-20260924/grid_certificate.tex']
OLDEC=[
 'revisions/or-r42-certified-joint-design-20260924/institution.tex',
 'revisions/or-r39-robust-quantizer-20260924/derived/deterministic.tex',
 'revisions/or-r39-robust-quantizer-20260924/derived/lotteries.tex',
 'revisions/or-r42-certified-joint-design-20260924/promise_robustness.tex',
 'revisions/or-r39-robust-quantizer-20260924/derived/core_proofs.tex',
 'revisions/or-r39-robust-quantizer-20260924/derived/mechanism.tex',
 'revisions/or-r37-integrated-frontier-20260924/bounded_overrun.tex',
 'revisions/or-r39-robust-quantizer-20260924/allocation_companion.tex',
 'revisions/or-r43-prefix-decomposition-20260924/monotone_charge.tex',
 'revisions/or-r42-certified-joint-design-20260924/catalog_design.tex',
 'revisions/or-r44-resource-augmentation-20260924/augmentation.tex',
 'revisions/or-r44-resource-augmentation-20260924/augmentation_companion.tex',
 'revisions/or-r39-robust-quantizer-20260924/resources.tex']
ABSTRACT='''A renewal provider must select a limited execution alphabet and allocate an accepted obligation under participation caps, realization ceilings, and level-opening charges. We derive an exact target-crossing dynamic program that computes the entire memory--charge frontier conditional on branch targets. At saturation it solves joint catalog design in polynomial time with variable branch count and symbol budget. At an interior promise, a feasible weighted target net gives any prescribed additive accuracy at the original symbol budget when the branch count is fixed; its accuracy exponent is explicit. Local distortion certificates, charge-aware compression of price supports, and an inexact-oracle repair theorem provide complementary feasible policies without assuming zero duality gap. Exact continuous quadratic design and saturated Monge results are retained. Independent support enumeration and a separate uneliminated mixed-integer formulation validate the computation. Across thirty-six synthetic comparisons, the core target portfolio attains thirty-five original-budget optima; a retained charged counterexample motivates an explicit greedy safeguard. Heterogeneous scaling and adaptive-catalog experiments distinguish conditional performance from global guarantees. The resulting theory addresses limited-memory design without making additional symbols a prerequisite for approximation.'''


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot():
    (R/'predecessor').mkdir(exist_ok=True)
    for name in ['main.tex','electronic_companion.tex','main.pdf','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md']:
        dest=R/'predecessor'/name
        if (ROOT/'.git').exists():
            raw=subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT)
            if dest.exists(): assert dest.read_bytes()==raw
            else:dest.write_bytes(raw)
        elif not dest.exists(): shutil.copy2(ROOT/name,dest)
    # Old cross-reference numbers are for explicit archival table pointers only.
    for name in ['r44-main-labels.aux','r44-ec-labels.aux']:
        if (ROOT/name).exists() and not (R/'predecessor'/name).exists():shutil.copy2(ROOT/name,R/'predecessor'/name)


def preamble(ec=False):
    s=(R/'predecessor'/'main.tex').read_text().split('\\begin{document}')[0]
    s=s.replace('r44-ec-labels','r45-ec-labels').replace('Exact Quadratic Design and Resource Augmentation','Budgeted Compression and Certified Joint Design')
    if ec:
        s=s.replace(r'\externaldocument{r45-ec-labels}[electronic_companion.pdf]',r'\externaldocument{r45-main-labels}[main.pdf]')
        s+=r'''\renewcommand{\thesection}{EC.\arabic{section}}
\renewcommand{\theequation}{EC.\arabic{equation}}
\renewcommand{\thetable}{EC.\arabic{table}}
'''
    return s


def copy_source(path):
    dest=R/'derived'/path.replace('/','__')
    dest.write_text((ROOT/path).read_text())
    return dest.relative_to(ROOT).as_posix()

def input_(path): return '\\input{'+path+'}\n'

def expand(path,stack=()):
    if path in stack:raise RuntimeError('Recursive input '+path)
    text=(ROOT/path).read_text()
    def replace(m):
        p=m.group(1);p=p if p.endswith('.tex') else p+'.tex'
        return expand(p,stack+(path,))
    return re.sub(r'\\input\{([^}]+)\}',replace,text)


def run():
    snapshot();(R/'derived').mkdir(exist_ok=True);(R/'generated').mkdir(exist_ok=True)
    (R/'ABSTRACT.txt').write_text(ABSTRACT+'\n'); assert len(ABSTRACT.split())<=200
    newmodel=r'''\section{Model and Canonical Allocation}\label{sec:joint}
A public branch $j$ is observed with probability $\pi_j>0$, with $\sum_j\pi_j=1$. It has a continuation cap $b_j\in(0,1)$ and a convex nondecreasing intermediate-service cost $h_j$, with $h_j(0)=0$. The common terminal reward $f$ is strictly increasing and concave on $[0,1]$. Caps may repeat; write $\bar b=\sum_j\pi_jb_j$. An encoder selects a terminal command from one installed alphabet, and only its symbol reaches the common terminal gateway. The gateway cannot recover the observed branch, an inherited intermediate tier, or an uncharged shared random seed. Thus $m$ distinct commands require $\lceil\log_2m\rceil$ writable bits; read-only program constants and public-state storage are separate resources. The full institutional mechanism and saturated benchmarks are retained in the companion.

The provider selects a pre-draw tier $y_j$ and a lottery $C_j$ on the installed book, with operating payoff $\E f(C_j)-h_j(y_j)$. The accepted root obligation is $B\in[0,\bar b]$. Expected participation restricts the mean obligation, while a realization ceiling restricts every positive-probability draw. With a common risk tolerance $\delta\geq0$,
'''
    joint=(ROOT/'revisions/or-r43-prefix-decomposition-20260924/joint_design.tex').read_text()
    cut=joint.index('\\subsection{A finite exact reduction')
    start=joint.index('\\begin{equation}\\label{eq:unified-feasible}')
    model=newmodel+joint[start:cut]
    model+=r'''
All canonical arguments continue to hold for branch-specific ceilings $\tau_j\geq b_j$ in place of $b_j+\delta$: the eligibility prefix is then $c\cap[0,\tau_j]$. We write $\mathcal V_{m,\mathcal A}^{\tau}(B;\rho)$ for this generalized catalog value. The new budgeted algorithms and numerical formulation use these heterogeneous ceilings. The retained continuous and institutional results use their stated common-$\delta$ specialization.
'''
    (R/'model.tex').write_text(model)
    tail=joint[cut:].replace('\\subsection{A finite exact reduction of the continuous outer problem}',r'\section{Exact Continuous Quadratic Design}\label{app:r45-continuous}',1)
    tail=tail.replace('Section~\\ref{sec:joint-study} compares their exact values along an entire declared parameter path.', 'The complete predecessor companion retains the earlier exact institutional comparison path; the current study reports the separately executed budgeted-design comparisons.')
    (R/'continuous_appendix.tex').write_text(tail)
    mapping={p:copy_source(p) for p in OLDMAIN+OLDEC}
    main=preamble()+r'''\begin{document}\hypersetup{pageanchor=false}
\begin{titlepage}\centering
{\Large\bfseries Limited-Memory Renewal Contracts:\newline Budgeted Compression and Certified Joint Design\par}
\vspace{.3in}Anonymous manuscript for Operations Research\par\vspace{.2in}
\begin{minipage}{\textwidth}\textbf{Abstract.} '''+ABSTRACT+r'''
\par\vspace{.15in}\textbf{Keywords:} renewal contracts; quantization; dynamic programming.
\par\vspace{.1in}\textbf{Subject classifications:} Dynamic programming: service design; Programming: resource allocation.
\par\vspace{.1in}\textbf{Area of review:} Optimization.
\par\vspace{.1in}\textbf{Submission category:} Lengthy manuscript.
\end{minipage}\vfill September 24, 2026\end{titlepage}
\hypersetup{pageanchor=true}
'''
    for p in ['introduction','model','compression','target_net','certificates']:main+=input_(RP+'/'+p+'.tex')
    main+=input_(mapping[OLDMAIN[0]])
    for p in ['support','study','conclusion']:main+=input_(RP+'/'+p+'.tex')
    main+='\\appendix\n'+input_(RP+'/continuous_appendix.tex')
    for p in OLDMAIN[1:]:
        main+=input_(mapping[p])
        if p.endswith('/global.tex'): main+=input_('revisions/or-r39-robust-quantizer-20260924/figure.tex')
    main+='\\clearpage\\phantomsection\\label{refs-start}\n'+input_(RP+'/generated/references.tex')+'\\label{refs-end}\n\\clearpage\n'+input_(RP+'/generated/main_tables.tex')+'\\end{document}\n'
    ec=preamble(True)+r'''\begin{document}
\begin{center}{\Large\bfseries Electronic Companion}\par
Limited-Memory Renewal Contracts: Budgeted Compression and Certified Joint Design\end{center}
This companion supplies retained institutional and mathematical results together with the new independent optimization formulation and execution protocol. Cross-references to the article refer to the current revision. Historical numerical tables are explicitly identified as archival, not newly executed evidence.
'''
    for p in OLDEC:ec+=input_(mapping[p])
    ec+=input_(RP+'/protocol.tex')+'\\clearpage\n'+input_(RP+'/generated/references.tex')+'\\clearpage\n'+input_(RP+'/generated/companion_tables.tex')+input_('revisions/or-r39-robust-quantizer-20260924/derived/accounting_table.tex')+'\\end{document}\n'
    (ROOT/'main.tex').write_text(main);(ROOT/'electronic_companion.tex').write_text(ec)
    refs=(ROOT/'revisions/or-r44-resource-augmentation-20260924/generated/references.tex').read_text()
    newref=r'''\bibitem[Nielsen and Nock(2014)]{NielsenNock2014}
Nielsen F, Nock R (2014) Optimal interval clustering: Application to Bregman clustering and statistical mixture learning. Author manuscript, arXiv:1403.2485.

'''
    refs=refs.replace(r'\bibitem[Pag\`es',newref+r'\bibitem[Pag\`es')
    (R/'generated/references.tex').write_text(refs)
    oldpaths=set()
    for name in ['main.tex','electronic_companion.tex']:
        oldpaths.update(re.findall(r'\\input\{([^}]+)\}',(R/'predecessor'/name).read_text()))
    content={p:dict(original_sha256=sha(ROOT/p),location=('current article' if p in OLDMAIN else 'current companion') if p in mapping else
        ('current article, canonical model and continuous appendix' if p.endswith('/joint_design.tex') else 'complete preserved R44 reader and immutable source'),
        derived_path=mapping.get(p)) for p in sorted(oldpaths)}
    (R/'CONTENT_MAP.json').write_text(json.dumps(dict(base=BASE,paths=content),indent=2)+'\n')
    return mapping

if __name__=='__main__':run()
