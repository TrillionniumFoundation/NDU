"""One reproduction entry point. Never pushes, merges, or submits to a journal."""
from pathlib import Path
import argparse
import os
import shutil
import subprocess
import sys

CODE = Path(__file__).resolve().parent
R = CODE.parent
ROOT = R.parents[1]


def command(filename):
    subprocess.run([sys.executable, str(CODE/filename)], cwd=ROOT, check=True,
                   env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})


def snapshot():
    from prepare import snapshot_engines
    snapshot_engines()


def prepare_readers():
    command('prepare.py')
    command('layout.py')
    shutil.copy2(R/'README.md', ROOT/'README.md')
    shutil.copy2(R/'SUBMISSION_CHECKLIST.md', ROOT/'NDU_OR_submission_checklist.md')


def run(stage):
    if stage in ('snapshot', 'verify', 'study', 'all'):
        snapshot()
    if stage in ('verify', 'all'):
        command('test_revision.py')
        command('external_solver.py')
    if stage in ('study', 'all'):
        command('study.py')
    if stage in ('prepare', 'all'):
        prepare_readers()
    if stage in ('build', 'all'):
        command('build.py')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('snapshot', 'verify', 'study', 'prepare', 'build', 'all'))
    args = parser.parse_args()
    run(args.stage)
