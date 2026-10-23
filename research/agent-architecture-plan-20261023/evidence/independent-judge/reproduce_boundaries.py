"""Reproduce two cached-state identity failures without editing either candidate."""
from dataclasses import asdict
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
PLAN=HERE.parents[1]
CANDIDATES=PLAN/'prototypes'
BASE='611ac4f6fe525ad3ba80ba5025aa8b5f0a45a079'
INITIAL_CANDIDATE_COMMIT='bc00b741219e7b9bced7dd9cf1d1cf6d38cd918d'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def command(argv, cwd, log):
    p=subprocess.run(argv,cwd=cwd,text=True,capture_output=True,timeout=120,
                     env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'})
    log.write_text(p.stdout+p.stderr)
    if p.returncode:raise RuntimeError(f'Probe exit {p.returncode}; see {log}')
    return {'command':list(map(str,argv)),'exit_code':p.returncode,'log_sha256':sha(log)}


def a_probe(output):
    output.mkdir()
    with tempfile.TemporaryDirectory(prefix='architecture-judge-a-') as folder:
        copied=Path(folder)/'repo';copied.mkdir()
        files=subprocess.check_output(['git','ls-tree','-rz','--name-only',BASE],cwd=REPO).split(b'\0')
        selected=[p.decode() for p in files if p and p.decode().endswith('.py') and
                  any(p.decode().startswith(root) for root in ['research/styles-firmware-20261022/','research/semantic-styles/','research/hdr-native/'])]
        source_hashes={}
        for name in selected:
            target=copied/name;target.parent.mkdir(parents=True,exist_ok=True)
            data=subprocess.check_output(['git','show',BASE+':'+name],cwd=REPO)
            target.write_bytes(data);source_hashes[name]=hashlib.sha256(data).hexdigest()
        input_file=Path(folder)/'context.json'
        input_file.write_bytes(subprocess.check_output(['git','show',BASE+':research/styles-firmware-20261022/evidence/complete-context-s15a.json'],cwd=REPO))
        subprocess.run(['git','init','-q',str(copied)],check=True)
        subprocess.run(['git','-C',str(copied),'add','.'],check=True)
        subprocess.run(['git','-C',str(copied),'-c','user.name=Identity probe','-c','user.email=probe@example.invalid','commit','-qm','Copy public baseline Python sources for isolated cache probe'],check=True)
        commands=[]
        for mode in ('cached','fresh'):
            argv=[sys.executable,str(HERE/'cache_worker.py'),str(CANDIDATES/'candidate_package'),str(copied),str(input_file),str(output/mode),mode]
            commands.append(command(argv,REPO,output/(mode+'.log')))
        cached=json.loads((output/'cached/probe-result.json').read_text())
        fresh=json.loads((output/'fresh/probe-result.json').read_text())
        import numpy as np
        x=np.load(output/'cached/writer.npy');y=np.load(output/'fresh/writer.npy')
        delta=np.abs(x.astype('f8')-y.astype('f8'))
        result={'probe':'A imports backend, edits helper before preparation, hashes edited disk, compares cached execution with fresh process',
                'baseline_sources_copied_from':BASE,'copied_python_files':len(selected),
                'copied_source_manifest_sha256':hashlib.sha256(json.dumps(source_hashes,sort_keys=True).encode()).hexdigest(),
                'candidate_sources':{p.name:sha(p)for p in sorted((CANDIDATES/'candidate_package').glob('*.py'))},
                'method_commands':commands,'run_count':2,'cached':cached,'fresh':fresh,
                'same_bound_helper_sha256':cached['bound_helper_sha256']==fresh['bound_helper_sha256'],
                'same_full_bound_source_snapshot':cached['source_snapshot_sha256']==fresh['source_snapshot_sha256'],
                'same_input_sha256':cached['context_sha256']==fresh['context_sha256'],
                'both_accepted':cached['outcome']==fresh['outcome']=='RenderedModel',
                'writer_half_bit_mismatches':int(np.count_nonzero(x.view('u2')!=y.view('u2'))),
                'max_abs_writer_difference':float(delta.max()),
                'native_calls':0,'production_or_candidate_sources_modified':False,
                'verdict':'ISSUES: disk hashes do not bind imported bytecode in a long-lived process'}
        assert result['same_full_bound_source_snapshot'] and result['same_input_sha256'] and result['both_accepted'] and result['writer_half_bit_mismatches']>0
        (output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
        return result


def b_probe(output):
    output.mkdir()
    sys.path.insert(0,str(CANDIDATES/'candidate_registry'))
    from coordinator import Coordinator, Intent
    registry=output/'registry.json';registry.write_bytes((CANDIDATES/'candidate_registry/registry.json').read_bytes())
    input_file=output/'input.json';input_file.write_text(json.dumps({'pattern':'colors','height':2,'width':2,'field3':0,'selection':'context'}))
    stale=Coordinator(REPO,registry)
    before=sha(registry);data=json.loads(registry.read_text());data['capabilities']['portable-image']['availability']='prepared-only';registry.write_text(json.dumps(data,indent=2)+'\n')
    stale_request=stale.prepare('portable-image',Intent.PORTABLE_MODEL,input_file,output/'cached')
    old=stale.run(stale_request)
    fresh=Coordinator(REPO,registry)
    fresh_request=fresh.prepare('portable-image',Intent.PORTABLE_MODEL,input_file,output/'fresh')
    new=fresh.run(fresh_request)
    key=str(registry.relative_to(REPO))
    result={'probe':'B existing coordinator before policy file edit versus new coordinator on same current disk registry',
            'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
            'candidate_source_sha256':sha(CANDIDATES/'candidate_registry/coordinator.py'),
            'registry_before_sha256':before,'registry_after_sha256':sha(registry),
            'cached_status':old.status,'fresh_status':new.status,
            'cached_bound_registry_sha256':dict(stale_request.source_snapshot)[key],
            'fresh_bound_registry_sha256':dict(fresh_request.source_snapshot)[key],
            'same_bound_registry':dict(stale_request.source_snapshot)[key]==dict(fresh_request.source_snapshot)[key]==sha(registry),
            'cached_reason':old.reason,'fresh_reason':new.reason,
            'run_count':2,'actual_CLI_invocations':1,'native_calls':0,'production_or_candidate_sources_modified':False,
            'verdict':'ISSUES: new disk registry bytes are bound to old in-memory capability policy'}
    assert old.status=='model_only' and new.status=='blocked' and result['same_bound_registry']
    (output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def freeze_candidates(output, commit):
    target=output/'frozen-candidates'
    prefix=str((PLAN/'prototypes').relative_to(REPO))+'/'
    names=subprocess.check_output(['git','ls-tree','-rz','--name-only',commit],cwd=REPO).split(b'\0')
    manifest={}
    for value in names:
        name=value.decode()
        if not name.startswith(prefix) or not name.endswith(('.py','registry.json')):continue
        relative=name[len(prefix):]
        if relative.split('/')[0] not in ('candidate_package','candidate_registry'):continue
        destination=target/relative;destination.parent.mkdir(parents=True,exist_ok=True)
        data=subprocess.check_output(['git','show',commit+':'+name],cwd=REPO)
        destination.write_bytes(data);manifest[relative]=hashlib.sha256(data).hexdigest()
    if not manifest:raise ValueError('No candidate source found at requested commit')
    (output/'frozen-candidate-manifest.json').write_text(json.dumps({'commit':commit,'sources':manifest},indent=2)+'\n')
    return target


def main(output, candidate_commit):
    global CANDIDATES
    output=output.resolve()
    if not output.is_relative_to(REPO):raise ValueError('Registry-copy probe output must be inside this checkout')
    output.mkdir(parents=True,exist_ok=False)
    CANDIDATES=freeze_candidates(output,candidate_commit)
    result={'A':a_probe(output/'candidate-a-cache'),'B':b_probe(output/'candidate-b-cache'),
            'candidate_commit':candidate_commit,
            'adaptation':'Independent inherited-model judge. No cross-model diversity claim.',
            'native_calls':0,'recommended_unmodified_candidate':None}
    (output/'boundary-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v['verdict']for k,v in result.items()if k in ('A','B')},indent=2))

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path,help='new directory inside this checkout')
    parser.add_argument('--candidate-commit',default=INITIAL_CANDIDATE_COMMIT)
    args=parser.parse_args()
    main(args.output,args.candidate_commit)
