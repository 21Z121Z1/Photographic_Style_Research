#define main RuntimePreflightMain
#include "semantic_runtime_s1.m"
#undef main
#import <CoreMedia/CoreMedia.h>
@interface NSObject (SemanticS2)
+(NSArray*)inputNames;
+(id)allowedEffectTypesForUsage:(NSUInteger)u;
+(id)inputRequirementsForUsage:(NSUInteger)u;
+(id)inputConfigurationForEffectType:(NSUInteger)t isVideo:(BOOL)v;
+(id)semanticStylePropertiesFromData:(NSData*)data fromVideo:(BOOL)video keyTime:(CMTime)t error:(NSError**)e;
+(id)textureStylePropertiesFromImageMetadata:(NSData*)data auxImageMetadata:(NSDictionary*)aux error:(NSError**)e;
+(id)personInputDataFromStillProperties:(id)p;
+(id)descriptorForEffectName:(NSString*)name tuningDictionary:(NSDictionary*)d semanticStyleProperties:(id)p semanticStyleInfo:(id)i;
@end
static void SaveJSON(id v,NSString*p){[[NSJSONSerialization dataWithJSONObject:v options:NSJSONWritingPrettyPrinted|NSJSONWritingSortedKeys error:NULL]writeToFile:p atomically:YES];}
static NSDictionary* Dump(CIImage*i,CIContext*c,CGColorSpaceRef cs,NSString*p){
 if(!i)return @{@"nil":@YES};CGRect r=i.extent;NSUInteger w=lround(r.size.width),h=lround(r.size.height);
 if(!w||!h||w*h>2000000)@throw[NSException exceptionWithName:@"size"reason:NSStringFromRect(NSRectFromCGRect(r))userInfo:nil];
 NSMutableData*d=[NSMutableData dataWithLength:w*h*16];[c render:i toBitmap:d.mutableBytes rowBytes:w*16 bounds:r format:kCIFormatRGBAf colorSpace:cs];[d writeToFile:p atomically:YES];
 NSDictionary*m=@{@"shape":@[@(h),@(w),@4],@"dtype":@"<f4",@"space":@"extended linear Display P3",@"coded_orientation":@YES};SaveJSON(m,[p stringByAppendingString:@".json"]);return m;
}
static CIImage* ReadImage(NSString*p,BOOL unmanaged){NSMutableDictionary*d=[@{kCIImageApplyOrientationProperty:@NO,kCIImageExpandToHDR:@NO}mutableCopy];if(unmanaged)d[kCIImageColorSpace]=NSNull.null;return[CIImage imageWithContentsOfURL:[NSURL fileURLWithPath:p]options:d];}
static CIImage* Scale(CIImage*i,CGRect r){return[[i imageByApplyingTransform:CGAffineTransformMakeScale(r.size.width/i.extent.size.width,r.size.height/i.extent.size.height)]imageByCroppingToRect:r];}
static void DumpMask(CIImage*i,CIContext*c,NSString*p){CGRect r=i.extent;NSUInteger w=lround(r.size.width),h=lround(r.size.height);NSMutableData*d=[NSMutableData dataWithLength:w*h*2];[c render:i toBitmap:d.mutableBytes rowBytes:w*2 bounds:r format:kCIFormatRh colorSpace:NULL];[d writeToFile:p atomically:YES];SaveJSON(@{@"shape":@[@(h),@(w)],@"dtype":@"<f2",@"space":@"unmanaged matte",@"sampling":@"CI affine scale then native half capture"},[p stringByAppendingString:@".json"]);}
static NSData* Bitmap(CIImage*i,CIContext*c,CGColorSpaceRef cs){CGRect r=i.extent;NSUInteger w=lround(r.size.width),h=lround(r.size.height);NSMutableData*d=[NSMutableData dataWithLength:w*h*16];[c render:i toBitmap:d.mutableBytes rowBytes:w*16 bounds:r format:kCIFormatRGBAf colorSpace:cs];return d;}
static BOOL NoResidency(id self,SEL cmd){return NO;}
int main(int argc,char**argv){@autoreleasepool{
 if(argc!=4)return 2;NSString*res=@(argv[1]),*out=@(argv[2]),*photo=@(argv[3]);[[NSFileManager defaultManager]createDirectoryAtPath:out withIntermediateDirectories:YES attributes:nil error:NULL];
 NSMutableDictionary*f=[@{@"os":NSProcessInfo.processInfo.operatingSystemVersionString,@"scope":@"Controlled CI processor interventions on a decoded real image. Not the complete Photos graph, not a proven inverse of original camera texture processing."}mutableCopy];
 for(NSString*n in @[@"NeutrinoCore",@"PhotoImaging",@"CMImaging"])dlopen([[NSString stringWithFormat:@"/System/Library/PrivateFrameworks/%@.framework/%@",n,n]UTF8String],RTLD_NOW|RTLD_LOCAL);
 Method m=class_getInstanceMethod(NSClassFromString(@"NUAssertionPolicyAbort"),NSSelectorFromString(@"notifyAssertion:"));if(m)method_setImplementation(m,(IMP)AssertionToException);
 m=class_getClassMethod(NSClassFromString(@"CMIMetalResourceCache"),NSSelectorFromString(@"_enableResidencySets"));if(m)method_setImplementation(m,(IMP)NoResidency);
 @try{
  NSError*e=nil;NSData*data=[NSData dataWithContentsOfFile:[res stringByAppendingPathComponent:@"styles.plist"]];id semantic=[NSClassFromString(@"_NUSemanticStyleProperties")semanticStylePropertiesFromData:data fromVideo:NO keyTime:kCMTimeInvalid error:&e];
  data=[NSData dataWithContentsOfFile:[res stringByAppendingPathComponent:@"texture_styles.plist"]];id texture=[NSClassFromString(@"_NUTextureStyleProperties")textureStylePropertiesFromImageMetadata:data auxImageMetadata:@{} error:&e];
  f[@"texture_properties"]=Safe(texture,0);f[@"texture_parse_error"]=e.description?:@"none";f[@"person_input_data"]=Safe([NSClassFromString(@"PITextureStyleProcessorKernel")personInputDataFromStillProperties:texture],0);
  Class pipe=NSClassFromString(@"PITextureStylePipelineProcessor");NSMutableArray*usages=[NSMutableArray new];
  for(NSUInteger u=0;u<8;u++)[usages addObject:@{@"usage":@(u),@"allowed_types":Safe([pipe allowedEffectTypesForUsage:u],0),@"requirements":Safe([pipe inputRequirementsForUsage:u],0)}];f[@"usage_requirements"]=usages;
  NSMutableDictionary*requirements=[NSMutableDictionary new];for(NSUInteger t=1;t<=3;t++)requirements[[@(t)stringValue]]=Safe([pipe inputConfigurationForEffectType:t isVideo:NO],0);f[@"effect_requirements"]=requirements;SaveJSON(f,[out stringByAppendingPathComponent:@"checkpoint.json"]);
  NSDictionary*t=[NSDictionary dictionaryWithContentsOfFile:@"/System/Library/PrivateFrameworks/CMImaging.framework/Resources/TextureStyleTuning.plist"];
  NSDictionary*selected=t[@"iPhone19,2"][@"PortTypeBack"][@"Still"][@"Studio"][@"Common"];if(!selected)@throw[NSException exceptionWithName:@"tuning"reason:@"Exact hardware/port/mode tuning missing"userInfo:nil];f[@"selected_tuning"]=selected;
  id<MTLDevice>dev=MTLCreateSystemDefaultDevice();NSError*le=nil;id<MTLLibrary>lib=[dev newLibraryWithFile:@"/System/Library/PrivateFrameworks/CMImaging.framework/Resources/default.metallib"error:&le];f[@"library_function_names"]=lib.functionNames?:@[];
  CGColorSpaceRef cs=CGColorSpaceCreateWithName(kCGColorSpaceExtendedLinearDisplayP3);
  CIContext*ctx=[CIContext contextWithMTLDevice:dev options:@{kCIContextWorkingColorSpace:(__bridge id)cs,kCIContextWorkingFormat:@(kCIFormatRGBAh)}];
  CGRect r=CGRectMake(0,0,512,384);CIImage*image=Scale(ReadImage(photo,NO),r);
  NSData*linear=[NSData dataWithContentsOfFile:[res stringByAppendingPathComponent:@"thumbnail/native_linear.f32"]];
  CIImage*thumb=[CIImage imageWithBitmapData:linear bytesPerRow:1024*16 size:CGSizeMake(1024,768)format:kCIFormatRGBAf colorSpace:cs];thumb=Scale(thumb,r);
  f[@"input"]=Dump(image,ctx,cs,[out stringByAppendingPathComponent:@"input.f32"]);
  NSArray*names=[NSClassFromString(@"PITextureStylePipelineProcessor")inputNames];NSMutableArray*inputs=[NSMutableArray arrayWithObjects:image,thumb,nil],*extents=[NSMutableArray arrayWithObjects:[CIVector vectorWithCGRect:r],[CIVector vectorWithCGRect:r],nil],*missing=[NSMutableArray new];
  CIImage*zero=[[CIImage imageWithColor:[CIColor colorWithRed:0 green:0 blue:0 alpha:1]]imageByCroppingToRect:r];
  for(NSString*n in names){CIImage*i=ReadImage([res stringByAppendingPathComponent:[n stringByAppendingString:@".heic"]],YES);if(!i){[missing addObject:n];i=zero;}else i=Scale(i,r);[inputs addObject:i];[extents addObject:[CIVector vectorWithCGRect:r]];
   DumpMask(i,ctx,[out stringByAppendingPathComponent:[n stringByAppendingString:@"-mask.f16"]]);}
  f[@"missing_masks_zero_filled_for_diagnostic_only"]=missing;f[@"input_order"]=names;f[@"input_count"]=@(inputs.count);
  NSMutableArray*trials=[NSMutableArray new];Class kernel=NSClassFromString(@"PITextureStyleProcessorKernel");
  for(NSString*effect in @[@"UnderEyeBrightening",@"SkinSmoothingStandalone",@"Mattify"]){@try{
    id desc=[kernel descriptorForEffectName:effect tuningDictionary:selected semanticStyleProperties:semantic semanticStyleInfo:@{@"cast":@"Standard",@"color":@0}];
    NSDictionary*args=@{@"usage":@0,@"intensity":@0.87999999523162842,@"grainIntensity":@0,@"textureStyleProperties":texture,@"semanticStyleProperties":semantic,@"isVideo":@NO,@"effectDescriptors":@[desc],@"extents":extents};
    f[@"current_effect"]=effect;f[@"current_descriptor"]=Safe(desc,0);SaveJSON(f,[out stringByAppendingPathComponent:@"before-render.json"]);
    NSError*err=nil;CIImage*o=[(Class)kernel applyWithExtent:r inputs:inputs arguments:args error:&err];
    NSMutableDictionary*q=[@{@"effect":effect,@"descriptor":Safe(desc,0),@"error":err.description?:@"none"}mutableCopy];
    q[@"output"]=Dump(o,ctx,cs,[out stringByAppendingPathComponent:[effect stringByAppendingString:@".f32"]]);
    if(o){
     NSData*target=Bitmap(image,ctx,cs),*observed=Bitmap(o,ctx,cs);const float*a=target.bytes,*b=observed.bytes;NSUInteger count=target.length/4,changed=0;
     for(NSUInteger k=0;k<count;k++)if(k%4<3&&a[k]!=b[k])changed++;
     q[@"forward_changed_components"]=@(changed);
     // Residual iteration in the selected native forward context. This is a
     // candidate root, never a proof of the camera's original pre-image.
     if(changed){
      NSMutableData*guess=[target mutableCopy];NSMutableArray*history=[NSMutableArray new];CIImage*x=image,*y=o;
      for(NSUInteger iteration=0;iteration<10;iteration++){
       float*g=guess.mutableBytes;const float*t=target.bytes,*v=observed.bytes;double maxAbs=0,maxRel=0,squared=0;NSUInteger valid=0;
       for(NSUInteger k=0;k<count;k++)if(k%4<3){double d=(double)t[k]-v[k];maxAbs=fmax(maxAbs,fabs(d));squared+=d*d;if(t[k]>1./255&&isfinite(v[k])){maxRel=fmax(maxRel,fabs(d)/t[k]);valid++;}g[k]+=(float)d;}
       [history addObject:@{@"iteration":@(iteration),@"max_abs":@(maxAbs),@"max_relative_above_1_over_255":@(maxRel),@"mse":@(squared/(count/4*3)),@"valid_components":@(valid)}];
       if(maxRel<=1e-3&&maxAbs<=1e-5)break;
       x=[CIImage imageWithBitmapData:[guess copy]bytesPerRow:512*16 size:CGSizeMake(512,384)format:kCIFormatRGBAf colorSpace:cs];NSMutableArray*trialInputs=[inputs mutableCopy];trialInputs[0]=x;
       y=[(Class)kernel applyWithExtent:r inputs:trialInputs arguments:args error:NULL];observed=Bitmap(y,ctx,cs);
      }
      q[@"candidate_inverse_history"]=history;q[@"candidate_inverse_scope"]=@"Fixed original thumbnail, mattes, metadata, tuning. Residual-only candidate; no uniqueness or camera equivalence asserted.";
      q[@"candidate_inverse"]=Dump(x,ctx,cs,[out stringByAppendingPathComponent:[effect stringByAppendingString:@"-inverse.f32"]]);q[@"candidate_roundtrip"]=Dump(y,ctx,cs,[out stringByAppendingPathComponent:[effect stringByAppendingString:@"-roundtrip.f32"]]);
     }else q[@"inverse_status"]=@"identity forward in available context; original camera texture undo is untested";
    }
    [trials addObject:q];
   }@catch(NSException*x){[trials addObject:@{@"effect":effect,@"exception":x.description}];}f[@"trials"]=trials;SaveJSON(f,[out stringByAppendingPathComponent:@"texture-results.json"]);
  }
  CGColorSpaceRelease(cs);
 }@catch(NSException*x){f[@"exception"]=x.description;}
 SaveJSON(f,[out stringByAppendingPathComponent:@"texture-results.json"]);return 0;
}}
