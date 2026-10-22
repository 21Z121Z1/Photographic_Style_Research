"""Conditional domain intersections justified by existing AIR branch guards.

These do not alter a gate or remove an input: callers must keep the original
else branch in their output union. They never replace a set by its center.
"""
import numpy as np
from leaf_numeric import V,DomainUnknown


def strictly_positive_branch(value: V,threshold=0.):
    """Intersect a typed divisor with the already-selected value>threshold.

    A finite half/f32 divisor has a least representable value above threshold.
    The original strict comparison, including equality in its else, is retained.
    """
    dtype='f2'if value.precision=='h'else'f4';lower=np.asarray(threshold,dtype=dtype)
    if float(lower)<=float(threshold):lower=np.nextafter(lower,np.asarray(np.inf,dtype=dtype))
    if value.point:
        if value.lo<=threshold:raise DomainUnknown('Selected strict-positive branch is empty')
        return value
    lo=np.maximum(value.lo,float(lower))
    if np.any(lo>value.hi):raise DomainUnknown('Selected strict-positive branch contains no typed value')
    return V(lo,value.hi,value.precision,False)
