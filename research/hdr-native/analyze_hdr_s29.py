"""Bounded synthetic comparison, run only on the macOS runner.

Uses the already recovered _flexMap equation and metadata, not a fit to native
outputs. Writer error, equation error and target representation error stay apart.
"""
from pathlib import Path
import json,hashlib,math,xml.etree.ElementTree as ET
import numpy as np
from render_contract import gain_from_pair,apply_decoded_map,iso_scale
Y=np.array([.2289745641,.6917385218,.0792869141])
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def metric(a,b):
 a=np.asarray(a,dtype='f8');b=np.asarray(b,dtype='f8');d=a-b
 finite=np.isfinite(a).all(-1)&np.isfinite(b).all(-1)
 if not finite.all():return {'nonfinite_pixels':int((~finite).sum()),'gate':False}
 mse=float(np.mean(d*d));maximum=float(abs(d).max());psnr=-10*math.log10(mse) if mse else 'inf'
 ev=np.log2(np.maximum(a@Y,1e-6)/np.maximum(b@Y,1e-6))
 return {'max_abs':maximum,'max_relative':float((abs(d)/np.maximum(abs(b),1e-6)).max()),'PSNR_peak1_db':psnr,'luma_EV_MAE':float(abs(ev).mean()),'luma_EV_max':float(abs(ev).max()),'nonpositive_luma_pixels':int(((a@Y)<=0).sum()),'gate':maximum<=1e-5 and (psnr=='inf' or psnr>=60)}
def analyze(root):
 root=Path(root);freeze=root/'reference-formula-freeze.json'
 assert freeze.exists(),'Freeze the equation before reading native outputs'
 results=json.loads((root/'native/native-results.json').read_text());rows=[]
 for case in results['cases']:
  p=root/'native'/case['case'];w=case['width'];h=case['height']
  def load(name):return np.fromfile(p/name,dtype='<f4').reshape(h,w,4)[...,:3].astype('f8')
  s=load('source-sdr.f32');t=load('target-hdr.f32')
  pair=gain_from_pair(s,t,offset_sdr=1e-5,offset_hdr=1e-5);mask=pair['positive_ratio_mask']
  g=pair['log2_gain'].astype('f4').astype('f8');rebuilt=(s+1e-5)*np.exp2(g)-1e-5
  row={'case':case['case'],'gain_present':case.get('gain_present',False),'known_pair_saved_f32_log_map':metric(rebuilt[mask],t[mask]),'eligible_pixels':int(mask.sum()),'pixels':mask.size}
  if not row['gain_present']:
   row['scope']='No gain map returned; original below-white target retained as a boundary observation';rows.append(row);continue
  base=load('decoded-sdr.f32');full=load('decoded-hdr.f32');gm=load('decoded-gain.f32')
  xml=ET.parse(p/'ISO-metadata.xml').getroot();ns={'h':'http://ns.apple.com/HDRToneMap/1.0/','rdf':'http://www.w3.org/1999/02/22-rdf-syntax-ns#'}
  def value(name):return float(xml.find('.//h:'+name,ns).text)
  channels=xml.findall('.//h:ChannelMetadata/rdf:Seq/rdf:li',ns)
  assert len(channels)==3
  def vector(name):return np.array([float(c.find('h:'+name,ns).text) for c in channels])
  meta={'gain_min':vector('GainMapMin'),'gain_max':vector('GainMapMax'),'inverse_gamma':1/vector('Gamma'),'offset_sdr':vector('BaseOffset'),'offset_hdr':vector('AlternateOffset')}
  capacity_min=value('BaseHeadroom');capacity_max=value('AlternateHeadroom')
  row['metadata']={k:v.tolist() for k,v in meta.items()}|{'capacity_min_log2':capacity_min,'capacity_max_log2':capacity_max,'metadata_source':'Original ImageIO XMP values; no native-output fitting'}
  row['writer_SDR_vs_supplied_SDR']=metric(base,s);row['writer_HDR_vs_supplied_HDR']=metric(full,t)
  row['decoded_gain_channel_abs_difference_max']=float(np.max(abs(gm-gm[...,:1])))
  row['headrooms']=[]
  for sweep in case['headroom_sweep']:
   headroom=sweep['requested_headroom'];scale=iso_scale(headroom,capacity_min_log2=capacity_min,capacity_max_log2=capacity_max)
   predicted=apply_decoded_map(base,gm,scale=scale,**meta);native=load(sweep['file'])
   row['headrooms'].append({'headroom':headroom,'scale':scale,'reference_vs_native':metric(predicted,native)})
  row['full_map_reference_vs_decoded_HDR']=metric(apply_decoded_map(base,gm,scale=1,**meta),full)
  rows.append(row)
 report={'os_build':'26A434','scope':'Synthetic pairs only; not five-photo, inverse, scene or actual display validation','formula_freeze_sha256':digest(freeze),'rows':rows,'all_sampled_formula_comparisons_pass':all(h['reference_vs_native']['gate'] for r in rows for h in r.get('headrooms',[])),'original_SDR_preservation_pass':all(r.get('writer_SDR_vs_supplied_SDR',{}).get('max_abs')==0 for r in rows if r['gain_present']),'old_acceptance_complete':False}
 (root/'analysis-s29.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
 return report
if __name__=='__main__':
 import sys
 r=analyze(sys.argv[1]);print(json.dumps({k:v for k,v in r.items() if k!='rows'}))
