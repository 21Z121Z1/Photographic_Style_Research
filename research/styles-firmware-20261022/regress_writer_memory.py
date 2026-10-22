"""Three saved writer witnesses after memory-summary widening, plus phase negative."""
import argparse,ctypes,hashlib,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from output_writer_host import build,C_SOURCE
from native_output_writer_check import fixtures,execute


def check(source,saved,output):
    if output.exists():raise FileExistsError(output)
    original=json.loads(saved.read_text());ir,meta=build(source.read_text());rows=[]
    with tempfile.TemporaryDirectory(prefix='psr-writer-memory-')as t:
        w=Path(t);(w/'source.ll').write_text(ir);(w/'shim.c').write_text(C_SOURCE);c=subprocess.run(['/opt/homebrew/opt/llvm/bin/clang','-target','arm64-apple-macos27.0','-Wno-override-module','-dynamiclib',str(w/'source.ll'),str(w/'shim.c'),'-o',str(w/'writer.dylib')],capture_output=True,text=True,timeout=60)
        if c.returncode:raise RuntimeError(c.stderr[:4000])
        lib=ctypes.CDLL(str(w/'writer.dylib'));all_cases=list(fixtures())
        for index in [0,2,6]:
            name,controls,colors,frame=all_cases[index];prior=original['rows'][index]
            if prior['case']!=name or colors.tolist()!=original['input_tile_colors']or any(tuple(prior[n])!=getattr(controls,n)for n in ['logical_origin','output_offset12','render_edge2'])or prior['imageblock']!=controls.imageblock or not np.all(frame==original['target_initial_value']):raise ValueError('Saved fixture identity changed')
            native,counters,digest,n=execute(lib,controls,colors,frame);same=native.view('u2').tolist()==prior['native_output_half_bits'];row={'case':name,'same_saved_half_bits':same,'counters':counters,'input_digest':digest,'writer_calls':n};rows.append(row)
            if not same or counters['errors']or counters['pixels']!=prior['native_written_pixels']:raise AssertionError('Saved writer witness changed')
        _,controls,colors,frame=all_cases[1];native,counters,digest,n=execute(lib,controls,colors,frame,leader_first=True);negative={'case':'leader-first invalid schedule','host_diagnostic_errors':counters['errors'],'written_pixels':counters['pixels'],'target_unchanged':bool(np.array_equal(native,frame)),'writer_calls':n}
        if not counters['errors']or counters['pixels']or not negative['target_unchanged']:raise AssertionError('Bad phase schedule was not rejected')
    root=Path(__file__).parent;r={'saved_full_receipt_sha256':hashlib.sha256(saved.read_bytes()).hexdigest(),'original':meta,'source_sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest()for n in ['output_writer_host.py','native_output_writer_check.py','regress_writer_memory.py']},'host_IR_sha256':hashlib.sha256(ir.encode()).hexdigest(),'C_sha256':hashlib.sha256(C_SOURCE.encode()).hexdigest(),'saved_witnesses_replayed':3,'old_seven_case_batch_repeated':False,'rows':rows,'invalid_phase_negative':negative,'GPU_executed':False,'arithmetic_FP_flags_or_inputs_changed':False}
    output.write_text(json.dumps(r,indent=2)+'\n');return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('saved',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=check(a.source,a.saved,a.output);print(json.dumps({'saved':r['saved_witnesses_replayed'],'same_bits':all(x['same_saved_half_bits']for x in r['rows']),'negative':r['invalid_phase_negative']}))
