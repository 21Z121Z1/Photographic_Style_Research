"""Set-valued semantic -> BG -> FG fragment, with explicit unresolved leaves.

Only this actual AIR10 helper order is composed. Input RGB already belongs at
the helper call site; outer sampling/color transforms/skin/style are omitted.
"""
from dataclasses import dataclass
from semantic_tone import I,SemanticSetResult
from semantic_caller import runtime_semantic_set,mixed_guide_set,prepare_intervals
from precomputed_semantic import PrecomputedInputs,forward_set as precomputed_set
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


def forward(inputs,fields,*,cast_type,baseline_exposure,guide_texture8,guide_texture9,skin_weight,texture6_present: bool,texture7_present: bool,leaf_models=None,whites_curve=None):
    from all_pixel_leaves import models
    providers={**models(whites_curve),**(leaf_models or {})}
    if type(texture6_present)is not bool or type(texture7_present)is not bool:raise ValueError('Explicit presence of both precomputed semantic textures required')
    if texture6_present and texture7_present:
        if not isinstance(inputs,PrecomputedInputs):return FragmentResult('unknown_precomputed_inputs',None,None,None,None,None)
        lo,hi=prepare_intervals(fields,cast_type=cast_type,baseline_exposure=baseline_exposure)
        semantic=precomputed_set(inputs,lo,hi,input_branches=fields.branch_decisions)
    else:
        if isinstance(inputs,PrecomputedInputs):raise ValueError('Fallback path needs its own working/GTC inputs; no equivalence assumed')
        semantic=runtime_semantic_set(inputs,fields,cast_type=cast_type,baseline_exposure=baseline_exposure)
    guide=mixed_guide_set(fields,guide_texture8,guide_texture9,inputs.person_weight,cast_type=cast_type,baseline_exposure=baseline_exposure)
    context=PixelContext(guide,inputs.person_weight,skin_weight);rgb=I(semantic.lower,semantic.upper)
    if guide.lo<0 or guide.hi>1:return FragmentResult('unknown_guide_domain',semantic,guide,None,None,None)
    bg=run('bg',rgb,fields,context,leaf_models=providers)
    if bg.output is None:return FragmentResult('unknown_BG_operator',semantic,guide,bg,None,None)
    fg=run('fg',bg.output,fields,context,semantic_rgb=rgb,leaf_models=providers)
    return FragmentResult('computed_fragment_set'if fg.output is not None else 'unknown_FG_operator',semantic,guide,bg,fg,fg.output)
