"""Recover the hash-verified unpublished R38 sources and assemble R39.

The five inherited transport files are read only. Their one documented byte
repair is performed in memory, never written back over a historical file.
Generated source is subsequently committed before readers are compiled.
"""
from pathlib import Path, PurePosixPath
import base64, hashlib, json, re, shutil

R = Path(__file__).resolve().parent
ROOT = R.parents[1]
OLD = ROOT/'revisions/or-r38-contractual-quantization-20260924'
OLDNAME = OLD.name
NEWNAME = R.name
oldbranch = 'revision/ndu-operations-research-r38-contractual-quantization-20260924'
newbranch = 'revision/ndu-operations-research-r39-robust-quantizer-20260924'
parts = sorted((OLD/'_transport').glob('part-*.b64'))
assert len(parts) == 5
texts = [p.read_text().strip() for p in parts]
texts[1] = texts[1].replace('pEdrYQQCA6Z','pEdrYQCA6Z')
encoded = ''.join(texts)
assert len(encoded) == 45060
compressed = base64.b64decode(encoded, validate=True)
assert hashlib.sha256(compressed).hexdigest() == '5d49927ad2608179f31578f4db7209bdb5c554ab04ed4d00195bbcc5e1ee287d'
raw = __import__('zlib').decompress(compressed)
assert hashlib.sha256(raw).hexdigest() == '066b7c85d8c51c7c3666682e10409b86d7d6bdc32d6ab65f59fd9dbb867f7b98'
data = json.loads(raw)
assert len(data) == 17
for name, text in data.items():
    relative = PurePosixPath(name)
    assert not relative.is_absolute() and '..' not in relative.parts
    assert name.startswith(str(OLD.relative_to(ROOT))+'/') and isinstance(text, str)
    original = ROOT/name
    if original.exists():
        assert original.read_text() == text, 'Recovered R38 source differs: '+name
    else:
        original.parent.mkdir(parents=True, exist_ok=True)
        original.write_text(text)
    p = R/original.relative_to(OLD)
    p.parent.mkdir(parents=True, exist_ok=True)
    current = text.replace(oldbranch, newbranch).replace(OLDNAME, NEWNAME)
    current = current.replace('ndu-r38','ndu-r39').replace('r38-main-labels','r39-main-labels').replace('r38-ec-labels','r39-ec-labels')
    current = current.replace('R38', 'R39')
    p.write_text(current)
(R/'R38_RECOVERY.json').write_text(json.dumps({
    'remote_base':'a149cb3e5df35e33e64a148d7d620e019ca2b135',
    'latest_review':'1cf9c8df76437ee71d4291d1001e9c7f055781c5',
    'failed_predecessor_run':35951814408,
    'failure':'generated/references.tex parent directory absent; source/PDF publication skipped',
    'source_bundle_sha256':hashlib.sha256(raw).hexdigest(),
    'recovered_original_files':{p:hashlib.sha256(t.encode()).hexdigest() for p,t in data.items()},
    'historical_transport_files':'read only; normalization performed in memory'
},indent=2)+'\n')
(R/'generated').mkdir(exist_ok=True)
(R/'results').mkdir(exist_ok=True)
# Local artifact builds use the exact already archived R37 predecessor readers.
# Full checkouts instead have build.py obtain these from the pinned Git base.
if not (ROOT/'.git').exists() and (OLD/'predecessor').exists():
    shutil.copytree(OLD/'predecessor',R/'predecessor',dirs_exist_ok=True)

p=R/'introduction.tex'; s=p.read_text()
s=s.replace('$O(KN)$ work','work linear in the number of source points per level')
s=s.replace('$O(k)$ exact-rational oracle/comparison work','linear exact-rational oracle and comparison work')
s=s.replace('same-alphabet scaling and saturation-lift argument', 'same-alphabet contraction and partial-lift argument')
s=s.replace('bounds the change of every finite-budget value uniformly.',
            'bounds the change of every finite-budget value between any two feasible root promises uniformly.')
s=s.replace('rather than treating branch caps as targets after they cease to bind.',
            'rather than treating branch caps as targets after they cease to bind. An exact supporting-price algorithm certifies each fixed-book allocation, including zero intermediate costs and repeated caps.')
assert '$' not in s and '\\[' not in s
p.write_text(s)

p=R/'positioning.tex'; s=p.read_text()
s=s.replace('For $u\\leq b\\leq v$,','For distinct adjacent levels $u<v$ and $u\\leq b\\leq v$,')
s=s.replace('Same-alphabet lifts give uniform bounds for both institutions and an explicit strict nonsaturated advantage.',
            'Same-alphabet transport gives all-promise bounds, exact fixed-book certificates, and a strict nonsaturated advantage.')
table=re.search(r'\\begin\{table\}.*?\\end\{table\}',s,re.S)
assert table
(R/'novelty_table.tex').write_text(table.group(0).replace('[tb]','[p]')+'\n')
s=s[:table.start()]+'Table~\\ref{tab:r37-priority} states the predecessor principle and contractual increment for each result.\n'+s[table.end():]
p.write_text(s)

p=R/'promise_robustness.tex'; s=p.read_text()
a=s.index('\\subsection{A uniform stability theorem')
b=s.index('In the equal-probability three-branch example',a)
s=s[:a]+(R/'pairwise.tex').read_text()+'\n'+s[b:]
s+='\nElectronic Companion Proposition~\\ref{prop:allocation-certificate} gives an exact supporting-price algorithm and a separately checkable certificate for every fixed-book allocation. Exhaustive certified catalog search extends that computation to all promises on small catalogs; its exponential cost is stated explicitly.\n'
p.write_text(s)

p=R/'code/prepare.py'; s=p.read_text()
s=s.replace("D=R/'derived'; D.mkdir(exist_ok=True)","D=R/'derived'; D.mkdir(exist_ok=True)\n(R/'generated').mkdir(parents=True,exist_ok=True)")
s=s.replace('budget-uniform value bounds: every strict saturated institutional advantage persists on an explicit interval of nonsaturated promises.',
            'budget-uniform bounds between every pair of promises, with exact fixed-book allocation certificates. Strict saturated institutional advantages persist on explicit nonsaturated intervals.')
s=s.replace('renewal contracts; quantization; participation; dynamic programming.',
            'renewal contracts; quantization; dynamic programming.')
s=s.replace("inp('generated/references.tex')+'\\\\label{refs-end}\\n\\\\end{document}\\n'",
            "inp('generated/references.tex')+'\\\\label{refs-end}\\n\\\\clearpage\\n'+inp('novelty_table.tex')+'\\\\end{document}\\n'")
s=s.replace("ec+=inp('derived/methodology.tex')+inp('derived/legacy_evidence.tex')",
            "ec+=inp('allocation_companion.tex')+inp('generated/allocation_evidence.tex')+inp('derived/methodology.tex')+inp('derived/legacy_evidence.tex')")
# Main conclusion remains the last narrative section; reproduction follows it.
s=s.replace("main+='\\\\clearpage\\\\phantomsection\\\\label{refs-start}",
            "main+=inp('data_statement.tex')\nmain+='\\\\clearpage\\\\phantomsection\\\\label{refs-start}")
# New tests run before prepare, so all reader counts derive from executed evidence.
s=s.replace("(R/'evidence.tex').write_text(evidence)", """allocation=json.loads((R/'results/allocation_validation.json').read_text())
assert allocation['status']=='PASS'
ac=allocation['counts']
evidence+='\\nThe nonsaturated extension additionally passes '+str(ac['allocation_dual_equalities'])+' exact primal/dual-event comparisons, '+str(ac['supporting_branch_maxima'])+' supporting branch maxima, '+str(ac['saturated_catalog_equalities'])+' saturated catalog/DP equalities, '+str(ac['all_promise_catalog_checks'])+' interior-promise catalog comparisons, and '+str(ac['pairwise_policy_transport_checks'])+' arbitrary-promise transport checks. The supporting-price equality certifies each fixed-book solution; finite regression is not used as proof of the general theorem.\\n'
(R/'evidence.tex').write_text(evidence)
(R/'generated/allocation_evidence.tex').write_text('\\\\subsection{Executed allocation checks}\\nThe executed exact suite reports '+str(ac['allocation_dual_equalities'])+' primal/dual-event equalities and '+str(ac['supporting_branch_maxima'])+' supporting branch maxima. It includes repeated caps, zero curvatures, singleton books, endpoint promises, and nonsaturated charged-book selection. Full rational values and checks are in the allocation validation record.\\n')""")
# Bibliography includes the actual current reader union. Sort by the author field.
s=s.replace("items[k] for k in sorted(keys)","items[k] for k in sorted(keys,key=lambda k: re.sub(r'[^A-Za-z0-9 ]','',items[k].split('\\n',1)[1]).lower())")
p.write_text(s)

p=R/'code/build.py'; s=p.read_text()
s=s.replace("BASE='1cf9c8df76437ee71d4291d1001e9c7f055781c5'", "BASE='a149cb3e5df35e33e64a148d7d620e019ca2b135'\nREVIEW='1cf9c8df76437ee71d4291d1001e9c7f055781c5'")
s=s.replace("'base_review_sha':BASE", "'base_source_sha':BASE,'review_sha':REVIEW")
s=s.replace("base_review_sha=BASE", "base_source_sha=BASE,review_sha=REVIEW")
s=s.replace("('verify.py','study.py','inherited.py','prepare.py')", "('verify.py','verify_allocation.py','study.py','inherited.py','prepare.py')")
s=s.replace("assert abstract_words<=300", "assert abstract_words<=200,('Abstract exceeds journal limit',abstract_words)")
s=s.replace("'verification.json','catalog_study.json','inherited.json'", "'verification.json','allocation_validation.json','catalog_study.json','inherited.json'")
s=s.replace("'-output-directory='+str(B),name", "'-recorder','-output-directory='+str(B),name")
s=s.replace("    manifest=dict(status='PASS'", """    # Only a committed, byte-identical source tree can receive a scientific SHA.
    dependencies=set()
    for reader in ('main','electronic_companion','RESPONSE_TO_REFEREES'):
        for line in (B/(reader+'.fls')).read_text().splitlines():
            if not line.startswith('INPUT '): continue
            p=Path(line[6:])
            if not p.is_absolute(): p=ROOT/p
            p=p.resolve()
            if p.is_file() and ROOT in p.parents and p.suffix in ('.tex','.sty','.cls','.bib'):
                dependencies.add(p)
    dependencies.update(R.glob('*.py'))
    dependencies.update((R/'code').glob('*.py'))
    dependencies.add(R/'RESPONSE_TO_REFEREES.md')
    tracked_source_files=[str(p.relative_to(ROOT)) for p in sorted(dependencies)]
    clean=False
    if (ROOT/'.git').exists():
        changed=git('diff','--name-only','HEAD','--',*tracked_source_files)
        untracked=git('ls-files','--others','--exclude-standard','--',*tracked_source_files)
        clean=not changed and not untracked
        if not clean: raise RuntimeError('Scientific source must be committed before build: '+changed+' '+untracked)
    manifest=dict(status='PASS'""")
s=s.replace("source_commit=git('rev-parse','HEAD') if (ROOT/'.git').exists() else 'local-artifact-worktree',",
            "source_commit=git('rev-parse','HEAD') if clean else 'local-artifact-worktree',source_tree_clean=clean,complete_reader_inputs={str(p.relative_to(ROOT)):sha(p) for p in sorted(dependencies)},toolchain=subprocess.check_output(['pdflatex','--version'],text=True).splitlines()[0],")
p.write_text(s)

(R/'data_statement.tex').write_text(r'''\paragraph{Data and code availability.}
All populations, prices, and curvatures in the experiments are synthetic and distributed with the implementation. The accompanying code contains an executable readme, exact input interfaces, seeded verification, raw measurements, and machine-readable certificates. One preparation command runs the current and historical exact tests in isolated output paths; a separate build command compiles committed sources and records every reader input and output hash. Historical measurements retain their original runner and timing definitions. No external customer data are needed. The repository reproduction instructions identify the current source revision and package paths without treating a generated PDF as its own source identity.
''')

p=R/'RESPONSE_TO_REFEREES.md'; s=p.read_text()
s=s.replace('same-alphabet scaling and saturation lifts', 'same-alphabet contractions and partial lifts')
s=s.replace('Same-alphabet scaling and saturation lifts', 'Same-alphabet contractions and partial lifts')
s=s.replace('`V_m^I(bar b) - L_f epsilon <= V_m^I(bar b-epsilon) <= V_m^I(bar b) + H epsilon`',
            '`V_m^I(B2) - L_f (B2-B1) <= V_m^I(B1) <= V_m^I(B2) + H (B2-B1)` for every 0 <= B1 <= B2 <= bar b')
s+='''
## 11. Further strengthening and complete publication recovery

The prior R38 branch contained a verified source transport but its publication job stopped when the generated-reference directory was absent. Its root reader still described R37. R39 starts from that remote commit, leaves its transport and every earlier branch untouched, recovers all 17 source files against the existing SHA-256 checks, and adds a clean-checkout-safe preparation path. It does not relabel the old PDF as a new manuscript.

The value stability theorem now compares any two feasible root promises, not only saturation with an interior promise. Its partial lift preserves the writable alphabet under all three timing conventions. Electronic Companion Proposition on supporting-price certificates turns the interior fixed-book reduction into an exact algorithm. It fills positive chord segments, then zero-cost tails, then a sorted positive-curvature water-level sweep. A separate dual-event algorithm and exhaustive branch-maximizer checks verify the result. Small finite-catalog optimization at any promise compares certified allocations with actual selected-level charges; its exponential subset-search complexity is explicit and is not confused with the polynomial saturated catalog recurrence.

The current journal instructions are enforced: abstract at most 200 words, three keywords, a mathematics-free introduction, author-year references sorted by author, and main tables following references. The build validates anonymous readers, layout, cross-references, committed source identity, all transitive local TeX inputs, and complete inherited-file preservation. The final evidence counts and page totals are those actually produced by the executed validation records, not prospective claims.
'''
p.write_text(s)
p=R/'README.md'; s=p.read_text()
s+='''
## R39 recovery and additional exact allocation

This branch is based on remote R38 commit `a149cb3e5df35e33e64a148d7d620e019ca2b135`. That predecessor's publication job failed before replacing the R37 root readers. `R38_RECOVERY.json` records the source-bundle hashes and the failed run; `assemble.py` verifies and recovers the original source without changing the historical transport.

From a full clean checkout, run `python revisions/or-r39-robust-quantizer-20260924/assemble.py`, then the `code/build.py prepare` command below this directory. Commit the prepared scientific sources, then run `code/build.py build`. The separate phases prevent an uncommitted or obsolete source tree from being assigned a scientific commit identity.

`code/allocation.py` exposes `solve_allocation(model, codebook, promise)` and `solve_catalog_promise(model, catalog, charges, budget, promise)`. The first returns exact rational branch targets, the value, a supporting multiplier, and an equal dual bound. The second is an exponential small-catalog reference solver, not the saturated polynomial catalog DP. `code/verify_allocation.py` compares independent primal/dual algorithms, checks branch maxima, tests arbitrary-promise contractions and partial lifts, and compares the saturation endpoint against the existing DP.

The authoritative readers are root `main.pdf` and `electronic_companion.pdf`; the current response and machine-readable build, recovery, preservation, and evidence records are in this directory. Earlier root historical supplements are archives, not competing current submission readers.
'''
p.write_text(s)
p=R/'SUBMISSION_CHECKLIST.md'; s=p.read_text().replace('300','200')
s+='\n- R39: arbitrary-promise stability and independently certified nonsaturated allocation; original R38 source recovered without overwriting transport.\n- Final page counts, complete source dependencies, exact test results, and output hashes are validated by BUILD_VALIDATION.json.\n'
p.write_text(s)
p=R/'LITERATURE_AUDIT.md'; s=p.read_text()
s+='''

## R39 independent source recheck, 2026-09-24

The journal's current submission-guidelines page requires a text-only abstract of at most 200 words and an introduction without mathematical notation; R39 enforces both. Wu's publisher record confirms the bibliographic entry; the directly readable Gronlund et al. arXiv v4 manuscript discusses the earlier matrix-search quantization result. Publisher full-text fetches for Wu and Croci were not available in this recheck, so their inaccessible full texts are not claimed as newly inspected. The Croci et al. authors' Manchester manuscript, pages 2–3, gives the adjacent distance-proportional rule. Pages–Wilbertz arXiv:1010.4642v2, page 16, explicitly extends splitting by nearest-neighbor projection outside the grid convex hull; R39 retains that closer predecessor in its comparison. Fu's publisher page confirms the finite-rate control scope and journal metadata. These checks establish the cited predecessor principles, not an exhaustive worldwide novelty proof.

Primary access points: https://pubsonline.informs.org/page/opre/submission-guidelines ; https://www.sciencedirect.com/science/article/pii/0196677491900392 ; https://eprints.maths.manchester.ac.uk/2836/1/cfhm21.pdf ; https://arxiv.org/pdf/1010.4642 ; https://arxiv.org/html/1701.07204v4 ; https://www.ieee-jas.net/article/doi/10.1109/JAS.2023.123972 .
'''
p.write_text(s)
print('Recovered 17 hash-verified R38 sources; assembled R39 without editing inherited files.')
