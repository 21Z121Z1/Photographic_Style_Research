"""Preselected second synthetic scene, frozen before any forward/host search."""
from dataclasses import replace
from pathlib import Path
import argparse,json
import numpy as np
from baseline_archive import sha,encoded
from complete_fixture import encode,decode
from select_active_color import CONTEXT_SHA


def freeze(base_file:Path,context_file:Path,selection_file:Path):
    if context_file.exists()or selection_file.exists():raise FileExistsError('Never replace a frozen scene')
    if sha(base_file)!=CONTEXT_SHA:raise ValueError('Known explicit auxiliary ABI base required')
    base=decode(json.loads(base_file.read_text()))
    rgb=np.array([[[.62,.18,.09],[.08,.26,.58],[.42,.55,.12],[.12,.10,.16]],[[.09,.18,.12],[.78,.62,.36],[.22,.09,.32],[.36,.44,.64]],[[.48,.12,.22],[.16,.38,.28],[.68,.74,.52],[.24,.20,.08]]],dtype='f4')
    primary=np.concatenate([rgb,np.ones((3,4,1),dtype='f4')],axis=2).astype('f2')
    linear=np.concatenate([np.float32(.7)*rgb+np.array([.015,.025,.01],dtype='f4'),np.ones((3,4,1),dtype='f4')],axis=2).astype('f2')
    lum=rgb@np.array([.25,.5,.25],dtype='f4');guide=np.stack([lum,.9*lum,.8*lum,np.ones((3,4),dtype='f4')],axis=2).astype('f2')
    matte=np.array([[.2,.8,.4,.6],[.7,.1,.9,.3],[.5,.65,.15,.75]],dtype='f2')[...,None]
    y,x=np.mgrid[:3,:4];g8=(.12+.08*((x+2*y)%4))[...,None].astype('f2');g9=(.22+.06*((2*x+y)%5))[...,None].astype('f2')
    person=(.18+.12*((x+y)%5))[...,None].astype('f2');skin=(.10+.09*((3*x+y)%4))[...,None].astype('f2');sky=(.05+.13*((x+3*y)%4))[...,None].astype('f2')
    c=replace(base,images=(primary,linear,guide,matte,g8,g9,person,skin,sky,base.images[9]))
    data=encode(c);data['origin']='S25 independently preselected literal 3x4 chromatic blocks/nonmonotone luminance and modular spatial masks; auxiliary ABI, curves, zero lookup, ROI and format explicitly inherited from frozen S15; no output-based selection'
    context_file.write_bytes(encoded(data))
    selection={'scope':__doc__,'selection_happened_before_any_second_scene_forward_or_host_call':True,'base_context_sha256':sha(base_file),'new_context_sha256':sha(context_file),'generator_sha256':sha(Path(__file__)),'shape':[3,4],'target_controls':[{'id':'target_A','raw_f32_bits':int(np.float32(.125).view('u4'))},{'id':'target_B','raw_f32_bits':int(np.float32(.34375).view('u4'))}],'boundary_rule':'after blind exact query: first/last inclusive matching raw f32 and immediate domain-valid outside neighbors for every candidate union, deduplicated; at most8 new controls; skip already executed target controls and eight old S22 raw controls; record any omissions, never substitute nearest candidates','finite_domain':{'first_f32_bits':0,'last_f32_bits':int(np.float32(.375).view('u4'))},'changed_inputs':['primary RGB','explicit linear auxiliary RGB','guide RGB','producer matte','guide8/9','person/skin/sky masks'],'retained_explicit_inputs':['management and all non-field3 params','raw stats','ROI and producer2x3/output5x6 grids','SRL','GTC and whites','zero selective lookup','cast0/tuning2/version0','RGBA16/R16 and original samplers'],'point_or_native_calls':0,'UI_or_unknown_source_inverse_verified':False}
    selection_file.write_bytes(encoded(selection));print(json.dumps({'context_sha256':sha(context_file),'target_controls_preselected':selection['target_controls'],'point_or_native_calls':0}));return selection


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('base',type=Path);p.add_argument('context',type=Path);p.add_argument('selection',type=Path);a=p.parse_args();freeze(a.base,a.context,a.selection)
