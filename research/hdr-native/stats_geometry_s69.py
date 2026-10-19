"""Integer geometry of the original statistics host, not a scene certificate.
Scope: positive integer full-frame render/statistics ROI at origin0; source
sampling transforms and original caller remain separate preconditions.
"""
def full_frame(width,height,thread_width,max_threads):
    if not all(isinstance(x,int)and not isinstance(x,bool)and x>0 for x in [width,height,thread_width,max_threads]):
        raise ValueError('positive integer geometry and original PSO limits required')
    tx=min((width+31)//32,thread_width)
    ty=min((height+31)//32,max_threads//tx)
    if ty<1:raise ValueError('PSO cannot host this group')
    x,y=width//tx,height//ty
    return {'group':[tx,ty,1],'tile_range':[x,y],
            'within_fixed_32_array':x<=32 and y<=32,
            'aligned_full_grid':32*tx==width and 32*ty==height,
            'caller_binding_or_scene_accuracy_certified':False}
