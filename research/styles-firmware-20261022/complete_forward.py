"""One connected conditional source -> producer -> guided -> main -> writer model.

Raw buffers/textures are inputs; no API accepts generated BG/FG maps, RGB335,
RGB392, BW477, RGB567 or RGB600 as an oracle. Unsupported domains remain unknown.
"""
from dataclasses import dataclass
import numpy as np
from leaf_numeric import V,DomainUnknown,mix
from texture_numeric import Texture,PixelFormat
from full_ltm_chain import generate
from ltm_preprocess import Parameters as Pre
from ltm_gain import Parameters as Gain
from semantic_tone import Curve1D
from cast_values import CastValues
from main_pre393 import Controls,forward as pre393
from typed_bgfg import Fields
from pixel_skin import forward as skin,highlight_recover
from pixel_bright import BrightStats,forward as bright
from pixel_neutral_root import NeutralStats,forward as neutral
from pixel_warmth import forward as warmth
from pixel_selective import SelectiveTexture,forward as selective
from computed_bw_outer import forward as bw_outer
from pixel_bw import Parameters as BW
from pixel_haze import Parameters as Haze,select_video
from pixel_postprotect import forward as protect
from pixel_channel_mix import forward as channel
from pixel_output import Parameters as Output,forward as output
from output_writer import Controls as Write,forward as write


@dataclass(frozen=True)
class Context:
    """Original raw ABI buffers plus explicit synthetic auxiliary texture inputs."""
    images: tuple # primary,linear,guide,producer matte,guide8,guide9,person,skin,sky,lookup
    management: np.ndarray
    params: np.ndarray
    stats: np.ndarray
    roi: np.ndarray
    srl: np.ndarray
    gtc: Curve1D
    whites: Curve1D
    epsilon: np.float32
    producer_shape: tuple
    output_initial: np.ndarray
    version: int
    hardware: str='iPhone17,3'
    build: str='24A446'

    def __post_init__(self):
        if len(self.images)!=10:raise TypeError('Ten explicit raw source/auxiliary textures required')
        frozen=[]
        for i,a in enumerate(self.images):
            a=np.array(a,dtype='f2',copy=True);c=4 if i in(0,1,2,9)else 1
            if a.ndim!=3 or a.shape[2]!=c or not np.isfinite(a).all():raise TypeError('Explicit finite role/format shape required')
            if i!=9 and max(a.shape[:2])>32:raise ValueError('Bounded synthetic context only')
            a.setflags(write=False);frozen.append(a)
        if frozen[9].shape!=(4,360,4):raise TypeError('Explicit selective lookup4x360RGBA required')
        object.__setattr__(self,'images',tuple(frozen))
        for name,size in [('management',80),('params',168),('stats',2660),('roi',44),('srl',1)]:
            a=np.array(getattr(self,name),dtype='f4',copy=True)
            if a.shape!=(size,)or not np.isfinite(a).all():raise TypeError('Original ABI buffer size and finite bits required')
            a.setflags(write=False);object.__setattr__(self,name,a)
        if (self.hardware,self.build)!=('iPhone17,3','24A446')or type(self.version)is not int:raise ValueError('Only the matched version identity is covered')
        if self.params.view('u4')[0]not in(0,2):raise ValueError('Connected contract currently covers resolved cast0/2 only')
        if self.params[167]>=0:raise ValueError('This fixed context requires negative person hint; other hint domains use pre393 API')
        if tuple(self.images[0].shape[:2])!=tuple(self.images[2].shape[:2]):raise ValueError('Original source/guide grid identity required')
        if not isinstance(self.producer_shape,tuple)or len(self.producer_shape)!=2 or any(type(v)is not int or not 1<=v<=32 for v in self.producer_shape):raise TypeError('Exact bounded producer grid required')
        if type(self.epsilon)is not np.float32 or not np.isfinite(self.epsilon)or not 0<=self.epsilon<=1:raise TypeError('Explicit bounded raw epsilon f32 required')
        if any(self.management.view('u1')[80*slot+64]for slot in range(4)):raise ValueError('This complete context covers supplied zero gamma-mode flags only')
        a=np.array(self.output_initial,dtype='f2',copy=True)
        if a.ndim!=3 or a.shape[2]!=4 or not np.isfinite(a).all()or max(a.shape[:2])>32:raise ValueError('Finite bounded RGBA16 output storage required')
        a.setflags(write=False);object.__setattr__(self,'output_initial',a)


@dataclass(frozen=True)
class Result:
    observations: dict
    generated: object
    pixel_unknowns: dict
    internal_unknowns: dict
    writer: object|None
    point: bool
    full_camera_pipeline_verified: bool=False


def stack(rows,point):
    return V(np.array([[v.lo for v in row]for row in rows]),np.array([[v.hi for v in row]for row in rows]),'h',point)


def forward(c: Context,*,point: bool,shared_semantic=False):
    if not isinstance(c,Context)or type(point)is not bool or type(shared_semantic)is not bool:raise TypeError('Fixed raw context and exact point/set/relation selection required')
    H=lambda x:V.value(x)if point else V.bounds(x,x)
    F=lambda x:V.value(x,'f')if point else V.bounds(x,x,'f')
    def tex(i):return Texture(H(c.images[i]),PixelFormat.RGBA16Float if i in(0,1,2)else PixelFormat.R16Float,'synthetic raw role'+str(i))
    m,p,s,r=c.management,c.params,c.stats,c.roi
    cols=lambda slot:np.stack([m[20*slot+4+4*k:20*slot+7+4*k]for k in range(3)])
    code=lambda slot:int(m.view('u4')[20*slot])
    pre=Pre(F(c.srl[0]),F(cols(0)),code(0),False,False)
    generated=generate(tex(0),tex(1),tex(3),tex(2),producer_shape=c.producer_shape,pre_parameters=pre,gain_parameters=Gain(F(cols(1)),F(p[6]),F(p[155:162])),curve=c.gtc,epsilon=F(c.epsilon),input_branch_decisions=('single immutable raw context; no intermediate output oracle',))
    observations={**{'producer_'+k:v for k,v in generated.producer_observations.items()}};unknown={};internal={};rows={};write_rows=[]
    if generated.raw_bg is not None:observations['raw_BG']=generated.raw_bg.pixels
    if generated.raw_fg is not None:observations['raw_FG']=generated.raw_fg.pixels
    for side,g in [('BG',generated.guided_bg),('FG',generated.guided_fg)]:
        if g is not None:
            for k,v in g.items():observations[side+'_'+k]=v
    if generated.guided_bg is None or generated.guided_fg is None:return Result(observations,generated,{'generation':generated.unknowns},internal,None,point)
    maps=tuple(Texture(g['output'],PixelFormat.RGBA16Float,'AIR7 RGBA16 BG/FG gain-ratio working domain')for g in [generated.guided_bg,generated.guided_fg]);cast=CastValues(F(p[9:43]));fields=Fields(F(p[122:139]),F(p[139:155]));controls=Controls(int(p.view('u4')[0]),c.version,F(p[1]),F(p[2]),F(p[3]),F(p[6]),F(p[7]),F(p[167]),F(p[111]));transforms={k:F(r[4*(k-3)+4:4*(k-3)+8])for k in range(3,12)}
    stat=lambda g,f:F(s[2560+g*9+f]);ns=NeutralStats(stat(2,4),stat(3,4),stat(4,4));bs=BrightStats(stat(2,4),stat(3,4),stat(5,0),stat(6,6),stat(6,4));lookup=SelectiveTexture(c.images[9],'explicit synthetic lookup; producer unmodeled');castcode=int(p.view('u4')[0]);tuning=int(p.view('u4')[163]);height,width=c.images[0].shape[:2]
    for y in range(height):
        local={};outputs=[]
        for x in range(width):
            key=f'{x},{y}';q=pre393(tex(0),tex(1),tex(4),tex(5),tex(6),tex(7),tex(8),maps,grid=(x,y),transforms=transforms,pre_parameters=pre,linear_CCM_columns=F(cols(1)),controls=controls,cast=cast,semantic7=F(p[155:162]),helper_fields=fields,gtc=c.gtc,whites=c.whites,shared_semantic=shared_semantic);o=dict(q.observations);stage=q.unknown_operator
            def optional(name,fn):
                try:o[name]=fn()
                except DomainUnknown as e:internal[key+':'+name]=str(e)
            try:
                if stage:raise DomainUnknown(q.unknown_reason)
                person=o['person96'];skin95=o['skin95'];guide=o['guide350'];stage='skin393';o[stage]=skin(o['output392'],skin95,guide,F(p[148]),F(p[149]))
                optional('highlight394',lambda:highlight_recover(o['skin393'],guide,H(2)))
                if castcode==2 and 'highlight394'not in o:stage='highlight394';raise DomainUnknown(internal[key+':highlight394'])
                o['highlight398']=mix(o['skin393'],o['highlight394'],H(.5))if castcode==2 else o['skin393']
                optional('bright400',lambda:bright(o['skin393'],o['working286'],person,skin95,F(p[7]).h(),bs))
                o['selected404']=o['skin393'];stage='neutral408';o[stage]=neutral(o['selected404'],enabled=True,cast=cast,skin=skin95,person=person,use_skin=True,stats=ns);stage='warm409';o[stage]=warmth(o['neutral408'],cast,person);stage='selective413';o[stage]=selective(o['warm409'],cast,lookup,person,skin95,o['sky77'],F(p[112]).h())
                stage='BW/outer';bw=bw_outer(o['selective413'],o['highlight398'],guide,person,F(p[4]),F(p[5]),parameters=BW(F(p[2]),F(p[63]),F(p[108]),castcode,tuning),raw_cast_type245=castcode,whites=c.whites)
                for name,value in [('tonal468',bw.outer.tonal468),('BW_input472',bw.outer.bw_input472),('color476',bw.outer.color476),('BW477',bw.bw.output477 if bw.bw else None),('mixed492',bw.output492)]:
                    if value is not None:o[name]=value
                internal.update({key+':outer:'+k:v for k,v in bw.outer.unknowns.items()})
                if bw.bw:internal.update({key+':BW:'+k:v for k,v in bw.bw.unknowns.items()})
                if bw.output492 is None:raise DomainUnknown(bw.unknown_reason)
                stage='haze';haze=select_video(bw.output492,o['guide211'],person,Haze(F(p[114:122]),bool(p.view('u1')[452])),tuning_type17=tuning)
                if haze.haze493 is not None:o['haze493']=haze.haze493
                if haze.unknown_reason:internal[key+':haze493']=haze.unknown_reason
                if haze.output501 is None:raise DomainUnknown(haze.unknown_reason)
                o['selected501']=haze.output501;stage='protect566';o[stage]=protect(haze.output501,o['color476'],cast,ns,texture10_present=True);stage='channel567';o[stage]=channel(o['protect566'],person,cast_type0=castcode,tone17_19=F(p[60:63]),stats=ns);stage='output600';out=output(o['channel567'],Output(o['gain176'],F(p[2]),F(cols(3)),code(0),code(3)));o.update(linear597=out.linear597,output600=out.output600);outputs.append(out.output600)
            except DomainUnknown as e:unknown[key]={'operator':stage,'reason':str(e)}
            for name,value in o.items():local.setdefault(name,[]).append(value)
        for name,vs in local.items():
            if len(vs)==width:rows.setdefault(name,[]).append(vs)
        if len(outputs)==width:write_rows.append(outputs)
    for name,vs in rows.items():
        if len(vs)==height:observations[name]=stack(vs,point)
    writer=None
    if len(write_rows)==height:
        offsets=tuple(int(v)for v in r.view('u2')[80:82]);edges=tuple(int(v)for v in r.view('u2')[4:6]);writer=write(Texture(H(c.output_initial),PixelFormat.RGBA16Float,'synthetic output storage'),stack(write_rows,point),Write((0,0),offsets,edges,False));observations['writer']=writer.output.pixels
    return Result(observations,generated,unknown,internal,writer,point)
