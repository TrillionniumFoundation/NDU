"""Untimed mathematical replay of nine completed exact searches.

Instrumentation is by wrappers; the published optimizer is unchanged. These
are not replacement timing observations and not new independent instances.
"""
from pathlib import Path
from itertools import combinations
import json,datetime,time
import price_path as core
from rational import F,write,encode,digest
from check_price import check_policy
HERE=Path(__file__).resolve().parent;OUT=HERE.parent/'results'

def main():
    cases=[x for x in json.loads((OUT/'EXTENDED_CASES.json').read_text()) if x['family']=='exact_extension' and x['seconds']==2.0]
    write(HERE.parent/'MECHANICS_REPLAY_PROTOCOL.json',dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Post-study deterministic mechanical replay, not a timing replacement. Compare forward search-selected original fixed books with lexicographic enumeration at the same number of distinct fixed-book evaluations; an oracle call is not treated as equal work to a fixed-book evaluation.',cases=[x['id'] for x in cases]))
    rows=[]
    for case in cases:
        orig_run=core.Oracle.run;orig_allocate=core.allocate;calls=[];books={}
        def trace_run(self,lam,required=frozenset(),forbidden=frozenset()):
            out=orig_run(self,lam,required,forbidden)
            calls.append(dict(price=lam,required=sorted(required),forbidden=sorted(forbidden),result=out))
            return out
        def trace_allocate(d,book,B,charges):
            out=orig_allocate(d,book,B,charges);books[tuple(book)]=out['value'];return out
        core.Oracle.run=trace_run;core.allocate=trace_allocate
        try:ans=core.solve(case['spec'],epsilon=0,seconds=None,max_nodes=100000)
        finally:core.Oracle.run=orig_run;core.allocate=orig_allocate
        original=json.loads((OUT/'runs'/(case['id']+'--price.json')).read_text())
        same=(ans['nodes']==original['nodes'] and ans['oracle_calls']==original['oracle_calls'] and ans['lower']==F(original['lower']) and ans['upper']==F(original['upper']))
        if not same:raise ArithmeticError('Replay changed exact search mechanics')
        d,a,rho,B,m=core.normalize(case['spec']);count=0;best=None
        for ell in range(1,m+1):
            for ids in combinations(range(len(a)),ell):
                if a[ids[0]]>min(B,min(d.caps)):continue
                pol=orig_allocate(d,tuple(a[i] for i in ids),B,dict(zip(a,rho)));count+=1
                if best is None or pol['value']>best['value']:best=pol
                if count==len(books):break
            if count==len(books):break
        check_policy(case['spec'],encode(best));check_policy(case['spec'],ans['certificate']['policy'])
        rows.append(dict(id=case['id'],instance_sha256=case['instance_sha256'],mechanics_match_published=True,nodes=ans['nodes'],oracle_calls=ans['oracle_calls'],unique_fixed_books=len(books),enumeration_books=count,price_value=ans['lower'],matched_enumeration_value=best['value'],difference=ans['lower']-best['value'],enumeration_policy=best,price_policy=ans['certificate']['policy'],oracle_trace=calls,book_values=[dict(book=b,value=v) for b,v in books.items()]))
    write(OUT/'MECHANICS_REPLAY.json',rows);print('PASS',len(rows),'mechanical replays')
if __name__=='__main__':main()
