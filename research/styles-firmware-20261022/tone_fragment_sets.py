"""Set-valued semantic -> BG -> FG fragment, with explicit unresolved leaves.

Only this actual AIR10 helper order is composed. Input RGB already belongs at
the helper call site; outer sampling/color transforms/skin/style are omitted.
"""
from dataclasses import dataclass
from semantic_tone import I,SemanticSetResult
from semantic_caller import runtime_semantic_set,mixed_guide_set
from bgfg_tone import PixelContext,PixelResult,run


@dataclass(frozen=True)
class FragmentResult:
    status: str
    semantic: SemanticSetResult | None
    guide: I | None
    bg: PixelResult | None
    fg: PixelResult | None
    output: I | None
    full_camera_pipeline_verified: bool=False


def forward(inputs,fields,*,cast_type,baseline_exposure,guide_texture8,guide_texture9,skin_weight,texture6_present: bool,texture7_present: bool,leaf_models=None):
    if type(texture6_present)is not bool or type(texture7_present)is not bool:raise ValueError('Explicit presence of both precomputed semantic textures required')
    if texture6_present and texture7_present:
        return FragmentResult('unknown_precomputed_semantic_path',None,None,None,None,None)
    semantic=runtime_semantic_set(inputs,fields,cast_type=cast_type,baseline_exposure=baseline_exposure)
    guide=mixed_guide_set(fields,guide_texture8,guide_texture9,inputs.person_weight,cast_type=cast_type,baseline_exposure=baseline_exposure)
    context=PixelContext(guide,inputs.person_weight,skin_weight);rgb=I(semantic.lower,semantic.upper)
    if guide.lo<0 or guide.hi>1:return FragmentResult('unknown_guide_domain',semantic,guide,None,None,None)
    bg=run('bg',rgb,fields,context,leaf_models=leaf_models)
    if bg.output is None:return FragmentResult('unknown_BG_operator',semantic,guide,bg,None,None)
    fg=run('fg',bg.output,fields,context,semantic_rgb=rgb,leaf_models=leaf_models)
    return FragmentResult('computed_fragment_set'if fg.output is not None else 'unknown_FG_operator',semantic,guide,bg,fg,fg.output)
