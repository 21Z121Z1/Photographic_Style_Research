"""Requested CI ROI model, finite rectangles only; no texture allocation model.
The branch/reference formula was frozen before S73's native54 controls. This
standalone implementation was added after the capture, not a new holdout. It
neither replaces frozen context nor certifies the consumer's full shader domain.
"""
import math

def rect4(value):
    if len(value)!=4:raise ValueError('four rectangle components required')
    v=tuple(map(float,value))
    if not all(math.isfinite(x)for x in v):raise ValueError('finite fixture scope only')
    return v

def requested_roi(index,extents,output):
    if not isinstance(index,int)or isinstance(index,bool)or index<0:
        raise ValueError('nonnegative integer input index required')
    out=rect4(output)
    if index==0:return tuple(out)
    if not 0<=index<len(extents):raise ValueError('input extent unavailable')
    dst=rect4(extents[index])
    if 6<=index<=8:return tuple(dst)
    src=rect4(extents[0])
    if src[2]<=0 or src[3]<=0:raise ValueError('positive main extent required')
    return (dst[0]+(out[0]-src[0])*dst[2]/src[2],
            dst[1]+(out[1]-src[1])*dst[3]/src[3],
            out[2]*dst[2]/src[2],out[3]*dst[3]/src[3])
