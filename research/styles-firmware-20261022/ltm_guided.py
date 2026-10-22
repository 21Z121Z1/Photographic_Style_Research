"""Sampled AIR7 inputs -> raw BG/FG maps -> guided complete set interfaces.

All input colors/matte are already sampled at original gain-map texel centers.
Guide, coefficients and epsilon remain explicit. No original frame is inferred.
"""
from dataclasses import dataclass
import numpy as np
from leaf_numeric import V,DomainUnknown
from ltm_preprocess import forward as preprocess
from ltm_gain import forward as gains
from guided_conditioned import forward_set as guided


@dataclass(frozen=True)
class Result:
    raw_bg: V|None
    raw_fg: V|None
    guided_bg: dict|None
    guided_fg: dict|None
    unknowns: dict
    input_branch_decisions: tuple
    original_2D_source_sampling_verified: bool=False
    GPU_or_same_frame_verified: bool=False


def forward(primary24,linear98,matte30,guide,*,pre_parameters,gain_parameters,curve,epsilon,output_shape,working_domain,input_branch_decisions=()):
    colors=[primary24,linear98]
    if any(not isinstance(x,V)or x.point or x.precision!='h'or len(x.lo.shape)!=3 or x.lo.shape[2]!=3 for x in colors)or primary24.lo.shape!=linear98.lo.shape:raise TypeError('Matching whole half HxWx3 sampled primary/linear sets required')
    h,w=primary24.lo.shape[:2]
    if not 1<=h<=32 or not 1<=w<=32 or not isinstance(matte30,V)or matte30.point or matte30.precision!='h'or matte30.lo.shape!=(h,w):raise TypeError('Matching sampled matte set and bounded grid required')
    markers=tuple(input_branch_decisions);bg=[];fg=[]
    try:
        for y in range(h):
            br=[];fr=[]
            for x in range(w):
                pre=preprocess(primary24[y,x],matte30[y,x],pre_parameters);r=gains(pre.reference96,linear98[y,x],gain_parameters,curve)
                br.append(r.bg203);fr.append(r.fg205)
            bg.append(br);fg.append(fr)
    except DomainUnknown as error:return Result(None,None,None,None,{'AIR7_sampled_color_core':str(error)},markers)
    def image(rows):return V(np.stack([[x.lo for x in row]for row in rows]),np.stack([[x.hi for x in row]for row in rows]),'h',False)
    bg=image(bg);fg=image(fg);outputs=[];unknowns={}
    for name,value in [('BG',bg),('FG',fg)]:
        try:outputs.append(guided(None,gain=value,guide=guide,epsilon=epsilon,output_shape=output_shape,working_domain=working_domain))
        except DomainUnknown as error:outputs.append(None);unknowns['guided_'+name]=str(error)
    return Result(bg,fg,*outputs,unknowns,markers)
