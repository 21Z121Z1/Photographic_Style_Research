"""AIR10 SSA568..600: original gain, output CCM order and raw transfer enum."""
from dataclasses import dataclass
from leaf_numeric import V,DomainUnknown,lazy_select,mix
from pixel_leaves import H,F
from pixel_transfer import forward as transfer


@dataclass(frozen=True)
class Parameters:
    reference_gain176: V
    parameter2: V
    output_CCM_columns: V
    input_transfer136: int
    output_transfer599: int

    def __post_init__(self):
        vs=[self.reference_gain176,self.parameter2,self.output_CCM_columns]
        if any(not isinstance(x,V)for x in vs)or [x.precision for x in vs]!=['h','f','f']or [x.lo.shape for x in vs]!=[(),(),(3,3)]or any(x.point!=vs[0].point for x in vs):raise TypeError('Matching half gain, f32 parameter2 and output CCM3x3 columns required')
        if any(type(x)is not int or not 0<=x<=0xffffffff for x in [self.input_transfer136,self.output_transfer599]):raise TypeError('Exact input/output transfer uint32 required')


@dataclass(frozen=True)
class Result:
    output600: V
    linear597: V
    gain577: V
    image_writer_or_GPU_verified: bool=False


def forward(rgb567,parameters: Parameters):
    if not isinstance(rgb567,V)or rgb567.precision!='h'or rgb567.lo.shape!=(3,)or parameters.parameter2.point!=rgb567.point:raise TypeError('Matching half RGB567 and parameter backend required')
    p=parameters;one=H(1,rgb567)
    if p.input_transfer136==6:one=lazy_select(p.parameter2.gt(0),lambda:mix(H(1,rgb567),H(1,rgb567),(p.parameter2*F(2,rgb567)).abs().h()),lambda:H(1,rgb567))
    gain=one/p.reference_gain176;c=p.output_CCM_columns.h()
    linear=((c[1]*rgb567[1]+c[0]*rgb567[0])+c[2]*rgb567[2])*gain
    return Result(transfer(linear,p.output_transfer599,to_linear=False),linear,gain)


def from_post_chain(post_chain,parameters):
    if post_chain.output567 is None:raise DomainUnknown('Upstream '+str(post_chain.unknown_operator)+': '+str(post_chain.reason))
    if post_chain.output567.point:raise TypeError('Whole upstream set required, never an output center')
    return forward(post_chain.output567,parameters),post_chain.input_branch_decisions
