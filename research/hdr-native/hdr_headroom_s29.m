// Public synthetic probe of the original Core Image dual-rendition writer
// and applyingGainMap:headroom:. No photo, Apple executable, or capture upload.
#import <Foundation/Foundation.h>
#import <CoreImage/CoreImage.h>
#import <ImageIO/ImageIO.h>
#import <Metal/Metal.h>
#import <CommonCrypto/CommonDigest.h>
#import <objc/runtime.h>
#include <math.h>
static void Need(BOOL ok,NSString*reason){if(!ok)@throw[NSException exceptionWithName:@"HDRS29"reason:reason userInfo:nil];}
static void JSON(id obj,NSString*path){NSData*d=[NSJSONSerialization dataWithJSONObject:obj options:NSJSONWritingPrettyPrinted|NSJSONWritingSortedKeys error:NULL];Need(d!=nil,@"Non-JSON data");Need([d writeToFile:path atomically:YES],@"JSON write");}
static NSString*SHA(NSData*d){unsigned char h[32];CC_SHA256(d.bytes,(CC_LONG)d.length,h);NSMutableString*s=[NSMutableString new];for(int k=0;k<32;k++)[s appendFormat:@"%02x",h[k]];return s;}
static id Safe(id v){if(!v)return NSNull.null;if([v isKindOfClass:NSString.class]||[v isKindOfClass:NSNumber.class]||[v isKindOfClass:NSNull.class])return v;if([v isKindOfClass:NSData.class])return @{@"size":@([v length]),@"sha256":SHA(v)};if([v isKindOfClass:NSDictionary.class]){NSMutableDictionary*r=[NSMutableDictionary new];for(id k in v)r[[k description]]=Safe(v[k]);return r;}if([v isKindOfClass:NSArray.class]){NSMutableArray*r=[NSMutableArray new];for(id x in v)[r addObject:Safe(x)];return r;}return [v description];}
static NSData*Render(CIContext*ctx,CIImage*im,CGColorSpaceRef cs,NSUInteger w,NSUInteger h){Need(CGRectEqualToRect(im.extent,CGRectMake(0,0,w,h)),@"Unexpected output extent");NSMutableData*d=[NSMutableData dataWithLength:w*h*16];[ctx render:im toBitmap:d.mutableBytes rowBytes:w*16 bounds:im.extent format:kCIFormatRGBAf colorSpace:cs];return d;}
static NSDictionary*Diff(NSData*a,NSData*b){Need(a.length==b.length,@"Metric shape mismatch");const float*x=a.bytes,*y=b.bytes;double maximum=0,square=0,relative=0;NSUInteger bits=0,nonfinite=0,n=a.length/16;for(NSUInteger p=0;p<n;p++)for(int c=0;c<3;c++){NSUInteger k=p*4+c;double v=x[k],z=y[k],e=fabs(v-z);nonfinite+=!isfinite(v)||!isfinite(z);maximum=fmax(maximum,e);relative=fmax(relative,e/fmax(fabs(z),1e-6));square+=e*e;bits+=memcmp(x+k,y+k,4)!=0;}return @{@"pixels":@(n),@"float_components_different":@(bits),@"nonfinite":@(nonfinite),@"max_abs":@(maximum),@"max_relative":@(relative),@"PSNR_peak1_db":square?@(-10*log10(square/(n*3))):@"inf"};}
static void Bin(NSData*d,NSString*path,NSUInteger w,NSUInteger h){Need([d writeToFile:path atomically:YES],@"Bin write");JSON(@{@"shape":@[@(h),@(w),@4],@"dtype":@"<f4",@"space":@"extended-linear Display P3",@"sha256":SHA(d)},[path stringByAppendingString:@".json"]);}
int main(int argc,char**argv){@autoreleasepool{if(argc!=2)return 2;NSString*root=@(argv[1]);[[NSFileManager defaultManager]createDirectoryAtPath:root withIntermediateDirectories:YES attributes:nil error:NULL];NSMutableDictionary*report=[@{@"os":NSProcessInfo.processInfo.operatingSystemVersionString,@"scope":@"Original Core Image public dual-image HEIF writer and gain-map headroom reader; five synthetic pairs only. No captured camera/scene inverse.",@"photos_used":@NO,@"camera_inverse_verified":@NO,@"old_gates_modified":@NO}mutableCopy];@try{
 id<MTLDevice>dev=MTLCreateSystemDefaultDevice();Need(dev!=nil,@"Metal unavailable");report[@"device"]=dev.name;
 CGColorSpaceRef linear=CGColorSpaceCreateWithName(kCGColorSpaceExtendedLinearDisplayP3);CGColorSpaceRef display=CGColorSpaceCreateWithName(kCGColorSpaceDisplayP3);
 CIContext*ctx=[CIContext contextWithMTLDevice:dev options:@{kCIContextWorkingColorSpace:(__bridge id)linear,kCIContextOutputColorSpace:(__bridge id)linear,kCIContextWorkingFormat:@(kCIFormatRGBAf),kCIContextCacheIntermediates:@NO}];
 const NSUInteger w=256,h=128;NSMutableArray*cases=[NSMutableArray new];NSArray*names=@[@"flat-neutral",@"gray-expansion",@"rgb-opposing",@"edge-reversal",@"nearblack-highlight",@"flat-HDR",@"edge-HDR"];
 for(NSUInteger test=0;test<names.count;test++){@autoreleasepool{
  NSString*dir=[root stringByAppendingPathComponent:names[test]];[[NSFileManager defaultManager]createDirectoryAtPath:dir withIntermediateDirectories:YES attributes:nil error:NULL];NSMutableDictionary*row=[@{@"case":names[test],@"width":@(w),@"height":@(h)}mutableCopy];
  @try{NSMutableData*base=[NSMutableData dataWithLength:w*h*16],*target=[NSMutableData dataWithLength:w*h*16];float*s=base.mutableBytes,*t=target.mutableBytes;double peak=0;
   for(NSUInteger y=0;y<h;y++)for(NSUInteger x=0;x<w;x++){double u=(x+.5)/w,v=(y+.5)/h;for(int c=0;c<3;c++){double a=.18,e=2;
    if(test==1){a=.002+.8*u;e=3*u;}
    if(test==2){a=.04+.7*(c==0?u:c==1?v:1-u);e=c==0?3*u:c==1?-.5+2*v:2*(1-u);}
    if(test==3){a=x<w/2?.08:.65;e=x<w/2?1.5:-.25;}
    if(test==4){a=x<8?0:x<16?1e-6:x<24?1e-4:pow(u,3);e=3*pow(u,.25);}
    if(test==5){a=.18;e=3;}
    if(test==6){a=x<w/2?.08:.65;e=x<w/2?2:1;}
    s[(y*w+x)*4+c]=a;t[(y*w+x)*4+c]=a*exp2(e);peak=fmax(peak,t[(y*w+x)*4+c]);}
    s[(y*w+x)*4+3]=t[(y*w+x)*4+3]=1;
   }
   CIImage*S=[CIImage imageWithBitmapData:base bytesPerRow:w*16 size:CGSizeMake(w,h)format:kCIFormatRGBAf colorSpace:linear];CIImage*H=[CIImage imageWithBitmapData:target bytesPerRow:w*16 size:CGSizeMake(w,h)format:kCIFormatRGBAf colorSpace:linear];
   Bin(base,[dir stringByAppendingPathComponent:@"source-sdr.f32"],w,h);Bin(target,[dir stringByAppendingPathComponent:@"target-hdr.f32"],w,h);
   NSURL*file=[NSURL fileURLWithPath:[dir stringByAppendingPathComponent:@"dual.heic"]];NSError*error=nil;BOOL ok=[ctx writeHEIFRepresentationOfImage:S toURL:file format:kCIFormatRGBA8 colorSpace:display options:@{kCIImageRepresentationHDRImage:H,kCIImageRepresentationHDRGainMapAsRGB:@YES,(__bridge NSString*)kCGImageDestinationLossyCompressionQuality:@1}error:&error];Need(ok,error.description?:@"Dual writer failed");row[@"carrier_sha256"]=SHA([NSData dataWithContentsOfURL:file]);
   CIImage*decoded=[CIImage imageWithContentsOfURL:file options:@{kCIImageApplyOrientationProperty:@NO,kCIImageExpandToHDR:@NO}];CIImage*full=[CIImage imageWithContentsOfURL:file options:@{kCIImageApplyOrientationProperty:@NO,kCIImageExpandToHDR:@YES}];CIImage*gain=[CIImage imageWithContentsOfURL:file options:@{kCIImageApplyOrientationProperty:@NO,kCIImageAuxiliaryHDRGainMap:@YES}];row[@"decoded_present"]=@(decoded!=nil);row[@"expanded_present"]=@(full!=nil);row[@"gain_present"]=@(gain!=nil);row[@"supplied_target_peak"]=@(peak);Need(decoded&&full,@"Native decoded SDR/HDR nil");
   if(!gain){Need(test==0||test==3,@"Unexpected missing gain map for above-white target");row[@"boundary_observation"]=@"Gain map not returned for this unchanged below-white synthetic target; no universal writer rule inferred";row[@"success"]=@YES;row[@"gain_contract_verified"]=@NO;JSON(row,[dir stringByAppendingPathComponent:@"case.json"]);[cases addObject:row];report[@"cases"]=cases;JSON(report,[root stringByAppendingPathComponent:@"native-results.json"]);continue;}
   row[@"content_headroom"]=@(full.contentHeadroom);row[@"base_headroom"]=@(decoded.contentHeadroom);row[@"gain_extent"]=@[@(gain.extent.origin.x),@(gain.extent.origin.y),@(gain.extent.size.width),@(gain.extent.size.height)];row[@"gain_properties"]=Safe(gain.properties);
   CGImageSourceRef src=CGImageSourceCreateWithURL((__bridge CFURLRef)file,NULL);Need(src!=NULL,@"ImageIO source nil");NSDictionary*aux=CFBridgingRelease(CGImageSourceCopyAuxiliaryDataInfoAtIndex(src,0,kCGImageAuxiliaryDataTypeISOGainMap));row[@"ISO_aux"]=Safe(aux);id metadata=aux[(__bridge NSString*)kCGImageAuxiliaryDataInfoMetadata];if(metadata){NSData*xmp=CFBridgingRelease(CGImageMetadataCreateXMPData((__bridge CGImageMetadataRef)metadata,NULL));if(xmp){[xmp writeToFile:[dir stringByAppendingPathComponent:@"ISO-metadata.xml"]atomically:YES];row[@"ISO_metadata_XMP"]=@"ISO-metadata.xml";}}CFRelease(src);
   NSData*decodedBase=Render(ctx,decoded,linear,w,h),*decodedFull=Render(ctx,full,linear,w,h);Bin(decodedBase,[dir stringByAppendingPathComponent:@"decoded-sdr.f32"],w,h);Bin(decodedFull,[dir stringByAppendingPathComponent:@"decoded-hdr.f32"],w,h);row[@"base_codec_difference"]=Diff(decodedBase,base);row[@"native_HDR_vs_target"]=Diff(decodedFull,target);
   NSUInteger gw=llround(gain.extent.size.width),gh=llround(gain.extent.size.height);CGColorSpaceRef raw=NULL;NSMutableData*gm=[NSMutableData dataWithLength:gw*gh*16];[ctx render:gain toBitmap:gm.mutableBytes rowBytes:gw*16 bounds:gain.extent format:kCIFormatRGBAf colorSpace:raw];Bin(gm,[dir stringByAppendingPathComponent:@"decoded-gain.f32"],gw,gh);
   NSMutableArray*sweep=[NSMutableArray new];for(NSNumber*headroom in @[@1,@1.25,@1.5,@2,@3,@4,@8]){CIImage*adapted=[decoded imageByApplyingGainMap:gain headroom:headroom.floatValue];NSData*actual=Render(ctx,adapted,linear,w,h);NSString*name=[NSString stringWithFormat:@"headroom-%@.f32",headroom];Bin(actual,[dir stringByAppendingPathComponent:name],w,h);[sweep addObject:@{@"requested_headroom":headroom,@"output_content_headroom":@(adapted.contentHeadroom),@"native_vs_decoded_SDR":Diff(actual,decodedBase),@"native_vs_full_HDR":Diff(actual,decodedFull),@"file":name}];}
   row[@"headroom_sweep"]=sweep;row[@"success"]=@YES;
  }@catch(NSException*e){row[@"success"]=@NO;row[@"exception"]=e.description;}
  JSON(row,[dir stringByAppendingPathComponent:@"case.json"]);[cases addObject:row];report[@"cases"]=cases;JSON(report,[root stringByAppendingPathComponent:@"native-results.json"]);
 }}
 CGColorSpaceRelease(linear);CGColorSpaceRelease(display);BOOL all=YES;for(NSDictionary*r in cases)all&=[r[@"success"]boolValue];report[@"all_cases_executed"]=@(all);JSON(report,[root stringByAppendingPathComponent:@"native-results.json"]);return all?0:5;
 }@catch(NSException*e){report[@"exception"]=e.description;JSON(report,[root stringByAppendingPathComponent:@"native-results.json"]);return 6;}
}}
