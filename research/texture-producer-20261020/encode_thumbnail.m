#import "native_common.h"

int main(int argc, char **argv) {
    @autoreleasepool {
        if (argc != 2) return 64;
        NSString *directory = @(argv[1]);
        NSDictionary *facts = [NSJSONSerialization JSONObjectWithData:[NSData dataWithContentsOfFile:[directory stringByAppendingPathComponent:@"carrier-production.json"]] options:0 error:NULL];
        size_t width = [facts[@"width"] unsignedLongValue], height = [facts[@"height"] unsignedLongValue];
        NSData *data = [NSData dataWithContentsOfFile:[directory stringByAppendingPathComponent:@"derived-applelog-thumbnail.rgba32f"]];
        if (data.length != width * height * 16) return 1;
        CGColorSpaceRef color = CGColorSpaceCreateWithName(kCGColorSpaceDisplayP3);
        CIImage *image = [CIImage imageWithBitmapData:data bytesPerRow:width * 16 size:CGSizeMake(width, height) format:kCIFormatRGBAf colorSpace:color];
        NSMutableData *neutral = [NSMutableData dataWithLength:512 * 512 * 16];
        for (size_t i = 0; i < 512 * 512; i++) { float *p = ((float *)neutral.mutableBytes) + i * 4; p[0] = p[1] = p[2] = 0.5; p[3] = 1; }
        CIImage *delta = [CIImage imageWithBitmapData:neutral bytesPerRow:512 * 16 size:CGSizeMake(512, 512) format:kCIFormatRGBAf colorSpace:color];
        CIContext *context = [CIContext contextWithOptions:@{kCIContextWorkingColorSpace: NSNull.null}];
        NSMutableArray *rows = [NSMutableArray new];
        for (NSString *name in @[@"linear-thumbnail-codec.heic", @"neutral-delta-codec.heic"]) {
            NSURL *url = [NSURL fileURLWithPath:[directory stringByAppendingPathComponent:name]];
            NSError *error = nil;
            BOOL success = [context writeHEIF10RepresentationOfImage:([name hasPrefix:@"linear"] ? image : delta) toURL:url colorSpace:color options:@{} error:&error];
            [rows addObject:@{@"file": name, @"success": @(success), @"error": error.description ?: @"", @"sha256": SHA([NSData dataWithContentsOfURL:url])}];
            if (!success) { Write(@{@"rows": rows}, [directory stringByAppendingPathComponent:@"thumbnail-codecs.json"]); return 1; }
        }
        Write(@{@"rows": rows, @"derived_context": @YES, @"original_camera_data": @NO}, [directory stringByAppendingPathComponent:@"thumbnail-codecs.json"]);
        CGColorSpaceRelease(color); return 0;
    }
}
