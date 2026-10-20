"""Validate native production and final-file replay, without claiming UI activation."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import plistlib


def validate(root, head):
    read = lambda name: json.loads((root / name).read_text())
    sha = lambda name: hashlib.sha256((root / name).read_bytes()).hexdigest()
    assert (root / 'head.txt').read_text().strip() == head
    controls = [read('mattify-type1-Studio-EV'+str(ev)+'.json') for ev in [-1,0,1]]
    for row in controls:
        assert all(row[stage] == 0 for stage in ['setup','prewarm','prepareToProcess:','calculateStats','process','finishProcessing'])
        assert not row['provided_capture_image_stats'] and not row.get('provided_precomputed_image_stats_from_final_HEIC',False)
        assert all(math.isfinite(v) and v > 0 for v in row['native_output_person_stats']['AverageFaceColor'])
    assert len({row['image_pixels']['sha256'] for row in controls}) == 3
    assert len({tuple(row['native_output_person_stats']['AverageFaceColor']) for row in controls}) == 3
    assert controls[2]['native_output_person_stats']['HighlightsToMaskRatio'] > controls[1]['native_output_person_stats']['HighlightsToMaskRatio']
    for name in ['undereyebrighten-type1-Studio-EV0.json','skinsmoothstandalone-type1-Studio-EV0.json']:
        row = read(name)
        assert all(row[stage] == 0 for stage in ['setup','prewarm','prepareToProcess:','calculateStats','process','finishProcessing'])
        assert row['native_output_person_stats'] and not row.get('exception')
    production = read('carrier-production.json')
    assert production['stage'] == 'finished' and len(production['resources']) == 13
    assert sha('semanticfaceskinmatte.l8') == controls[1]['face_skin_sha256']
    assert all(row['native_auxiliary_readback'] for row in production['native_mask_codec_controls'])
    candidate = read('texture-candidate.heic.admission.json')
    assert candidate['input_sha256'] == sha('texture-candidate.heic')
    assert candidate['ImageIO_decoded'] and candidate['semantic_properties_present'] and candidate['texture_properties_present']
    assert candidate['texture_person_count'] == 1 and len(candidate['native_person_data_readback']) == 1
    person = candidate['native_person_data_readback'][0]
    assert len(person['faceLandmarks']) == 76
    assert set(person['imageStats']) == {'Mattify','UnderEyeBrightening','SkinSmoothingStandalone'}
    assert person['imageStats']['Mattify'] == controls[1]['native_output_person_stats']
    assert person['imageStats']['UnderEyeBrightening'] == read('undereyebrighten-type1-Studio-EV0.json')['native_output_person_stats']
    assert person['imageStats']['SkinSmoothingStandalone'] == read('skinsmoothstandalone-type1-Studio-EV0.json')['native_output_person_stats']
    assert read('texture-no-people-control.heic.admission.json')['texture_person_count'] == 0
    assembly = read('texture-candidate.heic.assembly.json')
    assert assembly['image_and_auxiliary_payloads_byte_identical'] and len(assembly['native_encoded_masks']) == 16
    assert read('final-mask-projections.json')['final_carrier_sha256'] == sha('texture-candidate.heic')
    for row in read('final-mask-decode.json')['rows']: assert row['sha256'] == sha('stored-'+row['role']+'.l8')
    replay = read('final-file-replay.json')
    assert replay['input_sha256'] == sha('texture-candidate.heic') and replay['provided_precomputed_image_stats_from_final_HEIC']
    assert not replay['fresh_Vision_observations_used_as_replay_inputs']
    for role in ['skin','face','instance']: assert replay['actual_input_mask_textures'][role]['sha256'] == sha('stored-'+role+'.l8')
    assert replay['render_process_status'] == replay['render_calculate_stats_status'] == 0
    assert replay['render_command_status'] == 4 and not replay['render_command_error']
    assert replay['rendered_pixels']['changed_pixels_over_0_0001'] > 0 and replay['rendered_pixels']['nonfinite'] == 0
    assert replay['native_preview_finalized']
    assert not candidate['photos_UI_tested'] and not candidate['capabilities_injected']
    props = candidate['ImageIO_properties']
    assert not any(key in props.get('{TIFF}',{}) for key in ['Make','Model'])
    assert not any(key in props.get('{Exif}',{}) for key in ['ExposureTime','ISOSpeedRatings','FNumber','DateTimeOriginal'])
    return {'schema':'texture-cloud-production-acceptance-v1','source_head':head,
            'cloud_production_and_final_file_replay_passed':True,'Photos_activation_proved':False,
            'verified_input_scope':'public NASA portrait, one detected face and instance; not a universal-input certification',
            'native_statistics_effects':sorted(person['imageStats']), 'final_file_person_count':candidate['texture_person_count'],
            'native_editor_gate':{key:candidate[key] for key in ['PhotographicStyleV2','canRenderTextureStylesOnComposition','pipeline_isAvailable','platform_supportsSemanticStyleRendering']},
            'final_file_replay_rendered_pixels':replay['rendered_pixels'],
            'optional_protection_disabled':['ears','tattoo'], 'hand_request':production['hand_inference'],
            'files':{name:{'sha256':sha(name),'bytes':(root/name).stat().st_size} for name in ['texture-candidate.heic','control.heic','final-file-mattify-preview.heic']}}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('directory',type=Path);parser.add_argument('--head',required=True);args=parser.parse_args()
    result=validate(args.directory,args.head)
    (args.directory/'acceptance.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
