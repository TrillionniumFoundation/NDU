"""Build a flat R63 reader without altering reviewed sources or execution rows."""
from pathlib import Path
import argparse, csv, hashlib, json, re, shutil, statistics, sys
ROOT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def slice_lines(text,a,b):return ''.join(text.splitlines(True)[a-1:b-1])
def table(caption,label,cols,head,rows,note):
    return ('\\begin{table}[p]\\centering\\caption{'+caption+'}\\label{'+label+'}\n'
            '\\begin{singlespace}\\small\\begin{tabular}{'+cols+'}\\toprule\n'+head+'\\\\\\midrule\n'+
            '\n'.join(' & '.join(map(str,row))+' \\\\' for row in rows)+
            '\n\\bottomrule\\end{tabular}\\par\\smallskip\\begin{minipage}{\\textwidth}\\footnotesize '+note+
            '\\end{minipage}\\end{singlespace}\\end{table}\n')

def tables(r61):
    rows=list(csv.DictReader((r61/'results/ALL_RUNS.csv').open()));out=[]
    for N,k,m in ((17,12,8),(65,32,16),(129,48,32)):
      for sec in (1,6):
        rr=[r for r in rows if r['family']=='scaling' and int(r['N'])==N and float(r['total_seconds'])==sec]
        vals=[]
        for meth in ('tariff','price','hybrid','enumeration','scip'):
          q=[r for r in rr if r['method']==meth];assert len(q)==8
          vals.append(f"{sum(r['numerical_target_met' if meth=='scip' else 'rational_target_met']=='True' for r in q)}/8")
        out.append([N,k,m,sec,*vals])
    t=table('Controlled scaling: target attainment within the original total allowance','tab:scaling63','rrrrrrrrr',
        '$N$ & $k$ & $m$ & Sec. & Tariff & Price & Hybrid & Enumer. & SCIP',out,
        'Every cell includes all eight exception counts. Tariff, price, hybrid, and enumeration use independently checked rational upper and lower bounds. SCIP uses its numerical upper bound and an independently checked lower policy. A later successful replay does not change these original timing outcomes. All entries are constructed controlled cells, not independent random replicates.')
    out=[]
    for d in (0,1,2,4,6,8,10,12):
      r=next(r for r in rows if r['family']=='scaling' and r['N']=='17' and r['d']==str(d) and r['total_seconds']=='6.0' and r['method']=='tariff')
      out.append([d,*[f"{float(r[x]):.4f}" for x in ('optimization_seconds','serialization_seconds','verification_seconds')],
                  r['optimizer_peak_rss_kib'],r['checker_peak_rss_kib'],f"{int(r['proof_bytes']):,}"])
    t+=table('The exception loop and independent certification at fixed physical size','tab:d63','rrrrrrr',
      '$d$ & Optimize (s) & Serialize (s) & Check (s) & Opt. KiB & Check KiB & Proof bytes',out,
      'Fixed $(N,k,m)=(17,12,8)$ and a six-second total allowance. Resident memory is the separate optimizer/checker process high-water mark. Proof bytes are uncompressed. Setup, process startup, and compression also consume the parent deadline; displayed component times are not asserted to sum to the total. The raw records contain all components and budgets.')
    root=json.loads((ROOT/'results/SUPPORT_STUDY63.json').read_text());out=[]
    for flag in (True,False):
      q=[x for x in root['rows'] if x['truth']['same_book_support']==flag]
      split=[x['mechanics']['splits'] for x in q]
      depths=[max(z['depth'] for z in x['mechanics']['evaluations']) for x in q]
      out.append(['Supported' if flag else 'Positive gap',len(q),f'{statistics.median(split):g}',max(split),max(depths),
                  f"{statistics.median(x['price_seconds'] for x in q):.4f}",
                  f"{statistics.median(x['verification_seconds'] for x in q):.4f}"])
    t+=table('Exact root-support classification and observed price-search work','tab:root63','lrrrrrr',
        'Root class & Cases & Med. splits & Max. splits & Max. depth & Med. solve (s) & Med. check (s)',out,
        'Classification comes from complete feasible-book enumeration and the exact upper concave hull, not from a selected probe book. All 48 final certificates are exact; 1,176 books are enumerated in total. Root-gap cases have a maximum exact minimum-price gap of $1/20$. Local diagnostic times are descriptive and are not pooled with the earlier frozen execution environment.')
    return t

def build(r60,r61):
    expected={'main.tex':'9dd88b398938c4bc4947e105ab0cdac2e6a92f745d31d0d2045d1801405a0719',
     'electronic_companion.tex':'55a1da24fac8869d90fbeb9109ed42a42dc3f64c06a9538ec14b8aa80f96d2d9'}
    for name,h in expected.items():assert sha(r60/name)==h,(name,'not reviewed R60 source')
    main=(r60/'main.tex').read_text();ec=(r60/'electronic_companion.tex').read_text()
    section=lambda n:(ROOT/'sections'/n).read_text()
    pre=slice_lines(main,1,62).replace('.build/r60/','.build/r63/').replace('--- R60','--- R63')
    a=pre.index('\\textbf{Abstract.}');b=pre.index('\\par\\vspace',a)
    abstract='A service provider must allocate an accepted aggregate promise while installing a small shared catalog of terminal commands. Individual expected caps and realization ceilings constrain implementation, and every installed command incurs a fixed charge. We derive an exact resource-path representation and establish a tariff-sensitive complexity frontier. With common linear rewards and free preliminary service, arbitrary command-specific charges remain parameterized-hard in the command allowance and cap count. A capacity dynamic program instead gives exact fixed-parameter tractability in the number of exceptions to a standard fee, and uniform fees permit polynomial-time optimization without a resource grid. We extend this result to near-standard tariffs through an explicit original-policy perturbation certificate and a minimum-distortion sparse-exception projection. Exact fee frontiers identify changes in installed commands and service allocation. Conservation, additive approximation, and same-book price support provide complementary guarantees for broader regimes. Controlled scaling and adversarial studies retain every interrupted request, separate numerical bounds from rational certification, and measure optimization, proof size, memory, and independent checking. An additional exhaustive diagnostic distinguishes genuine root support from positive price gaps.'
    assert len(abstract.split())<=200
    pre=pre[:a]+'\\textbf{Abstract.} '+abstract+'\n'+pre[b:]
    intro=slice_lines(main,62,83)
    intro=intro[:intro.index('The computational study evaluates')]+'''The computational study preserves the earlier evidence and adds an expanded frozen scaling and adversarial design. It varies the number of fee exceptions separately from physical size, records memory and proof costs, and retains every interrupted request. A separate exhaustive diagnostic identifies when the whole price-active family supports the promise. Near-standard fees are not treated as exact uniform fees: we bound the value lost by simplifying the tariff and evaluate the returned policy under its original charges.\n\n'''+slice_lines(main,75,83)
    # Main theorem chain; retained secondary results move to the companion.
    core=slice_lines(main,83,121)+section('institution.tex')+slice_lines(main,121,187)
    hard=slice_lines(main,263,321)
    tariff=slice_lines(main,321,382).replace('A most frequent catalog fee minimizes $d$ and is found without optimizing any allocation.',
      'A most frequent catalog fee minimizes $d$ and is found without optimizing any allocation. Equal-frequency modes are resolved by the smallest rational fee; any mode gives the same minimum exception count.')
    price=slice_lines(main,494,520);price=price[:price.index('For method selection,')]+'''These certificates suggest observable diagnostics, not a universally validated routing rule. The implemented hybrid and its unfavorable as well as favorable outcomes are evaluated in Section~\\ref{sec:study59}. The exact tariff theorem, a same-book support witness, and a resource approximation guarantee have different scopes and different checking costs.\n'''
    bib=slice_lines(main,592,650)
    text=pre+intro+core+hard+tariff+section('robustness.tex')+slice_lines(main,382,494)+price+section('study.tex')+bib+slice_lines(main,650,661)+tables(r61)+'\\end{document}\n'
    text=text.replace('electronic_companion}[electronic_companion.pdf]', 'electronic_companion_refs}[electronic_companion.pdf]')
    (ROOT/'main.tex').write_text(text)
    rp=text.split('\\begin{document}')[0];rp=rp[:rp.index('\\externaldocument')]+r'\externaldocument{.build/r63/main_refs}[main.pdf]'+'\n'+r'\externaldocument{.build/r63/electronic_companion_refs}[electronic_companion.pdf]'+'\n'
    (ROOT/'RESPONSE_TO_REFEREES.tex').write_text(rp+'\\begin{document}\n'+section('response_body.tex')+'\n\\end{document}\n')
    ep=slice_lines(ec,1,58).replace('.build/r60/','.build/r63/').replace('--- R60','--- R63')
    ep=ep[:ep.index('This companion contains')]+'''This companion retains the supporting structural theory, exact recovery and approximation proofs, heterogeneous rewards and prototypes, and a nonrenewal application. The current main text concentrates on the tariff-sensitive frontier. Byte-identical earlier readers and all execution evidence are retained in the accompanying archive, with an explicit section map.\n'''
    potential='\\section{Selected-Boundary Extensions}\n'+slice_lines(main,187,229)
    recognized=slice_lines(main,229,263)
    # Retain the repair principle; its later centered recurrence supersedes the older grid presentation.
    grid='\\section{Capacity Repair for the Original Equality}\\label{sec:algorithm52}\n'+slice_lines(ec,403,428)
    et=ep+slice_lines(ec,59,390)+slice_lines(ec,395,401)+potential+recognized+grid+slice_lines(main,520,553)+slice_lines(ec,488,511)+section('implementation.tex')
    eb=ec[ec.index('\\begin{thebibliography}'):ec.index('\\end{thebibliography}')+len('\\end{thebibliography}')]
    et+='\\clearpage\\phantomsection\\label{ec-refs-start}\n'+eb+'\n\\label{ec-refs-end}\\end{document}\n'
    et=et.replace('main}[main.pdf]', 'main_refs}[main.pdf]')
    (ROOT/'electronic_companion.tex').write_text(et)
    # Byte-preserved evidence, never copied back over a source panel.
    for source,dest in ((r60,ROOT/'evidence/r60'),(r61,ROOT/'evidence/r61')):
      if not dest.exists():shutil.copytree(source,dest,ignore=shutil.ignore_patterns('.build','__pycache__','*.png'))
    for name in ('main.tex','main.pdf','electronic_companion.tex','electronic_companion.pdf','RESPONSE_TO_REFEREES.tex','RESPONSE_TO_REFEREES.pdf'):
      dst=ROOT/'archive/r60'/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r60/name,dst)
    (ROOT/'generated').mkdir(exist_ok=True)
    for p in (r60/'generated').glob('*'):
      if p.is_file():shutil.copy2(p,ROOT/'generated'/p.name)
    for p in (r61/'code').glob('*.py'):
      if not (ROOT/'code'/p.name).exists():shutil.copy2(p,ROOT/'code'/p.name)
    defs=set(re.findall(r'\\label\{([^}]+)\}',text+et));refs=set(re.findall(r'\\(?:ref|eqref)\{([^}]+)\}',text+et))
    missing=sorted(refs-defs);assert not missing,missing
    report={'status':'PASS','abstract_words':len(abstract.split()),'reviewed_source_sha256':expected,
       'main_source_sha256':sha(ROOT/'main.tex'),'companion_source_sha256':sha(ROOT/'electronic_companion.tex'),
       'references_resolved':len(refs),'historical_rows_unchanged':sha(r61/'results/ALL_RUNS.csv')==sha(ROOT/'evidence/r61/results/ALL_RUNS.csv')}
    (ROOT/'results/ASSEMBLY63.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--r60',type=Path,required=True);p.add_argument('--r61',type=Path,required=True);a=p.parse_args();build(a.r60,a.r61)
