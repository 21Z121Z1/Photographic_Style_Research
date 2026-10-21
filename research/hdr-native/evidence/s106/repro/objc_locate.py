"""Bounded ObjC method locators, calibrated against two existing native symbols.

Layout reference: Apple's objc4/runtime/objc-runtime-new.h. Locators do not
constitute pixel-order or file-thumbnail provenance evidence.
"""
from pathlib import Path
import importlib.util
import json
import re
import struct

C=Path(__file__).resolve().parent;R=Path('/home/Z121Z121/work/styles-gtm-ltm')
s=importlib.util.spec_from_file_location('cache',R/'iterations/20261018-v3/scripts/ios_cache_reader.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);c=m.Cache()
images=json.loads((C/'locators.json').read_text())['images'];rows=[];unknown=[]

def ptr(value):
    return c.decode_pointer(value)

def named(pointer):
    return c.text(pointer)if pointer else None

def method_lists(raw):
    if raw==0:return []
    address=ptr(raw&~1)
    if address is None:raise ValueError('unresolved method list pointer')
    if raw&1:
        stride,count=struct.unpack('<II',c.read(address,8));assert stride==8 and count<10000
        out=[]
        for i in range(count):
            entry=address+8+8*i;v=c.u64(entry);relative=v>>16;relative-=1<<48 if relative&(1<<47)else 0
            out.append(entry+relative)
        return out
    return [address]

def entries(raw):
    result=[]
    for address in method_lists(raw):
        flags,count=struct.unpack('<II',c.read(address,8));stride=flags&0xfffc
        assert count<20000 and stride in[12,24]
        for i in range(count):
            a=address+8+i*stride
            if flags&0x80000000:
                assert stride==12
                no,to,im=struct.unpack('<iii',c.read(a,12))
                result.append({'entry':a,'relative_name':no,'types':named(a+4+to),'IMP':a+8+im,'flags':flags})
            else:
                assert stride==24
                n,t,im=struct.unpack('<QQQ',c.read(a,24))
                result.append({'entry':a,'absolute_name':ptr(n),'types':named(ptr(t)),'IMP':ptr(im),'flags':flags})
    return result

classes=[]
for image in images:
    section=next((x for x in image['selected_sections']if x['name']=='__objc_classlist'),None)
    if not section:continue
    raw=c.read(int(section['address'],16),section['bytes'])
    for index in range(0,len(raw),8):
        cl=ptr(struct.unpack_from('<Q',raw,index)[0])
        if cl is None:unknown.append({'framework':image['framework'],'stage':'class_pointer'});continue
        for role,obj in[('instance',cl),('class',ptr(c.u64(cl)))]:
            try:
                if obj is None:raise ValueError('missing metaclass')
                ro=ptr(c.u64(obj+32)&~7)
                if ro is None:raise ValueError('missing class RO')
                name=named(ptr(c.u64(ro+24)))
                if not name or not re.fullmatch(r'[A-Za-z_$][A-Za-z0-9_.$]*',name):raise ValueError('unvalidated class name')
                methods=entries(c.u64(ro+32))
                classes.append({'framework':image['framework'],'class':name,'role':role,'methods':methods})
            except (ValueError,AssertionError,struct.error):
                unknown.append({'framework':image['framework'],'stage':'class_RO_or_methods','role':role,'class_address':hex(cl)})

def selector_from_stub(start):
    regs={}
    for k in range(8):
        a=start+4*k;ins=struct.unpack('<I',c.read(a,4))[0];rd=ins&31;rn=(ins>>5)&31
        if ins&0x9f000000==0x90000000:
            imm=((ins>>29)&3)|(((ins>>5)&0x7ffff)<<2);imm-=1<<21 if imm&(1<<20)else 0;regs[rd]=(a&~4095)+(imm<<12)
        elif ins&0xffc00000==0x91000000 and rn in regs:
            regs[rd]=regs[rn]+((ins>>10)&4095)*(4096 if(ins>>22)&1 else 1)
            if rd==1 and named(regs[rd]):return regs[rd],named(regs[rd])
        elif ins&0xffc00000==0xf9400000 and rn in regs:
            regs[rd]=c.u64(regs[rn]+((ins>>10)&4095)*8)
            if rd==1:
                p=ptr(regs[rd])
                if named(p):return p,named(p)
    raise ValueError('unresolved selected selector stub')

calibrations=[]
for imp,stub,expected in[(0x256b77b14,0x2580b9950,'generateLinearRGBATexture:'),(0x256baf924,0x2580b96f0,'createLTMInTextureFromRGBAFloatTex:undoScaleDown:')]:
    candidates=[q for cl in classes if cl['class']=='LTMProcessor'and cl['role']=='instance'for q in cl['methods']if q['IMP']==imp]
    assert len(candidates)==1
    selector,text=selector_from_stub(stub);assert text==expected
    q=candidates[0];assert 'relative_name'in q
    calibrations.append({'selector':text,'IMP':hex(imp),'stub':hex(stub),'selector_chars_address':hex(selector),'relative_name':q['relative_name'],'shared_selector_base':selector-q['relative_name']})
assert len({x['shared_selector_base']for x in calibrations})==1
base=calibrations[0]['shared_selector_base']
total=0
for cl in classes:
    for q in cl['methods']:
        name=named(q['absolute_name'])if'absolute_name'in q else named(base+q['relative_name'])if q['flags']&0x40000000 else named(ptr(c.u64(q['entry']+q['relative_name'])))
        if not name:continue
        total+=1
        if 'linearthumbnail'in name.lower()or'linearthumbnail'in cl['class'].lower()or('CMI' in cl['class']and 'thumbnail'in name.lower()):
            rows.append({'framework':cl['framework'],'class':cl['class'],'role':cl['role'],'selector':name,'IMP':hex(q['IMP'])if q['IMP']else None,'method_entry':hex(q['entry']),'types':q['types']})
assert c.unchanged()
result={'source_layout_reference':'https://github.com/apple-oss-distributions/objc4/blob/main/runtime/objc-runtime-new.h','reference_build_only':'24A446 iPhone12,1','calibrations':calibrations,'method_names_resolved':total,'class_groups_parsed':len(classes),'unresolved_groups':unknown,'categories_not_parsed':True,'locators_not_algorithm_or_provenance_proof':True,'rows':rows,'cache_unchanged':True}
with(C/'objc-locators.json').open('x')as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'method_names_resolved':total,'matching_locators':len(rows),'unknown_class_groups':len(unknown),'two_selector_bases_agree':True,'cache_unchanged':True}))
