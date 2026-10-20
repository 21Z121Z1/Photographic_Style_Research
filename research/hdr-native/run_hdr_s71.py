"""S71 applies the already-proven S56 stats preparation mask1 to S70.
The failed parent remains immutable; no new curve/shader/crop model changes.
"""
from pathlib import Path
import hashlib,json,os
D=Path('research/hdr-native');W=Path(os.environ['W']);O=W/'out'
s=(D/'probe_matte_roi_s70.m').read_text()
a='unsigned type=2;';assert s.count(a)==1;s=s.replace(a,'unsigned type=1;')
a='Require(pso!=nil&&pso.threadExecutionWidth==32&&pso.maxTotalThreadsPerThreadgroup==1024,@"original PSO properties");'
assert s.count(a)==1
s=s.replace(a,'r[@"original_PSO_properties"]=@{@"present":@(pso!=nil),@"thread_execution_width":@(pso.threadExecutionWidth),@"max_threads":@(pso.maxTotalThreadsPerThreadgroup)};'+a)
target=W/'probe-s71.m';target.write_text(s)
with (O/'derivation-s71.json').open('x')as f:json.dump({'parent':'probe_matte_roi_s70.m','parent_sha256':hashlib.sha256((D/'probe_matte_roi_s70.m').read_bytes()).hexdigest(),'derived_sha256':hashlib.sha256(s.encode()).hexdigest(),'processing_mask':1,'prior_static_evidence':'evidence/s56/prepare-mask-source.txt, original0x23336dc78 bit0 and self+0x4d8','failure_parent_run':39345177157,'failure_parent_ZIP_sha256':'23972244a31f790ae3edaf0b8868e4ff14fab667f4f29f2014ed6cdc35bf241a','changes':'Use S56 proven stats mask1; add PSO diagnostic properties only; frozen inputs, crop cases, predictions and shader unchanged'},f,separators=(',',':'));f.write('\n')
body=(D/'run_hdr_s70.py').read_text();a="str(D/'probe_matte_roi_s70.m'),'-o'";assert body.count(a)==1;body=body.replace(a,"str(target),'-o'")
exec(compile(body,'run_hdr_s70_derived_for_s71.py','exec'))
