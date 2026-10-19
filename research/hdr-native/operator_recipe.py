"""26A434 consumer parameter retargeting with explicit evidence boundaries.

These are known-input forward counterfactual controls. They do not invert an
observed final image and cannot identify the camera's baked local processing.
The native shader, metadata decoder, Apple Log path, and frozen models stay
unchanged. Use only with the corresponding original captured 672-byte layout.
"""
from dataclasses import dataclass
from hashlib import sha256
import math,struct

LAYOUT_BUILD='26A434'
@dataclass(frozen=True)
class RetargetResult:
 parameters: bytes
 report: dict

def retarget(parameters,*,operator,strength,os_build,context_sha256,known_input_available):
 if os_build!=LAYOUT_BUILD:raise ValueError('This layout is validated only on26A434')
 if len(parameters)!=672:raise ValueError('Expected original672-byte SSRParams buffer')
 if not known_input_available:raise ValueError('Retargeting final Y requires a separately validated set inverse; direct parameter replay on Y is not that inverse')
 if not math.isfinite(strength) or not 0<=strength<=1:raise ValueError('Withdrawal strength must be in[0,1]')
 if len(context_sha256)!=64 or any(c not in '0123456789abcdef' for c in context_sha256):raise ValueError('Frozen context SHA256 required')
 targets={'local.consumer_ltm':{620:1.,624:1.},'local.consumer_background':{620:1.},'local.consumer_person':{624:1.},'semantic.skin_color':{592:0.},'semantic.skin_brightness':{596:0.},'semantic.skin_both':{592:0.,596:0.}}
 if operator not in targets:raise ValueError('Unknown or unverified operator. Camera j, global exposure and Studio cannot be guessed from this layout.')
 out=bytearray(parameters);changes=[];allowed=set()
 for offset,neutral in targets[operator].items():
  original=struct.unpack_from('<f',parameters,offset)[0]
  if not math.isfinite(original):raise ValueError('Nonfinite source parameter requires explicit native contract')
  if operator.startswith('local.') and not 0<=original<=1:raise ValueError('Captured local mixture lies outside the verified control interval')
  # Our withdrawal policy, not Apple's UI-tone mapping. Endpoints have native
  # S27 oracle evidence; other strengths need their own native receipt.
  # The arithmetic order agrees with S27's (v+1)*.5 at strength=.5.
  f=lambda v:struct.unpack('<f',struct.pack('<f',v))[0]
  if strength==0:target=original
  elif strength==1:target=f(neutral)
  elif strength==.5 and neutral==1:target=f(f(original+1)*.5)
  else:target=f(f(f(1-strength)*original)+f(f(strength)*neutral))
  struct.pack_into('<f',out,offset,target);allowed.update(range(offset,offset+4));changes.append({'offset':offset,'before':original,'target':target,'neutral':neutral})
 outside=sum(a!=b and i not in allowed for i,(a,b) in enumerate(zip(parameters,out)));assert outside==0
 return RetargetResult(bytes(out),{'operator':operator,'strength':strength,'os_build':os_build,'context_sha256':context_sha256,'target_fields':changes,'changed_bytes_outside_target':outside,'source_parameters_sha256':sha256(parameters).hexdigest(),'target_parameters_sha256':sha256(out).hexdigest(),'execution':'Known-input retained-Apple-PSO counterfactual; not an inverse solution from final Y','scene_referred_verified':False,'camera_local_inverse_verified':False,'semantic_j_is_direct_gain':False})
