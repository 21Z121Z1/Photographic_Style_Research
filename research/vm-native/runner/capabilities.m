#import <Foundation/Foundation.h>
#import <CoreImage/CoreImage.h>
#import <Metal/Metal.h>
#import <objc/runtime.h>
#import <dlfcn.h>
int main(int argc,char **argv){@autoreleasepool{
 NSMutableDictionary *d=[NSMutableDictionary new];
 id<MTLDevice> dev=MTLCreateSystemDefaultDevice();
 d[@"metal_device"]=dev.name ?: (id)NSNull.null;
 d[@"metal_devices"]=@([MTLCopyAllDevices() count]);
 d[@"os"]=NSProcessInfo.processInfo.operatingSystemVersionString;
 NSMutableDictionary *loads=[NSMutableDictionary new],*classes=[NSMutableDictionary new];
 for(NSString *f in @[@"CMImaging",@"NeutrinoCore",@"PhotoImaging"]){
  NSString *p=[NSString stringWithFormat:@"/System/Library/PrivateFrameworks/%@.framework/%@",f,f];
  void *h=dlopen(p.UTF8String,RTLD_NOW|RTLD_LOCAL);loads[f]=h?@"ok":@(dlerror());
 }
 for(NSString *n in @[@"_NUSemanticStyleProperties",@"NUStyleTransferReverseNode",@"_NUStyleEngine",@"_NUStyleTransferApplyProcessor",@"PISemanticStyleFilter",@"CMISmartStyleMetalRendererV1",@"CMIStyleEngineProcessor",@"CMIGuidedFilter",@"CIAppleLogToLinear"]){
  Class c=NSClassFromString(n);NSMutableArray *methods=[NSMutableArray new],*ivars=[NSMutableArray new];
  for(Class q=c;q && q!=NSObject.class;q=class_getSuperclass(q)){
   unsigned count=0;Method *ms=class_copyMethodList(q,&count);
   for(unsigned i=0;i<count;i++)[methods addObject:@{@"class":NSStringFromClass(q),@"selector":NSStringFromSelector(method_getName(ms[i])),@"encoding":@(method_getTypeEncoding(ms[i]))}];free(ms);
   Ivar *vs=class_copyIvarList(q,&count);for(unsigned i=0;i<count;i++)[ivars addObject:@{@"class":NSStringFromClass(q),@"name":@(ivar_getName(vs[i])),@"type":@(ivar_getTypeEncoding(vs[i])),@"offset":@(ivar_getOffset(vs[i]))}];free(vs);
  }
  classes[n]=@{@"found":@(c!=nil),@"methods":methods,@"ivars":ivars};
 }
 d[@"loads"]=loads;d[@"classes"]=classes;
 CIContext *cpu=[CIContext contextWithOptions:@{kCIContextUseSoftwareRenderer:@YES,kCIContextWorkingColorSpace:NSNull.null,kCIContextOutputColorSpace:NSNull.null}];
 float x[4]={.2f,.3f,.4f,1},y[4]={0};
 CIImage *im=[CIImage imageWithBitmapData:[NSData dataWithBytes:x length:16] bytesPerRow:16 size:CGSizeMake(1,1) format:kCIFormatRGBAf colorSpace:NULL];
 @try{[cpu render:im toBitmap:y rowBytes:16 bounds:im.extent format:kCIFormatRGBAf colorSpace:NULL];d[@"cpu_ci_identity"]=@[@(y[0]),@(y[1]),@(y[2]),@(y[3])];}@catch(NSException *e){d[@"cpu_ci_exception"]=e.description;}
 CIFilter *filter=[NSClassFromString(@"PISemanticStyleFilter") new];[filter setDefaults];
 NSMutableDictionary *defaults=[NSMutableDictionary new];for(NSString *key in filter.inputKeys){@try{id val=[filter valueForKey:key];defaults[key]=val?[val description]:@"nil";}@catch(NSException *e){defaults[key]=e.description;}}
 d[@"filter_defaults"]=defaults;d[@"filter_attributes"]=filter.attributes.description?:@"nil";
 if(argc>1)[[NSJSONSerialization dataWithJSONObject:d options:NSJSONWritingPrettyPrinted|NSJSONWritingSortedKeys error:NULL] writeToFile:@(argv[1]) atomically:YES];
 printf("metal=%s frameworks=%lu classes=%lu\n",dev.name.UTF8String?:"NONE",(unsigned long)loads.count,(unsigned long)classes.count);
 return 0;
}}
