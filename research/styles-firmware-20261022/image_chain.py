"""Inspectable source-to-writer experiments, separate from the pinned v3 profile.

The strict backend retains v3's Darwin/arm64 final-transfer gate. The portable
backend explicitly substitutes the existing generic code3 model; NumPy math is
not a replacement for the target Apple powf. BRIGHT16 changes the supplied raw
cast code and follows the statically established SSA400 -> SSA404 selection.
Neither option inherits the finite native comparisons of S25/S29/S30.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass, replace
from enum import Enum
import hashlib
from pathlib import Path
import platform
from typing import Any

import numpy as np

import complete_forward
import pixel_output
from complete_forward import Context, Result
from leaf_numeric import DomainUnknown, V
from pixel_transfer import forward as generic_transfer


ROOT = Path(__file__).parent
PINNED_FORWARD_SHA256 = 'f7bc4bbbf34694fdfeebd026d1ef0a5c8285ee02614a755e1a5b408ef8585793'


class BranchSelection(Enum):
    CONTEXT = 'context_cast0_or_2'
    EXPERIMENTAL_BRIGHT16 = 'experimental_raw_cast16'


class Numerics(Enum):
    STRICT_HOST_POINT = 'strict_host_point'
    EXPERIMENTAL_PORTABLE_POINT = 'experimental_portable_point'


@dataclass(frozen=True)
class SemanticMasks:
    """Synthetic R16Float masks; None explicitly means the model's zero fallback.

    Values must be finite [0,1] on the source grid. These are supplied masks,
    not predictions, and do not establish real person/face segmentation quality.
    """
    person: np.ndarray | None = None
    skin: np.ndarray | None = None
    sky: np.ndarray | None = None

    def __post_init__(self) -> None:
        for name in ('person', 'skin', 'sky'):
            value = getattr(self, name)
            if value is None:
                continue
            raw = np.asarray(value)
            if raw.ndim != 3 or raw.shape[-1] != 1 or not np.isfinite(raw).all():
                raise TypeError('Synthetic masks require finite HxWx1 scalar arrays')
            if np.any(raw < 0) or np.any(raw > 1):
                raise ValueError('Synthetic semantic weights must lie in [0,1]')
            frozen = np.array(raw, dtype='f2', copy=True)
            frozen.setflags(write=False)
            object.__setattr__(self, name, frozen)


@dataclass(frozen=True)
class Checkpoint:
    name: str
    value: V
    inputs: tuple[str, ...]
    domain: str


@dataclass(frozen=True)
class BranchDecision:
    destination: str
    selector: str
    selected: str
    candidates: tuple[str, ...]
    model_observed: bool
    selection_evidence: str


@dataclass(frozen=True)
class ImageChainResult:
    model: Result
    checkpoints: tuple[Checkpoint, ...]
    branches: tuple[BranchDecision, ...]
    status: str
    numerics: Numerics
    selection: BranchSelection
    provenance: dict[str, Any]
    gaps: tuple[str, ...]
    evidence_level: str = 'model_only'
    apple_pipeline_verified: bool = False


@dataclass(frozen=True)
class _BoundContext:
    """Private validated view; generated maps and intermediate RGB are excluded."""
    source: Context
    params: np.ndarray

    def __getattr__(self, name: str) -> Any:
        return getattr(self.source, name)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _selected(o: dict[str, V], castcode: int, key: str, internal: dict) -> V:
    name = 'bright400' if castcode == 16 else 'skin393'
    if name not in o:
        raise DomainUnknown('Selected '+name+' unavailable: '+internal.get(key+':'+name, 'upstream unknown'))
    return o[name]


def _portable_code3(rgb: V) -> V:
    # Deliberately use the existing general transfer implementation. Its
    # float64 NumPy power rounded to half is not the target f32 powf ABI.
    return generic_transfer(rgb, 3, to_linear=False)


def _output_for(numerics: Numerics):
    if numerics is Numerics.STRICT_HOST_POINT:
        return pixel_output.forward
    namespace = dict(vars(pixel_output))
    namespace['host_code3'] = _portable_code3
    # A local Python function clone avoids mutating the imported v3 module.
    from types import FunctionType
    fn = pixel_output.forward
    return FunctionType(fn.__code__, namespace, fn.__name__, fn.__defaults__, fn.__closure__)


def _runner(numerics: Numerics):
    path = ROOT/'complete_forward.py'
    if _sha(path) != PINNED_FORWARD_SHA256:
        raise ValueError('Source-to-writer adapter requires its exact reviewed v3 source')
    tree = ast.parse(path.read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'forward')

    class Connect(ast.NodeTransformer):
        count = 0

        def visit_Assign(self, node):
            self.generic_visit(node)
            if (len(node.targets) == 1 and isinstance(node.targets[0], ast.Subscript)
                    and isinstance(node.targets[0].value, ast.Name)
                    and node.targets[0].value.id == 'o'
                    and isinstance(node.targets[0].slice, ast.Constant)
                    and node.targets[0].slice.value == 'selected404'):
                self.count += 1
                # Mark the selected dependency before a DomainUnknown. The
                # legacy optional bright diagnostic cannot hide its failure.
                stage = ast.Assign([ast.Name('stage', ast.Store())], ast.Constant('selected404'))
                node.value = ast.Call(ast.Name('psr_selected', ast.Load()),
                                      [ast.Name(x, ast.Load()) for x in ('o', 'castcode', 'key', 'internal')], [])
                return [stage, node]
            return node

    transform = Connect()
    fn = transform.visit(fn)
    if transform.count != 1:
        raise ValueError('Exactly one original SSA404 selection is required')
    namespace = dict(vars(complete_forward))
    namespace.update(Context=(Context, _BoundContext), psr_selected=_selected,
                     output=_output_for(numerics))
    module = ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[]))
    exec(compile(module, '<PSR-explicit-image-chain-model>', 'exec'), namespace)
    return namespace['forward']


DEPENDENCIES = {
    'producer_source24': ('source.primary', 'producer_shape'),
    'producer_postSRL34': ('producer_source24',),
    'producer_linear37': ('producer_postSRL34', 'management.input_transfer'),
    'producer_reference96': ('producer_linear37', 'management.inputCCM'),
    'producer_working121': ('source.linear', 'management.linearCCM', 'params.scale6'),
    'producer_BG203': ('producer_working121', 'producer_reference96', 'GTC', 'params.semantic7'),
    'producer_FG205': ('producer_working121', 'producer_reference96', 'GTC', 'params.semantic7'),
    'raw_BG': ('producer_BG203',), 'raw_FG': ('producer_FG205',),
    'source38': ('source.primary', 'roi.primary'),
    'raw_person63': ('source.person', 'roi.person'),
    'raw_skin70': ('source.skin', 'roi.skin'),
    'sky77': ('source.sky', 'roi.sky'),
    'skin95': ('raw_skin70', 'params.hint167'),
    'person96': ('raw_person63', 'params.hint167'),
    'SRL134': ('source38', 'params.srl', 'person96', 'version'),
    'linear137': ('SRL134', 'management.input_transfer'),
    'gain176': ('linear137', 'management.input_transfer', 'management.gamma_flag'),
    'reference196': ('linear137', 'gain176', 'management.inputCCM'),
    'guide211': ('source.guide8', 'roi.guide8'),
    'guide214': ('source.guide9', 'roi.guide9'),
    'working286': ('source.linear', 'roi.linear', 'management.linearCCM', 'params.scale6'),
    'precomputed335': ('BG_output', 'FG_output', 'reference196', 'person96', 'params.semantic7'),
    'semantic347': ('precomputed335',), 'guide350': ('source.guide8', 'source.guide9', 'person96', 'params.semantic7'),
    'BG352': ('semantic347', 'guide350', 'person96', 'skin95', 'params.BG17', 'whites'),
    'FG354': ('BG352', 'semantic347', 'guide350', 'person96', 'skin95', 'params.FG16', 'whites'),
    'saturated374': ('FG354', 'params.color3', 'params.color_boost111'),
    'color_mix389': ('person96', 'params.color3'),
    'output392': ('FG354', 'saturated374', 'color_mix389'),
    'skin393': ('output392', 'skin95', 'guide350', 'params.FGtheta9', 'params.FGtheta10'),
    'highlight394': ('skin393', 'guide350'),
    'bright400': ('skin393', 'working286', 'person96', 'skin95', 'params.exposure7', 'stats2.4', 'stats3.4', 'stats5.0', 'stats6.6', 'stats6.4'),
    'neutral408': ('selected404', 'skin95', 'person96', 'params.cast34', 'stats2.4', 'stats3.4', 'stats4.4'),
    'warm409': ('neutral408', 'person96', 'params.cast34'),
    'selective413': ('warm409', 'source.lookup', 'person96', 'skin95', 'sky77', 'params.selective112'),
    'tonal468': ('selective413', 'person96', 'params.tone2', 'params.tone65'),
    'BW477': ('BW_input472', 'guide350', 'person96', 'params.BW', 'whites'),
    'mixed492': ('color476', 'BW477', 'person96', 'params.BWmix4', 'params.BWmix5'),
    'haze493': ('mixed492', 'guide211', 'person96', 'params.haze8'),
    'protect566': ('selected501', 'color476', 'params.cast34', 'stats2.4', 'stats3.4', 'stats4.4'),
    'channel567': ('protect566', 'person96', 'params.tone17_19', 'stats2.4', 'stats3.4', 'stats4.4'),
    'linear597': ('channel567', 'gain176', 'management.outputCCM', 'params.tone2'),
    'output600': ('linear597', 'management.output_transfer'),
    'writer': ('output600', 'output_initial', 'roi.output_offset', 'roi.render_edge'),
}
for _side in ('BG', 'FG'):
    DEPENDENCIES.update({
        _side+'_a': ('raw_'+_side, 'source.guide', 'epsilon'),
        _side+'_b': ('raw_'+_side, 'source.guide', _side+'_a'),
        _side+'_mean_a': (_side+'_a',),
        _side+'_mean_b': (_side+'_b',),
        _side+'_output': (_side+'_mean_a', _side+'_mean_b', 'source.guide'),
    })


def _domain(name: str) -> str:
    if name == 'writer':
        return 'RGBA16Float output storage; alpha=1 for written pixels; supplied output transfer enum'
    if name in ('linear597', 'linear137', 'working286'):
        return 'linear working RGB; supplied CCM/transfer contract; no assumed ICC primaries'
    if name.startswith(('raw_', 'BG_', 'FG_')):
        return 'LTM gain ratios or guided-filter internal values; see named stage; not display RGB'
    if name in ('person96', 'skin95', 'sky77', 'raw_person63', 'raw_skin70'):
        return 'synthetic semantic weight; caller supplied, no segmentation claim'
    return 'named AIR working stage; half/f32 operation model; no universal [0,1] or display-space claim'


def run(context: Context, *, selection: BranchSelection = BranchSelection.CONTEXT,
        numerics: Numerics = Numerics.STRICT_HOST_POINT,
        masks: SemanticMasks | None = None) -> ImageChainResult:
    """Compute one bounded <=32x32 source tile with all raw auxiliaries explicit.

    Portable math and raw cast16 require named opt-ins. An unsupported numeric
    domain remains pixel_unknown; it is never filled from a saved native frame.
    """
    if not isinstance(context, Context) or not isinstance(selection, BranchSelection) or not isinstance(numerics, Numerics):
        raise TypeError('Typed raw context, branch selection and numeric backend required')
    if masks is not None and not isinstance(masks, SemanticMasks):
        raise TypeError('Explicit SemanticMasks or the original context masks required')
    fallback = []
    if masks is not None:
        images = list(context.images)
        shape = context.images[0].shape[:2] + (1,)
        for index, name in ((6, 'person'), (7, 'skin'), (8, 'sky')):
            value = getattr(masks, name)
            if value is None:
                value = np.zeros(shape, dtype='f2')
                fallback.append(name)
            if value.shape != shape:
                raise ValueError('Replacement semantic mask must match the source grid')
            images[index] = value
        context = replace(context, images=tuple(images))
    if any(np.any(image < 0) or np.any(image > 1) for image in context.images[6:9]):
        raise ValueError('Source person/skin/sky weights must lie in [0,1] for this experiment')
    params = context.params.copy()
    if selection is BranchSelection.EXPERIMENTAL_BRIGHT16:
        params.view('u4')[0] = 16
    params.setflags(write=False)
    cast = int(params.view('u4')[0])
    bound = _BoundContext(context, params)
    model = _runner(numerics)(bound, point=True)
    obs = model.observations
    choices = [
        ('highlight398', 'raw_cast245 == 2', 'highlight394+skin393 half mix' if cast == 2 else 'skin393', ('skin393', 'highlight394+skin393 half mix')),
        ('selected404', 'raw_cast245 == 16', 'bright400' if cast == 16 else 'skin393', ('skin393', 'bright400')),
        ('BW_input472', 'raw_cast245 == 3', 'selective413', ('selective413', 'tonal468')),
        ('color476', 'raw_cast245 == 4', 'highlight398', ('highlight398', 'BW_input472')),
        ('BW477', 'SSRParams0 == 4 or 15', 'BW_input472', ('BW_input472', 'stark12', 'tonal67')),
        ('selected501', 'tuning17 == 7 and haze.enabled0', 'haze493' if int(params.view('u4')[163]) == 7 and bool(params.view('u1')[452]) else 'mixed492', ('mixed492', 'haze493')),
        ('channel567', 'SSRParams0 == 4 or 15', 'protect566', ('protect566', 'BW channel mix')),
    ]
    branches = tuple(BranchDecision(dst, condition, chosen, candidates, dst in obs,
                                   'Existing static AIR10 caller model; numeric output remains model_only')
                     for dst, condition, chosen, candidates in choices)
    dependencies = dict(DEPENDENCIES)
    for branch in branches:
        dependencies[branch.destination] = (branch.selected,)
    checkpoints = []
    for name, value in obs.items():
        lo = np.array(value.lo, copy=True); hi = np.array(value.hi, copy=True)
        lo.setflags(write=False); hi.setflags(write=False)
        checkpoints.append(Checkpoint(name, V(lo, hi, value.precision, value.point),
                                      dependencies.get(name, ('raw context / existing named upstream stages',)), _domain(name)))
    replacements = ['SSA404 chooses computed bright400 for explicit raw cast16; selected unknown propagates']
    if numerics is Numerics.EXPERIMENTAL_PORTABLE_POINT:
        replacements.append('pixel_output.host_code3 -> existing pixel_transfer(code3,to_linear=False): NumPy float64 pow then half; separate half multiply/add')
    source_paths = [p for p in ROOT.glob('*.py') if not p.name.startswith('test_')]
    source_paths += [ROOT.parent/'hdr-native/guided_reference_v3.py',
                     ROOT.parent/'semantic-styles/spatial_curve_retarget.py',
                     ROOT.parent/'semantic-styles/semantic_curve_inverse.py']
    input_digest = hashlib.sha256()
    for value in (*context.images, context.management, params, context.stats, context.roi, context.srl, context.output_initial):
        input_digest.update(str(value.shape).encode()); input_digest.update(value.dtype.str.encode()); input_digest.update(value.tobytes())
    input_digest.update(repr((context.gtc.red_samples, context.gtc.coordinate_space,
                              context.whites.red_samples, context.whites.coordinate_space, context.producer_shape,
                              int(np.array(context.epsilon).view('u4')), context.version, context.hardware, context.build)).encode())
    provenance = {'runtime': {'system': platform.system(), 'release': platform.release(), 'machine': platform.machine(), 'numpy': np.__version__},
                  'source_sha256': {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else '../'+str(p.relative_to(ROOT.parent)): _sha(p) for p in source_paths},
                  'source_manifest_scope': 'superset of local Python modules plus actual cross-directory curve and guided dependencies',
                  'raw_input_sha256': input_digest.hexdigest(),
                  'raw_cast_type': cast, 'original_context_cast_type': int(context.params.view('u4')[0]),
                  'replacements': replacements, 'synthetic_zero_mask_fallbacks': fallback,
                  'native_intermediates_used': False, 'native_reference_compared': False,
                  'native_calls': 0, 'GPU_calls': 0, 'inherits_S25_S29_S30_bit_certification': False,
                  'precision': 'IEEE half/f32 rounding at existing V operations; transcendental NumPy model; no FPCR or Apple accuracy guarantee',
                  'parameter_semantics': 'raw ABI SSRParams fields; UI mapping and stats generation are external',
                  'input_color_contract': 'source half RGB plus explicit raw transfer enum and CCM columns; supplied linear texture; no assumed ICC profile',
                  'output_color_contract': 'half RGB through explicit output transfer enum/CCM; RGBA16F writer alpha=1; values not restricted to display range'}
    gaps = ('Target Apple CPU/GPU end-to-end reference absent for this run and numeric backend',
            'Person/skin/sky and guide/lookup producers, original frame statistics and UI-to-raw parameter mapping remain supplied inputs',
            'Raw cast16 reuses supplied coefficients; actual renderer cast resolution and cast16-specific coefficient production are unverified',
            'Texture Styles placement and full Texture chain are not included',
            'Synthetic zero-mask policy tests processing fallback; equivalence to every native nil-texture caller path is unverified')
    return ImageChainResult(model, tuple(checkpoints), branches,
                            'model_source_to_writer_complete' if model.writer is not None and not model.pixel_unknowns else 'unknown_no_writer',
                            numerics, selection, provenance, gaps)
