"""Connect positive normalized Tone to the existing conditional skin operator.

Actual iPhone17,3/24A446 RenderingParamsFromStats AIR11 SSA368..374, branch339,
writes SSRFGAdjustment fields9/10. Domain is the *already scene-scaled* SSRParams
tone field [0,1], not a UI percentage, EV, original exposure or a full style.
These two fields in this branch are independent of stats; other fields are not.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'semantic-styles'))
import semantic_skin_model


@dataclass(frozen=True)
class SkinToneCoefficients:
    tone: np.float32
    theta9: np.float32
    theta10: np.float32
    native_GPU_verified: bool=False


def coefficients(tone: float) -> SkinToneCoefficients:
    t=np.float32(tone)
    if not np.isfinite(t) or not 0<=t<=1:raise ValueError('Only positive SSRParams tone field [0,1] is modeled')
    square=np.multiply(t,t,dtype=np.float32)
    theta9=np.subtract(np.multiply(t,np.float32(2.75),dtype=np.float32),np.multiply(square,np.float32(3.75),dtype=np.float32),dtype=np.float32)
    # Exact constants as f32 bit patterns from the original AIR, not rounded
    # decimal approximations of an inferred formula.
    a=np.array([0x3e554c98],dtype='u4').view('f4')[0]
    b=np.array([0x3f355326],dtype='u4').view('f4')[0]
    theta10=np.subtract(np.multiply(square,a,dtype=np.float32),np.multiply(t,b,dtype=np.float32),dtype=np.float32)
    return SkinToneCoefficients(t,theta9,theta10)


def forward(original,skin_weight,guide,*,tone: float):
    """Reuse the frozen continuous skin model; context is explicit and supplied.

    This omits other BG/FG/semantic/color/LTM terms. No pixel-domain or Apple
    GPU accuracy certificate is inherited from the coefficient connection.
    """
    p=coefficients(tone)
    return semantic_skin_model.forward(original,skin_weight,guide,float(p.theta9),float(p.theta10))
