"""Assemble current readers; archive every replaced entry point first."""
from pathlib import Path
import shutil,json,hashlib
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1];REL=R.relative_to(ROOT).as_posix()
TITLE='Finite-Catalog Renewal Design by Selected-Boundary Resource Paths'
ABSTRACT='A renewal provider chooses a limited menu of terminal commands and allocates an accepted obligation across heterogeneous histories. We give an exact selected-boundary decomposition for finite catalogs with opening charges, individual expected caps, realization ceilings, and convex intermediate-service costs. Each adjacent selected pair owns a terminal-reward increment and the service costs of the histories whose eligibility ends there. The resulting resource path has enough capacity to restore the original obligation after rounding. With rational quadratic primitives, this identity yields a polynomial additive approximation scheme whose degree does not depend on the number of catalog-eligibility classes. The scheme retains the original command budget and admits independently checked rational global intervals. Exact polynomial common-prefix optimization remains available as a stronger special case. We establish catalog-insertion and threshold-stability results and extend the capacity-repair argument to compatible production modules. A fixed synthetic study tests strict interior prefixes through 1,024 histories, controlled eligibility splits, unused splitting commands, difficult historical models, certificate costs, and direct mixed-integer comparisons. Numerical optimization is faster on the small comparison models; the contribution is the structural reduction and its original-obligation certification guarantee.'
PREAMBLE=r'''\documentclass[11pt,letterpaper]{article}
\usepackage[margin=1in]{geometry}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amsthm,booktabs,array,longtable}
\usepackage{newtxtext,newtxmath}
\usepackage[round,authoryear]{natbib}
\usepackage{setspace,xr-hyper,xurl}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\onehalfspacing\setlength{\emergencystretch}{2em}
\newtheorem{theorem}{Theorem}[section]
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{corollary}[theorem]{Corollary}
\theoremstyle{definition}\newtheorem{remark}[theorem]{Remark}
\newcommand{\R}{\mathbb R}\newcommand{\E}{\mathbb E}
\newcommand{\argmax}{\operatorname*{arg\,max}}
\newcommand{\argmin}{\operatorname*{arg\,min}}
\pagestyle{fancy}\fancyhf{}\fancyhead[L]{\small Selected-Boundary Resource Paths}
\fancyhead[R]{\small Anonymous}\fancyfoot[C]{\thepage}\setlength{\headheight}{14pt}
'''
ENTRY=['main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','README.md','NDU_OR_submission_checklist.md']
def input_(name):return r'\input{'+REL+'/'+name+'}\n'
def run():
    archive=R/'predecessor';archive.mkdir(exist_ok=True)
    for name in ENTRY:
        src=ROOT/name;dst=archive/name
        if src.exists() and not dst.exists():shutil.copy2(src,dst)
    title=r'''\begin{document}\hypersetup{pageanchor=false}
\begin{titlepage}\centering
{\Large\bfseries '''+TITLE+r'''\par}
\vspace{0.25in}Anonymous manuscript for Operations Research\par\vspace{0.20in}
\begin{minipage}{\textwidth}\textbf{Abstract.} '''+ABSTRACT+r'''
\par\vspace{0.15in}\textbf{Keywords:} renewal contracts; dynamic programming; global optimization.
\par\vspace{0.10in}\textbf{Subject classifications:} Dynamic programming: finite command design; Programming: global optimization.
\par\vspace{0.10in}\textbf{Area of review:} Optimization.
\end{minipage}\vfill September 25, 2026\end{titlepage}
\hypersetup{pageanchor=true}
'''
    s=PREAMBLE+input_('generated/metrics.tex')+r'\hypersetup{pdftitle={'+TITLE+r'},pdfauthor={Anonymous}}'+'\n'+title
    for n in ['introduction','model','selected_boundaries','algorithm','common_and_robustness','production','study','conclusion']:s+=input_(n+'.tex')
    s+=r'\clearpage\phantomsection\label{refs-start}'+'\n'+input_('references.tex')+r'\label{refs-end}\clearpage'+'\n'+input_('generated/main_tables.tex')+r'\clearpage\end{document}'+'\n'
    (ROOT/'main.tex').write_text(s)
    ec=PREAMBLE+r'\externaldocument{.build/r52/main}[main.pdf]'+'\n'+input_('generated/metrics.tex')+r'''\renewcommand{\thesection}{EC.\arabic{section}}
\renewcommand{\thetable}{EC.\arabic{table}}
\begin{document}
\begin{center}{\Large\bfseries Electronic Companion}\par\vspace{6pt}
'''+TITLE+r'''\par Anonymous\end{center}
'''+input_('companion_body.tex')+r'\clearpage'+input_('references.tex')+r'\clearpage'+input_('generated/ec_tables.tex')+r'\clearpage\end{document}'+'\n'
    (ROOT/'electronic_companion.tex').write_text(ec)
    response=PREAMBLE+r'\externaldocument{.build/r52/main}[../../main.pdf]'+'\n'+input_('generated/metrics.tex')+r'\begin{document}'+'\n'+input_('response_body.tex')+r'\end{document}'+'\n'
    (R/'RESPONSE_TO_REFEREES.tex').write_text(response)
    (R/'ABSTRACT.txt').write_text(ABSTRACT+'\n')
    readme=f'''# NDU — Operations Research R52

## Current manuscript

**{TITLE}**

Branch: `revision/ndu-operations-research-r52-resource-path-20260925`.
Scientific source: R49 `2098592a99e47d36cc9fd16311f21d1858fa6e1e`.
Parent and latest report: `4f0b662bd4184fc77fb57bd09c339bffb6213a69`.
The first independent R49 report is also addressed. R50 and R51 contained no later scientific manuscript at inspection; neither is overwritten.

Read `main.pdf`, `electronic_companion.pdf`, and `{REL}/RESPONSE_TO_REFEREES.pdf`.
The revision directory contains all readable source, code, frozen protocol, execution records, independent certificates, preservation manifest, and the code-and-data reproduction archive.

## Structural advance

The exact selected-boundary identity converts arbitrary-eligibility finite-catalog joint design into a scalar-resource path. A capacity identity permits recovery at the original promise and command budget. Rational quadratic primitives admit an additive scheme polynomial in histories, catalog size, budget, binary input length, and inverse normalized accuracy, with no eligibility-dependent exponent. Exact common-prefix optimization remains a stronger special case. The article gives full proofs, catalog and threshold robustness, and a separate compatible-production model.

This is not an exact unrestricted polynomial algorithm, a relative-error scheme, a hardness classification, or a universal solver-speed claim. All operational inputs are synthetic. Numerical mixed-integer optimization and enumeration are faster on the small comparison models.

## Reproduce

```bash
R={REL}
python "$R/code/tests.py"
python "$R/code/study.py" --phase all
python "$R/code/readers.py"
python "$R/code/build.py"
python "$R/code/preservation.py"
```

Python must run without `-O`, because independent checkers reject invalid witnesses with assertions. A single new certificate can be checked offline using `python "$R/code/check_resource.py" path/to/certificate.json.gz`. The study imports unchanged historical allocation modules; the reproduction archive includes those files at their original paths. Numerical comparisons use SciPy 1.17.0. Publication uses Python 3.13.5 and PyMuPDF 1.26.7; actual versions are recorded.

The protocol was committed before the full study and discloses development pilots. Completed cases resume only with the unchanged protocol hash. For fresh timings use a separate checkout and remove only its generated R52 `results/` directory; never overwrite committed evidence. Local execution is separately preserved in `LOCAL_EXECUTION.json`; journal tables use `results/` from the publication environment.

## Evidence and preservation

All 44 prescribed cases, 42 subdivision comparisons, and 12 numerical envelope solves are retained. The study verifies 80 exact certificates; the six difficult models meet tolerance 0.001. Positive-width certificates are not called exact solutions. The controlled two-class case returns a policy below its exhaustive optimum; its interval is valid. All 24 historical stress requests, including ten unresolved requests, remain unchanged.

Every inherited source and result is preserved. Replaced root reader entry points have exact predecessor copies. `PRESERVATION_MANIFEST.json` checks all inherited Git blobs; `CONTENT_MAP.json` identifies the preserved proof locations. Main and review branches, and all earlier revision branches, are unchanged. `BUILD_VALIDATION.json` gives measured page counts, mathematical labels, PDF hashes, abstract length, and typesetting diagnostics; a successful build is not an editorial acceptance claim.
'''
    (ROOT/'README.md').write_text(readme);(R/'README.md').write_text(readme)
    (ROOT/'NDU_OR_submission_checklist.md').write_text('''# R52 submission preparation

Current reader entry points are main.pdf, electronic_companion.pdf, and the R52 response.

The measured page counts and length category are in R52 BUILD_VALIDATION.json. The source uses 11-point text, one-and-a-half spacing, one-inch margins, a text-only abstract below 200 words, a notation-free introduction, alphabetical author-year references, tables after references, and a code/data statement after the main body. The electronic companion does not exceed the article length. No author identity is inserted.

This repository revision is not a submission to ScholarOne. The author must separately verify authorship, actual conflicts of interest, funding, prior-submission identifiers, overlapping manuscripts, and exclusive-submission eligibility. No unsupported declarations about those matters have been made.

All code and data are synthetic and included. Historical results remain under their original assumptions in the preservation map. Format checks do not establish editorial suitability.
''')
if __name__=='__main__':run()
