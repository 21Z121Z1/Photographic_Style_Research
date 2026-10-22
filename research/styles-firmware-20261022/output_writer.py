"""AIR10 25..27/601..618 RGBA packing and conditional ROI tile writes."""
from dataclasses import dataclass
import numpy as np
from leaf_numeric import V,DomainUnknown
from texture_numeric import Texture,PixelFormat,rgba


@dataclass(frozen=True)
class Controls:
    logical_origin: tuple[int,int]
    output_offset12: tuple[int,int]
    render_edge2: tuple[int,int]
    imageblock: bool

    def __post_init__(self):
        if any(not isinstance(v,tuple)or len(v)!=2 or any(type(x)is not int or not 0<=x<=65535 for x in v)for v in [self.logical_origin,self.output_offset12,self.render_edge2])or type(self.imageblock)is not bool:raise TypeError('Three exact ushort2 values and original imageblock flag required')


@dataclass(frozen=True)
class Result:
    output: Texture
    written_pixels: np.ndarray
    leader_destination27: tuple[int,int]
    copy_extent614: tuple[int,int]|None
    original_GPU_executed: bool=False


def forward(frame: Texture,rgb600: V,controls: Controls):
    if frame.pixel_format!=PixelFormat.RGBA16Float or not isinstance(rgb600,V)or rgb600.precision!='h'or rgb600.point!=frame.pixels.point or len(rgb600.lo.shape)!=3 or rgb600.lo.shape[2]!=3:raise TypeError('Matching supplied half RGB600 tile and explicit RGBA16 output storage required')
    h,w=rgb600.lo.shape[:2]
    if not 1<=h<=32 or not 1<=w<=32:raise TypeError('Explicit active imageblock tile sides1..32 required')
    a=frame.pixels.lo.copy();b=frame.pixels.hi.copy();written=np.zeros(a.shape[:2],dtype=bool);packed=rgba(rgb600);dest=tuple((x+y)&65535 for x,y in zip(controls.logical_origin,controls.output_offset12));extent=None
    if controls.imageblock:
        extent=tuple(min(n,(edge-origin)&65535)for n,edge,origin in zip((w,h),controls.render_edge2,dest));cw,ch=extent
    else:cw,ch=w,h
    for y in range(ch):
        for x in range(cw):
            dx,dy=(dest[0]+x)&65535,(dest[1]+y)&65535
            if not(0<=dy<a.shape[0]and 0<=dx<a.shape[1]):raise DomainUnknown('Writer address outside supplied target; hardware out-of-bounds semantics not assumed')
            a[dy,dx]=packed.lo[y,x];b[dy,dx]=packed.hi[y,x];written[dy,dx]=True
    return Result(Texture(V(a,b,'h',frame.pixels.point),PixelFormat.RGBA16Float,frame.working_domain),written,dest,extent)


def from_output_grid(frame,output_grid,controls,*,input_branch_decisions=()):
    """Carry complete pixel_output.Result boxes into packing; never centers."""
    if not output_grid or not output_grid[0]or any(len(row)!=len(output_grid[0])for row in output_grid):raise TypeError('Nonempty rectangular upstream output grid required')
    values=[[item.output600 for item in row]for row in output_grid]
    if any(not isinstance(v,V)or v.point or v.precision!='h'or v.lo.shape!=(3,)for row in values for v in row):raise TypeError('Whole upstream output600 sets required')
    tile=V(np.stack([[v.lo for v in row]for row in values]),np.stack([[v.hi for v in row]for row in values]),'h',False)
    return forward(frame,tile,controls),tuple(input_branch_decisions)
