"""Bounded practical strength control for a conditional semantic counterfactual.

Run image work on the macOS runner. The native full/neutral evaluations must
share the same recovered input and all external context. This does not identify
baked camera parameters, produce a unique inverse, or undo global/local tone.
"""
import numpy as np

def apply(base, recovered_native, recovered_neutral, strength):
    """Use D=F_neutral(xhat)-F(xhat), C=base+D, then RGB log-ratio strength.

    Exact identity at zero strength. Outside the finite, strictly RGB-positive
    ratio domain preserve the base and return an explicit mask. No extra matte,
    spatial smoother, black replacement, tone or exposure operation is hidden.
    Strength is an output-effect interpolation, not an Apple parameter setting.
    """
    arrays=[np.asarray(x)for x in [base,recovered_native,recovered_neutral]]
    if any(x.shape!=arrays[0].shape for x in arrays)or arrays[0].ndim<2 or arrays[0].shape[-1]!=3:
        raise ValueError('Matching RGB tile shapes required')
    if arrays[0].size>3*262144:raise ValueError('Stream tiles of at most262144 pixels on the macOS runner')
    if not np.isfinite(strength)or not 0<=strength<=1:raise ValueError('Strength must be finite and in[0,1]')
    if arrays[0].dtype not in [np.dtype('f4'),np.dtype('f8')]:raise ValueError('Base must be float32 or float64; preserve its storage at strength0')
    a,f,n=[x.astype('f8',copy=False)for x in arrays]
    candidate=a+(n-f)
    finite=np.isfinite(a).all(-1)&np.isfinite(f).all(-1)&np.isfinite(n).all(-1)&np.isfinite(candidate).all(-1)
    valid=finite&(a.min(-1)>0)&(candidate.min(-1)>0)
    loggain=np.zeros(a.shape,'f8')
    loggain[valid]=np.log2(candidate[valid])-np.log2(a[valid])
    result=np.array(arrays[0],copy=True)
    if strength:
        selected=a[valid]*np.exp2(float(strength)*loggain[valid])
        if not np.isfinite(selected).all():raise FloatingPointError('Finite-domain correction overflow; preserve and report rather than upload invalid output')
        result[valid]=selected.astype(result.dtype)
    return {'rgb':result,'log2_gain':loggain*float(strength),'ratio_valid':valid,'nonfinite_context':~finite,'candidate_nonpositive':finite&(candidate.min(-1)<=0),'base_nonpositive':finite&(a.min(-1)<=0),'unique_inverse_certified':False}
