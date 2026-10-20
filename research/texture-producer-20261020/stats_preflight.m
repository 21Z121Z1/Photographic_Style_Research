#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#import <CoreVideo/CoreVideo.h>
#import <objc/runtime.h>
#import <objc/message.h>
#import <dlfcn.h>

static void Save(NSDictionary *report, NSString *path) {
    NSData *data = [NSJSONSerialization dataWithJSONObject:report options:NSJSONWritingPrettyPrinted | NSJSONWritingSortedKeys error:NULL];
    if (!data || ![data writeToFile:path atomically:YES]) exit(1);
}

static BOOL ABI(id object, const char *name, NSArray<NSString *> *args, const char *ret) {
    NSMethodSignature *signature = [object methodSignatureForSelector:sel_registerName(name)];
    if (!signature || signature.numberOfArguments != args.count + 2 || strcmp(signature.methodReturnType, ret)) return NO;
    for (NSUInteger i = 0; i < args.count; i++) if (strcmp([signature getArgumentTypeAtIndex:i + 2], args[i].UTF8String)) return NO;
    return YES;
}

int main(int argc, char **argv) {
    @autoreleasepool {
        if (argc != 3) return 64;
        NSString *name = @(argv[1]), *out = @(argv[2]);
        dlopen("/System/Library/PrivateFrameworks/CMImaging.framework/CMImaging", RTLD_NOW | RTLD_LOCAL);
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        NSMutableDictionary *report = [@{
            @"schema": @"texture-statistics-preflight-v1", @"class": name,
            @"device": device.name ?: @"unavailable", @"apple_implementation_patched": @NO,
            @"stage": @"device", @"scope": @"original statistics effect initialization only; no stats result claimed",
        } mutableCopy];
        Save(report, out);
        @try {
            MTLResidencySetDescriptor *descriptor = [MTLResidencySetDescriptor new];
            NSError *error = nil;
            id<MTLResidencySet> residency = [device newResidencySetWithDescriptor:descriptor error:&error];
            report[@"public_residency_set_created"] = @(residency != nil);
            report[@"public_residency_error"] = error.description ?: @"";
            CVMetalTextureCacheRef cache = NULL;
            CVReturn status = CVMetalTextureCacheCreate(NULL, NULL, device, NULL, &cache);
            report[@"public_CVMetalTextureCache_status"] = @(status);
            if (cache) CFRelease(cache);
            Class effectClass = NSClassFromString(name);
            id allocation = [effectClass alloc];
            if (!ABI(allocation, "initWithOptionalMetalContext:", @[@"@"], "@")) @throw [NSException exceptionWithName:@"SPIABI" reason:@"effect initializer" userInfo:nil];
            report[@"stage"] = @"effect-init"; Save(report, out);
            id effect = ((id(*)(id,SEL,id))objc_msgSend)(allocation, sel_registerName("initWithOptionalMetalContext:"), nil);
            report[@"initialized"] = @(effect != nil); Save(report, out);
            if (effect) {
                for (NSString *method in @[@"setup", @"prewarm"]) {
                    report[@"stage"] = method; Save(report, out);
                    if (!ABI(effect, method.UTF8String, @[], "i")) @throw [NSException exceptionWithName:@"SPIABI" reason:method userInfo:nil];
                    int result = ((int(*)(id,SEL))objc_msgSend)(effect, NSSelectorFromString(method));
                    report[method] = @(result); Save(report, out);
                    if (result != 0) break;
                }
            }
            report[@"stage"] = @"finished";
        } @catch (NSException *exception) {
            report[@"exception"] = @{@"name": exception.name, @"reason": exception.reason ?: @""};
        }
        Save(report, out);
        return 0;
    }
}
