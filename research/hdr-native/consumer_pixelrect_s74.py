"""Source-derived finite ROI reference; separate from frozen RGB/image models.

Only positive-size finite CGRects and positive finite scales are implemented.
This scope does not filter any existing pixel mask or certify the consumer domain.
Rounding literals must come from the matching native metadata, never a guessed epsilon.
"""
import math
import struct

def literal_values(metadata):
    values=[]
    for row,address in zip(metadata['rounding_literals'],['0x1c5cf52a8','0x1c5cf5450'],strict=True):
        assert row['unslid']==address
        value=struct.unpack('<d',int(row['bits'],16).to_bytes(8,'little'))[0]
        assert math.isfinite(value)and value==row['value']
        values.append(value)
    return values

def _rect(rect):
    values=tuple(map(float,rect))
    if len(values)!=4 or not all(map(math.isfinite,values)) or min(values[2:])<=0:
        raise ValueError('Only positive-size finite CGRect controls are supported')
    return values

def _minmax(left,top,right,bottom,ca,cb):
    if not all(map(math.isfinite,[left,top,right,bottom,ca,cb])):
        raise ValueError('Nonfinite geometry is not certified')
    x,y=math.floor(left+ca),math.floor(top+ca)
    hi_x,hi_y=math.ceil(right+cb),math.ceil(bottom+cb)
    result=[x,y,hi_x-x,hi_y-y]
    if min(result[2:])<0 or not all(-(1<<63)<=v<(1<<63)for v in result):
        raise ValueError('Signed-long overflow or reversed bounds is not certified')
    return result

def from_cgrect(rect,ca,cb):
    x,y,w,h=_rect(rect)
    return _minmax(x,y,x+w,y+h,ca,cb)

def scale_pixelrect(pixel_rect,scale,ca,cb):
    x,y,w,h=pixel_rect;sx,sy=map(float,scale)
    if not all(isinstance(v,int)and -(1<<63)<=v<(1<<63)for v in pixel_rect):
        raise ValueError('PixelRect must contain four signed long integers')
    if min(w,h)<0 or not all(math.isfinite(v)and v>0 for v in[sx,sy]):
        raise ValueError('Only nonnegative sizes and positive finite scales are supported')
    left,top=float(x)*sx,float(y)*sy
    right,bottom=left+float(w)*sx,top+float(h)*sy
    return _minmax(left,top,right,bottom,ca,cb)

def flip_cgrect(rect,bounds):
    x,y,w,h=_rect(rect);bx,by,bw,bh=_rect(bounds)
    return[x-bx,(by+bh)-(y+h),w,h]

def reference_case(case,ca,cb):
    first=from_cgrect(case['rect'],ca,cb)
    scaled=scale_pixelrect(first,case['scale'],ca,cb)
    return{'case':case['id'],'from_pixel_rect':first,'from_CGRect':list(map(float,first)),
           'scaled_pixel_rect':scaled,'scaled_CGRect':list(map(float,scaled)),
           'flipped_CGRect':flip_cgrect(scaled,case['bounds'])}
