"""New SDR identity-edit context from this image's measured linear P3 pixels.

Texture per-person statistics come from the separate original Apple producers.
This module makes the ordinary Styles prerequisite; it does not reconstruct a
camera's RAW, exposure, original tone mapping, or original capture statistics.
"""
import array
import hashlib
import json
import math
from pathlib import Path
import plistlib
import struct
import sys


def gamma(value):
    return 12.92 * value if value <= 0.0031308 else 1.055 * value ** (1 / 2.4) - 0.055


def apple_log(value):
    # Apple's published Apple Log transfer function, applied to newly derived
    # linear image values, rather than an assertion about camera encoding.
    if value >= 0.01:
        return 0.08550479 * math.log2(value + 0.00964052) + 0.69336945
    return 47.28711236 * (max(-0.05641088, value) + 0.05641088) ** 2


def distribution(values):
    values = sorted(values)
    if not values:
        raise ValueError('an expected inferred population is empty')
    def q(percent):
        pos = percent * (len(values) - 1) / 100
        lo, hi = math.floor(pos), math.ceil(pos)
        return values[lo] * (1 - (pos - lo)) + values[hi] * (pos - lo)
    return {key: q(p) for key, p in [('blackPoint', .5), ('highKey', 95), ('p02', 2), ('p10', 10),
                                    ('p25', 25), ('p50', 50), ('p75', 75), ('p98', 98), ('whitePoint', 99.5)]}


def main(root):
    production = json.loads((root / 'carrier-production.json').read_text())
    width, height = production['width'], production['height']; count = width * height
    raw = (root / 'native-linear-p3.rgba32f').read_bytes()
    stats = json.loads((root / 'mattify-type1-Studio-EV0.json').read_text())
    assert hashlib.sha256(raw).hexdigest() == stats['linear_RGBA32f_for_derived_styles_sha256']
    rgba = array.array('f'); rgba.frombytes(raw)
    if sys.byteorder != 'little': rgba.byteswap()
    assert len(rgba) == count * 4 and all(math.isfinite(v) and v >= 0 for v in rgba)
    rgb = [tuple(rgba[i * 4:i * 4 + 3]) for i in range(count)]
    encoded = [tuple(gamma(v) for v in pixel) for pixel in rgb]
    luma = lambda p: .22897456 * p[0] + .69173852 * p[1] + .07928691 * p[2]
    linear = [luma(p) for p in rgb]; tone = [luma(p) for p in encoded]; mapped = [gamma(v) for v in linear]
    skin = (root / 'semanticskinmattev2.l8').read_bytes(); person = (root / 'semanticpersonmatte.l8').read_bytes()
    assert len(skin) == len(person) == count
    subset = lambda values, mask: [v for v, m in zip(values, mask) if m >= 128]
    distributions = {'LinearGTCImage': distribution(mapped), 'LinearImage': distribution(linear),
                     'LinearImagePersonSegmentBased': distribution(subset(linear, person)),
                     'LinearImageSkinBased': distribution(subset(linear, skin)), 'ToneMappedImage': distribution(tone),
                     'ToneMappedImagePersonSegmentBased': distribution(subset(tone, person)),
                     'ToneMappedImageSkinBased': distribution(subset(tone, skin))}
    for c, name in enumerate(['Red', 'Green', 'Blue']):
        distributions['ToneMappedImage' + name + 'ChannelSkinBased'] = distribution(subset([p[c] for p in encoded], skin))
    def lightmap(values):
        output = bytearray()
        for y in range(32):
            for x in range(32):
                xs = range(x * width // 32, max(x * width // 32 + 1, (x + 1) * width // 32))
                ys = range(y * height // 32, max(y * height // 32 + 1, (y + 1) * height // 32))
                mean = sum(values[yy * width + xx] for yy in ys for xx in xs) / (len(xs) * len(ys))
                output.extend(struct.pack('<e', min(1, max(0, mean))))
        return bytes(output)
    block = b''.join(struct.pack('<e', float(i in [3, 7, 11])) for i in range(30))
    identity = block * (12 * 9 * 8)
    assert hashlib.sha256(identity).hexdigest() == '43e0ae73508cc10684d4be708fa1d19f3b55b8de15cb8e3544ef16300db91dbe'
    curve = struct.pack('<H', 257) + b''.join(struct.pack('<H', round(gamma(i / 255) * 65534)) for i in range(256)) + struct.pack('<H', 65534)
    document = {'0': 16, '1': identity, '2': True, '3': curve, '4': 0.0, '5': 0, '6': distributions,
                '7': {'PeopleRatio': sum(person) / (255 * count), 'SkinRatio': sum(skin) / (255 * count), 'PersonMasksValidHint': 1.0},
                'c': lightmap(tone), 'd': lightmap(mapped), 'e': 32, 'f': 32, 'g': 0x4C303068,
                'h': 1.0, 'i': {'Gain': 1.0, 'OriginalRangeMin': min(linear), 'OriginalRangeMax': max(linear)},
                'j': 0.0, 'k': False, 'l': False}
    metadata = plistlib.dumps(document, fmt=plistlib.FMT_BINARY, sort_keys=True)
    (root / 'derived-styles.bplist').write_bytes(metadata)
    thumbnail = array.array('f')
    for pixel in rgb: thumbnail.extend([*(apple_log(v) for v in pixel), 1.0])
    if sys.byteorder != 'little': thumbnail.byteswap()
    (root / 'derived-applelog-thumbnail.rgba32f').write_bytes(thumbnail.tobytes())
    report = {'schema': 'derived-sdr-identity-styles-v1', 'original_camera_reconstructed': False,
              'input_linear_p3_sha256': hashlib.sha256(raw).hexdigest(), 'metadata_sha256': hashlib.sha256(metadata).hexdigest(),
              'thumbnail_encoding': 'published Apple Log function applied to this image-derived linear P3',
              'tone_pipeline': 'new sRGB-transfer SDR identity edit, exposure 0, gains 1, no extra face boost',
              'mask_population_statistics': distributions, 'people_and_skin_ratios': document['7']}
    (root / 'derived-styles.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__': main(Path(sys.argv[1]))
