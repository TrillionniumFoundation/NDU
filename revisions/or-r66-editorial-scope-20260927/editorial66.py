"""Reconstruct the R66 editorial revision from an intact, hash-checked R65 package.

No accepted checker, request schema, theorem, proof, table or timing record changes.
The script writes complete standalone sources; it is not a substitute for them.
"""
from pathlib import Path
import argparse, hashlib, json, re, shutil

BASE = '6bc195dcdbc93d1a796b1388639c053c0a11ddd0'
BASE_TREE = '13f8d13ef25e3ca6c1dd99e046b245bc70f0d5a2'
REVIEW = '0382789afc96be20497063930602d5a6be96909a'
REPORT = 'reviews/operation_research_referee_report_r65_independent_harsh_2026-09-27.md'
REPORT_BLOB = '3d1c9c5ef76988894b624b9872e3a5332566cf07'
BRANCH = 'revision/ndu-operations-research-r66-editorial-scope-20260927'

MAIN_SCOPE = (' The verification receipt certifies only its explicitly reported mathematical '
              'conclusions; it neither authenticates the request source nor endorses '
              'unreported legacy metadata.')
EC_SCOPE = r'''\paragraph{Scope of a verification receipt.}\label{sec:receipt66}
Only mathematical conclusions explicitly represented in the returned verification receipt are certified, with the meaning assigned by its proof class. A valid interval and attainment of the externally requested width are separate conclusions; a lower-only receipt supplies no certified upper bound. Unknown fields are rejected in the exact request and envelope schemas. A low-level legacy certificate may contain additional metadata, but an unreported extension claim is not endorsed by a successful check. In particular, a certificate cannot acquire authenticated origin, runtime attestation, or editorial approval by adding such a claim. A content digest binds bytes or canonical values, not the identity or authority of their supplier. The caller must obtain its external request from trusted storage or an authenticated channel; that trust is an assumption, not a conclusion of this mathematical checker. Historical replay wrappers remain newly constructed wrappers, and neither their creation nor a later successful check alters the original execution outcome.

'''

COMMENTS = [
 ('1', 'Physical regime of exact tractability', 'Main, Sections 1 and 5; Theorem 5.1',
  'The common linear terminal reward and free preliminary service assumptions remain explicit. Uniform fees are not asserted to solve the curved-reward or costly-service model.'),
 ('2', 'Near-standard tariffs', 'Main, Abstract and Section 6',
  'The surrogate is solved exactly; the recovered original policy is feasible and evaluated exactly, but its original-fee optimality guarantee remains additive.'),
 ('3', 'Projection class', 'Main, Abstract, Section 6.2 and Proposition 6.2',
  'Minimum distortion is claimed only within the specified sparse-exception class. The trimmed absolute-deviation antecedents and proof are retained.'),
 ('4', 'Three exception counts', 'Main, Section 6 and Table 5; companion, EC.11.2',
  'd_allow is the projection allowance, d_proj the actual exceptions around its projection standard, and d_tariff the inner modal count. Their distinct definitions and inequality are unchanged.'),
 ('5', 'Guard interpretation', 'Companion, EC.11.1 and verification-receipt paragraph',
  'A verified guard means agreement with the external mathematical request, not an attestation that a runtime process used that guard.'),
 ('6', 'Proof, target and execution outcomes', 'Main, Section 9 and table notes; companion, EC.11.1',
  'Mathematical PASS, requested-width attainment, original on-time success and later integrity replay remain separate. No original failure is upgraded.'),
 ('7', 'Numerical upper bounds', 'Main, Section 9 and Table 2; companion, EC.11.1',
  'SCIP upper bounds remain numerical. Independently reconstructed feasible policies establish lower bounds only, with PASS_LOWER_ONLY and no certified upper bound.'),
 ('8', 'Regret intervals', 'Main, Section 9.5 and Table 5',
  'Bracket notation is unchanged when exact regret is not identified. The five identified zero regrets and two bounded regrets retain their original comparator evidence.'),
 ('9', 'Historical wrappers', 'Companion, EC.11.1; REQUEST_CONTRACT65.md',
  'Legacy bytes remain unchanged. Wrappers are constructed at replay and are not represented as having existed at original execution.'),
 ('10', 'Request authentication', 'Companion, verification-receipt paragraph; REQUEST_CONTRACT65.md',
  'Authentication and trusted storage remain outside the mathematical checker. A digest does not authenticate the request source.'),
 ('11', 'Hybrid routing', 'Main, Section 9.4',
  'The hybrid is the tested routing policy, not a universally optimal router. The adversarial outcomes and their complete denominators are unchanged.'),
 ('12', 'Placement of implementation detail', 'Main, code-and-data paragraph; companion, EC.11',
  'The main article remains centered on the representation and complexity frontier. The receipt clarification is explained primarily in the companion.'),
 ('optional', 'Unknown legacy extension metadata', 'Companion, verification-receipt paragraph; tests66.py',
  'Only explicitly returned mathematical conclusions are certified. Unreported extension metadata is not endorsed. Exact request/envelope schemas and all existing checkers remain unchanged; new tests document their existing behavior.')
]

SCOPE_MD = '''# R66 editorial scope and response map

The governing R65 report recommends **Accept** and requests no further scientific revision. This is a response to a referee recommendation, not a claim of an editor's or journal's formal acceptance.

R66 makes the optional receipt-scope clarification and preserves all twelve nonblocking qualifications. No theorem, proof, mathematical display, bibliography, empirical table, solver, checker, request schema, frozen input, historical timing, failure classification, or original certificate is changed. The request API deliberately remains `binding65.verify_request` and its schema remains `NDU-R65-request-v1`.

## Comment-by-comment disposition

| R65 item | Subject | Current location | Disposition |
|---|---|---|---|
'''
SCOPE_MD += ''.join('| '+ ' | '.join(row)+' |\n' for row in COMMENTS)
SCOPE_MD += '''
## Interpretation of a returned receipt

Read `status`, the reported objective bound(s), `tolerance_met`, and the reported binding/transfer fields according to their documented proof class. `PASS` alone is not a statement of target attainment, original on-time completion, authenticated provenance, runtime configuration, or editorial acceptance. `PASS_LOWER_ONLY` has no certified upper bound. Content hashes identify content, not the identity or authority of its supplier. Runtime and original target outcomes still require the frozen execution record; new replay does not backdate that record.

The exact request and envelope schemas reject unknown fields. Low-level legacy certificate bodies are not uniformly closed schemas. An unknown extension field inside such a body is not certified merely because the recognized mathematical proof passes. Consumers must use the checker-produced receipt, not merge unverified extension claims into it and present the combination as checker output. This is an interpretation of the existing interface, not a new authentication protocol or schema version.

## New regression evidence

`tests66.py` selects the smallest archived proof of each of the six supported classes, validates each baseline, and inserts nonmathematical extension claims into low-level certificate bodies. It checks that all mathematical receipt fields are unchanged and do not contain those claims. The comparison excludes only the checker's per-execution `seconds` diagnostic, which is not a mathematical conclusion. The same extension keys are rejected in the exact request, embedded request and envelope. The test also preserves numerical lower-only semantics and checks unknown nested tariff metadata. These are documentation-regression checks, not new optimization observations or a universal fuzzing guarantee.

## Preservation

Every entry of the 7,080-file R65 manifest resolves to `archive/r65/<path>` if that file was changed and to its original relative path otherwise. Original root readers, response and manifest are retained. The current main article and companion contain all accepted mathematical environments and tables, not merely archival copies. All existing `code/`, `evidence/`, `generated/`, `sections/` and `results/` files retain their R65 bytes; new execution evidence is confined to `results/r66/`. The current package verifier checks both preservation and complete delivered-file coverage.
'''

RESPONSE = r'''\documentclass[11pt,letterpaper]{article}
\usepackage[margin=1in]{geometry}
\usepackage[T1]{fontenc}
\usepackage{newtxtext,newtxmath}
\usepackage{setspace,enumitem,xurl}
\usepackage[hidelinks]{hyperref}
\onehalfspacing\setlength{\emergencystretch}{2em}
\begin{document}
\begin{center}
{\Large\bfseries Response to the R65 Referee Report}\par\medskip
Finite-Catalog Resource Allocation:\\ A Tariff-Sensitive Complexity Frontier\par\medskip
Anonymous revision R66 --- September 27, 2026
\end{center}
We thank the referee for the careful independent audit and the recommendation to accept the paper. The report identifies no remaining scientific revision and asks that twelve qualifications be preserved during final preparation. We have retained each qualification and incorporated the optional clarification of what a verification receipt certifies. We have not changed a theorem, proof, mathematical display, empirical table, checker, request schema, or historical execution outcome. The complete R65 readers and response remain available in the preservation archive.

\section*{Editorial clarification of the receipt boundary}
The companion now states explicitly that only mathematical conclusions represented in the returned verification receipt are certified, with their proof-class-specific meaning. A successful check does not endorse arbitrary additional metadata inside a low-level legacy certificate. The exact request and envelope schemas continue to reject unknown fields. The main article's code-and-data paragraph provides a single-sentence statement of this boundary; implementation detail remains in the companion.

We also distinguish content binding from authenticated provenance. A digest does not establish the identity or authority of its supplier. The caller must obtain the external request from trusted storage or an authenticated channel; this remains an assumption outside the mathematical checker. Neither runtime attestation nor editorial approval can be acquired by adding such a claim to a certificate. This is an explanatory clarification of the existing interface, not a new checker contract or authentication layer.

\section*{Disposition of the twelve nonblocking comments}
\begin{enumerate}[leftmargin=*,label=\textbf{\arabic*.}]
\item \textbf{Physical regime.} The abstract, introduction and tariff section continue to specify common linear terminal reward and free preliminary service. The exact tariff theorem and proof are unchanged. Uniform fees are not claimed to solve the general curved-reward or costly-service model.
\item \textbf{Near-standard tariffs.} We retain exact optimization of the sparse-exception surrogate, exact original-policy feasibility and fee evaluation, and an additive original-fee optimality certificate. No exact-tractability extension to arbitrary near-standard fees is introduced.
\item \textbf{Projection class.} The abstract and projection subsection retain the specified sparse-exception class. Minimum distortion is not asserted over an unrestricted surrogate family. The attribution to trimmed absolute-deviation methods and the complete projection argument are unchanged.
\item \textbf{Exception counts.} The projection allowance, actual projected exception count and inner modal exception count remain distinct in the text, companion and projection-quality table. Their definitions, ordering and reported values are unchanged.
\item \textbf{Guard.} The companion continues to interpret a verified guard as agreement with the external mathematical request, not runtime attestation. Execution configuration and deadlines require separate immutable records.
\item \textbf{Evidence categories.} Mathematical validity, requested-width attainment, original on-time success and later integrity replay remain separate. A valid interval need not meet the requested tolerance. The historical failures and incomplete checks retain their original classification.
\item \textbf{Numerical solver evidence.} SCIP upper bounds remain numerical. Independently checked reconstructed policies certify lower bounds only. The clarification explicitly states that a lower-only receipt supplies no certified upper bound.
\item \textbf{Regret intervals.} Table 5 retains bracketed regret bounds wherever the comparator does not identify exact regret. No bounded regret is relabeled as an exact value, and the five identified zero regrets retain their exact comparator evidence.
\item \textbf{Historical wrappers.} The companion and request-contract document continue to disclose that wrappers are constructed at replay. Original certificate bytes are unchanged, and the new wrappers are not attributed to the original execution.
\item \textbf{Authentication.} Trusted storage and authenticated transport remain outside the mathematical certification scope. The new receipt paragraph makes this boundary explicit without asserting an unimplemented transport layer.
\item \textbf{Hybrid routing.} The computational section retains the tested hybrid and its mixed adversarial outcomes. It does not assert a universally optimal routing policy. All original requests and unsuccessful outcomes remain in the reported denominators.
\item \textbf{Expository placement.} The article remains centered on the selected-boundary representation and tariff-sensitive complexity frontier. Detailed certificate interpretation stays in the companion. No scientific content has been removed to make room for it.
\end{enumerate}

\section*{Verification and preservation}
The new receipt-scope regression uses existing frozen certificates from all six supported proof classes. It checks that adding unknown extension claims to legacy certificate bodies does not add certified conclusions to their returned receipts, while the corresponding unknown fields are rejected in the exact request and envelope. A nested tariff case and numerical lower-only semantics are also checked. The accepted checkers and their schemas are byte-identical to R65.

The package verifier compares every accepted mathematical environment, mathematical display, bibliography and table in the current readers with R65. It resolves all 7,080 original manifest entries through an explicit preservation map and requires unchanged existing code, inputs, proof files and execution records. New qualification reruns the request/transfer and retained semantic regressions, the structural suites and the complete frozen-proof replay. Original timing and target classifications are never overwritten by this replay. The exact commands, outcomes, file hashes and build checks accompany the revision.

A separate receipt binds the published commit and tree to the rebuilt readers and executed checks. It is evidence of artifact integrity and verification, not an editorial decision. This revision addresses the report's editorial comments without changing the scientific claims or checker contract that the referee found acceptable.
\end{document}
'''

README = '''# NDU — Operations Research revision R66

**Finite-Catalog Resource Allocation: A Tariff-Sensitive Complexity Frontier**

Read `main.pdf`, `electronic_companion.pdf` and `RESPONSE_TO_REFEREES.pdf`. All three have standalone LaTeX sources. R66 responds to the September 27, 2026 R65 report, which recommends **Accept** with nonblocking editorial comments. A referee recommendation is not represented as a formal journal decision.

## What changed

The main article adds one receipt-scope sentence; the companion explains that only explicitly reported mathematical conclusions are certified and that unreported legacy extension metadata is not endorsed. Content binding is not request authentication, runtime attestation or editorial approval. `EDITORIAL_SCOPE66.md` maps all twelve comments and the optional clarification to their retained or revised locations. `EDITORIAL_DIFF66.patch` exposes the entire reader diff.

No accepted theorem, proof, mathematical display, bibliography, empirical table, optimizer, checker, request schema or historical observation changes. All scientific content remains in the current main article and companion. Existing R65 code and evidence remain byte-identical. The external request API is still `code/binding65.py`, with the exact same schema; `REQUEST_CONTRACT65.md` remains the operative request contract.

## Reproduction

Python 3.13.5 and the versions in `requirements.txt` are used by the qualification workflow. Install the declared TeX packages (including newtx) to compile the readers.

```sh
python -m pip install -r requirements.txt
python qualify66.py
python publish66.py
python verify66.py --replay-output /tmp/ndu-r66-independent-replay
```

`qualify66.py` executes new and inherited regressions, compiles the readers and replays all frozen requests. It writes only new `results/r66/` evidence and current reader PDFs; reseal afterward. `publish66.py` seals the current package. `verify66.py` is read-only; optional fresh replay output must be outside the package. Old numbered builders remain preserved history, not current reproduction entry points. The current readers are direct, complete sources, not references to an unexecuted patch.

For a tariff or robust-tariff request, the accepted interface is unchanged:

```sh
python code/produce65.py request.json certificate.json
python code/binding65.py certificate.json request.json --output receipt.json
```

Supply the external request separately from the submitted proof. `--legacy` creates a request-binding wrapper at replay time; it does not backdate that wrapper. `PASS`, `tolerance_met`, original on-time success and later replay have different meanings. `PASS_LOWER_ONLY` certifies no upper bound. Consumers must not present arbitrary unverified legacy metadata as part of the checker-produced receipt.

## Evidence

`results/r66/SCOPE_TESTS66.json` documents the six-class receipt-scope regression. `results/r66/request/` and `results/r66/semantic/` contain fresh executions of the accepted request/transfer and semantic suites. Structural tests and the independent 48-case root-support enumeration remain checked. `results/r66/replay/` records fresh request-bound replay of all 405 frozen requests: 342 two-sided rational proofs, 47 lower-only proofs, and 16 requests without a certificate. All 389 available certificates, including 42 robust transfer proofs, remain checked. The 45 later-successful checks are not reclassified as original successes.

`results/r66/QUALIFICATION66.json` records actual commands, exit codes and logs. `results/r66/BUILD66.json` records page, abstract, reference and overflow checks. A separate exact-head receipt binds the final Git commit and tree after publication; it is external to that commit to avoid a self-referential hash.

## Preservation

For each of the 7,080 R65 manifest entries, `verify66.py` resolves `archive/r65/<path>` first and otherwise its original relative path, then checks the original SHA-256. Only changed root readers, response, README, content map and manifest need archival copies; existing `code/`, `evidence/`, `generated/`, `sections/` and `results/` entries are unchanged. The mathematical environments, displays, bibliographies and empirical tables are checked directly in the current readers. All earlier derivations and evidence remain included through the inherited preservation maps.

`PROVENANCE66.json` pins the R65 author commit and the exact R65 report commit/path/blob. The revision descends from the author commit, not the review commit. Main, review and prior revision branches are not modified. The full referee report is retained for provenance without treating its recommendation as a publisher decision.
'''

TESTS = r'''"""Document existing receipt semantics; do not change an accepted checker."""
from pathlib import Path
from copy import deepcopy
import argparse, gzip, hashlib, json, sys, time
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'code'))
from binding65 import bind_legacy, verify_request, NUMERICAL, ROBUST
from rational import digest
EXTENSIONS={
    'authenticated_origin': {'claimed': True, 'authority': 'unverified-extension'},
    'runtime_attestation': {'guard_used': 999, 'on_time': True},
    'editorial_approval': {'accepted': True},
    'unreported_optimality_claim': {'globally_exact': True},
    'vendor_extension': {'certified': True, 'payload': 'not-a-receipt-conclusion'}}

def mathematical_receipt(value):
    # Elapsed seconds are an execution diagnostic, not a certified mathematical conclusion.
    if isinstance(value,dict):return {k:mathematical_receipt(v) for k,v in value.items() if k!='seconds'}
    if isinstance(value,list):return [mathematical_receipt(v) for v in value]
    return value

def run(output):
    start=time.perf_counter(); output.mkdir(parents=True,exist_ok=True)
    rows=[json.loads(x) for x in (R/'results/r65/replay/REQUEST_RECEIPTS65.jsonl').read_text().splitlines()]
    chosen={}
    for row in rows:
        if 'external_request' not in row: continue
        rec=json.loads((R/'evidence/r61/results/records'/f"{row['id']}--{row['method']}.json").read_text())
        p=R/'evidence/r61/results'/rec['certificate'];cls=row['external_request']['certificate_class']
        if cls not in chosen or p.stat().st_size<chosen[cls][0]: chosen[cls]=(p.stat().st_size,p,row)
    assert len(chosen)==6
    accepted=[];rejected=[];witnesses=[];nested=0
    for cls,(_,p,row) in sorted(chosen.items()):
        cert=json.loads(gzip.decompress(p.read_bytes()));req=row['external_request']
        env=bind_legacy(cert,req);baseline=verify_request(env,req)
        if cls==NUMERICAL:
            assert baseline['status']=='PASS_LOWER_ONLY' and 'upper' not in baseline and not baseline['tolerance_met']
        for key,value in EXTENSIONS.items():
            assert key not in cert and key not in baseline
            changed=deepcopy(env);changed['certificate'][key]=value
            assert mathematical_receipt(verify_request(changed,req))==mathematical_receipt(baseline),(cls,key)
            accepted.append({'class':cls,'extension':key,'mathematical_receipt_unchanged':True})
            # The same fields are forbidden at all exact-schema boundaries.
            for where in ('envelope','external_request','embedded_request'):
                e=deepcopy(env);r=deepcopy(req)
                if where=='envelope':e[key]=value
                elif where=='external_request':r[key]=value
                else:
                    e['request'][key]=value
                    e['request_sha256']=digest(e['request'])
                try: verify_request(e,r)
                except ValueError as exc: rejected.append({'class':cls,'extension':key,'boundary':where,'reason':str(exc)})
                else:raise AssertionError((cls,key,where))
        if cls==ROBUST:
            for key,value in EXTENSIONS.items():
                e=deepcopy(env);e['certificate']['surrogate_certificate'][key]=value
                assert mathematical_receipt(verify_request(e,req))==mathematical_receipt(baseline)
                nested+=1
        witnesses.append({'class':cls,'source_file':p.relative_to(R).as_posix(),
            'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
            'external_request':req,'certificate':cert,'receipt':baseline})
    assert len(accepted)==30 and len(rejected)==90 and nested==5
    ans={'schema':'NDU-R66-receipt-scope-regression-v1','status':'PASS','baseline_classes':6,
         'legacy_extension_receipts_unchanged':len(accepted),'nested_tariff_receipts_unchanged':nested,
         'exact_schema_extensions_rejected':len(rejected),'numerical_lower_only_preserved':True,
         'excluded_comparison_fields':['seconds (per-execution diagnostic)'],
         'accepted_cases':accepted,'rejected_cases':rejected,'seconds':time.perf_counter()-start,
         'scope':'Finite documentation regression of unchanged checker behavior; not authentication, runtime attestation or new optimization evidence.'}
    (output/'SCOPE_TESTS66.json').write_text(json.dumps(ans,indent=2)+'\n')
    (output/'SCOPE_WITNESSES66.json').write_text(json.dumps({'extensions':EXTENSIONS,'cases':witnesses},indent=2)+'\n')
    return ans
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=R/'results/r66');a=p.parse_args()
    print(json.dumps(run(a.output),indent=2))
'''


def prepare(root):
    root=root.resolve();old=json.loads((root/'PACKAGE_MANIFEST.json').read_text())
    assert old['schema']=='NDU-R65-payload-manifest-v1' and len(old['files'])==7080
    for name,h in old['files'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==h,name
    archive=root/'archive/r65';assert not archive.exists();archive.mkdir(parents=True)
    names=['main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf',
           'RESPONSE_TO_REFEREES.tex','RESPONSE_TO_REFEREES.pdf','README.md','CONTENT_MAP.md','PACKAGE_MANIFEST.json']
    for name in names:shutil.copy2(root/name,archive/name)
    main=(root/'main.tex').read_text().replace('.build/r65/','.build/r66/')
    assert main.count('Operations Research --- R65')==1
    main=main.replace('Operations Research --- R65','Operations Research --- R66')
    needle='No proprietary operational data are used.'
    assert main.count(needle)==1;main=main.replace(needle,needle+MAIN_SCOPE)
    (root/'main.tex').write_text(main)
    ec=(root/'electronic_companion.tex').read_text().replace('.build/r65/','.build/r66/')
    assert 'R65' in ec
    # Version strings only; retain historical references to the R65 package.
    ec=ec.replace('Operations Research --- R65','Operations Research --- R66')
    ec=ec.replace('Electronic Companion --- R65','Electronic Companion --- R66')
    needle=r'\subsection{Certifying fee selection, projection, and minimal allowance}'
    assert ec.count(needle)==1;ec=ec.replace(needle,EC_SCOPE+needle)
    needle='Exact-head receipts establish artifact integrity and executed checks, not novelty or editorial acceptance.'
    assert ec.count(needle)==1
    ec=ec.replace(needle,needle+' R66 retains the complete R65 payload and adds only the receipt-scope clarification; the accepted mathematical statements, proofs, checkers, request schema, and historical observations are unchanged.')
    (root/'electronic_companion.tex').write_text(ec)
    (root/'RESPONSE_TO_REFEREES.tex').write_text(RESPONSE)
    (root/'EDITORIAL_SCOPE66.md').write_text(SCOPE_MD)
    (root/'README.md').write_text(README)
    content=(archive/'CONTENT_MAP.md').read_text()
    (root/'CONTENT_MAP.md').write_text(content+'''\n\n## R66 editorial clarification — accepted science and checker unchanged\n\nAll 7,080 R65 manifest entries are preserved under the `archive/r65/<path>`-first resolution rule. The current article and companion retain all 36 and 42 accepted mathematical environments, respectively, every display and bibliography, and all empirical tables. No inherited `code/`, `evidence/`, `generated/`, `sections/` or `results/` file is replaced. The complete editorial diff and all twelve comment dispositions are provided in `EDITORIAL_DIFF66.patch` and `EDITORIAL_SCOPE66.md`. Current build, qualification, sealing and read-only verification entry points end in `66.py`; the request API and schema remain the accepted R65 versions.\n''')
    (root/'tests66.py').write_text(TESTS)
    provenance={'revision':'R66','scope':'Editorial-only receipt interpretation; no scientific or checker-contract change',
        'scientific_parent':BASE,'scientific_parent_tree':BASE_TREE,
        'governing_review':{'branch':'review/operation-research-r65-independent-harsh-20260927',
          'commit':REVIEW,'path':REPORT,'blob':REPORT_BLOB,'recommendation':'Accept'},
        'branch':BRANCH,'preserved_manifest_entries':7080,'request_schema_unchanged':'NDU-R65-request-v1',
        'journal_acceptance_not_asserted':True}
    (root/'PROVENANCE66.json').write_text(json.dumps(provenance,indent=2)+'\n')
    import difflib
    diff=''.join(''.join(difflib.unified_diff((archive/name).read_text().splitlines(True),
                    (root/name).read_text().splitlines(True),fromfile='R65/'+name,tofile='R66/'+name))
                 for name in ('main.tex','electronic_companion.tex'))
    (root/'EDITORIAL_DIFF66.patch').write_text(diff)
    (root/'results/r66').mkdir(parents=True)
    print('R66 editorial sources reconstructed; accepted code and evidence untouched.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();prepare(a.root)
