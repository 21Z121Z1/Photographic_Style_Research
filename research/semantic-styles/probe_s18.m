#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#include <math.h>
#include <stdint.h>
#include <string.h>
int main(){@autoreleasepool{
 NSUInteger finite=0,nonfinite=0;double minPositive=INFINITY,maxFinite=0;
 for(uint32_t b=0;b<65536;b++){uint16_t bits=b;__fp16 h;memcpy(&h,&bits,2);double v=(double)h;if(isfinite(v)){finite++;maxFinite=fmax(maxFinite,fabs(v));if(v>0)minPositive=fmin(minPositive,v);}else nonfinite++;}
 id<MTLDevice>d=MTLCreateSystemDefaultDevice();NSDictionary*r=@{@"os":NSProcessInfo.processInfo.operatingSystemVersionString,@"metal":d.name?:@"none",@"RGBA16Float_enum":@(MTLPixelFormatRGBA16Float),@"finite_half_bit_patterns":@(finite),@"nonfinite_half_bit_patterns":@(nonfinite),@"largest_finite_half_abs":@(maxFinite),@"smallest_positive_half_including_subnormal":@(minPositive),@"excludes_nonfinite_from_global_feasibility":@NO};
 NSData*j=[NSJSONSerialization dataWithJSONObject:r options:NSJSONWritingPrettyPrinted|NSJSONWritingSortedKeys error:NULL];fwrite(j.bytes,1,j.length,stdout);puts("");return 0;
}}
