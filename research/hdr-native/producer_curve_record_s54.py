"""Conditional decoder for the 24A446 LTMMetadataWriterV2 global records.

This is a record/quantizer model, NOT the camera's pixel application model.
No photography, NumPy, scene exposure estimate, or changes to frozen models.
The interval contract assumes binary32 round-to-nearest/ties-to-even, FPCR=0.
"""
import math
import struct


def f32(x):
    return struct.unpack('<f', struct.pack('<f', x))[0]


def from_bits(bits):
    return struct.unpack('<f', struct.pack('<I', bits))[0]


def quantize_node(value):
    """FMINNM(value,1), FMAXNM(result,0), binary32 *65535, floor, u16.

    Python float conversion quiets signaling NaNs. Use quantize_bits() for raw NaN identity.
    Host exceptions on arbitrary Python values are not iOS exception evidence.
    """
    x = f32(value)
    clipped = 1.0 if math.isnan(x) else min(x, 1.0)
    clipped = max(clipped, 0.0)
    return math.floor(f32(clipped * 65535.0))


def first_nonnegative_bits_at_code(code):
    """First nonnegative finite f32 with Q(x)>=code, for 1<=code<=65535.

    IEEE binary32 multiplication by a positive constant and floor are
    monotone. Ordered positive f32 bits support an exact discrete lower bound.
    The product of two f32 inputs is exactly representable in Python binary64;
    f32() performs the one required binary32 rounding.
    """
    if type(code) is not int or not 1 <= code <= 65535:
        raise ValueError('code must be an integer in 1..65535')
    lo, hi = 0, 0x3f800000
    while lo < hi:
        middle = (lo + hi) // 2
        if quantize_node(from_bits(middle)) >= code:
            hi = middle
        else:
            lo = middle + 1
    return lo


def node_preimage(code):
    """Exact finite-f32 preimage endpoints of the declared quantizer only.

    Null bound means unbounded before the clamp, NOT a recovered value.
    Positive-normalized interior bounds are lower-inclusive/upper-exclusive.
    NaN/infinity routing is reported separately from the finite interval.
    """
    if type(code) is not int or not 0 <= code <= 65535:
        raise ValueError('invalid uint16 code')
    lower = first_nonnegative_bits_at_code(code) if code else None
    upper = first_nonnegative_bits_at_code(code + 1) if code < 65535 else None
    return {
        'code': code,
        'lower_f32': from_bits(lower) if lower is not None else None,
        'upper_f32_exclusive': from_bits(upper) if upper is not None else None,
        'lower_bits': lower,
        'upper_bits_exclusive': upper,
        'lower_unbounded_by_clamp': code == 0,
        'upper_unbounded_by_clamp': code == 65535,
        'special_inputs': (['negative_infinity', 'signaling_NaN_under_FPCR0'] if code == 0 else
                           ['positive_infinity', 'quiet_NaN_under_FPCR0']
                           if code == 65535 else []),
        'scope': '24A446 writer scalar quantizer, conditional FPCR=0; not full consumer proof',
    }


def decode_global_record(raw):
    """The writer emits 258 little-endian uint16s: 257 header +257 nodes."""
    if len(raw) != 516:
        raise ValueError('only the statically identified 516-byte record is supported')
    words = struct.unpack('<258H', raw)
    if words[0] != 257:
        raise ValueError('unrecognized node-count header')
    return {'node_count': 257, 'codes': list(words[1:]),
            'preimages': [node_preimage(x) for x in words[1:]],
            'application_domain': 'unidentified: require same-frame application capture',
            'scene_linear_certified': False}


def ios_gtc_input_ratios(raw):
    """Only the ratio stage in iOS CMI _createGlobalToneCurveTexture.

    This 257-header branch reads words[1..256], divisor words[256].
    It does not read words[257]. Transfer-function decoding and half storage
    follow this stage in original code; no claim about a file key3 binding.
    """
    record = decode_global_record(raw)
    codes = record['codes']
    if codes[255] == 0:
        raise ValueError('zero normalization divisor: retain nonfinite-path obligation')
    return [x / codes[255] for x in codes[:256]]


def quantize_bits(bits):
    """Exact raw f32 NaN distinction; conditional FPCR=0, exceptions disabled.

    FMINNM(sNaN,1) quiets it; FMAXNM(qNaN,0) then chooses zero.
    FMINNM(qNaN,1) chooses one; the remaining quantizer gives 65535.
    This CPU chain is not Metal's clamp/fast-math contract.
    """
    if type(bits) is not int or not 0 <= bits <= 0xffffffff:
        raise ValueError('expected raw uint32 float bits')
    exponent = bits & 0x7f800000
    mantissa = bits & 0x007fffff
    if exponent == 0x7f800000 and mantissa:
        return 65535 if bits & 0x00400000 else 0
    return quantize_node(from_bits(bits))
