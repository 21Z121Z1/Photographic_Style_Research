#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#import <CommonCrypto/CommonDigest.h>
#include <dlfcn.h>

static NSString *Sha(NSData *data) {
    unsigned char digest[CC_SHA256_DIGEST_LENGTH];
    CC_SHA256(data.bytes, (CC_LONG)data.length, digest);
    NSMutableString *value = [NSMutableString new];
    for (NSUInteger i=0; i<sizeof(digest); ++i) [value appendFormat:@"%02x", digest[i]];
    return value;
}

int main(void) { @autoreleasepool {
    id<MTLDevice> device = MTLCreateSystemDefaultDevice();
    NSMutableDictionary *report = [@{@"schema":@"psr-native-capabilities-v1",
        @"os":NSProcessInfo.processInfo.operatingSystemVersionString,
        @"metal_available":@(device != nil), @"device":device.name ?: @"unavailable",
        @"private_photographs_used":@NO, @"GPU_dispatches":@0} mutableCopy];
    NSMutableArray *frameworks = [NSMutableArray new];
    for (NSString *name in @[@"CMImaging", @"PhotoImaging", @"CMCapture"]) {
        NSString *path = [NSString stringWithFormat:@"/System/Library/PrivateFrameworks/%@.framework/%@", name, name];
        void *handle = dlopen(path.UTF8String, RTLD_NOW | RTLD_LOCAL);
        [frameworks addObject:@{@"name":name, @"loaded":@(handle != NULL)}];
    }
    report[@"frameworks"] = frameworks;
    NSString *path = @"/System/Library/PrivateFrameworks/CMImaging.framework/Resources/default.metallib";
    NSData *data = [NSData dataWithContentsOfFile:path];
    report[@"library_path"] = path;
    report[@"library_exists"] = @(data != nil);
    if (data) report[@"library_sha256"] = Sha(data);
    NSError *error = nil;
    id<MTLLibrary> library = device && data ? [device newLibraryWithFile:path error:&error] : nil;
    report[@"library_loaded"] = @(library != nil);
    report[@"library_error"] = error.localizedDescription ?: @"";
    NSMutableArray *functions = [NSMutableArray new];
    for (NSString *name in library.functionNames) {
        if ([name containsString:@"TextureStyle"] || [name containsString:@"SmartStyle"] ||
            [name containsString:@"smartStyle"]) [functions addObject:name];
    }
    report[@"selected_function_names"] = [functions sortedArrayUsingSelector:@selector(compare:)];
    NSData *json = [NSJSONSerialization dataWithJSONObject:report options:NSJSONWritingSortedKeys error:&error];
    if (!json) return 2;
    fwrite(json.bytes, 1, json.length, stdout);
    fputc('\n', stdout);
    return 0;
}}
