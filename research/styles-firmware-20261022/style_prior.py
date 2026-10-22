"""Conditional prior updates from iPhone17,3/24A446 CMImaging AIR108/109.

The color-space conversion, tone/color/intensity->CCM, upstream reduction and
solver are external inputs. These are coefficient-buffer operations, not pixel
GTM/LTM, face gain, or a complete style inverse. Explicit f32 rounding models
the written IR operations; fast-math GPU contraction/denormals are uncertified.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray

F32 = NDArray[np.float32]


def finite_vector(value, size: int, name: str) -> F32:
    a = np.array(value, dtype=np.float32, copy=True)
    if a.shape != (size,) or not np.isfinite(a).all():
        raise ValueError(f'{name} needs {size} finite f32 values')
    return a


@dataclass(frozen=True)
class SystemLayout:
    polynomial_count: int
    system_size: int
    weight_plane_count: int

    def __post_init__(self):
        # A bounded model domain, not Apple's validation behavior.
        if self.polynomial_count not in (4, 7, 10):
            raise ValueError('Model supports polynomial counts 4, 7, 10')
        if not 1 <= self.system_size <= 1024 or not 1 <= self.weight_plane_count <= 1024:
            raise ValueError('Model layout budget exceeded')


@dataclass(frozen=True)
class PriorFactors:
    constant: float
    linear: float
    quadratic: float

    def array(self) -> F32:
        return finite_vector((self.constant,self.linear,self.quadratic),3,'prior factors')


def factors_from_reduced_sum(reduced_sum: float, layout: SystemLayout, lambdas: PriorFactors) -> PriorFactors:
    """CalculatePrior AIR107 SSA98..126, *after* caller's actual SIMD reduction.

    No replacement of the GPU reduction order by a NumPy sum is claimed. Both
    RHS factors (constant/linear) equal the corresponding LHS factors for P>=4.
    """
    total = finite_vector([reduced_sum],1,'reduced sum')[0]
    mean = np.float32(total / np.float32(layout.system_size * layout.polynomial_count))
    values = np.maximum(np.float32(2**-23), np.multiply(lambdas.array(),mean,dtype=np.float32))
    return PriorFactors(*map(float,values))


@dataclass(frozen=True)
class BufferUpdates:
    offsets: NDArray[np.int64]
    additions: F32
    native_gpu_verified: bool = False

    def apply(self, buffer) -> F32:
        a = np.array(buffer,dtype=np.float32,copy=True)
        if a.ndim != 1 or not np.isfinite(a).all():
            raise ValueError('Need a finite one-dimensional coefficient buffer')
        if len(self.offsets) and self.offsets.max() >= len(a):
            raise ValueError('Coefficient buffer is too short for actual offsets')
        a[self.offsets] = np.add(a[self.offsets], self.additions,dtype=np.float32)
        return a


def grid_ids(gids) -> NDArray[np.int64]:
    a = np.asarray(gids)
    if a.ndim != 1 or a.dtype.kind not in 'iu' or np.any(a < 0) or np.any(a > 65535):
        raise ValueError('Need a vector of ushort grid IDs')
    if len(np.unique(a)) != len(a):
        raise ValueError('Duplicate grid IDs would make write ordering ambiguous')
    return a.astype(np.int64)


def lhs_updates(layout: SystemLayout, gids, factors: PriorFactors, weight_plane_scales) -> BufferUpdates:
    """AIR108: only diagonal-address writes; degree group is 0 / 1..3 / >3."""
    g = grid_ids(gids); p=layout.polynomial_count
    factors_ = factors.array()
    scale = finite_vector(weight_plane_scales,layout.weight_plane_count*3,'prior plane scales').reshape(-1,3)
    term = g % p; degree = np.where(term == 0,0,np.where(term > 3,2,1))
    plane = (g // p) % layout.weight_plane_count
    delta = np.multiply(scale[plane,degree], factors_[degree],dtype=np.float32)
    offsets = (layout.system_size * p + 1) * g
    return BufferUpdates(offsets,delta)


def rhs_updates(layout: SystemLayout, gids, factors: PriorFactors, weight_plane_scales, prior_matrix) -> BufferUpdates:
    """AIR109: priorMatrix is a flat 12-float buffer; do not infer RGB ordering.

    The three constant slots use factor[0], next nine use factor[1]. Row/column
    orientation of the upstream CCM is intentionally not guessed here.
    """
    g=grid_ids(gids);p=layout.polynomial_count;term=g % 12;block=g // 12
    group=(term > 2).astype(np.int64)
    factors_=factors.array()
    scale=finite_vector(weight_plane_scales,layout.weight_plane_count*3,'prior plane scales').reshape(-1,3)
    prior=finite_vector(prior_matrix,12,'flat prior matrix')
    delta=np.multiply(factors_[group],scale[block % layout.weight_plane_count,group],dtype=np.float32)
    delta=np.multiply(delta,prior[term],dtype=np.float32)
    return BufferUpdates(3*p*block+term,delta)
