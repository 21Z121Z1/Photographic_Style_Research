#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#import <CommonCrypto/CommonDigest.h>

static NSString *Sha(NSData *data) {
    unsigned char digest[CC_SHA256_DIGEST_LENGTH];
    CC_SHA256(data.bytes, (CC_LONG)data.length, digest);
    NSMutableString *value = [NSMutableString new];
    for (NSUInteger i=0; i<sizeof(digest); ++i) [value appendFormat:@"%02x", digest[i]];
    return value;
}

static id<MTLTexture> Texture(id<MTLDevice> device, NSUInteger width, NSUInteger height,
                              MTLPixelFormat format, NSData *bytes) {
    MTLTextureDescriptor *desc = [MTLTextureDescriptor texture2DDescriptorWithPixelFormat:format
        width:width height:height mipmapped:NO];
    desc.storageMode = MTLStorageModeShared;
    desc.usage = MTLTextureUsageShaderRead | MTLTextureUsageShaderWrite;
    id<MTLTexture> texture = [device newTextureWithDescriptor:desc];
    if (bytes) [texture replaceRegion:MTLRegionMake2D(0,0,width,height) mipmapLevel:0
                          withBytes:bytes.bytes bytesPerRow:bytes.length/height];
    return texture;
}

static void Observe(NSString *manifestPath, NSMutableDictionary *report) {
    NSError *error = nil;
    NSData *manifestBytes = [NSData dataWithContentsOfFile:manifestPath];
    NSDictionary *manifest = manifestBytes ? [NSJSONSerialization JSONObjectWithData:manifestBytes options:0 error:&error] : nil;
    if (!manifest) { report[@"error"] = @"input manifest unavailable"; return; }
    NSUInteger width = [manifest[@"width"] unsignedIntegerValue], height = [manifest[@"height"] unsignedIntegerValue];
    if (!width || width > 32 || !height || height > 32) { report[@"error"] = @"unsupported input dimensions"; return; }
    report[@"input_manifest_sha256"] = Sha(manifestBytes);
    report[@"width"] = @(width); report[@"height"] = @(height);
    id<MTLDevice> device = MTLCreateSystemDefaultDevice();
    report[@"device"] = device.name ?: @"unavailable";
    if (!device) { report[@"error"] = @"Metal device unavailable"; return; }
    NSString *path = @"/System/Library/PrivateFrameworks/CMImaging.framework/Resources/default.metallib";
    NSData *libraryBytes = [NSData dataWithContentsOfFile:path];
    NSString *expected = @"16a8a119e3e0ae1649d32b2bbc8ea9136cb757a8d1f3eb451025821901edff11";
    report[@"library_sha256"] = libraryBytes ? Sha(libraryBytes) : @"unavailable";
    if (![report[@"library_sha256"] isEqual:expected]) { report[@"error"] = @"library identity differs from the predeclared ABI"; return; }
    id<MTLLibrary> library = [device newLibraryWithFile:path error:&error];
    MTLFunctionConstantValues *constants = [MTLFunctionConstantValues new];
    BOOL imageblocks = NO;
    [constants setConstantValue:&imageblocks type:MTLDataTypeBool atIndex:16];
    NSString *name = @"CMITextureStylesUnderEyeBrighten::FinalMix";
    report[@"function"] = name; report[@"function_constant_16"] = @NO;
    id<MTLFunction> function = [library newFunctionWithName:name constantValues:constants error:&error];
    MTLComputePipelineReflection *reflection = nil;
    id<MTLComputePipelineState> pipeline = function ? [device newComputePipelineStateWithFunction:function
        options:MTLPipelineOptionArgumentInfo | MTLPipelineOptionBufferTypeInfo reflection:&reflection error:&error] : nil;
    if (!pipeline) { report[@"error"] = error.localizedDescription ?: @"pipeline unavailable"; return; }
    NSMutableArray *arguments = [NSMutableArray new];
    NSSet *textures = [NSSet setWithArray:@[@0,@1,@2,@3,@4,@5,@6,@7,@8,@14,@15]];
    NSSet *buffers = [NSSet setWithArray:@[@3,@18,@13,@23,@22,@4,@5,@7,@8,@9,@6,@10]];
    NSMutableSet *observedTextures = [NSMutableSet new];
    for (MTLArgument *argument in reflection.arguments) {
        NSMutableDictionary *row = [@{@"name":argument.name, @"index":@(argument.index),
            @"type":@(argument.type), @"active":@(argument.active), @"access":@(argument.access)} mutableCopy];
        if (argument.type == MTLArgumentTypeBuffer) row[@"buffer_bytes"] = @(argument.bufferDataSize);
        if (argument.type == MTLArgumentTypeTexture) row[@"texture_type"] = @(argument.textureType);
        [arguments addObject:row];
        if (!argument.active) continue;
        if (argument.type == MTLArgumentTypeTexture && [textures containsObject:@(argument.index)] &&
            argument.textureType == MTLTextureType2D) [observedTextures addObject:@(argument.index)];
        else if (argument.type == MTLArgumentTypeBuffer && [buffers containsObject:@(argument.index)]) {
            NSUInteger suppliedBytes = argument.index == 3 ? 52 : argument.index == 18 ? 48 : 16;
            if (argument.bufferDataSize > suppliedBytes) { report[@"error"] = @"active buffer ABI exceeds declared storage"; report[@"arguments"] = arguments; return; }
        } else { report[@"error"] = @"unexpected active argument ABI"; report[@"arguments"] = arguments; return; }
    }
    report[@"arguments"] = arguments;
    if (![observedTextures containsObject:@0] || ![observedTextures containsObject:@1] ||
        ![observedTextures containsObject:@15]) { report[@"error"] = @"required RGB texture ABI unavailable"; return; }
    if (pipeline.maxTotalThreadsPerThreadgroup < 256) { report[@"error"] = @"16x16 dispatch unsupported"; return; }
    id<MTLCommandQueue> queue = [device newCommandQueue];
    NSMutableArray *rows = [NSMutableArray new]; report[@"rows"] = rows;
    NSArray *maskNames = @[@"instance",@"hair",@"face",@"lips",@"ears",@"tattoo",@"glasses"];
    NSString *inputRoot = manifestPath.stringByDeletingLastPathComponent;
    for (NSDictionary *test in manifest[@"cases"]) { @autoreleasepool {
        NSMutableDictionary *inputs = [NSMutableDictionary new], *hashes = [NSMutableDictionary new];
        for (NSString *key in @[@"source",@"edited",@"instance",@"hair",@"face",@"lips",@"ears",@"tattoo",@"glasses",@"blend"]) {
            NSData *data = [NSData dataWithContentsOfFile:[inputRoot stringByAppendingPathComponent:test[@"files"][key]]];
            BOOL rgb = [key isEqual:@"source"] || [key isEqual:@"edited"];
            if (data.length != width*height*(rgb ? 8 : 2)) { report[@"error"] = @"synthetic input byte count mismatch"; return; }
            inputs[key] = Texture(device,width,height,rgb ? MTLPixelFormatRGBA16Float : MTLPixelFormatR16Float,data);
            hashes[key] = Sha(data);
        }
        NSMutableData *initial = [NSMutableData dataWithLength:width*height*8];
        for (NSUInteger i=0; i<width*height*4; ++i) ((__fp16 *)initial.mutableBytes)[i] = -99;
        id<MTLTexture> output = Texture(device,width,height,MTLPixelFormatRGBA16Float,initial);
        float params[13] = {0}, stats[12] = {0}, roi[4] = {0,0,1,1};
        params[2] = [test[@"brightness_mix"] floatValue]; stats[3] = [test[@"strength"] floatValue];
        id<MTLCommandBuffer> command = [queue commandBuffer];
        id<MTLComputeCommandEncoder> encoder = [command computeCommandEncoder];
        [encoder setComputePipelineState:pipeline];
        [encoder setTexture:inputs[@"source"] atIndex:0]; [encoder setTexture:output atIndex:1];
        for (NSUInteger i=0; i<maskNames.count; ++i) [encoder setTexture:inputs[maskNames[i]] atIndex:i+2];
        [encoder setTexture:inputs[@"blend"] atIndex:14]; [encoder setTexture:inputs[@"edited"] atIndex:15];
        [encoder setBytes:params length:sizeof(params) atIndex:3];
        [encoder setBytes:stats length:sizeof(stats) atIndex:18];
        for (NSNumber *index in @[@13,@23,@22,@4,@5,@7,@8,@9,@6,@10]) [encoder setBytes:roi length:sizeof(roi) atIndex:index.unsignedIntegerValue];
        [encoder dispatchThreads:MTLSizeMake(width,height,1) threadsPerThreadgroup:MTLSizeMake(16,16,1)];
        [encoder endEncoding]; [command commit]; [command waitUntilCompleted];
        report[@"GPU_dispatches"] = @([report[@"GPU_dispatches"] unsignedIntegerValue]+1);
        if (command.error || command.status != MTLCommandBufferStatusCompleted) { report[@"error"] = command.error.localizedDescription ?: @"command not completed"; return; }
        NSMutableData *data = [NSMutableData dataWithLength:width*height*8];
        [output getBytes:data.mutableBytes bytesPerRow:width*8 fromRegion:MTLRegionMake2D(0,0,width,height) mipmapLevel:0];
        [rows addObject:@{@"name":test[@"name"], @"input_sha256":hashes,
            @"params_sha256":Sha([NSData dataWithBytes:params length:sizeof(params)]),
            @"stats_sha256":Sha([NSData dataWithBytes:stats length:sizeof(stats)]),
            @"output_sha256":Sha(data), @"output_f16_base64":[data base64EncodedStringWithOptions:0],
            @"command_status":@(command.status)}];
    }}
    report[@"library_unchanged"] = @([Sha([NSData dataWithContentsOfFile:path]) isEqual:expected]);
    report[@"status"] = @"native_under_eye_final_mix_completed";
}

int main(int argc, char **argv) { @autoreleasepool {
    if (argc != 2) return 2;
    NSMutableDictionary *report = [@{@"schema":@"psr-native-under-eye-v1", @"status":@"blocked",
        @"GPU_dispatches":@0, @"full_Texture_pipeline_verified":@NO, @"Apple_capture_order_verified":@NO} mutableCopy];
    @try { Observe(@(argv[1]),report); }
    @catch (NSException *exception) { report[@"error"] = exception.description; report[@"status"] = @"exception"; }
    NSData *json = [NSJSONSerialization dataWithJSONObject:report options:NSJSONWritingSortedKeys error:NULL];
    if (!json) return 3;
    fwrite(json.bytes,1,json.length,stdout); fputc('\n',stdout);
    return 0;
}}
