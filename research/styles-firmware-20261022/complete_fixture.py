"""Freeze saved S14B fixture0, extending its previously unspecified main ABI."""
import numpy as np
from native_ltm_roi_chain import fixture,EPSILON
from complete_forward import Context
from semantic_tone import Curve1D


def context():
    f=fixture(0);h,w=f['primary'].shape[:2];y,x=np.mgrid[:h,:w]
    # Guide8/9 and mask values reuse saved S14C case0 auxiliary inputs. Their
    # upstream generators are not part of this conditional model.
    g8=(.2+.04*x+.03*y)[...,None].astype('f2');g9=(.35+.02*x+.01*y)[...,None].astype('f2');person=(.4+.03*x)[...,None].astype('f2');skin=(.25+.02*y+np.zeros_like(x))[...,None].astype('f2');sky=np.full((h,w,1),.2,dtype='f2');lookup=np.zeros((4,360,4),dtype='f2')
    management=np.zeros(80,dtype='f4')
    for slot in range(4):
        management.view('u4')[20*slot]=3
        columns=f['columns']if slot in(0,1)else np.eye(3,dtype='f4')
        for col in range(3):management[20*slot+4+4*col:20*slot+7+4*col]=columns[col]
    p=np.zeros(168,dtype='f4');p[1]=.7;p[4:8]=[.25,.65,.9,.8];p[42]=.8;p[111]=4;p[122+8]=1;p[122+11]=1;p[139]=1;p[139+5]=1;p[155:162]=f['semantic'];p.view('u4')[163]=2;p[167]=-1
    # Keep valid nonselected internal haze parameters; do not rely on outer
    # selection to conceal NaN from an all-zero denominator block.
    p[114:122]=[.05,.8,.6,.1,.08,.4,.03,.02]
    s=np.zeros(2660,dtype='f4')
    for g,k,value in [(2,4,.3),(3,4,.2),(4,4,.25),(5,0,.2),(6,6,.45),(6,4,.4)]:s[2560+g*9+k]=value
    roi=np.zeros(44,dtype='f4');roi.view('u2')[:6]=[w,h,w,h,w+1,h+1]
    for k in range(3,12):roi[4*(k-3)+4:4*(k-3)+8]=[1/w,1/h,0,0]
    roi[12:16]=f['ROI5'];roi[16:20]=f['ROI6'];roi.view('u2')[80:82]=[1,1]
    return Context((f['primary'],f['linear'],f['guide'],f['matte'],g8,g9,person,skin,sky,lookup),management,p,s,roi,np.array([f['SRL']],dtype='f4'),Curve1D(tuple(np.linspace(0,1,17)**.8),'supplied AIR7 GTC'),Curve1D(tuple(np.linspace(0,1,17)**1.1),'supplied whites'),EPSILON,(2,3),np.full((h+2,w+2,4),-.75,dtype='f2'),0)


def encode(c):
    return {'identity':{'hardware':c.hardware,'build':c.build,'product':'Styles2 reference','bundle':'SmartStyleV1','class':'CMISmartStyleProcessorV1','IMG2810_identity_asserted':False},'origin':'S14B saved fixture0 source/guide/linear/matte/CCM/semantic/SRL/ROI5/6; main auxiliary values from saved S14C case0; remaining raw main fields explicitly completed once','images_half_bits':[a.view('u2').tolist()for a in c.images],'image_roles':['primary','linear','original guide','producer matte','guide8','guide9','person','skin','sky','selective lookup'],'raw_f32_bits':{n:getattr(c,n).view('u4').tolist()for n in ['management','params','stats','roi','srl']},'gtc':list(c.gtc.red_samples),'whites':list(c.whites.red_samples),'epsilon_f32_bits':int(np.array(c.epsilon).view('u4')),'producer_shape':c.producer_shape,'output_initial_half_bits':c.output_initial.view('u2').tolist(),'version':c.version,'remaining_external_inputs':['guide8/9 raw textures and their unmodeled producers','person/skin/sky masks and their unmodeled producers','GTC/whites curves','34 cast values; full tuning and auxiliary coefficients','raw stats reference fields','selective lookup and unmodeled producer','CCMs/transfer enums/SRL/ROI/format/version identity'],'intermediate_outputs_supplied':False}


def decode(d):
    images=tuple(np.array(a,dtype='u2').view('f2')for a in d['images_half_bits']);buffers={n:np.array(a,dtype='u4').view('f4')for n,a in d['raw_f32_bits'].items()}
    return Context(images,**buffers,gtc=Curve1D(tuple(d['gtc']),'supplied AIR7 GTC'),whites=Curve1D(tuple(d['whites']),'supplied whites'),epsilon=np.array(d['epsilon_f32_bits'],dtype='u4').view('f4')[()],producer_shape=tuple(d['producer_shape']),output_initial=np.array(d['output_initial_half_bits'],dtype='u2').view('f2'),version=d['version'],hardware=d['identity']['hardware'],build=d['identity']['build'])
