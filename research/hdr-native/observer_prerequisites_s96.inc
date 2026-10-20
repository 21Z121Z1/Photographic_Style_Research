// Resource prerequisite + read-only ownership/status observation. No pixel math.
#import <ptrauth.h>
#import <pthread.h>
static NSMutableArray *PoolEvents96;
static NSMutableDictionary *Runtime96;
static void (*MemOriginal96)(id,SEL,NSUInteger);
static uintptr_t ExpectedMemCaller96;
static BOOL (*PIOriginal96)(id,SEL,NSArray*,NSDictionary*,id<CIImageProcessorOutput>,NSError*__autoreleasing*);
static int (*GuidedOriginal96)(id,SEL,id,id,id,id,NSUInteger,float);
static NSString *OwnerKey96=@"semanticS96.CI.owner";
static NSString *GuidedKey96=@"semanticS96.guided.calls";
static NSUInteger PISerial96;
static NSArray *Rect96(CGRect r){double v[]={r.origin.x,r.origin.y,r.size.width,r.size.height};NSMutableArray*a=[NSMutableArray new];for(int j=0;j<4;j++)[a addObject:isfinite(v[j])?@(v[j]):NSNull.null];return a;}
static NSDictionary *Tex96(id<MTLTexture>t){return t?@{@"width":@(t.width),@"height":@(t.height),@"format":@(t.pixelFormat)}:@{@"nil":@YES};}
static NSDictionary *Allocator96(id renderer){NSMutableDictionary*d=[NSMutableDictionary new];@try{Ivar i=class_getInstanceVariable(object_getClass(renderer),"_metalContext");if(!i)return @{@"context_ivar_missing":@YES};id c=object_getIvar(renderer,i),a=[c valueForKey:@"allocator"];d[@"context_class"]=c?NSStringFromClass(object_getClass(c)):@"nil";d[@"allocator_class"]=a?NSStringFromClass(object_getClass(a)):@"nil";for(NSString*k in @[@"memSize",@"allocatorType"]){@try{d[k]=[a valueForKey:k]?:NSNull.null;}@catch(NSException*e){d[k]=e.name;}}}@catch(NSException*e){d[@"observation_error"]=e.name;}return d;}
static void SetMem96(id object,SEL selector,NSUInteger requested){
 uintptr_t caller=(uintptr_t)ptrauth_strip(__builtin_return_address(0),ptrauth_key_return_address);
 BOOL matched=requested==150994944&&ExpectedMemCaller96!=0&&caller==ExpectedMemCaller96;
 NSUInteger effective=matched?536870912:requested;
 MemOriginal96(object,selector,effective);
 @synchronized(Calls94){if(PoolEvents96.count<128)[PoolEvents96 addObject:@{@"requested_bytes":@(requested),@"effective_bytes":@(effective),@"known_constructor_caller_matched":@(matched),@"only_capacity_argument_changed":@YES}];}
}
static BOOL PI96(id cls,SEL sel,NSArray*inputs,NSDictionary*args,id<CIImageProcessorOutput>output,NSError*__autoreleasing*error){
 NSMutableDictionary*td=[NSThread currentThread].threadDictionary;id previous=td[OwnerKey96];uint64_t tid=0;pthread_threadid_np(NULL,&tid);NSMutableDictionary*owner=[NSMutableDictionary new];
 @try{owner[@"output_region"]=Rect96(output.region);NSMutableArray*rs=[NSMutableArray new];for(id<CIImageProcessorInput>i in inputs)[rs addObject:Rect96(i.region)];owner[@"input_regions"]=rs;}@catch(NSException*e){owner[@"observation_error"]=e.name;}
 @synchronized(Calls94){owner[@"PI_callback_serial"]=@(PISerial96++);}owner[@"thread_id"]=@(tid);td[OwnerKey96]=owner;
 BOOL result=NO;@try{result=PIOriginal96(cls,sel,inputs,args,output,error);}@finally{if(previous)td[OwnerKey96]=previous;else[td removeObjectForKey:OwnerKey96];}return result;
}
static int Guided96(id s,SEL c,id cb,id input,id guide,id output,NSUInteger radius,float epsilon){
 NSMutableArray*events=[NSThread currentThread].threadDictionary[GuidedKey96];
 NSMutableDictionary*e=events?[@{@"radius":@(radius),@"epsilon":@(epsilon),@"input":Tex96(input),@"guide":Tex96(guide),@"output":Tex96(output)}mutableCopy]:nil;
 int rc=GuidedOriginal96(s,c,cb,input,guide,output,radius,epsilon);if(events){e[@"original_return"]=@(rc);[events addObject:e];}return rc;
}
static void InstallPrerequisites96(void){
 PoolEvents96=[NSMutableArray new];Runtime96=[NSMutableDictionary new];NSArray*images=Images94();Runtime96[@"loaded_images"]=images;
 BOOL uuid=NO;for(NSDictionary*d in images)if([d[@"path"]containsString:@"/CMImaging.framework/"])uuid=[d[@"loaded_UUID"]isEqualToString:@"3CCD434E-B1E0-3F14-8EF6-E29D58379BE8"];
 Class c=NSClassFromString(@"CMISmartStyleMetalRendererV1");Method init=class_getInstanceMethod(c,NSSelectorFromString(@"initWithMetalContext:"));Need94(init!=NULL,@"native designated initializer");
 ExpectedMemCaller96=uuid?(uintptr_t)ptrauth_strip(method_getImplementation(init),ptrauth_key_function_pointer)+0x12c:0;
 Runtime96[@"expected_CMI_UUID_matched"]=@(uuid);Runtime96[@"capacity_override_original_bytes"]=@150994944;Runtime96[@"capacity_override_new_bytes"]=@536870912;Runtime96[@"capacity_override_callsite_offset_from_initializer"]=@0x12c;Runtime96[@"new_capacity_not_previously_validated"]=@YES;
 Method m=class_getInstanceMethod(NSClassFromString(@"FigMetalAllocatorDescriptor"),NSSelectorFromString(@"setMemSize:"));Need94(m!=NULL,@"allocator descriptor size setter");NSMethodSignature*sig=[NSMethodSignature signatureWithObjCTypes:method_getTypeEncoding(m)];Need94(sig.numberOfArguments==3&&sig.methodReturnLength==0&&[sig getArgumentTypeAtIndex:2][0]==@encode(NSUInteger)[0],@"allocator size setter ABI");Runtime96[@"allocator_setter_ABI"]=@(method_getTypeEncoding(m));MemOriginal96=(void*)method_getImplementation(m);method_setImplementation(m,(IMP)SetMem96);
 m=class_getInstanceMethod(NSClassFromString(@"CMIGuidedFilter"),NSSelectorFromString(@"encodeToCommandBuffer:inputTexture:guideTexture:outputTexture:kernelRadius:epsilon:"));Need94(m!=NULL,@"original guided method");sig=[NSMethodSignature signatureWithObjCTypes:method_getTypeEncoding(m)];Need94(sig.numberOfArguments==8&&strchr("iI",sig.methodReturnType[0])&&[sig getArgumentTypeAtIndex:6][0]==@encode(NSUInteger)[0]&&[sig getArgumentTypeAtIndex:7][0]=='f',@"guided original ABI");Runtime96[@"guided_ABI"]=@(method_getTypeEncoding(m));GuidedOriginal96=(void*)method_getImplementation(m);method_setImplementation(m,(IMP)Guided96);
 m=class_getClassMethod(NSClassFromString(@"PISemanticStyleProcessor"),NSSelectorFromString(@"processWithInputs:arguments:output:error:"));Need94(m!=NULL,@"original PI processor method");sig=[NSMethodSignature signatureWithObjCTypes:method_getTypeEncoding(m)];Need94(sig.numberOfArguments==6&&sig.methodReturnLength==sizeof(BOOL),@"PI processor return ABI");for(NSUInteger k=2;k<=4;k++)Need94([sig getArgumentTypeAtIndex:k][0]=='@',@"PI object argument ABI");Need94([sig getArgumentTypeAtIndex:5][0]=='^',@"PI error pointer ABI");Runtime96[@"PI_processor_ABI"]=@(method_getTypeEncoding(m));PIOriginal96=(void*)method_getImplementation(m);method_setImplementation(m,(IMP)PI96);
}
