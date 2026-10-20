// Read-only binding/dispatch observer, adapted from encoder_capture_v2.inc.
// New synchronized state; opaque constant bytes are hashed, never serialized.
static NSMutableDictionary *T75States;
static NSMutableArray *T75Dispatches;
static NSObject *T75Lock;
static BOOL T75Active;
static NSUInteger T75Depth;
static BOOL T75CaptureLimit;
static NSString *T75EncoderClass;
static void(*T75OldPSO)(id,SEL,id);
static void(*T75OldTexture)(id,SEL,id,NSUInteger);
static void(*T75OldBytes)(id,SEL,const void*,NSUInteger,NSUInteger);
static void(*T75OldBuffer)(id,SEL,id,NSUInteger,NSUInteger);
static void(*T75OldGroups)(id,SEL,MTLSize,MTLSize);
static void(*T75OldThreads)(id,SEL,MTLSize,MTLSize);
static void(*T75OldEnd)(id,SEL);
static NSMutableDictionary*T75State(id e){NSString*k=[NSString stringWithFormat:@"%p",e];NSMutableDictionary*d=T75States[k];if(!d){d=[@{@"textures":[NSMutableDictionary new],@"bytes":[NSMutableDictionary new],@"buffers":[NSMutableDictionary new]}mutableCopy];T75States[k]=d;}return d;}
static NSDictionary*T75Tex(id<MTLTexture>t){return t?@{@"class":NSStringFromClass(object_getClass(t)),@"width":@(t.width),@"height":@(t.height),@"pixelFormat":@(t.pixelFormat),@"textureType":@(t.textureType),@"storageMode":@(t.storageMode),@"label":t.label?:@""}:@{@"nil":@YES};}
static void T75PSO(id e,SEL s,id<MTLComputePipelineState>p){@synchronized(T75Lock){if(T75Active){T75State(e)[@"PSO"]=p?@{@"class":NSStringFromClass(object_getClass(p)),@"label":p.label?:@"unlabelled",@"threadExecutionWidth":@(p.threadExecutionWidth),@"maxTotalThreads":@(p.maxTotalThreadsPerThreadgroup)}:@{@"nil":@YES};}}T75OldPSO(e,s,p);}
static void T75Texture(id e,SEL s,id<MTLTexture>t,NSUInteger i){@synchronized(T75Lock){if(T75Active){NSMutableDictionary*d=T75State(e)[@"textures"];if(t)d[@(i).stringValue]=T75Tex(t);else[d removeObjectForKey:@(i).stringValue];}}T75OldTexture(e,s,t,i);}
static void T75Bytes(id e,SEL s,const void*p,NSUInteger n,NSUInteger i){@synchronized(T75Lock){if(T75Active){T75State(e)[@"bytes"][@(i).stringValue]=@{@"length":@(n),@"sha256":n<65536?SHA75(p,n):@"not_hashed_over_limit"};[T75State(e)[@"buffers"]removeObjectForKey:@(i).stringValue];}}T75OldBytes(e,s,p,n,i);}
static void T75Buffer(id e,SEL s,id<MTLBuffer>b,NSUInteger off,NSUInteger i){@synchronized(T75Lock){if(T75Active){NSMutableDictionary*d=T75State(e)[@"buffers"];if(b)d[@(i).stringValue]=@{@"length":@(b.length),@"offset":@(off),@"storageMode":@(b.storageMode),@"label":b.label?:@""};else[d removeObjectForKey:@(i).stringValue];[T75State(e)[@"bytes"]removeObjectForKey:@(i).stringValue];}}T75OldBuffer(e,s,b,off,i);}
static void T75Record(id e,MTLSize g,MTLSize t,NSString*kind){@synchronized(T75Lock){if(!T75Active)return;if(T75Dispatches.count>=512){T75CaptureLimit=YES;return;}NSMutableDictionary*d=[T75State(e)mutableCopy];for(NSString*k in @[@"textures",@"bytes",@"buffers"])d[k]=[d[k]copy];d[@"grid"]=@[@(g.width),@(g.height),@(g.depth)];d[@"group"]=@[@(t.width),@(t.height),@(t.depth)];d[@"dispatch"]=kind;[T75Dispatches addObject:d];}}
static void T75Groups(id e,SEL s,MTLSize g,MTLSize t){T75Record(e,g,t,@"groups");T75OldGroups(e,s,g,t);}
static void T75Threads(id e,SEL s,MTLSize g,MTLSize t){T75Record(e,g,t,@"threads");T75OldThreads(e,s,g,t);}
static void T75End(id e,SEL s){T75OldEnd(e,s);@synchronized(T75Lock){[T75States removeObjectForKey:[NSString stringWithFormat:@"%p",e]];}}
static void T75Install(id<MTLDevice>dev){T75Lock=[NSObject new];T75States=[NSMutableDictionary new];T75Dispatches=[NSMutableArray new];id<MTLCommandQueue>q=[dev newCommandQueue];id<MTLCommandBuffer>b=[q commandBuffer];id<MTLComputeCommandEncoder>e=[b computeCommandEncoder];Class c=object_getClass(e);T75EncoderClass=NSStringFromClass(c);Method m;
 #define T75HOOK(n,o,f) m=class_getInstanceMethod(c,NSSelectorFromString(@n));Need(m!=NULL,@n);o=(void*)method_getImplementation(m);method_setImplementation(m,(IMP)f);
 T75HOOK("setComputePipelineState:",T75OldPSO,T75PSO)
 T75HOOK("setTexture:atIndex:",T75OldTexture,T75Texture)
 T75HOOK("setBytes:length:atIndex:",T75OldBytes,T75Bytes)
 T75HOOK("setBuffer:offset:atIndex:",T75OldBuffer,T75Buffer)
 T75HOOK("dispatchThreadgroups:threadsPerThreadgroup:",T75OldGroups,T75Groups)
 T75HOOK("dispatchThreads:threadsPerThreadgroup:",T75OldThreads,T75Threads)
 T75HOOK("endEncoding",T75OldEnd,T75End)
 #undef T75HOOK
 [e endEncoding];[b commit];[b waitUntilCompleted];Need(b.error==nil,@"independent preflight encoder completion");
}
