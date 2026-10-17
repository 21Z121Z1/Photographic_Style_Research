#!/usr/bin/env python3
"""Read linked HEIF items; redirect pitm in new containers, never edit sources."""
from pathlib import Path
import sys,json,hashlib,plistlib,struct
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tools.heif_dump import parse_heif,iter_boxes,parse_infe,_payload_from_item_extents

def digest(b): return hashlib.sha256(b).hexdigest()
def safe(x):
 if isinstance(x,bytes): return {'bytes':len(x),'sha256':digest(x)}
 if isinstance(x,dict): return {str(k):safe(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)): return [safe(v) for v in x]
 return x


def libheif_visible(data,itemid):
 """Change container declarations only; original HEVC bytes stay untouched."""
 h=parse_heif(data);copy=bytearray(data)
 meta=next(b for b in iter_boxes(data) if b['type']=='meta')
 children=iter_boxes(data,meta['payload_offset']+4,meta['offset']+meta['size'])
 for b in children:
  pos=b['payload_offset']
  if b['type']=='pitm':
   n=2 if data[pos]==0 else 4;copy[pos+4:pos+4+n]=itemid.to_bytes(n,'big')
  elif b['type']=='iinf':
   n=2 if data[pos]<=1 else 4
   for infe in iter_boxes(data,pos+4+n,b['offset']+b['size']):
    info=parse_infe(data,infe)
    if info.get('item_type') in ('grid','hvc1','av01'):
     q=infe['payload_offset'];copy[q+1:q+4]=(0 if info.get('item_id')==itemid else 1).to_bytes(3,'big')
  elif b['type']=='iref':
   n=2 if data[pos]==0 else 4
   for ref in iter_boxes(data,pos+4,b['offset']+b['size']):
    q=ref['payload_offset']
    if ref['type']=='auxl' and int.from_bytes(data[q:q+n],'big')==itemid:
     q=ref['offset'];copy[q+4:q+8]=b'free'
 for assoc in h['items'][str(itemid)]['property_associations']:
  if assoc['type']=='auxC':
   q=h['properties'][assoc['property_index']-1]['offset'];copy[q+4:q+8]=b'free'
 return bytes(copy)

def extract(path,out):
 data=path.read_bytes(); h=parse_heif(data); primary=h['primary_item_id']
 def unique(pred,kind):
  match=[i for i in h['items'].values() if pred(i) and any(r['from_item_id']==i['item_id'] and primary in r['to_item_ids'] and r['type']==kind for r in h['references'])]
  if len(match)!=1: raise ValueError(f'{path}: expected one linked item, got {len(match)}')
  return match[0]
 style=unique(lambda i:i.get('uri_type')=='tag:apple.com,2023:photo:metadata:styles','cdsc')
 out.mkdir(parents=True,exist_ok=True)
 raw=_payload_from_item_extents(data,style); (out/'styles.plist').write_bytes(raw)
 stored=plistlib.loads(raw); (out/'styles-summary.json').write_text(json.dumps(safe(stored),ensure_ascii=False,indent=2)+'\n')
 (out/'container.json').write_text(json.dumps(h,indent=2)+'\n')
 meta=next(b for b in iter_boxes(data) if b['type']=='meta')
 pitm=next(b for b in iter_boxes(data,meta['payload_offset']+4,meta['offset']+meta['size']) if b['type']=='pitm')
 pos=pitm['payload_offset']; n=2 if data[pos]==0 else 4
 inventory={'photo':path.name,'source_sha256':digest(data),'primary_id':primary,'metadata_id':style['item_id'],'version':stored.get('0'),'items':{}}
 for key,suffix in [('linear','linearthumbnail'),('delta','styledeltamap')]:
  item=unique(lambda i:i.get('aux_type')==f'tag:apple.com,2023:photo:aux:{suffix}','auxl')
  copy=libheif_visible(data,item['item_id'])
  target=out/f'{key}.heic'; target.write_bytes(copy)
  inventory['items'][key]={k:safe(item[k]) for k in ['item_id','item_type','dimensions','pixi','hvcC','colr'] if k in item}
  inventory['items'][key]['container_sha256']=digest(copy)
 for k in ['1','3','c','d']:
  if isinstance(stored.get(k),bytes): (out/f'key{k}.bin').write_bytes(stored[k])
 (out/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
 print(json.dumps(inventory))
 return inventory
if __name__=='__main__':
 source=Path(sys.argv[1]);out=Path(sys.argv[2]);extract(source,out)
 h=parse_heif(source.read_bytes())
 choices={'inputSubjectMatteImage':['semanticpersonmatte'],'inputSkinMatteImage':['semanticskinmattev2','semanticskinmatte'],'inputSkyMatteImage':['semanticskymatte'],'inputGainMapImage':['hdrgainmap']}
 meta=next(b for b in iter_boxes(source.read_bytes()) if b['type']=='meta')
 pitm=next(b for b in iter_boxes(source.read_bytes(),meta['payload_offset']+4,meta['offset']+meta['size']) if b['type']=='pitm')
 for key,suffixes in choices.items():
  items=[i for i in h['items'].values() if any(i.get('aux_type','').endswith(s) for s in suffixes)]
  if items:
   b=libheif_visible(source.read_bytes(),items[0]['item_id']);(out/(key+'.heic')).write_bytes(b)
