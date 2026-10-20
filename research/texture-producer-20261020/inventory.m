#import <Foundation/Foundation.h>
#import <CoreImage/CoreImage.h>
#import <Metal/Metal.h>
#import <objc/runtime.h>
#import <dlfcn.h>

// Observation only: no swizzles, assertion replacements, or system writes.
__attribute__((noinline)) void ProducerDebugReady(void) { __asm__ volatile(""); }

static NSArray *Methods(Class cls) {
    unsigned count = 0;
    Method *methods = class_copyMethodList(cls, &count);
    NSMutableArray *rows = [NSMutableArray new];
    for (unsigned i = 0; i < count; i++) {
        Dl_info location = {0};
        IMP implementation = method_getImplementation(methods[i]);
        dladdr((const void *)implementation, &location);
        [rows addObject:@{
            @"selector": NSStringFromSelector(method_getName(methods[i])),
            @"encoding": @(method_getTypeEncoding(methods[i])),
            @"image": location.dli_fname ? @(location.dli_fname) : @"",
            @"image_offset": @((uintptr_t)implementation - (uintptr_t)location.dli_fbase),
        }];
    }
    free(methods);
    return [rows sortedArrayUsingComparator:^NSComparisonResult(id a, id b) {
        return [a[@"selector"] compare:b[@"selector"]];
    }];
}

static NSDictionary *ClassInfo(Class cls) {
    NSMutableArray *ivars = [NSMutableArray new], *properties = [NSMutableArray new];
    unsigned count = 0;
    Ivar *items = class_copyIvarList(cls, &count);
    for (unsigned i = 0; i < count; i++) [ivars addObject:@{
        @"name": @(ivar_getName(items[i])),
        @"encoding": @(ivar_getTypeEncoding(items[i]) ?: "?"),
        @"offset": @(ivar_getOffset(items[i])),
    }];
    free(items);
    objc_property_t *props = class_copyPropertyList(cls, &count);
    for (unsigned i = 0; i < count; i++) [properties addObject:@{
        @"name": @(property_getName(props[i])), @"attributes": @(property_getAttributes(props[i]))
    }];
    free(props);
    Class parent = class_getSuperclass(cls);
    return @{
        @"class": @(class_getName(cls)), @"superclass": parent ? @(class_getName(parent)) : @"",
        @"instance_size": @(class_getInstanceSize(cls)), @"ivars": ivars, @"properties": properties,
        @"instance_methods": Methods(cls), @"class_methods": Methods(object_getClass(cls)),
    };
}

int main(int argc, char **argv) {
    @autoreleasepool {
        if (argc != 2) return 64;
        NSMutableArray *frameworks = [NSMutableArray new];
        for (NSString *name in @[@"NeutrinoCore", @"PhotoImaging", @"CMImaging", @"CMCapture", @"ANSTKit", @"Vision"]) {
            NSString *root = [name isEqual:@"Vision"] ? @"Frameworks" : @"PrivateFrameworks";
            NSString *path = [NSString stringWithFormat:@"/System/Library/%@/%@.framework/%@", root, name, name];
            void *handle = dlopen(path.UTF8String, RTLD_NOW | RTLD_LOCAL);
            [frameworks addObject:@{@"path": path, @"loaded": @(handle != NULL), @"error": handle ? @"" : @(dlerror() ?: "unknown")}];
        }
        unsigned count = 0;
        Class *classes = objc_copyClassList(&count);
        NSMutableSet<NSString *> *selected = [NSMutableSet new];
        NSMutableArray *candidateNames = [NSMutableArray new];
        NSMutableArray *sourceNames = [NSMutableArray new];
        for (unsigned i = 0; i < count; i++) {
            NSString *name = @(class_getName(classes[i]));
            BOOL fsinc = [name rangeOfString:@"fsinc" options:NSCaseInsensitiveSearch].location != NSNotFound;
            if ([name hasPrefix:@"NU"] || [name hasPrefix:@"_NU"] ||
                [name hasPrefix:@"VNGenerate"] || fsinc ||
                [name containsString:@"SmartStyle"]) [sourceNames addObject:name];
            if ([name containsString:@"AutoCalculator"] || [name containsString:@"TextureStyle"] ||
                [name containsString:@"PersonImageStat"] || [name containsString:@"SemanticStyle"] ||
                [name hasPrefix:@"NURender"] || [name hasPrefix:@"NUImage"] ||
                [name hasPrefix:@"PISemantic"] || [name hasPrefix:@"PIMatte"] ||
                [name hasPrefix:@"_NUImage"] || [name hasPrefix:@"NUURL"] ||
                [name isEqual:@"NUAssetLoader"] || [name hasPrefix:@"_NUCGImage"] || [name isEqual:@"_NUImageAsset"] ||
                [name hasPrefix:@"CMITS"] || [name hasPrefix:@"CMIImageTile"] ||
                [name hasPrefix:@"CMIMetalResource"] || [name hasPrefix:@"FigMetal"] ||
                [name hasPrefix:@"CMIExternalMemory"] ||
                [name hasPrefix:@"VNGenerate"] || [name containsString:@"HumanAttributes"] ||
                [name containsString:@"FaceSegments"] || [name containsString:@"SegmentationObservation"] ||
                [name containsString:@"CompositionController"] || [name hasPrefix:@"NUSource"] ||
                fsinc || [name containsString:@"SmartStyle"]) {
                [candidateNames addObject:name];
                for (Class cls = classes[i]; cls && cls != NSObject.class; cls = class_getSuperclass(cls))
                    [selected addObject:@(class_getName(cls))];
            }
        }
        free(classes);
        // Composition/request objects establish the actual producer input contract.
        for (NSString *name in @[@"NUComposition", @"NUCompositionRequest", @"NUImageSource", @"NUImageProperties", @"NUPipeline", @"NUContext"]) {
            Class cls = NSClassFromString(name);
            if (cls) [selected addObject:name];
        }
        NSMutableArray *rows = [NSMutableArray new];
        for (NSString *name in [[selected allObjects] sortedArrayUsingSelector:@selector(compare:)])
            [rows addObject:ClassInfo(NSClassFromString(name))];
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        NSDictionary *report = @{
            @"schema": @"texture-producer-inventory-v1", @"os": NSProcessInfo.processInfo.operatingSystemVersionString,
            @"device": device.name ?: @"unavailable", @"frameworks": frameworks,
            @"candidate_names": [candidateNames sortedArrayUsingSelector:@selector(compare:)], @"classes": rows,
            @"source_class_names": [sourceNames sortedArrayUsingSelector:@selector(compare:)],
            @"apple_implementation_patched": @NO, @"photos_used": @NO,
        };
        NSError *error = nil;
        NSData *data = [NSJSONSerialization dataWithJSONObject:report options:NSJSONWritingSortedKeys | NSJSONWritingPrettyPrinted error:&error];
        if (!data || ![data writeToFile:@(argv[1]) options:NSDataWritingAtomic error:&error]) {
            fprintf(stderr, "%s\n", error.description.UTF8String); return 1;
        }
        fprintf(stdout, "PRODUCER_INVENTORY classes=%lu file=%s\n", (unsigned long)rows.count, argv[1]);
        fflush(stdout);
        ProducerDebugReady();
        return 0;
    }
}
