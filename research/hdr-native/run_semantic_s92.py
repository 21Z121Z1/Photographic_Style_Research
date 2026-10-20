"""S92: one diagnosed ObjC type fix and fresh transport bindings only."""
from pathlib import Path
import hashlib,json,os

D=Path(__file__).resolve().parent;source=D/'run_semantic_s91.py'
original=source.read_text();expected='58d3f1f6480a5ec44e37d0837c5e944b5c771f6f6b516cb8e2dbf07e6b9670f1'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
replacements=[('inputs_s91.json','inputs_s92.json'),('SEMANTIC_S91_INPUT_SESSION','SEMANTIC_S92_INPUT_SESSION')]
for field in['width','height','pixelFormat']:
    replacements.append((f'[call[@"textures"][@"0"] {field}]',f'((id<MTLTexture>)call[@"textures"][@"0"]).{field}'))
derived=original
counts=[]
for old,new in replacements:
    count=derived.count(old);assert count==1,(old,count)
    derived=derived.replace(old,new);counts.append({'old':old,'new':new,'count':count})
restored=derived
for old,new in reversed(replacements):restored=restored.replace(new,old)
assert restored==original
out=Path(os.environ['W'])/'out'
(out/'S92-derived-driver.txt').write_text(derived)
(out/'S92-binding.json').write_text(json.dumps({'original_source':'research/hdr-native/run_semantic_s91.py','original_source_commit':'c27610d0dd63ca70f6bca4acfe7f9c9068756df5','original_source_SHA256':expected,'derived_source_SHA256':hashlib.sha256(derived.encode()).hexdigest(),'wrapper_source_SHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'exact_replacements':counts,'reverse_changes_equal_original':True,'inverse_solver_or_frozen_model_changed':False,'S91_failure_retained':True},indent=2)+'\n')
exec(compile(derived,'S92-derived-S91-driver','exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
