"""AIR10 BW channel-mix567 and its stats-derived weights, supplied context."""
from leaf_numeric import V,DomainUnknown,hc,vec,mix,lazy_select
from pixel_leaves import H
from pixel_color import to_lab
from pixel_skin import encode,decode
from pixel_neutral import smooth
from pixel_neutral_root import NeutralStats


def weights(stats: NeutralStats,cast_type0: int):
    if cast_type0 not in (4,15):raise DomainUnknown('getBWChannelMixFromStats has undef default outside4/15')
    if not isinstance(stats,NeutralStats):raise TypeError('Three actual f32 stats fields required')
    raw=vec([stats.s2_4.h(),stats.s3_4.h(),stats.s4_4.h()]);lab=to_lab(raw)
    angle=lazy_select(lab[2].ne(0)|lab[1].ne(0),lambda:lab[2].atan2(lab[1]),lambda:H(0,lab))
    amount=smooth((angle.abs()*H(hc('3c72'),lab)).clamp())
    target=['3883','3629','2a87']if cast_type0==4 else['38f8','3558','2b0a']
    result=mix(H([hc('3555')]*3,lab),H([hc(x)for x in target],lab),amount)
    return result/result.sum_channels()


def forward(rgb,person96,*,cast_type0: int,tone17_19: V|None,stats: NeutralStats|None):
    if not isinstance(rgb,V)or rgb.precision!='h'or rgb.lo.shape!=(3,)or not isinstance(person96,V)or person96.precision!='h'or person96.lo.shape!=()or person96.point!=rgb.point:raise TypeError('Matching half RGB and scalar person96 required')
    if type(cast_type0)is not int or not 0<=cast_type0<=0xffffffff:raise TypeError('Exact SSRParams0 uint32 code required')
    if cast_type0 not in (4,15):return rgb
    if not isinstance(stats,NeutralStats):raise DomainUnknown('Active BW channel mix requires supplied stats')
    if stats.s2_4.point!=rgb.point:raise TypeError('Stats and RGB backends must match')
    reference=weights(stats,cast_type0);curved=encode(rgb)
    if cast_type0==4:
        if not isinstance(tone17_19,V)or tone17_19.precision!='f'or tone17_19.point!=rgb.point or tone17_19.lo.shape!=(3,):raise TypeError('Three explicit f32 SSRTone fields17..19 required for cast4')
        original=(curved*tone17_19.h()).sum_channels()
    else:original=curved.square().sum_channels()/curved.sum_channels()
    changed=(curved*reference).sum_channels();gray=decode(mix(original,changed,person96))
    return vec([gray,gray,gray])
