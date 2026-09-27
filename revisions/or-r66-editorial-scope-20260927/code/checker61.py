"""Fresh-process verification: peak memory excludes retained optimizer tables."""
import time
START=time.perf_counter()
from pathlib import Path
import gzip,json,resource,sys,traceback
from worker61 import check
from rational import write

def main():
    dest=Path(sys.argv[2])
    try:
        c=json.loads(gzip.decompress(Path(sys.argv[1]).read_bytes()))
        spec=c.get('spec',c.get('instance'));tick=time.perf_counter();ans=check(c,spec)
        ans.update(checking_seconds=time.perf_counter()-tick,process_seconds=time.perf_counter()-START,
            peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        write(dest,ans)
    except Exception as e:
        write(dest,dict(status='FAIL',error=repr(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
