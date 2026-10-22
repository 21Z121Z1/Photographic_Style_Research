"""Whole-window affine enclosures with shared texels and host FMA order.

A center plus named [-1,1] generators represents the WHOLE input box. Centers
are never substituted for unknown inputs. Each original f32 arithmetic/FMA
gets the existing 2u+tiny allowance; half conversions retain all possible bins.
This is a CPU sampler/rounding contract, not a measured iOS GPU error bound.
"""
import itertools,math
from dataclasses import dataclass
import numpy as np
from leaf_numeric import V,DomainUnknown

IDS=itertools.count()


@dataclass(frozen=True)
class A:
    c: float
    terms: dict
    clip: tuple|None=None

    @classmethod
    def box(cls,lo,hi):
        lo=float(lo);hi=float(hi);mid=lo+(hi-lo)*.5;r=max(mid-lo,hi-mid)
        return cls(mid,{}if not r else{next(IDS):r},(lo,hi))

    @classmethod
    def value(cls,x):return cls(float(x),{})
    def radius(self):return math.fsum(abs(v)for v in self.terms.values())
    def bounds(self):
        r=self.radius();lo=math.nextafter(self.c-r,-math.inf)if r else self.c;hi=math.nextafter(self.c+r,math.inf)if r else self.c
        if self.clip is not None:lo=max(lo,self.clip[0]);hi=min(hi,self.clip[1])
        if not math.isfinite(lo+hi)or lo>hi:raise DomainUnknown('Affine enclosure nonfinite/unordered')
        return lo,hi
    def noise(self,lo,hi):
        mid=lo+(hi-lo)*.5;r=max(mid-lo,hi-mid);d=dict(self.terms)
        if r:d[next(IDS)]=r
        return A(self.c+mid,d)
    def guard(self):
        # Conservative f64 bookkeeping only, separate from the unchanged f32
        # primitive budget. Never reduces an enclosure or modifies a threshold.
        e=(len(self.terms)+4)*2**-52*max(abs(self.c),self.radius(),2**-149)
        return self.noise(-e,e)
    def neg(self):return A(-self.c,{k:-v for k,v in self.terms.items()},None if self.clip is None else(-self.clip[1],-self.clip[0]))
    def add(self,b):
        b=b if isinstance(b,A)else A.value(b);d=dict(self.terms)
        for k,v in b.terms.items():d[k]=d.get(k,0)+v
        return A(self.c+b.c,{k:v for k,v in d.items()if v}).guard()
    def scale(self,b):return A(self.c*b,{k:v*b for k,v in self.terms.items()if v*b}).guard()
    def product(self,b):
        d={k:self.c*b.terms.get(k,0)+b.c*self.terms.get(k,0)for k in self.terms.keys()|b.terms.keys()};diag=[v*b.terms[k]for k,v in self.terms.items()if k in b.terms];cross=max(0.,self.radius()*b.radius()-math.fsum(abs(v)for v in diag));lo=math.fsum(v for v in diag if v<0)-cross;hi=math.fsum(v for v in diag if v>0)+cross
        return A(self.c*b.c,{k:v for k,v in d.items()if v}).noise(lo,hi).guard()
    def rounded(self):
        lo,hi=self.bounds();e=2**-23*max(abs(lo),abs(hi))+2**-149
        return self.noise(-e,e)
    def fadd(self,b):return self.add(b).rounded()
    def fma(self,b,c):return self.product(b).add(c).rounded()
    def div(self,b):
        lo,hi=b.bounds()
        if lo<=0<=hi:raise DomainUnknown('Shared guided denominator still includes zero')
        if b.c==0:raise DomainUnknown('Affine reciprocal expansion at zero')
        r=b.radius();q=b.scale(-1/(b.c*b.c)).add(2/b.c);rem=r*r/(b.c*b.c*min(abs(lo),abs(hi)))
        q=q.noise(0,rem)if lo>0 else q.noise(-rem,0)
        return self.product(q).rounded()
    def half(self,*,sampler=False):
        lo,hi=self.bounds()
        if max(abs(lo),abs(hi))>65504:raise DomainUnknown('Finite arithmetic budget exceeded')
        def convert(x):
            h=np.float16(x)
            if sampler and x>float(h):
                up=np.nextafter(h,np.float16(np.inf))
                if x==(float(h)+float(up))*.5:return float(up)
            return float(h)
        lower,upper=convert(lo),convert(hi)
        if lower==upper:return A.value(lower)
        e=2**-11*max(abs(lo),abs(hi))+2**-25
        a=self.noise(-e,e)
        return A(a.c,a.terms,(lower,upper))


def field(a):
    a=np.asarray(a,dtype=object);lo=np.empty(a.shape);hi=lo.copy()
    for index in np.ndindex(a.shape):lo[index],hi[index]=a[index].bounds()
    return V.bounds(lo,hi)


def forward_set(gain,guide,epsilon,output_shape,*,diagnostics=None):
    def image(v):
        a=np.empty(v.lo.shape,dtype=object)
        for i in np.ndindex(a.shape):a[i]=A.box(v.lo[i],v.hi[i])
        return a
    p=image(gain);g=image(guide);eps=A.box(epsilon.lo,epsilon.hi);h,w,c=*g.shape[:2],p.shape[2];cache={}
    def sample(a,u,v,token):
        height,width,channels=a.shape;x=np.float32(u)*np.float32(width)-np.float32(.5);y=np.float32(v)*np.float32(height)-np.float32(.5);ix=int(np.floor(x));iy=int(np.floor(y));fx=float(np.rint((x-ix)*256)/256);fy=float(np.rint((y-iy)*256)/256);xs=[min(max(ix+i,0),width-1)for i in range(2)];ys=[min(max(iy+i,0),height-1)for i in range(2)];key=(token,*xs,*ys,fx,fy)
        if key in cache:return cache[key]
        out=[]
        for lane in range(channels):
            aa,bb,cc,dd=[a[yy,xx,lane]for yy,xx in [(ys[0],xs[0]),(ys[0],xs[1]),(ys[1],xs[0]),(ys[1],xs[1])]]
            # C shim q10-q00 and q11-q01 are original f32 subtractions,
            # followed by FMA; sampling conversion uses declared v3 tie-up.
            top=bb.add(aa.neg()).rounded().fma(A.value(fx),aa);bottom=dd.add(cc.neg()).rounded().fma(A.value(fx),cc);out.append(bottom.add(top.neg()).rounded().fma(A.value(fy),top).half(sampler=True))
        cache[key]=out;return out
    result={k:np.empty((h,w,c),dtype=object)for k in ['a','b','mean_p','mean_i','mean_ip','mean_ii','cov','epsilon_plus_mii','var','a_f32','b_f32','sum_p','sum_i','sum_ip','sum_ii']};inv=A.value(np.float32(1/9))
    for y in range(h):
        for x in range(w):
            sp=[A.value(0)for _ in range(c)];si=sp.copy();sip=sp.copy();sii=sp.copy()
            for dx in range(-1,2):
                for dy in range(-1,2):
                    u=np.float32(x+np.float32(.5+dx))/np.float32(w);v=np.float32(y+np.float32(.5+dy))/np.float32(h);pv=sample(p,u,v,'input');iv=sample(g,u,v,'guide')
                    if len(iv)==1:iv=iv*c
                    for i in range(c):sp[i]=pv[i].fadd(sp[i]);si[i]=iv[i].fadd(si[i]);sip[i]=iv[i].fma(pv[i],sip[i]);sii[i]=iv[i].fma(iv[i],sii[i])
            for i in range(c):
                mp=sp[i].product(inv).rounded();mi=si[i].product(inv).rounded();mip=sip[i].product(inv).rounded();mii=sii[i].product(inv).rounded();cov=mi.neg().fma(mp,mip);ep=sii[i].fma(inv,eps);var=mi.neg().fma(mi,ep);av=cov.div(var);bv=av.neg().fma(mi,mp)
                for name,value in zip(result,[av.half(),bv.half(),mp,mi,mip,mii,cov,ep,var,av,bv,sp[i],si[i],sip[i],sii[i]]):result[name][y,x,i]=value
    mean={k:np.empty((h,w,c),dtype=object)for k in ['mean_a','mean_b']}
    for y in range(h):
        for x in range(w):
            sa=[A.value(0)for _ in range(c)];sb=sa.copy()
            for dx in range(-1,2):
                for dy in range(-1,2):
                    xx=min(max(x+dx,0),w-1);yy=min(max(y+dy,0),h-1)
                    for i in range(c):sa[i]=sa[i].fadd(result['a'][yy,xx,i]);sb[i]=sb[i].fadd(result['b'][yy,xx,i])
            for i in range(c):mean['mean_a'][y,x,i]=sa[i].product(inv).rounded().half();mean['mean_b'][y,x,i]=sb[i].product(inv).rounded().half()
    oh,ow=output_shape;out=np.empty((oh,ow,c),dtype=object)
    for y in range(oh):
        for x in range(ow):
            u=np.float32(x+.5)/np.float32(ow);v=np.float32(y+.5)/np.float32(oh);aa=sample(mean['mean_a'],u,v,'mean_a');bb=sample(mean['mean_b'],u,v,'mean_b');iv=sample(g,u,v,'guide')
            if len(iv)==1 and c>1:iv=[iv[0]]+[A.value(1 if i==3 else 0)for i in range(1,c)]
            for i in range(c):out[y,x,i]=iv[i].fma(aa[i],bb[i]).half()
    if diagnostics is not None:
        for name,arr in result.items():
            values=[a.bounds()for a in arr.flat];diagnostics[name]={'min':min(a for a,b in values),'max':max(b for a,b in values),'max_width':max(b-a for a,b in values)}
        diagnostics['stage_bounds']={name:{'lo':[[[a.bounds()[0]for a in row]for row in plane]for plane in arr],'hi':[[[a.bounds()[1]for a in row]for row in plane]for plane in arr]}for name,arr in result.items()}
        diagnostics['sampled_gain_max_width']=max((a.bounds()[1]-a.bounds()[0]for k,vs in cache.items()if k[0]=='input'for a in vs),default=0);diagnostics['sampled_guide_max_width']=max((a.bounds()[1]-a.bounds()[0]for k,vs in cache.items()if k[0]=='guide'for a in vs),default=0);diagnostics['contract']='shared affine input generators and reused sampled values; actual ARM64 FMA order; unchanged 2u f32 primitive budget; explicit half bins'
    return {'a':field(result['a']),'b':field(result['b']),**{k:field(v)for k,v in mean.items()},'output':field(out)}
