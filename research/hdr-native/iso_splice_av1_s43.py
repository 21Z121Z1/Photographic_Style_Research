"""Direct ISO gain-item replacement derived from the frozen carrier writer.
Experimental AV1 map item with untouched HEVC primary; format/native support not assumed.
Native support of new bit depths is a separate gate, never inferred here.
"""
import struct
from tools.heif_dump import parse_heif,iter_boxes,parse_infe,_payload_from_item_extents
def u16(v):return struct.pack('>H',v)
def u32(v):return struct.pack('>I',v)
def box(kind,payload):return u32(len(payload)+8)+kind.encode()+payload
def full(kind,payload,version=0,flags=0):return box(kind,bytes([version])+flags.to_bytes(3,'big')+payload)
def payload(data,item):return _payload_from_item_extents(data,item)
def tmap_metadata(min_ev,max_ev,offset,capacity_log2):
 values=[0,capacity_log2,min_ev,max_ev,1,offset,offset]
 return bytes([0,0,0,0,0,0x40])+b''.join(struct.pack('>iI',round(v*1_000_000),1_000_000) for v in values)
def replace_map(source,encoded,metadata):
 h=parse_heif(source);enc=parse_heif(encoded);tmap=[i for i in h['items'].values() if i.get('item_type')=='tmap'];assert len(tmap)==1
 tid=tmap[0]['item_id'];ref=next(r for r in h['references'] if r['type']=='dimg' and r['from_item_id']==tid);base,gid=ref['to_item_ids'];assert base==h['primary_item_id']
 ep=enc['items'][str(enc['primary_item_id'])];assert ep['item_type']=='av01','Single direct AV1 gain image expected';assert ep['pixi']['channels']==3 and set(ep['pixi']['bits']) in ({10},{12});assert sum(p['type']=='av1C' for p in enc['properties'])==1
 items=sorted(h['items'].values(),key=lambda i:i['item_id']);raws={i['item_id']:payload(source,i) for i in items};raws[gid]=payload(encoded,ep);raws[tid]=metadata
 meta=next(b for b in iter_boxes(source) if b['type']=='meta');children=iter_boxes(source,meta['payload_offset']+4,meta['offset']+meta['size']);iinf=next(b for b in children if b['type']=='iinf');s=iinf['payload_offset'];n=2 if source[s]<=1 else 4
 infes=[]
 for b in iter_boxes(source,s+4+n,iinf['offset']+iinf['size']):
  i=parse_infe(source,b)
  infes.append(full('infe',u16(gid)+u16(0)+b'av01\0',version=2,flags=1) if i.get('item_id')==gid else source[b['offset']:b['offset']+b['size']])
 props=[source[p['offset']:p['offset']+p['size']] for p in h['properties']];newassoc=[]
 for a in ep['property_associations']:
  p=enc['properties'][a['property_index']-1]
  if p['type'] not in ('av1C','ispe','pixi','colr'):continue
  props.append(encoded[p['offset']:p['offset']+p['size']]);newassoc.append((len(props),a.get('essential',False)))
 # ISO auxiliary semantic; keep the source gain root's rotation aligned with SDR.
 props.append(full('auxC',b'urn:iso:std:iso:ts:21496:-1\0'));newassoc.append((len(props),False))
 for a in h['items'][str(gid)].get('property_associations',[]):
  if h['properties'][a['property_index']-1]['type']=='irot':newassoc.append((a['property_index'],a.get('essential',False)))
 assoc=[]
 for i in items:
  a=newassoc if i['item_id']==gid else [(a['property_index'],a.get('essential',False)) for a in i.get('property_associations',[])]
  if a:assoc.append(u16(i['item_id'])+bytes([len(a)])+b''.join(u16(index|(0x8000 if essential else 0)) for index,essential in a))
 iprp=box('iprp',box('ipco',b''.join(props))+full('ipma',u32(len(assoc))+b''.join(assoc),flags=1))
 refs=[r for r in h['references'] if not(r['type'] in ('dimg','auxl') and r['from_item_id']==gid)]
 refs.append({'type':'auxl','from_item_id':gid,'to_item_ids':[base,tid]})
 iref=full('iref',b''.join(box(r['type'],u16(r['from_item_id'])+u16(len(r['to_item_ids']))+b''.join(u16(j) for j in r['to_item_ids'])) for r in refs))
 def iloc(start):
  p=bytes([0x44,0])+u16(len(items));cursor=start
  for item in items:
   b=raws[item['item_id']];p+=u16(item['item_id'])+u16(0)+u16(1)+u32(cursor)+u32(len(b));cursor+=len(b)
  return full('iloc',p)
 hdlr=next(b for b in children if b['type']=='hdlr');hdlr=source[hdlr['offset']:hdlr['offset']+hdlr['size']];pitm=full('pitm',u16(base));iinf=full('iinf',u16(len(infes))+b''.join(infes))
 ftyp=next(b for b in iter_boxes(source) if b['type']=='ftyp');ftyp=source[ftyp['offset']:ftyp['offset']+ftyp['size']]
 extras=b''.join(source[z['offset']:z['offset']+z['size']] for z in children if z['type'] not in ('hdlr','pitm','iinf','iloc','iprp','iref','idat'))
 meta=full('meta',hdlr+pitm+iinf+iloc(0)+iprp+iref+extras);meta=full('meta',hdlr+pitm+iinf+iloc(len(ftyp)+len(meta)+8)+iprp+iref+extras)
 out=ftyp+meta+box('mdat',b''.join(raws[i['item_id']] for i in items));new=parse_heif(out)
 # Preserve all original coded primary descendants and exact color/geometry properties.
 queue=[base];seen=set()
 while queue:
  iid=queue.pop()
  if iid in seen:continue
  seen.add(iid);old=h['items'][str(iid)];now=new['items'][str(iid)];assert payload(source,old)==payload(out,now)
  op=[source[h['properties'][a['property_index']-1]['offset']:h['properties'][a['property_index']-1]['offset']+h['properties'][a['property_index']-1]['size']] for a in old.get('property_associations',[])];np_=[out[new['properties'][a['property_index']-1]['offset']:new['properties'][a['property_index']-1]['offset']+new['properties'][a['property_index']-1]['size']] for a in now.get('property_associations',[])];assert op==np_
  queue.extend(j for r in h['references'] if r['type']=='dimg' and r['from_item_id']==iid for j in r['to_item_ids'])
 return out,{'primary_item_id':base,'gain_item_id':gid,'tmap_item_id':tid,'primary_descendant_payloads_checked':len(seen),'primary_coded_and_properties_identical':True}
