#import "native_common.h"
#import <MetalKit/MetalKit.h>

// Calls only the explicitly named SPI below. NSInvocation preserves struct ABI.
static id Call(id target, NSString *name, NSArray *args) {
    NSMethodSignature *signature = [target methodSignatureForSelector:NSSelectorFromString(name)];
    if (!signature || signature.numberOfArguments != args.count + 2)
        @throw [NSException exceptionWithName:@"SPIABI" reason:name userInfo:nil];
    NSInvocation *call = [NSInvocation invocationWithMethodSignature:signature];
    call.target = target; call.selector = NSSelectorFromString(name);
    for (NSUInteger i = 0; i < args.count; i++) {
        const char *type = [signature getArgumentTypeAtIndex:i + 2];
        while (*type && strchr("rnNoORV", *type)) type++;
        id value = args[i];
        if (*type == '@') { __unsafe_unretained id item = value == NSNull.null ? nil : value; [call setArgument:&item atIndex:i + 2]; }
        else if (!strcmp(type, "Q")) { uint64_t item = [value unsignedLongLongValue]; [call setArgument:&item atIndex:i + 2]; }
        else if (!strcmp(type, "q")) { int64_t item = [value longLongValue]; [call setArgument:&item atIndex:i + 2]; }
        else if (!strcmp(type, "i")) { int item = [value intValue]; [call setArgument:&item atIndex:i + 2]; }
        else if (!strcmp(type, "I")) { unsigned item = [value unsignedIntValue]; [call setArgument:&item atIndex:i + 2]; }
        else if (!strcmp(type, "B")) { BOOL item = [value boolValue]; [call setArgument:&item atIndex:i + 2]; }
        else if (!strcmp(type, "f")) { float item = [value floatValue]; [call setArgument:&item atIndex:i + 2]; }
        else if (!strcmp(type, "d")) { double item = [value doubleValue]; [call setArgument:&item atIndex:i + 2]; }
        else if (!strcmp(type, @encode(CGPoint))) { CGPoint item = [value pointValue]; [call setArgument:&item atIndex:i + 2]; }
        else if (!strcmp(type, @encode(CGSize))) { CGSize item = [value sizeValue]; [call setArgument:&item atIndex:i + 2]; }
        else if (!strcmp(type, @encode(CGRect))) { CGRect item = [value rectValue]; [call setArgument:&item atIndex:i + 2]; }
        else @throw [NSException exceptionWithName:@"SPIABI" reason:[name stringByAppendingFormat:@" unsupported argument %s", type] userInfo:nil];
    }
    [call invoke];
    const char *type = signature.methodReturnType;
    if (*type == '@' || *type == '#') { __unsafe_unretained id result = nil; [call getReturnValue:&result]; return result; }
    if (*type == 'v') return NSNull.null;
    if (!strcmp(type, "i")) { int result; [call getReturnValue:&result]; return @(result); }
    if (!strcmp(type, "Q")) { uint64_t result; [call getReturnValue:&result]; return @(result); }
    if (!strcmp(type, "B")) { BOOL result; [call getReturnValue:&result]; return @(result); }
    if (!strcmp(type, "f")) { float result; [call getReturnValue:&result]; return @(result); }
    if (!strcmp(type, "d")) { double result; [call getReturnValue:&result]; return @(result); }
    @throw [NSException exceptionWithName:@"SPIABI" reason:[name stringByAppendingFormat:@" unsupported return %s", type] userInfo:nil];
}

static id Make(NSString *name) { return Call([NSClassFromString(name) alloc], @"init", @[]); }

static id<MTLTexture> Texture(id<MTLDevice> device, MTLPixelFormat format, size_t width, size_t height) {
    MTLTextureDescriptor *descriptor = [MTLTextureDescriptor texture2DDescriptorWithPixelFormat:format width:width height:height mipmapped:NO];
    descriptor.usage = MTLTextureUsageShaderRead | MTLTextureUsageShaderWrite;
    descriptor.storageMode = MTLStorageModeShared;
    return [device newTextureWithDescriptor:descriptor];
}

static id Wrap(id<MTLTexture> texture, CGRect region) {
    id wrapper = Make(@"CMITSTextureAndFullImageRegion");
    Call(wrapper, @"setTexture:", @[texture]);
    Call(wrapper, @"setFullImageRegion:", @[[NSValue valueWithRect:region]]);
    return wrapper;
}

static id<MTLTexture> CopyBuffer(id<MTLDevice> device, CVPixelBufferRef buffer) {
    OSType format = CVPixelBufferGetPixelFormatType(buffer);
    MTLPixelFormat metalFormat = format == kCVPixelFormatType_OneComponent8 ? MTLPixelFormatR8Unorm : MTLPixelFormatR32Float;
    if (format != kCVPixelFormatType_OneComponent8 && format != kCVPixelFormatType_OneComponent32Float)
        @throw [NSException exceptionWithName:@"BufferFormat" reason:@(format).description userInfo:nil];
    id<MTLTexture> texture = Texture(device, metalFormat, CVPixelBufferGetWidth(buffer), CVPixelBufferGetHeight(buffer));
    CVPixelBufferLockBaseAddress(buffer, kCVPixelBufferLock_ReadOnly);
    [texture replaceRegion:MTLRegionMake2D(0, 0, texture.width, texture.height) mipmapLevel:0 withBytes:CVPixelBufferGetBaseAddress(buffer) bytesPerRow:CVPixelBufferGetBytesPerRow(buffer)];
    CVPixelBufferUnlockBaseAddress(buffer, kCVPixelBufferLock_ReadOnly);
    return texture;
}

int main(int argc, char **argv) {
    @autoreleasepool {
        if (argc < 4 || argc > 6) return 64;
        NSString *input = @(argv[1]), *out = @(argv[2]);
        uint64_t landmarkType = strtoull(argv[3], NULL, 10);
        NSString *parameterSource = argc > 4 ? @(argv[4]) : @"defaults";
        double exposure = argc > 5 ? strtod(argv[5], NULL) : 0;
        NSMutableDictionary *report = [@{
            @"schema": @"texture-image-statistics-v1", @"stage": @"begin", @"input_sha256": SHA([NSData dataWithContentsOfFile:input]),
            @"apple_implementation_patched": @NO, @"provided_capture_image_stats": @NO,
            @"landmark_type_control": @(landmarkType), @"color_domain": @"newly derived extended linear Display P3 from upright SDR input",
            @"parameter_source_control": parameterSource, @"exposure_EV_control": @(exposure),
        } mutableCopy];
        Write(report, out);
        @try {
            dlopen("/System/Library/PrivateFrameworks/CMImaging.framework/CMImaging", RTLD_NOW | RTLD_LOCAL);
            dlopen("/System/Library/PrivateFrameworks/PhotoImaging.framework/PhotoImaging", RTLD_NOW | RTLD_LOCAL);
            id<MTLDevice> device = MTLCreateSystemDefaultDevice();
            CGImageSourceRef source = CGImageSourceCreateWithURL((__bridge CFURLRef)[NSURL fileURLWithPath:input], NULL);
            CGImageRef image = CGImageSourceCreateImageAtIndex(source, 0, NULL);
            if (!image) @throw [NSException exceptionWithName:@"Decode" reason:@"image unavailable" userInfo:nil];
            size_t width = CGImageGetWidth(image), height = CGImageGetHeight(image);
            CGRect full = CGRectMake(0, 0, width, height);
            VNImageRequestHandler *handler = [[VNImageRequestHandler alloc] initWithCGImage:image options:@{}];
            VNRequest *segmentRequest = [NSClassFromString(@"VNGenerateFaceSegmentsRequest") new];
            VNRequest *skinRequest = [NSClassFromString(@"VNGenerateHumanAttributesSegmentationRequest") new];
            VNGeneratePersonInstanceMaskRequest *instanceRequest = [VNGeneratePersonInstanceMaskRequest new];
            NSError *error = nil;
            report[@"stage"] = @"inference"; Write(report, out);
            BOOL success = [handler performRequests:@[segmentRequest, skinRequest, instanceRequest] error:&error];
            report[@"inference_success"] = @(success); report[@"inference_error"] = error.description ?: @"";
            if (!success) @throw [NSException exceptionWithName:@"Inference" reason:report[@"inference_error"] userInfo:nil];
            VNDetectFaceLandmarksRequest *landmarkRequest = [VNDetectFaceLandmarksRequest new];
            landmarkRequest.inputFaceObservations = (NSArray<VNFaceObservation *> *)segmentRequest.results;
            success = [handler performRequests:@[landmarkRequest] error:&error];
            if (!success || landmarkRequest.results.count != 1 || instanceRequest.results.count != 1)
                @throw [NSException exceptionWithName:@"ProbeScope" reason:@"this first statistics control requires exactly one inferred face and one person observation" userInfo:nil];
            VNFaceObservation *face = landmarkRequest.results[0];
            report[@"face_geometry"] = FaceFacts(@[face]);
            VNPixelBufferObservation *skinObservation = nil;
            for (VNPixelBufferObservation *item in skinRequest.results)
                if ([[item valueForKey:@"featureName"] isEqual:@"human_attribute_skin"]) skinObservation = item;
            if (!skinObservation) @throw [NSException exceptionWithName:@"Inference" reason:@"no skin output" userInfo:nil];
            VNInstanceMaskObservation *instance = instanceRequest.results[0];
            if (instance.allInstances.count != 1) @throw [NSException exceptionWithName:@"ProbeScope" reason:@"multiple instances require explicit face matching" userInfo:nil];
            CVPixelBufferRef instanceMask = [instance generateScaledMaskForImageForInstances:instance.allInstances fromRequestHandler:handler error:&error];
            if (!instanceMask) @throw [NSException exceptionWithName:@"InstanceMask" reason:error.description userInfo:nil];
            CGRect box = face.boundingBox;
            CGRect faceRect = CGRectMake(box.origin.x * width, (1 - CGRectGetMaxY(box)) * height, box.size.width * width, box.size.height * height);
            report[@"pixel_face_roi_top_left"] = @[@(faceRect.origin.x), @(faceRect.origin.y), @(faceRect.size.width), @(faceRect.size.height)];
            report[@"skin_buffer"] = BufferFacts(skinObservation.pixelBuffer);
            report[@"instance_buffer"] = BufferFacts(instanceMask);
            id<MTLTexture> skinTexture = CopyBuffer(device, skinObservation.pixelBuffer);
            id<MTLTexture> instanceTexture = CopyBuffer(device, instanceMask);
            // Diagnostic face-skin derivation uses measured skin probabilities and face bounds.
            // It is distinct from a FSINC face-skin result, which is not claimed here.
            size_t maskWidth = skinTexture.width, maskHeight = skinTexture.height;
            NSMutableData *faceMaskData = [NSMutableData dataWithLength:maskWidth * maskHeight];
            [skinTexture getBytes:faceMaskData.mutableBytes bytesPerRow:maskWidth fromRegion:MTLRegionMake2D(0, 0, maskWidth, maskHeight) mipmapLevel:0];
            uint8_t *values = faceMaskData.mutableBytes;
            for (size_t y = 0; y < maskHeight; y++) for (size_t x = 0; x < maskWidth; x++)
                if (!CGRectContainsPoint(faceRect, CGPointMake((x + 0.5) * width / maskWidth, (y + 0.5) * height / maskHeight))) values[y * maskWidth + x] = 0;
            id<MTLTexture> faceTexture = Texture(device, MTLPixelFormatR8Unorm, maskWidth, maskHeight);
            [faceTexture replaceRegion:MTLRegionMake2D(0, 0, maskWidth, maskHeight) mipmapLevel:0 withBytes:values bytesPerRow:maskWidth];
            report[@"face_skin_source"] = @"diagnostic intersection of inferred skin probabilities with measured face bounds";
            report[@"face_skin_sha256"] = SHA(faceMaskData);
            uint64_t faceMaskSum = 0;
            for (size_t i = 0; i < faceMaskData.length; i++) faceMaskSum += values[i];
            report[@"face_skin_mean"] = @(faceMaskSum / (255.0 * faceMaskData.length));
            MTKTextureLoader *loader = [[MTKTextureLoader alloc] initWithDevice:device];
            id<MTLTexture> encoded = [loader newTextureWithCGImage:image options:@{MTKTextureLoaderOptionOrigin: MTKTextureLoaderOriginTopLeft, MTKTextureLoaderOptionSRGB: @NO} error:&error];
            if (!encoded) @throw [NSException exceptionWithName:@"ImageTexture" reason:error.description userInfo:nil];
            CGColorSpaceRef srgb = CGColorSpaceCreateWithName(kCGColorSpaceSRGB);
            CGColorSpaceRef working = CGColorSpaceCreateWithName(kCGColorSpaceExtendedLinearDisplayP3);
            CIImage *ciImage = [CIImage imageWithMTLTexture:encoded options:@{kCIImageColorSpace: (__bridge id)srgb}];
            if (exposure != 0) ciImage = [ciImage imageByApplyingFilter:@"CIExposureAdjust" withInputParameters:@{kCIInputEVKey: @(exposure)}];
            id<MTLTexture> inputTexture = Texture(device, MTLPixelFormatRGBA16Float, width, height);
            id<MTLTexture> outputTexture = Texture(device, MTLPixelFormatRGBA16Float, width, height);
            id<MTLCommandQueue> queue = [device newCommandQueue];
            id<MTLCommandBuffer> command = [queue commandBuffer];
            CIContext *context = [CIContext contextWithMTLDevice:device options:@{}];
            [context render:ciImage toMTLTexture:inputTexture commandBuffer:command bounds:full colorSpace:working];
            [command commit]; [command waitUntilCompleted];
            report[@"image_upload_status"] = @(command.status);
            NSMutableData *imagePixels = [NSMutableData dataWithLength:width * height * 8];
            [inputTexture getBytes:imagePixels.mutableBytes bytesPerRow:width * 8 fromRegion:MTLRegionMake2D(0, 0, width, height) mipmapLevel:0];
            const __fp16 *imageValues = imagePixels.bytes;
            double mean[3] = {0}, maxValue = 0; uint64_t nonfinite = 0;
            for (size_t i = 0; i < width * height; i++) for (size_t c = 0; c < 3; c++) {
                float v = imageValues[i * 4 + c];
                if (!isfinite(v)) { nonfinite++; continue; }
                mean[c] += v / (width * height); maxValue = MAX(maxValue, v);
            }
            report[@"image_pixels"] = @{@"sha256": SHA(imagePixels), @"mean_rgb": @[@(mean[0]), @(mean[1]), @(mean[2])], @"maximum": @(maxValue), @"nonfinite": @(nonfinite)};
            id person = Make(@"CMITextureStylesPersonInputData");
            Call(person, @"setFaceID:", @[@1]);
            Call(person, @"setFaceROI:", @[[NSValue valueWithRect:faceRect]]);
            Call(person, @"setFaceSkinROI:", @[[NSValue valueWithRect:faceRect]]);
            Call(person, @"setInstanceROI:", @[[NSValue valueWithRect:full]]);
            Call(person, @"setFaceLandmarkType:", @[@(landmarkType)]);
            Call(person, @"setUnitOfAngle:", @[@0]);
            for (NSString *key in @[@"yaw", @"pitch", @"roll"]) {
                NSNumber *angle = [face valueForKey:key];
                if (angle) {
                    NSString *setter = [NSString stringWithFormat:@"setFace%@%@:", [[key substringToIndex:1] uppercaseString], [key substringFromIndex:1]];
                    Call(person, setter, @[@(angle.doubleValue * 180.0 / M_PI)]);
                }
            }
            NSMutableArray *landmarks = [NSMutableArray new];
            VNFaceLandmarkRegion2D *points = face.landmarks.allPoints;
            for (NSUInteger i = 0; i < points.pointCount; i++) {
                CGPoint p = points.normalizedPoints[i];
                p = CGPointMake((box.origin.x + p.x * box.size.width) * width, (1 - box.origin.y - p.y * box.size.height) * height);
                id landmark = Call([NSClassFromString(@"CMITextureStylesFaceLandmark") alloc], @"initWithPoint:error:", @[[NSValue valueWithPoint:p], @0]);
                [landmarks addObject:landmark];
            }
            Call(person, @"setFaceLandmarks:", @[landmarks]);
            report[@"person_before_stats"] = Call(person, @"dictionaryRepresentation", @[]);
            NSMutableDictionary *nativeStats = [NSMutableDictionary new];
            id io = Make(@"CMITextureStylesMattifyIO");
            Call(io, @"setInputImage:", @[Wrap(inputTexture, full)]);
            Call(io, @"setOutputImage:", @[Wrap(outputTexture, full)]);
            Call(io, @"setInputSkinMask:", @[Wrap(skinTexture, full)]);
            Call(io, @"setInputFaceMask:", @[Wrap(faceTexture, full)]);
            Call(io, @"setInputInstanceMask:", @[Wrap(instanceTexture, full)]);
            Call(io, @"setOutputPersonStats:", @[nativeStats]);
            id effect = Call([NSClassFromString(@"CMITextureStylesMattify") alloc], @"initWithOptionalMetalContext:", @[NSNull.null]);
            id parameters = nil;
            if ([parameterSource isEqual:@"defaults"]) parameters = Make(@"CMITextureStylesMattifyParameters");
            else {
                id tuning = Call(NSClassFromString(@"CMITextureStyleTuningLookup"), @"tuningDictionaryForHardwareModel:portType:captureMode:preset:captureType:", @[@"iPhone19,2", @"PortTypeBack", @"Still", parameterSource, @"LF"]);
                if (!tuning) @throw [NSException exceptionWithName:@"TuningUnavailable" reason:parameterSource userInfo:nil];
                id effectDescriptor = Call(NSClassFromString(@"PITextureStyleProcessorKernel"), @"descriptorForMattifyWithTuningDictionary:", @[tuning]);
                parameters = Call(effectDescriptor, @"parameters", @[]);
                if (!parameters) @throw [NSException exceptionWithName:@"TuningUnavailable" reason:@"native Mattify parameters unavailable" userInfo:nil];
                report[@"tuning_target_is_source_camera_provenance"] = @NO;
                report[@"native_effect_type"] = Call(effectDescriptor, @"type", @[]);
            }
            NSMutableDictionary *parameterValues = [NSMutableDictionary new];
            for (NSString *key in @[@"editingStrength", @"smallBlurRadiusFaceDiagonalFactor", @"largeBlurRadiusFaceDiagonalFactor", @"fracMaskHighlightsHeadroom", @"fracMaskHighlightsNormFactor"])
                parameterValues[key] = Call(parameters, key, @[]);
            report[@"native_parameters"] = parameterValues;
            Call(effect, @"setParameters:", @[parameters]);
            Call(effect, @"setInputOutput:", @[io]);
            Call(effect, @"setPersonData:", @[person]);
            Call(effect, @"setInstanceID:", @[@1]);
            Call(effect, @"setFullImageSize:", @[[NSValue valueWithSize:full.size]]);
            Call(effect, @"setRegionToRender:", @[[NSValue valueWithRect:full]]);
            Call(effect, @"setSkipRendering:", @[@YES]);
            report[@"parameter_validation"] = Call(parameters, @"validate", @[]);
            id allocator = Call(effect, @"allocator", @[]);
            if (!allocator) {
                // Type 2 is the native CMI allocator path recorded in the prior
                // CMIStyleEngineProcessor investigation; no cache implementation is changed.
                allocator = Call([NSClassFromString(@"FigMetalAllocator") alloc], @"initWithDevice:allocatorType:", @[device, @2]);
                id descriptor = Make(@"FigMetalAllocatorDescriptor");
                Call(descriptor, @"setMemSize:", @[@(128ull * 1024 * 1024)]);
                Call(descriptor, @"setAllowFallback:", @[@YES]);
                report[@"allocator_setup"] = Call(allocator, @"setupWithDescriptor:", @[descriptor]);
                Call(effect, @"setAllocator:", @[allocator]);
            }
            report[@"allocator_class"] = allocator ? NSStringFromClass([allocator class]) : @"nil";
            for (NSString *stage in @[@"setup", @"prepareToProcess:", @"calculateStats", @"process", @"finishProcessing"]) {
                report[@"stage"] = stage; Write(report, out);
                NSNumber *status = Call(effect, stage, [stage containsString:@":"] ? @[@0] : @[]);
                if ([stage isEqual:@"calculateStats"] || [stage isEqual:@"process"] || [stage isEqual:@"finishProcessing"]) {
                    id nativeContext = [effect valueForKey:@"_context"];
                    Call(nativeContext, @"forceCommit", @[]);
                    Call(nativeContext, @"waitForIdle", @[]);
                }
                report[stage] = status; report[@"native_output_person_stats"] = nativeStats; Write(report, out);
                if (status.intValue != 0) break;
            }
            report[@"stage"] = @"finished";
            CVPixelBufferRelease(instanceMask); CGImageRelease(image); CFRelease(source);
            CGColorSpaceRelease(srgb); CGColorSpaceRelease(working);
        } @catch (NSException *exception) {
            report[@"exception"] = @{@"name": exception.name, @"reason": exception.reason ?: @""};
        }
        Write(report, out);
        return 0;
    }
}
