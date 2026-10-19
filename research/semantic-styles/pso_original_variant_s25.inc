// Observe the original base-PSO initializer. No source compilation/capture mode changes.
#import <objc/message.h>
static NSMutableDictionary*S25Variants;
static id S25Meta(id x,int depth,NSMutableSet*seen,NSString*stem){
 if(!x)return NSNull.null;NSString*className=NSStringFromClass(object_getClass(x));NSMutableDictionary*r=[@{@"class":className?:@"",@"pointer":S22Ptr(x)}mutableCopy];
 if([x isKindOfClass:NSString.class]){r[@"text"]=[x length]<2048?x:@"text-too-long";return r;}
 if([x isKindOfClass:NSNumber.class]){r[@"number"]=x;return r;}
 if([x isKindOfClass:NSData.class]){NSData*d=x;r[@"length"]=@(d.length);r[@"sha256"]=Digest(d);if(d.length&&d.length<30_000_000){NSString*n=[NSString stringWithFormat:@"%@-%@.bin",stem,Digest(d)];NSString*b=[NSProcessInfo.processInfo.environment[@"W"]stringByAppendingPathComponent:@"backend"];[[NSFileManager defaultManager]createDirectoryAtPath:b withIntermediateDirectories:YES attributes:nil error:NULL];[d writeToFile:[b stringByAppendingPathComponent:n]atomically:YES];r[@"runner_only_code_candidate"]=n;}return r;}
 if(depth<=0||[seen containsObject:S22Ptr(x)])return r;[seen addObject:S22Ptr(x)];
 if([x isKindOfClass:NSDictionary.class]){NSMutableDictionary*d=[NSMutableDictionary new];for(id k in (NSDictionary*)x){NSString*key=[k isKindOfClass:NSString.class]?k:[k description];if(key.length>200)continue;d[key]=S25Meta(x[k],depth-1,seen,stem);}r[@"dictionary"]=d;return r;}
 if([x isKindOfClass:NSArray.class]){NSMutableArray*a=[NSMutableArray new];NSUInteger n=0;for(id y in (NSArray*)x){if(n++>=64)break;[a addObject:S25Meta(y,depth-1,seen,stem)];}r[@"array"]=a;return r;}
 NSMutableArray*ivs=[NSMutableArray new];for(Class c=object_getClass(x);c&&c!=NSObject.class;c=class_getSuperclass(c)){unsigned int n=0;Ivar*iv=class_copyIvarList(c,&n);for(unsigned int i=0;i<n;i++){const char*t=ivar_getTypeEncoding(iv[i]);NSString*name=@(ivar_getName(iv[i]));NSMutableDictionary*row=[@{@"name":name,@"type":t?@(t):@"",@"offset":@(ivar_getOffset(iv[i]))}mutableCopy];if(t&&t[0]=='@'){@try{id val=object_getIvar(x,iv[i]);if(val)row[@"object"]=S25Meta(val,depth-1,seen,stem);}@catch(NSException*e){row[@"read_exception"]=e.name;}}[ivs addObject:row];}free(iv);}r[@"ivars"]=ivs;return r;
}
typedef id S25InitType(__unsafe_unretained id,SEL,id,id,id,id*) __attribute__((ns_returns_retained));
static S25InitType*S25OldInit;
static id S25Init(__unsafe_unretained id s,SEL c,id device,id pd,id variant,id*error) __attribute__((ns_returns_retained));
static id S25Init(__unsafe_unretained id s,SEL c,id device,id pd,id variant,id*error){id result=S25OldInit(s,c,device,pd,variant,error);if(result){@synchronized(S25Variants){S25Variants[S22Ptr(result)]=@{@"pso_object":result,@"variant_object":variant?:NSNull.null,@"descriptor_object":pd?:NSNull.null,@"device_class":NSStringFromClass(object_getClass(device))};}}return result;}
static void S25Install(void){S25Variants=[NSMutableDictionary new];Class c=NSClassFromString(@"AppleParavirtComputePipelineState");Method m=class_getInstanceMethod(c,NSSelectorFromString(@"initWithDevice:pipelineStateDescriptor:computeVariant:errorMessage:"));if(!m)@throw[NSException exceptionWithName:@"S25Hook"reason:@"Known base PSO initializer absent"userInfo:nil];S25OldInit=(void*)method_getImplementation(m);method_setImplementation(m,(IMP)S25Init);}
#define Probe S25BaseProbe
#include "semantic_s22.inc"
#undef Probe
static void Probe(id renderer,NSDictionary*call){S25BaseProbe(renderer,call);id ps=call[@"pipeline_object"];NSDictionary*record=S25Variants[S22Ptr(ps)];NSMutableDictionary*r=[@{@"retained_pipeline_class":NSStringFromClass(object_getClass(ps)),@"original_initializer_record_matched":@(record!=nil),@"capture_environment":NSProcessInfo.processInfo.environment[@"MTL_CAPTURE_ENABLED"]?:@"unset",@"native_context_file":@"s22-results.json",@"scope":@"Actual original base-PSO constructor arguments. No guessed private getter, recompilation mode or operator parameter intervention. Raw code candidate bytes stay runner-only."}mutableCopy];
 if(record){r[@"variant"]=S25Meta(record[@"variant_object"],4,[NSMutableSet new],@"original-variant");r[@"descriptor"]=S25Meta(record[@"descriptor_object"],2,[NSMutableSet new],@"original-descriptor");}
 Put(r,[SOut stringByAppendingPathComponent:@"s25-original-variant.json"]);
}
