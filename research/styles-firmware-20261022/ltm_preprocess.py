"""AIR7 sampled primary24 -> SRL34 -> transfer37 -> reference96."""
from dataclasses import dataclass
from leaf_numeric import V,hc,fc,lazy_select,mix
from pixel_leaves import H,F,dot
from pixel_transfer import forward as transfer


def semantic_srl(rgb,parameter,matte):
    def apply(q):
        y=dot(rgb,[hc('34c9'),hc('38b2'),hc('2f4c')])
        def active():
            z=(q*y.f())/((1-q)*(1-y).f());gain=((1-1/(z+1))/y.f()).h()
            return gain*rgb
        return lazy_select(y.abs().lt(H(hc('0101'),rgb)),lambda:rgb,active)
    def high():
        def over2():
            return lazy_select(parameter.lt(F(3,rgb)),lambda:mix((parameter-F(2.5,rgb))*F(.5,rgb)+F(.5,rgb),parameter-F(2,rgb),matte.f()),lambda:F(-1,rgb))
        q=lazy_select(parameter.lt(F(2,rgb)),lambda:mix(F(.5,rgb),parameter-F(1,rgb),matte.f()),over2)
        return lazy_select(q.gt(F(0,rgb))&q.lt(F(1,rgb)),lambda:apply(q),lambda:rgb)
    return lazy_select(parameter.lt(F(1,rgb)),lambda:lazy_select(parameter.gt(F(0,rgb)),lambda:apply(parameter),lambda:rgb),high)


@dataclass(frozen=True)
class Parameters:
    srl_parameter: V
    input_CCM_columns: V
    transfer_code: int
    use_srl_before_stats: bool
    input_gamma_mode: bool

    def __post_init__(self):
        if not isinstance(self.srl_parameter,V)or self.srl_parameter.precision!='f'or self.srl_parameter.lo.shape!=()or not isinstance(self.input_CCM_columns,V)or self.input_CCM_columns.precision!='f'or self.input_CCM_columns.lo.shape!=(3,3)or self.srl_parameter.point!=self.input_CCM_columns.point:raise TypeError('Matching f32 SRL scalar and input CCM columns required')
        if type(self.transfer_code)is not int or not 0<=self.transfer_code<=0xffffffff or any(type(x)is not bool for x in [self.use_srl_before_stats,self.input_gamma_mode]):raise TypeError('Exact enum and two original flags required')


@dataclass(frozen=True)
class Result:
    reference96: V
    linear37: V
    post_srl34: V
    upstream_2D_sampling_included: bool=False


def forward(primary24,matte30,parameters: Parameters):
    p=parameters
    if any(not isinstance(x,V)or x.precision!='h'for x in [primary24,matte30])or primary24.lo.shape!=(3,)or matte30.lo.shape!=()or primary24.point!=matte30.point or primary24.point!=p.srl_parameter.point:raise TypeError('Matching supplied half primary24/matte30 and parameter backend required')
    work=semantic_srl(primary24,p.srl_parameter,matte30)if p.use_srl_before_stats else primary24
    linear=transfer(work,p.transfer_code,to_linear=True);gain=H(1,linear)
    if p.transfer_code==6:
        exponent=(H(hc('3c72'),linear).pow(H(hc('2e66'),linear).log(True)).f()*F(fc('3FF3333340000000'),linear)).h()
        if p.input_gamma_mode:base=(dot(linear,[hc('32d1'),hc('39b8'),hc('2c9c')])+linear.max_channels())*H(.5,linear);gain=base.pow(exponent-1)
        else:
            y=(linear[0].f()*F(fc('3FD0D013A0000000'),linear)+linear[1].f()*F(fc('3FE5B22D00000000'),linear))+linear[2].f()*F(fc('3FAE5C91E0000000'),linear)
            gain=y.pow(exponent.f()-1).h()
    corrected=linear*gain;c=p.input_CCM_columns.h();ref=(corrected[0]*c[0]+corrected[1]*c[1])+corrected[2]*c[2]
    return Result(ref,linear,work)
