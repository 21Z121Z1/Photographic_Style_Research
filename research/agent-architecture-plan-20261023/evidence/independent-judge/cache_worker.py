"""Run the candidate A cache probe in an isolated copied repository."""
import hashlib
import json
from pathlib import Path
import sys

candidate, repo, context, output, mode = map(str, sys.argv[1:])
sys.path.insert(0, candidate)
from execution import Study, Selection, _modules
repo, context, output = Path(repo), Path(context), Path(output)
helper = repo/'research/styles-firmware-20261022/pixel_output.py'
original = hashlib.sha256(helper.read_bytes()).hexdigest()
if mode == 'cached':
    _modules(repo)
    text = helper.read_text()
    needle = '    curved=host_code3(linear)'
    assert text.count(needle) == 1
    helper.write_text(text.replace(needle, '    linear=linear*H(.5,rgb567)\n'+needle))
study = Study.portable(repo, context, selection=Selection.BRIGHT16)
result = study.run(output)
receipt = json.loads((output/'receipt.json').read_text())
record = {'mode':mode,'outcome':type(result).__name__,
          'source_commit_in_copied_repo':receipt['source_commit'],
          'before_helper_sha256':original,
          'after_helper_sha256':hashlib.sha256(helper.read_bytes()).hexdigest(),
          'bound_helper_sha256':receipt['source_sha256']['research/styles-firmware-20261022/pixel_output.py'],
          'source_snapshot_sha256':hashlib.sha256(json.dumps(receipt['source_sha256'],sort_keys=True).encode()).hexdigest(),
          'context_sha256':receipt['input_sha256'],
          'result':receipt['result'],'native_calls':receipt['native_calls_performed']}
(output/'probe-result.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
