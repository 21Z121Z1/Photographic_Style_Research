#import <Foundation/Foundation.h>
#import <CoreImage/CoreImage.h>
#import <ImageIO/ImageIO.h>
#import <CommonCrypto/CommonDigest.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
static NSString *digest(CC_SHA256_CTX *c){unsigned char d[CC_SHA256_DIGEST_LENGTH];CC_SHA256_Final(d,c);NSMutableString*s=[NSMutableString new];for(int i=0;i<sizeof(d);i++)[s appendFormat:@"%02x",d[i]];return s;}
int main(int argc,char **argv){@autoreleasepool{
 if(argc!=4)return 2;
 NSDictionary *options=@{kCIImageApplyOrientationProperty:@NO,kCIImageExpandToHDR:@NO};
 CIImage*a=[CIImage imageWithContentsOfURL:[NSURL fileURLWithPath:@(argv[1])]options:options];
 CIImage*b=[CIImage imageWithContentsOfURL:[NSURL fileURLWithPath:@(argv[2])]options:options];
 if(!a||!b||!CGRectEqualToRect(a.extent,b.extent))return 3;
 size_t width=(size_t)a.extent.size.width,height=(size_t)a.extent.size.height,rows=64;
 CGColorSpaceRef p3=CGColorSpaceCreateWithName(kCGColorSpaceExtendedLinearDisplayP3);
 CIContext *ctx=[CIContext contextWithOptions:@{kCIContextWorkingColorSpace:(__bridge id)p3,kCIContextOutputColorSpace:(__bridge id)p3}];
 float*x=malloc(width*rows*16),*y=malloc(width*rows*16);if(!x||!y)return 4;
 double maximum=0;uint64_t changed=0,nonfinite=0;CC_SHA256_CTX hx,hy;CC_SHA256_Init(&hx);CC_SHA256_Init(&hy);
 for(size_t row=0;row<height;row+=rows){@autoreleasepool{
  size_t count=MIN(rows,height-row);CGRect bounds=CGRectMake(a.extent.origin.x,a.extent.origin.y+row,width,count);
  [ctx render:a toBitmap:x rowBytes:width*16 bounds:bounds format:kCIFormatRGBAf colorSpace:p3];
  [ctx render:b toBitmap:y rowBytes:width*16 bounds:bounds format:kCIFormatRGBAf colorSpace:p3];
  CC_SHA256_Update(&hx,x,(CC_LONG)(width*count*16));CC_SHA256_Update(&hy,y,(CC_LONG)(width*count*16));
  for(size_t i=0;i<width*count*4;i++){if(!isfinite(x[i])||!isfinite(y[i]))nonfinite++;double d=fabs((double)x[i]-y[i]);if(d>maximum)maximum=d;if(memcmp(x+i,y+i,4))changed++;}
 }}
 NSDictionary*r=@{@"os":NSProcessInfo.processInfo.operatingSystemVersionString,@"shape":@[@(height),@(width),@4],@"components":@(height*width*4),@"colour_space":@"extended-linear Display P3",@"apply_orientation":@NO,@"expand_hdr":@NO,@"max_abs":@(maximum),@"different_float_bitpatterns":@(changed),@"nonfinite":@(nonfinite),@"source_decoded_sha256":digest(&hx),@"carrier_decoded_sha256":digest(&hy)};
 [[NSJSONSerialization dataWithJSONObject:r options:NSJSONWritingPrettyPrinted error:NULL]writeToFile:@(argv[3])atomically:YES];free(x);free(y);CGColorSpaceRelease(p3);return nonfinite||changed||maximum?5:0;
}}
