"""Independent arithmetic leaf for the mapped saved-host SSA134..138 segment.

RN-even is an explicit assumption (FPCR was not measured). Domain guarantees
normal finite arithmetic or exact zero, so no subnormal/overflow claim is made.
This does not certify upstream square132 production or the full bright caller.
"""
from dataclasses import dataclass
import numpy as np
from leaf_numeric import V

PROFILE='bright-low-host-47185c09-half-rn-square-1over16-to1-v1'
PRODUCT_SHA='47185c09c0407d7c96aa9dc55e0581ae4e781836951c8b236d17f2ac6f8efbbe'


@dataclass(frozen=True)
class Low:
    s134:V
    s135:V
    s136:V
    s137:V
    s138:V


def forward(square:V):
    if not isinstance(square,V)or square.precision!='h'or not square.point or square.lo.shape!=(3,):
        raise TypeError('Explicit finite half3 point square132 required')
    if not np.isfinite(square.lo).all()or np.any(square.lo<1/16)or np.any(square.lo>1):
        raise ValueError('Mapped leaf working domain is square132 in [1/16,1]')
    if not np.array_equal(square.lo,square.lo.astype('f2').astype('f8')):
        raise ValueError('Exact binary16 operands required')
    s134=square*V.value(16)
    s135=square.fma_half(V.value(16),V.value(-12))
    s136=s135*square
    s137=s135.fma_half(square,V.value(4))
    return Low(s134,s135,s136,s137,s137*square)
