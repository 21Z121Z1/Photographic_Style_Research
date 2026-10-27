// Read-only CMISmartStyle runtime availability probe for GitHub macOS runners.
// Does not invoke private rendering methods or process personal photos.
#import <Foundation/Foundation.h>
#import <objc/runtime.h>
#include <dlfcn.h>
#include <sys/utsname.h>

static NSString *StringFromCString(const char *s) {
    return s ? [NSString stringWithUTF8String:s] ?: @"<invalid UTF-8>" : @"";
}

static NSArray<NSDictionary *> *MethodsForClass(Class cls, BOOL classMethods) {
    Class target = classMethods ? object_getClass(cls) : cls;
    unsigned int count = 0;
    Method *methods = class_copyMethodList(target, &count);
    NSMutableArray<NSDictionary *> *result = [NSMutableArray array];
    for (unsigned int i = 0; i < count; ++i) {
        NSString *name = StringFromCString(sel_getName(method_getName(methods[i])));
        if ([name localizedCaseInsensitiveContainsString:@"Unstyled"] ||
            [name localizedCaseInsensitiveContainsString:@"DeltaMap"] ||
            [name localizedCaseInsensitiveContainsString:@"ToneCurve"] ||
            [name localizedCaseInsensitiveContainsString:@"Coefficient"] ||
            [name localizedCaseInsensitiveContainsString:@"LinearThumbnail"] ||
            [name localizedCaseInsensitiveContainsString:@"GainMap"]) {
            [result addObject:@{
                @"selector": name,
                @"type_encoding": StringFromCString(method_getTypeEncoding(methods[i])),
            }];
        }
    }
    free(methods);
    return result;
}

static NSDictionary *ProbeClass(NSString *name) {
    Class cls = NSClassFromString(name);
    if (!cls) {
        return @{@"class_name": name, @"available": @NO};
    }
    NSMutableDictionary *output = [@{
        @"class_name": name,
        @"available": @YES,
        @"image_name": StringFromCString(class_getImageName(cls)),
        @"relevant_instance_methods": MethodsForClass(cls, NO),
        @"relevant_class_methods": MethodsForClass(cls, YES),
    } mutableCopy];
    NSArray<NSString *> *selectors = @[
        @"computeOriginalUnstyledPixelBufferFrom:inputDeltaMapPixelBuffer:inputMetadataDict:outputUnstyledPixelBuffer:",
        @"computeOriginalUnstyledPixelBufferFrom:inputDeltaMapPixelBuffer:inputCoefficientsPixelBuffer:outputUnstyledPixelBuffer:",
        @"computeDeltaMapForSourcePixelBuffer:targetPixelBuffer:coefficientsDict:outputDeltaMapPixelBuffer:",
        @"interpolateCoefficientsFromStartFrameMetadataDict:startFrameTime:endFrameMetadataDict:endFrameTime:frameTimesToInterpolate:",
        @"adjustedGainMapHeadroomForStyle:originalHeadroom:",
    ];
    NSMutableArray *matches = [NSMutableArray array];
    for (NSString *selectorName in selectors) {
        SEL sel = NSSelectorFromString(selectorName);
        Method instance = class_getInstanceMethod(cls, sel);
        Method type = class_getClassMethod(cls, sel);
        if (instance || type) {
            [matches addObject:@{
                @"selector": selectorName,
                @"instance": @(instance != NULL),
                @"class_method": @(type != NULL),
                @"type_encoding": StringFromCString(method_getTypeEncoding(instance ?: type)),
            }];
        }
    }
    output[@"exact_candidate_selectors"] = matches;
    return output;
}

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        if (argc != 2) {
            fprintf(stderr, "usage: smartstyle_spi_probe OUTPUT_JSON\n");
            return 2;
        }

        NSArray<NSString *> *frameworkPaths = @[
            @"/System/Library/PrivateFrameworks/CMImaging.framework/CMImaging",
            @"/System/Library/PrivateFrameworks/CameraImaging.framework/CameraImaging",
            @"/System/Library/PrivateFrameworks/PhotoImaging.framework/PhotoImaging",
            @"/System/Library/VideoProcessors/SmartStyleV1.bundle/SmartStyleV1",
        ];
        NSMutableArray<NSDictionary *> *frameworks = [NSMutableArray array];
        for (NSString *path in frameworkPaths) {
            dlerror();
            void *handle = dlopen(path.fileSystemRepresentation, RTLD_LAZY | RTLD_LOCAL);
            const char *error = handle ? NULL : dlerror();
            [frameworks addObject:@{
                @"path": path,
                @"exists_on_disk": @([[NSFileManager defaultManager] fileExistsAtPath:path]),
                @"dlopen_succeeded": @(handle != NULL),
                @"dlerror": StringFromCString(error),
            }];
            // Keep successful images loaded while introspecting ObjC classes.
        }

        NSArray<NSString *> *classNames = @[
            @"CMISmartStyleUtilitiesV1",
            @"CMISmartStyleProcessorUtilitiesV1",
            @"CMISmartStyleMetalRendererV1",
        ];
        NSMutableArray *classes = [NSMutableArray array];
        for (NSString *name in classNames) {
            [classes addObject:ProbeClass(name)];
        }

        struct utsname systemInfo;
        uname(&systemInfo);
        NSDictionary *result = @{
            @"probe_version": @1,
            @"probe_scope": @"dynamic-library/class/method-presence-only; no private SPI invoked",
            @"os_version": [NSProcessInfo processInfo].operatingSystemVersionString,
            @"architecture": StringFromCString(systemInfo.machine),
            @"frameworks": frameworks,
            @"classes": classes,
        };
        NSError *error = nil;
        NSData *encoded = [NSJSONSerialization dataWithJSONObject:result
                                                       options:NSJSONWritingPrettyPrinted | NSJSONWritingSortedKeys
                                                         error:&error];
        if (!encoded || ![encoded writeToFile:StringFromCString(argv[1])
                                     options:NSDataWritingAtomic error:&error]) {
            fprintf(stderr, "Cannot save JSON: %s\n", error.localizedDescription.UTF8String);
            return 1;
        }
        printf("SMARTSTYLE_SPI_PROBE_JSON_BEGIN\n%s\nSMARTSTYLE_SPI_PROBE_JSON_END\n",
               [[NSString alloc] initWithData:encoded encoding:NSUTF8StringEncoding].UTF8String);
        return 0;
    }
}
