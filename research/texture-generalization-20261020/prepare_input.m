#import "../texture-producer-20261020/native_common.h"

// Decode the immutable source once, apply its orientation, and explicitly make
// a new SDR/sRGB editing raster. This does not preserve an HDR gain map or video.
int main(int argc, char **argv) {
    @autoreleasepool {
        if (argc != 4) return 64;
        NSString *input = @(argv[1]), *directory = @(argv[2]);
        NSUInteger limit = strtoul(argv[3], NULL, 10);
        if (limit < 128 || limit > 4096) return 64;
        [[NSFileManager defaultManager] createDirectoryAtPath:directory withIntermediateDirectories:YES attributes:nil error:NULL];
        NSString *reportPath = [directory stringByAppendingPathComponent:@"input.json"];
        NSMutableDictionary *report = [@{@"schema":@"texture-normalized-input-v1", @"source_sha256":SHA([NSData dataWithContentsOfFile:input]), @"requested_max_dimension":@(limit), @"source_unchanged":@YES, @"output_color_space":@"sRGB, 8-bit SDR", @"HDR_and_motion_preserved":@NO} mutableCopy];
        @try {
            CGImageSourceRef source = CGImageSourceCreateWithURL((__bridge CFURLRef)[NSURL fileURLWithPath:input], NULL);
            if (!source) @throw [NSException exceptionWithName:@"Decode" reason:@"source unavailable" userInfo:nil];
            NSDictionary *props = CFBridgingRelease(CGImageSourceCopyPropertiesAtIndex(source,0,NULL));
            report[@"source_width"] = props[(__bridge id)kCGImagePropertyPixelWidth] ?: @0;
            report[@"source_height"] = props[(__bridge id)kCGImagePropertyPixelHeight] ?: @0;
            report[@"source_orientation"] = props[(__bridge id)kCGImagePropertyOrientation] ?: @1;
            report[@"source_type"] = (__bridge id)CGImageSourceGetType(source);
            CGImageRef decoded = CGImageSourceCreateThumbnailAtIndex(source,0,(__bridge CFDictionaryRef)@{(__bridge id)kCGImageSourceCreateThumbnailFromImageAlways:@YES, (__bridge id)kCGImageSourceCreateThumbnailWithTransform:@YES, (__bridge id)kCGImageSourceThumbnailMaxPixelSize:@(limit)});
            if (!decoded) @throw [NSException exceptionWithName:@"Decode" reason:@"upright thumbnail unavailable" userInfo:nil];
            CGColorSpaceRef srgb = CGColorSpaceCreateWithName(kCGColorSpaceSRGB);
            CIContext *context = [CIContext contextWithOptions:@{}];
            CIImage *ci = [CIImage imageWithCGImage:decoded];
            CGImageRef image = [context createCGImage:ci fromRect:ci.extent format:kCIFormatRGBA8 colorSpace:srgb];
            NSString *path = [directory stringByAppendingPathComponent:@"working.png"];
            CGImageDestinationRef destination = CGImageDestinationCreateWithURL((__bridge CFURLRef)[NSURL fileURLWithPath:path],CFSTR("public.png"),1,NULL);
            CGImageDestinationAddImage(destination,image,(__bridge CFDictionaryRef)@{(__bridge id)kCGImagePropertyOrientation:@1});
            if (!CGImageDestinationFinalize(destination)) @throw [NSException exceptionWithName:@"Encode" reason:@"working PNG failed" userInfo:nil];
            report[@"working_width"] = @(CGImageGetWidth(image)); report[@"working_height"] = @(CGImageGetHeight(image));
            report[@"working_sha256"] = SHA([NSData dataWithContentsOfFile:path]);
            // CGImage provider storage may contain unspecified padding/skip
            // bytes. Hash an initialized, tightly packed canonical RGBA raster.
            size_t pw=CGImageGetWidth(image),ph=CGImageGetHeight(image);
            NSMutableData *pixels=[NSMutableData dataWithLength:pw*ph*4];
            CGContextRef bitmap=CGBitmapContextCreate(pixels.mutableBytes,pw,ph,8,pw*4,srgb,kCGImageAlphaPremultipliedLast|kCGBitmapByteOrder32Big);
            if(!bitmap)@throw [NSException exceptionWithName:@"PixelHash" reason:@"canonical bitmap unavailable" userInfo:nil];
            CGContextDrawImage(bitmap,CGRectMake(0,0,pw,ph),image);CGContextRelease(bitmap);
            report[@"working_native_pixels_sha256"]=SHA(pixels);
            report[@"working_pixel_hash_layout"]=@"tightly packed initialized RGBA8; provider padding and skipped channels excluded";
            VNImageRequestHandler *handler = [[VNImageRequestHandler alloc] initWithCGImage:image options:@{}];
            VNDetectFaceLandmarksRequest *faces = [VNDetectFaceLandmarksRequest new];
            VNGeneratePersonInstanceMaskRequest *instances = [VNGeneratePersonInstanceMaskRequest new];
            NSError *error = nil;
            BOOL success = [handler performRequests:@[faces,instances] error:&error];
            report[@"inference_success"] = @(success); report[@"inference_error"] = error.description ?: @"";
            if (!success) @throw [NSException exceptionWithName:@"Inference" reason:error.description userInfo:nil];
            report[@"face_count"] = @(faces.results.count); report[@"face_geometry"] = FaceFacts(faces.results);
            report[@"instance_count"] = @(instances.results.count ? instances.results[0].allInstances.count : 0);
            report[@"finished"] = @YES;
            CFRelease(destination); CGImageRelease(image); CGColorSpaceRelease(srgb); CGImageRelease(decoded); CFRelease(source);
        } @catch (NSException *e) { report[@"exception"] = @{@"name":e.name,@"reason":e.reason ?: @""}; }
        Write(report,reportPath); return report[@"exception"] ? 1 : 0;
    }
}
