#import <Foundation/Foundation.h>
#import <AVFoundation/AVFoundation.h>
#import <CoreImage/CoreImage.h>
#import <Metal/Metal.h>
#import <dlfcn.h>

static void Require(BOOL value,NSString*message){if(!value){fprintf(stderr,"%s\n",message.UTF8String);exit(1);}}
static NSString*Path(NSString*root,NSString*name){return [root stringByAppendingPathComponent:name];}
static id Safe(id x){
    if(!x)return NSNull.null;
    if([x isKindOfClass:NSNumber.class])return isfinite([x doubleValue])?x:NSNull.null;
    if([x isKindOfClass:NSString.class]||x==NSNull.null)return x;
    if([x isKindOfClass:NSData.class])return @{@"bytes":@([x length])};
    if([x isKindOfClass:NSDictionary.class]){NSMutableDictionary*d=[NSMutableDictionary new];for(id k in x)d[[k description]]=Safe(x[k]);return d;}
    if([x isKindOfClass:NSArray.class]){NSMutableArray*a=[NSMutableArray new];for(id v in x)[a addObject:Safe(v)];return a;}
    return [x description];
}
static void JSON(id value,NSString*file){NSError*e=nil;NSData*d=[NSJSONSerialization dataWithJSONObject:Safe(value)options:NSJSONWritingPrettyPrinted|NSJSONWritingSortedKeys error:&e];Require(d&&[d writeToFile:file options:NSDataWritingAtomic error:&e],e.description?:@"JSON failed");}
static NSDictionary*Time(CMTime t){return @{@"value":@(t.value),@"scale":@(t.timescale),@"seconds":@(CMTimeGetSeconds(t))};}
static CIImage*Resize(CIImage*im,CGRect rect,size_t w,size_t h){im=[im imageByCroppingToRect:rect];im=[im imageByApplyingTransform:CGAffineTransformMakeTranslation(-rect.origin.x,-rect.origin.y)];return [im imageByApplyingTransform:CGAffineTransformMakeScale(w/rect.size.width,h/rect.size.height)];}
static NSData*Render(CIImage*im,CIContext*ctx,CGColorSpaceRef cs,size_t w,size_t h){Require(im!=nil,@"Nil image");NSMutableData*d=[NSMutableData dataWithLength:w*h*16];[ctx render:im toBitmap:d.mutableBytes rowBytes:w*16 bounds:CGRectMake(0,0,w,h)format:kCIFormatRGBAf colorSpace:cs];return d;}
static NSDictionary*Save(NSData*d,NSString*file,size_t w,size_t h){Require([d writeToFile:file atomically:YES],@"Pixel write failed");const float*p=d.bytes;float lo=INFINITY,hi=-INFINITY;double sum=0;size_t bad=0;for(size_t i=0;i<w*h;i++)for(int c=0;c<3;c++){float v=p[4*i+c];if(!isfinite(v))bad++;else{lo=fminf(lo,v);hi=fmaxf(hi,v);sum+=v;}}Require(!bad&&hi>0,@"Invalid pixels");return @{@"file":file.lastPathComponent,@"width":@(w),@"height":@(h),@"min":@(lo),@"max":@(hi),@"mean":@(sum/(w*h*3))};}
static AVAssetReaderTrackOutput*Reader(AVAsset*a,AVAssetTrack*t,AVAssetReader**r,BOOL decode){*r=[[AVAssetReader alloc]initWithAsset:a error:NULL];AVAssetReaderTrackOutput*o=[[AVAssetReaderTrackOutput alloc]initWithTrack:t outputSettings:decode?@{(id)kCVPixelBufferPixelFormatTypeKey:@(kCVPixelFormatType_64RGBAHalf),(id)kCVPixelBufferIOSurfacePropertiesKey:@{}}:nil];o.alwaysCopiesSampleData=NO;[*r addOutput:o];if(decode)Require([*r startReading],(*r).error.description);return o;}
static NSDictionary*Extensions(AVAssetTrack*t){return (__bridge NSDictionary*)CMFormatDescriptionGetExtensions((__bridge CMFormatDescriptionRef)t.formatDescriptions.firstObject);}

int main(int argc,char**argv){@autoreleasepool{
    if(argc!=6){fprintf(stderr,"decode PHOTO_HEIC LINEAR_PRIMARY_HEIC STYLES_PLIST MOV NEW_OUTPUT\n");return 2;}
    NSString*out=@(argv[5]);NSError*error=nil;Require([[NSFileManager defaultManager]createDirectoryAtPath:out withIntermediateDirectories:NO attributes:nil error:&error],error.description);
    id<MTLDevice>device=MTLCreateSystemDefaultDevice();Require(device!=nil,@"Metal unavailable");
    CGColorSpaceRef p3=CGColorSpaceCreateWithName(kCGColorSpaceExtendedLinearDisplayP3),rec2020=CGColorSpaceCreateWithName(kCGColorSpaceExtendedLinearITUR_2020);
    CIContext*raw=[CIContext contextWithMTLDevice:device options:@{kCIContextWorkingColorSpace:NSNull.null,kCIContextOutputColorSpace:NSNull.null,kCIContextWorkingFormat:@(kCIFormatRGBAf)}];
    CIContext*managed=[CIContext contextWithMTLDevice:device options:@{kCIContextWorkingColorSpace:(__bridge id)p3,kCIContextWorkingFormat:@(kCIFormatRGBAf),kCIContextCacheIntermediates:@NO}];
    NSDictionary*metadata=[NSPropertyListSerialization propertyListWithData:[NSData dataWithContentsOfFile:@(argv[3])]options:0 format:NULL error:&error];Require(metadata!=nil,error.description);
    NSDictionary*enc=metadata[@"i"];double gain=[enc[@"Gain"]doubleValue],low=[enc[@"OriginalRangeMin"]doubleValue],high=[enc[@"OriginalRangeMax"]doubleValue];Require(gain>0&&high>low,@"Incomplete still encoding metadata");
    CIImage*stored=[CIImage imageWithContentsOfURL:[NSURL fileURLWithPath:@(argv[2])]options:@{kCIImageColorSpace:NSNull.null,kCIImageApplyOrientationProperty:@NO,kCIImageExpandToHDR:@NO}];Require(stored!=nil,@"Cannot decode selected HEIF auxiliary item");
    size_t sw=llround(stored.extent.size.width),sh=llround(stored.extent.size.height);fprintf(stderr,"Selected auxiliary extent: %zux%zu %s\n",sw,sh,NSStringFromRect(stored.extent).UTF8String);Require(sw==1024&&sh==768,@"Unexpected still auxiliary dimensions");
    NSMutableDictionary*facts=[@{@"photoSourcePath":[@(argv[1])stringByStandardizingPath],@"movieSourcePath":[@(argv[4])stringByStandardizingPath],@"gpu":device.name,@"os":NSProcessInfo.processInfo.operatingSystemVersionString,@"encoding":enc,@"metadataVersion":metadata[@"0"],@"floatLayout":@"RGBA float32 little endian; rows in Core Image render coordinates"}mutableCopy];
    facts[@"photoCodes"]=Save(Render(stored,raw,NULL,sw,sh),Path(out,@"photo-codes.f32"),sw,sh);
    CIImage*inverse=[stored imageByApplyingFilter:@"CIAppleLogToLinear"];Require(inverse!=nil,@"Native Apple Log filter unavailable");
    inverse=[inverse imageByApplyingFilter:@"CIColorMatrix"withInputParameters:@{@"inputRVector":[CIVector vectorWithX:1/gain Y:0 Z:0 W:0],@"inputGVector":[CIVector vectorWithX:0 Y:1/gain Z:0 W:0],@"inputBVector":[CIVector vectorWithX:0 Y:0 Z:1/gain W:0]}];
    inverse=[inverse imageByApplyingFilter:@"CIColorClamp"withInputParameters:@{@"inputMinComponents":[CIVector vectorWithX:low Y:low Z:low W:0],@"inputMaxComponents":[CIVector vectorWithX:high Y:high Z:high W:1]}];
    facts[@"photoLinear"]=Save(Render(inverse,raw,NULL,sw,sh),Path(out,@"photo-linear-p3.f32"),sw,sh);
    CIImage*photo=[CIImage imageWithContentsOfURL:[NSURL fileURLWithPath:@(argv[1])]options:@{kCIImageApplyOrientationProperty:@NO,kCIImageExpandToHDR:@NO}];Require(photo!=nil,@"Cannot decode still primary");facts[@"photoPrimaryExtent"]=NSStringFromRect(photo.extent);
    facts[@"photoSDR"]=Save(Render(Resize(photo,photo.extent,384,288),managed,p3,384,288),Path(out,@"photo-sdr.f32"),384,288);
    AVAsset*asset=[AVURLAsset URLAssetWithURL:[NSURL fileURLWithPath:@(argv[4])]options:nil];AVAssetTrack*main=[asset tracksWithMediaType:AVMediaTypeVideo].firstObject,*thumb=nil;
    for(AVAssetTrack*t in [asset tracksWithMediaType:AVMediaTypeAuxiliaryPicture])if([Extensions(t)[@"LogTransferFunction"]containsString:@"apple-log"])thumb=t;Require(main&&thumb,@"Missing video primary or logarithmic thumbnail track");
    NSMutableArray*allMetadata=[NSMutableArray new];CMTime still=kCMTimeInvalid;
    for(AVAssetTrack*t in [asset tracksWithMediaType:AVMediaTypeMetadata]){
        AVAssetReader*r;AVAssetReaderTrackOutput*o=Reader(asset,t,&r,NO);AVAssetReaderOutputMetadataAdaptor*ad=[[AVAssetReaderOutputMetadataAdaptor alloc]initWithAssetReaderTrackOutput:o];Require([r startReading],r.error.description);AVTimedMetadataGroup*g;
        while((g=[ad nextTimedMetadataGroup]))for(AVMetadataItem*item in g.items){NSString*name=item.identifier?:@"";id v=item.value;if([name hasSuffix:@"still-image-time"])still=g.timeRange.start;
            if([v isKindOfClass:NSData.class]){id parsed=[NSPropertyListSerialization propertyListWithData:v options:0 format:NULL error:NULL];if(parsed)v=parsed;}
            [allMetadata addObject:@{@"identifier":name,@"pts":Time(g.timeRange.start),@"duration":Time(g.timeRange.duration),@"value":Safe(v)}];
        }Require(r.status!=AVAssetReaderStatusFailed,r.error.description);[r cancelReading];
    }Require(CMTIME_IS_VALID(still),@"No still-image-time metadata");facts[@"stillTime"]=Time(still);facts[@"timedMetadata"]=allMetadata;facts[@"thumbnailTrack"]=@(thumb.trackID);facts[@"thumbnailFormat"]=Safe(Extensions(thumb));
    AVAssetReader*r;AVAssetReaderTrackOutput*o=Reader(asset,thumb,&r,YES);CMSampleBufferRef sb;size_t index=0;NSMutableArray*frames=[NSMutableArray new];
    while((sb=[o copyNextSampleBuffer])){@autoreleasepool{
        CVPixelBufferRef pb=CMSampleBufferGetImageBuffer(sb);size_t w=CVPixelBufferGetWidth(pb),h=CVPixelBufferGetHeight(pb);CIImage*codes=[CIImage imageWithCVPixelBuffer:pb options:@{kCIImageColorSpace:NSNull.null,kCIImageApplyCleanAperture:@NO}];
        NSString*cf=[NSString stringWithFormat:@"video-codes-%04zu.f32",index],*lf=[NSString stringWithFormat:@"video-linear-%04zu.f32",index];
        NSDictionary*cr=Save(Render(codes,raw,NULL,w,h),Path(out,cf),w,h);CIImage*lin=[codes imageByApplyingFilter:@"CIAppleLogToLinear"];NSData*lp=Render(lin,raw,NULL,w,h);
        CIImage*rgb=[CIImage imageWithBitmapData:lp bytesPerRow:w*16 size:CGSizeMake(w,h)format:kCIFormatRGBAf colorSpace:rec2020];NSDictionary*lr=Save(Render(rgb,managed,p3,w,h),Path(out,lf),w,h);
        [frames addObject:@{@"index":@(index++),@"pts":Time(CMSampleBufferGetPresentationTimeStamp(sb)),@"duration":Time(CMSampleBufferGetDuration(sb)),@"codes":cr,@"linear":lr,@"attachments":Safe(CFBridgingRelease(CVBufferCopyAttachments(pb,kCVAttachmentMode_ShouldPropagate)))}];CFRelease(sb);
    }}Require(r.status==AVAssetReaderStatusCompleted,@"Thumbnail decoding incomplete");facts[@"thumbnails"]=frames;
    AVAssetReader*mr;AVAssetReaderTrackOutput*mo=Reader(asset,main,&mr,YES);index=0;NSMutableArray*near=[NSMutableArray new];
    CGRect clean=CMVideoFormatDescriptionGetCleanAperture((__bridge CMFormatDescriptionRef)main.formatDescriptions.firstObject,NO);facts[@"mainCleanAperture"]=NSStringFromRect(clean);facts[@"mainFormat"]=Safe(Extensions(main));
    while((sb=[mo copyNextSampleBuffer])){@autoreleasepool{CMTime pts=CMSampleBufferGetPresentationTimeStamp(sb);if(fabs(CMTimeGetSeconds(CMTimeSubtract(pts,still)))<=.13){CVPixelBufferRef pb=CMSampleBufferGetImageBuffer(sb);CIImage*im=[CIImage imageWithCVPixelBuffer:pb options:@{kCIImageApplyCleanAperture:@NO}];NSString*file=[NSString stringWithFormat:@"main-full-%04zu.f32",index],*crop=[NSString stringWithFormat:@"main-clean-%04zu.f32",index];
        NSDictionary*full=Save(Render(Resize(im,im.extent,384,288),managed,p3,384,288),Path(out,file),384,288),*cropped=Save(Render(Resize(im,clean,384,288),managed,p3,384,288),Path(out,crop),384,288);
        [near addObject:@{@"index":@(index),@"pts":Time(pts),@"nativeBufferWidth":@(CVPixelBufferGetWidth(pb)),@"nativeBufferHeight":@(CVPixelBufferGetHeight(pb)),@"ciExtent":NSStringFromRect(im.extent),@"full":full,@"clean":cropped}];}
        index++;CFRelease(sb);
    }}Require(mr.status==AVAssetReaderStatusCompleted,@"Primary decode incomplete");facts[@"nearbyMainFrames"]=near;
    float basis[12]={1,0,0,1,0,1,0,1,0,0,1,1};CIImage*test=[CIImage imageWithBitmapData:[NSData dataWithBytes:basis length:sizeof(basis)]bytesPerRow:sizeof(basis)size:CGSizeMake(3,1)format:kCIFormatRGBAf colorSpace:rec2020];NSData*matrix=Render(test,managed,p3,3,1);[matrix writeToFile:Path(out,@"rec2020-to-p3-basis.f32")atomically:YES];
    JSON(facts,Path(out,@"decoded.json"));printf("Decoded still %zux%zu, %lu video thumbnails, %lu nearby main frames, still PTS %.9f\n",sw,sh,(unsigned long)frames.count,(unsigned long)near.count,CMTimeGetSeconds(still));CGColorSpaceRelease(p3);CGColorSpaceRelease(rec2020);return 0;
}}
