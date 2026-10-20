"""Check actual per-input native production, final decoding and per-person replay."""
import hashlib
import json
import math
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'texture-producer-20261020'))
from pack_carrier import parse,iprp


def validate(root, head):
    read=lambda p:json.loads((root/p).read_text())
    sha=lambda p:hashlib.sha256((root/p).read_bytes()).hexdigest()
    inp=read('input.json');production=read('carrier-production.json')
    assert production['stage']=='finished' and not production.get('exception')
    assert production['input_sha256']==inp['working_sha256']==sha('working.png')
    width,height=production['width'],production['height']
    assert (width,height)==(inp['working_width'],inp['working_height'])
    assert len(production['resources'])==13
    people=production['people']
    assert len({p['instance_role'] for p in people})==len(people)
    assert len({p['instance_reference_key'] for p in people})==len(people)
    for p in people:
        assert p['face_probability_overlap']>=.02
        assert not p['native_person_without_stats'].get('imageStats')
    for r in production['resources']+production['instance_resources']:
        assert sha(r['file'])==r['sha256'] and (root/r['file']).stat().st_size==width*height
    assert all(r['native_auxiliary_readback'] for r in production['native_mask_codec_controls'])
    admission=read('texture-candidate.heic.admission.json')
    assert not admission.get('exception') and admission['ImageIO_decoded'] and admission['asset_loaded']
    assert admission['input_sha256']==sha('texture-candidate.heic')
    assert admission['texture_properties_present'] and admission['semantic_properties_present']
    assert (admission['decoded_width'],admission['decoded_height'])==(width,height)
    native=admission.get('native_person_data_readback',[])
    assert admission['texture_person_count']==len(native)==len(people)
    native_by_key={p['instanceMaskReferenceKey']:p for p in native}
    assert set(native_by_key)=={p['instance_reference_key'] for p in people}
    stages=['setup','prewarm','prepareToProcess:','calculateStats','process','finishProcessing']
    effects={'Mattify':'mattify','UnderEyeBrightening':'undereyebrighten','SkinSmoothingStandalone':'skinsmoothstandalone'}
    decode=read('final-mask-decode.json')['rows']
    assert len(decode)==14+len(people)
    for r in decode:
        assert (r['width'],r['height'])==(width,height) and sha('stored-'+r['role']+'.l8')==r['sha256']
    decode_by_role={r['role']:r for r in decode}
    renders=[];effect_outcomes=[]
    for index,p in enumerate(people):
        stored=native_by_key[p['instance_reference_key']]
        assert stored['faceID']==p['native_person_without_stats']['faceID']
        assert len(stored['faceLandmarks'])==len(p['native_person_without_stats']['faceLandmarks'])>0
        assert 'Mattify' in stored['imageStats'] and set(stored['imageStats'])<=set(effects)
        for effect,name in effects.items():
            generated=read(f'person-{index}/{name}-type1-Studio-EV0.json')
            assert not generated.get('exception') and generated['native_statistics_operations_completed']
            assert all(generated[stage]==0 for stage in stages)
            assert generated['shared_context_geometry_used'] and not generated['person_before_stats'].get('imageStats')
            assert generated['actual_input_mask_textures']['instance']['sha256']==sha(p['instance_role']+'.l8')
            assert generated['actual_input_mask_textures']['skin']['sha256']==sha('semanticskinmattev2.l8')
            if generated['native_returned_empty_statistics']:
                assert not generated['native_output_person_stats'] and effect not in stored['imageStats']
                outcome='native returned empty statistics; group omitted'
            else:
                assert generated['statistics_generation_completed']
                assert generated['native_output_person_stats']==stored['imageStats'][effect]
                assert 'nonfinite_number' not in json.dumps(stored['imageStats'][effect],allow_nan=False)
                outcome='measured native statistics round-tripped'
            effect_outcomes.append({'person_index':index,'effect':effect,'outcome':outcome})
        replay=read(f'person-{index}/final-file-replay.json')
        assert not replay.get('exception') and replay['input_sha256']==sha('texture-candidate.heic')
        assert replay['provided_precomputed_image_stats_from_final_HEIC']
        assert not replay['fresh_Vision_observations_used_as_replay_inputs']
        for role,facts in replay['actual_input_mask_textures'].items():
            stored_role='instance-'+str(index) if role=='instance' else role
            assert facts['sha256']==decode_by_role[stored_role]['sha256']
        assert replay['render_calculate_stats_status']==replay['render_process_status']==0
        assert replay['render_command_status']==4 and not replay['render_command_error']
        assert replay['rendered_pixels']['nonfinite']==0 and replay['native_preview_finalized']
        renders.append(replay['rendered_pixels'])
    if not people:
        linear=read('linear-only.json')
        assert linear['linearization_only'] and not linear.get('exception')
        assert not (root/'person-0').exists()
    derived=read('derived-styles.json')
    populations=derived['population_counts']
    if not populations['person']:
        assert not any('PersonSegmentBased' in k for k in derived['mask_population_statistics'])
    if not populations['skin']:
        assert not any('SkinBased' in k for k in derived['mask_population_statistics'])
    assembly=read('texture-candidate.heic.assembly.json')
    assert assembly['image_and_auxiliary_payloads_byte_identical']
    assert len(assembly['native_encoded_masks'])==15+len(people)
    encoded=(root/'texture-candidate.heic').read_bytes()
    _,_,children,_,_,payloads,primary=parse(encoded)
    *_,control_payloads,control_primary=parse((root/'control.heic').read_bytes())
    assert primary==control_primary and all(payloads[k]==v for k,v in control_payloads.items() if k not in assembly['changed_metadata_items'])
    properties,_=iprp(encoded,children);assert len(properties)<=100
    assert read('final-mask-projections.json')['final_carrier_sha256']==sha('texture-candidate.heic')
    assert not admission['photos_UI_tested'] and not admission['capabilities_injected']
    props=admission['ImageIO_properties']
    assert props.get('Orientation',1)==1
    assert not any(k in props.get('{TIFF}',{}) for k in ['Make','Model'])
    assert not any(k in props.get('{Exif}',{}) for k in ['ExposureTime','ISOSpeedRatings','FNumber','DateTimeOriginal'])
    return {'schema':'texture-real-fixture-acceptance-v1','source_head':head,'passed':True,
            'input_sha256':inp['source_sha256'],'working_sha256':inp['working_sha256'],
            'dimensions':[width,height],'native_face_count':len(production['face_geometry']),
            'native_instance_count':production['instance_count'],'stored_person_count':len(people),
            'unmatched_faces':production['unmatched_faces'],'native_replay_renders':renders,
            'native_effect_outcomes':effect_outcomes,
            'no_person_behavior':'empty measured context; no fabricated people or population statistics' if not people else None,
            'container_properties':len(properties),'population_counts':populations,
            'source_media_preserved':True,'output_profile':'new 8-bit SDR edit copy; HDR and motion not retained',
            'device_activation':'not tested for this new file',
            'files':{name:{'sha256':sha(name),'bytes':(root/name).stat().st_size} for name in ['texture-candidate.heic','control.heic']}}
