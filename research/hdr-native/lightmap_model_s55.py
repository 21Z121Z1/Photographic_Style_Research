"""Conditional scalar map generator model; original consumer/inverse untouched.

Input is the native histogram's already quantized p50 index, not scene pixels.
The complete shader has transfer/CCM/SRL/sampling/atomic paths outside this tail.
"""
import numpy as np
F=np.float32
H=np.float16
A=np.array([0x401c3d8f],dtype='<u4').view('<f4')[0]
B=np.array([0xbf87ede0],dtype='<u4').view('<f4')[0]
INV255=np.array([0x3b808081],dtype='<u4').view('<f4')[0]


def encode_tail(normalizer,p50):
    """AIR0002:706..720; ordered reference, no fitted coefficients."""
    product=F(F(F(normalizer)*A)*F(p50))
    inner=H(F(product+B))
    return H(F(F(F(inner)+F(1.2))*F(.29412)))


def decode_bucket_set(code_bits,normalizer):
    """All 256 histogram bucket indices compatible with this reference tail.

    This is conditional on known normalizer and this arithmetic contract;
    it is not an image inverse, RAW interval, or a full fast-math certificate.
    """
    encoded=np.asarray([encode_tail(normalizer,F(F(k)*INV255))for k in range(256)],dtype='<f2')
    return np.flatnonzero(encoded.view('<u2')==code_bits).tolist()
