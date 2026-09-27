"""Resume publication from immutable, successful scientific execution evidence.

The first R63 job completed every mathematical check but lacked the generic
TeX binhex dependency. Preserve that execution, repair only the toolchain, and
independently recheck all proofs again on the actual published commit.
"""
from pathlib import Path
import hashlib,json,os,subprocess,sys,zipfile
import yaml

PIN='b8b7d774e1a438cacc64249a2130080c067b571f'
raw=subprocess.check_output(['git','show',PIN+':.github/workflows/ndu-or-r63-publish.yml'])
steps=yaml.safe_load(raw)['jobs']['publish']['steps']
commands={s['name']:s['run'] for s in steps if 'run' in s}
phases={
 'source':'Validate author ancestry and materialize the complete reviewed source payload',
 'artifacts':'Retrieve immutable reviewed source and historical execution artifacts',
 'install':'Install pinned numerical dependencies and manuscript TeX toolchain',
 'regressions':'Re-run inherited and new structural regressions and freeze the new diagnostic',
 'compile':'Assemble the full revision and compile all three readers',
 'publish':'Seal and publish materialized manuscripts, proofs, data, code and preservation map',
 'exact':'Recheck the exact published commit without mutating its evidence',
}
phase=sys.argv[1]
if phase=='restore':
    temp=Path(os.environ['RUNNER_TEMP']);archive=temp/'r63-prior-scientific-evidence.zip'
    with archive.open('wb') as out:
        subprocess.run(['gh','api',f"repos/{os.environ['GITHUB_REPOSITORY']}/actions/artifacts/10922570892/zip"],stdout=out,check=True)
    h=hashlib.sha256(archive.read_bytes()).hexdigest()
    assert h=='77f5884632c2504f080345ef868ec0a73a0aff4033ae27cacf5845c2257d304f'
    r=Path(os.environ['REV']);prefix='NDU/NDU/'+str(r)+'/results/'
    with zipfile.ZipFile(archive) as z:
        names=[n for n in z.namelist() if n.startswith(prefix) and not n.endswith('/')]
        assert len(names)==57,len(names)
        for name in names:
            p=r/'results'/name[len(prefix):]
            assert p.resolve().is_relative_to((r/'results').resolve())
            p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(name))
    frozen=json.loads((r/'results/SUPPORT_FREEZE63.json').read_text())
    for name,digest in frozen['source_hashes'].items():
        assert hashlib.sha256((r/'code'/name).read_bytes()).hexdigest()==digest,name
    replay=json.loads((r/'results/BINDING_REPLAY.json').read_text())
    assert replay['status']=='PASS' and replay['certificates']==389 and replay['requests']==405
    recovery={'schema':'NDU-R63-publication-recovery-v1','scientific_execution_run':36290857976,
      'execution_source_commit':PIN,'immutable_artifact_id':10922570892,'artifact_sha256':h,
      'retained_result_files':len(names),'build_failure':'Missing generic TeX dependency binhex.tex',
      'repair':'Install texlive-plain-generic and tex-gyre; no mathematical source changes',
      'scope':'Restore complete successful scientific execution evidence without changing timing or failure outcomes; recheck all 389 historical certificates again on the final published commit.'}
    (r/'results/PUBLICATION_RECOVERY63.json').write_text(json.dumps(recovery,indent=2)+'\n')
    print(json.dumps(recovery,indent=2))
else:
    command=commands[phases[phase]]
    if phase=='install':
        old='texlive-fonts-extra >';assert old in command
        command=command.replace(old,'texlive-fonts-extra texlive-plain-generic tex-gyre >')
        command+='\nkpsewhich binhex.tex\n'
    elif phase=='regressions':
        old='python "$REV/code/support63.py"';assert old in command
        command=command.replace(old,"echo 'Retain immutable R63 root diagnostic, its original freeze, timings and 48 proofs.'")
    subprocess.run(['bash','-e','-o','pipefail','-c',command],check=True)
