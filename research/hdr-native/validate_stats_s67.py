"""Replay only S67 synthetic diagnostics; never changes inverse gates."""
import hashlib,io,json,struct,sys,tarfile
from pathlib import Path
p=Path(sys.argv[1]);assert hashlib.sha256(p.read_bytes()).hexdigest()=='543f9678c59945a304d32d0ffcf32c40c3a67d1d396360a930c07a9ca7c451d5'
with tarfile.open(p,'r:xz')as t:
    manifest=json.load(t.extractfile('manifest.json'));checks={x['path']:x['sha256']for x in manifest['files']}
    selected=json.load(t.extractfile('selection-provenance.json'))
    for n in selected['selected_original_members']:
        if n!='manifest.json':assert hashlib.sha256(t.extractfile(n).read()).hexdigest()==checks[n]
    rows=json.load(t.extractfile('synthetic.json'))['rows']
    for r in rows:
        w,h=r['W'],r['H'];raw=t.extractfile(f'stats-{w}.bin').read();n=sum(struct.unpack_from('<256I',raw));tx,ty,_=next(d for d in r['host']['dispatches']if d['PSO']=='_localHistogramStatsAll')['group']
        assert n==tx*ty*sum(min(w//tx,1024-32*y)for y in range(min(h//ty,32)))
        assert r['host']['input_textures_SHA_unchanged']
        assert struct.unpack_from('<f',raw,10256)[0]==(.25 if n/(w*h)>=.5 else 0)
    assert sum(r['hist0_model_equal']for r in rows)==2
print(json.dumps({'synthetic_cases':3,'conditional_diagnostics_passed':True,'original_frozen_model_passed':2,'acceptance_complete':False}))
