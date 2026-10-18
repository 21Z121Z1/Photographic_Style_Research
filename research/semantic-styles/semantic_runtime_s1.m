#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#import <CoreImage/CoreImage.h>
#import <objc/runtime.h>
#import <objc/message.h>
#import <dlfcn.h>

static id Safe(id value,int depth){
 if(!value)return NSNull.null;if(depth>6)return @"depth-limit";
 if([value isKindOfClass:NSData.class])return @{@"bytes":@([value length])};
 if([value isKindOfClass:NSString.class]||[value isKindOfClass:NSNumber.class]||value==NSNull.null)return value;
 if([value isKindOfClass:NSDictionary.class]){NSMutableDictionary*d=[NSMutableDictionary new];for(id k in value)d[[k description]]=Safe(value[k],depth+1);return d;}
 if([value isKindOfClass:NSArray.class]){NSMutableArray*a=[NSMutableArray new];for(id v in value)[a addObject:Safe(v,depth+1)];return a;}
 NSMutableDictionary*d=[@{@"class":NSStringFromClass([value class])}mutableCopy];unsigned n=0;objc_property_t*p=class_copyPropertyList([value class],&n);
 for(unsigned i=0;i<n;i++){@try{NSString*k=@(property_getName(p[i]));if([@[@"description",@"debugDescription",@"superclass",@"hash"]containsObject:k])continue;d[k]=Safe([value valueForKey:k],depth+1);}@catch(NSException*e){}}
 free(p);if(d.count==1)d[@"description"]=[value description]?:@"nil";return d;
}
static NSDictionary*ClassInfo(Class c){
 NSMutableDictionary*d=[@{@"class":NSStringFromClass(c),@"instance_size":@(class_getInstanceSize(c))}mutableCopy];NSMutableArray*a=[NSMutableArray new];unsigned n=0;Method*m=class_copyMethodList(c,&n);
 for(unsigned i=0;i<n;i++)[a addObject:@{@"selector":NSStringFromSelector(method_getName(m[i])),@"encoding":@(method_getTypeEncoding(m[i]))}];free(m);d[@"instance_methods"]=a;a=[NSMutableArray new];m=class_copyMethodList(object_getClass(c),&n);
 for(unsigned i=0;i<n;i++)[a addObject:@{@"selector":NSStringFromSelector(method_getName(m[i])),@"encoding":@(method_getTypeEncoding(m[i]))}];free(m);d[@"class_methods"]=a;a=[NSMutableArray new];Ivar*v=class_copyIvarList(c,&n);
 for(unsigned i=0;i<n;i++)[a addObject:@{@"name":@(ivar_getName(v[i])),@"encoding":@(ivar_getTypeEncoding(v[i])),@"offset":@(ivar_getOffset(v[i]))}];free(v);d[@"ivars"]=a;return d;
}
static void AssertionToException(id self,SEL sel,id assertion){@throw[NSException exceptionWithName:@"SemanticResearchAssertion"reason:[assertion description]userInfo:nil];}
static id ObjectCall(id target,NSString*selector,NSArray*args){
 SEL sel=NSSelectorFromString(selector);if(![target respondsToSelector:sel])return @{@"unavailable":selector};NSMethodSignature*s=[target methodSignatureForSelector:sel];
 if(s.numberOfArguments!=args.count+2||s.methodReturnType[0]!='@')return @{@"unsupported_signature":selector,@"return_type":@(s.methodReturnType),@"argument_count":@(s.numberOfArguments)};
 NSInvocation*i=[NSInvocation invocationWithMethodSignature:s];i.target=target;i.selector=sel;
 for(NSUInteger k=0;k<args.count;k++){const char*t=[s getArgumentTypeAtIndex:k+2];if(t[0]!='@')return @{@"unsupported_argument":@(t),@"selector":selector};id value=args[k]==NSNull.null?nil:args[k];[i setArgument:&value atIndex:k+2];}
 @try{[i invoke];__unsafe_unretained id result=nil;[i getReturnValue:&result];return Safe(result,0);}@catch(NSException*e){return @{@"exception":e.description,@"selector":selector};}
}
int main(int argc,char**argv){@autoreleasepool{
 if(argc!=2)return 2;NSString*out=@(argv[1]);[[NSFileManager defaultManager]createDirectoryAtPath:out withIntermediateDirectories:YES attributes:nil error:NULL];NSMutableDictionary*facts=[NSMutableDictionary new];
 for(NSString*name in @[@"NeutrinoCore",@"PhotoImaging",@"CMImaging"]){NSString*p=[NSString stringWithFormat:@"/System/Library/PrivateFrameworks/%@.framework/%@",name,name];void*h=dlopen(p.UTF8String,RTLD_NOW|RTLD_LOCAL);facts[name]=@{@"loaded":@(h!=NULL),@"error":h?@"":@(dlerror()?:"unknown")};}
 Method policy=class_getInstanceMethod(NSClassFromString(@"NUAssertionPolicyAbort"),NSSelectorFromString(@"notifyAssertion:"));if(policy)method_setImplementation(policy,(IMP)AssertionToException);
 id<MTLDevice>device=MTLCreateSystemDefaultDevice();facts[@"host"]=@{@"os":NSProcessInfo.processInfo.operatingSystemVersionString,@"metal":@(device!=nil),@"device":device.name?:@"nil",@"input_photographs":@0,@"scope":@"No photograph, matte pixels, key1 coefficients, or secret is present in this public preflight"};
 NSMutableArray*classes=[NSMutableArray new];unsigned n=0;Class*list=objc_copyClassList(&n);
 for(unsigned k=0;k<n;k++){NSString*name=NSStringFromClass(list[k]);if([name hasPrefix:@"CMITextureStyle"]||[name hasPrefix:@"PITextureStyle"]||[name hasPrefix:@"_NUTextureStyle"]||[name isEqual:@"CMISmartStyleMetalRendererV1"])[classes addObject:ClassInfo(list[k])];}free(list);facts[@"classes"]=classes;
 NSMutableDictionary*defaults=[NSMutableDictionary new];for(NSString*preset in @[@"Studio",@"Standard",@"Natural",@"None"]){NSMutableDictionary*d=[NSMutableDictionary new];d[@"effect_order"]=ObjectCall(NSClassFromString(@"PITextureStyleProcessorKernel"),@"defaultEffectOrderForPreset:",@[preset]);d[@"default_dictionary"]=ObjectCall(NSClassFromString(@"PITextureStylePipelineProcessor"),@"defaultTextureStyleDictionaryForPreset:",@[preset]);defaults[preset]=d;}facts[@"preset_defaults"]=defaults;
 facts[@"input_names"]=ObjectCall(NSClassFromString(@"PITextureStylePipelineProcessor"),@"inputNames",@[]);
 NSMutableDictionary*parameters=[NSMutableDictionary new];for(NSString*name in @[@"CMITextureStylesSkinSmoothParameters",@"CMITextureStylesUnderEyeBrightenParameters",@"CMITextureStylesMattifyParameters"]){Class c=NSClassFromString(name);if(!c)continue;@try{parameters[name]=Safe([c new],0);}@catch(NSException*e){parameters[name]=@{@"exception":e.description};}}facts[@"parameter_defaults"]=parameters;
 NSData*json=[NSJSONSerialization dataWithJSONObject:facts options:NSJSONWritingPrettyPrinted|NSJSONWritingSortedKeys error:NULL];if(!json)return 3;[json writeToFile:[out stringByAppendingPathComponent:@"runtime.json"]atomically:YES];return 0;
}}
