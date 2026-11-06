#import <Foundation/Foundation.h>
#import <AVFoundation/AVFoundation.h>
#import <CoreImage/CoreImage.h>
#import <ImageIO/ImageIO.h>
#import <Metal/Metal.h>
#import <Vision/Vision.h>
#import <VideoToolbox/VideoToolbox.h>
#import <objc/runtime.h>
#import <dlfcn.h>

@interface NSObject (ResearchSPI)
- (instancetype)initWithOptionalMetalCommandQueue:(id)queue useCase:(NSUInteger)useCase processingType:(NSUInteger)type optionalExternalMemoryResource:(id)resource;
- (uint32_t)coefficientsPixelBufferPixelFormat;
- (int)computeOriginalUnstyledPixelBufferFrom:(CVPixelBufferRef)source inputDeltaMapPixelBuffer:(CVPixelBufferRef)delta inputCoefficientsPixelBuffer:(CVPixelBufferRef)coeff outputUnstyledPixelBuffer:(CVPixelBufferRef)output;
+ (id)StyleEngineConfigurationForUseCase:(NSUInteger)useCase;
+ (CGSize)hardwareStyleEngineCoefficientPixelBufferSizeForUseCase:(NSUInteger)useCase;
- (instancetype)initWithDevice:(id)device allocatorType:(int)type;
- (void)setMemSize:(NSUInteger)size;
- (void)setResourceOptions:(MTLResourceOptions)options;
- (int)setupWithDescriptor:(id)descriptor;
- (instancetype)initWithOptionalCommandQueue:(id)queue allocator:(id)allocator;
- (int)encodeToCommandBuffer:(id)command inputTexture:(id)input guideTexture:(id)guide outputTexture:(id)output kernelRadius:(NSUInteger)radius epsilon:(float)epsilon;
+ (id)semanticStylePropertiesFromData:(NSData*)data fromVideo:(BOOL)video keyTime:(CMTime)time error:(NSError**)error;
@end

static void Stop(NSString *s){fprintf(stderr,"%s\n",s.UTF8String);exit(1);}
static void Check(BOOL condition,NSString *s){if(!condition)Stop(s);}
static NSString *P(NSString *dir,NSString *name){return [dir stringByAppendingPathComponent:name];}
static id Safe(id x){
    if(!x)return NSNull.null;
    if([x isKindOfClass:NSNumber.class])return isfinite([x doubleValue])?x:NSNull.null;
    if([x isKindOfClass:NSString.class]||x==NSNull.null)return x;
    if([x isKindOfClass:NSData.class]){NSMutableDictionary*d=[@{@"bytes":@([x length])}mutableCopy];if([x length]<=24){NSMutableString*s=[NSMutableString new];const uint8_t*p=[x bytes];for(size_t i=0;i<[x length];i++)[s appendFormat:@"%02x",p[i]];d[@"hex"]=s;}return d;}
    if([x isKindOfClass:NSDictionary.class]){NSMutableDictionary*d=[NSMutableDictionary new];for(id k in x)d[[k description]]=Safe(x[k]);return d;}
    if([x isKindOfClass:NSArray.class]){NSMutableArray*a=[NSMutableArray new];for(id v in x)[a addObject:Safe(v)];return a;}
    return [x description];
}
static void JSON(id x,NSString *path){NSError*e=nil;NSData*d=[NSJSONSerialization dataWithJSONObject:Safe(x) options:NSJSONWritingPrettyPrinted|NSJSONWritingSortedKeys error:&e];Check(d&&[d writeToFile:path options:NSDataWritingAtomic error:&e],e.description?:@"JSON write failed");}
static id LoadJSON(NSString *path){return [NSJSONSerialization JSONObjectWithData:[NSData dataWithContentsOfFile:path] options:0 error:NULL];}
static NSDictionary *T(CMTime t){return @{@"value":@(t.value),@"scale":@(t.timescale),@"seconds":@(CMTimeGetSeconds(t))};}
static CMTime CT(NSDictionary*d){return CMTimeMake([d[@"value"]longLongValue],[d[@"scale"]intValue]);}
static NSDictionary *Ext(AVAssetTrack*t){return (__bridge NSDictionary*)CMFormatDescriptionGetExtensions((__bridge CMFormatDescriptionRef)t.formatDescriptions.firstObject);}
static CMVideoDimensions Dim(AVAssetTrack*t){return CMVideoFormatDescriptionGetDimensions((__bridge CMFormatDescriptionRef)t.formatDescriptions.firstObject);}
static CVPixelBufferRef Buffer(size_t w,size_t h,OSType fmt){CVPixelBufferRef b=NULL;CVReturn s=CVPixelBufferCreate(NULL,w,h,fmt,(__bridge CFDictionaryRef)@{(id)kCVPixelBufferIOSurfacePropertiesKey:@{},(id)kCVPixelBufferMetalCompatibilityKey:@YES},&b);Check(s==0,@"Pixel buffer allocation failed");return b;}
static AVAssetReaderTrackOutput *Reader(AVAsset*a,AVAssetTrack*t,BOOL decode,AVAssetReader**r){
    NSError*e=nil;*r=[[AVAssetReader alloc]initWithAsset:a error:&e];Check(*r!=nil,e.description);
    NSDictionary *settings=decode?@{(id)kCVPixelBufferPixelFormatTypeKey:@(kCVPixelFormatType_64RGBAHalf),(id)kCVPixelBufferIOSurfacePropertiesKey:@{}}:nil;
    AVAssetReaderTrackOutput*o=[[AVAssetReaderTrackOutput alloc]initWithTrack:t outputSettings:settings];o.alwaysCopiesSampleData=NO;[*r addOutput:o];if(decode)Check([*r startReading],(*r).error.description);return o;
}
static CIImage *Fit(CIImage*im,CGRect crop,size_t w,size_t h){
    im=[im imageByCroppingToRect:crop];im=[im imageByApplyingTransform:CGAffineTransformMakeTranslation(-crop.origin.x,-crop.origin.y)];
    return [im imageByApplyingTransform:CGAffineTransformMakeScale(w/crop.size.width,h/crop.size.height)];
}
static NSData *Pixels(CIImage*im,CIContext*ctx,CGColorSpaceRef cs,size_t w,size_t h){
    NSMutableData*d=[NSMutableData dataWithLength:w*h*16];[ctx render:im toBitmap:d.mutableBytes rowBytes:w*16 bounds:CGRectMake(0,0,w,h) format:kCIFormatRGBAf colorSpace:cs];return d;
}
static NSDictionary *Stats(NSData*d){const float*p=d.bytes;size_t count=d.length/16;double sum=0;float lo=INFINITY,hi=-INFINITY;size_t bad=0;for(size_t i=0;i<count;i++)for(int c=0;c<3;c++){float v=p[4*i+c];if(!isfinite(v))bad++;else{sum+=v;lo=fminf(lo,v);hi=fmaxf(hi,v);}}Check(bad==0&&hi>0,@"Nonfinite or empty render");return @{@"min":@(lo),@"max":@(hi),@"mean":@(sum/(count*3)),@"nonfinite":@(bad)};}
static CIImage *FloatImage(NSString*path,size_t w,size_t h,CGColorSpaceRef cs){NSData*d=[NSData dataWithContentsOfFile:path];Check(d.length==w*h*16,@"Float image byte length mismatch");return [CIImage imageWithBitmapData:d bytesPerRow:w*16 size:CGSizeMake(w,h) format:kCIFormatRGBAf colorSpace:cs];}

static id<MTLDevice>Device;static id<MTLCommandQueue>Queue;
static CGColorSpaceRef Linear,Linear2020;static CIContext*Context,*Unmanaged;
static void Setup(void){
    Check(dlopen("/System/Library/PrivateFrameworks/CMImaging.framework/CMImaging",RTLD_NOW)!=NULL,@"CMImaging unavailable");
    dlopen("/System/Library/PrivateFrameworks/NeutrinoCore.framework/NeutrinoCore",RTLD_NOW);
    Device=MTLCreateSystemDefaultDevice();Check(Device!=nil,@"Metal unavailable");Queue=[Device newCommandQueue];
    Linear=CGColorSpaceCreateWithName(kCGColorSpaceExtendedLinearDisplayP3);Linear2020=CGColorSpaceCreateWithName(kCGColorSpaceExtendedLinearITUR_2020);
    Context=[CIContext contextWithMTLDevice:Device options:@{kCIContextWorkingColorSpace:(__bridge id)Linear,kCIContextWorkingFormat:@(kCIFormatRGBAf),kCIContextCacheIntermediates:@NO}];
    Unmanaged=[CIContext contextWithMTLDevice:Device options:@{kCIContextWorkingColorSpace:NSNull.null,kCIContextOutputColorSpace:NSNull.null,kCIContextWorkingFormat:@(kCIFormatRGBAf),kCIContextCacheIntermediates:@NO}];
}
static CIImage *DecodeLog(CVPixelBufferRef pb){
    CIImage*raw=[CIImage imageWithCVPixelBuffer:pb options:@{kCIImageColorSpace:NSNull.null}];
    CIImage*inverse=[raw imageByApplyingFilter:@"CIAppleLogToLinear"];Check(inverse!=nil,@"Native Apple Log decoder unavailable");
    size_t w=CVPixelBufferGetWidth(pb),h=CVPixelBufferGetHeight(pb);NSData*d=Pixels(inverse,Unmanaged,NULL,w,h);
    return [CIImage imageWithBitmapData:d bytesPerRow:w*16 size:CGSizeMake(w,h) format:kCIFormatRGBAf colorSpace:Linear2020];
}
static id Utility(CVPixelBufferRef *coeff,NSDictionary **config){
    Class c=NSClassFromString(@"CMISmartStyleUtilitiesV1");Check(c!=Nil,@"Smart Style utility unavailable");
    id u=[(id)[c alloc]initWithOptionalMetalCommandQueue:Queue useCase:2 processingType:0 optionalExternalMemoryResource:nil];Check(u!=nil,@"Native video inverse initialization failed");
    CGSize size=[c hardwareStyleEngineCoefficientPixelBufferSizeForUseCase:2];
    id nativeConfig=[c StyleEngineConfigurationForUseCase:2];NSMutableDictionary*fields=[NSMutableDictionary new];
    for(NSString*k in @[@"inputIsLinear",@"outputShouldBeLinear",@"weightPlaneCount",@"spotlightCountX",@"spotlightCountY",@"linearSystemOrder"])
        if([nativeConfig respondsToSelector:NSSelectorFromString(k)])fields[k]=Safe([nativeConfig valueForKey:k]);
    *config=fields;
    Check(size.width>0&&size.height>0,@"Native coefficient dimensions unavailable");
    *coeff=Buffer(size.width,size.height,[u coefficientsPixelBufferPixelFormat]);return u;
}
static int Reverse(id utility,CVPixelBufferRef coeff,NSDictionary*meta,CVPixelBufferRef input,CVPixelBufferRef delta,CVPixelBufferRef *output){
    Check([meta[@"0"]integerValue]==16,@"This tested decoder supports Smart Style version 16 only");
    NSData*bytes=meta[@"1"];size_t w=CVPixelBufferGetWidth(coeff),h=CVPixelBufferGetHeight(coeff);
    Check([bytes isKindOfClass:NSData.class]&&bytes.length==w*h*2,@"Video coefficient size differs from native useCase 2");
    Check(CVPixelBufferGetPixelFormatType(coeff)==kCVPixelFormatType_OneComponent32Float,@"Unsupported native coefficient format");
    CVPixelBufferLockBaseAddress(coeff,0);float*p=CVPixelBufferGetBaseAddress(coeff);size_t stride=CVPixelBufferGetBytesPerRow(coeff)/4;const __fp16*v=bytes.bytes;
    for(size_t y=0;y<h;y++)for(size_t x=0;x<w;x++)p[y*stride+x]=v[y*w+x];CVPixelBufferUnlockBaseAddress(coeff,0);
    *output=Buffer(CVPixelBufferGetWidth(input),CVPixelBufferGetHeight(input),kCVPixelFormatType_64RGBAHalf);
    int status=[utility computeOriginalUnstyledPixelBufferFrom:input inputDeltaMapPixelBuffer:delta inputCoefficientsPixelBuffer:coeff outputUnstyledPixelBuffer:*output];
    Check(status==0,[NSString stringWithFormat:@"Native inverse failed: %d",status]);return status;
}

static int Collect(NSString*photo,NSString*movie,NSString*out,size_t w){
    NSError*e=nil;Check([[NSFileManager defaultManager]createDirectoryAtPath:out withIntermediateDirectories:NO attributes:nil error:&e],e.description?:@"Output exists");
    AVAsset*a=[AVURLAsset URLAssetWithURL:[NSURL fileURLWithPath:movie] options:nil];AVAssetTrack*main=[a tracksWithMediaType:AVMediaTypeVideo].firstObject,*delta=nil,*log=nil;
    Check(main!=nil,@"No primary video");CMVideoDimensions dim=Dim(main);NSDictionary *clean=Ext(main)[@"CVCleanAperture"];
    size_t cw=clean? [clean[@"Width"]unsignedIntegerValue]:dim.width,ch=clean?[clean[@"Height"]unsignedIntegerValue]:dim.height;
    CGRect crop=CMVideoFormatDescriptionGetCleanAperture((__bridge CMVideoFormatDescriptionRef)main.formatDescriptions.firstObject,NO);size_t h=llround((double)w*ch/cw);
    Check(crop.size.width==cw&&crop.size.height==ch,@"Clean aperture geometry mismatch");
    NSMutableArray*tracks=[NSMutableArray new],*styles=[NSMutableArray new],*otherMetadata=[NSMutableArray new];CMTime still=kCMTimeInvalid;
    for(AVAssetTrack*t in a.tracks){
        [tracks addObject:@{@"id":@(t.trackID),@"type":t.mediaType,@"format":Safe(Ext(t)),@"transform":@[@(t.preferredTransform.a),@(t.preferredTransform.b),@(t.preferredTransform.c),@(t.preferredTransform.d),@(t.preferredTransform.tx),@(t.preferredTransform.ty)]}];
        if([t.mediaType isEqualToString:AVMediaTypeAuxiliaryPicture]){
            NSDictionary*x=Ext(t);if([x[@"LogTransferFunction"]containsString:@"apple-log"])log=t;
            else if([x[@"CVImageBufferTransferFunction"]isEqualToString:@"Linear"]&&Dim(t).width==dim.width)delta=t;
        }
        if(![t.mediaType isEqualToString:AVMediaTypeMetadata])continue;
        AVAssetReader*r;AVAssetReaderTrackOutput*o=Reader(a,t,NO,&r);AVAssetReaderOutputMetadataAdaptor*ad=[[AVAssetReaderOutputMetadataAdaptor alloc]initWithAssetReaderTrackOutput:o];AVTimedMetadataGroup*g;Check([r startReading],r.error.description);
        while((g=[ad nextTimedMetadataGroup]))for(AVMetadataItem*item in g.items){
            NSString*name=item.identifier?:@"";NSMutableDictionary*m=[@{@"id":name,@"pts":T(g.timeRange.start),@"duration":T(g.timeRange.duration),@"value":Safe(item.value)}mutableCopy];
            if([name hasSuffix:@"smartstyle-info"]&&[item.value isKindOfClass:NSData.class]){
                NSString*file=[NSString stringWithFormat:@"style-%04lu.plist",(unsigned long)styles.count];[(NSData*)item.value writeToFile:P(out,file) atomically:YES];
                m[@"file"]=file;NSDictionary*d=[NSPropertyListSerialization propertyListWithData:(NSData*)item.value options:0 format:NULL error:&e];m[@"stored"]=Safe(d);
                id props=[NSClassFromString(@"_NUSemanticStyleProperties")semanticStylePropertiesFromData:(NSData*)item.value fromVideo:YES keyTime:g.timeRange.start error:&e];Check(props!=nil,e.description?:@"Native metadata parse failed");
                NSMutableDictionary*named=[NSMutableDictionary new];for(NSString*k in @[@"version",@"baseGain",@"baselineExposure",@"linearGain",@"linearHighKey",@"linearRangeMin",@"linearRangeMax",@"lightMapWidth",@"lightMapHeight"]){named[k]=Safe([props valueForKey:k]);}m[@"native"]=named;[styles addObject:m];
            }else{
                if([name hasSuffix:@"still-image-time"])still=g.timeRange.start;
                [otherMetadata addObject:m];
            }
        }
        Check(r.status!=AVAssetReaderStatusFailed,r.error.description);[r cancelReading];
    }
    Check(delta&&log&&styles.count&&CMTIME_IS_VALID(still),@"Input lacks required native style resources or still-time");
    NSMutableArray *frames=[NSMutableArray new],*thumbs=[NSMutableArray new];NSDictionary*config=nil;CVPixelBufferRef coefficients=NULL;id utility=Utility(&coefficients,&config);
    AVAssetReader*r,*dr;AVAssetReaderTrackOutput*o=Reader(a,main,YES,&r),*dout=Reader(a,delta,YES,&dr);CMSampleBufferRef sb;size_t index=0;
    while((sb=[o copyNextSampleBuffer])){@autoreleasepool{
        CMSampleBufferRef db=[dout copyNextSampleBuffer];CMTime pts=CMSampleBufferGetPresentationTimeStamp(sb);
        Check(db&&CMTimeCompare(pts,CMSampleBufferGetPresentationTimeStamp(db))==0,@"Delta PTS mismatch");
        NSDictionary*m=nil;for(NSDictionary*s in styles)if(CMTimeCompare(pts,CT(s[@"pts"]))==0){m=s;break;}Check(m!=nil,@"No exact per-frame style PTS");
        NSDictionary*style=[NSPropertyListSerialization propertyListWithData:[NSData dataWithContentsOfFile:P(out,m[@"file"])] options:0 format:NULL error:NULL];
        CVPixelBufferRef source=CMSampleBufferGetImageBuffer(sb),neutral=NULL;int status=Reverse(utility,coefficients,style,source,CMSampleBufferGetImageBuffer(db),&neutral);
        CIImage*si=[CIImage imageWithCVPixelBuffer:source];
        CIImage*ui=[CIImage imageWithCVPixelBuffer:neutral options:si.colorSpace?@{kCIImageColorSpace:(__bridge id)si.colorSpace}:@{}];
        NSData*sp=Pixels(Fit(si,crop,w,h),Context,Linear,w,h),*up=Pixels(Fit(ui,crop,w,h),Context,Linear,w,h);
        NSString*sf=[NSString stringWithFormat:@"styled-%04zu.f32",index],*uf=[NSString stringWithFormat:@"neutral-%04zu.f32",index];
        [sp writeToFile:P(out,sf) atomically:YES];[up writeToFile:P(out,uf) atomically:YES];
        [frames addObject:@{@"index":@(index),@"pts":T(pts),@"duration":T(CMSampleBufferGetDuration(sb)),@"styled":sf,@"neutral":uf,@"style":m,@"reverseStatus":@(status),@"styledStats":Stats(sp),@"neutralStats":Stats(up),@"inputColorSpace":si.colorSpace?Safe(CFBridgingRelease(CGColorSpaceCopyName(si.colorSpace))):@"none"}];
        CFRelease(neutral);CFRelease(sb);CFRelease(db);index++;
    }}
    Check(r.status==AVAssetReaderStatusCompleted&&dr.status!=AVAssetReaderStatusFailed,@"Video decode incomplete");
    [dr cancelReading];CFRelease(coefficients);
    AVAssetReader*lr;AVAssetReaderTrackOutput*lo=Reader(a,log,YES,&lr);index=0;
    while((sb=[lo copyNextSampleBuffer])){@autoreleasepool{
        CVPixelBufferRef pb=CMSampleBufferGetImageBuffer(sb);size_t tw=CVPixelBufferGetWidth(pb),th=CVPixelBufferGetHeight(pb);
        NSData*pixels=Pixels(DecodeLog(pb),Context,Linear,tw,th);NSString*file=[NSString stringWithFormat:@"scene-%04zu.f32",index++];[pixels writeToFile:P(out,file) atomically:YES];
        [thumbs addObject:@{@"pts":T(CMSampleBufferGetPresentationTimeStamp(sb)),@"width":@(tw),@"height":@(th),@"file":file,@"stats":Stats(pixels)}];CFRelease(sb);
    }}Check(lr.status==AVAssetReaderStatusCompleted,@"Thumbnail decode incomplete");
    CIImage*sd=[CIImage imageWithContentsOfURL:[NSURL fileURLWithPath:photo] options:@{kCIImageApplyOrientationProperty:@NO,kCIImageExpandToHDR:@NO}];
    CIImage*hd=[CIImage imageWithContentsOfURL:[NSURL fileURLWithPath:photo] options:@{kCIImageApplyOrientationProperty:@NO,kCIImageExpandToHDR:@YES}];Check(sd&&hd,@"Cannot decode paired HEIC");Check(hd.contentHeadroom>1,@"Paired HEIC has no native HDR look reference");
    NSData*ps=Pixels(Fit(sd,sd.extent,w,h),Context,Linear,w,h),*ph=Pixels(Fit(hd,hd.extent,w,h),Context,Linear,w,h);
    [ps writeToFile:P(out,@"photo-sdr.f32")atomically:YES];[ph writeToFile:P(out,@"photo-hdr.f32")atomically:YES];
    JSON(@{@"schema":@"native-style-hdr-independent-collection-v1",@"photo":photo,@"movie":movie,@"gpu":Device.name,@"os":NSProcessInfo.processInfo.operatingSystemVersionString,@"width":@(w),@"height":@(h),@"codedWidth":@(dim.width),@"codedHeight":@(dim.height),@"cleanWidth":@(cw),@"cleanHeight":@(ch),@"crop":@[@(crop.origin.x),@(crop.origin.y),@(cw),@(ch)],@"stillTime":T(still),@"headroom":@(hd.contentHeadroom),@"utilityConfiguration":config,@"tracks":tracks,@"frames":frames,@"thumbnails":thumbs,@"otherMetadata":otherMetadata,@"photoSDR":Stats(ps),@"photoHDR":Stats(ph)},P(out,@"collection.json"));
    printf("collected %lu main frames, %lu scene thumbnails, %zux%zu; native inverse passed\n",(unsigned long)frames.count,(unsigned long)thumbs.count,w,h);return 0;
}

static int Flow(NSString*from,NSString*to,NSString*out,size_t w,size_t h,BOOL homography){
    CGColorSpaceRef srgb=CGColorSpaceCreateWithName(kCGColorSpaceSRGB);CVPixelBufferRef a=Buffer(w,h,kCVPixelFormatType_32BGRA),b=Buffer(w,h,kCVPixelFormatType_32BGRA);
    [Context render:FloatImage(from,w,h,Linear)toCVPixelBuffer:a bounds:CGRectMake(0,0,w,h)colorSpace:srgb];
    [Context render:FloatImage(to,w,h,Linear)toCVPixelBuffer:b bounds:CGRectMake(0,0,w,h)colorSpace:srgb];
    if(homography){
        VNHomographicImageRegistrationRequest*request=[[VNHomographicImageRegistrationRequest alloc]initWithTargetedCVPixelBuffer:b options:@{}];
        VNImageRequestHandler*handler=[[VNImageRequestHandler alloc]initWithCVPixelBuffer:a options:@{}];NSError*e=nil;
        BOOL ok=[handler performRequests:@[request]error:&e];VNImageHomographicAlignmentObservation*obs=request.results.firstObject;
        NSMutableArray*matrix=[NSMutableArray new];if(obs)for(int row=0;row<3;row++)[matrix addObject:@[@(obs.warpTransform.columns[0][row]),@(obs.warpTransform.columns[1][row]),@(obs.warpTransform.columns[2][row])]];
        JSON(@{@"success":@(ok&&obs),@"matrix":matrix,@"confidence":obs?@(obs.confidence):@0,@"error":e.description?:@""},out);CFRelease(a);CFRelease(b);CGColorSpaceRelease(srgb);return ok&&obs?0:1;
    }
    VNGenerateOpticalFlowRequest*req=[[VNGenerateOpticalFlowRequest alloc]initWithTargetedCVPixelBuffer:b options:@{}];req.revision=VNGenerateOpticalFlowRequestRevision1;req.computationAccuracy=VNGenerateOpticalFlowRequestComputationAccuracyHigh;req.outputPixelFormat=kCVPixelFormatType_TwoComponent32Float;
    VNImageRequestHandler*handler=[[VNImageRequestHandler alloc]initWithCVPixelBuffer:a options:@{}];NSError*e=nil;Check([handler performRequests:@[req]error:&e],e.description?:@"Optical flow failed");
    CVPixelBufferRef f=req.results.firstObject.pixelBuffer;Check(f&&CVPixelBufferGetWidth(f)==w&&CVPixelBufferGetHeight(f)==h,@"Optical flow extent mismatch");CVPixelBufferLockBaseAddress(f,kCVPixelBufferLock_ReadOnly);
    NSMutableData*data=[NSMutableData dataWithLength:w*h*8];for(size_t y=0;y<h;y++)memcpy((char*)data.mutableBytes+y*w*8,(char*)CVPixelBufferGetBaseAddress(f)+y*CVPixelBufferGetBytesPerRow(f),w*8);
    CVPixelBufferUnlockBaseAddress(f,kCVPixelBufferLock_ReadOnly);Check([data writeToFile:out atomically:YES],@"Flow write failed");CFRelease(a);CFRelease(b);CGColorSpaceRelease(srgb);return 0;
}

static id<MTLTexture> Tex(size_t w,size_t h){
    MTLTextureDescriptor*d=[MTLTextureDescriptor texture2DDescriptorWithPixelFormat:MTLPixelFormatR16Float width:w height:h mipmapped:NO];d.storageMode=MTLStorageModeShared;d.usage=MTLTextureUsageShaderRead|MTLTextureUsageShaderWrite;
    id<MTLTexture>t=[Device newTextureWithDescriptor:d];Check(t!=nil,@"Metal texture allocation failed");return t;
}
static void Upload(id<MTLTexture>t,const float*p){size_t n=t.width*t.height;NSMutableData*d=[NSMutableData dataWithLength:n*2];__fp16*h=d.mutableBytes;for(size_t i=0;i<n;i++)h[i]=p[i];[t replaceRegion:MTLRegionMake2D(0,0,t.width,t.height)mipmapLevel:0 withBytes:h bytesPerRow:t.width*2];}
static NSData *Download(id<MTLTexture>t){NSMutableData*d=[NSMutableData dataWithLength:t.width*t.height*2];[t getBytes:d.mutableBytes bytesPerRow:t.width*2 fromRegion:MTLRegionMake2D(0,0,t.width,t.height)mipmapLevel:0];return d;}
static float Lookup(const float*curve,size_t n,float x){x=fminf(fmaxf(x,0),1)*(n-1);size_t a=floorf(x),b=MIN(a+1,n-1);return curve[a]*(b-x)+curve[b]*(x-a)+(a==b?curve[a]:0);}
static int Render(NSString*collection,NSString*model,NSString*movie,NSString*out,NSInteger only){
    Check(![[NSFileManager defaultManager]fileExistsAtPath:out],@"Output path already exists");
    NSDictionary*source=LoadJSON(P(collection,@"collection.json")),*plan=LoadJSON(P(model,@"model.json"));Check(source&&plan,@"Missing collection or model manifest");
    size_t w=[source[@"cleanWidth"]unsignedIntegerValue],h=[source[@"cleanHeight"]unsignedIntegerValue],pw=[source[@"width"]unsignedIntegerValue],ph=[source[@"height"]unsignedIntegerValue];
    size_t gw=(w+1)/2,gh=(h+1)/2,mw=[plan[@"mapWidth"]unsignedIntegerValue],mh=[plan[@"mapHeight"]unsignedIntegerValue];
    NSArray*c=source[@"crop"];CGRect crop=CGRectMake([c[0]doubleValue],[c[1]doubleValue],[c[2]doubleValue],[c[3]doubleValue]);
    NSDictionary*utilityConfig;CVPixelBufferRef coeff=NULL;id utility=Utility(&coeff,&utilityConfig);
    BOOL neutralIsLinear=[utilityConfig[@"outputShouldBeLinear"]boolValue];
    id allocator=[(id)[NSClassFromString(@"FigMetalAllocator")alloc]initWithDevice:Device allocatorType:2];id desc=[NSClassFromString(@"FigMetalAllocatorDescriptor")new];[desc setMemSize:384ULL*1024*1024];[desc setResourceOptions:MTLResourceStorageModePrivate];Check([allocator setupWithDescriptor:desc]==0,@"Guided-filter allocator setup failed");
    id filter=[(id)[NSClassFromString(@"CMIGuidedFilter")alloc]initWithOptionalCommandQueue:Queue allocator:allocator];Check(filter!=nil,@"Native guided filter unavailable");
    id<MTLTexture>map=Tex(mw,mh),guide=Tex(gw,gh),result=Tex(gw,gh);
    AVAsset*a=[AVURLAsset URLAssetWithURL:[NSURL fileURLWithPath:movie]options:nil];AVAssetTrack*main=[a tracksWithMediaType:AVMediaTypeVideo].firstObject,*delta=nil;
    for(AVAssetTrack*t in [a tracksWithMediaType:AVMediaTypeAuxiliaryPicture])if([Ext(t)[@"CVImageBufferTransferFunction"]isEqualToString:@"Linear"]&&Dim(t).width==Dim(main).width)delta=t;Check(delta!=nil,@"Missing delta track");
    CGColorSpaceRef hlg=CGColorSpaceCreateWithName(kCGColorSpaceITUR_2100_HLG);Check(hlg!=NULL,@"HLG profile unavailable");
    NSData*clli=[NSData dataWithBytes:(uint8_t[]){0,0,0,0}length:4];
    NSDictionary*settings=@{AVVideoCodecKey:AVVideoCodecTypeHEVC,AVVideoWidthKey:@(w),AVVideoHeightKey:@(h),AVVideoColorPropertiesKey:@{AVVideoColorPrimariesKey:AVVideoColorPrimaries_ITU_R_2020,AVVideoTransferFunctionKey:AVVideoTransferFunction_ITU_R_2100_HLG,AVVideoYCbCrMatrixKey:AVVideoYCbCrMatrix_ITU_R_2020},AVVideoCompressionPropertiesKey:@{AVVideoAverageBitRateKey:@35000000,AVVideoProfileLevelKey:(__bridge id)kVTProfileLevel_HEVC_Main10_AutoLevel,AVVideoAllowFrameReorderingKey:@NO,(__bridge NSString*)kVTCompressionPropertyKey_ContentLightLevelInfo:clli}};
    NSError*error=nil;AVAssetWriter*writer=[[AVAssetWriter alloc]initWithURL:[NSURL fileURLWithPath:out]fileType:AVFileTypeQuickTimeMovie error:&error];Check(writer!=nil,error.description);
    AVAssetWriterInput*input=[[AVAssetWriterInput alloc]initWithMediaType:AVMediaTypeVideo outputSettings:settings];
    CGAffineTransform transform=main.preferredTransform;transform.tx=0;transform.ty=0;CGRect rotated=CGRectApplyAffineTransform(CGRectMake(0,0,w,h),transform);transform.tx=-rotated.origin.x;transform.ty=-rotated.origin.y;input.transform=transform;
    input.expectsMediaDataInRealTime=NO;AVAssetWriterInputPixelBufferAdaptor*adaptor=[[AVAssetWriterInputPixelBufferAdaptor alloc]initWithAssetWriterInput:input sourcePixelBufferAttributes:@{(id)kCVPixelBufferPixelFormatTypeKey:@(kCVPixelFormatType_420YpCbCr10BiPlanarVideoRange),(id)kCVPixelBufferWidthKey:@(w),(id)kCVPixelBufferHeightKey:@(h),(id)kCVPixelBufferIOSurfacePropertiesKey:@{}}];
    [writer addInput:input];Check([writer startWriting],writer.error.description);[writer startSessionAtSourceTime:kCMTimeZero];
    CIColorKernel*kernel=[CIColorKernel kernelWithString:@"kernel vec4 hdr(__sample s,__sample g,float cap){return vec4(min(s.rgb*exp2(g.rgb),vec3(cap)),s.a);}"];Check(kernel!=nil,@"HDR kernel compile failed");
    AVAssetReader*r,*dr;AVAssetReaderTrackOutput*ro=Reader(a,main,YES,&r),*dout=Reader(a,delta,YES,&dr);NSMutableArray*facts=[NSMutableArray new];CMSampleBufferRef sb;size_t index=0;
    NSString*previewDir=[out stringByAppendingString:@".pixels"];Check([[NSFileManager defaultManager]createDirectoryAtPath:previewDir withIntermediateDirectories:NO attributes:nil error:&error],error.description);
    while((sb=[ro copyNextSampleBuffer])){@autoreleasepool{
        CMSampleBufferRef db=[dout copyNextSampleBuffer];CMTime pts=CMSampleBufferGetPresentationTimeStamp(sb);Check(db&&CMTimeCompare(pts,CMSampleBufferGetPresentationTimeStamp(db))==0,@"Delta PTS mismatch during render");
        if(only>=0&&index!=(size_t)only){CFRelease(sb);CFRelease(db);index++;continue;}
        NSDictionary*f=source[@"frames"][index];Check(CMTimeCompare(pts,CT(f[@"pts"]))==0,@"Model frame PTS mismatch");
        NSData*plist=[NSData dataWithContentsOfFile:P(collection,f[@"style"][@"file"])];NSDictionary*meta=[NSPropertyListSerialization propertyListWithData:plist options:0 format:NULL error:NULL];
        CVPixelBufferRef neutral=NULL,src=CMSampleBufferGetImageBuffer(sb);int rs=Reverse(utility,coeff,meta,src,CMSampleBufferGetImageBuffer(db),&neutral);
        CIImage*si=[CIImage imageWithCVPixelBuffer:src];CGColorSpaceRef ncs=neutralIsLinear?Linear:si.colorSpace;
        CIImage*ui=[CIImage imageWithCVPixelBuffer:neutral options:ncs?@{kCIImageColorSpace:(__bridge id)ncs}:@{}];
        NSData*small=Pixels(Fit(ui,crop,gw,gh),Context,Linear,gw,gh);const float*up=small.bytes;NSMutableData*gd=[NSMutableData dataWithLength:gw*gh*4];float*gp=gd.mutableBytes;
        id props=[NSClassFromString(@"_NUSemanticStyleProperties")semanticStylePropertiesFromData:plist fromVideo:YES keyTime:pts error:&error];Check(props!=nil,error.description?:@"Metadata parse failed during render");
        NSData*curveData=[props valueForKey:@"globalToneCurveData"];size_t cn=curveData.length/4;const float*cv=curveData.bytes;
        double scale=[[props valueForKey:@"baseGain"]doubleValue]*[[props valueForKey:@"baselineExposure"]doubleValue];Check(cn==256&&scale>0,@"Native GTC metadata layout unsupported");
        for(size_t i=0;i<gw*gh;i++)gp[i]=.299f*Lookup(cv,cn,up[4*i]*scale)+.587f*Lookup(cv,cn,up[4*i+1]*scale)+.114f*Lookup(cv,cn,up[4*i+2]*scale);
        Upload(guide,gp);NSData*maps=[NSData dataWithContentsOfFile:P(model,[NSString stringWithFormat:@"gain-%04zu.f32",index])];Check(maps.length==mw*mh*12,@"Gain map size mismatch");const float*mp=maps.bytes;
        NSMutableData*rgb=[NSMutableData dataWithLength:gw*gh*16],*channel=[NSMutableData dataWithLength:mw*mh*4];float*rgbp=rgb.mutableBytes,*cp=channel.mutableBytes;int statuses[3];
        for(size_t k=0;k<3;k++){
            for(size_t i=0;i<mw*mh;i++)cp[i]=mp[3*i+k];Upload(map,cp);id<MTLCommandBuffer>command=[Queue commandBuffer];
            statuses[k]=[filter encodeToCommandBuffer:command inputTexture:map guideTexture:guide outputTexture:result kernelRadius:1 epsilon:.05f];[command commit];[command waitUntilCompleted];Check(statuses[k]==0&&!command.error,@"Native guided upsample failed");
            NSData*half=Download(result);const __fp16*hp=half.bytes;for(size_t i=0;i<gw*gh;i++)rgbp[4*i+k]=hp[i];
        }
        for(size_t i=0;i<gw*gh;i++)rgbp[4*i+3]=1;
        CIImage*gain=[CIImage imageWithBitmapData:rgb bytesPerRow:gw*16 size:CGSizeMake(gw,gh)format:kCIFormatRGBAf colorSpace:nil];gain=Fit(gain,gain.extent,w,h);
        CIImage*styled=Fit(si,crop,w,h);CIImage*scene=[kernel applyWithExtent:CGRectMake(0,0,w,h)arguments:@[styled,gain,plan[@"linearPeakCap"]]];Check(scene!=nil,@"HDR scene assembly failed");
        NSData*prediction=Pixels(Fit(scene,scene.extent,pw,ph),Context,Linear,pw,ph);NSString*name=[NSString stringWithFormat:@"hdr-%04zu.f32",index];[prediction writeToFile:P(previewDir,name)atomically:YES];
        CVPixelBufferRef encoded=Buffer(w,h,kCVPixelFormatType_420YpCbCr10BiPlanarVideoRange);[Context render:scene toCVPixelBuffer:encoded bounds:CGRectMake(0,0,w,h)colorSpace:hlg];
        CVBufferSetAttachment(encoded,kCVImageBufferColorPrimariesKey,kCVImageBufferColorPrimaries_ITU_R_2020,kCVAttachmentMode_ShouldPropagate);CVBufferSetAttachment(encoded,kCVImageBufferTransferFunctionKey,kCVImageBufferTransferFunction_ITU_R_2100_HLG,kCVAttachmentMode_ShouldPropagate);CVBufferSetAttachment(encoded,kCVImageBufferYCbCrMatrixKey,kCVImageBufferYCbCrMatrix_ITU_R_2020,kCVAttachmentMode_ShouldPropagate);
        if([plan[@"ambientViewingEnvironmentHex"]isKindOfClass:NSString.class]){
            NSString*hex=plan[@"ambientViewingEnvironmentHex"];Check(hex.length==16,@"Invalid ambient metadata length");uint8_t bytes[8];for(int j=0;j<8;j++){unsigned value=0;[[NSScanner scannerWithString:[hex substringWithRange:NSMakeRange(j*2,2)]]scanHexInt:&value];bytes[j]=value;}
            NSData*ambient=[NSData dataWithBytes:bytes length:8];CVBufferSetAttachment(encoded,kCVImageBufferAmbientViewingEnvironmentKey,(__bridge CFDataRef)ambient,kCVAttachmentMode_ShouldPropagate);
        }
        while(!input.readyForMoreMediaData){Check(writer.status==AVAssetWriterStatusWriting,writer.error.description);usleep(1000);}
        Check([adaptor appendPixelBuffer:encoded withPresentationTime:pts],writer.error.description);
        [facts addObject:@{@"index":@(index),@"pts":T(pts),@"reverseStatus":@(rs),@"guidedStatuses":@[@(statuses[0]),@(statuses[1]),@(statuses[2])],@"linearStats":Stats(prediction),@"gtcPoints":@(cn),@"guideScale":@(scale)}];
        fprintf(stderr,"render %zu pts %.6f inverse %d guided %d/%d/%d\n",index,CMTimeGetSeconds(pts),rs,statuses[0],statuses[1],statuses[2]);
        CFRelease(encoded);CFRelease(neutral);CFRelease(sb);CFRelease(db);index++;
    }}
    Check(r.status==AVAssetReaderStatusCompleted,@"Primary decode incomplete during render");[dr cancelReading];
    if(only<0)[writer endSessionAtSourceTime:main.timeRange.duration];[input markAsFinished];dispatch_semaphore_t sem=dispatch_semaphore_create(0);[writer finishWritingWithCompletionHandler:^{dispatch_semaphore_signal(sem);}];Check(dispatch_semaphore_wait(sem,dispatch_time(DISPATCH_TIME_NOW,55*NSEC_PER_SEC))==0,@"Writer timed out");Check(writer.status==AVAssetWriterStatusCompleted,writer.error.description);
    JSON(@{@"schema":@"native-dynamic-hdr-render-v1",@"gpu":Device.name,@"width":@(w),@"height":@(h),@"model":model,@"onlyFrame":@(only),@"frames":facts,@"utilityConfiguration":utilityConfig,@"guideWidth":@(gw),@"guideHeight":@(gh),@"transfer":@"HLG",@"referenceWhite":@"Core Image native HLG profile; no pre-exposure rescale",@"contentLightLevelInfo":@"unknown (0,0)",@"ambientMetadataSource":plan[@"ambientMetadataSource"]?:@"absent"},[out stringByAppendingString:@".json"]);
    CFRelease(coeff);CGColorSpaceRelease(hlg);return 0;
}

static int Audit(NSString*movie,NSString*out,size_t w){
    NSError*e=nil;Check([[NSFileManager defaultManager]createDirectoryAtPath:out withIntermediateDirectories:NO attributes:nil error:&e],e.description);
    AVAsset*a=[AVURLAsset URLAssetWithURL:[NSURL fileURLWithPath:movie]options:nil];AVAssetTrack*t=[a tracksWithMediaType:AVMediaTypeVideo].firstObject;Check(t!=nil,@"No primary video for audit");
    CMVideoDimensions dim=Dim(t);size_t h=llround((double)w*dim.height/dim.width);AVAssetReader*r;AVAssetReaderTrackOutput*ro=Reader(a,t,YES,&r);CMSampleBufferRef sb;NSMutableArray*frames=[NSMutableArray new];size_t n=0;
    while((sb=[ro copyNextSampleBuffer])){@autoreleasepool{
        CIImage*im=[CIImage imageWithCVPixelBuffer:CMSampleBufferGetImageBuffer(sb)];NSData*d=Pixels(Fit(im,im.extent,w,h),Context,Linear,w,h);NSString*file=[NSString stringWithFormat:@"decoded-%04zu.f32",n++];[d writeToFile:P(out,file)atomically:YES];
        [frames addObject:@{@"pts":T(CMSampleBufferGetPresentationTimeStamp(sb)),@"file":file,@"stats":Stats(d)}];CFRelease(sb);
    }}Check(r.status==AVAssetReaderStatusCompleted,@"Native decoding audit incomplete");
    JSON(@{@"schema":@"native-encoded-hdr-audit-v1",@"movie":movie,@"frames":frames,@"width":@(w),@"height":@(h),@"mainFormat":Safe(Ext(t)),@"containsHDRVideo":@([t hasMediaCharacteristic:AVMediaCharacteristicContainsHDRVideo]),@"assetMetadata":Safe([a.metadata valueForKey:@"value"])},P(out,@"audit.json"));return 0;
}

int main(int argc,char**argv){@autoreleasepool{
    if(argc<2)return 2;Setup();NSString*op=@(argv[1]);
    if([op isEqualToString:@"collect"]&&argc==6)return Collect(@(argv[2]),@(argv[3]),@(argv[4]),strtoul(argv[5],NULL,10));
    if(([op isEqualToString:@"flow"]||[op isEqualToString:@"homography"])&&argc==7)return Flow(@(argv[2]),@(argv[3]),@(argv[4]),strtoul(argv[5],NULL,10),strtoul(argv[6],NULL,10),[op isEqualToString:@"homography"]);
    if([op isEqualToString:@"render"]&&(argc==6||argc==7))return Render(@(argv[2]),@(argv[3]),@(argv[4]),@(argv[5]),argc==7?strtol(argv[6],NULL,10):-1);
    if([op isEqualToString:@"audit"]&&argc==5)return Audit(@(argv[2]),@(argv[3]),strtoul(argv[4],NULL,10));
    fprintf(stderr,"native collect HEIC MOV NEW_DIRECTORY WIDTH\nnative flow FROM.f32 TO.f32 OUT.f32 WIDTH HEIGHT\n");return 2;
}}
