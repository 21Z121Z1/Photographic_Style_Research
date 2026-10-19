// S22: observational hooks. Original arguments/return objects are passed through.
// Internal objects stay in runner temporary storage; publication is whitelisted text.
#import <execinfo.h>
#import <Metal/Metal.h>
static NSMutableArray *S22Events;
static NSMutableDictionary *S22PipelineRecords, *S22Constants;
static NSMutableSet *S22LibraryClasses;
static BOOL S22Recording=YES;
static NSString*S22Ptr(id o){return [NSString stringWithFormat:@"%p",o];}
static NSArray*S22Stack(void){void*p[24];int n=backtrace(p,24);char**a=backtrace_symbols(p,n);NSMutableArray*r=[NSMutableArray new];for(int i=1;i<n;i++)[r addObject:@(a[i])];free(a);return r;}
static id S22Safe(id o,NSString*k){@try{return [o valueForKey:k]?:NSNull.null;}@catch(NSException*e){return @{@"unavailable":e.name};}}
static NSDictionary*S22Options(MTLCompileOptions*o){if(!o)return @{@"provided":@NO};NSMutableDictionary*d=[@{@"provided":@YES,@"class":NSStringFromClass(o.class)}mutableCopy];for(NSString*k in @[@"fastMathEnabled",@"mathMode",@"mathFloatingPointFunctions",@"languageVersion",@"optimizationLevel",@"preserveInvariance",@"compileSymbolVisibility",@"allowReferencingUndefinedSymbols",@"maxTotalThreadsPerThreadgroup",@"enableLogging"]){id v=S22Safe(o,k);if([v isKindOfClass:NSNumber.class]||[v isKindOfClass:NSDictionary.class])d[k]=v;}return d;}
static NSDictionary*S22Function(id<MTLFunction>fn){if(!fn)return @{};NSMutableDictionary*d=[@{@"name":fn.name?:@"",@"class":NSStringFromClass([(id)fn class]),@"type":@(fn.functionType)}mutableCopy];NSMutableArray*c=[NSMutableArray new];for(NSString*k in fn.functionConstantsDictionary){MTLFunctionConstant*v=fn.functionConstantsDictionary[k];[c addObject:@{@"name":v.name?:k,@"index":@(v.index),@"type":@(v.type),@"required":@(v.required)}];}d[@"function_constant_definitions"]=c;return d;}
static NSDictionary*S22Descriptor(MTLComputePipelineDescriptor*d){if(!d)return @{@"provided":@NO};NSMutableDictionary*r=[@{@"provided":@YES,@"function":S22Function(d.computeFunction),@"label":d.label?:@"",@"threadGroupSizeIsMultipleOfThreadExecutionWidth":@(d.threadGroupSizeIsMultipleOfThreadExecutionWidth),@"maxTotalThreadsPerThreadgroup":@(d.maxTotalThreadsPerThreadgroup),@"supportIndirectCommandBuffers":@(d.supportIndirectCommandBuffers),@"binary_archive_count":@(d.binaryArchives.count)}mutableCopy];NSMutableArray*b=[NSMutableArray new];for(NSUInteger i=0;i<31;i++)[b addObject:@(d.buffers[i].mutability)];r[@"buffers_mutability"]=b;for(NSString*k in @[@"shaderValidation",@"requiredThreadsPerThreadgroup"]){id v=S22Safe(d,k);if([v isKindOfClass:NSNumber.class]||[v isKindOfClass:NSDictionary.class])r[k]=v;else if(v!=NSNull.null)r[k]=[v description];}return r;}
static BOOL S22IsTarget(id<MTLFunction>f){return [f.name containsString:@"renderFinalAdjustments"];}
static void S22RecordPipeline(id<MTLComputePipelineState>ps,id<MTLFunction>fn,MTLComputePipelineDescriptor*d,NSUInteger options,NSString*api,id reflection,NSError*error){if(!S22Recording)return;NSMutableDictionary*r=[@{@"kind":@"pso_creation",@"api":api,@"returned_object":S22Ptr(ps),@"function":S22Function(fn?:d.computeFunction),@"options":@(options),@"descriptor":S22Descriptor(d),@"callstack":S22Stack(),@"error":error.description?:@"",@"target":@(S22IsTarget(fn?:d.computeFunction))}mutableCopy];if(ps){r[@"pipeline_object"]=ps;if(fn)r[@"function_object"]=fn;if(d)r[@"descriptor_object"]=[d copy];if(reflection)r[@"reflection_object"]=reflection;@synchronized(S22Events){S22PipelineRecords[S22Ptr(ps)]=r;[S22Events addObject:r];}}else @synchronized(S22Events){[S22Events addObject:r];}}
typedef id S22NewFn(id,SEL,id,NSError**) __attribute__((ns_returns_retained));
typedef id S22NewFnOpts(id,SEL,id,NSUInteger,id*,NSError**) __attribute__((ns_returns_retained));
static S22NewFn *S22OldFn;
static S22NewFnOpts *S22OldFnOpts,*S22OldDesc;
static id S22Fn(id s,SEL c,id f,NSError**e) __attribute__((ns_returns_retained));
static id S22Fn(id s,SEL c,id f,NSError**e){id p=S22OldFn(s,c,f,e);S22RecordPipeline(p,f,nil,0,NSStringFromSelector(c),nil,e?*e:nil);return p;}
static id S22FnOpts(id s,SEL c,id f,NSUInteger o,id*r,NSError**e) __attribute__((ns_returns_retained));
static id S22FnOpts(id s,SEL c,id f,NSUInteger o,id*r,NSError**e){id p=S22OldFnOpts(s,c,f,o,r,e);S22RecordPipeline(p,f,nil,o,NSStringFromSelector(c),r?*r:nil,e?*e:nil);return p;}
static id S22Desc(id s,SEL c,id d,NSUInteger o,id*r,NSError**e) __attribute__((ns_returns_retained));
static id S22Desc(id s,SEL c,id d,NSUInteger o,id*r,NSError**e){id p=S22OldDesc(s,c,d,o,r,e);S22RecordPipeline(p,nil,d,o,NSStringFromSelector(c),r?*r:nil,e?*e:nil);return p;}
static void(*S22OldAsyncFn)(id,SEL,id,void(^)(id,NSError*));
static void(*S22OldAsyncFnOpts)(id,SEL,id,NSUInteger,void(^)(id,id,NSError*));
static void(*S22OldAsyncDesc)(id,SEL,id,NSUInteger,void(^)(id,id,NSError*));
static void S22AsyncFn(id s,SEL c,id f,void(^h)(id,NSError*)){S22OldAsyncFn(s,c,f,^(id p,NSError*e){S22RecordPipeline(p,f,nil,0,NSStringFromSelector(c),nil,e);h(p,e);});}
static void S22AsyncFnOpts(id s,SEL c,id f,NSUInteger o,void(^h)(id,id,NSError*)){S22OldAsyncFnOpts(s,c,f,o,^(id p,id r,NSError*e){S22RecordPipeline(p,f,nil,o,NSStringFromSelector(c),r,e);h(p,r,e);});}
static void S22AsyncDesc(id s,SEL c,id d,NSUInteger o,void(^h)(id,id,NSError*)){S22OldAsyncDesc(s,c,d,o,^(id p,id r,NSError*e){S22RecordPipeline(p,nil,d,o,NSStringFromSelector(c),r,e);h(p,r,e);});}
static NSUInteger S22TypeBytes(MTLDataType t){switch(t){case MTLDataTypeBool:case MTLDataTypeChar:case MTLDataTypeUChar:return 1;case MTLDataTypeHalf:case MTLDataTypeShort:case MTLDataTypeUShort:return 2;case MTLDataTypeInt:case MTLDataTypeUInt:case MTLDataTypeFloat:return 4;case MTLDataTypeInt2:case MTLDataTypeUInt2:case MTLDataTypeFloat2:return 8;case MTLDataTypeInt3:case MTLDataTypeUInt3:case MTLDataTypeFloat3:case MTLDataTypeInt4:case MTLDataTypeUInt4:case MTLDataTypeFloat4:return 16;default:return 0;}}
static void(*S22OldConstant)(id,SEL,const void*,MTLDataType,NSUInteger);
static void(*S22OldConstantNamed)(id,SEL,const void*,MTLDataType,NSString*);
static void(*S22OldReset)(id,SEL);
static NSDictionary*S22Constant(const void*v,MTLDataType t){NSUInteger n=S22TypeBytes(t);return @{@"type":@(t),@"size":@(n),@"hex":n?[[NSData dataWithBytes:v length:n]description]:@"unrecorded-type"};}
static void S22SetConstant(id s,SEL c,const void*v,MTLDataType t,NSUInteger i){S22OldConstant(s,c,v,t,i);@synchronized(S22Constants){NSMutableDictionary*d=[S22Constants[S22Ptr(s)]mutableCopy]?:[NSMutableDictionary new];d[[@"index:"stringByAppendingString:@(i).stringValue]]=S22Constant(v,t);S22Constants[S22Ptr(s)]=d;}}
static void S22SetNamed(id s,SEL c,const void*v,MTLDataType t,NSString*n){S22OldConstantNamed(s,c,v,t,n);@synchronized(S22Constants){NSMutableDictionary*d=[S22Constants[S22Ptr(s)]mutableCopy]?:[NSMutableDictionary new];d[[@"name:"stringByAppendingString:n]]=S22Constant(v,t);S22Constants[S22Ptr(s)]=d;}}
static void S22Reset(id s,SEL c){S22OldReset(s,c);@synchronized(S22Constants){[S22Constants removeObjectForKey:S22Ptr(s)];}}
// Each library class has its own original IMP; calls on subclasses do not recurse.
static NSMutableDictionary*S22LibraryIMPs;
typedef id S22ConstFn(id,SEL,NSString*,MTLFunctionConstantValues*,NSError**) __attribute__((ns_returns_retained));
static id S22ConstFunction(id s,SEL c,NSString*n,MTLFunctionConstantValues*v,NSError**e) __attribute__((ns_returns_retained));
static id S22ConstFunction(id s,SEL c,NSString*n,MTLFunctionConstantValues*v,NSError**e){S22ConstFn*orig=(void*)[S22LibraryIMPs[NSStringFromClass([s class])]pointerValue];id f=orig(s,c,n,v,e);if(S22Recording){@synchronized(S22Events){[S22Events addObject:@{@"kind":@"function_specialization",@"name":n?:@"",@"returned_object":S22Ptr(f),@"constants":S22Constants[S22Ptr(v)]?:@{},@"error":e&&*e?[*e description]:@""}];}}return f;}
static void S22HookLibrary(id l){if(!l)return;Class c=object_getClass(l);NSString*k=NSStringFromClass(c);@synchronized(S22LibraryClasses){if([S22LibraryClasses containsObject:k])return;[S22LibraryClasses addObject:k];SEL s=@selector(newFunctionWithName:constantValues:error:);Method m=class_getInstanceMethod(c,s);if(m){IMP old=method_getImplementation(m);if(old!=(IMP)S22ConstFunction){S22LibraryIMPs[k]=[NSValue valueWithPointer:old];class_addMethod(c,s,old,method_getTypeEncoding(m));method_setImplementation(class_getInstanceMethod(c,s),(IMP)S22ConstFunction);}}}}
static S22NewFn*S22OldLibraryURL,*S22OldLibraryFile,*S22OldLibraryData;
typedef id S22NewSource(id,SEL,NSString*,MTLCompileOptions*,NSError**) __attribute__((ns_returns_retained));
static S22NewSource*S22OldLibrarySource;
static void S22LibraryEvent(id l,NSString*api,NSString*source,MTLCompileOptions*opts,NSError*error){S22HookLibrary(l);if(!S22Recording)return;@synchronized(S22Events){[S22Events addObject:@{@"kind":@"library_creation",@"api":api,@"source":source?:@"",@"returned_object":S22Ptr(l),@"compile_options":S22Options(opts),@"error":error.description?:@""}];}}
static id S22LibraryURL(id s,SEL c,id url,NSError**e) __attribute__((ns_returns_retained));
static id S22LibraryURL(id s,SEL c,id url,NSError**e){id l=S22OldLibraryURL(s,c,url,e);S22LibraryEvent(l,NSStringFromSelector(c),[url description],nil,e?*e:nil);return l;}
static id S22LibraryFile(id s,SEL c,id path,NSError**e) __attribute__((ns_returns_retained));
static id S22LibraryFile(id s,SEL c,id path,NSError**e){id l=S22OldLibraryFile(s,c,path,e);S22LibraryEvent(l,NSStringFromSelector(c),path,nil,e?*e:nil);return l;}
static id S22LibraryData(id s,SEL c,id data,NSError**e) __attribute__((ns_returns_retained));
static id S22LibraryData(id s,SEL c,id data,NSError**e){id l=S22OldLibraryData(s,c,data,e);S22LibraryEvent(l,NSStringFromSelector(c),@"dispatch_data_t (not persisted)",nil,e?*e:nil);return l;}
static id S22LibrarySource(id s,SEL c,NSString*text,MTLCompileOptions*o,NSError**e) __attribute__((ns_returns_retained));
static id S22LibrarySource(id s,SEL c,NSString*text,MTLCompileOptions*o,NSError**e){id l=S22OldLibrarySource(s,c,text,o,e);S22LibraryEvent(l,NSStringFromSelector(c),Digest([text dataUsingEncoding:NSUTF8StringEncoding]),o,e?*e:nil);return l;}
static NSDictionary*S22Sampler(MTLSamplerDescriptor*d){return @{@"normalizedCoordinates":@(d.normalizedCoordinates),@"minFilter":@(d.minFilter),@"magFilter":@(d.magFilter),@"mipFilter":@(d.mipFilter),@"sAddressMode":@(d.sAddressMode),@"tAddressMode":@(d.tAddressMode),@"rAddressMode":@(d.rAddressMode),@"maxAnisotropy":@(d.maxAnisotropy),@"compareFunction":@(d.compareFunction),@"lodMinClamp":@(d.lodMinClamp),@"lodMaxClamp":@(d.lodMaxClamp)};}
typedef id S22NewSampler(id,SEL,MTLSamplerDescriptor*) __attribute__((ns_returns_retained));
static S22NewSampler*S22OldSampler;
static NSMutableDictionary*S22Samplers;
static id S22SamplerNew(id s,SEL c,MTLSamplerDescriptor*d) __attribute__((ns_returns_retained));
static id S22SamplerNew(id s,SEL c,MTLSamplerDescriptor*d){id a=S22OldSampler(s,c,d);if(a)S22Samplers[S22Ptr(a)]=S22Sampler(d);return a;}
static void(*S22OldSetSampler)(id,SEL,id,NSUInteger);
static void S22SetSampler(id s,SEL c,id a,NSUInteger i){if(ECActive){NSMutableDictionary*d=[ECState(s)[@"samplers"]mutableCopy]?:[NSMutableDictionary new];d[@(i).stringValue]=a?(S22Samplers[S22Ptr(a)]?:@{@"descriptor_unobserved":@YES}):@{@"nil":@YES};ECState(s)[@"samplers"]=[d copy];}S22OldSetSampler(s,c,a,i);}
static NSDictionary*S22Install(void){S22Events=[NSMutableArray new];S22PipelineRecords=[NSMutableDictionary new];S22Constants=[NSMutableDictionary new];S22LibraryClasses=[NSMutableSet new];S22LibraryIMPs=[NSMutableDictionary new];S22Samplers=[NSMutableDictionary new];NSMutableArray*installed=[NSMutableArray new];id<MTLDevice>d=MTLCreateSystemDefaultDevice();Class c=object_getClass(d);Method m;
#define S22HOOK(n,o,r) m=class_getInstanceMethod(c,NSSelectorFromString(@n));if(m){o=(void*)method_getImplementation(m);method_setImplementation(m,(IMP)r);[installed addObject:@n];}
 S22HOOK("newComputePipelineStateWithFunction:error:",S22OldFn,S22Fn)
 S22HOOK("newComputePipelineStateWithFunction:options:reflection:error:",S22OldFnOpts,S22FnOpts)
 S22HOOK("newComputePipelineStateWithDescriptor:options:reflection:error:",S22OldDesc,S22Desc)
 S22HOOK("newComputePipelineStateWithFunction:completionHandler:",S22OldAsyncFn,S22AsyncFn)
 S22HOOK("newComputePipelineStateWithFunction:options:completionHandler:",S22OldAsyncFnOpts,S22AsyncFnOpts)
 S22HOOK("newComputePipelineStateWithDescriptor:options:completionHandler:",S22OldAsyncDesc,S22AsyncDesc)
 S22HOOK("newLibraryWithURL:error:",S22OldLibraryURL,S22LibraryURL)
 S22HOOK("newLibraryWithFile:error:",S22OldLibraryFile,S22LibraryFile)
 S22HOOK("newLibraryWithData:error:",S22OldLibraryData,S22LibraryData)
 S22HOOK("newLibraryWithSource:options:error:",S22OldLibrarySource,S22LibrarySource)
 S22HOOK("newSamplerStateWithDescriptor:",S22OldSampler,S22SamplerNew)
 c=object_getClass([MTLFunctionConstantValues new]);
 S22HOOK("setConstantValue:type:atIndex:",S22OldConstant,S22SetConstant)
 S22HOOK("setConstantValue:type:withName:",S22OldConstantNamed,S22SetNamed)
 S22HOOK("reset",S22OldReset,S22Reset)
 id<MTLCommandQueue>q=[d newCommandQueue];id<MTLCommandBuffer>b=[q commandBuffer];id<MTLComputeCommandEncoder>en=[b computeCommandEncoder];c=object_getClass(en);
 S22HOOK("setSamplerState:atIndex:",S22OldSetSampler,S22SetSampler)
#undef S22HOOK
 [en endEncoding];[b commit];[b waitUntilCompleted];return @{@"device_class":NSStringFromClass([(id)d class]),@"encoder_class":NSStringFromClass([(id)en class]),@"installed_selectors":installed};}
static NSArray*S22PublicEvents(void){NSMutableArray*a=[NSMutableArray new];for(NSDictionary*r in S22Events){NSMutableDictionary*d=[r mutableCopy];for(NSString*k in @[@"pipeline_object",@"function_object",@"descriptor_object",@"reflection_object"])[d removeObjectForKey:k];[a addObject:d];}return a;}
