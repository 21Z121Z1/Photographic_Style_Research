"""AIR10 source/working-domain/guide combination through original color392."""
from dataclasses import dataclass
from leaf_numeric import V,DomainUnknown,vec,lazy_select,mix,fc
from pixel_leaves import H,F
from texture_numeric import Texture,PixelFormat,sample_normalized,ROI,consume_block290
from ltm_preprocess import Parameters as PreParameters,forward as linear_reference,semantic_srl
from ltm_gain import gain_ratios
from cast_values import CastValues
from typed_bgfg import Fields,forward as bgfg
from pre_skin_color import forward as outer_color


@dataclass(frozen=True)
class Controls:
    cast0: int
    srl_version: int
    intensity1: V
    tone2: V
    color3: V
    scale6: V
    baseline7: V
    hint21: V
    color_boost11_2: V

    def __post_init__(self):
        vs=[self.intensity1,self.tone2,self.color3,self.scale6,self.baseline7,self.hint21,self.color_boost11_2]
        if any(not isinstance(v,V)or v.precision!='f'or v.lo.shape!=()for v in vs)or any(v.point!=vs[0].point for v in vs):raise TypeError('Matching original f32 control scalars required')
        if type(self.cast0)is not int or not 0<=self.cast0<=0xffffffff or type(self.srl_version)is not int or not -2**31<=self.srl_version<2**31:raise TypeError('Original uint32 cast and int32 SRL version required')


@dataclass(frozen=True)
class Result:
    observations: dict
    post_semantic7: V|None
    unknown_operator: str|None
    unknown_reason: str|None
    input_branch_decisions: tuple
    full_camera_pipeline_verified: bool=False


def mutate_semantic(p,controls):
    if controls.cast0!=2:return p
    weight=1-controls.intensity1*F(.5,p)
    def branch(nonpositive):
        return vec([mix(p[i],controls.baseline7,weight)if nonpositive and i in(2,3)else mix(p[i],F(1,p),weight)if i in(5,6)else p[i]for i in range(7)])
    return lazy_select(controls.tone2.gt(F(0,p)),lambda:branch(False),lambda:branch(True))


def forward(primary,linear,guide8,guide9,person_tex,skin_tex,sky_tex,maps,*,grid,transforms,pre_parameters,linear_CCM_columns,controls,cast,semantic7,helper_fields,gtc,whites,input_branch_decisions=()):
    point=primary.pixels.point;obs={};post=None;stage='source sampling';markers=tuple(input_branch_decisions)
    if not isinstance(controls,Controls)or not isinstance(cast,CastValues)or not isinstance(helper_fields,Fields)or any(v.point!=point for v in [controls.tone2,cast.raw,helper_fields.bg17,semantic7,pre_parameters.srl_parameter,linear_CCM_columns]):raise TypeError('Whole matching parameter/source backends required')
    def uv(field):
        t=transforms[field]
        if not isinstance(t,V)or t.precision!='f'or t.lo.shape!=(4,)or t.point!=point:raise TypeError('Matching original f32 ROI transform required')
        return t[:2]*(V.value(grid,'f',point)+V.value(.5,'f',point))+t[2:]
    def mask(tex,field):
        if tex is None:return H(0,semantic7)
        if tex.pixel_format!=PixelFormat.R16Float:raise TypeError('Conditional mask contract is explicit R16Float')
        return sample_normalized(tex,uv(field))[0]
    try:
        rgb=sample_normalized(primary,uv(3))[:3];person=mask(person_tex,9);skin=mask(skin_tex,10);sky=mask(sky_tex,11);obs.update(source38=rgb,raw_person63=person,raw_skin70=skin,sky77=sky)
        stage='person/skin hint scaling'
        def scale():
            q=(controls.hint21/cast.scalar(21)).clamp();factor=((q*q)*(3-2*q)).maximum(F(fc('3FD3333340000000'),q)).h()
            return vec([skin*factor,person*factor])
        masks=lazy_select(controls.hint21.lt(F(0,semantic7)),lambda:vec([skin,person]),scale);skin=masks[0];person=masks[1];obs.update(skin95=skin,person96=person)
        stage='SRL selection'
        if controls.srl_version==1:rgb=lazy_select(pre_parameters.srl_parameter.gt(F(0,semantic7))&pre_parameters.srl_parameter.lt(F(1,semantic7)),lambda:semantic_srl(rgb,pre_parameters.srl_parameter,person),lambda:rgb)
        elif controls.srl_version==2:rgb=semantic_srl(rgb,pre_parameters.srl_parameter,person)
        obs['SRL134']=rgb;stage='input transfer/CCM/HLG'
        pre=linear_reference(rgb,person,PreParameters(pre_parameters.srl_parameter,pre_parameters.input_CCM_columns,pre_parameters.transfer_code,False,pre_parameters.input_gamma_mode));ref=pre.reference96;obs.update(linear137=pre.linear37,gain176=pre.reference_gain,reference196=ref)
        stage='guide and linear working inputs';g8=sample_normalized(guide8,uv(7))[0];g9=sample_normalized(guide9,uv(8))[0];lin=sample_normalized(linear,uv(4))[:3];c=linear_CCM_columns.h();working=((c[1]*lin[1]+c[0]*lin[0])+c[2]*lin[2])*controls.scale6.h();obs.update(guide211=g8,guide214=g9,working286=working)
        stage='cast2 semantic mutation';post=mutate_semantic(semantic7,controls);p=post.h()
        stage='semantic branch'
        if maps[0]is not None and maps[1]is not None:
            result=consume_block290(*maps,ROI(grid,transforms[5],transforms[6]),ref,person,post);semantic=result['output335'];obs['precomputed335']=semantic
        else:
            bg,fg=gain_ratios(working,ref,post,gtc)
            def branch(ratio,ltm,hr):
                local=mix(ratio,H(1,ratio),ltm);return mix(local,local.minimum(1),hr)*ref
            semantic=mix(branch(bg,p[0],p[5]),branch(fg,p[1],p[6]),person)
        obs['semantic347']=semantic;guide=mix(mix(g9,g8,p[0]),mix(g9,g8,p[1]),person);obs['guide350']=guide
        stage='BG352';bg=bgfg('bg',semantic,semantic,helper_fields,guide=guide,person=person,skin=skin,whites=whites);obs['BG352']=bg
        stage='FG354';fg=bgfg('fg',bg,semantic,helper_fields,guide=guide,person=person,skin=skin,whites=whites);obs['FG354']=fg
        stage='outer color355..392';color=outer_color(fg,person,controls.color3,controls.color_boost11_2);obs.update(saturated374=color.saturated374,color_mix389=color.person_mix389,output392=color.output392)
        return Result(obs,post,None,None,markers)
    except DomainUnknown as error:return Result(obs,post,stage,str(error),markers)
