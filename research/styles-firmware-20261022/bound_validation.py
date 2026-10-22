"""Bind exact source/input hashes before a new bounded validation command."""
import argparse,hashlib,json,subprocess,time
from pathlib import Path


def run(label,output,command):
    if not command:raise ValueError('Explicit validation command required')
    root=Path(__file__).parent;repo=root.parents[1];pre=output.with_name(output.stem+'.pre.json');log=output.with_name(output.stem+'.log')
    if any(p.exists()for p in [output,pre,log]):raise FileExistsError('Validation artifacts must not exist')
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();sources={p.name:sha(p)for p in sorted(root.glob('*.py'))};input_names=sorted(set(['complete-context-s15a.json','native-complete-s15a.json','native-main-pre393-s14c.json','bg-dependency-s15c.json','selective-domain-s18b.json']+[p.name for p in (root/'evidence').glob('*s20*.json')]));inputs={n:sha(root/'evidence'/n)for n in input_names}
    start={'label':label,'command':command,'source_sha256_before_execution':sources,'input_sha256_before_execution':inputs,'prior_S19_source_binding_limitation_preserved':True,'wall_clock_before_execution':time.time()};pre.write_text(json.dumps(start,indent=2)+'\n')
    p=subprocess.run(command,cwd=repo,capture_output=True,text=True,timeout=60);log.write_text(p.stdout+p.stderr);after={n:sha(root/n)for n in sources};input_after={n:sha(root/'evidence'/n)for n in inputs};result={'label':label,'pre_run_binding_sha256':sha(pre),'source_unchanged_during_command':sources==after,'inputs_unchanged_during_command':inputs==input_after,'exit_code':p.returncode,'log_sha256':sha(log),'elapsed_seconds':time.time()-start['wall_clock_before_execution'],'native_execution':'only if explicit command requests it; inspect command','command':command};output.write_text(json.dumps(result,indent=2)+'\n');print(p.stdout+p.stderr);print(json.dumps(result))
    if p.returncode or sources!=after or inputs!=input_after:raise RuntimeError('Bound validation failed; all artifacts retained')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('label');p.add_argument('output',type=Path);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args();run(a.label,a.output,a.command)
