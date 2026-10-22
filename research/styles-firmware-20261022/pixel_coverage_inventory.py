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
    'airyFilter':'reused leaf; outer cast connection not numerically covered',
    'contrastFilter':'reused leaf; outer cast connection not numerically covered',
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
        edges.append({'main_SSA_result':int(ssa),'helper':label,'symbol':name,'function_text_sha256':hashlib.sha256(body.encode()).hexdigest(),'coverage':MAPPED.get(label,'pixel algorithm/connection not modeled in this task'),'source_line':source.count('\n',0,source.index(body))+1})
    return {'reference':{'hardware_model':'iPhone17,3','OS_build':'24A446','internal_bundle_class':'SmartStyleV1 / CMISmartStyleProcessorV1','IMG_2810_exact_capture_build':'unknown; separate identity'},'main_function_sha256':hashlib.sha256(main[1].encode()).hexdigest(),'direct_pixel_calls':edges,'precomputed_semantic_block290':{'conditional_model':'explicit post-guided-filter texture6/7 inputs; accepted isolated 27-call host check','remaining_producer':'createLTMGainMap AIR7 and guided filter numerics not reproduced; original textures required to replay a frame'},'known_numeric_limits':['24 all-active helper calls have set-domain unknowns; point checks do not remove them','RichSat black normalization is unknown','2u/4u and host sampler are assumptions, not measured GPU error','nine unresolved fields retain unknown consumers; no repeated 215-header scan'],'scope':'Function boundaries only. Shared algorithms are reused; missing outer calls remain work, not hardware blockers.','GPU_executed':False,'full_pipeline_verified':False,'private_media_inputs':0,'new_download_bytes':0}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    a.output.write_text(json.dumps(inventory(a.source.read_text()),indent=2)+'\n')
