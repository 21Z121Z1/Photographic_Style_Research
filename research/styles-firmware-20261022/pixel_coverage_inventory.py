"""Hash and classify direct AIR10 pixel-call boundaries without exporting AIR.

This is an inventory of this task's numerical coverage, not a scan claiming
that absent consumers or the nine unresolved fields are unused.
"""
import argparse,hashlib,json,re
from pathlib import Path
from native_semantic_tone_check import fragment
from leaf_host import short


MAPPED={
    'renderSemanticToneAdjustments':'fallback semantic model; accepted isolated host check',
    'renderBGAdjustments':'S20 saved S14C case0 BG set produced, width13548.88; broad conditional coverage is not runtime/numeric accuracy',
    'renderFGAdjustments':'all leaf algorithms; S20 saved S14C case0 next fails at FG contrast with half amount0.02000427, outside admitted BG contrast domain',
    'RichSat':'reused leaf; actual outer355..392 color/boost/person mixing connected inS14C, known point domains only; black/whole-set unknowns retained',
    'smoothSatFilter':'S20 source-checked f32/half neutral raw-color0 path carries shared RGB/Lab roots and roundtrip displacement through392; other gains retain old model',
    'airyFilter':'reused leaf and outer tonal/BW root; finite host domains and unknowns retained',
    'contrastFilter':'S19 guarded BG cell0/sorted7/exact saved-parent cover retained; S20 saved S14C case0 advances through BG whites then fails at FG contrast amount0.02000427; no complete-set accuracy claim',
    'applySemanticSRL':'AIR7 complete helper model; targeted AIR10 text equality except attribute group IDs; caller connection still explicit',
    'linearFromCurved':'raw transfer branches; code3 reuses existing decode; specialized code8 selected zero-divisor unknown',
    'curvedFromLinear':'raw output transfer branches; connected568..600 with explicit gain/CCM',
    'renderSkinAdjustments':'reused legacy skin with this AIR precision contract; known point differences/black domain retained',
    'highlightRecover':'complete helper conditional model; black/HDR domain unknown retained',
    'renderBrightAndContrast':'complete conditional helper; S17 saved context point residuals0 under scoped CPU half-FMA contract; other domains and set unknowns retained',
    'renderNeutralizingAdjustments':'complete current caller model using full cast and supplied stats',
    'renderWarmthCastAdjustments':'complete conditional root; unproved negative pow sets retained',
    'renderSelectiveColorAdjustments':'S20 shared RGB relation reaches neutral selective in all12 frozen pixels; RGB110 excluded upstream, other negative outer bases retain12 pow unknowns',
    'renderBWAdjustmentsByCastType':'actual BW477 root computed; independent stark/tonal observations and zero-domain unknowns',
    'renderVideoHazeCorrection':'complete eight-field root; original guide211, independent internal unknown and main501 gate',
    'renderChannelMixForBWCasts':'complete raw-code root plus actual stats-derived weights; cast15 black0/0 unknown',
    'protectMaskFilter':'shared protect helper reused; mainSSA502..566 true-ignore-chroma path covered by S12-D, finite supplied-context host/set domains only',
}


def inventory(source):
    fragment(source)  # Verify the exact canonical AIR10 reference first.
    definitions={m[1]:m[0]for m in re.finditer(r'^define[^\n]*?@([^ (]+)\([^\n]+\{\n.*?^}',source,re.M|re.S)}
    main=next((n,b)for n,b in definitions.items()if n=='renderFinalAdjustments')
    edges=[]
    for m in re.finditer(r'^  %(\d+) = .*?call[^\n]*?@([^ (]+)\([^\n]+',main[1],re.M):
        ssa,name=m.groups()
        if name not in definitions:continue
        body=definitions[name];label=short(name)
        if 'linearFromCurved'in name:label='linearFromCurved'
        elif 'curvedFromLinear'in name:label='curvedFromLinear'
        edge={'main_SSA_result':int(ssa),'helper':label,'symbol':name,'function_text_sha256':hashlib.sha256(body.encode()).hexdigest(),'coverage':MAPPED.get(label,'pixel algorithm/connection not modeled in this task'),'source_line':source.count('\n',0,source.index(body))+1}
        if int(ssa)==557 and label=='protectMaskFilter':edge['coverage_evidence']={'report':'PROGRESS-S12-D.zh-CN.md','host_receipt':'evidence/native-postprotect-s12d.json','current_model_replay':'evidence/postprotect-replay-s12d.json','main_region':'502..566','ignore_chroma':True,'new_native_calls':0}
        edges.append(edge)
    return {
        'reference':{'hardware_model':'iPhone17,3','OS_build':'24A446','internal_bundle_class':'SmartStyleV1 / CMISmartStyleProcessorV1','IMG_2810_exact_capture_build':'unknown; separate identity'},
        'main_function_sha256':hashlib.sha256(main[1].encode()).hexdigest(),
        'direct_pixel_calls':edges,
        'precomputed_semantic_block290':{
            'conditional_model':'source2D -> complete original AIR7 -> original guided3 -> original block290 ROI composition, S14-B two new finite synthetic fixtures,6consumer calls',
            'producer_now_modeled':'selected source/linear/matte normalized coordinates, RGBA16 gain storage and alpha, SRL/transfer/CCM/gain/GTC/ratio, both producer write paths, guided3 and ROI5/6 set sampling',
            'static_contract':'gain maps RGBA16Float115; actual epsilon f32.001 from0x1d44e3d78; original guide self20 distinct from selected primary override',
            'remaining_connection':'source/guide/CCM/stats/ROI/frame identity remain explicit; cast2 mutation covered separately inS14C, not inS14B producer composition; original GPU sampler accuracy not established'},
        'main_prefix_through392':{'known_complete_point_contexts':4,'unknown_point_contexts':1,'unknown_whole_set_contexts':5,'17_independent_observations':'175 known half components bit0, post-semantic35f32 bit0','report':'PROGRESS-S14-C.zh-CN.md'},
        'final_writer':{'conditional_model':'supplied RGB600 to original RGBA pack/ROI direct or phased imageblock copy, explicit RGBA16 storage only','tests':'S14D seven new tiles; three saved witnesses after diagnostic memory-summary widening; invalid phase rejected','report':'PROGRESS-S14-D.zh-CN.md','original_GPU_or_multithreaded_imageblock':False},
        'complete_conditional_forward':{
            'report':'PROGRESS-S20.zh-CN.md','fixture':'evidence/complete-context-s15a.json','host_receipt':'evidence/native-complete-s15a.json','current_replay':'evidence/shared-color-s20b.json',
            'actual_chain':'same raw synthetic3x4 context: AIR7 -> guided -> complete original main ->600 -> direct writer',
            'strict_scope':'cast0 / tuning2 / neutralBGFG / zero lookup; one saved synthetic context',
            'historical_S15_original_calls':102,'additional_S16_diagnostic_main_calls':6,'additional_S17_diagnostic_main_calls':2,
            'point_model':'1938 saved half components bit0 after scoped CPU half-FMA149 correction; not1938 independent cases',
            'whole_sets':'S20 all12 remain unknown atselective413,24 unselected internal unknowns; saturated width.74512 and392/warm.66693; RGB110 excluded but converted min lower-.192871; no writer set',
            'auxiliary_producers':'guide8/9,person/skin/sky,statistics,lookup,curves,34cast/coefficients and input identity remain explicit'},
        'local_enclosures':{
            'neutral_selective':'S20 complete propagation uses joint RGB/LMS/root and original mix half errors; no observed warm substitution; all12 other negative-base domains remain unknown',
            'BG_contrast':'S19 admitted64 parent cover retained, width9483; S20 whites proves original product then quotient finite under supplied zero-origin curve contract, moves S14C failure to FG contrast'},
        'complete_active_color':{
            'report':'PROGRESS-S21.zh-CN.md','raw_control':'post-scene f32 SSRParams.color field3 byte12; UI mapping unverified',
            'strict_scope':'same frozen3x4 raw source/auxiliary context,cast0/tuning2,other coefficients/lookup fixed; color values0,.01,.02,.3,next-f32(.3)',
            'native_receipt':'evidence/native-active-s21c.json','analysis':'evidence/active-analysis-s21d.json',
            'raw_contexts':5,'original_kernel_calls':510,'point_half_components_per_context':1938,'point_half_bit_mismatches':0,
            'observed_vs_plain_writer_half_bit_mismatches':0,'active_point3_effect':'36 saturated/392 components and35 final RGB half components differ from raw0; writer max difference.0078125',
            'nonidentifiability':'distinct half controls.01/.02 have same writer; raw.3 f32 preimage has8191 values under IEEE conversion; conditional interface intervals, no unique inverse',
            'optional_shared_semantic':'precomputed335 to FG354 width.57839683->.09057617; default backend unchanged',
            'active_sets':'all12 fail atRichSat rescaled power mean including0; not proven reachable, no writer set',
            'original_GPU_or_photo_inverse_verified':False},
        'bounded_color_inverse':{
            'report':'PROGRESS-S22.zh-CN.md','control':'internal post-scene raw f32 field3 byte12; known frozen source and auxiliary context',
            'domain':'canonical+0 through3/8,1052770305 f32 bit patterns; negative zero and larger nonnegative controls unsearched',
            'half_cells':13825,'compressed_interface_states':146,'fresh_complete_point_model_evaluations':146,'missing_or_unknown_states':0,
            'platform_candidate':'[0,.02210235595703125],1018499073 f32 values; two separate interface states',
            'point3_candidate':'(.2989501953125,.3006591796875),57343 f32 values; includes old open8191-f32 half cell',
            'query_API':'query_color_inverse.py solve accepts explicit known-context uint16 writer bits; no nearest/unique fallback',
            'native_boundary_controls':8,'new_original_kernel_calls':270,'original_host_states_with_any_finite_witness':'0,1,2,92,93,94 of146; not exhaustive original-host domain acceptance',
            'receipt':'evidence/inverse-audit-s22e.json','not_verified':'unknown source,UI,original GPU,outside finite domain; RichSat whole-set unknown retained'},
        'latest_stage':{'report':'PROGRESS-S22.zh-CN.md','inverse':'evidence/color-inverse-s22c.json','reusable_queries':['evidence/query-platform-s22e.json','evidence/query-point3-s22e.json'],'native_boundaries':'evidence/native-boundaries-s22d.json','pre_run_test_binding':'evidence/test-binding-s22f.pre.json','new_original_host_calls':270,'new_controls_not_call_count':8,'complete_finite_model_search':True,'original_host_all146_states_verified':False},
        'unfinished_software_tracking':{
            'receipt':'evidence/consumer-paths-s18c.json','consumer_slots':9,
            'hardware_wait_required_to_continue_static_tracking':False,
            'scope':'S18 paths and missing CPU image/method/binding restoration list retained; S19 bridge paused, no new search/download/mount; nine consumers remain unfinished software work'},
        'main_remaining_connections':[
            'original iOS/GPU and same-frame chain unverified; finite synthetic conditional point chain is connected through writer',
            '12 selective pow domains, unselected internal domains and wider pre393 BG/FG set domains remain software work',
            'S21 active color point chain accepted only in five fixed contexts; active sets stop atRichSat rescaled-power mean zero-domain outer enclosure',
            'S20 saved S14C case0 produces broad BG set, then FG contrast quotient finite-budget unknown; no whole-runtime or originalGPU acceptance',
            'other output pixel encodings and original multi-thread GPU behavior are unverified'],
        'known_numeric_limits':[
            '24 old all-active helper set unknowns and old8 leaf-domain unknowns retained without rerun',
            'saved context point1938 bit0 does not remove historical point differences in other contexts',
            'cast15 black0/0, transfer8 selected zero divisor, black HDR gain remain unknown',
            'old155.125 and17941.5513 envelopes retained as historical evidence, not accuracy',
            'S14B five guided mismatches diagnosed in S15B/S16; saved fixture replays bit0 do not prove GPU order',
            'S16 diagnostic48 positive domains remain historical; S19 default64 boxes and sorted42 positive/42else are distinct counts, no new independent host cases',
            'S19 local observed-input exclusion remains separate; S20 complete upstream boxes exclude RGB110 but12 other converted-negative outer domains remain unproved',
            '2u/4u, host math and sampler are assumptions, not measured GPU error',
            'nine unresolved coefficient consumers are unfinished software tracking; no repeated same-range scan'],
        'scope':'S22 bounded known-source raw-color inverse returns equivalent candidate sets; exhaustive finite MODEL catalog, partial original-host boundaries; old set failures,S19 audit limitation and GPU/unknown-source inverse gaps retained.',
        'GPU_executed':False,'full_pipeline_verified':False,'private_media_inputs':0,'new_download_bytes':0}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    a.output.write_text(json.dumps(inventory(a.source.read_text()),indent=2)+'\n')
