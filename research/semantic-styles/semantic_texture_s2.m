#define main RuntimePreflightMain
#include "semantic_runtime_s1.m"
#undef main
#import <CoreMedia/CoreMedia.h>
@interface NSObject (SemanticS2)
+(NSArray*)inputNames;
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
  f[@"texture_properties"]=Safe(texture,0);f[@"texture_parse_error"]=e.description?:@"none";f[@"person_input_data"]=Safe([NSClassFromString(@"PITextureStyleProcessorKernel")personInputDataFromStillProperties:texture],0);SaveJSON(f,[out stringByAppendingPathComponent:@"checkpoint.json"]);
  NSDictionary*t=[NSDictionary dictionaryWithContentsOfFile:@"/System/Library/PrivateFrameworks/CMImaging.framework/Resources/TextureStyleTuning.plist"];
  NSDictionary*selected=t[@"iPhone19,2"][@"PortTypeBack"][@"Still"][@"Studio"][@"Common"];if(!selected)@throw[NSException exceptionWithName:@"tuning"reason:@"Exact hardware/port/mode tuning missing"userInfo:nil];f[@"selected_tuning"]=selected;
  id<MTLDevice>dev=MTLCreateSystemDefaultDevice();CGColorSpaceRef cs=CGColorSpaceCreateWithName(kCGColorSpaceExtendedLinearDisplayP3);
  CIContext*ctx=[CIContext contextWithMTLDevice:dev options:@{kCIContextWorkingColorSpace:(__bridge id)cs,kCIContextWorkingFormat:@(kCIFormatRGBAh)}];
  CGRect r=CGRectMake(0,0,512,384);CIImage*image=Scale(ReadImage(photo,NO),r);
  NSData*linear=[NSData dataWithContentsOfFile:[res stringByAppendingPathComponent:@"thumbnail/native_linear.f32"]];
  CIImage*thumb=[CIImage imageWithBitmapData:linear bytesPerRow:1024*16 size:CGSizeMake(1024,768)format:kCIFormatRGBAf colorSpace:cs];thumb=Scale(thumb,r);
  f[@"input"]=Dump(image,ctx,cs,[out stringByAppendingPathComponent:@"input.f32"]);
  NSArray*names=[NSClassFromString(@"PITextureStylePipelineProcessor")inputNames];NSMutableArray*inputs=[NSMutableArray arrayWithObjects:image,thumb,nil],*extents=[NSMutableArray arrayWithObjects:[NSValue valueWithRect:NSRectFromCGRect(r)],[NSValue valueWithRect:NSRectFromCGRect(r)],nil],*missing=[NSMutableArray new];
  CIImage*zero=[[CIImage imageWithColor:[CIColor colorWithRed:0 green:0 blue:0 alpha:1]]imageByCroppingToRect:r];
  for(NSString*n in names){CIImage*i=ReadImage([res stringByAppendingPathComponent:[n stringByAppendingString:@".heic"]],YES);if(!i){[missing addObject:n];i=zero;}else i=Scale(i,r);[inputs addObject:i];[extents addObject:[NSValue valueWithRect:NSRectFromCGRect(r)]];}
  f[@"missing_masks_zero_filled_for_diagnostic_only"]=missing;f[@"input_order"]=names;f[@"input_count"]=@(inputs.count);
  NSMutableArray*trials=[NSMutableArray new];Class kernel=NSClassFromString(@"PITextureStyleProcessorKernel");
  for(NSString*effect in @[@"UnderEyeBrightening",@"SkinSmoothingStandalone",@"Mattify"]){@try{
    id desc=[kernel descriptorForEffectName:effect tuningDictionary:selected semanticStyleProperties:semantic semanticStyleInfo:@{@"cast":@"Standard",@"color":@0}];
    NSDictionary*args=@{@"usage":@0,@"intensity":@0.87999999523162842,@"grainIntensity":@0,@"textureStyleProperties":texture,@"semanticStyleProperties":semantic,@"isVideo":@NO,@"effectDescriptors":@[desc],@"extents":extents};
    NSError*err=nil;CIImage*o=[(Class)kernel applyWithExtent:r inputs:inputs arguments:args error:&err];
    NSMutableDictionary*q=[@{@"effect":effect,@"descriptor":Safe(desc,0),@"error":err.description?:@"none"}mutableCopy];
    q[@"output"]=Dump(o,ctx,cs,[out stringByAppendingPathComponent:[effect stringByAppendingString:@".f32"]]);[trials addObject:q];
   }@catch(NSException*x){[trials addObject:@{@"effect":effect,@"exception":x.description}];}f[@"trials"]=trials;SaveJSON(f,[out stringByAppendingPathComponent:@"texture-results.json"]);
  }
  CGColorSpaceRelease(cs);
 }@catch(NSException*x){f[@"exception"]=x.description;}
 SaveJSON(f,[out stringByAppendingPathComponent:@"texture-results.json"]);return 0;
}}
