"""Original CPU statistics matte UV encoding in a positive full-frame context.
This encodes supplied crop metadata; it cannot identify a camera/CI caller or
certify the complete shader/sampler domain. Never install it over frozen inputs.
"""
import math,struct

def rn32(value):
    try:return struct.unpack('<f',struct.pack('<f',value))[0]
    except OverflowError:return math.copysign(math.inf,value)

def full_frame_uv(main_size,mask_size,crop=(0.,0.,0.,0.)):
    if len(main_size)!=2 or len(mask_size)!=2 or len(crop)!=4:
        raise ValueError('main/mask extents and a four-component crop required')
    if not all(isinstance(x,int)and not isinstance(x,bool)and 0<x<=65535 for x in (*main_size,*mask_size)):
        raise ValueError('positive integer dimensions in the declared helper scope')
    ox,oy,cw,ch=map(float,crop)
    if not all(math.isfinite(x)for x in (ox,oy,cw,ch)):
        raise ValueError('finite crop required')
    if not ((cw==0 and ch==0)or(cw>0 and ch>0)):
        raise ValueError('zero/zero or positive crop extent required')
    # _calculateROIShift: sequential double divides, then float -> double.
    if cw==0 and ch==0:
        # Original checker fallback converts the texture dimension to float.
        sx,sy=(rn32(1./rn32(n))for n in mask_size)
    else:
        sx=rn32((cw/main_size[0])/mask_size[0])
        sy=rn32((ch/main_size[1])/mask_size[1])
    # _encodeRenderRegionForStats: delta narrowed before float division.
    bx=rn32(rn32(ox)/rn32(mask_size[0]))
    by=rn32(rn32(oy)/rn32(mask_size[1]))
    if not all(math.isfinite(x)for x in (sx,sy,bx,by)):
        raise ValueError('encoded UV outside finite helper scope')
    return sx,sy,bx,by
