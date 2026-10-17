// Capture argument bindings in this isolated research process, while renderer process runs.
static NSMutableDictionary *ECStates;
static NSMutableArray *ECDispatches;
static BOOL ECActive;
static void (*ECPipeline)(id,SEL,id);
static void (*ECTexture)(id,SEL,id,NSUInteger);
static void (*ECBytes)(id,SEL,const void *,NSUInteger,NSUInteger);
static void (*ECBuffer)(id,SEL,id,NSUInteger,NSUInteger);
static void (*ECThreadgroups)(id,SEL,MTLSize,MTLSize);
static void (*ECThreads)(id,SEL,MTLSize,MTLSize);
static void (*ECImageblock)(id,SEL,NSUInteger,NSUInteger);
static void (*ECThreadMemory)(id,SEL,NSUInteger,NSUInteger);
static NSMutableDictionary *ECState(id self){NSString *k=[NSString stringWithFormat:@"%p",self];NSMutableDictionary *d=ECStates[k];if(!d){d=[@{@"textures":[NSMutableDictionary new],@"bytes":[NSMutableDictionary new],@"buffers":[NSMutableDictionary new]} mutableCopy];ECStates[k]=d;}return d;}
static void ECSetPipeline(id self,SEL cmd,id p){if(ECActive){ECState(self)[@"pipeline"]=[(id<MTLComputePipelineState>)p label]?:@"unlabelled";ECState(self)[@"pipeline_object"]=p;}ECPipeline(self,cmd,p);}
static void ECSetTexture(id self,SEL cmd,id t,NSUInteger index){if(ECActive){NSMutableDictionary *d=ECState(self)[@"textures"];if(t)d[@(index).stringValue]=t;else[d removeObjectForKey:@(index).stringValue];}ECTexture(self,cmd,t,index);}
static void ECSetBytes(id self,SEL cmd,const void *bytes,NSUInteger length,NSUInteger index){if(ECActive && length<65536){ECState(self)[@"bytes"][@(index).stringValue]=[NSData dataWithBytes:bytes length:length];[ECState(self)[@"buffers"]removeObjectForKey:@(index).stringValue];}ECBytes(self,cmd,bytes,length,index);}
static void ECSetBuffer(id self,SEL cmd,id b,NSUInteger offset,NSUInteger index){if(ECActive){NSMutableDictionary *d=ECState(self)[@"buffers"];if(b)d[@(index).stringValue]=@{@"buffer":b,@"offset":@(offset)};else[d removeObjectForKey:@(index).stringValue];[ECState(self)[@"bytes"]removeObjectForKey:@(index).stringValue];}ECBuffer(self,cmd,b,offset,index);}
static void ECRecord(id self,MTLSize grid,MTLSize group,NSString *kind){if(!ECActive)return;NSMutableDictionary *d=[ECState(self) mutableCopy];d[@"textures"]=[d[@"textures"] copy];d[@"bytes"]=[d[@"bytes"] copy];d[@"buffers"]=[d[@"buffers"] copy];d[@"grid"]=@[@(grid.width),@(grid.height),@(grid.depth)];d[@"group"]=@[@(group.width),@(group.height),@(group.depth)];d[@"dispatch"]=kind;[ECDispatches addObject:d];}
static void ECDispatchGroups(id self,SEL cmd,MTLSize grid,MTLSize group){ECRecord(self,grid,group,@"groups");ECThreadgroups(self,cmd,grid,group);}
static void ECDispatchThreads(id self,SEL cmd,MTLSize grid,MTLSize group){ECRecord(self,grid,group,@"threads");ECThreads(self,cmd,grid,group);}
static void ECSetImageblock(id self,SEL cmd,NSUInteger w,NSUInteger h){if(ECActive)ECState(self)[@"imageblock"]=@[@(w),@(h)];ECImageblock(self,cmd,w,h);}
static void ECSetThreadMemory(id self,SEL cmd,NSUInteger n,NSUInteger index){if(ECActive){NSMutableDictionary*d=ECState(self)[@"threadgroup_memory"];if(!d){d=[NSMutableDictionary new];ECState(self)[@"threadgroup_memory"]=d;}d[@(index).stringValue]=@(n);}ECThreadMemory(self,cmd,n,index);}
static void ECInstall(void){
 id<MTLCommandQueue> q=[MTLCreateSystemDefaultDevice() newCommandQueue];id<MTLCommandBuffer> b=[q commandBuffer];id<MTLComputeCommandEncoder> e=[b computeCommandEncoder];Class c=object_getClass(e);Method m;
 #define ECHOOK(name,original,replacement) m=class_getInstanceMethod(c,NSSelectorFromString(@name));if(m){original=(void *)method_getImplementation(m);method_setImplementation(m,(IMP)replacement);}
 ECHOOK("setComputePipelineState:",ECPipeline,ECSetPipeline)
 ECHOOK("setTexture:atIndex:",ECTexture,ECSetTexture)
 ECHOOK("setBytes:length:atIndex:",ECBytes,ECSetBytes)
 ECHOOK("setBuffer:offset:atIndex:",ECBuffer,ECSetBuffer)
 ECHOOK("dispatchThreadgroups:threadsPerThreadgroup:",ECThreadgroups,ECDispatchGroups)
 ECHOOK("dispatchThreads:threadsPerThreadgroup:",ECThreads,ECDispatchThreads)
 ECHOOK("setImageblockWidth:height:",ECImageblock,ECSetImageblock)
 ECHOOK("setThreadgroupMemoryLength:atIndex:",ECThreadMemory,ECSetThreadMemory)
 #undef ECHOOK
 [e endEncoding];[b commit];[b waitUntilCompleted];
}
static void ECWrite(NSString *dir,NSDictionary *textures){
 NSMutableArray *items=[NSMutableArray new];NSUInteger serial=0;
 for(NSDictionary *call in ECDispatches){NSMutableDictionary *d=[call mutableCopy],*tex=[NSMutableDictionary new],*bytes=[NSMutableDictionary new],*buffers=[NSMutableDictionary new];
  for(NSString *key in call[@"textures"]){id<MTLTexture> t=call[@"textures"][key];NSString *name=nil;for(NSString *n in textures)if(textures[n]==t){name=n;break;}tex[key]=@{@"ivar":name?:@"unmatched",@"label":[t label]?:@"",@"width":@([t width]),@"height":@([t height]),@"pixel_format":@([t pixelFormat])};}
  for(NSString *key in call[@"bytes"]){NSString *file=[NSString stringWithFormat:@"dispatch-%lu-bytes-%@.bin",(unsigned long)serial,key];[call[@"bytes"][key] writeToFile:[dir stringByAppendingPathComponent:file] atomically:YES];bytes[key]=file;}
  for(NSString *key in call[@"buffers"]){NSDictionary *binding=call[@"buffers"][key];id<MTLBuffer> b=binding[@"buffer"];buffers[key]=@{@"length":@(b.length),@"offset":binding[@"offset"],@"label":b.label?:@""};}
  [d removeObjectForKey:@"pipeline_object"];d[@"textures"]=tex;d[@"bytes"]=bytes;d[@"buffers"]=buffers;[items addObject:d];serial++;
 }
 [[NSJSONSerialization dataWithJSONObject:items options:NSJSONWritingPrettyPrinted|NSJSONWritingSortedKeys error:NULL]writeToFile:[dir stringByAppendingPathComponent:@"dispatches.json"] atomically:YES];
}
