#import "native_common.h"

int main(int argc, char **argv) {
    @autoreleasepool {
        if (argc != 2) return 64;
        NSString *root = @(argv[1]); NSMutableArray *rows = [NSMutableArray new];
        for (NSString *role in @[@"skin", @"face", @"instance"]) {
            NSString *name = [@"stored-" stringByAppendingString:role];
            CGImageSourceRef source = CGImageSourceCreateWithURL((__bridge CFURLRef)[NSURL fileURLWithPath:[root stringByAppendingPathComponent:[name stringByAppendingString:@".heic"]]], NULL);
            CGImageRef image = source ? CGImageSourceCreateImageAtIndex(source, 0, NULL) : NULL;
            size_t bits = image ? CGImageGetBitsPerPixel(image) : 0;
            if (!image || CGImageGetBitsPerComponent(image) != 8 || !(bits == 8 || bits == 24 || bits == 32)) {
                Write(@{@"failure": @"unsupported native grayscale projection representation", @"bits_per_pixel": @(bits), @"bits_per_component": @(image ? CGImageGetBitsPerComponent(image) : 0)}, [root stringByAppendingPathComponent:@"final-mask-decode.json"]); return 1;
            }
            size_t width = CGImageGetWidth(image), height = CGImageGetHeight(image), stride = CGImageGetBytesPerRow(image);
            CFDataRef raw = CGDataProviderCopyData(CGImageGetDataProvider(image)); NSMutableData *bytes = [NSMutableData dataWithLength:width * height];
            size_t pixelBytes = bits / 8;
            // Standalone ImageIO can expose the scalar HEVC matte as RGB.
            // Its middle byte is a color channel in RGB/BGR and every 32-bit
            // RGB layout, independent of the alpha byte at either end.
            for (size_t y = 0; y < height; y++) for (size_t x = 0; x < width; x++)
                ((uint8_t *)bytes.mutableBytes)[y * width + x] = CFDataGetBytePtr(raw)[y * stride + x * pixelBytes + (pixelBytes == 1 ? 0 : 1)];
            [bytes writeToFile:[root stringByAppendingPathComponent:[name stringByAppendingString:@".l8"]] atomically:YES];
            [rows addObject:@{@"role": role, @"width": @(width), @"height": @(height), @"sha256": SHA(bytes), @"native_bits_per_pixel": @(bits), @"exported_probability_channel": pixelBytes == 1 ? @"scalar L8" : @"a native decoded grayscale RGB channel", @"source": @"original Apple ImageIO decoder reading encoded bytes projected from the final HEIC"}];
            CFRelease(raw); CGImageRelease(image); CFRelease(source);
        }
        Write(@{@"rows": rows}, [root stringByAppendingPathComponent:@"final-mask-decode.json"]); return 0;
    }
}
