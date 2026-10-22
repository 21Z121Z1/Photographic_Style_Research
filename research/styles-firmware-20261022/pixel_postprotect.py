"""AIR10 SSA502..566 protection, preserving raw threshold and presence gate."""
from leaf_numeric import V,DomainUnknown,vec,lazy_select,mix,fc
from pixel_leaves import H,F
from pixel_color import to_lab
from pixel_warmth import angle_of,protect
from pixel_neutral_root import NeutralStats
from cast_values import CastValues


def forward(rgb501,color476,cast: CastValues,stats: NeutralStats|None,*,texture10_present: bool):
    if any(not isinstance(x,V)or x.precision!='h'or x.lo.shape!=(3,)for x in [rgb501,color476])or rgb501.point!=color476.point:raise TypeError('Matching half RGB501/color476 required')
    if type(texture10_present)is not bool:raise TypeError('Exact original texture10 presence flag required')
    if not isinstance(cast,CastValues)or cast.raw.point!=rgb501.point:raise TypeError('Matching full cast block required')
    if not texture10_present:return rgb501
    amount=cast.scalar(19)
    def active():
        if not isinstance(stats,NeutralStats):raise DomainUnknown('Active post-protection needs original stats reference')
        if stats.s2_4.point!=rgb501.point:raise TypeError('Stats and RGB backends must match')
        lab=to_lab(vec([stats.s2_4.h(),stats.s3_4.h(),stats.s4_4.h()]))
        width=(cast.scalar(20).square()*F(fc('3F19690E20000000'),rgb501)).h()
        p=vec([angle_of(lab),width,H(1,rgb501)])
        mask=protect(rgb501,[p,p,p],ignore_chroma=True)[0]
        return mix(rgb501,color476,(amount*mask.f()).h())
    return lazy_select(amount.lt(F(fc('3F847AE140000000'),rgb501)),lambda:rgb501,active)
