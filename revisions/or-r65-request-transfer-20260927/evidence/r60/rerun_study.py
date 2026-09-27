from pathlib import Path
import argparse,shutil,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();dest=Path(a.output).resolve();root=Path(__file__).resolve().parent
if dest.exists() and any(dest.iterdir()):raise SystemExit('Output directory must be empty; recorded evidence is immutable.')
dest.mkdir(parents=True,exist_ok=True);shutil.copytree(root/'code',dest/'code');shutil.copyfile(root/'requirements.txt',dest/'requirements.txt')
(dest/'results').mkdir();(dest/'generated').mkdir()
subprocess.run([sys.executable,str(dest/'code/study60.py'),'freeze','run','verify'],cwd=dest,check=True)
print('New execution only:',dest)
