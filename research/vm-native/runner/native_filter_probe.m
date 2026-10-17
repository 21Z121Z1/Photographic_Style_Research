#import <Foundation/Foundation.h>
#import <CoreImage/CoreImage.h>
#import <CoreMedia/CoreMedia.h>
#import <ImageIO/ImageIO.h>
#import <Metal/Metal.h>
#import <objc/runtime.h>
#import <dlfcn.h>

@interface NSObject (XDToneProbe)
+ (id)semanticStylePropertiesFromData:(NSData *)data fromVideo:(BOOL)video keyTime:(CMTime)time error:(NSError **)error;
- (CIImage *)curveImageWithData:(NSData *)data;
- (CIImage *)_lightMapImageWithData:(NSData *)data;
- (id)gtcKernel;
@end

static NSMutableArray *Calls;
static id GTC;
static id (*OriginalColorApply)(id,SEL,CGRect,id);
static id (*OriginalApply)(id,SEL,CGRect,id,id);
static NSString *Extent(CGRect r) { return NSStringFromRect(NSRectFromCGRect(r)); }
static id Describe(id value) {
    if([value isKindOfClass:CIImage.class]) return @{@"class":NSStringFromClass([value class]),@"extent":Extent([value extent]),@"colour_space":((CIImage *)value).colorSpace ? (__bridge id)CGColorSpaceCopyName(((CIImage *)value).colorSpace) : @"none"};
    if([value isKindOfClass:NSData.class]) return @{@"bytes":@([value length])};
    if([value isKindOfClass:NSNumber.class] || [value isKindOfClass:NSString.class] || [value isKindOfClass:NSNull.class]) return value;
    return [value description] ?: @"nil";
}
static void Capture(id kernel,NSString *kind,CGRect extent,NSArray *args) {
    if(kernel!=GTC) return;
    NSMutableArray *description=[NSMutableArray new];for(id a in args) [description addObject:Describe(a)];
    [Calls addObject:@{@"kind":kind,@"extent":Extent(extent),@"arguments":description}];
}
static id ColorApply(id self,SEL sel,CGRect r,id args) { Capture(self,@"color",r,args);return OriginalColorApply(self,sel,r,args); }
static id Apply(id self,SEL sel,CGRect r,id roi,id args) { Capture(self,@"general",r,args);return OriginalApply(self,sel,r,roi,args); }
static void AssertionToException(id self,SEL sel,id assertion) {
    NSString *reason=[assertion description] ?: @"Native assertion";
    fprintf(stderr,"NATIVE ASSERTION: %s\n",reason.UTF8String);
    @throw [NSException exceptionWithName:@"XDToneNativeAssertion" reason:reason userInfo:nil];
}

static NSDictionary *Render(CIImage *image,CIContext *context,CGColorSpaceRef space,NSString *path) {
    if(!image) return @{@"nil":@YES};
    CGRect r=image.extent;
    if(CGRectIsInfinite(r)||CGRectIsEmpty(r)) return @{@"invalid_extent":Extent(r)};
    NSUInteger w=llround(r.size.width),h=llround(r.size.height);
    if(w*h>2000000) @throw [NSException exceptionWithName:@"capture-too-large" reason:Extent(r) userInfo:nil];
    NSMutableData *data=[NSMutableData dataWithLength:w*h*16];
    [context render:image toBitmap:data.mutableBytes rowBytes:w*16 bounds:r format:kCIFormatRGBAf colorSpace:space];
    const float *p=data.bytes;double sum=0;float lo=INFINITY,hi=-INFINITY;NSUInteger nonfinite=0;
    for(NSUInteger i=0;i<w*h;i++)for(int c=0;c<3;c++) { float v=p[i*4+c];if(!isfinite(v))nonfinite++;else{lo=fminf(lo,v);hi=fmaxf(hi,v);sum+=v;} }
    NSError *error=nil;if(![data writeToFile:path options:NSDataWritingAtomic error:&error]) @throw [NSException exceptionWithName:@"write" reason:error.description userInfo:nil];
    NSDictionary *layout=@{@"shape":@[@(h),@(w),@4],@"dtype":@"<f4",@"colour_space":space?(__bridge id)CGColorSpaceCopyName(space):@"unmanaged"};
    [[NSJSONSerialization dataWithJSONObject:layout options:NSJSONWritingPrettyPrinted error:NULL]writeToFile:[path stringByAppendingString:@".json"] atomically:YES];
    return @{@"width":@(w),@"height":@(h),@"minimum":@(lo),@"maximum":@(hi),@"mean":@(sum/(w*h*3)),@"nonfinite":@(nonfinite)};
}

int main(int argc,char **argv) {
 @autoreleasepool {
    if(argc!=4) {fprintf(stderr,"source.heic resource-directory new-output-directory\n");return 2;}
    NSString *source=@(argv[1]),*resources=@(argv[2]),*out=@(argv[3]);
    NSError *error=nil;
    if(![[NSFileManager defaultManager]createDirectoryAtPath:out withIntermediateDirectories:NO attributes:nil error:&error]) {fprintf(stderr,"%s\n",error.description.UTF8String);return 3;}
    NSMutableDictionary *facts=[NSMutableDictionary new];
    @try {
        dlopen("/System/Library/PrivateFrameworks/NeutrinoCore.framework/NeutrinoCore",RTLD_NOW|RTLD_LOCAL);
        dlopen("/System/Library/PrivateFrameworks/PhotoImaging.framework/PhotoImaging",RTLD_NOW|RTLD_LOCAL);
        // Keep unmet private preconditions visible and contained in this probe.
        Method assertionMethod=class_getInstanceMethod(NSClassFromString(@"NUAssertionPolicyAbort"),NSSelectorFromString(@"notifyAssertion:"));
        if(assertionMethod)method_setImplementation(assertionMethod,(IMP)AssertionToException);
        NSData *bytes=[NSData dataWithContentsOfFile:[resources stringByAppendingPathComponent:@"styles.plist"]];
        NSDictionary *stored=[NSPropertyListSerialization propertyListWithData:bytes options:0 format:NULL error:&error];
        id properties=[NSClassFromString(@"_NUSemanticStyleProperties") semanticStylePropertiesFromData:bytes fromVideo:NO keyTime:kCMTimeInvalid error:&error];
        if(!properties) @throw [NSException exceptionWithName:@"parse" reason:error.description userInfo:nil];
        CIFilter *filter=[NSClassFromString(@"PISemanticStyleFilter") new];
        if(!filter) return 4;
        [filter setDefaults];
        NSMutableDictionary *defaults=[NSMutableDictionary new];
        for(NSString *key in filter.inputKeys) {id value=[filter valueForKey:key];defaults[key]=value?Describe(value):@"nil";}
        facts[@"defaults"]=defaults;
        facts[@"attributes"]=[filter.attributes description];
        [filter setValue:stored[@"e"] forKey:@"inputLightMapWidth"];
        [filter setValue:stored[@"f"] forKey:@"inputLightMapHeight"];
        CIImage *curve=[(id)filter curveImageWithData:[properties valueForKey:@"globalToneCurveData"]];
        CIImage *light=[(id)filter _lightMapImageWithData:stored[@"c"]];
        CIImage *linearLight=[(id)filter _lightMapImageWithData:stored[@"d"]];
        id<MTLDevice> device=MTLCreateSystemDefaultDevice();
        if(!device) return 5;
        CIContext *unmanaged=[CIContext contextWithMTLDevice:device options:@{kCIContextWorkingColorSpace:NSNull.null,kCIContextOutputColorSpace:NSNull.null,kCIContextWorkingFormat:@(kCIFormatRGBAf)}];
        facts[@"native_curve_image"]=Render(curve,unmanaged,NULL,[out stringByAppendingPathComponent:@"curve.f32"]);
        facts[@"native_light_image"]=Render(light,unmanaged,NULL,[out stringByAppendingPathComponent:@"light.f32"]);
        facts[@"native_linear_light_image"]=Render(linearLight,unmanaged,NULL,[out stringByAppendingPathComponent:@"linear_light.f32"]);
        GTC=[(id)filter gtcKernel];Calls=[NSMutableArray new];
        facts[@"gtc_kernel"]=@{@"class":NSStringFromClass([GTC class]),@"description":[GTC description]?:@"nil"};
        Method m=class_getInstanceMethod(CIColorKernel.class,@selector(applyWithExtent:arguments:));
        OriginalColorApply=(void *)method_getImplementation(m);method_setImplementation(m,(IMP)ColorApply);
        m=class_getInstanceMethod(CIKernel.class,@selector(applyWithExtent:roiCallback:arguments:));
        OriginalApply=(void *)method_getImplementation(m);method_setImplementation(m,(IMP)Apply);
        CIImage *image=[CIImage imageWithContentsOfURL:[NSURL fileURLWithPath:source] options:@{kCIImageApplyOrientationProperty:@NO,kCIImageExpandToHDR:@NO}];
        NSString *primaryFloat=NSProcessInfo.processInfo.environment[@"XD_TONE_PRIMARY_F32"];
        if(primaryFloat) {
            NSUInteger width=[NSProcessInfo.processInfo.environment[@"XD_TONE_PRIMARY_WIDTH"] integerValue],height=[NSProcessInfo.processInfo.environment[@"XD_TONE_PRIMARY_HEIGHT"] integerValue];
            NSData *pixels=[NSData dataWithContentsOfFile:primaryFloat];
            if(!width||!height||pixels.length!=width*height*16) @throw [NSException exceptionWithName:@"pixels" reason:@"Invalid primary override geometry" userInfo:nil];
            CGColorSpaceRef cs=CGColorSpaceCreateWithName(kCGColorSpaceExtendedLinearDisplayP3);
            image=[CIImage imageWithBitmapData:pixels bytesPerRow:width*16 size:CGSizeMake(width,height) format:kCIFormatRGBAf colorSpace:cs];CGColorSpaceRelease(cs);
            facts[@"primary_float_source"]=primaryFloat;
        }
        double edge=[NSProcessInfo.processInfo.environment[@"XD_TONE_MAX_EDGE"] doubleValue];if(edge<=0)edge=512;
        double scale=fmin(1.,edge/fmax(image.extent.size.width,image.extent.size.height));
        image=[image imageByApplyingTransform:CGAffineTransformMakeScale(scale,scale)];
        CIImage *thumbnail=[CIImage imageWithContentsOfURL:[NSURL fileURLWithPath:[resources stringByAppendingPathComponent:@"linear.heic"]] options:@{kCIImageApplyOrientationProperty:@NO,kCIImageColorSpace:NSNull.null}];
        NSString *thumbMode=NSProcessInfo.processInfo.environment[@"XD_TONE_THUMB_MODE"] ?: @"stored-codes-control";
        if([thumbMode isEqualToString:@"native-stage-mirror"]) {
            thumbnail=[thumbnail imageByApplyingFilter:@"CIAppleLogToLinear"];
            double gain=[stored[@"i"][@"Gain"] doubleValue];
            thumbnail=[thumbnail imageByApplyingFilter:@"CIColorMatrix" withInputParameters:@{
                @"inputRVector":[CIVector vectorWithX:1/gain Y:0 Z:0 W:0],@"inputGVector":[CIVector vectorWithX:0 Y:1/gain Z:0 W:0],
                @"inputBVector":[CIVector vectorWithX:0 Y:0 Z:1/gain W:0],@"inputAVector":[CIVector vectorWithX:0 Y:0 Z:0 W:1],@"inputBiasVector":[CIVector vectorWithX:0 Y:0 Z:0 W:0]}];
            double lo=[stored[@"i"][@"OriginalRangeMin"] doubleValue],hi=[stored[@"i"][@"OriginalRangeMax"] doubleValue];
            thumbnail=[thumbnail imageByApplyingFilter:@"CIColorClamp" withInputParameters:@{
                @"inputMinComponents":[CIVector vectorWithX:lo Y:lo Z:lo W:0],@"inputMaxComponents":[CIVector vectorWithX:hi Y:hi Z:hi W:1]}];
            CGColorSpaceRef ltSpace=CGColorSpaceCreateWithName(kCGColorSpaceExtendedLinearDisplayP3);
            thumbnail=[thumbnail imageByColorMatchingColorSpaceToWorkingSpace:ltSpace];CGColorSpaceRelease(ltSpace);
        }
        NSString *thumbFloat=NSProcessInfo.processInfo.environment[@"XD_TONE_THUMB_F32"];
        if(thumbFloat) {
            NSUInteger width=[NSProcessInfo.processInfo.environment[@"XD_TONE_THUMB_WIDTH"] integerValue],height=[NSProcessInfo.processInfo.environment[@"XD_TONE_THUMB_HEIGHT"] integerValue];
            NSData *pixels=[NSData dataWithContentsOfFile:thumbFloat];
            if(!width||!height||pixels.length!=width*height*16) @throw [NSException exceptionWithName:@"pixels" reason:@"Invalid thumbnail override geometry" userInfo:nil];
            CGColorSpaceRef cs=CGColorSpaceCreateWithName(kCGColorSpaceExtendedLinearDisplayP3);
            thumbnail=[CIImage imageWithBitmapData:pixels bytesPerRow:width*16 size:CGSizeMake(width,height) format:kCIFormatRGBAf colorSpace:cs];CGColorSpaceRelease(cs);
            facts[@"thumbnail_float_source"]=thumbFloat;
        }
        facts[@"thumbnail_mode"]=thumbMode;
        [filter setValue:image forKey:kCIInputImageKey];
        [filter setValue:thumbnail forKey:@"inputLinearThumbnailImage"];
        [filter setValue:[properties valueForKey:@"globalToneCurveData"] forKey:@"inputTRCData"];
        NSString *trcControl=NSProcessInfo.processInfo.environment[@"XD_TONE_TRC_TABLE"];
        if(trcControl) {
            NSMutableData *table=[NSMutableData dataWithLength:256*4];float *q=table.mutableBytes;
            for(int i=0;i<256;i++){float v=(float)i/255;q[i]=[trcControl isEqualToString:@"square"]?v*v:v;}
            [filter setValue:table forKey:@"inputTRCData"];facts[@"trc_control"]=trcControl;
        }
        [filter setValue:stored[@"c"] forKey:@"inputLightMapData"];
        [filter setValue:stored[@"d"] forKey:@"inputLinearLightMapData"];
        [filter setValue:stored[@"6"] forKey:@"inputStatistics"];
        [filter setValue:stored[@"7"] forKey:@"inputExtendedStatistics"];
        [filter setValue:[properties valueForKey:@"baselineExposure"] forKey:@"inputBaselineExposure"];
        [filter setValue:[properties valueForKey:@"baseGain"] forKey:@"baseGain"];
        [filter setValue:[properties valueForKey:@"faceBasedGlobalExposureBoostRatio"] forKey:@"faceBasedGlobalExposureBoostRatio"];
        [filter setValue:[properties valueForKey:@"tuningType"] forKey:@"tuningType"];
        double tone=[NSProcessInfo.processInfo.environment[@"XD_TONE_BIAS"] doubleValue];
        [filter setValue:@(tone) forKey:@"inputToneBias"];facts[@"tone_bias"]=@(tone);
        NSString *matteDir=NSProcessInfo.processInfo.environment[@"XD_TONE_MATTE_DIR"];
        NSDictionary *mattes=@{@"inputSubjectMatteImage":@"tag_apple.com,2026_photo_aux_semanticpersonmatte.png",
            @"inputSkinMatteImage":@"urn_com_apple_photo_2019_aux_semanticskinmatte.png",
            @"inputSkyMatteImage":@"urn_com_apple_photo_2020_aux_semanticskymatte.png",
            @"inputGainMapImage":@"urn_com_apple_photo_2020_aux_hdrgainmap.png"};
        NSMutableDictionary *matteFacts=[NSMutableDictionary new];
        for(NSString *key in mattes) {
            NSString *file=[NSString stringWithFormat:@"%@-%@",source.lastPathComponent.stringByDeletingPathExtension,mattes[key]];
            NSString *path=[matteDir stringByAppendingPathComponent:file];
            CIImage *matte=matteDir?[CIImage imageWithContentsOfURL:[NSURL fileURLWithPath:path] options:@{kCIImageApplyOrientationProperty:@NO,kCIImageColorSpace:NSNull.null}]:nil;
            if(matte) {
                matte=[matte imageByApplyingTransform:CGAffineTransformMakeScale(image.extent.size.width/matte.extent.size.width,image.extent.size.height/matte.extent.size.height)];
                [filter setValue:matte forKey:key];matteFacts[key]=path;
            }
        }
        if([NSProcessInfo.processInfo.environment[@"XD_TONE_SYNTHETIC_AUX"] boolValue]) {
            CIImage *zero=[[CIImage imageWithColor:[CIColor colorWithRed:0 green:0 blue:0 alpha:1]]imageByCroppingToRect:image.extent];
            for(NSString *key in mattes)[filter setValue:zero forKey:key];
            facts[@"synthetic_auxiliary_control"]=@YES;
        }
        for(NSString *key in mattes) {
            NSString *path=[resources stringByAppendingPathComponent:[key stringByAppendingString:@".heic"]];
            CIImage *matte=[CIImage imageWithContentsOfURL:[NSURL fileURLWithPath:path] options:@{kCIImageApplyOrientationProperty:@NO,kCIImageColorSpace:NSNull.null}];
            if(!matte) matte=[[CIImage imageWithColor:[CIColor colorWithRed:0 green:0 blue:0 alpha:1]]imageByCroppingToRect:image.extent];
            else matte=[matte imageByApplyingTransform:CGAffineTransformMakeScale(image.extent.size.width/matte.extent.size.width,image.extent.size.height/matte.extent.size.height)];
            [filter setValue:matte forKey:key];matteFacts[key]=[[NSFileManager defaultManager]fileExistsAtPath:path]?path:@"missing-zero-control";
        }
        facts[@"matte_sources"]=matteFacts;
        [[NSJSONSerialization dataWithJSONObject:facts options:NSJSONWritingPrettyPrinted|NSJSONWritingSortedKeys error:NULL]
            writeToFile:[out stringByAppendingPathComponent:@"checkpoint.json"] atomically:YES];
        CGColorSpaceRef linear=CGColorSpaceCreateWithName(kCGColorSpaceExtendedLinearDisplayP3);
        CIContext *context=[CIContext contextWithMTLDevice:device options:@{kCIContextWorkingColorSpace:(__bridge id)linear,kCIContextOutputColorSpace:(__bridge id)linear,kCIContextWorkingFormat:@(kCIFormatRGBAf)}];
        facts[@"primary_input"]=Render(image,context,linear,[out stringByAppendingPathComponent:@"primary_input.f32"]);
        facts[@"thumbnail_input"]=Render(thumbnail,context,linear,[out stringByAppendingPathComponent:@"thumbnail_input.f32"]);
        NSMutableArray *trials=[NSMutableArray new];
        for(NSNumber *engine in @[@NO,@YES]) {
            @try {
                [filter setValue:engine forKey:@"useStyleEngine"];
                CIImage *result=filter.outputImage;
                NSString *name=engine.boolValue?@"engine":@"renderer";
                [trials addObject:@{@"use_style_engine":engine,@"output":Render(result,context,linear,[out stringByAppendingPathComponent:[name stringByAppendingString:@".f32"]])}];
            } @catch(NSException *exception) {[trials addObject:@{@"use_style_engine":engine,@"exception":exception.description}];}
        }
        facts[@"trials"]=trials;facts[@"gtc_calls"]=Calls;
        if([NSProcessInfo.processInfo.environment[@"VM_GTC_SPOTCHECK"] boolValue]) {
        // Optional single spot-check; the established GTC experiments are not rerun by default.
        NSUInteger width=4096,height=4;
        NSMutableData *ramp=[NSMutableData dataWithLength:width*height*16];float *p=ramp.mutableBytes;
        for(NSUInteger y=0;y<height;y++)for(NSUInteger x=0;x<width;x++) {
            float v=(float)x/(width-1);NSUInteger i=(y*width+x)*4;
            p[i]=y==0||y==1?v:(y==2?.5:.25);
            p[i+1]=y==0||y==2?v:(y==1?.25:.5);
            p[i+2]=y==0||y==3?v:(y==1?.5:.25);p[i+3]=1;
        }
        CIImage *rampImage=[CIImage imageWithBitmapData:ramp bytesPerRow:width*16 size:CGSizeMake(width,height) format:kCIFormatRGBAf colorSpace:nil];
        NSMutableArray *kernelTrials=[NSMutableArray new];
        for(NSNumber *count in @[@1,@2,@3,@4]) { @try {
            NSMutableArray *args=[NSMutableArray arrayWithObject:rampImage];
            if(count.intValue>=2)[args addObject:curve];
            while(args.count<count.intValue)[args addObject:@1];
            CIImage *result=[(CIColorKernel *)GTC applyWithExtent:rampImage.extent arguments:args];
            [kernelTrials addObject:@{@"argument_count":count,@"output":Render(result,unmanaged,NULL,[out stringByAppendingPathComponent:[NSString stringWithFormat:@"kernel-%@.f32",count]])}];
        } @catch(NSException *exception){[kernelTrials addObject:@{@"argument_count":count,@"exception":exception.description}];} }
        facts[@"kernel_trials"]=kernelTrials;
        NSMutableArray *controlled=[NSMutableArray new];
        for(NSString *kind in @[@"actual",@"identity",@"square"]) {
            CIImage *table=curve;
            if(![kind isEqualToString:@"actual"]) {
                NSMutableData *values=[NSMutableData dataWithLength:256*4];float *q=values.mutableBytes;
                for(int i=0;i<256;i++) {float v=(float)i/255;q[i]=[kind isEqualToString:@"square"]?v*v:v;}
                table=[(id)filter curveImageWithData:values];
            }
            CIVector *domain=[CIVector vectorWithX:0 Y:1];
            CIVector *normalizer=[CIVector vectorWithX:255./256 Y:.5/256];
            CIImage *result=[(CIColorKernel *)GTC applyWithExtent:rampImage.extent arguments:@[rampImage,table,domain,normalizer]];
            [controlled addObject:@{@"kind":kind,@"domain":@[@0,@1],@"normalizer":@[@(255./256),@(.5/256)],@"output":Render(result,unmanaged,NULL,[out stringByAppendingPathComponent:[kind stringByAppendingString:@"-gtc-ramp.f32"]])}];
        }
        facts[@"controlled_gtc"]=controlled;
        }
        CGColorSpaceRelease(linear);
        facts[@"os"]=NSProcessInfo.processInfo.operatingSystemVersionString;facts[@"device"]=device.name;
    } @catch(NSException *exception) {facts[@"exception"]=exception.description;}
    NSData *json=[NSJSONSerialization dataWithJSONObject:facts options:NSJSONWritingPrettyPrinted|NSJSONWritingSortedKeys error:&error];
    [json writeToFile:[out stringByAppendingPathComponent:@"facts.json"] atomically:YES];
    printf("%s\n",[[facts description] UTF8String]);
    return facts[@"exception"]?6:0;
 }
}
