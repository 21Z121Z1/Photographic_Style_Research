"""Copy a HEIF image and its dimg descendants into a minimal lossless wrapper.

Only container metadata is rebuilt. No image codec is called; hashes prove each
coded item payload and relevant raw color/codec property is preserved.
"""
import struct,hashlib
from tools.heif_dump import parse_heif,_payload_from_item_extents

def u16(n):return struct.pack('>H',n)
def u32(n):return struct.pack('>I',n)
def box(t,b):return u32(len(b)+8)+t.encode('ascii')+b
def full(t,b=b'',version=0,flags=0):return box(t,bytes([version])+flags.to_bytes(3,'big')+b)
def standalone(data,itemid):
 h=parse_heif(data);ids=[];links=[]
 def visit(i):
  if i in ids:return
  ids.append(i)
  for r in h['references']:
   if r['type']=='dimg' and r['from_item_id']==i:
    links.append(r)
    for j in r['to_item_ids']:visit(j)
 visit(itemid);mapping={iid:n+1 for n,iid in enumerate(ids)}
 payloads=[_payload_from_item_extents(data,h['items'][str(i)]) for i in ids]
 ftyp=box('ftyp',b'heic'+u32(0)+b'mif1heicmiaf')
 hdlr=full('hdlr',u32(0)+b'pict'+bytes(12)+b'PictureHandler\0')
 pitm=full('pitm',u16(1));infes=[];properties=[];assocs=[];property_index={}
 for i in ids:
  item=h['items'][str(i)];kind=item['item_type'];nid=mapping[i]
  infes.append(full('infe',u16(nid)+u16(0)+kind.encode()+b'\0',version=2,flags=0 if i==itemid else 1))
  refs=[]
  for a in item.get('property_associations',[]):
   prop=h['properties'][a['property_index']-1]
   if prop['type'] not in ('hvcC','ispe','pixi','colr','clap','pasp'):continue
   raw=data[prop['offset']:prop['offset']+prop['size']]
   if raw not in property_index:properties.append(raw);property_index[raw]=len(properties)
   refs.append(property_index[raw]|(0x8000 if a.get('essential') else 0))
  assocs.append(u16(nid)+bytes([len(refs)])+b''.join(u16(r) for r in refs))
 iinf=full('iinf',u16(len(infes))+b''.join(infes));iprp=box('iprp',box('ipco',b''.join(properties))+full('ipma',u32(len(ids))+b''.join(assocs),flags=1))
 iref=full('iref',b''.join(box('dimg',u16(mapping[r['from_item_id']])+u16(len(r['to_item_ids']))+b''.join(u16(mapping[j]) for j in r['to_item_ids'])) for r in links)) if links else b''
 def iloc(start):
  p=bytes([0x44,0])+u16(len(ids));cursor=start
  for i,payload in zip(ids,payloads):
   p+=u16(mapping[i])+u16(0)+u16(1)+u32(cursor)+u32(len(payload));cursor+=len(payload)
  return full('iloc',p)
 meta=full('meta',hdlr+pitm+iinf+iloc(0)+iprp+iref);start=len(ftyp)+len(meta)+8
 meta2=full('meta',hdlr+pitm+iinf+iloc(start)+iprp+iref);assert len(meta2)==len(meta)
 out=ftyp+meta2+box('mdat',b''.join(payloads));parsed=parse_heif(out)
 for i,payload in zip(ids,payloads):assert _payload_from_item_extents(out,parsed['items'][str(mapping[i])])==payload
 return out
