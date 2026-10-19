"""Runs inside runner LLDB after the native checkpoint. Missing symbols are data."""
import lldb,os,json,pathlib
root=pathlib.Path(os.environ['W']);ci=lldb.debugger.GetCommandInterpreter()
f=root/'probe/consumer/semantic/s23-original-extra.json'
if f.exists():
 data=json.loads(f.read_text())
 for row in data.get('pipeline_method_addresses',[]):
  print('S23_METHOD '+json.dumps(row,sort_keys=True))
  if row['selector'] in ['initWithDevice:pipelineStateDescriptor:computeVariant:errorMessage:','parseReply:','getComputePipelineStateInfo:']:
   result=lldb.SBCommandReturnObject();ci.HandleCommand('disassemble --start-address '+row['address']+' --count 128',result)
   print(result.GetOutput() or '');print(result.GetError() or '')
else:print('S23 metadata checkpoint file absent')
result=lldb.SBCommandReturnObject();ci.HandleCommand('image list -u',result);print(result.GetOutput() or '');print(result.GetError() or '')
result=lldb.SBCommandReturnObject();ci.HandleCommand('continue',result);print(result.GetOutput() or '');print(result.GetError() or '')
process=lldb.debugger.GetSelectedTarget().GetProcess();print('S23_INFERIOR '+json.dumps({'state':process.GetState(),'exit_status':process.GetExitStatus(),'exit_description':process.GetExitDescription()}))
