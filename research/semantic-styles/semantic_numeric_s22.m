// S22 public synthetic contract probe. No camera images, mattes, metadata, or private inputs.
// Compiles the original Apple renderFinalAdjustments PSO with S19 function constants.
// The three math modes apply ONLY to self-authored probes, not Apple's metallib.
#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#import <CommonCrypto/CommonDigest.h>
#include <math.h>
#include <stdint.h>
#include <string.h>

static void Save(id obj, NSString *path) {
    NSError *error = nil;
    NSData *data = [NSJSONSerialization dataWithJSONObject:obj
        options:NSJSONWritingPrettyPrinted|NSJSONWritingSortedKeys error:&error];
    if (!data || ![data writeToFile:path options:NSDataWritingAtomic error:&error]) {
        NSLog(@"S22 JSON write failed: %@", error); exit(10);
    }
}
static NSString *Hash(NSData *data) {
    if (!data) return @"missing";
    uint8_t h[32]; CC_SHA256(data.bytes, (CC_LONG)data.length, h);
    NSMutableString *s = [NSMutableString new];
    for (int i=0;i<32;i++) [s appendFormat:@"%02x", h[i]];
    return s;
}
static id<MTLComputePipelineState> Pipeline(id<MTLDevice> device,
    id<MTLLibrary> lib, NSString *name, NSError **error) {
    id<MTLFunction> fn = [lib newFunctionWithName:name];
    return fn ? [device newComputePipelineStateWithFunction:fn error:error] : nil;
}
static NSArray *Vector(const float *x, NSUInteger count) {
    NSMutableArray *a=[NSMutableArray arrayWithCapacity:count];
    for(NSUInteger i=0;i<count;i++) {
        if(!isfinite(x[i])) return @[];
        [a addObject:@(x[i])];
    }
    return a;
}

int main(int argc, char **argv) {
 @autoreleasepool {
    if (argc != 2) return 2;
    NSString *dir = @(argv[1]);
    [[NSFileManager defaultManager] createDirectoryAtPath:dir
       withIntermediateDirectories:YES attributes:nil error:NULL];
    id<MTLDevice> device=MTLCreateSystemDefaultDevice();
    if (!device) { Save(@{@"error":@"no Metal device"}, [dir stringByAppendingPathComponent:@"s22.json"]); return 3; }
    NSError *error=nil;
    NSString *path=@"/System/Library/PrivateFrameworks/CMImaging.framework/Resources/default.metallib";
    NSData *metalBytes=[NSData dataWithContentsOfFile:path];
    id<MTLLibrary> orig=[device newLibraryWithFile:path error:&error];
    MTLFunctionConstantValues *fc=[MTLFunctionConstantValues new];
    BOOL useImageBlock=NO; int useSrlVersion=0;
    [fc setConstantValue:&useImageBlock type:MTLDataTypeBool atIndex:0];
    [fc setConstantValue:&useSrlVersion type:MTLDataTypeInt atIndex:1];
    id<MTLFunction> origFn=[orig newFunctionWithName:@"renderFinalAdjustments" constantValues:fc error:&error];
    id<MTLComputePipelineState> originalPSO=origFn?[device newComputePipelineStateWithFunction:origFn error:&error]:nil;
    if(!originalPSO){
        Save(@{@"error":error.description?:@"Original PSO missing"},
          [dir stringByAppendingPathComponent:@"s22.json"]);return 4;
    }
    NSString *source=
    @"#include <metal_stdlib>\n"
    @"using namespace metal;\n"
    @"kernel void numeric(const device float2 *x[[buffer(0)]], device float4 *y[[buffer(1)]], uint i[[thread_position_in_grid]]) {\n"
    @" float a=x[i].x, b=x[i].y; half ha=half(a), hb=half(b);\n"
    @" half hp=pow(ha,hb); float fp=pow(a,b);\n"
    @" float cancel=(a+16777216.0f)-16777216.0f;\n"
    @" half hcancel=(ha+half(2048.0f))-half(2048.0f);\n"
    @" y[i]=float4(float(hp),fp,cancel,float(hcancel));}\n"
    @"kernel void sampling(texture2d<half,access::sample> t[[texture(0)]], sampler s[[sampler(0)]],\n"
    @" const device float2 *uv[[buffer(0)]], device float4 *y[[buffer(1)]],uint i[[thread_position_in_grid]]) {\n"
    @" y[i]=float4(t.sample(s,uv[i]));}\n";
    // 8 declared, positive-domain half/float pow probes; no photos.
    const float pairs[]={1.f,.5f, 2.f,2.f, 1.5f,.5f, 0.5f,1.5f,
                         4.f,-1.f, 1.0009765625f,3.f, .25f,1.f, 8.f,.333333343f};
    const int n=8;
    id<MTLBuffer> input=[device newBufferWithBytes:pairs length:sizeof(pairs)
                                             options:MTLResourceStorageModeShared];
    id<MTLBuffer> output=[device newBufferWithLength:n*4*sizeof(float)
                                             options:MTLResourceStorageModeShared];
    id<MTLCommandQueue> queue=[device newCommandQueue];
    NSMutableArray *modeRows=[NSMutableArray new];
    for(int mode=0;mode<3;mode++) {
        MTLCompileOptions *opts=[MTLCompileOptions new];
        opts.mathMode=mode==0?MTLMathModeSafe:(mode==1?MTLMathModeRelaxed:MTLMathModeFast);
        opts.mathFloatingPointFunctions=MTLMathFloatingPointFunctionsPrecise;
        error=nil;
        id<MTLLibrary> lib=[device newLibraryWithSource:source options:opts error:&error];
        id<MTLComputePipelineState> p=lib?Pipeline(device,lib,@"numeric",&error):nil;
        if(!p){ Save(@{@"error":error.description?:@"numeric PSO"},
                   [dir stringByAppendingPathComponent:@"s22.json"]);return 5; }
        id<MTLCommandBuffer> cb=[queue commandBuffer];
        id<MTLComputeCommandEncoder> enc=[cb computeCommandEncoder];
        [enc setComputePipelineState:p];
        [enc setBuffer:input offset:0 atIndex:0]; [enc setBuffer:output offset:0 atIndex:1];
        [enc dispatchThreads:MTLSizeMake(n,1,1) threadsPerThreadgroup:MTLSizeMake(n,1,1)];
        [enc endEncoding];[cb commit];[cb waitUntilCompleted];
        if(cb.error){ Save(@{@"error":cb.error.description},
                         [dir stringByAppendingPathComponent:@"s22.json"]);return 6; }
        const float *result=output.contents;
        NSMutableArray *cases=[NSMutableArray new];
        for(int i=0;i<n;i++){
            NSArray *v=Vector(&result[i*4],4);
            if(v.count!=4){Save(@{@"error":@"nonfinite numeric probe"},
                              [dir stringByAppendingPathComponent:@"s22.json"]);return 7;}
            [cases addObject:@{@"x":@(pairs[2*i]),@"y":@(pairs[2*i+1]),
                                @"half_pow":v[0],@"float_pow":v[1],
                                @"float_cancellation":v[2],@"half_cancellation":v[3]}];
        }
        // Sampler: 2x2 four synthetic pixels encoding texel coordinates in RGB.
        MTLTextureDescriptor *td=[MTLTextureDescriptor texture2DDescriptorWithPixelFormat:MTLPixelFormatRGBA16Float
            width:2 height:2 mipmapped:NO];
        td.usage=MTLTextureUsageShaderRead; td.storageMode=MTLStorageModeShared;
        id<MTLTexture> tex=[device newTextureWithDescriptor:td];
        const __fp16 rgba[]={0,0,0,1, 1,0,0,1, 0,1,0,1, 1,1,0,1};
        [tex replaceRegion:MTLRegionMake2D(0,0,2,2) mipmapLevel:0
                   withBytes:rgba bytesPerRow:16];
        const float uv[]={.25f,.25f, .75f,.25f, .5f,.5f, -1.f,2.f};
        id<MTLBuffer> coords=[device newBufferWithBytes:uv length:sizeof(uv)
                 options:MTLResourceStorageModeShared];
        id<MTLBuffer> sampled=[device newBufferWithLength:4*4*sizeof(float)
                 options:MTLResourceStorageModeShared];
        MTLCompileOptions *samplerOptions=[MTLCompileOptions new]; samplerOptions.mathMode=opts.mathMode;
        samplerOptions.mathFloatingPointFunctions=MTLMathFloatingPointFunctionsPrecise;
        id<MTLLibrary> lib2=[device newLibraryWithSource:source options:samplerOptions error:&error];
        id<MTLComputePipelineState> sp=lib2?Pipeline(device,lib2,@"sampling",&error):nil;
        if(!sp){Save(@{@"error":error.description?:@"sampler PSO"},
                    [dir stringByAppendingPathComponent:@"s22.json"]);return 8;}
        MTLSamplerDescriptor *sd=[MTLSamplerDescriptor new];
        sd.sAddressMode=MTLSamplerAddressModeClampToEdge;
        sd.tAddressMode=MTLSamplerAddressModeClampToEdge;
        sd.minFilter=MTLSamplerMinMagFilterNearest;
        sd.magFilter=MTLSamplerMinMagFilterNearest;
        id<MTLSamplerState> nearest=[device newSamplerStateWithDescriptor:sd];
        sd.minFilter=MTLSamplerMinMagFilterLinear;
        sd.magFilter=MTLSamplerMinMagFilterLinear;
        id<MTLSamplerState> linear=[device newSamplerStateWithDescriptor:sd];
        NSMutableArray *samples=[NSMutableArray new];
        for(int filter=0;filter<2;filter++){
            id<MTLCommandBuffer> c=[queue commandBuffer];
            id<MTLComputeCommandEncoder> e=[c computeCommandEncoder];
            [e setComputePipelineState:sp];[e setTexture:tex atIndex:0];
            [e setSamplerState:filter==0?nearest:linear atIndex:0];
            [e setBuffer:coords offset:0 atIndex:0];
            [e setBuffer:sampled offset:0 atIndex:1];
            [e dispatchThreads:MTLSizeMake(4,1,1) threadsPerThreadgroup:MTLSizeMake(4,1,1)];
            [e endEncoding];[c commit];[c waitUntilCompleted];
            if(c.error){Save(@{@"error":c.error.description},
                       [dir stringByAppendingPathComponent:@"s22.json"]);return 9;}
            NSArray *values=Vector(sampled.contents,16);
            if(values.count!=16){Save(@{@"error":@"nonfinite sampling"},
                                  [dir stringByAppendingPathComponent:@"s22.json"]);return 10;}
            [samples addObject:@{@"filter":filter==0?@"nearest":@"linear",
                                 @"clamp_to_edge":@YES,@"RGBA_flat":values}];
        }
        [modeRows addObject:@{@"mode":@[@"safe",@"relaxed",@"fast"][mode],
                @"math_mode":@(opts.mathMode),
                @"float_functions":@(opts.mathFloatingPointFunctions),
                @"pow_cases":cases,@"samples":samples}];
    }
    NSDictionary *report=@{
       @"os":NSProcessInfo.processInfo.operatingSystemVersionString,
       @"gpu":device.name?:@"unknown",
       @"source":@"Own MSL pow/cancellation/sampler kernels, plus Apple original PSO construction.",
       @"photo_inputs":@NO,@"person_media_generated":@NO,
       @"original_metallib_sha256":Hash(metalBytes),
       @"original_pso":@{@"function":@"renderFinalAdjustments",
          @"useImageBlock":@NO, @"useSrlVersion":@0,
          @"created":@YES,
          @"max_threads_per_threadgroup":@(originalPSO.maxTotalThreadsPerThreadgroup),
          @"math_mode_overridden":@NO,
          @"whole_original_consumer_recompiled":@NO,
          @"original_pixel_dispatch_performed":@NO},
       @"modes_apply_to":@"synthetic kernels only",
       @"mode_rows":modeRows,
       @"global_inverse_certified":@NO,
       @"camera_face_ev_identified":@NO,
       @"actual_photo_processed":@NO};
    Save(report,[dir stringByAppendingPathComponent:@"s22.json"]);
    NSLog(@"S22 ORIGINAL_PSO_OK modes=%lu photo_inputs=0 complete_domain_proof=0",
            (unsigned long)modeRows.count);
    return 0;
 }
}
