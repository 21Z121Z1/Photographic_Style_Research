#import "spi_call.h"
#import <CoreML/CoreML.h>

int main(int argc, char **argv) {
    @autoreleasepool {
        if (argc != 3) return 64;
        NSString *input = @(argv[1]), *out = @(argv[2]);
        NSMutableDictionary *report = [@{
            @"schema": @"texture-fsinc-coreml-v1", @"input_sha256": SHA([NSData dataWithContentsOfFile:input]),
            @"apple_algorithm_patched": @NO, @"model_modified": @NO, @"model_uploaded": @NO,
            @"stage": @"descriptor", @"scope": @"execute installed Apple FSINC through its native model descriptor and CoreML CPU path",
        } mutableCopy];
        Write(report, out);
        @try {
            dlopen("/System/Library/PrivateFrameworks/ANSTKit.framework/ANSTKit", RTLD_NOW | RTLD_LOCAL);
            id config = Call([NSClassFromString(@"ANSTFsincInferenceConfiguration") alloc], @"initWithVersion:resolution:", @[@(0x20190), @2]);
            Class cls = NSClassFromString(@"ANSTFsincInferenceDescriptor");
            Require(cls, @"e5DescriptorWithConfiguration:error:", @[@"@", @"^@"], "@");
            NSError *error = nil;
            id descriptor = ((id(*)(id,SEL,id,NSError **))objc_msgSend)(cls, NSSelectorFromString(@"e5DescriptorWithConfiguration:error:"), config, &error);
            report[@"descriptor_error"] = error.description ?: @"";
            if (!descriptor) @throw [NSException exceptionWithName:@"Descriptor" reason:error.description userInfo:nil];
            NSURL *url = Call(descriptor, @"assetURL", @[]);
            report[@"asset_url"] = url.path ?: @"";
            report[@"asset_type"] = [descriptor valueForKey:@"assetType"];
            report[@"native_input_descriptor"] = [Call(descriptor, @"inputImageDescriptor", @[]) description] ?: @"";
            report[@"native_output_descriptors"] = [Call(descriptor, @"outputDescriptors", @[]) description] ?: @"";
            report[@"stage"] = @"coreml-load-CPUOnly"; Write(report, out);
            MLModelConfiguration *modelConfig = [MLModelConfiguration new];
            modelConfig.computeUnits = MLComputeUnitsCPUOnly;
            MLModel *model = [MLModel modelWithContentsOfURL:url configuration:modelConfig error:&error];
            report[@"model_loaded"] = @(model != nil); report[@"load_error"] = error.description ?: @"";
            Write(report, out);
            if (model) {
                NSDictionary<NSString *, MLFeatureDescription *> *features = model.modelDescription.inputDescriptionsByName;
                NSMutableDictionary *descriptions = [NSMutableDictionary new];
                for (NSString *name in features) descriptions[name] = features[name].description;
                report[@"model_inputs"] = descriptions;
                if (features.count != 1 || features.allValues[0].type != MLFeatureTypeImage)
                    @throw [NSException exceptionWithName:@"InputContract" reason:@"model does not expose exactly one image input" userInfo:nil];
                NSString *featureName = features.allKeys[0];
                MLImageConstraint *constraint = features[featureName].imageConstraint;
                NSInteger width = constraint.pixelsWide, height = constraint.pixelsHigh;
                report[@"model_input_size"] = @[@(width), @(height)];
                report[@"model_input_format"] = @(constraint.pixelFormatType);
                if (width <= 0 || height <= 0 || constraint.pixelFormatType != kCVPixelFormatType_32BGRA)
                    @throw [NSException exceptionWithName:@"InputContract" reason:@"image shape or format differs from native BGRA binding" userInfo:nil];
                CIImage *image = [CIImage imageWithContentsOfURL:[NSURL fileURLWithPath:input]];
                CGFloat scale = MAX(width / image.extent.size.width, height / image.extent.size.height);
                image = [image imageByApplyingTransform:CGAffineTransformMakeScale(scale, scale)];
                image = [image imageByApplyingTransform:CGAffineTransformMakeTranslation((width - image.extent.size.width) / 2 - image.extent.origin.x, (height - image.extent.size.height) / 2 - image.extent.origin.y)];
                CVPixelBufferRef buffer = NULL;
                CVReturn status = CVPixelBufferCreate(NULL, width, height, constraint.pixelFormatType, (__bridge CFDictionaryRef)@{(id)kCVPixelBufferIOSurfacePropertiesKey: @{}}, &buffer);
                report[@"input_allocation_status"] = @(status);
                if (!buffer) @throw [NSException exceptionWithName:@"InputBuffer" reason:@"allocation failed" userInfo:nil];
                CGColorSpaceRef srgb = CGColorSpaceCreateWithName(kCGColorSpaceSRGB);
                [[CIContext contextWithOptions:@{}] render:image toCVPixelBuffer:buffer bounds:CGRectMake(0, 0, width, height) colorSpace:srgb];
                CGColorSpaceRelease(srgb);
                report[@"native_input_buffer"] = BufferFacts(buffer);
                MLDictionaryFeatureProvider *provider = [[MLDictionaryFeatureProvider alloc] initWithDictionary:@{featureName: [MLFeatureValue featureValueWithPixelBuffer:buffer]} error:&error];
                report[@"stage"] = @"coreml-prediction"; Write(report, out);
                id<MLFeatureProvider> prediction = [model predictionFromFeatures:provider error:&error];
                report[@"prediction_returned"] = @(prediction != nil); report[@"prediction_error"] = error.description ?: @"";
                NSMutableDictionary *outputs = [NSMutableDictionary new];
                for (NSString *name in prediction.featureNames) {
                    MLFeatureValue *value = [prediction featureValueForName:name];
                    NSMutableDictionary *details = [@{@"type": @(value.type)} mutableCopy];
                    if (value.type == MLFeatureTypeImage) details[@"buffer"] = BufferFacts(value.imageBufferValue);
                    if (value.type == MLFeatureTypeMultiArray) {
                        MLMultiArray *array = value.multiArrayValue;
                        details[@"shape"] = array.shape; details[@"strides"] = array.strides; details[@"dtype"] = @(array.dataType);
                        double lo = INFINITY, hi = -INFINITY, mean = 0; uint64_t nonfinite = 0;
                        for (NSInteger i = 0; i < array.count; i++) {
                            double v = array[i].doubleValue;
                            if (!isfinite(v)) { nonfinite++; continue; }
                            lo = MIN(lo, v); hi = MAX(hi, v); mean += v / array.count;
                        }
                        details[@"range"] = @[@(lo), @(hi)]; details[@"mean"] = @(mean); details[@"nonfinite"] = @(nonfinite);
                    }
                    outputs[name] = details;
                }
                report[@"outputs"] = outputs;
                CVPixelBufferRelease(buffer);
            }
            report[@"stage"] = @"finished";
        } @catch (NSException *exception) {
            report[@"exception"] = @{@"name": exception.name, @"reason": exception.reason ?: @""};
        }
        Write(report, out);
        return 0;
    }
}
