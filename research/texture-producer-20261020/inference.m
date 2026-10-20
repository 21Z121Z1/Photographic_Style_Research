#import <Foundation/Foundation.h>
#import <CoreImage/CoreImage.h>
#import <CoreVideo/CoreVideo.h>
#import <ImageIO/ImageIO.h>
#import <Vision/Vision.h>
#import <CommonCrypto/CommonDigest.h>
#import <objc/message.h>
#import <objc/runtime.h>
#import <dlfcn.h>

#import "native_common.h"

int main(int argc, char **argv) {
    @autoreleasepool {
        if (argc != 4) return 64;
        NSString *mode = @(argv[1]), *input = @(argv[2]), *output = @(argv[3]);
        NSData *source = [NSData dataWithContentsOfFile:input];
        if (!source) return 66;
        NSMutableDictionary *report = [@{
            @"schema": @"texture-image-inference-v1", @"mode": mode,
            @"input_sha256": SHA(source), @"os": NSProcessInfo.processInfo.operatingSystemVersionString,
            @"source_camera_metadata_required": @NO, @"photos_used": @NO,
            @"apple_implementation_patched": @NO, @"stage": @"loaded-source",
        } mutableCopy];
        Write(report, output);
        @try {
            CGImageSourceRef imageSource = CGImageSourceCreateWithData((__bridge CFDataRef)source, NULL);
            if (!imageSource) @throw [NSException exceptionWithName:@"ImageDecode" reason:@"input is not an ImageIO source" userInfo:nil];
            NSDictionary *properties = CFBridgingRelease(CGImageSourceCopyPropertiesAtIndex(imageSource, 0, NULL));
            CGImagePropertyOrientation orientation = [properties[(id)kCGImagePropertyOrientation] unsignedIntValue] ?: kCGImagePropertyOrientationUp;
            CGImageRef image = CGImageSourceCreateImageAtIndex(imageSource, 0, NULL);
            if (!image) @throw [NSException exceptionWithName:@"ImageDecode" reason:@"source image unavailable" userInfo:nil];
            report[@"image_size"] = @[@(CGImageGetWidth(image)), @(CGImageGetHeight(image))];
            report[@"input_exif_orientation"] = @(orientation);
            if ([mode isEqual:@"vision"]) {
                VNImageRequestHandler *handler = [[VNImageRequestHandler alloc] initWithCGImage:image orientation:orientation options:@{}];
                VNDetectFaceLandmarksRequest *faceRequest = [VNDetectFaceLandmarksRequest new];
                NSError *error = nil;
                report[@"stage"] = @"vision-face-request"; Write(report, output);
                BOOL success = [handler performRequests:@[faceRequest] error:&error];
                report[@"face_request_success"] = @(success);
                report[@"face_error"] = error.description ?: @"";
                report[@"face_request_revision"] = @(faceRequest.revision);
                report[@"faces"] = FaceFacts(faceRequest.results);
                report[@"stage"] = @"vision-person-instance-request"; Write(report, output);
                VNGeneratePersonInstanceMaskRequest *instanceRequest = [VNGeneratePersonInstanceMaskRequest new];
                error = nil;
                success = [handler performRequests:@[instanceRequest] error:&error];
                report[@"instance_request_success"] = @(success);
                report[@"instance_error"] = error.description ?: @"";
                NSMutableArray *instances = [NSMutableArray new];
                for (VNInstanceMaskObservation *observation in instanceRequest.results) {
                    NSMutableArray *ids = [NSMutableArray new];
                    [observation.allInstances enumerateIndexesUsingBlock:^(NSUInteger index, BOOL *stop) { (void)stop; [ids addObject:@(index)]; }];
                    error = nil;
                    CVPixelBufferRef scaled = [observation generateScaledMaskForImageForInstances:observation.allInstances fromRequestHandler:handler error:&error];
                    [instances addObject:@{@"instance_ids": ids, @"label_mask": BufferFacts(observation.instanceMask), @"scaled_person_mask": BufferFacts(scaled), @"scaled_error": error.description ?: @""}];
                    if (scaled) CVPixelBufferRelease(scaled);
                }
                report[@"instances"] = instances;
                report[@"stage"] = @"vision-finished";
            } else if ([mode hasPrefix:@"VNGenerate"]) {
                Class requestClass = NSClassFromString(mode);
                if (!requestClass || ![requestClass isSubclassOfClass:VNRequest.class])
                    @throw [NSException exceptionWithName:@"SPIUnavailable" reason:mode userInfo:nil];
                VNRequest *request = [requestClass new];
                VNImageRequestHandler *handler = [[VNImageRequestHandler alloc] initWithCGImage:image orientation:orientation options:@{}];
                NSError *error = nil;
                report[@"stage"] = @"vision-private-request"; Write(report, output);
                BOOL success = [handler performRequests:@[request] error:&error];
                report[@"request_success"] = @(success); report[@"request_error"] = error.description ?: @"";
                report[@"request_revision"] = @(request.revision);
                NSMutableArray *results = [NSMutableArray new];
                for (VNObservation *observation in request.results) {
                    NSMutableDictionary *item = [@{@"class": NSStringFromClass([observation class]), @"confidence": @(observation.confidence)} mutableCopy];
                    if ([observation isKindOfClass:VNPixelBufferObservation.class])
                        item[@"pixel_buffer"] = BufferFacts(((VNPixelBufferObservation *)observation).pixelBuffer);
                    if ([observation isKindOfClass:VNFaceObservation.class]) {
                        item[@"face_geometry"] = FaceFacts(@[(VNFaceObservation *)observation]);
                        id segments = [observation valueForKey:@"faceSegments"];
                        if (segments) {
                            NSMutableDictionary *segmentInfo = [NSMutableDictionary new];
                            for (NSString *key in @[@"numberOfFaceSegments", @"outputBufferWidth", @"outputBufferHeight", @"faceSegmentLabelToProbabilityMap"]) {
                                id value = [segments valueForKey:key];
                                if ([value isKindOfClass:NSNumber.class]) segmentInfo[key] = value;
                                if ([value isKindOfClass:NSDictionary.class]) segmentInfo[[key stringByAppendingString:@"_keys"]] = [value allKeys];
                            }
                            Class segmentClass = [segments class];
                            for (NSString *key in @[@"faceSegmentIndexToFlagMap", @"faceSegmentToSegmentMaskGrayLevelDictionary"]) {
                                Require(segmentClass, key, @[], "@");
                                id mapping = ((id(*)(id,SEL))objc_msgSend)(segmentClass, NSSelectorFromString(key));
                                if ([mapping isKindOfClass:NSDictionary.class]) {
                                    NSMutableDictionary *jsonMap = [NSMutableDictionary new];
                                    for (id mapKey in mapping) jsonMap[[mapKey description]] = mapping[mapKey];
                                    segmentInfo[key] = jsonMap;
                                }
                            }
                            item[@"face_segments"] = segmentInfo;
                        }
                    }
                    NSMutableArray *properties = [NSMutableArray new];
                    for (Class cls = [observation class]; cls && cls != VNObservation.class; cls = class_getSuperclass(cls)) {
                        unsigned count = 0; objc_property_t *list = class_copyPropertyList(cls, &count);
                        for (unsigned i = 0; i < count; i++) {
                            NSString *key = @(property_getName(list[i]));
                            [properties addObject:@{@"name": key, @"attributes": @(property_getAttributes(list[i]))}];
                            @try {
                                id value = [observation valueForKey:key];
                                if ([value isKindOfClass:NSNumber.class] || [value isKindOfClass:NSString.class]) item[key] = value;
                                else if ([value isKindOfClass:NSDictionary.class]) item[[key stringByAppendingString:@"_keys"]] = [value allKeys];
                            } @catch (__unused NSException *ignored) {}
                        }
                        free(list);
                    }
                    item[@"runtime_properties"] = properties;
                    [results addObject:item];
                }
                report[@"results"] = results;
                report[@"stage"] = @"vision-private-finished";
            } else if ([mode isEqual:@"fsinc"]) {
                void *handle = dlopen("/System/Library/PrivateFrameworks/ANSTKit.framework/ANSTKit", RTLD_NOW | RTLD_LOCAL);
                if (!handle) @throw [NSException exceptionWithName:@"FrameworkUnavailable" reason:@(dlerror() ?: "ANSTKit") userInfo:nil];
                Class base = NSClassFromString(@"ANSTFsincAlgorithm"), configClass = NSClassFromString(@"ANSTFsincAlgorithmConfiguration");
                uint64_t version = 0x20190, resolution = 2;
                report[@"requested_version"] = @(version); report[@"requested_resolution"] = @(resolution);
                SEL selector = NSSelectorFromString(@"_concreteClassOfVersion:");
                NSMethodSignature *sig = [(id)base methodSignatureForSelector:selector];
                if (!sig || (strcmp(sig.methodReturnType, "#") && strcmp(sig.methodReturnType, "@")))
                    @throw [NSException exceptionWithName:@"SPIABI" reason:@"_concreteClassOfVersion:" userInfo:nil];
                Class concrete = ((Class(*)(id,SEL,uint64_t))objc_msgSend)(base, selector, version);
                report[@"concrete_class"] = concrete ? NSStringFromClass(concrete) : @"unavailable";
                if (!concrete) @throw [NSException exceptionWithName:@"SPIUnavailable" reason:@"FSINC concrete class unavailable" userInfo:nil];
                id allocation = [configClass alloc];
                Require(allocation, @"initWithVersion:resolution:", @[@"Q", @"Q"], "@");
                id config = ((id(*)(id,SEL,uint64_t,uint64_t))objc_msgSend)(allocation, NSSelectorFromString(@"initWithVersion:resolution:"), version, resolution);
                allocation = [concrete alloc];
                Require(allocation, @"initWithConfiguration:", @[@"@"], "@");
                id algorithm = ((id(*)(id,SEL,id))objc_msgSend)(allocation, NSSelectorFromString(@"initWithConfiguration:"), config);
                report[@"algorithm_initialized"] = @(algorithm != nil);
                report[@"stage"] = @"fsinc-prepare"; Write(report, output);
                Require(algorithm, @"prepareWithError:", @[@"^@"], "B");
                NSError *error = nil;
                BOOL success = ((BOOL(*)(id,SEL,NSError **))objc_msgSend)(algorithm, NSSelectorFromString(@"prepareWithError:"), &error);
                report[@"prepared"] = @(success); report[@"prepare_error"] = error.description ?: @"";
                Write(report, output);
                if (success) {
                    CIImage *ciImage = [[CIImage imageWithCGImage:image] imageByApplyingOrientation:orientation];
                    CGRect extent = ciImage.extent;
                    CGFloat scale = MAX(256.0 / extent.size.width, 256.0 / extent.size.height);
                    ciImage = [ciImage imageByApplyingTransform:CGAffineTransformMakeScale(scale, scale)];
                    extent = ciImage.extent;
                    ciImage = [ciImage imageByApplyingTransform:CGAffineTransformMakeTranslation((256 - extent.size.width) / 2 - extent.origin.x, (256 - extent.size.height) / 2 - extent.origin.y)];
                    CVPixelBufferRef buffer = NULL;
                    CVReturn created = CVPixelBufferCreate(NULL, 256, 256, kCVPixelFormatType_32BGRA, (__bridge CFDictionaryRef)@{(id)kCVPixelBufferIOSurfacePropertiesKey: @{}}, &buffer);
                    report[@"pixel_buffer_status"] = @(created);
                    if (!buffer) @throw [NSException exceptionWithName:@"PixelBuffer" reason:@"input allocation failed" userInfo:nil];
                    CIContext *context = [CIContext contextWithOptions:@{}];
                    CGColorSpaceRef colorSpace = CGColorSpaceCreateWithName(kCGColorSpaceSRGB);
                    [context render:ciImage toCVPixelBuffer:buffer bounds:CGRectMake(0, 0, 256, 256) colorSpace:colorSpace];
                    CGColorSpaceRelease(colorSpace);
                    report[@"bound_image"] = BufferFacts(buffer);
                    report[@"input_transform"] = @"upright sRGB, aspect-fill center crop to 256x256";
                    report[@"stage"] = @"fsinc-bind"; Write(report, output);
                    Require(algorithm, @"bindNetworkInputPixelBuffer:error:", @[@"^{__CVBuffer=}", @"^@"], "B");
                    error = nil;
                    success = ((BOOL(*)(id,SEL,CVPixelBufferRef,NSError **))objc_msgSend)(algorithm, NSSelectorFromString(@"bindNetworkInputPixelBuffer:error:"), buffer, &error);
                    report[@"bound"] = @(success); report[@"bind_error"] = error.description ?: @"";
                    report[@"stage"] = @"fsinc-inference"; Write(report, output);
                    if (success) {
                        Require(algorithm, @"executeInferenceWithError:", @[@"^@"], "@");
                        error = nil;
                        id inference = ((id(*)(id,SEL,NSError **))objc_msgSend)(algorithm, NSSelectorFromString(@"executeInferenceWithError:"), &error);
                        report[@"native_result_class"] = inference ? NSStringFromClass([inference class]) : @"unavailable";
                        report[@"inference_error"] = error.description ?: @"";
                        report[@"inference_returned"] = @(inference != nil);
                        if (inference) {
                            NSMutableArray *masks = [NSMutableArray new];
                            Require(inference, @"outputVisegMaskForCategory:error:", @[@"Q", @"^@"], "^{__CVBuffer=}");
                            for (NSUInteger category = 0; category < 64; category++) {
                                error = nil;
                                CVPixelBufferRef mask = ((CVPixelBufferRef(*)(id,SEL,NSUInteger,NSError **))objc_msgSend)(inference, NSSelectorFromString(@"outputVisegMaskForCategory:error:"), category, &error);
                                if (mask) [masks addObject:@{@"category": @(category), @"buffer": BufferFacts(mask)}];
                            }
                            report[@"semantic_masks"] = masks;
                        }
                    }
                    CVPixelBufferRelease(buffer);
                }
                report[@"stage"] = @"fsinc-finished";
            } else @throw [NSException exceptionWithName:@"Usage" reason:@"unknown inference mode" userInfo:nil];
            CGImageRelease(image); CFRelease(imageSource);
        } @catch (NSException *exception) {
            report[@"exception"] = @{@"name": exception.name, @"reason": exception.reason ?: @""};
        }
        Write(report, output);
        return 0;
    }
}
