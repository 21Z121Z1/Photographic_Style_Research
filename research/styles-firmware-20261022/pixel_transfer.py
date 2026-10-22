"""Matched AIR7/AIR10 CMI transfer functions by exact raw enum, no ICC alias."""
from leaf_numeric import V,DomainUnknown,hc,vec,select,lazy_select
from pixel_leaves import H
from pixel_skin import encode,decode


def forward(rgb,code: int,*,to_linear: bool):
    if not isinstance(rgb,V)or rgb.precision!='h'or rgb.lo.shape!=(3,):raise TypeError('Half RGB required')
    if type(code)is not int or not 0<=code<=0xffffffff or type(to_linear)is not bool:raise TypeError('Exact transfer uint32 and direction required')
    if code in(0,1):return rgb
    if code==2:return rgb.abs().pow(H(1,rgb))*rgb.sign()
    if code==3:return decode(rgb)if to_linear else encode(rgb)
    if code not in(4,5,6,7,8):return H([0,0,0],rgb)
    def one(x):
        a=x.abs();c=lambda s:H(hc(s),x)
        if code in(4,5):
            if to_linear:
                offset,scale,gate=('2e56','3b48','2d30')if code==4 else('2e5b','3b46','2d33')
                return lazy_select(a.gt(c(gate)),lambda:((a+c(offset))*c(scale)).pow(c('4072')),lambda:a*c('331c'))*x.sign()
            scale,offset,gate=('3c65','ae56','249c')if code==4 else('3c66','ae5b','249f')
            return lazy_select(a.gt(c(gate)),lambda:a.pow(c('3733'))*c(scale)+c(offset),lambda:a*c('4480'))*x.sign()
        if code==6:
            if to_linear:return lazy_select(a.gt(c('3800')),lambda:(((a+c('b87b'))*c('4598')).exp()+c('348e'))*c('2d55'),lambda:a.square()*c('3555'))*x.sign()
            const=c('39b9').log()*c('b1b9')+c('3800')
            return lazy_select(a.gt(c('2d55')),lambda:const+(a*c('4a00')+c('b48e')).log()*c('31b9'),lambda:(a*c('4200')).sqrt())*x.sign()
        if code==7:
            if to_linear:
                def positive():return (x*c('256a')).sqrt()+c('ab38')
                # Original upper branch is >=, including equality.
                return lazy_select(x.le(0)&x.ne(0),lambda:c('ab38'),lambda:lazy_select(x.lt(c('32ac')),positive,lambda:c('4000').pow((x+c('b98c'))*c('49d9'))+c('a0f0')))
            return lazy_select(x.gt(c('ab38'))&x.lt(c('211f')),lambda:(x+c('2b38')).square()*c('51e9'),lambda:lazy_select(x.lt(c('211f')),lambda:H(0,x),lambda:(x+c('20f0')).log(True)*c('2d79')+c('398c')))
        # Code8 really contains a zero divisor in this specialization's
        # linear direction. Preserve the selected finite small branch only.
        def undefined():raise DomainUnknown('Transfer8 selected original division by zero')
        if to_linear:return lazy_select(a.gt(c('1800')),undefined,lambda:a)*x.sign()
        return select(a.gt(c('1800')),c('b900'),a)*x.sign()
    return vec([one(rgb[i])for i in range(3)])
