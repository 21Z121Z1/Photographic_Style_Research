// Native finite collision control. Synthetic constants only, no photo or writer.
#define main s50_unused_s29_main
#include "hdr_headroom_s29.m"
#undef main
int main(int argc,char **argv){@autoreleasepool{
 if(argc!=3)return 2;NSString *input=@(argv[1]),*output=@(argv[2]);
 @try{
  NSDictionary*j=[NSJSONSerialization JSONObjectWithData:[NSData dataWithContentsOfFile:input]options:0 error:NULL];
  id<MTLDevice>dev=MTLCreateSystemDefaultDevice();Need(dev!=nil,@"Metal unavailable");
  CGColorSpaceRef cs=CGColorSpaceCreateWithName(kCGColorSpaceExtendedLinearDisplayP3);
  CIContext*ctx=[CIContext contextWithMTLDevice:dev options:@{kCIContextWorkingColorSpace:(__bridge id)cs,kCIContextOutputColorSpace:(__bridge id)cs,kCIContextWorkingFormat:@(kCIFormatRGBAf),kCIContextCacheIntermediates:@NO}];
  const NSUInteger w=8,h=8;NSMutableArray*rows=[NSMutableArray new];
  for(NSDictionary*c in j[@"cases"]){@autoreleasepool{
   NSMutableData*s=[NSMutableData dataWithLength:w*h*16],*g=[NSMutableData dataWithLength:w*h*16];float *sv=s.mutableBytes,*gv=g.mutableBytes;
   for(NSUInteger p=0;p<w*h;p++){for(int k=0;k<3;k++){sv[4*p+k]=[c[@"source"]floatValue];gv[4*p+k]=[c[@"gain_code"]floatValue];}sv[4*p+3]=gv[4*p+3]=1;}
   NSData*xmp=[NSData dataWithContentsOfFile:c[@"metadata_file"]];CGImageMetadataRef meta=CGImageMetadataCreateFromXMPData((__bridge CFDataRef)xmp);Need(meta!=NULL,@"Gain metadata missing");
   CIImage*S=[CIImage imageWithBitmapData:s bytesPerRow:w*16 size:CGSizeMake(w,h)format:kCIFormatRGBAf colorSpace:cs];
   CIImage*G=[CIImage imageWithBitmapData:g bytesPerRow:w*16 size:CGSizeMake(w,h)format:kCIFormatRGBAf colorSpace:NULL];
   G=[G imageBySettingProperties:@{(__bridge NSString*)kCGImageAuxiliaryDataInfoMetadata:(__bridge id)meta}];
   NSMutableArray*sweep=[NSMutableArray new];
   for(NSNumber*headroom in @[@1,@1.25,@2,@4,@8]){@autoreleasepool{
    CIImage*im=[S imageByApplyingGainMap:G headroom:headroom.floatValue];Need(im!=nil,@"Native gain apply nil");NSData*r=Render(ctx,im,cs,w,h);NSString*name=[NSString stringWithFormat:@"%@-h%@.f32",c[@"id"],headroom];
    Need([r writeToFile:[c[@"temporary_output"]stringByAppendingPathComponent:name]atomically:YES],@"Synthetic output write");
    [sweep addObject:@{@"headroom":headroom,@"file":name,@"output_sha256":SHA(r)}];
   }}
   [rows addObject:@{@"id":c[@"id"],@"source_texture_sha256":SHA(s),@"gain_texture_sha256":SHA(g),@"metadata_sha256":SHA(xmp),@"headrooms":sweep}];CFRelease(meta);
  }}
  JSON(@{@"device":dev.name,@"AppleFamily4":@([dev supportsFamily:MTLGPUFamilyApple4]),@"shape":@[@8,@8,@4],@"dtype":@"<f4",@"photos_used":@NO,@"rows":rows},output);CGColorSpaceRelease(cs);return 0;
 }@catch(NSException*e){JSON(@{@"exception":e.description},output);return 5;}
}}
