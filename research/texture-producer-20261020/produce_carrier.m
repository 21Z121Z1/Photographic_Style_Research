#import "spi_call.h"

static NSDictionary *Mask(CVPixelBufferRef buffer) {
    size_t w = CVPixelBufferGetWidth(buffer), h = CVPixelBufferGetHeight(buffer), stride = CVPixelBufferGetBytesPerRow(buffer);
    OSType format = CVPixelBufferGetPixelFormatType(buffer);
    if (format != kCVPixelFormatType_OneComponent8 && format != kCVPixelFormatType_OneComponent32Float)
        @throw [NSException exceptionWithName:@"MaskFormat" reason:@(format).description userInfo:nil];
    NSMutableData *data = [NSMutableData dataWithLength:w * h];
    CVPixelBufferLockBaseAddress(buffer, kCVPixelBufferLock_ReadOnly);
    const uint8_t *base = CVPixelBufferGetBaseAddress(buffer);
    for (size_t y = 0; y < h; y++) for (size_t x = 0; x < w; x++) {
        float v = format == kCVPixelFormatType_OneComponent8 ? base[y * stride + x] / 255.0f : ((const float *)(base + y * stride))[x];
        ((uint8_t *)data.mutableBytes)[y * w + x] = (uint8_t)lrintf(fminf(1, fmaxf(0, v)) * 255);
    }
    CVPixelBufferUnlockBaseAddress(buffer, kCVPixelBufferLock_ReadOnly);
    return @{@"data": data, @"width": @(w), @"height": @(h)};
}

static CGImageMetadataRef MatteMetadata(void) {
    CGMutableImageMetadataRef metadata = CGImageMetadataCreateMutable();
    CFErrorRef error = NULL;
    if (!CGImageMetadataRegisterNamespaceForPrefix(metadata, CFSTR("http://ns.apple.com/fsinc/1.0/"), CFSTR("fsincMattes"), &error) ||
        !CGImageMetadataSetValueWithPath(metadata, NULL, CFSTR("fsincMattes:FSINCMatteVersion"), CFSTR("0")))
        @throw [NSException exceptionWithName:@"MatteMetadata" reason:@"namespace or version unavailable" userInfo:nil];
    return metadata;
}

int main(int argc, char **argv) {
    @autoreleasepool {
        if (argc != 3) return 64;
        NSString *input = @(argv[1]), *directory = @(argv[2]);
        [[NSFileManager defaultManager] createDirectoryAtPath:directory withIntermediateDirectories:YES attributes:nil error:NULL];
        NSString *reportPath = [directory stringByAppendingPathComponent:@"carrier-production.json"];
        NSMutableDictionary *report = [@{@"schema": @"texture-derived-carrier-v1", @"input_sha256": SHA([NSData dataWithContentsOfFile:input]), @"original_camera_provenance": @NO, @"apple_implementation_patched": @NO, @"stage": @"begin"} mutableCopy];
        Write(report, reportPath);
        @try {
            CGImageSourceRef source = CGImageSourceCreateWithURL((__bridge CFURLRef)[NSURL fileURLWithPath:input], NULL);
            CGImageRef image = CGImageSourceCreateThumbnailAtIndex(source, 0, (__bridge CFDictionaryRef)@{(__bridge id)kCGImageSourceCreateThumbnailFromImageAlways: @YES, (__bridge id)kCGImageSourceCreateThumbnailWithTransform: @YES, (__bridge id)kCGImageSourceThumbnailMaxPixelSize: @4096});
            if (!image) @throw [NSException exceptionWithName:@"Input" reason:@"upright decode failed" userInfo:nil];
            size_t w = CGImageGetWidth(image), h = CGImageGetHeight(image);
            report[@"width"] = @(w); report[@"height"] = @(h);
            VNImageRequestHandler *handler = [[VNImageRequestHandler alloc] initWithCGImage:image options:@{}];
            VNRequest *attributes = [NSClassFromString(@"VNGenerateHumanAttributesSegmentationRequest") new];
            VNRequest *glasses = [NSClassFromString(@"VNGenerateGlassesSegmentationRequest") new];
            VNGeneratePersonInstanceMaskRequest *instances = [VNGeneratePersonInstanceMaskRequest new];
            VNDetectFaceLandmarksRequest *faces = [VNDetectFaceLandmarksRequest new];
            VNRequest *faceSegments = [NSClassFromString(@"VNGenerateFaceSegmentsRequest") new];
            NSError *error = nil;
            if (![handler performRequests:@[attributes, glasses, instances, faceSegments] error:&error])
                @throw [NSException exceptionWithName:@"Inference" reason:error.description userInfo:nil];
            faces.inputFaceObservations = (NSArray<VNFaceObservation *> *)faceSegments.results;
            if (![handler performRequests:@[faces] error:&error]) @throw [NSException exceptionWithName:@"Inference" reason:error.description userInfo:nil];
            NSMutableDictionary *masks = [NSMutableDictionary new];
            NSDictionary *features = @{@"human_attribute_skin": @"semanticskinmattev2", @"human_attribute_hair": @"semantichairmatte", @"human_attribute_teeth": @"semanticteethmattev2"};
            for (VNPixelBufferObservation *observation in attributes.results) {
                NSString *role = features[[observation valueForKey:@"featureName"]];
                if (role) masks[role] = Mask(observation.pixelBuffer);
            }
            if (glasses.results.count == 1) masks[@"semanticglassesmattev2"] = Mask(((VNPixelBufferObservation *)glasses.results[0]).pixelBuffer);
            if (instances.results.count == 1) {
                VNInstanceMaskObservation *observation = instances.results[0];
                report[@"instance_count"] = @(observation.allInstances.count);
                if (observation.allInstances.count) {
                    CVPixelBufferRef mask = [observation generateScaledMaskForImageForInstances:observation.allInstances fromRequestHandler:handler error:&error];
                    if (!mask) @throw [NSException exceptionWithName:@"InstanceMask" reason:error.description userInfo:nil];
                    masks[@"semanticpersonmatte"] = Mask(mask); CVPixelBufferRelease(mask);
                }
            }
            report[@"face_geometry"] = FaceFacts(faces.results);
            // Declared derived resource: real inferred skin intersected with the
            // measured face bounds; this is not presented as FSINC inference.
            NSDictionary *skin = masks[@"semanticskinmattev2"];
            if (skin && faces.results.count) {
                NSMutableData *data = [skin[@"data"] mutableCopy]; size_t mw = [skin[@"width"] unsignedLongValue], mh = [skin[@"height"] unsignedLongValue];
                for (size_t y = 0; y < mh; y++) for (size_t x = 0; x < mw; x++) {
                    BOOL inside = NO;
                    for (VNFaceObservation *face in faces.results) inside |= CGRectContainsPoint(face.boundingBox, CGPointMake((x + 0.5) / mw, 1 - (y + 0.5) / mh));
                    if (!inside) ((uint8_t *)data.mutableBytes)[y * mw + x] = 0;
                }
                masks[@"semanticfaceskinmatte"] = @{@"data": data, @"width": @(mw), @"height": @(mh)};
                report[@"face_skin_source"] = @"inferred skin intersected with measured face bounds";
            }
            NSMutableArray *resourceRows = [NSMutableArray new];
            for (NSString *name in [[masks allKeys] sortedArrayUsingSelector:@selector(compare:)]) {
                NSDictionary *mask = masks[name]; NSData *bytes = mask[@"data"];
                NSString *file = [name stringByAppendingString:@".l8"];
                [bytes writeToFile:[directory stringByAppendingPathComponent:file] atomically:YES];
                NSString *uri = [name isEqual:@"semantichairmatte"] ? (__bridge NSString *)kCGImageAuxiliaryDataTypeSemanticSegmentationHairMatte : [@"tag:apple.com,2026:photo:aux:" stringByAppendingString:name];
                [resourceRows addObject:@{@"role": name, @"uri": uri, @"file": file, @"width": mask[@"width"], @"height": mask[@"height"], @"sha256": SHA(bytes), @"size": @(bytes.length)}];
            }
            report[@"resources"] = resourceRows;
            NSMutableArray *codecRows = [NSMutableArray new];
            for (NSDictionary *row in resourceRows) {
                // Public ImageIO only writes recognized auxiliary identifiers.
                // Encode each actual mask through its supported L8 carrier; the
                // assembler later assigns that distinct payload its final role.
                NSString *codecFile = [@"codec-" stringByAppendingFormat:@"%@.heic", row[@"role"]];
                NSString *path = [directory stringByAppendingPathComponent:codecFile];
                CGImageDestinationRef destination = CGImageDestinationCreateWithURL((__bridge CFURLRef)[NSURL fileURLWithPath:path], CFSTR("public.heic"), 1, NULL);
                CGImageDestinationAddImage(destination, image, (__bridge CFDictionaryRef)@{(__bridge id)kCGImageDestinationLossyCompressionQuality: @0.95});
                CGMutableImageMetadataRef metadata = CGImageMetadataCreateMutable(); CFErrorRef metadataError = NULL;
                CGImageMetadataRegisterNamespaceForPrefix(metadata, CFSTR("http://ns.apple.com/semanticSegmentationMatte/1.0/"), CFSTR("semanticSegmentationMatte"), &metadataError);
                CGImageMetadataSetValueWithPath(metadata, NULL, CFSTR("semanticSegmentationMatte:SemanticSegmentationMatteVersion"), CFSTR("65536"));
                NSDictionary *mask = masks[row[@"role"]];
                NSDictionary *aux = @{(__bridge id)kCGImageAuxiliaryDataInfoData: mask[@"data"], (__bridge id)kCGImageAuxiliaryDataInfoDataDescription: @{(__bridge id)kCGImagePropertyWidth: row[@"width"], (__bridge id)kCGImagePropertyHeight: row[@"height"], (__bridge id)kCGImagePropertyBytesPerRow: row[@"width"], (__bridge id)kCGImagePropertyPixelFormat: @(kCVPixelFormatType_OneComponent8)}, (__bridge id)kCGImageAuxiliaryDataInfoMetadata: (__bridge id)metadata};
                CGImageDestinationAddAuxiliaryDataInfo(destination, kCGImageAuxiliaryDataTypeSemanticSegmentationSkinMatte, (__bridge CFDictionaryRef)aux);
                BOOL finalized = CGImageDestinationFinalize(destination); CFRelease(destination); CFRelease(metadata);
                CGImageSourceRef encoded = CGImageSourceCreateWithURL((__bridge CFURLRef)[NSURL fileURLWithPath:path], NULL);
                CFDictionaryRef read = encoded ? CGImageSourceCopyAuxiliaryDataInfoAtIndex(encoded, 0, kCGImageAuxiliaryDataTypeSemanticSegmentationSkinMatte) : NULL;
                [codecRows addObject:@{@"role": row[@"role"], @"file": codecFile, @"finalized": @(finalized), @"native_auxiliary_readback": @(read != NULL), @"readback": read ? JSONCompatible((__bridge id)read) : @{}}];
                if (read) CFRelease(read); if (encoded) CFRelease(encoded);
            }
            report[@"native_mask_codec_controls"] = codecRows;
            for (NSString *name in @[@"control.heic", @"inferred-mattes.heic"]) {
                NSString *path = [directory stringByAppendingPathComponent:name];
                CGImageDestinationRef destination = CGImageDestinationCreateWithURL((__bridge CFURLRef)[NSURL fileURLWithPath:path], CFSTR("public.heic"), 1, NULL);
                if (!destination) @throw [NSException exceptionWithName:@"HEIC" reason:@"destination unavailable" userInfo:nil];
                CGImageDestinationAddImage(destination, image, (__bridge CFDictionaryRef)@{(__bridge id)kCGImageDestinationLossyCompressionQuality: @0.95, (__bridge id)kCGImagePropertyOrientation: @1});
                if ([name isEqual:@"inferred-mattes.heic"]) for (NSDictionary *row in resourceRows) {
                    NSDictionary *mask = masks[row[@"role"]]; CGImageMetadataRef metadata = MatteMetadata();
                    NSDictionary *aux = @{(__bridge id)kCGImageAuxiliaryDataInfoData: mask[@"data"], (__bridge id)kCGImageAuxiliaryDataInfoDataDescription: @{(__bridge id)kCGImagePropertyWidth: row[@"width"], (__bridge id)kCGImagePropertyHeight: row[@"height"], (__bridge id)kCGImagePropertyBytesPerRow: row[@"width"], (__bridge id)kCGImagePropertyPixelFormat: @(kCVPixelFormatType_OneComponent8)}, (__bridge id)kCGImageAuxiliaryDataInfoMetadata: (__bridge id)metadata};
                    CGImageDestinationAddAuxiliaryDataInfo(destination, (__bridge CFStringRef)row[@"uri"], (__bridge CFDictionaryRef)aux); CFRelease(metadata);
                }
                BOOL finalized = CGImageDestinationFinalize(destination); CFRelease(destination);
                report[name] = @{@"finalized": @(finalized), @"sha256": SHA([NSData dataWithContentsOfFile:path])};
                if (!finalized) @throw [NSException exceptionWithName:@"HEIC" reason:@"finalization failed" userInfo:nil];
            }
            NSMutableArray *readback = [NSMutableArray new];
            CGImageSourceRef encoded = CGImageSourceCreateWithURL((__bridge CFURLRef)[NSURL fileURLWithPath:[directory stringByAppendingPathComponent:@"inferred-mattes.heic"]], NULL);
            for (NSDictionary *row in resourceRows) {
                CFDictionaryRef aux = CGImageSourceCopyAuxiliaryDataInfoAtIndex(encoded, 0, (__bridge CFStringRef)row[@"uri"]);
                [readback addObject:@{@"role": row[@"role"], @"native_auxiliary_readback": @(aux != NULL), @"data": aux ? JSONCompatible((__bridge NSDictionary *)aux) : @{}}];
                if (aux) CFRelease(aux);
            }
            report[@"readback"] = readback; CFRelease(encoded); CGImageRelease(image); CFRelease(source);
            report[@"stage"] = @"finished";
        } @catch (NSException *exception) { report[@"exception"] = @{@"name": exception.name, @"reason": exception.reason ?: @""}; }
        Write(report, reportPath); return report[@"exception"] ? 1 : 0;
    }
}
