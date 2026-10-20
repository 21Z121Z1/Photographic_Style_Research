#import "native_common.h"

int main(int argc, char **argv) {
    @autoreleasepool {
        if (argc != 2) return 64;
        NSString *root = @(argv[1]); NSMutableArray *rows = [NSMutableArray new];
        for (NSString *role in @[@"skin", @"face", @"instance"]) {
            NSString *name = [@"stored-" stringByAppendingString:role];
            CGImageSourceRef source = CGImageSourceCreateWithURL((__bridge CFURLRef)[NSURL fileURLWithPath:[root stringByAppendingPathComponent:[name stringByAppendingString:@".heic"]]], NULL);
            CGImageRef image = source ? CGImageSourceCreateImageAtIndex(source, 0, NULL) : NULL;
            if (!image || CGImageGetBitsPerComponent(image) != 8 || CGImageGetBitsPerPixel(image) != 8) {
                Write(@{@"failure": @"native final-mask decoder did not return L8"}, [root stringByAppendingPathComponent:@"final-mask-decode.json"]); return 1;
            }
            size_t width = CGImageGetWidth(image), height = CGImageGetHeight(image), stride = CGImageGetBytesPerRow(image);
            CFDataRef raw = CGDataProviderCopyData(CGImageGetDataProvider(image)); NSMutableData *bytes = [NSMutableData dataWithLength:width * height];
            for (size_t y = 0; y < height; y++) memcpy((uint8_t *)bytes.mutableBytes + y * width, CFDataGetBytePtr(raw) + y * stride, width);
            [bytes writeToFile:[root stringByAppendingPathComponent:[name stringByAppendingString:@".l8"]] atomically:YES];
            [rows addObject:@{@"role": role, @"width": @(width), @"height": @(height), @"sha256": SHA(bytes), @"source": @"original Apple ImageIO decoder reading encoded bytes projected from the final HEIC"}];
            CFRelease(raw); CGImageRelease(image); CFRelease(source);
        }
        Write(@{@"rows": rows}, [root stringByAppendingPathComponent:@"final-mask-decode.json"]); return 0;
    }
}
