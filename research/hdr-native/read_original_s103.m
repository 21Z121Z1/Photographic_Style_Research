// Only the exact S37 original-SDR rendering block, no inverse regeneration.
#include "../vm-native/runner/Styles_full_v3.m"
int main(int argc,char**argv){@autoreleasepool{
 if(argc!=3)return 2;NSString*photo=@(argv[1]),*dir=@(argv[2]);
 @try{
CGColorSpaceRef cs=CGColorSpaceCreateWithName(kCGColorSpaceExtendedLinearDisplayP3);CIImage*s=Image(photo);NSUInteger w=llround(s.extent.size.width),h=llround(s.extent.size.height);s=Canvas(s,CGSizeMake(w,h));NSMutableData*raw=[NSMutableData dataWithLength:w*h*16];[Context(cs)render:s toBitmap:raw.mutableBytes rowBytes:w*16 bounds:CGRectMake(0,0,w,h)format:kCIFormatRGBAf colorSpace:cs];Require([raw writeToFile:[dir stringByAppendingPathComponent:@"original-sdr.f32"]atomically:YES],@"SDR denominator write");CGColorSpaceRelease(cs);
 NSDictionary*r=@{@"shape":@[@(h),@(w),@4],@"dtype":@"<f4",@"file":@"original-sdr.f32",@"scope":@"Unchanged original SDR block from source_s37.m, filename only changed; no style/thumbnail/native-map recomputation"};
 NSData*j=[NSJSONSerialization dataWithJSONObject:r options:NSJSONWritingPrettyPrinted error:NULL];Require(j&&[j writeToFile:[dir stringByAppendingPathComponent:@"original-facts.json"]atomically:YES],@"Source facts write");return 0;
 }@catch(NSException*e){NSLog(@"Original SDR reader failed: %@",e);return 5;}
}}
