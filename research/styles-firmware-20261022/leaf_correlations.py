"""Exact shared-vector range facts, with unchanged original subtraction budget."""
import numpy as np
from leaf_numeric import V


def channel_span(x: V):
    """Bound max(x)-min(x), retaining that both extrema refer to the same RGB.

    Lower=max(0,max(lo)-min(hi)); upper=max(0,max_i!=j(hi_i-lo_j)).
    This bounds the original one subtraction, including its existing 2u budget.
    It does not reorder quotient/product arithmetic or assume a nonzero span.
    """
    if not isinstance(x,V)or x.lo.shape!=(3,):raise TypeError('One typed RGB required')
    if x.point:return x.max_channels()-x.min_channels()
    lo=max(0.,float(np.max(x.lo)-np.min(x.hi)));hi=max(0.,max(float(x.hi[i]-x.lo[j])for i in range(3)for j in range(3)if i!=j))
    return x.rounded(lo,hi)
