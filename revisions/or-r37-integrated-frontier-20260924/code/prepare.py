"""Prepare current readers from preserved sources and executed evidence.

Only root reader wrappers/documentation and the new R37 directory are changed.
Original theorem modules and evidence are not edited. Historical cross-
references use H-prefixed numbers and link to exact predecessor PDFs.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
from reporting import generate

R = Path(__file__).resolve().parents[1]
ROOT = R.parents[1]
REL = str(R.relative_to(ROOT))
BASE = 'f26f4da71207a7613735b0504bc34dbe231813c1'
BRANCH = 'revision/ndu-operations-research-r37-integrated-frontier-20260924'
TITLE = 'Service Contracts with Limited Memory: Participation, Randomization, and Exact Design'
TITLE_TEX = 'Service Contracts with Limited Memory:\\newline Participation, Randomization, and Exact Design'
ABSTRACT = ('Service agreements can reach the same operating state with different accepted obligations, while the execution system retains only a small service code. We solve the resulting memory-design problem under two participation institutions. Approval before a private draw permits lotteries that reduce the loss from a restricted code budget; realization-by-realization approval eliminates that advantage at every budget. For heterogeneous quadratic renewal contracts, the globally optimal lottery codebook has cap-anchored levels except for a continuously optimized highest level. An exact example shows why discretizing that level at the caps fails. We prove that the optimized terminal costs retain a Monge inequality and identify the resulting matrices with the classical easy-direction staircase-search setting. On ordered rational inputs, standard SMAWK then computes every requested budget frontier with linear rational work per layer, including codebook reconstruction. A resource-pricing formulation separates writable bits, read-only representation, evaluation work, and compilation. A bounded-overrun mechanism makes the institutional tradeoff explicit. Exact checks, independent matrix-search substitution, finite-network solver comparisons, and scale and memory measurements assess the implementations. The broader compact-response and exact-memory theory is retained in the electronic companion and preservation archive.')
P31 = 'revisions/or-r31-tightness-minimal-machine-20260923/'
P33 = 'revisions/or-r33-piecewise-randomized-20260923/'
P34 = 'revisions/or-r34-global-randomized-frontier-20260923/'
P35 = 'revisions/or-r35-monge-frontier-20260923/'
P36 = 'revisions/or-r36-linear-frontier-20260924/'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source(path):
    return (ROOT/path).read_text()


def git_bytes(path):
    return subprocess.check_output(['git', 'show', BASE+':'+path], cwd=ROOT)


def write(path, content):
    p = ROOT/path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)


def normalize():
    p = R/'positioning.tex'
    p.write_text(p.read_text().replace('{Aggarwal1987}', '{AggarwalEtAl1987}'))
    p = R/'extra_references.tex'
    p.write_text(p.read_text().replace('[Eppstein(2015)]', '[Eppstein(2005)]')
                 .replace('Eppstein D (2015)', 'Eppstein D (2005)'))
    p = R/'bounded_overrun.tex'
    p.write_text(p.read_text().replace('is off-cap for $0<\\delta<1/4$ once it reaches its unconstrained optimum $5/8$',
                                      'is off-cap for every $\\delta>0$'))


def snapshot_engines():
    result = {}
    for folder, filename in [('or-r34-global-randomized-frontier-20260923', 'randomized_frontier.py'),
                             ('or-r35-monge-frontier-20260923', 'monge_frontier.py'),
                             ('or-r36-linear-frontier-20260924', 'linear_frontier.py')]:
        p = ROOT/'revisions'/folder/filename
        target = R/'code/snapshots'/folder/filename
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
        result[str(target.relative_to(R))] = {'source': str(p.relative_to(ROOT)), 'sha256': digest(p)}
    (R/'code/ENGINE_PROVENANCE.json').write_text(json.dumps(result, indent=2)+'\n')


def preamble(which):
    old = git_bytes('main.tex').decode().split(r'\begin{document}', 1)[0]
    old = re.sub(r'\\externaldocument[^\n]*\n', '', old)
    old = re.sub(r'\\hypersetup[^\n]*\n', '', old)
    old = old.replace('Accepted Service Adaptation', 'Service Contracts with Limited Memory')
    old += ('\\externaldocument{r37-'+('ec' if which == 'main' else 'main')+'-labels}['
            +('electronic_companion.pdf' if which == 'main' else 'main.pdf')+']\n')
    old += '\\externaldocument{r37-history-main-labels}['+REL+'/predecessor/main.pdf]\n'
    old += '\\externaldocument{r37-history-ec-labels}['+REL+'/predecessor/electronic_companion.pdf]\n'
    old += '\\hypersetup{pdftitle={'+('Electronic Companion: ' if which == 'ec' else '')+TITLE+'},pdfauthor={Anonymous}}\n'
    if which == 'ec':
        old += r'\renewcommand{\thesection}{EC.\arabic{section}}'+'\n'
        old += r'\renewcommand{\theequation}{EC.\arabic{equation}}'+'\n'
        old += r'\renewcommand{\thetable}{EC.\arabic{table}}'+'\n'
    return old


def inputs(paths):
    return '\n'.join('\\input{'+p+'}' for p in paths)+'\n'


def expand(text, seen=None):
    seen = set() if seen is None else seen
    def insert(m):
        path = m.group(1)
        if path in seen:
            return ''
        seen.add(path)
        return expand(source(path), seen)
    return re.sub(r'\\input\{([^}]+)\}', insert, text)


def bibliography(paths, destination):
    pool = {}
    for path in [P36+'references.tex', REL+'/extra_references.tex']:
        for m in re.finditer(r'(\\bibitem\[[^\]]*\]\{([^}]+)\}.*?)(?=\\bibitem|\\end\{thebibliography\}|\Z)', source(path), re.S):
            pool[m.group(2)] = m.group(1).strip()
    citations = set()
    for path in paths:
        for m in re.finditer(r'\\cite\w*(?:\[[^\]]*\])*\{([^}]+)\}', expand(source(path))):
            citations.update(m.group(1).split(','))
    missing = citations-set(pool)
    if missing:
        raise ValueError('Unresolved bibliography entries: '+str(missing))
    write(destination, '\\begin{thebibliography}{99}\\raggedright\n'
          +'\n\n'.join(pool[k] for k in sorted(citations, key=str.lower))
          +'\n\\end{thebibliography}\n')


def response_reader():
    mapping = {'&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_',
               '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}',
               '\\': r'\textbackslash{}'}
    def esc(text):
        return ''.join(mapping.get(c, c) for c in text)
    def inline(text):
        parts = re.split(r'(`[^`]+`|\*\*[^*]+\*\*)', text)
        out = []
        for part in parts:
            if part.startswith('`') and part.endswith('`'):
                value = ''.join(esc(c)+(r'\allowbreak{}' if c in '/-_.:' else '') for c in part[1:-1])
                out.append(r'\texttt{'+value+'}')
            elif part.startswith('**') and part.endswith('**'):
                out.append(r'\textbf{'+esc(part[2:-2])+'}')
            else:
                out.append(esc(part))
        return ''.join(out)
    body = []
    for block in (R/'RESPONSE_TO_REFEREES.md').read_text().split('\n\n'):
        block = block.strip()
        if not block:
            continue
        if block.startswith('# '):
            body.append('\\begin{center}{\\Large\\bfseries '+inline(block[2:])+'}\\par\\medskip Anonymous revision R37, September 24, 2026\\end{center}')
        elif block.startswith('## '):
            body.append('\\section*{'+inline(block[3:])+'}')
        else:
            body.append(inline(block.replace('\n', ' ')))
    pre = preamble('main')
    pre = re.sub(r'\\externaldocument[^\n]*\n', '', pre)
    pre = pre.replace('pdftitle={'+TITLE+'}', 'pdftitle={R37 Response to Referees}')
    text = pre+'\\begin{document}\n'+'\n\n'.join(body)+'\n'
    text += '\\input{'+REL+'/generated/response_results.tex}\n\\end{document}\n'
    (R/'RESPONSE_TO_REFEREES.tex').write_text(text)


def prepare():
    normalize()
    snapshot_engines()
    generate()
    archive = R/'predecessor'
    archive.mkdir(exist_ok=True)
    archived = {}
    for name in ('main.tex', 'electronic_companion.tex', 'main.pdf', 'electronic_companion.pdf', 'README.md', 'NDU_OR_submission_checklist.md'):
        (archive/name).write_bytes(git_bytes(name))
        archived[name] = digest(archive/name)
    (archive/'README_ARCHIVE.md').write_text('Exact R36 readers and wrappers from review base '+BASE+'.\nThese are historical evidence, not current submission readers.\n')
    d = REL+'/derived/'
    provenance = {}
    def derived(name, original, text, selection):
        write(d+name, text)
        provenance[d+name] = {'source': original, 'source_sha256': digest(ROOT/original), 'selection': selection}
    memory = source(P31+'memory_theory.tex')
    start = memory.index(r'\subsection{Ordered memory frontiers beyond equal branch probabilities}')
    end = memory.index(r'\subsection{Mean-preserving radial spreads of outside options}')
    derived('minimal_memory.tex', P31+'memory_theory.tex', memory[:start], 'Complete general observation/minimal-machine portion, before ordered frontier.')
    derived('deterministic.tex', P31+'memory_theory.tex', memory[start:end].replace(r'\subsection{Ordered memory frontiers beyond equal branch probabilities}', r'\section{The Deterministic Service-Code Frontier}'), 'Complete ordered-frontier portion; heading promoted to section only.')
    derived('dispersion.tex', P31+'memory_theory.tex', memory[end:].replace(r'\subsection{Mean-preserving radial spreads of outside options}', r'\section{Mean-Preserving Radial Spreads of Outside Options}'), 'Complete radial-spread portion; heading promoted only.')
    support = source(P31+'companion_content.tex')
    sections = re.split(r'(?=\\section\{)', support)
    kept = [s for s in sections if not s.startswith(r'\section{Reading Guide') and not s.startswith(r'\section{Comparison Algorithms')]
    derived('supporting_proofs.tex', P31+'companion_content.tex', ''.join(kept), 'All mathematical supporting sections; older reading guide and experiment description remain in exact predecessor companion.')
    accounting = source(P33+'r32_accounting_text.tex').replace(r'\subsection{Referee-facing priority and complexity closure}', r'\section{Read-Only, Combined-State, and Writable Accounting}')
    derived('representation_accounting.tex', P33+'r32_accounting_text.tex', accounting, 'Complete accounting proposition and proof; heading renamed only.')
    oracle = source(P34+'companion_addendum.tex').split(r'\subsection{Independent checks and their logical scope}')[0]
    oracle = oracle.replace(r'\subsection{Rational implementation concordance}', r'\subsection{Rational implementation concordance}'+'\nThis subsection documents the retained quadratic enumeration engine. The current linear engine uses the same rational primitives but reconstructs only the winning codebook once per budget.\n')
    derived('oracle_concordance.tex', P34+'companion_addendum.tex', oracle, 'Complete rational implementation and general-convex-tail extension; historical experiment narrative archived.')
    alternative = source(P35+'companion_addendum.tex').split(r'\subsection{Search, storage, and exact arithmetic}', 1)[1].split(r'\subsection{Evidence and independence}', 1)[0]
    derived('divide_conquer.tex', P35+'companion_addendum.tex', r'\section{The Retained Divide-and-Conquer Alternative}'+'\n'+alternative, 'Complete search/storage/arithmetic argument; cost inequalities strengthened in current main; historical evidence archived.')
    guide = (r'\section*{Reading this companion}'+'\nThe main article is organized around restricted-memory renewal design. This companion retains the broader compact-response, tight-size, piecewise-quadratic, behavioral-minimization, dispersion, and shared-table theory with its original hypotheses. It also gives the bounded-overrun proofs and current computational methods. No implication is transferred from the scalar no-switching architecture to the older general switching or coupled-commitment model without its stated assumptions.\n\n'
             +'References whose numbers begin with H point to the exact preceding R36 readers in the preservation archive, not to a missing current section. Older experiment narratives, unfavorable findings, and revision concordances remain there and in their unchanged source modules. The current source-preservation map identifies each location; no historical theorem or data file is deleted.\n')
    write(REL+'/companion_guide.tex', guide)
    main_paths = [REL+'/'+n for n in ('introduction.tex', 'positioning.tex', 'institution.tex')]
    main_paths += [d+'deterministic.tex', P33+'randomized_memory.tex', P34+'global_frontier.tex']
    main_paths += [REL+'/'+n for n in ('monge_completion.tex', 'resources.tex', 'evidence.tex', 'conclusion.tex')]
    ec_paths = [REL+'/companion_guide.tex', P31+'model_literature.tex', P31+'quotient_theory.tex', P33+'extensions.tex',
                d+'minimal_memory.tex', d+'dispersion.tex', P31+'shared_comparator.tex', d+'supporting_proofs.tex',
                d+'representation_accounting.tex', d+'oracle_concordance.tex', d+'divide_conquer.tex',
                REL+'/bounded_overrun.tex', REL+'/methodology.tex']
    main_tables = [REL+'/static_tables.tex', REL+'/generated/main_tables.tex']
    ec_tables = [REL+'/generated/companion_tables.tex']
    bibliography(main_paths+main_tables, REL+'/generated/main_references.tex')
    bibliography(ec_paths+ec_tables, REL+'/generated/companion_references.tex')
    main = preamble('main')+r'\begin{document}'+'\n'+r'\hypersetup{pageanchor=false}'+'\n'+r'\begin{titlepage}\centering'+'\n'
    main += '{\\Large\\bfseries '+TITLE_TEX+'\\par}\n\\vspace{.3in}Anonymous manuscript for Operations Research\\par\\vspace{.2in}\n'
    main += '\\begin{minipage}{\\textwidth}\n\\textbf{Abstract.} '+ABSTRACT+'\n'
    main += r'\par\vspace{.15in}\textbf{Keywords:} service contracts; limited memory; Monge optimization.'+'\n'
    main += r'\par\vspace{.1in}\textbf{Subject classifications:} Dynamic programming: service-code design; Programming: exact resource allocation.'+'\n'
    main += r'\par\vspace{.1in}\textbf{Area of review:} Optimization.'+'\n'
    main += r'\end{minipage}\vfill Revision R37, September 24, 2026\end{titlepage}'+'\n'+r'\hypersetup{pageanchor=true}'+'\n'
    main += inputs(main_paths)+r'\clearpage\phantomsection\label{r37-refs-start}'+'\n'
    main += inputs([REL+'/generated/main_references.tex'])+r'\label{r37-refs-end}\clearpage'+'\n'
    main += inputs(main_tables[:1])+r'\clearpage'+'\n'+inputs(main_tables[1:])+r'\end{document}'+'\n'
    write('main.tex', main)
    ec = preamble('ec')+r'\begin{document}'+'\n'+r'\begin{center}{\Large\bfseries Electronic Companion}\par\medskip'+'\n'
    ec += '{\\large '+TITLE_TEX+'}\\par\\medskip Anonymous manuscript for Operations Research\\par Revision R37, September 24, 2026\\end{center}\n'
    ec += inputs(ec_paths)+r'\clearpage'+'\n'+inputs([REL+'/generated/companion_references.tex'])+r'\clearpage'+'\n'
    ec += inputs(ec_tables)+r'\end{document}'+'\n'
    write('electronic_companion.tex', ec)
    defined = set(re.findall(r'\\label\{([^}]+)\}', expand(main)+'\n'+expand(ec)))
    for which in ('main', 'ec'):
        lines = []
        for line in git_bytes('r36-'+which+'-labels.aux').decode().splitlines():
            match = re.match(r'\\newlabel\{([^}]+)\}', line)
            if match and match.group(1) not in defined:
                line = re.sub(r'^(\\newlabel\{[^}]+\}\{\{)', r'\1H.', line)
                lines.append(line)
        write('r37-history-'+which+'-labels.aux', '\n'.join(lines)+'\n')
    response_reader()
    old_inputs = set()
    for filename in ('main.tex', 'electronic_companion.tex'):
        old_inputs.update(re.findall(r'\\input\{([^}]+)\}', (archive/filename).read_text()))
    main_active, ec_active = set(main_paths+main_tables), set(ec_paths+ec_tables)
    preservation = []
    for path in sorted(old_inputs):
        if path in main_active:
            location = 'Current main reader, unchanged full module'
        elif path in ec_active:
            location = 'Current electronic companion, unchanged full module'
        elif any(v['source'] == path for v in provenance.values()):
            location = 'Current faithful excerpts recorded below, plus complete unchanged module and exact predecessor reader'
        else:
            location = 'Complete unchanged source and exact predecessor reader; superseded exposition or historical evidence, not a competing current reader'
        preservation.append({'path': path, 'sha256': digest(ROOT/path), 'location': location})
    manifest = {'base_commit': BASE, 'reviewed_manuscript_commit': '8b17bed9079aa8e3bcaf52e6a5847a60cbf7d7ca',
                'branch': BRANCH, 'archived_predecessor_files': archived,
                'inherited_reader_modules': preservation, 'faithful_excerpt_provenance': provenance,
                'current_main_inputs': main_paths+main_tables, 'current_companion_inputs': ec_paths+ec_tables,
                'policy': 'All base theorem, code, and evidence files are preserved. Root current readers and documentation may change. Historical H-prefixed references link to exact predecessor PDFs.'}
    (R/'PRESERVATION_MAP.json').write_text(json.dumps(manifest, indent=2)+'\n')
    lines = ['# R37 content preservation map', '', 'Base: `'+BASE+'`.', '',
             'Root main.pdf and electronic_companion.pdf are the only current readers. Predecessor readers are exact historical copies. Every original source remains unchanged.', '']
    for item in preservation:
        lines += ['## '+item['path'], item['location']+'.', 'SHA-256: `'+item['sha256']+'`.', '']
    lines += ['## Excerpt provenance', '']
    for path, value in provenance.items():
        lines += ['`'+path+'` from `'+value['source']+'`: '+value['selection'], '']
    (R/'PRESERVATION_MAP.md').write_text('\n'.join(lines))
    (R/'ABSTRACT.txt').write_text(ABSTRACT+'\n')
    print('Prepared readers; abstract words:', len(ABSTRACT.split()), flush=True)


if __name__ == '__main__':
    prepare()
