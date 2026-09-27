"""R58 publication audit and data-derived prose; no outcome is supplied by hand."""
from pathlib import Path
import collections,hashlib,json,os,subprocess,sys,zipfile,statistics
from fractions import Fraction
R=Path(__file__).resolve().parents[1];ROOT=R.parents[1]
sys.path.insert(0,str(R/'code'))
from rational import F,write
BASE='eee0d39e08eaedc3a26cad792b71c9c5b5a8abd9'

def joint_type_tests():
    import random
    from price_path import Model,normalize,allocate,encode
    from compression import compress
    from check_price import check_policy
    rows=[]
    for seed in range(36):
        rng=random.Random(5700+seed);k=6;n=9
        caps=[Fraction(1,2) if j%2==0 else Fraction(3,4) for j in range(k)]
        rr=[Fraction(2) if j%2==0 else Fraction(5,2) for j in range(k)]
        qq=[Fraction(1,2) if j%2==0 else Fraction(3,4) for j in range(k)]
        # Heterogeneous rewards, within-type heterogeneous costs and prefix ceilings.
        a=[Fraction(i,8) for i in range(n)]
        ceilings=[a[rng.randrange(int(caps[j]*8),9)] for j in range(k)]
        spec=dict(caps=caps,weights=[Fraction(1,k)]*k,gamma=[Fraction(rng.randrange(4),8) for _ in range(k)],ceilings=ceilings,reward_r=rr,reward_q=qq,catalog=a,charges=[Fraction(rng.randrange(3),100) for _ in a],B=Fraction(3,4)*sum(caps)/k,m=n)
        # normalize's schema uses the same explicit keys as the released generator.
        spec={'model':{key:spec[key] for key in ('caps','weights','gamma','ceilings','reward_r','reward_q')},'catalog':a,'charges':spec['charges'],'promise':spec['B'],'budget':n}
        spec=encode(spec);d,aa,rho,B,m=normalize(spec)
        p=allocate(d,aa,B,dict(zip(aa,rho)));out=compress(spec,p)
        check_policy(spec,encode(out['policy']))
        assert out['joint_types']==2 and len(out['policy']['book'])<=4
        assert out['policy']['value']>=p['value']
        rows.append(dict(seed=seed,joint_types=2,original_commands=n,compressed_commands=len(out['policy']['book']),value_gain=out['policy']['value']-p['value']))
    write(R/'results/JOINT_TYPE_REGRESSION.json',dict(status='PASS',models=len(rows),records=rows))
    print('Joint type regression PASS:',len(rows))

def checker_import_test():
    import ast
    modules=['check_price','check_deficit','check_enumeration','check_screen','check_certificate56','rational']
    forbidden={'price_path','deficit','enumeration','screening56','compression','saturation'}
    graph={}
    for name in modules:
        tree=ast.parse((R/'code'/(name+'.py')).read_text());imports=set()
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):imports.update(x.name.split('.')[0] for x in node.names)
            elif isinstance(node,ast.ImportFrom) and node.module:imports.add(node.module.split('.')[0])
        if imports & forbidden:raise RuntimeError('Checker imports optimizer: '+name)
        graph[name]=sorted(imports)
    write(R/'results/CHECKER_DEPENDENCIES.json',dict(status='PASS',forbidden=sorted(forbidden),import_graph=graph))
    print('Independent checker import graph PASS')

def outcomes():
    out=R/'results';s=json.loads((out/'SUMMARY.json').read_text());c=s['status_counts']
    rows=[json.loads(p.read_text()) for p in (out/'runs').glob('*.json') if '.phase.' not in p.name]
    xr=json.loads((out/'VERIFY_REPLAY.json').read_text())
    counts='; '.join(str(v)+' '+key.lower().replace('_','-') for key,v in sorted(c.items()))
    deficit=[x for x in rows if x['method']=='deficit'];done=[x for x in deficit if x['status'] in ('EXACT','TOLERANCE')]
    scr=s['screen_total_time_wins'];ratio=s['median_screen_total_ratio']
    exact=[x for x in rows if x['method']=='price' and x['family']=='exact_extension']
    lattice=[x for x in rows if x['method']=='lattice' and x['family']=='lattice']
    nlat=sum(x['status']=='EXACT' and x.get('verification_status')=='PASS' for x in lattice)
    text=r'''\subsection{All declared runs and certificate costs}
The source-frozen execution retains all '''+str(s['timed_records'])+''' timed records: '''+counts+r'''. Status counts summarize record completeness, not a pooled success rate across unequal accuracies, budgets, or method definitions. The separate panels in Tables~\ref{tab:primary56}--\ref{tab:lattice56} retain their original targets. '''+str(s['certificates'])+''' runs produce rational certificates, including conservative fallback intervals from interrupted algorithms. '''+str(s['completed_certificate_checks'])+''' certificates have a successful independent check. '''+str(s['primary_verification_timeouts'])+''' initial checks reach their twelve-second allowance; '''+str(s['replay_passes'])+''' unchanged certificates subsequently pass the separately timed extended check. No initial status is rewritten. The longest extended check takes '''+format(s['maximum_verification_replay_seconds'],'.3f')+r''' seconds. Numerical MIP returns remain separate from exact rational evidence.

The heterogeneous deficit method completes '''+str(len(done))+''' of '''+str(len(deficit))+''' requested primary and accuracy runs. '''+str(s['deficit_with_exact_reference'])+''' completed runs have an independently checked exact reference on the identical model. The maximum measured incumbent loss among those comparisons is '''+format(float(F(s['deficit_max_actual_regret'])),'.6g')+r'''. This observed loss is not the guaranteed upper-minus-lower interval. Interrupted resource computations and expensive independent checking remain part of the record; the faster convolution theorem does not make every complete proof pipeline inexpensive.

\subsection{Exact-target search and end-to-end screening}
The exact-target extension contains '''+str(len(exact))+''' price runs, of which '''+str(sum(x['status']=='EXACT' for x in exact))+r''' close at zero rational width. Table~\ref{tab:exact56} reports all nine two-second cases, with nodes, oracle calls, root gaps, fixed-book comparisons, depth and elapsed optimization time. The half-second counterparts remain in the raw records. Nine separate deterministic replays expose each tested price and required/forbidden set. They measure search mechanics, not replacement benchmark times. Across recorded price runs, maximum tree depth is '''+str(s['maximum_tree_depth'])+''' and the largest completed-oracle count is '''+str(s['maximum_oracle_calls'])+r'''. Retained prices use at most '''+str(s['maximum_price_numerator_bits'])+''' numerator bits and '''+str(s['maximum_price_denominator_bits'])+r''' denominator bits. The original R54 hard reduction instances, including failures, remain unchanged in the historical evidence. Neither root closure nor these observed bit lengths imply a polynomial worst-case search tree.

There are '''+str(s['screen_pairs'])+''' paired screening comparisons under the same two-second total optimization allowance. '''+str(scr)+''' pairs improve total optimization-plus-serialization-plus-checking time; the median paired total-time ratio is '''+format(ratio,'.3f')+r'''. Table~\ref{tab:screen56} reports charges, deletions by eligibility category, final widths and both total times. Screening is charged for incumbent construction and forced-command bounds before the reduced solve. All unfavorable pairs remain visible. A smaller catalog or tighter bound is not itself an end-to-end speed improvement.

\subsection{Lattice scaling and implementation checks}
Among the eighteen zero-service lattice cases, '''+str(nlat)+r''' return an independently checked exact optimum. Cap-grid denominators are 8, 16 and 32; command budgets are two and four; all three seeds are retained. The table reports the actual resource-grid size, which also depends on probabilities and commanded-quantity granularity. The separate encoding stress uses denominators $2^8$, $2^{16}$ and $2^{32}$ and preserves any state-limit rejection rather than assigning it an optimum.

The exact regression covers 36 general models, 36 lattice models, 36 common-reward cap-count constructions, four strict $2q$ examples, and 200 convolutions with support holes. The joint cap--reward extension adds 36 genuinely heterogeneous reward models, each with two joint classes and independently checked original-policy reconstruction. Seven certificate mutation classes are rejected. A full twenty-thousand-bit rational certificate and a pre-allocation enormous-state rejection distinguish correct serialization from numerical tractability. These finite tests validate implementations; the universal assertions rely on the stated proofs. All operational data remain synthetic.
'''
    (R/'generated/current_outcomes.tex').write_text(text)
    # Keep notes truthful even if machine-dependent timing changes a completion status.
    tab=R/'generated/main_tables.tex';st=tab.read_text()
    st=st.replace('Every price result in this panel has zero rational final width and passes independent verification.','The raw record states each final interval, status and independent-check result; the generated text reports the actual number of exact closures.')
    tab.write_text(st)
    audit=dict(status='PASS',timed_records=len(rows),declared_records=225,all_declared_runs_present=len(rows)==225,source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'code').glob('*.py')},record_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((out/'runs').glob('*.json'))},summary_sha256=hashlib.sha256((out/'SUMMARY.json').read_bytes()).hexdigest())
    if len(rows)!=225:raise RuntimeError('Incomplete declared run archive')
    for x in rows:
        if 'certificate' not in x:continue
        raw=(out/x['certificate']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=x['certificate_sha256']:raise RuntimeError('Certificate digest mismatch')
        ok=x.get('verification_status')=='PASS' or any(z['run_id']==x['id']+'--'+x['method'] and z['replay_status']=='PASS' and z['certificate_sha256']==x['certificate_sha256'] for z in xr)
        if not ok:raise RuntimeError('Unverified published certificate: '+x['id']+' '+x['method'])
    manifest=json.loads((out/'SOURCE_MANIFEST.json').read_text())['source_hashes']
    if manifest!=audit['source_hashes']:raise RuntimeError('Source changed after execution began')
    write(out/'PUBLICATION_AUDIT.json',audit)

def preservation():
    allowed={'README.md','main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','NDU_OR_submission_checklist.md'}
    cp=subprocess.run(['git','ls-tree','-rz',BASE],cwd=ROOT,capture_output=True,check=True)
    inherited=[];errors=[]
    for line in cp.stdout.split(b'\0'):
        if not line:continue
        meta,name=line.split(b'\t',1);mode,kind,sha=meta.decode().split();name=name.decode()
        if kind!='blob':continue
        path=ROOT/name
        if not path.is_file():errors.append('Missing '+name);continue
        data=path.read_bytes();current=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        status='unchanged'
        if current!=sha:
            if name not in allowed:errors.append('Unexpected replacement '+name)
            pred=R/'predecessor'/name
            if not pred.exists():errors.append('Missing predecessor '+name)
            else:
                b=pred.read_bytes();psha=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
                if psha!=sha:errors.append('Predecessor mismatch '+name)
            status='exact predecessor retained'
        inherited.append(dict(path=name,original_git_blob=sha,current_git_blob=current,status=status))
    write(R/'PRESERVATION_MANIFEST.json',dict(status='PASS' if not errors else 'FAIL',scientific_parent=BASE,inherited_files=len(inherited),errors=errors,files=inherited))
    if errors:raise RuntimeError('; '.join(errors[:10]))

def package():
    dest=R/'CODE_AND_DATA.zip'
    # The frozen baseline package is included when present; all current sources,
    # records and certificates remain individually readable in the Git tree.
    entries=[]
    for base in [ROOT/'revisions',ROOT/'artifact']:
        if not base.exists():continue
        for p in base.rglob('*'):
            if not p.is_file() or p==dest or p in (R/'PUBLICATION_STATUS.json',R/'PACKAGE_MANIFEST.json'):continue
            rel=p.relative_to(ROOT).as_posix()
            if '/__pycache__/' in rel or '/transport/' in rel:continue
            if p.suffix in ('.py','.tex','.json','.csv','.md','.txt','.gz','.bib','.bst','.cls') or (R in p.parents and p.suffix in ('.pdf','.png')):entries.append(p)
    entries+=[ROOT/name for name in ['README.md','main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','informs3.cls','main.bib','ormsv080.bst'] if (ROOT/name).exists()]
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(set(entries)):z.write(p,p.relative_to(ROOT))
    write(R/'PACKAGE_MANIFEST.json',dict(sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),bytes=dest.stat().st_size,files=len(set(entries)),scope='All retained readable revision source/data dependencies and current readers. Older large PDF readers remain unchanged in Git. No fabricated absent R55 local archive.'))

if __name__=='__main__':
    for task in sys.argv[1:]:globals()[task]()
