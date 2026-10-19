"""26A434 CMI scalar display-headroom helpers, separate from pixel GTM/LTM.

Source: original helpers0x2333c8994/0x2333c89fc, native run39330883147.
These functions do not undo tone curves, image exposure, local tone, or j.
Actual use on a photograph requires evidence of the applied helper branch;
Styles k alone has not been bound to that runtime decision in this research.
"""
import math
import struct

OS_BUILD = '26A434'
FORWARD_EXPONENT = struct.unpack('<d',bytes.fromhex('cff753e3a59be43f'))[0]
INVERSE_EXPONENT = struct.unpack('<d',bytes.fromhex('206c3c9a3fd8f83f'))[0]

def f32(value):
    return struct.unpack('<f',struct.pack('<f',value))[0]

def evaluate_helper(headroom,*,cast_is_long_gray,inverse=False):
    """Reproduce only the positive-finite/nonnegative tested scalar formula.

    Explicit finite domain here is an API boundary, not a change to any image
    inverse mask or a native nonfinite-behaviour guarantee. No implicit clamp.
    """
    if type(cast_is_long_gray)is not bool or type(inverse)is not bool:
        raise TypeError('Explicit boolean helper branch is required')
    h=f32(headroom)
    if not math.isfinite(h)or h<0:
        raise ValueError('Only nonnegative finite scalar headroom is modelled')
    if cast_is_long_gray:
        h=f32(math.pow(h,INVERSE_EXPONENT if inverse else FORWARD_EXPONENT))
    if not math.isfinite(h):
        raise ValueError('Result outside finite scalar helper contract')
    return h

def restore_recorded_headroom(current,*,cast_is_long_gray,applied_branch):
    """Undo a caller-confirmed helper application; unknown context is rejected.

    applied_branch must come from an authenticated caller/metadata contract,
    not a guess based on appearance or a helper/field name.
    """
    if type(applied_branch)is not bool:
        raise ValueError('Applied headroom branch has not been identified')
    return evaluate_helper(current,cast_is_long_gray=cast_is_long_gray if applied_branch else False,inverse=applied_branch)
