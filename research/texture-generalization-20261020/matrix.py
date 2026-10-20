"""Run immutable XDRemux real-media fixtures through native Texture production."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

from validate_case import validate

HERE = Path(__file__).resolve().parent
PRODUCER = HERE.parent / 'texture-producer-20261020'
SMOKE = {'motion-photo/samsung/jpeg-ultrahdr-01.jpg',
         'motion-photo/vivo/android-v1-sdr-01.jpg',
         'motion-photo/oppo/coloros15-ultrahdr-01.jpg',
         'proxdr/oppo/find-x9-ultra/uhdr-hr-01.heic',
         'proxdr/oppo/find-x9-ultra/uhdr-portrait-02.heic'}


def source_head():
    subprocess.run(['git','-C',HERE,'diff','--exit-code','--quiet','HEAD','--',str(HERE),str(PRODUCER)],check=True)
    return subprocess.check_output(['git','-C',HERE,'rev-parse','HEAD'],text=True).strip()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args, root, name, env=None, timeout=180):
    with (root / (name + '.stdout.log')).open('wb') as out, (root / (name + '.stderr.log')).open('wb') as err:
        try:
            code = subprocess.run([str(a) for a in args], stdout=out, stderr=err, timeout=timeout, env=env).returncode
        except subprocess.TimeoutExpired:
            code = 'timeout'
    return code


def require(args, root, name, env=None):
    code = run(args, root, name, env)
    if code != 0:
        raise RuntimeError(name + ' exit ' + str(code))


def compile_tools(build, phase):
    build.mkdir(parents=True, exist_ok=True)
    sources = [('prepare', HERE / 'prepare_input.m')]
    if phase == 'generate':
        sources += [('angle-tests',HERE/'angle_tests.m'),('matching-tests', HERE/'matching_tests.m'), ('augment', HERE/'augment_input.m'), ('produce',PRODUCER/'produce_carrier.m'),
                    ('stats',PRODUCER/'generate_stats.m'), ('thumbnail',PRODUCER/'encode_thumbnail.m'),
                    ('admission',PRODUCER/'native_admission.m'), ('decode',PRODUCER/'decode_final_masks.m')]
    for name, source in sources:
        args = ['xcrun', 'clang', '-g', '-O0', '-fobjc-arc', '-fblocks', '-Wall', '-Wextra', source]
        for framework in ['Foundation', 'CoreGraphics', 'CoreImage', 'CoreVideo', 'ImageIO', 'Vision', 'Metal', 'MetalKit']:
            args += ['-framework', framework]
        args += ['-o', build / name]
        require(args, build, name + '-build')
    if phase=='generate':
        require([build/'angle-tests',build/'angle-tests.json'],build,'angle-tests')
        require([build/'matching-tests',build/'matching-tests.json'],build,'matching-tests')


def generate_case(directory, build, head):
    image=directory/'working.png'
    require([build/'produce',image,directory],directory,'produce')
    production=json.loads((directory/'carrier-production.json').read_text())
    people=production['people']
    if people:
        for index,_person in enumerate(people):
            stats_root=directory/('person-'+str(index));stats_root.mkdir()
            for effect in ['Mattify','UnderEyeBrighten','SkinSmoothStandalone']:
                name=effect.lower()+'-type1-Studio-EV0'
                env={**os.environ,'TEXTURE_RAW_CONTEXT_DIR':str(directory),'TEXTURE_PERSON_INDEX':str(index),'TEXTURE_EFFECT':effect}
                require([build/'stats',image,stats_root/(name+'.json'),1,'Studio',0],stats_root,name,env)
        shutil.copyfile(directory/'person-0/native-linear-p3.rgba32f',directory/'native-linear-p3.rgba32f')
    else:
        env={**os.environ,'TEXTURE_RAW_CONTEXT_DIR':str(directory),'TEXTURE_LINEAR_ONLY':'1','TEXTURE_EFFECT':'Mattify'}
        require([build/'stats',image,directory/'linear-only.json',1,'Studio',0],directory,'linear-only',env)
    require(['python3',PRODUCER/'derive_styles.py',directory],directory,'derive')
    require([build/'thumbnail',directory],directory,'thumbnail')
    require(['python3',PRODUCER/'pack_carrier.py',directory],directory,'pack')
    for name in ['control.heic','texture-candidate.heic']:
        require([build/'admission',directory/name,directory/(name+'.admission.json')],directory,name+'-admission')
    require(['python3',PRODUCER/'project_final.py',directory],directory,'project')
    require([build/'decode',directory],directory,'decode')
    for index,_person in enumerate(people):
        stats_root=directory/('person-'+str(index))
        env={**os.environ,'TEXTURE_REPLAY_DIR':str(directory),'TEXTURE_PERSON_INDEX':str(index),'TEXTURE_EFFECT':'Mattify'}
        require([build/'stats',directory/'texture-candidate.heic',stats_root/'final-file-replay.json',1,'Studio',0],stats_root,'replay',env)
    result=validate(directory,head)
    (directory/'acceptance.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('fixtures', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--phase', choices=['inventory', 'generate'], default='inventory')
    parser.add_argument('--selection', choices=['smoke','all'],default='all')
    args = parser.parse_args()
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=True)
    head = source_head()
    fixture_head = subprocess.check_output(['git', '-C', args.fixtures, 'rev-parse', 'HEAD'], text=True).strip()
    rows=[]
    report={'schema':'texture-fixture-matrix-v1','source_head':head,'fixture_repository':'21Z121Z1/XDRemux','fixture_head':fixture_head,'phase':args.phase,'selection':args.selection,'rows':rows}
    def save(): (out/'matrix.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    build=out/'_build';compile_tools(build,args.phase)
    subprocess.run(['sw_vers'],stdout=(build/'os.txt').open('wb'),check=True)
    subprocess.run(['xcodebuild','-version'],stdout=(build/'xcode.txt').open('wb'),check=True)
    seen={};prepared={}
    def execute(row,path,limit=1024):
        directory=out/row['id'];directory.mkdir()
        try:
            require([build/'prepare',path,directory,limit],directory,'prepare')
            row['input']=json.loads((directory/'input.json').read_text())
            row['prepare_exit']=0
            prepared[row['id']]=directory
            if row.get('expected_upright_pixels'):
                row['orientation_pixels_match']=row['input']['working_native_pixels_sha256']==row['expected_upright_pixels']
                assert row['orientation_pixels_match'],'orientation did not restore original upright pixels'
            if args.phase=='generate':
                row['acceptance']=generate_case(directory,build,head)
                if 'expected_people' in row:
                    assert row['acceptance']['stored_person_count']==row['expected_people'],'unexpected matched-person count'
                row['passed']=True
            prepared[row['id']]=directory
        except Exception as error:
            row['passed']=False;row['failure']=str(error)
            (directory/'failure.json').write_text(json.dumps({'source_head':head,'failure':str(error)},indent=2)+'\n')
        rows.append(row);save()
        print(json.dumps({k:v for k,v in row.items() if k not in ['input','acceptance']}),flush=True)
    all_identities=[]
    for line in (args.fixtures/'SHA256SUMS').read_text().splitlines():
        digest,relative=line.split(None,1);relative=relative.strip();path=args.fixtures/relative
        assert sha(path)==digest,'fixture digest mismatch: '+relative
        all_identities.append({'fixture':relative,'sha256':digest})
        if args.selection=='smoke' and relative not in SMOKE:continue
        case=relative.replace('/','__').rsplit('.',1)[0]
        row={'id':case,'fixture':relative,'source_sha256':digest,'kind':'original_fixture'}
        if digest in seen:
            row['duplicate_of']=seen[digest];rows.append(row);continue
        seen[digest]=case;execute(row,path)
    report['fixture_identities']=all_identities
    if args.phase=='generate':
        nasa=build/'public-astronaut.png'
        require(['curl','--fail','--location','--silent','--show-error','https://raw.githubusercontent.com/scikit-image/scikit-image/v0.25.2/skimage/data/astronaut.png','--output',nasa],build,'fetch-baseline')
        assert sha(nasa)=='88431cd9653ccd539741b555fb0a46b61558b301d4110412b5bc28b5e3ea6cb5'
        execute({'id':'regression-nasa','kind':'prior_positive_input_regression','source_sha256':sha(nasa),'expected_people':1},nasa)
        left='motion-photo__samsung__jpeg-ultrahdr-01';right='motion-photo__vivo__android-v1-sdr-01'
        composite=build/'two-fixture-faces.png'
        require([build/'augment','compose',prepared[left]/'working.png',prepared[right]/'working.png',composite],build,'compose')
        execute({'id':'derived-two-fixture-faces','kind':'derived_two_input_stress','source_cases':[left,right],'source_sha256':sha(composite),'expected_people':2},composite)
        for orientation in ([6] if args.selection=='smoke' else range(2,9)):
            path=build/('orientation-'+str(orientation)+'.tiff')
            require([build/'augment','orientation',prepared[left]/'working.png',orientation,path],build,'make-orientation-'+str(orientation))
            baseline=json.loads((prepared[left]/'input.json').read_text())
            execute({'id':'derived-orientation-'+str(orientation),'kind':'lossless_inverse_raster_with_EXIF_orientation','source_case':left,'orientation':orientation,'source_sha256':sha(path),'expected_upright_pixels':baseline['working_native_pixels_sha256']},path)
        for limit in ([512] if args.selection=='smoke' else [512,2048]):
            source=args.fixtures/'motion-photo/samsung/jpeg-ultrahdr-01.jpg'
            execute({'id':'resolution-'+str(limit),'kind':'resolution_variant','fixture':'motion-photo/samsung/jpeg-ultrahdr-01.jpg','source_sha256':sha(source)},source,limit)
        cli_root=out/'cli-real-fixture'
        cli_source=args.fixtures/'motion-photo/samsung/jpeg-ultrahdr-01.jpg'
        cli_code=run(['python3',HERE/'convert.py',cli_source,cli_root,'--max-dimension',1024],build,'direct-cli')
        cli_row={'id':'cli-real-fixture','kind':'direct_cli','source_sha256':sha(cli_source),'exit':cli_code,'passed':False}
        if cli_code==0:
            cli_row['input']=json.loads((cli_root/'input.json').read_text());cli_row['prepare_exit']=0
            cli_row['acceptance']=validate(cli_root,head);cli_row['passed']=True
        rows.append(cli_row);save()
    unique=[r for r in rows if 'duplicate_of' not in r]
    report['fixture_file_count']=len(all_identities)
    report['unique_fixture_count']=len(seen)
    report['all_native_inputs_prepared']=all(r.get('prepare_exit')==0 for r in unique)
    report['all_cases_passed']=all(r.get('passed',args.phase=='inventory') for r in unique)
    report['passed_case_count']=sum(r.get('passed',args.phase=='inventory') for r in unique)
    report['case_count']=len(unique)
    save()
    return 0 if report['all_native_inputs_prepared'] and report['all_cases_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
