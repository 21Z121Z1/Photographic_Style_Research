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
    'RichSat':'reused leaf; outer color coefficient/mixing connection not numerically covered',
    'smoothSatFilter':'reused leaf; outer color coefficient/mixing connection not numerically covered',
    'airyFilter':'reused leaf and outer tonal/BW root; finite host domains and unknowns retained',
    'contrastFilter':'reused leaf and outer tonal/BW root; finite host domains and unknowns retained',
    'applySemanticSRL':'AIR7 complete helper model; targeted AIR10 text equality except attribute group IDs; caller connection still explicit',
    'linearFromCurved':'raw transfer branches; code3 reuses existing decode; specialized code8 selected zero-divisor unknown',
    'curvedFromLinear':'raw output transfer branches; connected568..600 with explicit gain/CCM',
    'renderSkinAdjustments':'reused legacy skin with this AIR precision contract; known point differences/black domain retained',
    'highlightRecover':'complete helper conditional model; black/HDR domain unknown retained',
    'renderBrightAndContrast':'complete conditional helper; bright host differences and set unknowns retained',
    'renderNeutralizingAdjustments':'complete current caller model using full cast and supplied stats',
    'renderWarmthCastAdjustments':'complete conditional root; unproved negative pow sets retained',
    'renderSelectiveColorAdjustments':'conditional root using explicit lookup texture; missing/invalid domains fail closed',
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
    return {'reference':{'hardware_model':'iPhone17,3','OS_build':'24A446','internal_bundle_class':'SmartStyleV1 / CMISmartStyleProcessorV1','IMG_2810_exact_capture_build':'unknown; separate identity'},'main_function_sha256':hashlib.sha256(main[1].encode()).hexdigest(),'direct_pixel_calls':edges,'precomputed_semantic_block290':{'conditional_model':'source2D -> complete original AIR7 -> original guided3 -> original block290 ROI composition, S14-B two new finite synthetic fixtures,6consumer calls','producer_now_modeled':'selected source/linear/matte normalized coordinates, RGBA16 gain storage and alpha, SRL/transfer/CCM/gain/GTC/ratio, both producer write paths, guided3 and ROI5/6 set sampling','static_contract':'gain maps RGBA16Float115; actual epsilon f32.001 from0x1d44e3d78; original guide self20 distinct from selected primary override','remaining_connection':'source/guide/CCM/stats/ROI/frame identity remain explicit; cast2 mutation not included in the new composition; original GPU sampler accuracy not established'},'main_remaining_connections':['early main input/CCM/guide and outer RichSat/smoothSat selections before393 are not a complete composed host verification','full producer-to-consumer-to600 same-frame composition not verified','final imageblock/ROI/texture write not executed'],'known_numeric_limits':['24 all-active helper calls have set-domain unknowns; point checks do not remove them','old8 leaf-domain unknowns retained','bright and earlier tonal/skin/neutralizing point differences retained','cast15 black0/0, transfer8 selected zero divisor, black HDR gain remain unknown','old155.125 image envelope retained; new true-epsilon ROI chain boxes reach17941.5513','five independent guided internal half mismatches, max.0009765625, remain despite final335 bit equality','2u/4u and host sampler are assumptions, not measured GPU error','nine unresolved fields retain unknown consumers; no repeated same-range consumer scan'],'scope':'Updated conditional operator and connection inventory; local model work is distinguished from original GPU/frame dependencies.','GPU_executed':False,'full_pipeline_verified':False,'private_media_inputs':0,'new_download_bytes':0}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    a.output.write_text(json.dumps(inventory(a.source.read_text()),indent=2)+'\n')
