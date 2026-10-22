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
    'renderBGAdjustments':'all leaf algorithms; fixed-field host and conditional set coverage only',
    'renderFGAdjustments':'all leaf algorithms; fixed-field host and conditional set coverage only',
    'RichSat':'reused leaf; actual outer355..392 color/boost/person mixing connected inS14C, known point domains only; black/whole-set unknowns retained',
    'smoothSatFilter':'reused leaf; actual nonpositive outer355..392 branch and person mixing connected inS14C; no complete-set claim',
    'airyFilter':'reused leaf and outer tonal/BW root; finite host domains and unknowns retained',
    'contrastFilter':'original graph plus S18 default set fallback only within savedcell0 bounds/exact half parameter; saved64 unknown8->7; whole S14C case0 remains unknown',
    'applySemanticSRL':'AIR7 complete helper model; targeted AIR10 text equality except attribute group IDs; caller connection still explicit',
    'linearFromCurved':'raw transfer branches; code3 reuses existing decode; specialized code8 selected zero-divisor unknown',
    'curvedFromLinear':'raw output transfer branches; connected568..600 with explicit gain/CCM',
    'renderSkinAdjustments':'reused legacy skin with this AIR precision contract; known point differences/black domain retained',
    'highlightRecover':'complete helper conditional model; black/HDR domain unknown retained',
    'renderBrightAndContrast':'complete conditional helper; S17 saved context point residuals0 under scoped CPU half-FMA contract; other domains and set unknowns retained',
    'renderNeutralizingAdjustments':'complete current caller model using full cast and supplied stats',
    'renderWarmthCastAdjustments':'complete conditional root; unproved negative pow sets retained',
    'renderSelectiveColorAdjustments':'conditional root using explicit lookup; S17 strict neutral joint Lab/inverse/gamma error enclosure; negative outer pow domains still unknown',
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
            'report':'PROGRESS-S17.zh-CN.md','fixture':'evidence/complete-context-s15a.json','host_receipt':'evidence/native-complete-s15a.json','current_replay':'evidence/selective-replay-s17a.json',
            'actual_chain':'same raw synthetic3x4 context: AIR7 -> guided -> complete original main ->600 -> direct writer',
            'strict_scope':'cast0 / tuning2 / neutralBGFG / zero lookup; one saved synthetic context',
            'historical_S15_original_calls':102,'additional_S16_diagnostic_main_calls':6,'additional_S17_diagnostic_main_calls':2,
            'point_model':'1938 saved half components bit0 after scoped CPU half-FMA149 correction; not1938 independent cases',
            'whole_sets':'12 pixels still unknown atselective413; known preceding ranges covered, warm width1.73493; converted joint width1.88428,gamma1; no writer set output',
            'auxiliary_producers':'guide8/9,person/skin/sky,statistics,lookup,curves,34cast/coefficients and input identity remain explicit'},
        'local_enclosures':{
            'neutral_selective':'S17 strict neutral joint error enclosure; S18 full-clamp-domain original host prefix witness has negative B; no pow1 simplification or originalGPU reachability claim',
            'BG_cell0':'S17 bound now wired into default contrast sets within savedcell0/exact half parameter only; width1.680803; S18 saved64 unknown7 and full S14C case0 still contrast unknown'},
        'latest_stage':{'report':'PROGRESS-S18.zh-CN.md','default_BG_replay':'evidence/bg-default-replay-s18a.json','original_prefix_domain_witness':'evidence/selective-domain-s18b.json','additional_original_host_prefix_calls':1,'post_negative_base_pow_executed':False},
        'unfinished_software_tracking':{
            'receipt':'evidence/consumer-paths-s18c.json','consumer_slots':9,
            'hardware_wait_required_to_continue_static_tracking':False,
            'scope':'S18 AIR13 recursive parameter-origin analysis and two CPU blit windows; no target reads in this bounded closure; CPU proxy bridge unextracted because owned SystemOS image is absent; other consumers remain software work'},
        'main_remaining_connections':[
            'original iOS/GPU and same-frame chain unverified; finite synthetic conditional point chain is connected through writer',
            '12 selective pow domains, unselected internal domains and wider pre393 BG/FG set domains remain software work',
            'S18 cell0 admitted by default contrast, seven of saved64 still unknown and whole S14C case0 fails before completeBG; no originalGPU acceptance',
            'other output pixel encodings and original multi-thread GPU behavior are unverified'],
        'known_numeric_limits':[
            '24 old all-active helper set unknowns and old8 leaf-domain unknowns retained without rerun',
            'saved context point1938 bit0 does not remove historical point differences in other contexts',
            'cast15 black0/0, transfer8 selected zero divisor, black HDR gain remain unknown',
            'old155.125 and17941.5513 envelopes retained as historical evidence, not accuracy',
            'S14B five guided mismatches diagnosed in S15B/S16; saved fixture replays bit0 do not prove GPU order',
            'S14C/S16 cell0 failure receipts retained; S18 default contrast admits exact proved cell0 domain, preserving quotient/product order; wholeBG remains unknown',
            '2u/4u, host math and sampler are assumptions, not measured GPU error',
            'nine unresolved coefficient consumers are unfinished software tracking; no repeated same-range scan'],
        'scope':'S18 conditional operator and connection inventory; software work, missing cached CPU bytes and original GPU/frame dependencies are distinct.',
        'GPU_executed':False,'full_pipeline_verified':False,'private_media_inputs':0,'new_download_bytes':0}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    a.output.write_text(json.dumps(inventory(a.source.read_text()),indent=2)+'\n')
