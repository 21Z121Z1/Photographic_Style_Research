#define main IndependentHDRMain
#include "/Users/retriedstormtrooper/Documents/Projects/Active/proxdrtest/artifacts/research/20261106-native-hdr-independent/src/native.m"
#undef main

static NSDictionary *SpaceDescription(CGColorSpaceRef s) {
    return s ? @{ @"name": Safe(CFBridgingRelease(CGColorSpaceCopyName(s))),
                  @"description": [(__bridge id)s description] } : @{ @"nil": @YES };
}

int main(int argc, char **argv) { @autoreleasepool {
    if(argc != 3) return 2;
    Setup();
    NSString *out = @(argv[2]);
    Check([[NSFileManager defaultManager] createDirectoryAtPath:out withIntermediateDirectories:NO attributes:nil error:NULL], @"Output must be new");
    AVAsset *asset = [AVURLAsset URLAssetWithURL:[NSURL fileURLWithPath:@(argv[1])] options:nil];
    AVAssetTrack *track = [asset tracksWithMediaType:AVMediaTypeVideo].firstObject;
    CGRect crop = CMVideoFormatDescriptionGetCleanAperture((__bridge CMVideoFormatDescriptionRef)track.formatDescriptions.firstObject, NO);
    NSArray *modes = @[
        @{ @"name": @"auto-rgba-half", @"settings": @{ (id)kCVPixelBufferPixelFormatTypeKey: @(kCVPixelFormatType_64RGBAHalf) } },
        @{ @"name": @"native-yuv", @"settings": @{ (id)kCVPixelBufferPixelFormatTypeKey: @(kCVPixelFormatType_420YpCbCr8BiPlanarFullRange) } },
        @{ @"name": @"explicit-linear-p3", @"settings": @{ (id)kCVPixelBufferPixelFormatTypeKey: @(kCVPixelFormatType_64RGBAHalf), AVVideoColorPropertiesKey: @{ AVVideoColorPrimariesKey: AVVideoColorPrimaries_P3_D65, AVVideoTransferFunctionKey: AVVideoTransferFunction_Linear, AVVideoYCbCrMatrixKey: AVVideoYCbCrMatrix_ITU_R_601_4 } } }
    ];
    NSMutableArray *facts = [NSMutableArray new];
    for(NSDictionary *mode in modes) { @autoreleasepool {
        NSMutableDictionary *item = [@{ @"mode": mode[@"name"] } mutableCopy];
        NSError *error = nil;
        @try {
            AVAssetReader *reader = [[AVAssetReader alloc] initWithAsset:asset error:&error];
            AVAssetReaderTrackOutput *output = [[AVAssetReaderTrackOutput alloc] initWithTrack:track outputSettings:mode[@"settings"]];
            [reader addOutput:output];
            if(![reader startReading]) { item[@"error"] = reader.error.description; [facts addObject:item]; continue; }
            NSMutableArray *frames = [NSMutableArray new];
            CMSampleBufferRef sample; NSUInteger index = 0;
            while((sample = [output copyNextSampleBuffer])) {
                if(index == 0 || index == 44) {
                    CVPixelBufferRef pb = CMSampleBufferGetImageBuffer(sample);
                    CIImage *image = [CIImage imageWithCVPixelBuffer:pb options:@{ kCIImageApplyCleanAperture: @NO }];
                    CIImage *unmanaged = [CIImage imageWithCVPixelBuffer:pb options:@{ kCIImageColorSpace: NSNull.null, kCIImageApplyCleanAperture: @NO }];
                    NSString *base = [NSString stringWithFormat:@"%@-%04lu",mode[@"name"],(unsigned long)index];
                    NSData *managed = Pixels(Fit(image,crop,384,288),Context,Linear,384,288);
                    NSData *raw = Pixels(Fit(unmanaged,crop,384,288),Unmanaged,NULL,384,288);
                    [managed writeToFile:P(out,[base stringByAppendingString:@"-managed.f32"]) atomically:YES];
                    [raw writeToFile:P(out,[base stringByAppendingString:@"-unmanaged.f32"]) atomically:YES];
                    [frames addObject:@{ @"index": @(index), @"pts": T(CMSampleBufferGetPresentationTimeStamp(sample)),
                        @"ciColorSpace": SpaceDescription(image.colorSpace),
                        @"bufferColorSpace": SpaceDescription(CVImageBufferGetColorSpace(pb)),
                        @"attachments": Safe(CFBridgingRelease(CVBufferCopyAttachments(pb,kCVAttachmentMode_ShouldPropagate))),
                        @"managed": Stats(managed), @"unmanaged": Stats(raw) }];
                }
                CFRelease(sample); index++;
                if(index > 44) break;
            }
            [reader cancelReading]; item[@"frames"] = frames;
        } @catch(NSException *exception) { item[@"exception"] = exception.description; }
        [facts addObject:item];
    }}
    JSON(@{ @"os": NSProcessInfo.processInfo.operatingSystemVersionString, @"modes": facts },P(out,@"facts.json"));
    return 0;
}}
