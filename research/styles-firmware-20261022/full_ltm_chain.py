"""Source textures -> AIR7 -> guided -> AIR10 block290 conditional chain.

This is a model connection under named storage/sampler/context contracts.
Original CPU host composition is tested separately; neither proves a frame
identity or recovers the supplied inputs from a final photograph.
"""
from dataclasses import dataclass
import numpy as np
from leaf_numeric import V,DomainUnknown
from texture_numeric import Texture,PixelFormat,producer_uv,sample_normalized,rgba,consume_block290
from ltm_preprocess import forward as preprocess
from ltm_gain import forward as gains
from guided_conditioned import Inputs,forward as guided_point,forward_set as guided_set


@dataclass(frozen=True)
class Result:
    producer_observations: dict
    raw_bg: Texture|None
    raw_fg: Texture|None
    guided_bg: dict|None
    guided_fg: dict|None
    consumer: dict|None
    unknowns: dict
    input_branch_decisions: tuple
    GPU_or_same_frame_verified: bool=False


def generate(primary,linear,matte,guide,*,producer_shape,pre_parameters,gain_parameters,curve,epsilon,input_branch_decisions=()):
    point=primary.pixels.point
    if primary.pixel_format!=PixelFormat.RGBA16Float or linear.pixel_format!=PixelFormat.RGBA16Float or guide.pixel_format not in(PixelFormat.RGBA16Float,PixelFormat.R16Float):raise TypeError('Explicit supported source formats required; unverified formats unsupported')
    if any(t.pixels.point!=point for t in [linear,guide])or gain_parameters.scale6.point!=point or pre_parameters.srl_parameter.point!=point:raise TypeError('Matching whole point/set source/parameter backends required')
    if pre_parameters.use_srl_before_stats and(matte is None or matte.pixel_format!=PixelFormat.R16Float or matte.pixels.point!=point):raise TypeError('Active original SRL requires explicit R16 matte')
    h,w=producer_shape;names=['source24','postSRL34','linear37','reference96','working121','BG203','FG205'];rows={k:[]for k in names};unknowns={};markers=tuple(input_branch_decisions)
    try:
        for y in range(h):
            current={k:[]for k in names}
            for x in range(w):
                uv=producer_uv((x,y),producer_shape,point=point);source=sample_normalized(primary,uv)[:3];lin=sample_normalized(linear,uv)[:3]
                mask=sample_normalized(matte,uv)[0]if pre_parameters.use_srl_before_stats else V.value(0,'h',point)
                pre=preprocess(source,mask,pre_parameters);gain=gains(pre.reference96,lin,gain_parameters,curve)
                for k,v in zip(names,[source,pre.post_srl34,pre.linear37,pre.reference96,gain.transformed_linear121,gain.bg203,gain.fg205]):current[k].append(v)
            for k in names:rows[k].append(current[k])
    except DomainUnknown as error:return Result({},None,None,None,None,None,{'producer':str(error)},markers)
    observations={k:V(np.stack([[v.lo for v in row]for row in a]),np.stack([[v.hi for v in row]for row in a]),'h',point)for k,a in rows.items()};domain='AIR7 RGBA16 BG/FG gain-ratio working domain';bg=Texture(rgba(observations['BG203']),PixelFormat.RGBA16Float,domain);fg=Texture(rgba(observations['FG205']),PixelFormat.RGBA16Float,domain);outshape=guide.pixels.lo.shape[:2];outputs=[]
    for name,t in [('BG',bg),('FG',fg)]:
        try:
            if point:
                result=guided_point(Inputs(t.pixels.lo.astype('f2'),guide.pixels.lo.astype('f2'),outshape,1,np.float32(epsilon.lo),domain));result={k:V.value(v)for k,v in result.items()}
            else:result=guided_set(None,gain=t.pixels,guide=guide.pixels,epsilon=epsilon,output_shape=outshape,working_domain=domain)
            outputs.append(result)
        except DomainUnknown as error:outputs.append(None);unknowns['guided_'+name]=str(error)
    return Result(observations,bg,fg,*outputs,None,unknowns,markers)


def forward(primary,linear,matte,guide,*,producer_shape,pre_parameters,gain_parameters,consumer_semantic7,curve,epsilon,roi,reference196,person96,input_branch_decisions=()):
    """Legacy explicit-consumer interface; generation itself needs no consumer oracle."""
    r=generate(primary,linear,matte,guide,producer_shape=producer_shape,pre_parameters=pre_parameters,gain_parameters=gain_parameters,curve=curve,epsilon=epsilon,input_branch_decisions=input_branch_decisions)
    outputs=[r.guided_bg,r.guided_fg];unknowns=dict(r.unknowns);consumer=None
    if all(x is not None for x in outputs):
        try:consumer=consume_block290(Texture(outputs[0]['output'],PixelFormat.RGBA16Float,r.raw_bg.working_domain),Texture(outputs[1]['output'],PixelFormat.RGBA16Float,r.raw_fg.working_domain),roi,reference196,person96,consumer_semantic7)
        except DomainUnknown as error:unknowns['consumer']=str(error)
    return Result(r.producer_observations,r.raw_bg,r.raw_fg,*outputs,consumer,unknowns,r.input_branch_decisions)
