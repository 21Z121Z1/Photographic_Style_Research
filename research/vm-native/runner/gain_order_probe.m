#import <Foundation/Foundation.h>
#import <CoreImage/CoreImage.h>
#import <ImageIO/ImageIO.h>
#import <CommonCrypto/CommonDigest.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
static CIImage* canvas(CIImage*i,CGSize s){CGRect r=i.extent;return [[i imageByApplyingTransform:CGAffineTransformMakeTranslation(-r.origin.x,-r.origin.y)]imageByApplyingTransform:CGAffineTransformMakeScale(s.width/r.size.width,s.height/r.size.height)];}
static NSData* render(CIImage*i,CIContext*c,CGColorSpaceRef s,CGSize size){NSMutableData*d=[NSMutableData dataWithLength:(size_t)size.width*(size_t)size.height*16];[c render:canvas(i,size) toBitmap:d.mutableBytes rowBytes:(size_t)size.width*16 bounds:CGRectMake(0,0,size.width,size.height)format:kCIFormatRGBAf colorSpace:s];return d;}
static NSDictionary* metrics(NSData*x,NSData*y){const float*a=x.bytes,*b=y.bytes;size_t n=x.length/16;double e=0,m=0,maxd=0,maxe=0;uint64_t nonpos=0;for(size_t i=0;i<n;i++){double ya=.2289745641*a[4*i]+.6917385218*a[4*i+1]+.0792869141*a[4*i+2],yb=.2289745641*b[4*i]+.6917385218*b[4*i+1]+.0792869141*b[4*i+2];double de=fabs(log2(fmax(ya,1e-6)/fmax(yb,1e-6)));e+=de;if(de>maxe)maxe=de;if(ya<=0)nonpos++;for(int k=0;k<3;k++){double d=fabs((double)a[4*i+k]-b[4*i+k]);m+=d*d;if(d>maxd)maxd=d;}}return @{@"pixels":@(n),@"mae_ev":@(e/n),@"max_ev":@(maxe),@"max_abs":@(maxd),@"psnr_peak1_db":m?@(-10*log10(m/(n*3))):@"inf",@"nonpositive_Y":@(nonpos)};}
static NSString* sha(NSData*d){unsigned char out[32];CC_SHA256(d.bytes,(CC_LONG)d.length,out);NSMutableString*s=[NSMutableString new];for(int i=0;i<32;i++)[s appendFormat:@"%02x",out[i]];return s;}
static void crop(NSData*d,NSString*path,CGSize size){const float*p=d.bytes;NSMutableData*out=[NSMutableData dataWithLength:64*64*16];float*q=out.mutableBytes;for(int y=0;y<64;y++)memcpy(q+y*64*4,p+y*(size_t)size.width*4,64*16);[out writeToFile:path atomically:YES];}
int main(int argc,char**argv){@autoreleasepool{
 if(argc!=8)return 2;NSString*out=@(argv[7]);CGSize size=CGSizeMake(2048,1536);
 CGColorSpaceRef p3=CGColorSpaceCreateWithName(kCGColorSpaceExtendedLinearDisplayP3);
 CIContext*ctx=[CIContext contextWithOptions:@{kCIContextWorkingColorSpace:(__bridge id)p3,kCIContextOutputColorSpace:(__bridge id)p3,kCIContextWorkingFormat:@(kCIFormatRGBAf)}];
 NSDictionary*sdro=@{kCIImageApplyOrientationProperty:@NO,kCIImageExpandToHDR:@NO};
 CIImage*base=[CIImage imageWithContentsOfURL:[NSURL fileURLWithPath:@(argv[1])]options:sdro];
 CIImage*reference=[CIImage imageWithContentsOfURL:[NSURL fileURLWithPath:@(argv[2])]options:@{kCIImageApplyOrientationProperty:@NO,kCIImageExpandToHDR:@YES}];
 CIImage*gain=[CIImage imageWithContentsOfURL:[NSURL fileURLWithPath:@(argv[3])]options:@{kCIImageApplyOrientationProperty:@NO,kCIImageExpandToHDR:@NO,kCIImageColorSpace:NSNull.null}];
 if(!base||!reference||!gain)return 3;
 CIVector*p=[CIVector vectorWithX:atof(argv[4])Y:atof(argv[5])Z:atof(argv[6])W:0];
 CIColorKernel*logapply=[CIColorKernel kernelWithString:@"kernel vec4 apply_log(__sample im,__sample gm,vec4 p){return vec4((im.rgb+p.z)*exp2(p.x+(p.y-p.x)*gm.rgb)-p.z,im.a);}"];
 CIColorKernel*linearize=[CIColorKernel kernelWithString:@"kernel vec4 linearize_gain(__sample gm,vec4 p){return vec4(exp2(p.x+(p.y-p.x)*gm.rgb),1.0);}"];
 CIColorKernel*linapply=[CIColorKernel kernelWithString:@"kernel vec4 apply_linear(__sample im,__sample gm,vec4 p){return vec4((im.rgb+p.z)*gm.rgb-p.z,im.a);}"];
 if(!logapply||!linearize||!linapply){fprintf(stderr,"kernel compile nil\n");return 4;}
 NSData*ref=render(reference,ctx,p3,size);crop(ref,[out stringByAppendingPathComponent:@"reference-crop.f32"],size);
 NSMutableDictionary*rows=[NSMutableDictionary new];CGRect full=base.extent;
 CIImage*a=[logapply applyWithExtent:full arguments:@[base,canvas(gain,full.size),p]];
 CIImage*b=[logapply applyWithExtent:CGRectMake(0,0,size.width,size.height)arguments:@[canvas(base,size),canvas(gain,size),p]];
 CIImage*lg=[linearize applyWithExtent:gain.extent arguments:@[gain,p]];if(!a||!b||!lg){fprintf(stderr,"apply nil log_before=%d log_after=%d linearize=%d\n",a!=nil,b!=nil,lg!=nil);return 5;}NSData*materialized=render(lg,ctx,NULL,gain.extent.size);
 lg=[CIImage imageWithBitmapData:materialized bytesPerRow:(size_t)gain.extent.size.width*16 size:gain.extent.size format:kCIFormatRGBAf colorSpace:NULL];
 CIImage*c=[linapply applyWithExtent:full arguments:@[base,canvas(lg,full.size),p]];
 if(!c){fprintf(stderr,"linear-gain application nil\n");return 6;}NSArray*images=@[a,b,c];NSArray*names=@[@"log_before_resize",@"log_after_resize",@"linear_gain_before_resize"];
 for(int i=0;i<3;i++){@autoreleasepool{NSData*d=render(images[i],ctx,p3,size);NSMutableDictionary*r=[metrics(d,ref)mutableCopy];r[@"output_sha256"]=sha(d);rows[names[i]]=r;crop(d,[out stringByAppendingPathComponent:[names[i]stringByAppendingString:@"-crop.f32"]],size);}}
 NSDictionary*facts=@{@"os":NSProcessInfo.processInfo.operatingSystemVersionString,@"original_size":@[@(full.size.height),@(full.size.width)],@"gain_size":@[@(gain.extent.size.height),@(gain.extent.size.width)],@"output_shape":@[@1536,@2048,@4],@"crop_shape":@[@64,@64,@4],@"dtype":@"<f4",@"reference_sha256":sha(ref),@"min_ev":@(p.X),@"max_ev":@(p.Y),@"offset":@(p.Z),@"comparisons_to_ImageIO_HDR":rows,@"scope":@"Controlled application/resampling variants; no RAW oracle"};
 [[NSJSONSerialization dataWithJSONObject:facts options:NSJSONWritingPrettyPrinted error:NULL]writeToFile:[out stringByAppendingPathComponent:@"order.json"]atomically:YES];CGColorSpaceRelease(p3);return 0;
}}
