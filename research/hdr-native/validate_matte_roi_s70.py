"""Replay small synthetic original-ROI/PSO counts, never a sampler-domain proof.
Run local Python via scripts/local-python-scope.sh. The ZIP stays immutable.
"""
import hashlib,json,math,pathlib,struct,sys,zipfile,runpy

def rn32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def positive_axis(length,mask_length,uv,axis):
    scale,bias=uv[axis],uv[axis+2]
    result=[]
    for x in range(length):
        u=rn32(rn32((x+.5)*scale)+bias)
        texel=u*mask_length-.5
        # Normalized bilinear clamp hypothesis; pure 0/1 step along one axis.
        value=max(0.,min(1.,texel-(mask_length//2-1)))
        half=struct.unpack('<e',struct.pack('<e',value))[0]
        result.append(half>=.25)
    return result

def validate(path):
    with zipfile.ZipFile(path)as z:
        m=json.loads(z.read('manifest.json'))
        assert m['os_build']=='26A434' and m['no_photo_input'] is True
        for f in m['files']:
            b=z.read(f['path']);assert len(b)==f['size'] and hashlib.sha256(b).hexdigest()==f['sha256']
        native=json.loads(z.read('native.json'));freeze=json.loads(z.read('freeze.json'))
    out={'run_id':m['run_id'],'commit':m['commit'],'os_build':m['os_build'],'image_version':m.get('image_version'),'ZIP_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'native_completed':native['completed'],'checkpoint':native.get('checkpoint'),'exception':native.get('exception'),'rows':[],'scope':'Finite synthetic original CPU ROI / original PSO controls only; not C04 all-domain sampling contract or physical scene proof','A_phase_complete':False,'acceptance_complete':False}
    if not native['completed']:return out
    assert len(native['rows'])==7
    base=native['rows'][0]['input_SHA256']
    cpu_uv=runpy.run_path(str(pathlib.Path(__file__).with_name('matte_roi_s71.py')))['full_frame_uv']
    for r in native['rows']:
        assert r['input_SHA256']==base and r['inputs_SHA_unchanged_after_dispatch'] and r['ROI_bytes_outside_target_unchanged']
        assert r['ROI_check_status']==0 and r['hist0_sum']==1024*768
        px=positive_axis(1024,32,r['person_uv'],0);sy=positive_axis(768,24,r['skin_uv'],1)
        pp=[sum(px[32*x:32*x+32])*24 for y in range(32)for x in range(32)]
        sp=[sum(sy[24*y:24*y+24])*32 for y in range(32)for x in range(32)]
        assert len(r['person_counts_32x32'])==len(r['skin_counts_32x32'])==1024
        pt,st=r['person_total'],r['skin_total']
        crop=r.get('crop',[0,0,0,0])
        ep=cpu_uv((1024,768),(32,24),crop if r['target']=='person'else(0,0,0,0))
        es=cpu_uv((1024,768),(32,24),crop if r['target']=='skin'else(0,0,0,0))
        uv_equal=struct.pack('<8f',*(ep+es))==struct.pack('<8f',*(r['person_uv']+r['skin_uv']))
        assert sum(r['person_counts_32x32'])==pt and sum(r['skin_counts_32x32'])==st
        out['rows'].append({'id':r['id'],'native_totals':[pt,st],'frozen_predicted_totals':freeze['predicted_normalized_bilinear_clamp_totals_before_native'][r['id']],'per_cell_max_abs':max(abs(a-b)for a,b in zip(pp+sp,r['person_counts_32x32']+r['skin_counts_32x32'])),'posthoc_actual_ROI_model_totals':[sum(pp),sum(sp)],'frozen_totals_match':[pt,st]==freeze['predicted_normalized_bilinear_clamp_totals_before_native'][r['id']],'post_native_CPU_UV_bit_exact':uv_equal})
    out['all_tested_cells_match']=all(r['per_cell_max_abs']==0 and r['frozen_totals_match']for r in out['rows'])
    out['post_native_CPU_UV_all56_components_bit_exact']=all(r['post_native_CPU_UV_bit_exact']for r in out['rows'])
    out['CPU_UV_implementation_is_post_native_not_new_holdout']=True
    return out
if __name__=='__main__':
    print(json.dumps(validate(pathlib.Path(sys.argv[1])),indent=2,allow_nan=False))
