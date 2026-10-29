"""Export complete HEIC files for the user's own Photos editing comparison."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from . import blind, corpus, isolate, native
from .joint_spatial import JOINT


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('adapter', 'generator', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--input', type=Path, action='append', required=True)
    args = parser.parse_args(argv)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    folders = {key: output / 'heic' / name for key, name in (
        ('original', '01_original'), ('before', '02_before_default'), ('after', '03_after_joint'))}
    for directory in folders.values():
        directory.mkdir(parents=True)
    report = {'schema': 'styles-editable-heic-export-v1', 'passed': False,
              'photos_ui_verified': False, 'product_defaults_changed': False,
              'scope': 'Complete generated HEICs and native full-resolution base preservation; user Photos editing remains unverified.',
              'calibrations': {'before': blind.DEFAULT, 'after': JOINT}, 'cases': []}
    try:
        with tempfile.TemporaryDirectory(prefix='editable-heic-', dir=output) as temporary:
            work = Path(temporary)
            for index, source in enumerate(args.input):
                source = source.resolve()
                if corpus.inspect_bytes(source.read_bytes())['standard_semantic_state'] is not True:
                    raise ValueError('Standard reference required')
                case_work = work / str(index)
                case_work.mkdir()
                width, height = native.display_geometry(isolate.Graph(source.read_bytes()))
                reference = native.readback(args.adapter, source, case_work / 'reference', width, height)
                headroom = reference['hdr_content_headroom']
                source_hash = isolate.sha(source.read_bytes())
                isolate.write_case(source, case_work / 'producer')
                original = folders['original'] / (source.stem + '_original.HEIC')
                shutil.copyfile(source, original)
                case = {'name': source.name, 'source_sha256': source_hash,
                        'width': width, 'height': height, 'source_headroom': headroom,
                        'original_path': str(original.relative_to(output)), 'variants': {}}
                report['cases'].append(case)
                for label, calibration in report['calibrations'].items():
                    target = folders[label] / (source.stem + '_' + label + '.HEIC')
                    generated = blind.regenerate(args.generator, args.adapter,
                        case_work / 'producer/input.heic', target, headroom, calibration)
                    readback = case_work / label
                    facts = native.readback(args.adapter, target, readback, width, height)
                    comparisons = {kind: native.compare_buffers(
                        case_work / 'reference' / f'published_{kind}.f32',
                        readback / f'published_{kind}.f32', width, height) for kind in ('sdr', 'hdr')}
                    if facts['hdr_content_headroom'] != headroom or any(
                            not v['passed'] or v['different_float32_components'] != 0
                            for v in comparisons.values()):
                        raise ValueError('final HEIC changed native base pixels: ' + json.dumps(comparisons))
                    if not all(generated['style']['resource_bytes'].get(key, 0) > 0
                               for key in ('1', '3', 'c', 'd')):
                        raise ValueError('generated HEIC is missing Styles resources')
                    case['variants'][label] = {'path': str(target.relative_to(output)),
                        'sha256': isolate.sha(target.read_bytes()), 'bytes': target.stat().st_size,
                        'generation': generated, 'native_base_preservation': comparisons}
                    target.with_suffix('.request.json').unlink()
                    shutil.rmtree(readback)
                if isolate.sha(source.read_bytes()) != source_hash:
                    raise ValueError('source changed')
                (output / 'report.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
                shutil.rmtree(case_work)
        report['passed'] = bool(report['cases'])
    except (ValueError, RuntimeError, OSError, KeyError, subprocess.TimeoutExpired) as error:
        report['error'] = str(error)
    finally:
        (output / 'report.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    (output / 'README.txt').write_text('''完整摄影风格 HEIC 对照包

01_original：三张苹果原生 Standard 照片，作为编辑对照。
02_before_default：相同照片，使用现有默认算法重建摄影风格资源。
03_after_joint：相同照片，使用固定联合候选重建资源（曝光、增益缩放均为 0.75，直方图 c/d，曝光上限 10.4）。

这是完整 HEIC，不是 PNG 预览或调完效果的扁平图。请导入 Photos 后自行调整摄影风格的影调、色彩及风格预设。文件本身没有预先套用 ±0.5 Tone。

生成器保留编码的主图与 HDR 增益图，每份生成文件另行核验了原始分辨率 SDR/HDR 基图的原生解码像素及 HDR 余量。各项结果与文件哈希见 report.json，构建版本见 source-binding.json。passed 表示导出和这些校验完成，不表示已经在 Photos 界面验证过编辑能力或真实性。

此前独立探针导出的参考和变体都有花屏，原因尚未定位，因此不以它证明 Photos 中的效果。本包供实际导入试调；没有把联合方案改为产品默认，也没有合并 PR85。
''')
    print(json.dumps({'passed': report['passed'], 'cases': len(report['cases']),
                      'error': report.get('error')}))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
