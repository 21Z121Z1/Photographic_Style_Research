"""Independent target -> explicit RGB ratio -> original native apply / HEIF.

Only synthetic fixtures. Heavy calculations stay on the macOS runner.
"""
from pathlib import Path
import os,subprocess,json,hashlib,math,sys,importlib.util
import numpy as np
from render_contract import gain_from_pair,apply_decoded_map,iso_scale
from analyze_hdr_s29 import metric
W=Path(os.environ['W']);O=W/'out';S=Path('research/hdr-native');O.mkdir(exist_ok=True)
assert subprocess.check_output(['sw_vers','-buildVersion'],text=True).strip()=='26A434'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
freeze={'scope':'Transport of known synthetic targets, no camera inverse','source_sha256':{p.name:sha(p) for p in [S/'carrier_oracle_s30.m',S/'run_hdr_s30.py',S/'render_contract.py']},'strict_gates':{'max_abs':1e-5,'PSNR_min_db':60,'relative_max':1e-3},'negative_components':'Excluded from exact-ratio eligible domain; recorded as loss, never silently clamped into a scene answer','automatic_HDRImage_generator':False}
(O/'formula-freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
with (O/'build.log').open('w') as f:subprocess.run(['clang','-O2','-fobjc-arc','-framework','Foundation','-framework','CoreImage','-framework','ImageIO','-framework','Metal','-framework','CoreGraphics',str(S/'carrier_oracle_s30.m'),'-o',str(W/'oracle')],stdout=f,stderr=subprocess.STDOUT,check=True)
sys.path.insert(0,str(Path('.').resolve()))
from tools.heif_dump import parse_heif
import xml.etree.ElementTree as ET
def metadata(lo,hi,cap):
 ch=''.join('<rdf:li rdf:parseType="Resource">'+''.join(f'<h:{k}>{v:.9f}</h:{k}>' for k,v in [('GainMapMin',lo),('GainMapMax',hi),('Gamma',1),('BaseOffset',1e-5),('AlternateOffset',1e-5)])+'</rdf:li>' for _ in range(3))
 xml=f'<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description xmlns:h="http://ns.apple.com/HDRToneMap/1.0/"><h:Version>1</h:Version><h:BaseHeadroom>0</h:BaseHeadroom><h:AlternateHeadroom>{cap:.9f}</h:AlternateHeadroom><h:ChannelMetadata><rdf:Seq>{ch}</rdf:Seq></h:ChannelMetadata><h:BaseColorIsWorkingColor>True</h:BaseColorIsWorkingColor></rdf:Description></rdf:RDF></x:xmpmeta>'
 return xml.replace('xmlns:h=', 'xmlns:HDRToneMap=').replace('<h:', '<HDRToneMap:').replace('</h:', '</HDRToneMap:')
def meta_from_xml(p):
 root=ET.parse(p).getroot();ns={'h':'http://ns.apple.com/HDRToneMap/1.0/','rdf':'http://www.w3.org/1999/02/22-rdf-syntax-ns#'};channels=root.findall('.//h:ChannelMetadata/rdf:Seq/rdf:li',ns);assert len(channels)==3
 def vector(k):return np.array([float(c.find('h:'+k,ns).text) for c in channels])
 def val(k):return float(root.find('.//h:'+k,ns).text)
 return {'gain_min':vector('GainMapMin'),'gain_max':vector('GainMapMax'),'inverse_gamma':1/vector('Gamma'),'offset_sdr':vector('BaseOffset'),'offset_hdr':vector('AlternateOffset')},val('BaseHeadroom'),val('AlternateHeadroom')
w,h=128,64;u=np.broadcast_to((np.arange(w)+.5)/w,(h,w));v=np.broadcast_to(((np.arange(h)+.5)/h)[:,None],(h,w));rows=[]
for name in ['gray-expansion','rgb-opposing','nearblack-highlight','flat-HDR','edge-HDR']:
 p=O/name;p.mkdir();inp=p/'input';inp.mkdir()
 if name=='gray-expansion':s=np.repeat((.002+.8*u)[...,None],3,-1);ev=np.repeat((3*u)[...,None],3,-1)
 elif name=='rgb-opposing':s=.04+.7*np.stack([u,v,1-u],-1);ev=np.stack([3*u,-.5+2*v,2*(1-u)],-1)
 elif name=='nearblack-highlight':a=np.where(u<8/w,0,np.where(u<16/w,1e-6,np.where(u<24/w,1e-4,u**3)));s=np.repeat(a[...,None],3,-1);ev=np.repeat((3*u**.25)[...,None],3,-1)
 elif name=='flat-HDR':s=np.full((h,w,3),.18);ev=np.full_like(s,3.)
 else:s=np.repeat(np.where(u<.5,.08,.65)[...,None],3,-1);ev=np.repeat(np.where(u<.5,2.,1.)[...,None],3,-1)
 # Freeze float32 inputs before deriving their ratio. The target is a supplied
 # rendition, not inferred scene radiance or a camera LTM inverse.
 s=s.astype('f4').astype('f8');t=(s*np.exp2(ev)).astype('f4').astype('f8');pair=gain_from_pair(s,t,offset_sdr=1e-5,offset_hdr=1e-5);assert pair['positive_ratio_mask'].all();lg=pair['log2_gain'];lo=float(min(lg.min(),0));hi=float(max(lg.max(),.001));cap=math.log2(max(t.max(),1.001));gm=((lg-lo)/(hi-lo)).astype('f4').astype('f8')
 def store(a,path):np.concatenate([a,np.ones(a.shape[:-1]+(1,))],-1).astype('<f4').tofile(path)
 for a,n in [(s,'base.f32'),(t,'target.f32'),(gm,'gain.f32')]:store(a,inp/n)
 (inp/'metadata.xml').write_text(metadata(lo,hi,cap));(inp/'input.json').write_text(json.dumps({'width':w,'height':h,'case':name,'target_defined_independently':True,'metadata':{'min':lo,'max':hi,'capacity_log2':cap}})+'\n')
 for fmt in [0,1]:
  out=p/('RGBAh' if fmt else 'RGBA8');out.mkdir()
  with (out/'native.log').open('w') as f:rc=subprocess.run([W/'oracle',inp,out,str(fmt)],stdout=f,stderr=subprocess.STDOUT).returncode
  row={'case':name,'format':'RGBAh' if fmt else 'RGBA8','native_returncode':rc,'gain_min_EV':lo,'gain_max_EV':hi,'native':json.loads((out/'native.json').read_text())};rows.append(row)
  # Even a writer failure retains the unencoded native results when available.
  def load(path):return np.fromfile(path,dtype='<f4').reshape(h,w,4)[...,:3].astype('f8')
  row['unencoded_headrooms']=[]
  for sweep in row['native'].get('unencoded_headrooms',[]):
   hr=sweep['headroom'];scale=iso_scale(hr,capacity_min_log2=0,capacity_max_log2=cap);expected=(s+1e-5)*np.exp2(scale*(lo+(hi-lo)*gm))-1e-5;actual=load(out/sweep['file']);row['unencoded_headrooms'].append({'headroom':hr,'reference_vs_native':metric(expected,actual),'native_vs_supplied_target':metric(actual,t)})
  if rc:continue
  hb=parse_heif((out/'manual.heic').read_bytes());row['coded_items']=[{k:i[k] for k in ['item_id','item_type','dimensions','pixi','hvcC','aux_type'] if k in i} for i in hb['items'].values()]
  base=load(out/'decoded-sdr.f32');full=load(out/'decoded-hdr.f32');gain=load(out/'decoded-gain.f32');meta,c0,c1=meta_from_xml(out/'metadata.xml')
  row['headrooms']=[]
  for sweep in row['native']['encoded_headrooms']:
   hr=sweep['headroom'];scale=iso_scale(hr,capacity_min_log2=c0,capacity_max_log2=c1);expected=apply_decoded_map(base,gain,scale=scale,**meta);actual=load(out/sweep['file']);row['headrooms'].append({'headroom':hr,'reference_vs_native':metric(expected,actual)})
  input_meta,_,_=meta_from_xml(inp/'metadata.xml');ideal=apply_decoded_map(s,gm,scale=1,**input_meta);using_decoded_base=apply_decoded_map(base,gm,scale=1,**input_meta)
  row['supplied_ratio_vs_target']=metric(ideal,t);row['SDR_codec_only']=metric(using_decoded_base,ideal);row['gain_codec_plus_metadata']=metric(full,using_decoded_base);row['combined_HDR_vs_target']=metric(full,t);row['decoded_gain_vs_supplied_code_max_abs']=float(abs(gain-gm).max())
  for bits in [8,10,12,16]:
   q=np.rint(gm*(2**bits-1))/(2**bits-1);row[f'uniform_{bits}bit_quantization_only']=metric(apply_decoded_map(s,q,scale=1,**input_meta),ideal)
report={'os_build':'26A434','formula_freeze_sha256':sha(O/'formula-freeze.json'),'scope':'Supplied target transport only, not inverse/scene/five-photo/full-resolution validation','rows':rows,'all_unencoded_native_formula_pass':all(x['reference_vs_native']['gate'] for r in rows for x in r['unencoded_headrooms']),'all_native_writers_succeeded':all(r['native_returncode']==0 for r in rows),'acceptance_complete':False}
(O/'analysis-s30.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='rows'}))
