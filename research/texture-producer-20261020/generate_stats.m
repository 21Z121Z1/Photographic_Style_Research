#import "spi_call.h"
#import <MetalKit/MetalKit.h>


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

static NSDictionary *ScalarTextureFacts(id<MTLTexture> texture) {
    if (!texture) return @{@"available": @NO};
    size_t size = texture.pixelFormat == MTLPixelFormatR8Unorm ? 1 : texture.pixelFormat == MTLPixelFormatR16Float ? 2 : texture.pixelFormat == MTLPixelFormatR32Float ? 4 : 0;
    NSMutableDictionary *result = [@{@"available": @YES, @"width": @(texture.width), @"height": @(texture.height), @"format": @(texture.pixelFormat), @"type": @(texture.textureType)} mutableCopy];
    if (!size || texture.textureType != MTLTextureType2D || texture.storageMode == MTLStorageModePrivate) return result;
    NSMutableData *pixels = [NSMutableData dataWithLength:texture.width * texture.height * size];
    [texture getBytes:pixels.mutableBytes bytesPerRow:texture.width * size fromRegion:MTLRegionMake2D(0, 0, texture.width, texture.height) mipmapLevel:0];
    double sum = 0, maxValue = 0; uint64_t nonzero = 0;
    for (size_t i = 0; i < texture.width * texture.height; i++) {
        double v = size == 1 ? ((const uint8_t *)pixels.bytes)[i] / 255.0 : size == 2 ? ((const __fp16 *)pixels.bytes)[i] : ((const float *)pixels.bytes)[i];
        if (isfinite(v)) { sum += v; maxValue = MAX(maxValue, v); nonzero += v > 0.001; }
    }
    result[@"mean"] = @(sum / (texture.width * texture.height)); result[@"maximum"] = @(maxValue);
    result[@"nonzero_over_0_001"] = @(nonzero); result[@"sha256"] = SHA(pixels);
    return result;
}

int main(int argc, char **argv) {
    @autoreleasepool {
        if (argc < 4 || argc > 6) return 64;
        NSString *input = @(argv[1]), *out = @(argv[2]);
        uint64_t landmarkType = strtoull(argv[3], NULL, 10);
        NSString *parameterSource = argc > 4 ? @(argv[4]) : @"defaults";
        double exposure = argc > 5 ? strtod(argv[5], NULL) : 0;
        NSString *effectKind = getenv("TEXTURE_EFFECT") ? @(getenv("TEXTURE_EFFECT")) : @"Mattify";
        NSMutableDictionary *report = [@{
            @"schema": @"texture-image-statistics-v1", @"stage": @"begin", @"input_sha256": SHA([NSData dataWithContentsOfFile:input]),
            @"apple_implementation_patched": @NO, @"provided_capture_image_stats": @NO,
            @"landmark_type_control": @(landmarkType), @"color_domain": @"newly derived extended linear Display P3 from upright SDR input",
            @"parameter_source_control": parameterSource, @"exposure_EV_control": @(exposure),
            @"producer_effect": effectKind,
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
            if (instanceTexture.pixelFormat == MTLPixelFormatR32Float) {
                // Vision's scaled Float32 mask can overshoot [0,1]. The native
                // HEIF instance-matte carrier uses an L8 mask, so normalize once.
                CVPixelBufferLockBaseAddress(instanceMask, kCVPixelBufferLock_ReadOnly);
                size_t iw = CVPixelBufferGetWidth(instanceMask), ih = CVPixelBufferGetHeight(instanceMask), stride = CVPixelBufferGetBytesPerRow(instanceMask);
                const uint8_t *base = CVPixelBufferGetBaseAddress(instanceMask);
                NSMutableData *l8 = [NSMutableData dataWithLength:iw * ih];
                for (size_t y = 0; y < ih; y++) for (size_t x = 0; x < iw; x++) {
                    float v = ((const float *)(base + y * stride))[x];
                    ((uint8_t *)l8.mutableBytes)[y * iw + x] = (uint8_t)lrintf(fminf(1, fmaxf(0, v)) * 255);
                }
                CVPixelBufferUnlockBaseAddress(instanceMask, kCVPixelBufferLock_ReadOnly);
                instanceTexture = Texture(device, MTLPixelFormatR8Unorm, iw, ih);
                [instanceTexture replaceRegion:MTLRegionMake2D(0, 0, iw, ih) mipmapLevel:0 withBytes:l8.bytes bytesPerRow:iw];
                report[@"instance_normalization"] = @"native inferred Float32 to clamped L8 probabilities";
                report[@"instance_texture"] = ScalarTextureFacts(instanceTexture);
            }
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
            // The original _calculateStats reads IO.outputImage. The main CMI
            // processor initializes that working image before calculating stats.
            id<MTLBlitCommandEncoder> initialCopy = [command blitCommandEncoder];
            [initialCopy copyFromTexture:inputTexture toTexture:outputTexture];
            [initialCopy endEncoding];
            [command commit]; [command waitUntilCompleted];
            report[@"image_upload_status"] = @(command.status);
            report[@"statistics_samples_initialized_output_image"] = @YES;
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
            if ([effectKind isEqual:@"Mattify"] && [parameterSource isEqual:@"Studio"] && exposure == 0) {
                NSMutableData *rgba = [NSMutableData dataWithLength:width * height * 16];
                for (size_t i = 0; i < width * height * 4; i++) ((float *)rgba.mutableBytes)[i] = imageValues[i];
                [rgba writeToFile:[[out stringByDeletingLastPathComponent] stringByAppendingPathComponent:@"native-linear-p3.rgba32f"] atomically:YES];
                report[@"linear_RGBA32f_for_derived_styles_sha256"] = SHA(rgba);
            }
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
            NSString *ioName = [effectKind isEqual:@"SkinSmoothStandalone"] ? @"CMITextureStylesSkinSmoothIO" : [[@"CMITextureStyles" stringByAppendingString:effectKind] stringByAppendingString:@"IO"];
            id io = Make(ioName);
            Call(io, @"setInputImage:", @[Wrap(inputTexture, full)]);
            Call(io, @"setOutputImage:", @[Wrap(outputTexture, full)]);
            if ([io respondsToSelector:NSSelectorFromString(@"setInputSkinMask:")]) Call(io, @"setInputSkinMask:", @[Wrap(skinTexture, full)]);
            if ([io respondsToSelector:NSSelectorFromString(@"setInputFaceMask:")]) Call(io, @"setInputFaceMask:", @[Wrap(faceTexture, full)]);
            if ([effectKind isEqual:@"SkinSmoothStandalone"]) {
                Call(io, @"setInputSkinMaskAndFullImageRegion:", @[Wrap(skinTexture, full)]);
                Call(io, @"setFaceSkinMaskTextureAndFullImageRegion:", @[Wrap(faceTexture, full)]);
                Call(io, @"setInstanceMaskTextureAndFullImageRegion:", @[Wrap(instanceTexture, full)]);
                Call(io, @"setPersonMaskTextureAndFullImageRegion:", @[Wrap(instanceTexture, full)]);
                Call(io, @"setInputFaceRect:", @[[NSValue valueWithRect:faceRect]]);
                Call(io, @"setAllPersonDataForBlending:", @[@[person]]);
            } else Call(io, @"setInputInstanceMask:", @[Wrap(instanceTexture, full)]);
            Call(io, @"setOutputPersonStats:", @[nativeStats]);
            id effect = Call([NSClassFromString([@"CMITextureStyles" stringByAppendingString:effectKind]) alloc], @"initWithOptionalMetalContext:", @[NSNull.null]);
            id parameters = nil;
            if ([parameterSource isEqual:@"defaults"]) parameters = Make([ioName stringByReplacingOccurrencesOfString:@"IO" withString:@"Parameters"]);
            else {
                id tuning = Call(NSClassFromString(@"CMITextureStyleTuningLookup"), @"tuningDictionaryForHardwareModel:portType:captureMode:preset:captureType:", @[@"iPhone19,2", @"PortTypeBack", @"Still", parameterSource, @"LF"]);
                if (!tuning) @throw [NSException exceptionWithName:@"TuningUnavailable" reason:parameterSource userInfo:nil];
                NSString *descriptorSelector = [effectKind isEqual:@"Mattify"] ? @"descriptorForMattifyWithTuningDictionary:" : [effectKind isEqual:@"UnderEyeBrighten"] ? @"descriptorForUnderEyeBrighteningWithTuningDictionary:" : @"descriptorForSkinSmoothingWithTuningDictionary:";
                id effectDescriptor = Call(NSClassFromString(@"PITextureStyleProcessorKernel"), descriptorSelector, @[tuning]);
                parameters = Call(effectDescriptor, @"parameters", @[]);
                if (!parameters) @throw [NSException exceptionWithName:@"TuningUnavailable" reason:@"native Mattify parameters unavailable" userInfo:nil];
                report[@"tuning_target_is_source_camera_provenance"] = @NO;
                report[@"native_effect_type"] = Call(effectDescriptor, @"type", @[]);
            }
            NSMutableDictionary *parameterValues = [NSMutableDictionary new];
            for (NSString *key in @[@"editingStrength", @"smallBlurRadiusFaceDiagonalFactor", @"largeBlurRadiusFaceDiagonalFactor", @"fracMaskHighlightsHeadroom", @"fracMaskHighlightsNormFactor"])
                if ([parameters respondsToSelector:NSSelectorFromString(key)]) parameterValues[key] = Call(parameters, key, @[]);
            report[@"native_parameters"] = parameterValues;
            Call(effect, @"setParameters:", @[parameters]);
            Call(effect, @"setInputOutput:", @[io]);
            Call(effect, @"setPersonData:", @[person]);
            Call(effect, @"setInstanceID:", @[@1]);
            Call(effect, @"setFullImageSize:", @[[NSValue valueWithSize:full.size]]);
            Call(effect, @"setRegionToRender:", @[[NSValue valueWithRect:full]]);
            if ([effect respondsToSelector:NSSelectorFromString(@"setSkipRendering:")]) Call(effect, @"setSkipRendering:", @[@YES]);
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
            id nativeContext = [effect valueForKey:@"_context"];
            id originalQueue = Call(effect, @"metalCommandQueue", @[]);
            report[@"native_queue_before_binding"] = originalQueue ? [originalQueue description] : @"nil";
            Call(effect, @"setMetalCommandQueue:", @[queue]);
            report[@"native_queue_explicitly_bound"] = @(Call(effect, @"metalCommandQueue", @[]) != nil);
            id executionStatus = Make(@"FigMetalExecutionStatus");
            Call(nativeContext, @"setExecutionStatus:", @[executionStatus]);
            for (NSString *stage in @[@"setup", @"prewarm", @"prepareToProcess:", @"calculateStats", @"process", @"finishProcessing"]) {
                report[@"stage"] = stage; Write(report, out);
                id<MTLCommandBuffer> explicitCommand = nil;
                if ([stage isEqual:@"calculateStats"] || [stage isEqual:@"process"]) {
                    explicitCommand = [queue commandBuffer];
                    explicitCommand.label = [@"Texture producer " stringByAppendingString:stage];
                    Call(nativeContext, @"setCommandBuffer:", @[explicitCommand]);
                }
                NSNumber *status = Call(effect, stage, [stage containsString:@":"] ? @[@0] : @[]);
                report[stage] = status; Write(report, out);
                if ([stage isEqual:@"setup"]) Call(effect, @"setMetalCommandQueue:", @[queue]);
                if ([stage isEqual:@"calculateStats"] || [stage isEqual:@"process"] || [stage isEqual:@"finishProcessing"]) {
                    Call(nativeContext, @"forceCommit", @[]);
                    Call(nativeContext, @"waitForIdle", @[]);
                }
                if (explicitCommand) {
                    if (explicitCommand.status == MTLCommandBufferStatusNotEnqueued || explicitCommand.status == MTLCommandBufferStatusEnqueued) [explicitCommand commit];
                    [explicitCommand waitUntilCompleted];
                    report[[stage stringByAppendingString:@"_command"]] = @{@"status": @(explicitCommand.status), @"error": explicitCommand.error.description ?: @""};
                }
                NSMutableArray *failures = [NSMutableArray new];
                for (id<MTLCommandBuffer> failed in Call(executionStatus, @"failedCommandBuffers", @[]))
                    [failures addObject:@{@"status": @(failed.status), @"error": failed.error.description ?: @"", @"label": failed.label ?: @""}];
                report[@"native_GPU_execution"] = @{@"status": Call(executionStatus, @"status", @[]), @"completed_command_buffers": Call(executionStatus, @"completedCommandBuffersCount", @[]), @"failures": failures};
                Write(report, out);
                @try {
                    NSDictionary *states = [effect valueForKey:@"_perPersonIntermediatesAndStats"];
                    id state = states[@1];
                    if (state) {
                        NSValue *roi = [state valueForKey:@"_extendedFaceROI"];
                        NSMutableDictionary *details = [@{@"extended_face_roi": roi.description ?: @""} mutableCopy];
                        report[@"native_intermediates"] = details;
                    }
                } @catch (NSException *diagnostic) { report[@"intermediate_inspection_error"] = diagnostic.reason ?: @""; }
                report[stage] = status; report[@"native_output_person_stats"] = nativeStats; Write(report, out);
                if (status.intValue != 0) break;
            }
            report[@"stage"] = @"finished";
            if (nativeStats.count && [report[@"process"] intValue] == 0) {
                id effectName = Call(NSClassFromString(@"CMITextureStylesProcessor"), @"effectTypeToEffectName:", @[report[@"native_effect_type"] ?: @3]);
                report[@"native_effect_name"] = effectName;
                Call(person, @"setImageStats:", @[@{effectName: nativeStats}]);
                id normalized = Call(person, @"normalizeRelativeToCropRect:", @[[NSValue valueWithRect:full]]);
                report[@"normalized_person_with_stats"] = Call(normalized, @"dictionaryRepresentation", @[]);
                report[@"statistics_generation_completed"] = @YES;
                if ([effectKind isEqual:@"Mattify"] && [parameterSource isEqual:@"Studio"] && exposure == 0 && ![report[@"calculateStats"] intValue]) {
                    report[@"stage"] = @"render_preview"; Write(report, out);
                    Call(effect, @"setSkipRendering:", @[@NO]);
                    id<MTLCommandBuffer> renderCommand = [queue commandBuffer];
                    Call(nativeContext, @"setCommandBuffer:", @[renderCommand]);
                    report[@"render_calculate_stats_status"] = Call(effect, @"calculateStats", @[]);
                    report[@"render_process_status"] = Call(effect, @"process", @[]);
                    Call(nativeContext, @"forceCommit", @[]);
                    if (renderCommand.status < MTLCommandBufferStatusCommitted) [renderCommand commit];
                    [renderCommand waitUntilCompleted];
                    Call(nativeContext, @"waitForIdle", @[]);
                    report[@"render_command_status"] = @(renderCommand.status);
                    report[@"render_command_error"] = renderCommand.error.description ?: @"";
                    NSMutableData *renderedPixels = [NSMutableData dataWithLength:imagePixels.length];
                    [outputTexture getBytes:renderedPixels.mutableBytes bytesPerRow:width * 8 fromRegion:MTLRegionMake2D(0, 0, width, height) mipmapLevel:0];
                    const __fp16 *renderedValues = renderedPixels.bytes;
                    double absoluteError = 0, maximumError = 0; uint64_t changed = 0, invalid = 0;
                    for (size_t i = 0; i < width * height; i++) {
                        BOOL pixelChanged = NO;
                        for (size_t c = 0; c < 3; c++) {
                            double value = renderedValues[i * 4 + c];
                            if (!isfinite(value)) { invalid++; continue; }
                            double delta = fabs(value - (double)imageValues[i * 4 + c]);
                            absoluteError += delta; maximumError = MAX(maximumError, delta); pixelChanged |= delta > 0.0001;
                        }
                        changed += pixelChanged;
                    }
                    report[@"rendered_pixels"] = @{@"sha256": SHA(renderedPixels), @"mean_absolute_RGB_change": @(absoluteError / (width * height * 3)), @"maximum_RGB_change": @(maximumError), @"changed_pixels_over_0_0001": @(changed), @"nonfinite": @(invalid)};
                    CIImage *preview = [CIImage imageWithMTLTexture:outputTexture options:@{kCIImageColorSpace: (__bridge id)working}];
                    CGImageRef previewImage = [context createCGImage:preview fromRect:full format:kCIFormatRGBA8 colorSpace:srgb];
                    NSString *previewPath = [[out stringByDeletingLastPathComponent] stringByAppendingPathComponent:@"mattify-native-preview.heic"];
                    CGImageDestinationRef previewOut = CGImageDestinationCreateWithURL((__bridge CFURLRef)[NSURL fileURLWithPath:previewPath], CFSTR("public.heic"), 1, NULL);
                    CGImageDestinationAddImage(previewOut, previewImage, (__bridge CFDictionaryRef)@{(__bridge id)kCGImageDestinationLossyCompressionQuality: @0.95});
                    report[@"native_preview_finalized"] = @(CGImageDestinationFinalize(previewOut));
                    CFRelease(previewOut); CGImageRelease(previewImage);
                    report[@"stage"] = @"finished";
                }
            }
            CVPixelBufferRelease(instanceMask); CGImageRelease(image); CFRelease(source);
            CGColorSpaceRelease(srgb); CGColorSpaceRelease(working);
        } @catch (NSException *exception) {
            report[@"exception"] = @{@"name": exception.name, @"reason": exception.reason ?: @""};
        }
        Write(report, out);
        return 0;
    }
}
