"""Actual two distinct enum mappings from the matched cache (not UI labels)."""
from dataclasses import replace
from tone_interface import ResolvedSceneType,evaluate

TUNING_TYPES={'DefaultParameters':1,'WYSIWYG':2,'UB':3,'DF':4,'DigitalFlash':5,'SWFR':6,'Video':7,'QuadraSFD':8}


class UnknownTuningType(ValueError):pass


def resolve_scene_type(semantic_scene_type: int) -> ResolvedSceneType:
    if type(semantic_scene_type)is not int or not 0<=semantic_scene_type<=0xffffffff:raise ValueError('Source semantic scene type must preserve uint32')
    return ResolvedSceneType({1:3,2:7,3:10}.get(semantic_scene_type,4))


def resolve_tuning_type(name: str) -> int:
    if type(name)is not str or name not in TUNING_TYPES:
        raise UnknownTuningType('Actual unknown-key path signals an error; there is no verified default enum fallback')
    return TUNING_TYPES[name]


def evaluate_runtime_keys(controls,semantic_scene_type,tuning_name,frame):
    return evaluate(controls,resolve_scene_type(semantic_scene_type),replace(frame,tuning_type=resolve_tuning_type(tuning_name)))
