#import "spi_call.h"

int main(int argc, char **argv) {
    @autoreleasepool {
        if (argc != 3) return 64;
        NSMutableDictionary *report = [@{@"schema": @"texture-native-admission-v1", @"input_sha256": SHA([NSData dataWithContentsOfFile:@(argv[1])]), @"photos_UI_tested": @NO, @"capabilities_injected": @NO} mutableCopy];
        @try {
            dlopen("/System/Library/PrivateFrameworks/NeutrinoCore.framework/NeutrinoCore", RTLD_NOW | RTLD_LOCAL);
            dlopen("/System/Library/PrivateFrameworks/PhotoImaging.framework/PhotoImaging", RTLD_NOW | RTLD_LOCAL);
            id source = Call(NSClassFromString(@"NUSourceDefinition"), @"imageSourceDefinitionWithURL:options:", @[[NSURL fileURLWithPath:@(argv[1])], @{}]);
            NSError *error = nil;
            id asset = Call(source, @"assetWithOptions:error:", @[@{}, [NSValue valueWithPointer:&error]]);
            report[@"asset_loaded"] = @(asset != nil); report[@"asset_error"] = error.description ?: @"";
            if (asset) {
                report[@"asset_class"] = NSStringFromClass([asset class]);
                if ([asset respondsToSelector:NSSelectorFromString(@"loadWithOptions:error:")]) report[@"load"] = Call(asset, @"loadWithOptions:error:", @[@{}, [NSValue valueWithPointer:&error]]);
                report[@"capabilities"] = Call(asset, @"capabilities", @[]);
                report[@"PhotographicStyleV2"] = Call(asset, @"hasCapability:", @[@"PhotographicStyleV2"]);
                report[@"PhotographicStyle"] = Call(asset, @"hasCapability:", @[@"PhotographicStyle"]);
                id media = Call(asset, @"media", @[]);
                report[@"media_description"] = [media description] ?: @"";
                for (NSString *key in @[@"imageProperties", @"properties", @"textureStyleProperties", @"metadata", @"rawProperties"])
                    if ([media respondsToSelector:NSSelectorFromString(key)]) {
                        id value = Call(media, key, @[]); report[key] = JSONCompatible(value);
                        if ([key isEqual:@"properties"] || [key isEqual:@"imageProperties"]) {
                            if ([value respondsToSelector:NSSelectorFromString(@"textureStyleProperties")]) {
                                id texture = Call(value, @"textureStyleProperties", @[]);
                                report[@"texture_properties_present"] = @(texture != nil);
                                if (texture) report[@"texture_person_count"] = Call(texture, @"numberOfPersons", @[]);
                            }
                        }
                    }
            }
            id schema = Call(NSClassFromString(@"PICompositionController"), @"photosSchema", @[]);
            id composition = Call([NSClassFromString(@"NUComposition") alloc], @"initWithCompositionSchema:", @[schema]);
            Call(composition, @"setObject:forKeyedSubscript:", @[source, @"source"]);
            report[@"canRenderTextureStylesOnComposition"] = Call(NSClassFromString(@"PITextureStyleAutoCalculator"), @"canRenderTextureStylesOnComposition:", @[composition]);
        } @catch (NSException *exception) { report[@"exception"] = @{@"name": exception.name, @"reason": exception.reason ?: @""}; }
        Write(report, @(argv[2])); return 0;
    }
}
