"""Reproduce the fixed IMG_3673 still/video scene-reference experiment locally."""
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path
from extract import boxes
SRC=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['photo','movie','new_output']:p.add_argument(name,type=Path)
    a=p.parse_args();photo=a.photo.resolve(strict=True);movie=a.movie.resolve(strict=True);out=a.new_output.resolve();out.mkdir(exist_ok=False)
    before={str(f):sha(f)for f in [photo,movie]};steps=[]
    def run(name,command,env=None):
        command=[str(v)for v in command];print(name,flush=True)
        with(out/f'{name}.log').open('w')as f:r=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,env=env)
        steps.append(dict(stage=name,command=command,status=r.returncode));(out/'steps.json').write_text(json.dumps(steps,indent=2)+'\n')
        if r.returncode:raise RuntimeError(f'{name} failed; see {out/name}.log')
    run('extract',[sys.executable,SRC/'extract.py',photo,out/'resources-isolated'])
    command=['xcrun','clang','-O2','-fobjc-arc','-fblocks','-fmodules','-fmodules-cache-path=/private/tmp/xd-pair-modules','-Wno-deprecated-declarations']
    for framework in ['Foundation','AVFoundation','CoreMedia','CoreVideo','CoreImage','Metal']:command+=['-framework',framework]
    run('build',command+[SRC/'decode.m','-o',out/'decode'])
    run('decode',[out/'decode',photo,out/'resources-isolated/linear-isolated.heic',out/'resources-isolated/styles.plist',movie,out/'decoded-isolated'])
    run('analyze',[sys.executable,SRC/'analyze.py',out,out/'analysis'])
    run('plot',[sys.executable,SRC/'plot.py',out,out/'analysis'],env={**os.environ,'MPLCONFIGDIR':'/private/tmp/xd-pair-matplotlib'})
    report=json.loads((out/'analysis/results.json').read_text());info=json.loads((out/'decoded-isolated/decoded.json').read_text());ext=json.loads((out/'resources-isolated/extract.json').read_text())
    checks=dict(originalsPreserved={str(f):sha(f)for f in [photo,movie]}==before,
                exactStillPTS=report['exactStillPTSMatch'],nativeStillDimensions=[info['photoCodes']['width'],info['photoCodes']['height']]==[1024,768],
                nativeVideoDimensions=report['resolution']==[128,96],nativeThumbFrames=len(info['thumbnails'])==28,
                stillNativeMirror=report['photoNativeMirrorMaxAbs']<5e-6,videoNativeMirror=report['videoNativeMirrorMaxAbs']<5e-6,
                geometryIndependentOfLinearPixels=report['geometry']['geometrySource'].startswith('SDR primary'),
                geometryCorrelation=report['geometry']['finalCorrelation']>.98,
                wrongTransferControlsWorse=report['controls']['inverse_sRGB_Rec2020']['maeEV']>report['primary']['maeEV']and report['controls']['codes_as_linear_Rec2020']['maeEV']>report['primary']['maeEV'],
                holdoutSampleCount=report['primary']['testPixels']>3000,plotsExist=(out/'analysis/comparison.png').exists()and(out/'analysis/comparison.svg').exists())
    isolated=(out/'resources-isolated/linear-isolated.heic').read_bytes()
    data_box=next(b for b in boxes(isolated,0,len(isolated))if b['kind']=='mdat')
    compressed=isolated[data_box['data']:data_box['end']]
    checks['compressedPayloadPreserved']=hashlib.sha256(compressed).hexdigest()==ext['compressedItemPayloadSHA256']and photo.read_bytes().count(compressed)==1
    receipt=dict(schema='paired-thumbnail-experiment-verification-v1',technicalChecks=checks,technicalPass=all(checks.values()),
                 scientificConclusion='Observe results.json; technical pass does not mean exact pixel or absolute radiometric equivalence.',
                 sourceHashes=before,sourceCodeHashes={f.name:sha(f)for f in SRC.iterdir()if f.suffix in ['.py','.m']},steps=steps,
                 resultSHA256=sha(out/'analysis/results.json'),compressedPayloadSHA256=ext['compressedItemPayloadSHA256'])
    (out/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');assert receipt['technicalPass'],checks
    print(json.dumps({'technicalPass':True,'primary':report['primary'],'metadataScale':report['metadataScaleHypothesis']['scale'],'matchedBand':report['symmetricLowPassComparisons'][-1]},indent=2),flush=True)

if __name__=='__main__':main()
